# Complete JSON Schema for cloud-init validation

CLOUD_INIT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "packages": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1
            }
        },
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "sudo": {"type": "string"},
                    "shell": {"type": "string"},
                    "ssh_authorized_keys": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^ssh-"
                        }
                    },
                    "groups": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "lock_passwd": {"type": "boolean"},
                    "home": {"type": "string"}
                }
            }
        },
        "write_files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "permissions": {
                        "type": "string",
                        "pattern": "^[0-7]{4}$"
                    },
                    "owner": {"type": "string"},
                    "encoding": {"type": "string"},
                    "append": {"type": "boolean"}
                }
            }
        },
        "runcmd": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                ]
            }
        },
        "bootcmd": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                ]
            }
        },
        "hostname": {"type": "string"},
        "timezone": {"type": "string"},
        "locale": {"type": "string"},
        "ssh_authorized_keys": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^ssh-"
            }
        },
        "final_message": {"type": "string"},
        "package_update": {"type": "boolean"},
        "package_upgrade": {"type": "boolean"},
        "power_state": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["poweroff", "reboot", "halt"]
                },
                "message": {"type": "string"},
                "timeout": {"type": "integer"}
            }
        }
    }
}
