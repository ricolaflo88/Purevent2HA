"""
Purevent2HA Utilities
Utility functions and helpers
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Load JSON file safely"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return {}


def save_json_file(filepath: Path, data: Dict[str, Any]) -> bool:
    """Save JSON file safely"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def parse_env_int(key: str, default: int) -> int:
    """Parse integer environment variable"""
    import os
    try:
        return int(os.getenv(key, default))
    except ValueError:
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default


def parse_env_str(key: str, default: str) -> str:
    """Parse string environment variable"""
    import os
    return os.getenv(key, default)


def get_device_name(device_type: str) -> str:
    """Get friendly name for device type"""
    names = {
        'D1079-01-00': 'VMI Purevent',
        'A5-09-04': 'Capteur CO2',
        'A5-04-01': 'Capteur T°/Humidité',
        'D1079-00-00': 'Assistant Ventilairsec',
    }
    return names.get(device_type, 'Unknown Device')


def convert_co2_value(raw: int, rorg: str = 'A5') -> float:
    """Convert raw CO2 sensor value to ppm"""
    if rorg == 'A5':
        # A5-09-04: 0-2500 ppm
        return (raw / 2047.0) * 2500
    return 0.0


def convert_temp_value(raw: int, scale: float = 51.0) -> float:
    """Convert raw temperature value to Celsius"""
    # Standard scaling for A5-04-01: 0-51°C
    if raw <= 255:
        return (raw / 255.0) * scale
    return 0.0


def convert_humidity_value(raw: int) -> float:
    """Convert raw humidity value to percentage"""
    if raw <= 255:
        return (raw / 255.0) * 100
    return 0.0


def format_uptime(seconds: int) -> str:
    """Format uptime in seconds to human readable"""
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)
