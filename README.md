# HomeKit Device Aggregator for Home Assistant

This custom integration for Home Assistant allows you to combine multiple entities into a single HomeKit device. This solves the common issue where multiple related entities appear as separate devices in HomeKit.

## Features

- Combine multiple Home Assistant entities into a single HomeKit device
- Configure through the Home Assistant UI
- Real-time state synchronisation between Home Assistant and HomeKit
- Supports multiple device types with specific HomeKit characteristics

## Installation

1. Copy this directory to your Home Assistant custom_components directory:
   ```bash
   cp -r homekit_device /config/custom_components/
   ```
2. Restart Home Assistant
3. Go to Configuration -> Integrations
4. Click the "+ ADD INTEGRATION" button
5. Search for "HomeKit Device Aggregator"
6. Follow the configuration steps

## Supported Device Types

### Smart Kettle

Combines all kettle controls and sensors into a single HomeKit kettle device.

- Required:
  - Power Switch (switch.kettle)
  - Current Temperature (sensor.kettle_temperature)
  - Target Temperature (number.kettle_target_temperature)
  - Countdown Timer (sensor.kettle_countdown_left)
  - Fault Status (sensor.kettle_fault)
  - Keep Warm Mode (select.kettle_keep_warm)
  - Keep Warm Idle Time (number.kettle_keep_warm_idle_time_mins)

Example configuration:
```yaml
name: Smart Kettle
device_type: kettle
power_switch: switch.kettle
current_temperature: sensor.kettle_temperature
target_temperature: number.kettle_target_temperature
countdown_timer: sensor.kettle_countdown_left
fault_status: sensor.kettle_fault
keep_warm_mode: select.kettle_keep_warm
keep_warm_idle_time: number.kettle_keep_warm_idle_time_mins
```

### Multi-Sensor Thermostat

Creates a thermostat with multiple temperature sensors and controls.

- Required:
  - Power Switch
  - Current Temperature Sensor
  - Target Temperature Control
- Optional:
  - Additional Temperature Sensors
  - Status Sensor

### Multi-Control Fan

Combines fan controls into a single device.

- Required:
  - Power Switch
- Optional:
  - Speed Control
  - Oscillation Control
  - Direction Control
  - Status Sensor

### Multi-Control Light

Aggregates light controls into a single light device.

- Required:
  - Power Switch
- Optional:
  - Brightness Control
  - Colour Temperature Control
  - RGB Colour Control
  - Status Sensor

### Smart Humidifier

Combines humidity sensing and control into a smart humidifier.

- Required:
  - Power Switch
  - Current Humidity Sensor
  - Target Humidity Control
- Optional:
  - Water Level Sensor
  - Status Sensor

### Air Purifier

Creates an air purifier with air quality monitoring.

- Required:
  - Power Switch
  - Air Quality Sensor
- Optional:
  - Filter Life Sensor
  - PM2.5 Sensor
  - VOC Sensor
  - Status Sensor

### Garage Door

Combines door controls and sensors into a garage door opener.

- Required:
  - Power Switch
  - Door Position Control
- Optional:
  - Obstruction Sensor
  - Motion Sensor
  - Light Control
  - Status Sensor

### Security System

Creates a security system from multiple sensors and controls.

- Required:
  - Alarm State Control
- Optional:
  - Security Sensors (multiple)
  - Siren Control
  - Status Sensor

## HomeKit Integration

This integration works alongside the Home Assistant HomeKit Bridge. After configuring your aggregated device, it will appear in the Home app as a single device with all its capabilities, rather than multiple separate accessories.

### Kettle Features in HomeKit

- Power on/off
- Current temperature display
- Target temperature control
- Keep warm mode toggle
- Keep warm duration setting
- Countdown timer display
- Fault status monitoring

## Troubleshooting

1. If a device doesn't appear in HomeKit:
   - Ensure all required entities are correctly configured
   - Check that the HomeKit Bridge is running
   - Restart Home Assistant

2. If states aren't updating:
   - Verify that all entities are working in Home Assistant
   - Check the Home Assistant logs for any errors

## Contributing

Feel free to submit issues and pull requests for:

- New device type support
- Bug fixes
- Feature enhancements

## License

MIT License - See LICENSE file for details
