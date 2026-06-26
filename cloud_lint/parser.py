from pathlib import Path
from typing import List, Any
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from .exceptions import YAMLParseError, EmptyConfigError, FileNotFoundError


class CloudInitParser:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
    
    def parse_file(self, path: Path) -> dict:
        """Parse a cloud-init YAML file. Raises YAMLParseError on failure."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        content = self.get_raw_content(path)
        return self.parse_string(content)
    
    def parse_string(self, content: str) -> dict:
        """Parse cloud-init YAML from string."""
        if not content.strip():
            raise EmptyConfigError("The configuration is empty.")
            
        try:
            parsed = self.yaml.load(content)
            if parsed is None:
                raise EmptyConfigError("The configuration contains no valid YAML data.")
            if not isinstance(parsed, dict):
                raise YAMLParseError("Root element of cloud-init must be a dictionary.")
            return parsed
        except YAMLError as e:
            raise YAMLParseError(f"Failed to parse YAML: {e}")
    
    def is_cloud_config(self, content: str) -> bool:
        """Check if file starts with #cloud-config header."""
        return content.lstrip().startswith("#cloud-config")
    
    def get_raw_content(self, path: Path) -> str:
        """Read raw file content."""
        try:
            return path.read_text(encoding="utf-8")
        except IOError as e:
            raise FileNotFoundError(f"Cannot read file: {e}")
    
    def detect_duplicate_keys(self, content: str) -> List[str]:
        """Detect duplicate YAML keys. (Basic implementation relying on ruamel.yaml behavior)"""
        # ruamel.yaml raises DuplicateKeyError on duplicate keys during load.
        # So typically `parse_string` catches it.
        # Alternatively, we could do regex parsing here if necessary.
        duplicates = []
        try:
            self.yaml.load(content)
        except YAMLError as e:
            err_str = str(e).lower()
            if "duplicate" in err_str:
                duplicates.append("Duplicate key detected")
        return duplicates
