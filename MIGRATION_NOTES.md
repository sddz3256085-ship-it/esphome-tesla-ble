# PedroKTFC → sddz3256085 传感器迁移说明

将 `PedroKTFC-esphome-tesla-ble-main` 中 `tesla_ble_vehicle:` 下显式声明的 34 个传感器
+ `sensor:` 平台下的 2 个（`ble_signal`、`charge_power_calculated`），共 36 个，
按照 `sddz3256085-ship-it-esphome-tesla-32-main` 自身的架构（基于角色自动创建实体 +
字符串 id → map 的通用存取方式）迁移进去。

## 改动了哪些文件

```
components/tesla_ble_vehicle/__init__.py            (Python 配置/codegen)
components/tesla_ble_vehicle/vehicle_state_manager.h
components/tesla_ble_vehicle/vehicle_state_manager.cpp
components/tesla_ble_vehicle/tesla_ble_vehicle.h
components/tesla_ble_vehicle/tesla_ble_vehicle.cpp
packages/client.yml
```

完整 diff 见同目录下的 `migration.diff`。

## 36 个传感器对照表

| # | Pedro 键名 | sddz 对应键名 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `is_asleep` | `asleep` | 已有，仅需在 client.yml 暴露 | |
| 2 | `is_user_present` | `user_present` | 已有 | |
| 3 | `is_unlocked` | `locked` | **修复了极性 bug** | 原代码 `publish_binary_sensor("locked", !unlocked)`，但 `device_class: lock` 要求 ON=解锁，原逻辑是反的，已改为 `unlocked` |
| 4 | `is_charge_flap_open` | `charge_flap_open` | 已有逻辑，**新增自动实体定义** | 原先只能靠用户在 CONFIG_SCHEMA 里 override，没有默认实体 |
| 5 | `is_boot_open` | `boot_open` | **新增** | 原先只有 Cover 实体反映开合，没有独立 binary_sensor |
| 6 | `is_frunk_open` | `frunk_open` | **新增** | 同上 |
| 7 | `shift_state` | `shift_state` | 已有 | |
| 8 | `defrost_state` | `defrost_state` | **新增**（text_sensor + 解析逻辑） | 需要 `CarServer_ClimateState.defrost_mode`，sddz 原来完全没解析这个字段 |
| 9 | `charge_state` | `battery_level` | 已有，改名 | |
| 10 | `odometer` | `odometer` | 已有 | |
| 11 | `charge_current` | `charger_current` | 已有，改名 | |
| 12 | `charge_voltage` | `charger_voltage` | 已有，改名 | |
| 13 | `charge_power` | `charger_power` | 已有，改名 | |
| 14 | `charge_energy_added` | `charge_energy_added` | **修复了死配置 bug** | 自动实体原来注册的 id 是 `energy_added`，但 C++ 实际发布状态用的 id 是 `charge_energy_added`，两者对不上，导致默认情况下这个传感器永远不会更新。已把自动实体 id 改为 `charge_energy_added` |
| 15 | `charge_distance_added` | `charge_distance_added` | **新增** | 用 `optional_charge_miles_added_ideal` 字段 |
| 16 | `max_soc` | `max_soc` | **新增**（只读傳感器） | 与既有的 `charging_limit` Number 实体数据同源，是额外的只读历史曲线用传感器 |
| 17 | `max_amps` | `max_amps` | **新增**（只读傳感器） | 与既有的 `charging_amps` Number 实体数据同源 |
| 18 | `mins_to_limit` | `time_to_full_charge` | 已有，改名 | |
| 19 | `battery_range` | `range` | 已有，改名 | |
| 20 | `charging_state` | `charging_state` | 已有 | |
| 21 | `charge_port_latch_state` | `charge_port_latch_state` | **新增**（text_sensor） | 与既有的 `charge_port_latch_lock` Lock 实体数据同源，多一个文字状态（SNA/Disengaged/Engaged/Blocking） |
| 22 | `last_update` | — | **故意跳过** | HA 每个实体自带"最后更新时间"属性，没必要重复发一个文本传感器 |
| 23 | `is_climate_on` | `climate_on` | **新增** | 原来只隐含在 Climate 实体里，现在单独暴露一个 binary_sensor |
| 24 | `internal_temp` | `inside_temp` | 已有，改名 | |
| 25 | `external_temp` | `outside_temp` | 已有，改名 | |
| 26 | `windows_state` | `windows_state` | **新增**（聚合）| 原来逐窗户的 binary_sensor + 一个 Cover 都有，但没有"任一车窗打开"这种单一聚合布尔值 |
| 27 | `tpms_pressure_fl` | `tpms_front_left` | 已有，改名 | |
| 28 | `tpms_pressure_fr` | `tpms_front_right` | 已有，改名 | |
| 29 | `tpms_pressure_rl` | `tpms_rear_left` | 已有，改名 | |
| 30 | `tpms_pressure_rr` | `tpms_rear_right` | 已有，改名 | |
| 31 | `ble_disconnected_time` | `ble_disconnected_time` | **新增**（需要新的计时逻辑） | sddz 原来完全没有追踪"断开了多久"，新增了 `ble_disconnected_since_` 成员+相关发布逻辑 |
| 32 | `charger_phases` | `charger_phases` | **新增** | 用 `optional_charger_phases` 字段 |
| 33 | `charge_rate` | `charge_rate` | **修复了死配置 bug** | CONFIG_SCHEMA 里本来就有这个 key，但 `to_code()` 从未真正用它创建/写入任何东西，是个"看起来能配置但完全不生效"的死选项。现在用 `charge_rate_mph * 1.60934` 换算成 km/h 并真正发布 |
| 34 | `driver_temp` | `driver_temp_setting` | 已有，改名 | |
| 35 | `ble_signal` | `ble_signal` | 已有，仅补了 `id:` | client.yml 里本来就有这个 rssi 传感器，只是没给它起 id |
| 36 | `charge_power_calculated` | `charge_power_calculated` | **新增**（template sensor） | 依赖 `charger_voltage`/`charger_current`/`charger_phases` 三个传感器的 id，照抄 Pedro 原始 lambda 逻辑 |

## 代码层面做了什么

1. **`__init__.py`**
   - `BINARY_SENSORS` / `SENSORS` / `TEXT_SENSORS` 三个自动创建列表里新增了对应条目，并补了 `CONFIG_SCHEMA` 的 `cv.Optional(...)` 和对应的 `*_OVERRIDES` 映射，确保用户在 `client.yml` 里写上这些 key 时能正确接管/跳过自动创建的那份。
   - 顺手给 `create_binary_sensor` / `create_sensor` / `create_text_sensor` 三个通用创建函数加上了 `entity_category` 支持（原来只有 button 支持）。
   - 修了两个已存在的"死 id"bug（`energy_added`→`charge_energy_added`、`time_to_full`→`time_to_full_charge`）。

2. **`vehicle_state_manager.h` / `.cpp`**
   - 新增 `update_ble_disconnected_seconds()`。
   - 新增两个文本映射函数 `get_defrost_state_text()`、`get_charge_port_latch_state_text()`（抄自 Pedro 库对应的查表逻辑）。
   - 在 `update_closures_state()` 里补了 `boot_open` / `frunk_open` / `windows_state` 的 `publish_binary_sensor` 调用。
   - 在 `update_climate_state()` 里补了 `climate_on` 的 binary_sensor 发布 + `defrost_state` 的文本解析发布。
   - 在 `update_charge_state()` 里补了 `max_soc` / `max_amps` / `charge_distance_added` / `charger_phases` / `charge_rate`(km/h) / `charge_port_latch_state`(文本) 的发布。
   - 修复了 `update_unlocked()` 里 `"locked"` 传感器状态极性反了的 bug。

3. **`tesla_ble_vehicle.h` / `.cpp`**
   - 新增 `ble_disconnected_since_` 成员，在 `handle_connection_lost()` / `handle_connection_established()` 里维护，在 `update()` 里周期性地把经过的秒数发布给 `ble_disconnected_time` 传感器。

4. **`packages/client.yml`**
   - 在 `tesla_ble_vehicle:` 块下新增了 33 个 key（对应 34 个 Pedro 传感器，`last_update` 跳过），每行都用注释标出对应的 Pedro 原键名，便于核对。
   - `sensor:` 平台下给原有的 `ble_client` rssi 传感器补了 `id: ble_signal`，并新增了 `charge_power_calculated` 模板传感器。

## ⚠️ 需要你在实际编译时确认的假设

这个仓库里**没有包含** `car_server.pb.h` / `vcsec.pb.h`（它们是编译时从外部 Tesla BLE 协议库拉取的），
所以下面这些新增字段名是**照抄 Pedro 库里对同一上游协议的用法**推断出来的，理论上两边用的是同一份
官方 `teslamotors/vehicle-command` protobuf 定义，但我没有条件直接编译验证：

- `CarServer_ChargeState.which_optional_charging_amps` / `optional_charging_amps.charging_amps`（`max_amps`）
- `CarServer_ChargeState.which_optional_charge_miles_added_ideal` / `optional_charge_miles_added_ideal.charge_miles_added_ideal`（`charge_distance_added`）
- `CarServer_ChargeState.which_optional_charger_phases` / `optional_charger_phases.charger_phases`（`charger_phases`）
- `CarServer_ClimateState.has_defrost_mode` / `defrost_mode.which_type`，以及 `CarServer_ClimateState_DefrostMode_{Off,Normal,Max}_tag`（`defrost_state`）
- `CarServer_ChargePortLatchState_{SNA,Disengaged,Engaged,Blocking}_tag`（`charge_port_latch_state` 的文本枚举，这部分 sddz 已经在用，只是之前没转成文字）

**强烈建议**：用 `esphome compile` 先跑一遍，如果上面任何一个字段名在你实际拉取到的 proto 版本里不存在，
编译器会直接报 "no member named ..." 的错误，到时候把对应那一小段删掉或改字段名即可，不影响其余部分。

## 已知的设计取舍（不是 bug，是主动决定）

- **`last_update`** 没有迁移：sddz 架构里没有现成的墙钟时间源可用（Pedro 用的是 `ctime()`），
  而且这类信息 Home Assistant 本身就有（每个实体的"最后更新时间"属性），重新做一个文本传感器意义不大。
- **`max_soc` / `max_amps`** 虽然新增成了独立的只读 Sensor，但要知道 sddz 本来就有功能等价、
  还能反向下发设置的 `charging_limit` / `charging_amps` Number 实体。两者数据同源，新增的 Sensor
  主要是为了在 HA 里拿到独立的历史曲线（Number 的长期统计不如 Sensor 好用），如果你觉得冗余，
  直接把 `client.yml` 里 `max_soc:` / `max_amps:` 两行删掉即可，不影响其它任何功能。
