import jsonschema
from typing import List, Tuple, Any

from .models import ValidationResult, ValidationError, ValidationWarning
from .schema import CLOUD_INIT_SCHEMA
from .constants import SUPPORTED_MODULES


class CloudInitValidator:
    def __init__(self):
        self.schema = CLOUD_INIT_SCHEMA
    
    def validate(self, content: str, data: dict) -> ValidationResult:
        """Run all validations and return ValidationResult."""
        result = ValidationResult(
            yaml_valid=True,
            schema_valid=True,
            cloud_init_compatible=False
        )
        
        # Check cloud-config header
        is_cloud_config, header_warnings = self.check_cloud_config_header(content)
        result.cloud_init_compatible = is_cloud_config
        result.warnings.extend(header_warnings)
        
        # Validate JSON Schema
        schema_valid, schema_errors = self.validate_schema(data)
        result.schema_valid = schema_valid
        result.errors.extend(schema_errors)
        
        # Check custom warnings
        result.warnings.extend(self.check_empty_values(data))
        result.warnings.extend(self.check_unknown_modules(data))
        result.warnings.extend(self.check_permission_format(data))
        
        return result
    
    def validate_yaml_syntax(self, content: str) -> Tuple[bool, List[ValidationError]]:
        """Check YAML is parseable. (Usually handled by parser, kept for API compat)"""
        return True, []
    
    def validate_schema(self, data: dict) -> Tuple[bool, List[ValidationError]]:
        """Validate against cloud-init JSON schema."""
        errors = []
        validator = jsonschema.Draft7Validator(self.schema)
        for error in validator.iter_errors(data):
            path = ".".join([str(p) for p in error.path]) if error.path else "root"
            errors.append(ValidationError(field=path, message=error.message))
            
        return len(errors) == 0, errors
    
    def check_cloud_config_header(self, content: str) -> Tuple[bool, List[ValidationWarning]]:
        """Check for #cloud-config header."""
        warnings = []
        is_cloud_config = content.lstrip().startswith("#cloud-config")
        if not is_cloud_config:
            warnings.append(ValidationWarning(
                message="Missing '#cloud-config' header at the top of the file.",
                suggestion="Add '#cloud-config' as the very first line."
            ))
        return is_cloud_config, warnings
    
    def check_empty_values(self, data: dict) -> List[ValidationWarning]:
        """Find null/empty values in arrays."""
        warnings = []
        for key, value in data.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if item is None:
                        warnings.append(ValidationWarning(
                            field=f"{key}[{i}]",
                            message=f"Empty or null item found in '{key}'.",
                            suggestion="Remove the empty list item or provide a value."
                        ))
        return warnings
    
    def check_unknown_modules(self, data: dict) -> List[ValidationWarning]:
        """Warn about unrecognized cloud-init modules."""
        warnings = []
        for key in data.keys():
            if key not in SUPPORTED_MODULES and key != "runcmd": # runcmd is standard, but check carefully
                warnings.append(ValidationWarning(
                    field=key,
                    message=f"Unrecognized module or key '{key}'.",
                    suggestion="Check if this is a supported cloud-init module or a typo."
                ))
        return warnings
    
    def check_permission_format(self, data: dict) -> List[ValidationWarning]:
        """Validate file permissions format (must be octal string like 0644)."""
        warnings = []
        write_files = data.get("write_files", [])
        if isinstance(write_files, list):
            for i, f in enumerate(write_files):
                if isinstance(f, dict) and "permissions" in f:
                    perms = f["permissions"]
                    if not isinstance(perms, str) or not perms.isdigit():
                        warnings.append(ValidationWarning(
                            field=f"write_files[{i}].permissions",
                            message="Permissions should ideally be a string like '0644'.",
                            suggestion="Quote the permissions value to avoid octal conversion issues in YAML."
                        ))
        return warnings
