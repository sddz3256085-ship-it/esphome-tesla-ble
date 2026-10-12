# esphome-tesla-132 深度检查与修复报告

> 对 `esphome-tesla-132.zip`（PedroKTFC → sddz 36 传感器移植的"最终修复代码"）的深度检查结果。
> 本目录为**修复后的代码**，已通过 `esphome config` 校验和 **完整固件编译**（ESP32 / ESP-IDF 5.5.5 / ESPHome 2026.8.2）。

---

## 一、检查方法

1. **三方逐行比对**：`PedroKTFC-esphome-tesla-ble-main`（移植来源）、`sddz3256085-ship-it-esphome-tesla-32-main`（目标基线）、`esphome-tesla-132`（被检代码）。
2. **协议字段核验**：克隆实际使用的底层库 `13210986088/tesla-ble`（`packages/board.yml` 所引用），逐一核对新增代码用到的每个 protobuf 字段与 nanopb 生成名（`car_server.pb.h` / `vehicle.pb.h` / `common.pb.h`）。
3. **36 个传感器全量对账**：对照 Pedro 的 `client.yml` + `__init__.py` 定义表，核对每个传感器在 sddz 侧的「YAML key → Python auto 实体 → C++ publish 键 → 单位/精度/device_class」四级链路。
4. **ESPHome 校验**：`esphome 2026.8.2 config` 全量通过，并解析 effective config 逐项核对。
5. **完整编译**：`esphome compile`（esp32-generic，ESP-IDF 框架）**编译链接成功**，RAM 57.9%、Flash 77%。

---

## 二、发现并已修复的 BUG

### BUG 1（严重·数据错误）：odometer 单位错误 —— km / mi 不匹配
- **位置**：`components/tesla_ble_vehicle/__init__.py` 的 `CONFIG_SCHEMA`
- **问题**：`cv.Optional("odometer")` 的默认 `unit_of_measurement="km"`，但 C++ 侧
  `update_drive_state()` 发布的是 `odometer_in_hundredths_of_a_mile / 100`，即**英里**。
  由于移植后的 `client.yml` 里写上了 `odometer:`（覆盖自动实体），这个默认单位被真正启用：
  HA 里会显示"单位 km、数值却是英里"，**读数偏小 1.609 倍**。
- **修复**：schema 默认单位 `km → mi`，`accuracy_decimals` `1 → 2`（对齐 Pedro 的 2 位小数）。
  自动实体精度同步改为 2 位。

### BUG 2（严重·新构建必失败）：`board.yml` 引用的 `ref: v5.0.3` 在上游仓库不存在
- **位置**：`packages/board.yml`
- **问题**：`13210986088/tesla-ble` 仓库**没有** `v5.0.3` 这个 tag/branch
  （实测 `git fetch origin v5.0.3` → `couldn't find remote ref`）。ESPHome 拉取 IDF 组件时
  会 `git fetch --depth=1 origin v5.0.3` 然后失败并删除缓存——**任何干净缓存的全新编译都会死在依赖拉取**。
  （此前能编译成功大概率是因为本机 `~/.cache/esphome` 里存有旧缓存。）
- **修复**：改钉到实际存在的提交 `04a1b0dc6369b786ec961b0fcc070ab451bb4e48`
  （即仓库 manifest `version: 5.0.3` 对应的 main 分支提交，2026-05-03）。
  **如果你本人管理 tesla-ble 仓库，最干净的长期方案是在该提交上补建 `v5.0.3` tag**，然后把这一行改回去。

### BUG 3（功能性·隐性）：binary_sensor 用户覆盖注册键错误
- **位置**：`__init__.py` `to_code()` 的覆盖循环
- **问题**：原代码 `create_binary_sensor(var, {"id": user_key}, ...)` 用的是 **YAML 键名**而不是
  auto 实体 id。`BINARY_SENSOR_OVERRIDES` 中唯一两者不同的是 `"charging" → "charger"`：
  用户在 YAML 里写 `charging:` 自定义实体时，实体会注册到 map 键 `"charging"` 下，
  而 C++ 只往 `"charger"` 发布——**该自定义实体永远不会有任何更新**（静默死实体）。
- **修复**：改为 `{"id": auto_id}` 并补 `auto_id is not None` 防御；text_sensor 循环同步统一用 `auto_id`。
  （此 bug 在 sddz 基线里就存在，属遗留问题，本次一并修复。）

### BUG 4（正确性·边界场景）：windows_state 聚合条件过松
- **位置**：`vehicle_state_manager.cpp` `update_closures_state()`
- **问题**：只要**任一**车窗字段出现就发布聚合值。如果报文只带部分车窗字段且均为 false，
  会误报"所有车窗已关"。Pedro 原版逻辑要求**四个车窗字段全部在场**才发布。
- **修复**：恢复 Pedro 的四字段全present判断（`||` → `&&`）。

### BUG 5（行为缺失）：ble_disconnected_time 不从开机起计
- **位置**：`tesla_ble_vehicle.cpp` `setup()` / `ble_disconnected_since_`
- **问题**：原实现只在**第一次连接断开**（`ESP_GATTC_CLOSE_EVT`）后才开始计时。如果设备开机后
  车一直不在范围内（从未连上过），传感器会永远停留在"未知"。Pedro 原版在 `setup()` 里
  `ble_disconnected_time_ = millis(); // Initialise disconnect time on startup`，从开机就计时。
- **修复**：`setup()` 中初始化 `ble_disconnected_since_ = millis()`；连接建立时照旧清零。
  语义：从开机到第一次连上之间的时长也算"断连时长"，与 Pedro 完全一致。

### BUG 6（对等性·影响功率计算）：charger_phases 缺少 Pedro 的 2→3 换算过滤器
- **位置**：`packages/client.yml`
- **问题**：Pedro 原版 `client.yml` 给 `charger_phases` 加了 `if (x == 2) return 3;` 的过滤器
  （部分车机固件三相充电时上报 2）。漏掉它不仅显示值不同，还会让
  `charge_power_calculated`（= 电压 × 电流 × 相数）在三相充电时**少算 1/3 功率**。
- **修复**：在 `client.yml` 中原样补回该过滤器（含说明注释）。

### BUG 7（代码缺陷）：`SENSOR_OVERRIDES` 字典里重复的 `"charge_rate"` 键
- **位置**：`__init__.py` `SENSOR_OVERRIDES`
- **问题**：Python 字面量里 `"charge_rate": "charge_rate"` 出现两次（Python 静默取后者，不报错）。
  功能上无影响，但属明显的手误。
- **修复**：删除重复项，留注释说明。

### BUG 8（一致性）：三个 device_class 与自动实体 / Pedro 原版不一致
- **位置**：`__init__.py` `CONFIG_SCHEMA`
- **问题与修复**：
  - `battery_level`：用户覆盖 schema 缺 `device_class`，而 Pedro 的 `charge_state` 是 `battery` → **已补上 `battery`**；
  - `user_present`：schema 是 `presence`，自动实体和 Pedro 都是 `occupancy` → **统一为 `occupancy`**；
  - `charge_flap_open`：schema 是 `opening`，自动实体和 Pedro 都是 `door` → **统一为 `door`**。

### BUG 9（对等性·精度）：range / charge_distance_added 小数位与 Pedro 不一致
- **位置**：`__init__.py`（schema + 自动实体定义）
- **问题**：Pedro 的 `battery_range`、`charge_distance_added` 都是 2 位小数（协议里这两个字段
  本身就是带 2 位小数的 float），原迁移为 0/1 位，会损失显示精度。
- **修复**：统一改为 `accuracy_decimals=2`（odometer 同步，见 BUG 1）。

---

## 三、重点核验过、确认无问题的关键点

以下都是本次深度检查中专门验证过、**原"最终修复代码"已经做对**的地方（也就是说，
MIGRATION_NOTES.md 里标注的假设全部核验通过）：

| 假设/改动 | 核验结果 |
|---|---|
| `which_optional_charge_limit_soc` / `optional_charge_limit_soc.charge_limit_soc`（max_soc） | ✅ 与 nanopb 生成头一致 |
| `which_optional_charging_amps` / `optional_charging_amps.charging_amps`（max_amps） | ✅ |
| `which_optional_charge_miles_added_ideal` / `...charge_miles_added_ideal`（charge_distance_added） | ✅ |
| `which_optional_charger_phases` / `optional_charger_phases.charger_phases`（charger_phases） | ✅ |
| `has_defrost_mode` / `defrost_mode.which_type` + `DefrostMode_{Off,Normal,Max}_tag`（defrost_state） | ✅ |
| `has_charge_port_latch` + `ChargePortLatchState_{SNA,Disengaged,Engaged,Blocking}_tag`（charge_port_latch_state） | ✅ |
| `which_optional_is_climate_on`（climate_on） | ✅ |
| `locked` 极性修复（device_class=lock ⇒ ON=解锁，与 Pedro `is_unlocked` 一致） | ✅ 逻辑正确 |
| `charge_energy_added` / `time_to_full_charge` 两个死 id 修复 | ✅ C++ publish 键与 Python id 已对齐 |
| VCSEC 与 ClosuresState 两条锁车状态的极性一致性 | ✅ 一致 |
| client.yml 33 + sensor 平台 2 = 35 个可见实体，对应 Pedro 36 - last_update | ✅ 数量与命名全对 |
| `charge_power_calculated` 模板对 `id(charge_voltage)/(charge_current)/(charger_phases)` 的引用 | ✅ 均有定义（config 校验通过） |
| 所有新增 auto 实体 id（`tesla_*_sensor`）无冲突 | ✅ |
| `frunk_open` 用 `which_optional_door_open_trunk_front` 判断（Pedro 原版这里有个复制粘贴 bug 用了 window 字段） | ✅ 迁移时已顺手修正，比 Pedro 原版更对 |

---

## 四、有意保留的差异（不是 bug，是设计取舍，供知悉）

1. **`charge_rate` 单位为 km/h（Pedro 是 mph）**：sddz 的 CONFIG_SCHEMA 本来就把这个 key
   定义为 km/h，且 sddz 已有 `charging_rate`（mph，内部实体）承载数据同源的 mph 读数；
   km/h 数值 = `charge_rate_mph × 1.60934`，换算正确。HA 中 `device_class: speed` 的实体
   会按 HA 单位制自动显示，不影响使用。
2. **`mins_to_limit` → `time_to_full_charge`**：数据源从 Pedro 的
   `minutes_to_charge_limit`（字段 142）换成了 sddz 原有的 `minutes_to_full_charge`（字段 123）。
   两者语义相近（充到上限/充满的分钟数），保留 sddz 原字段不动 C++。
3. **`last_update` 不迁移**：HA 自带每实体"最后更新时间"，维持 MIGRATION_NOTES 的决定。
4. **`max_soc` / `max_amps` 与 `charging_limit` / `charging_amps` Number 实体数据同源**：
   Sensor 版本用于历史曲线，Number 版本可反向设置，互不冲突。
5. **sddz 遗留死配置 `range_rated_api`**：schema 里保留该 key（避免老 YAML 报错），但 C++ 从不
   发布它（代码内已有注释说明协议无此字段）。未删除，知悉即可。
6. **充电开关不含 `Calibrating` 状态**：sddz 的 `is_charging_` 只认 Charging/Starting，
   Pedro 的 charger_switch 还包含 Calibrating。这是 sddz 基线固有行为，未改动；
   `charging_state` 文本传感器仍会如实显示 "Calibrating"。
7. **断连后传感器置 unknown 的行为**：sddz 只把 `asleep`/`user_present` 标记为无状态，
   Pedro 会把全部传感器置 Unknown（`ble_disconnected_min_time` 之后）。维持 sddz 设计。

---

## 五、验证结果

```
$ esphome 2026.8.2 config  test-build.yml   (esp32-generic + base + client 包)
INFO Configuration is valid!

$ esphome 2026.8.2 compile test-build.yml
INFO Successfully compiled program.
RAM:   57.9% ( 72116 / 124580 bytes)
Flash: 77.0% (1412519 / 1835008 bytes)
```

- tesla-ble 组件按新 pin 的 SHA 正常拉取（`managed_components/tesla-ble`, manifest 5.0.3）；
- 所有迁移的 C++ 代码（含全部 protobuf 字段访问）编译零错误；
- 编译产物中确认包含本报告全部修复（已核对生成源码）。

---

## 六、修改文件清单

| 文件 | 改动 |
|---|---|
| `components/tesla_ble_vehicle/__init__.py` | BUG 1、3、7、8、9 |
| `components/tesla_ble_vehicle/tesla_ble_vehicle.cpp` | BUG 5 |
| `components/tesla_ble_vehicle/tesla_ble_vehicle.h` | BUG 5 注释同步 |
| `components/tesla_ble_vehicle/vehicle_state_manager.cpp` | BUG 4 |
| `packages/board.yml` | BUG 2 |
| `packages/client.yml` | BUG 6 |
| `requirements.txt`（新增） | 补上 Makefile.common 依赖的版本文件（原快照缺失，`make compile/validate-config` 会因 grep 不到而失败） |
| `tesla-ble-{esp32-generic, m5stack-nanoc6, m5stack-atoms3}.yml`（新增） | 补上根构建入口（原快照缺失，`make compile` 没有 target；均验证 `config` 通过） |
| `secrets.yaml.example`（新增） | 与上游一致的样例 secrets |
| `BUGFIX_REPORT.md` / `fixes.diff` / `MIGRATION_NOTES.md` | 本报告 / 组件修复差异 / 原迁移说明 |

组件代码的完整差异见 `fixes.diff`（不含文档与新增的根 yml）。
