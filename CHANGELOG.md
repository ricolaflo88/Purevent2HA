# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-03

### Added

- Initial release of Purevent2HA addon
- Complete EnOcean protocol support
- VMI Purevent (D1079-01-00) integration
  - Temperature, humidity, and CO2 sensors
  - Power, heating, cooling, intake controls
  - Fan speed control
- CO2 Sensor (A5-09-04) support
- Temperature/Humidity Sensor (A5-04-01) support
- Ventilairsec Assistant (D1079-00-00) support
- Home Assistant integration with:
  - Sensor platform
  - Switch platform
  - Climate platform
  - Number platform
  - Custom services
- Configuration flow for easy setup
- Data persistence and history tracking
- Lovelace dashboard
- Multi-language support (French, English)
- Docker multi-architecture build support
- HTTP API for external integration
- Comprehensive logging and error handling

### Features

- Real-time sensor data reception
- Command sending to VMI
- Automatic device discovery
- Asyncio-based async operations
- Thread-safe message queue
- Automatic reconnection on connection loss
- Rate limiting and timeout handling
- Data validation and sanitization

## [Unreleased]

### Planned

- Advanced device discovery UI
- Data export (CSV, JSON)
- Energy consumption tracking
- Advanced automations templates
- Mobile notifications
- Custom device support
- REST API extended functionality
