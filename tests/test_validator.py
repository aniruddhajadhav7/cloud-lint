from cloud_lint.validator import CloudInitValidator

def test_valid_config():
    validator = CloudInitValidator()
    content = "#cloud-config\npackages:\n  - nginx"
    data = {"packages": ["nginx"]}
    
    result = validator.validate(content, data)
    assert result.yaml_valid is True
    assert result.schema_valid is True
    assert result.cloud_init_compatible is True
    assert len(result.errors) == 0

def test_missing_required_field_schema_error():
    validator = CloudInitValidator()
    content = "#cloud-config\nusers:\n  - sudo: ALL=(ALL)"
    data = {"users": [{"sudo": "ALL=(ALL)"}]}
    
    result = validator.validate(content, data)
    assert result.schema_valid is False
    assert len(result.errors) > 0
    assert "name" in result.errors[0].message

def test_unknown_module_returns_warning():
    validator = CloudInitValidator()
    content = "#cloud-config\nnot_a_module:\n  - test"
    data = {"not_a_module": ["test"]}
    
    result = validator.validate(content, data)
    assert len(result.warnings) > 0
    assert any("not_a_module" in w.message for w in result.warnings)

def test_empty_list_item_returns_warning():
    validator = CloudInitValidator()
    content = "#cloud-config\npackages:\n  - nginx\n  - null"
    data = {"packages": ["nginx", None]}
    
    result = validator.validate(content, data)
    assert len(result.warnings) > 0
    assert any("Empty or null item" in w.message for w in result.warnings)

def test_missing_cloud_config_header():
    validator = CloudInitValidator()
    content = "packages:\n  - nginx"
    data = {"packages": ["nginx"]}
    
    result = validator.validate(content, data)
    assert result.cloud_init_compatible is False
    assert any("Missing '#cloud-config' header" in w.message for w in result.warnings)
