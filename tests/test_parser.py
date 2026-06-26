import pytest
from pathlib import Path
from cloud_lint.parser import CloudInitParser
from cloud_lint.exceptions import YAMLParseError, EmptyConfigError, FileNotFoundError

def test_parse_valid_yaml(basic_yaml):
    parser = CloudInitParser()
    data = parser.parse_string(basic_yaml)
    assert isinstance(data, dict)
    assert "packages" in data
    assert "nginx" in data["packages"]

def test_parse_invalid_yaml(invalid_yaml):
    parser = CloudInitParser()
    with pytest.raises(YAMLParseError):
        parser.parse_string(invalid_yaml)

def test_parse_empty_file():
    parser = CloudInitParser()
    with pytest.raises(EmptyConfigError):
        parser.parse_string("   \n  \t  ")

def test_parse_cloud_config_header(basic_yaml):
    parser = CloudInitParser()
    assert parser.is_cloud_config(basic_yaml) is True

def test_detect_duplicate_keys():
    yaml_str = """
#cloud-config
packages:
  - a
packages:
  - b
    """
    parser = CloudInitParser()
    duplicates = parser.detect_duplicate_keys(yaml_str)
    assert len(duplicates) > 0
    with pytest.raises(YAMLParseError):
        parser.parse_string(yaml_str)

def test_parse_file_not_found():
    parser = CloudInitParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("/nonexistent/file.yaml"))
