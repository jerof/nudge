"""
Configuration management for Nudge
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Config:
    """Manages Nudge configuration"""
    
    # Default configuration
    DEFAULTS = {
        "paths": {
            "log_dirs": [
                "~/.config/claude/logs/",
                "~/.claude/logs/",
                "/tmp/claude-code/",
            ],
            "manual_log": "~/.nudge/claude.log"
        },
        "notification": {
            "title": "Claude Code",
            "message": "Claude has asked a question",
            "sound": "default"
        },
        "focus": {
            "terminals": ["Ghostty", "iTerm", "Terminal"],
            "ides": ["Code", "Cursor"]
        },
        "daemon": {
            "check_interval": 1,  # seconds
            "max_lines_per_check": 100
        }
    }
    
    def __init__(self, config_path: Path = None):
        """
        Initialize configuration
        
        Args:
            config_path: Custom config path (defaults to ~/.nudge/config.toml)
        """
        self.config_path = config_path or (Path.home() / ".nudge" / "config.toml")
        self.data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        try:
            import tomllib
        except ImportError:
            # Python < 3.11
            try:
                import tomli as tomllib
            except ImportError:
                logger.warning("tomllib not available, using defaults")
                return self.DEFAULTS.copy()
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'rb') as f:
                    config = tomllib.load(f)
                    # Merge with defaults
                    return self._merge_configs(self.DEFAULTS, config)
            except Exception as e:
                logger.error(f"Failed to load config: {e}, using defaults")
        
        return self.DEFAULTS.copy()
    
    def _merge_configs(self, defaults: Dict, custom: Dict) -> Dict:
        """Recursively merge custom config with defaults"""
        result = defaults.copy()
        
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Dot-separated key (e.g., "paths.log_dirs")
            default: Default value if key not found
        """
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_log_paths(self) -> List[Path]:
        """Get list of log paths to monitor (expanded)"""
        paths = self.get("paths.log_dirs", [])
        manual = self.get("paths.manual_log")
        
        result = []
        
        for p in paths:
            expanded = Path(p).expanduser()
            if expanded.exists():
                result.append(expanded)
        
        # Add manual log path if it exists
        if manual:
            manual_expanded = Path(manual).expanduser()
            if manual_expanded.exists():
                result.append(manual_expanded)
        
        return result
    
    def ensure_config_dir(self):
        """Ensure ~/.nudge directory exists"""
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Config directory ready: {config_dir}")
    
    def save_default_config(self):
        """Save default configuration to file"""
        self.ensure_config_dir()
        
        try:
            import toml
            with open(self.config_path, 'w') as f:
                toml.dump(self.DEFAULTS, f)
            logger.info(f"Default config saved to {self.config_path}")
        except ImportError:
            logger.warning("toml not available, config not saved")
