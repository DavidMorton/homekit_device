# HomeKit Device Aggregator for Home Assistant

This custom integration for Home Assistant allows you to combine multiple entities into a single HomeKit device. This solves the common issue where multiple related entities (like a smart kettle's various controls and sensors) appear as separate devices in HomeKit.

## Features

- Combine multiple Home Assistant entities into a single HomeKit device
- Configure through the Home Assistant UI
- Supports various device types (currently implemented: smart kettle)
- Real-time state synchronization between Home Assistant and HomeKit

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

## Configuration

### Smart Kettle Example

To combine a smart kettle's entities into a single HomeKit device:

1. Select "Smart Kettle" as the device type
2. Configure the following entities:
   - Power Switch: The switch entity that controls the kettle's power
   - Current Temperature: The sensor entity that shows the current water temperature
   - Target Temperature: The input_number entity that sets the target temperature
   - Status Sensor (Optional): A sensor entity showing the kettle's status

## Supported Device Types

Currently supported device types:

- Smart Kettle
  - Combines power control, temperature sensors, and target temperature into a single HomeKit kettle device

More device types coming soon:
- Multi-Sensor Thermostat
- Multi-Control Fan
- Multi-Control Light

## Contributing

Feel free to submit issues and pull requests for:
- New device type support
- Bug fixes
- Feature enhancements

## License

MIT License - See LICENSE file for details
