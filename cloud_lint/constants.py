CLOUD_INIT_STAGES = {
    "Generator": {
        "description": "Determines if cloud-init should run. Detects datasource.",
        "modules": []
    },
    "Local": {
        "description": "Runs before network. Finds datasource. Applies local config.",
        "modules": ["bootcmd"]
    },
    "Network": {
        "description": "Runs after network available. Applies network configuration.",
        "modules": ["network"]
    },
    "Config": {
        "description": "Main configuration phase. Applies all cc_* modules.",
        "modules": [
            "hostname", "locale", "timezone", "users", "groups",
            "ssh_authorized_keys", "ssh_pwauth", "disable_root",
            "disk_setup", "mounts", "package_update", "package_upgrade",
            "packages", "write_files", "apt"
        ]
    },
    "Final": {
        "description": "Runs user scripts and commands. Very last stage.",
        "modules": ["runcmd", "final_message", "power_state"]
    }
}

MODULE_STAGE_MAP = {
    "bootcmd": "Local",
    "network": "Network",
    "hostname": "Config",
    "locale": "Config",
    "timezone": "Config",
    "users": "Config",
    "groups": "Config",
    "ssh_authorized_keys": "Config",
    "ssh_pwauth": "Config",
    "disable_root": "Config",
    "disk_setup": "Config",
    "mounts": "Config",
    "apt": "Config",
    "package_update": "Config",
    "package_upgrade": "Config",
    "packages": "Config",
    "write_files": "Config",
    "runcmd": "Final",
    "final_message": "Final",
    "power_state": "Final",
}

MODULE_ORDER = {
    "bootcmd": 1,
    "network": 2,
    "hostname": 10,
    "locale": 11,
    "timezone": 12,
    "users": 20,
    "groups": 21,
    "ssh_authorized_keys": 22,
    "ssh_pwauth": 23,
    "disable_root": 24,
    "disk_setup": 30,
    "mounts": 31,
    "apt": 40,
    "package_update": 41,
    "package_upgrade": 42,
    "packages": 43,
    "write_files": 50,
    "runcmd": 60,
    "final_message": 70,
    "power_state": 99,
}

RISK_PATTERNS = [
    {
        "pattern": r"curl\s+['\"]?https?://[^\s|]+\s*\|\s*(ba)?sh",
        "level": "CRITICAL",
        "description": "Downloads and executes remote code — classic supply chain attack vector",
        "suggestion": "Download file first, verify checksum, then execute"
    },
    {
        "pattern": r"wget\s+['\"]?https?://[^\s|]+\s*[|;]\s*(ba)?sh",
        "level": "CRITICAL",
        "description": "Pipes downloaded content to shell — extreme risk",
        "suggestion": "Use package manager or verify downloaded scripts before execution"
    },
    {
        "pattern": r"chmod\s+[0-7]*777",
        "level": "HIGH",
        "description": "World-writable permissions — any user can modify this file",
        "suggestion": "Use least-privilege permissions: 644 for files, 755 for executables"
    },
    {
        "pattern": r"rm\s+-[rf]{1,2}\s+/(?!\s)",
        "level": "CRITICAL",
        "description": "Recursive delete from root — potentially destructive",
        "suggestion": "Double-check the target path is correct and scoped"
    },
    {
        "pattern": r"wget\s+http://(?!.*https)",
        "level": "MEDIUM",
        "description": "Downloading over unencrypted HTTP — content can be intercepted",
        "suggestion": "Use HTTPS URLs and verify checksums"
    },
    {
        "pattern": r"curl\s+http://(?!.*https)",
        "level": "MEDIUM",
        "description": "HTTP (non-TLS) download — vulnerable to MITM",
        "suggestion": "Use HTTPS and verify file integrity with checksums"
    },
    {
        "pattern": r"(password|passwd|secret|api_key)\s*[=:]\s*['\"]?\S+",
        "level": "HIGH",
        "description": "Hardcoded credential detected in config",
        "suggestion": "Use secrets manager or environment variables instead"
    },
    {
        "pattern": r"PermitRootLogin\s+yes",
        "level": "HIGH",
        "description": "SSH root login enabled — reduces security significantly",
        "suggestion": "Set PermitRootLogin no and use sudo instead"
    },
    {
        "pattern": r"PasswordAuthentication\s+yes",
        "level": "MEDIUM",
        "description": "SSH password authentication enabled — weaker than key-based",
        "suggestion": "Use PasswordAuthentication no with SSH keys only"
    },
    {
        "pattern": r"(ufw\s+disable|iptables\s+-[FXZ])",
        "level": "HIGH",
        "description": "Firewall disabled or flushed — system exposed to network",
        "suggestion": "Keep firewall enabled with specific rules instead of disabling"
    },
    {
        "pattern": r"NOPASSWD\s*:\s*ALL",
        "level": "MEDIUM",
        "description": "Passwordless sudo for all commands",
        "suggestion": "Limit NOPASSWD to specific required commands only"
    },
    {
        "pattern": r"dd\s+if=.*of=/dev/[a-z]",
        "level": "HIGH",
        "description": "Writing directly to block device — can destroy disk data",
        "suggestion": "Triple-check device path before executing dd operations"
    },
    {
        "pattern": r"eval\s+\$\(",
        "level": "MEDIUM",
        "description": "Dynamic code evaluation — can be exploited if input is controlled",
        "suggestion": "Avoid eval where possible; validate input if required"
    },
    {
        "pattern": r"chmod\s+[a-z]+\+s",
        "level": "HIGH",
        "description": "Setting SUID/SGID bit — can allow privilege escalation",
        "suggestion": "Avoid SUID/SGID unless absolutely necessary"
    },
]

RISK_WEIGHTS = {
    "CRITICAL": 30,
    "HIGH": 15,
    "MEDIUM": 7,
    "LOW": 2,
}

MODULE_DESCRIPTIONS = {
    "packages": "Install system packages via apt/yum",
    "users": "Create system users and configure access",
    "write_files": "Write files to the filesystem",
    "runcmd": "Execute shell commands at final stage",
    "bootcmd": "Execute commands before other modules (early boot)",
    "ssh_authorized_keys": "Add SSH public keys for authentication",
    "hostname": "Set the system hostname",
    "timezone": "Configure system timezone",
    "locale": "Set system locale and language",
    "mounts": "Configure filesystem mounts",
    "disk_setup": "Partition and format disks",
    "package_update": "Update package lists (apt update)",
    "package_upgrade": "Upgrade all installed packages",
    "ntp": "Configure NTP time synchronization",
    "final_message": "Display message when cloud-init completes",
    "power_state": "Control system power state after init",
    "network": "Configure network interfaces",
    "apt": "Configure apt sources and preferences",
}

SUPPORTED_MODULES = [
    "bootcmd", "hostname", "locale", "timezone", "users", "groups",
    "ssh_authorized_keys", "ssh_pwauth", "disable_root", "disk_setup",
    "mounts", "apt", "package_update", "package_upgrade", "packages",
    "write_files", "runcmd", "final_message", "power_state", "network",
    "chpasswd", "ntp", "resolv_conf", "manage_etc_hosts", "set_hostname",
    "update_hostname", "update_etc_hosts", "ca_certs", "puppet", "chef",
    "salt_minion", "mcollective", "byobu", "landscape", "snap"
]
