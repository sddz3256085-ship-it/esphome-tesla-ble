# ESPHome 2026.x Schema-Level Scan & Fix Report (esphome-tesla-ble)

扫描对象：`esphome-tesla-132.zip`（上一轮"最终修复代码"）的全部 YAML 与组件 Python schema。
扫描工具：`esphome 2026.9.1`（`uvx esphome config` / `compile`，动态验证）+ 逐行静态 schema 审计。
交付产物：本仓库（重命名为 `esphome-tesla-ble`）。

---

## 0. 你日志里三个报错的根因（已全部在库层面修复）

你看到的报错来自**上游原版库** `yoziru/esphome-tesla-ble`（或任何指向它的
`external_components` 缓存），不是 132 修复版：

| 你的日志 | 上游代码位置 | 本库（esphome-tesla-ble）的状态 |
|---|---|---|
| `value must be at least 5`（`vcsec_poll_interval: 3` 被拒） | `cv.int_range(min=5, max=300)`（整数，最小 5） | ✅ 已改为 `cv.float_range(min=0.2, max=300.0)`，`3`、`2.5`、`0.2` 均合法 |
| `[locked] is an invalid option` | 上游 `tesla_ble_vehicle:` 只接受 vin/role/轮询间隔等核心键，不接受任何传感器子键 | ✅ `locked:` 等 50+ 个传感器子键全部支持（见 §3 键名总表） |
| `[user_present] is an invalid option` | 同上 | ✅ 支持 |
| `[shift_state] is an invalid option` | 同上（上游把 shift_state 自动建为内部实体，键不可写） | ✅ 支持（hub 子键与 text_sensor 平台两种写法均可） |

`infotainment_poll_interval_awake: 10` / `infotainment_poll_interval_active: 6`
在上游本来就合法（min 分别为 10/5），本库进一步放宽到 0.2。

> [!IMPORTANT]
> 如果你用 `packages/external_components.dashboard.yml`
> （`source: github://13210986088/esphome-tesla-ble/components@main`），
> **必须把本修复后的代码推送到你的 GitHub 仓库 main 分支**，否则 dashboard
> 拉到的仍是旧代码、报错不会消失。本地使用 `external_components.yml`
> （`source: components`）则直接生效。

---

## 1. 动态验证结果（全部通过）

| 配置 | 结果 |
|---|---|
| `tesla-ble-esp32-generic.yml` | ✅ valid + **完整编译成功**（RAM 57.6% / Flash 75.1%） |
| `tesla-ble-m5stack-nanoc6.yml` | ✅ valid |
| `tesla-ble-m5stack-atoms3.yml` | ✅ valid |
| `base.yml` + `listener.yml`（VIN 扫描模式） | ✅ valid |
| 边界用例矩阵（8 组，见 §4） | ✅ 全部符合预期 |

## 2. 会导致 `esphome config` 失败的 YAML 项（完整清单）

### 2.1 轮询间隔取值边界（有意设计，错误信息清晰）

| YAML 项 | 合法范围 | 失败示例与报错 |
|---|---|---|
| `vcsec_poll_interval` | **0.2 – 300**（浮点） | `0.1` → `value must be at least 0.2.`；`301` → `value must be at most 300.0.` |
| `infotainment_poll_interval_awake` | 0.2 – 600 | 同上格式 |
| `infotainment_poll_interval_active` | 0.2 – 120 | 同上格式 |
| `infotainment_sleep_timeout` | 0.2 – 3600 | 同上格式 |
| `charging_amps_max` | 1 – 48（整数） | `0`/`49` 被拒 |

### 2.2 组件块内的非法/未知子键

- 任何不在 §3 总表里的键写在 `tesla_ble_vehicle:` 下都会失败：
  `[xxx] is an invalid option for [tesla_ble_vehicle]`。
- **PedroKTFC 旧键名一律不支持**（ESPHome 会自动给出建议）：
  `is_asleep`（→ 建议 `asleep`）、`is_unlocked`（→ `locked`，注意极性相反：
  `locked`=ON 表示已上锁，Pedro 的 `is_unlocked`=ON 表示未上锁）、
  `is_user_present`（→ `user_present`）、`is_charge_flap_open`（→ `charge_flap_open`）、
  `is_boot_open`（→ `boot_open`）、`is_frunk_open`（→ `frunk_open`）、
  `is_climate_on`（→ `climate_on`）、`internal_temp`（→ `inside_temp`）、
  `external_temp`（→ `outside_temp`）、`charge_state`（→ `battery_level`）、
  `charge_current`（→ `charger_current`）、`charge_voltage`（→ `charger_voltage`）、
  `charge_power`（→ `charger_power`）、`battery_range`（→ `range`）、
  `mins_to_limit`（→ `time_to_full_charge`）、`driver_temp`（→ `driver_temp_setting`）、
  `tpms_pressure_fl/fr/rl/rr`（→ `tpms_front_left/front_right/rear_left/rear_right`）。
- `ble_signal`、`charge_power_calculated` 属于标准平台（`ble_client` 的 rssi /
  `template`），写在 hub 块下会失败 —— 它们已经在 `packages/client.yml`
  的 `sensor:` 段正确声明。

### 2.3 双语法重复声明（本轮新增的守卫）

同一个键同时写在 hub 块和平台块里会直接失败并给出明确指引：
`'locked' is declared both as a sub-key of 'tesla_ble_vehicle:' and in a
'binary_sensor: - platform: tesla_ble_vehicle' block. Please declare it in
only one of the two places.`

### 2.4 平台块的必备键

`binary_sensor/text_sensor/sensor: - platform: tesla_ble_vehicle` 必须写
`tesla_ble_vehicle_id:`（缺失报 required key）；引用不存在的 id 报
ID 解析错误。

### 2.5 与本组件无关、但随包携带的配置项

- `secrets.yaml` 缺项（`wifi_ssid` / `api_encryption_key` / `ble_mac_address` /
  `tesla_vin` 等）→ `secret not found`。
- `api_encryption_key` 必须是 32 字节 base64（44 字符）。
- `ota: password:` 只产生 WARNING（浪费约 3.5KB flash），不会失败。

## 3. 合法键名总表（两种写法通用）

**hub 块核心键**：`id`、`ble_client_id`、`vin`（必填）、`charging_amps_max`、`role`
（OWNER/DRIVER/CHARGING_MANAGER）、`vcsec_poll_interval`、`infotainment_poll_interval_awake`、
`infotainment_poll_interval_active`、`infotainment_sleep_timeout`、`update_interval`。

**binary_sensor 键（19）**：`asleep` `user_present` `locked` `charging` `charge_flap_open`
`boot_open` `frunk_open` `windows_state` `climate_on` `parking_brake` `sunroof`
`door_driver_front` `door_driver_rear` `door_passenger_front` `door_passenger_rear`
`window_driver_front` `window_driver_rear` `window_passenger_front` `window_passenger_rear`

**sensor 键（27）**：`battery_level` `range` `range_rated_api` `inside_temp` `outside_temp`
`driver_temp_setting` `passenger_temp_setting` `odometer` `speed` `charger_power`
`charger_voltage` `charger_current` `charging_rate` `charge_rate`
`charge_energy_added`（旧别名 `energy_added`）`time_to_full_charge`（旧别名 `time_to_full`）
`tpms_front_left` `tpms_front_right` `tpms_rear_left` `tpms_rear_right`
`max_soc` `max_amps` `charge_distance_added` `charger_phases` `ble_disconnected_time`

**text_sensor 键（5）**：`shift_state` `charging_state` `iec61851_state` `defrost_state`
`charge_port_latch_state`

**控制类覆盖键（仅 hub 块）**：`charging_switch` `steering_wheel_heat_switch`
`charging_amps` `doors_lock` `charge_port_latch_lock` `frunk_cover` `trunk_cover`
`windows_cover` `charge_port_door_cover`

## 4. 边界用例验证矩阵（esphome 2026.9.1 实测）

| 用例 | 期望 | 实测 |
|---|---|---|
| A. `vcsec_poll_interval: 3` + awake `10` + active `6`（你的原始值） | 通过 | ✅ PASS |
| B. 全部间隔 `0.2`/`0.5`/`0.25`/`1.5`（浮点下限） | 通过 | ✅ PASS |
| C. `vcsec_poll_interval: 0.1` | 拒绝 | ✅ FAIL `value must be at least 0.2.` |
| D. `vcsec_poll_interval: 301` | 拒绝 | ✅ FAIL `value must be at most 300.0.` |
| E. 平台式 `binary_sensor:`/`text_sensor:`（官方示例语法，locked/user_present/charging/shift_state/charging_state） | 通过 | ✅ PASS |
| F. 平台式 `sensor:`（odometer/max_soc/charger_phases/ble_disconnected_time/energy_added 旧别名） | 通过 | ✅ PASS |
| G. 同键双语法重复声明 | 拒绝+指引 | ✅ FAIL（消息明确） |
| H. hub 子键式（locked/user_present/shift_state/sunroof/energy_added/time_to_full） | 通过 | ✅ PASS |
| 生成代码检查 | 平台实体以 `user_defined=true` 注册，自动实体不再重复创建 | ✅（main.cpp 实测） |

## 5. 本轮扫描中发现并修复的潜在 BUG（2026.x 兼容性）

1. **Python 子模块名遮蔽（严重，原代码就有）**：组件里存在 `sensor.py` 平台文件时，
   Python 加载它会把 `tesla_ble_vehicle` 包属性 `sensor` 覆盖掉，而包属性与
   `__init__.py` 的全局名字共享同一个 `__dict__` —— 任何使用
   `sensor: - platform: tesla_ble_vehicle` 的配置在代码生成阶段直接崩溃
   （`AttributeError: ... has no attribute 'Sensor'`）。修复：`__init__.py`
   改用不可碰撞的私有别名 `_binary_sensor/_sensor/_text_sensor` 导入。
2. **`sensor.py` 平台是死代码**：旧实现把传感器挂到一个孤立的
   `TeslaBLEVehicleSensor` 容器上，从不连到车辆状态管理器 —— 平台式声明的
   传感器**永远不会有数据**。修复：改为通过 `tesla_ble_vehicle_id` 接线到 hub
   （容器类保留以兼容旧 `id:` 引用）。
3. **2026.9 常量不存在**：`UNIT_BAR`、`UNIT_MILES`、`UNIT_MILES_PER_HOUR`、
   `UNIT_SECONDS` 已不在 `esphome.const` 中（旧 sensor.py 的 import 一加载就炸）。
   改用 `UNIT_SECOND` 与字符串字面量 `"bar"`/`"mi"`/`"mph"`。
4. **`binary_sensor_schema(device_class=None)` 报 `string value is None`**：
   无 device_class 的键（asleep/climate_on）改为不传该参数。
5. **代码生成顺序竞态（新平台引入时）**：hub 的自动建实体与平台块的注册顺序
   不保证 —— C++ 侧 `set_*_sensor` 增加 `user_defined` 参数：自动实体永不覆盖
   已注册键，用户实体总是覆盖。生成代码实测验证两种顺序都正确。
6. **重复声明守卫的子串误报**：`"charging" in "charging_amps_max"`（迭代 dict
   得到键名字符串导致子串匹配）→ 显式 `isinstance(hub, dict)` 修正。
7. **毫秒换算浮点截断**：`int(0.29*1000)` = 289 → `int(round(...))`。
8. **多车场景防御**：平台式声明的跳过逻辑按 `tesla_ble_vehicle_id` 归属到
   对应 hub，避免 A 车的平台实体抑制 B 车的自动实体（当前 schema 单 hub，
   该修复为前向兼容）。

## 6. 与上游 yoziru/esphome-tesla-ble 的行为差异（本库特性）

| 能力 | 上游 | 本库 |
|---|---|---|
| `vcsec_poll_interval: 3` | ❌ `value must be at least 5` | ✅（0.2–300 浮点） |
| hub 块直接写 `locked:`/`user_present:`/`shift_state:` 等 | ❌ invalid option | ✅（50+ 键） |
| `binary_sensor/text_sensor/sensor: - platform: tesla_ble_vehicle` | ❌ 平台不存在 | ✅（官方示例语法） |
| 实体暴露方式 | 全部自动创建并直接暴露（默认名） | 自动创建为 internal，写键才暴露（可控 id/name/filters） |
| 36 个 Pedro 传感器 | 无 | ✅ 全部（含 charger_phases 2→3 过滤、charge_power_calculated 模板） |
