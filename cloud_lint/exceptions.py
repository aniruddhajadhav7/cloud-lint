class CloudLintError(Exception):
    """Base class for all Cloud-Lint exceptions."""
    pass


class YAMLParseError(CloudLintError):
    """Raised when the YAML file cannot be parsed."""
    pass


class SchemaValidationError(CloudLintError):
    """Raised when the parsed YAML does not match the expected cloud-init schema."""
    pass


class UnsupportedModuleError(CloudLintError):
    """Raised when an unknown module is used in the configuration."""
    pass


class FileNotFoundError(CloudLintError):
    """Raised when the input file is missing or cannot be read."""
    pass


class EmptyConfigError(CloudLintError):
    """Raised when the input file is empty or only contains comments."""
    pass
