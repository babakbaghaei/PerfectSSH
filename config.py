"""
PerfectSSH - Configuration Manager
Handles loading, saving, and managing application configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).parent / "config.json"
        self.config = self._load_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "mode": "1_hop",
            "hop1": {"ip": "", "port": "22", "user": "root", "pass": ""},
            "hop2": {"ip": "", "port": "22", "user": "root", "pass": ""},
            "local_port": 1080,
            "compression": False
        }

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self._save_config(self._default_config())
            return self._default_config()
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._default_config()

    def _save_config(self, data: Dict[str, Any]) -> None:
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=4)
        self.config = data

    def save(self) -> None:
        self._save_config(self.config)

    def is_configured(self) -> bool:
        """Checks if the minimal required configuration exists."""
        return bool(self.config['hop1']['ip'])

    def validate_config(self) -> bool:
        """Validates the current configuration."""
        required_fields = ['mode', 'hop1', 'hop2', 'local_port']
        for field in required_fields:
            if field not in self.config:
                return False
        
        if self.config['mode'] not in ['1_hop', '2_hop']:
            return False
        
        if not isinstance(self.config['local_port'], int) or not (1024 <= self.config['local_port'] <= 65535):
            return False
        
        # Validate hop1
        if not self._validate_hop_config(self.config['hop1']):
            return False
        
        # Validate hop2 if in bridge mode
        if self.config['mode'] == '2_hop' and not self._validate_hop_config(self.config['hop2']):
            return False
        
        return True

    def _validate_hop_config(self, hop: Dict[str, Any]) -> bool:
        """Validates a single hop configuration."""
        required_hop_fields = ['ip', 'port', 'user', 'pass']
        for field in required_hop_fields:
            if field not in hop:
                return False
        
        # Basic IP validation (simple check)
        if not hop['ip'] or not isinstance(hop['ip'], str):
            return False
        
        # Port validation
        try:
            port = int(hop['port'])
            if not (1 <= port <= 65535):
                return False
        except (ValueError, TypeError):
            return False
        
        return True