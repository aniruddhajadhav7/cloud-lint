import re
from typing import List
from .models import RiskItem, RiskLevel
from .constants import RISK_PATTERNS, RISK_WEIGHTS


class RiskAnalyzer:
    def __init__(self):
        self.patterns = RISK_PATTERNS
    
    def analyze(self, data: dict) -> List[RiskItem]:
        """Scan entire config for risk patterns. Return all findings."""
        risks = []
        
        # Scan runcmd
        runcmds = data.get("runcmd", [])
        if isinstance(runcmds, list):
            risks.extend(self.scan_commands(runcmds, context="runcmd"))
            
        # Scan bootcmd
        bootcmds = data.get("bootcmd", [])
        if isinstance(bootcmds, list):
            risks.extend(self.scan_commands(bootcmds, context="bootcmd"))
            
        # Scan write_files
        write_files = data.get("write_files", [])
        if isinstance(write_files, list):
            risks.extend(self.scan_write_files(write_files))
            
        # Scan users for password/ssh config
        users = data.get("users", [])
        if isinstance(users, list):
            for i, user in enumerate(users):
                if isinstance(user, dict):
                    sudo = user.get("sudo", "")
                    if sudo:
                        risks.extend(self.scan_string(sudo, context=f"users[{i}].sudo"))
                        
        # Global SSH settings (often added as top-level though not standard cloud-init, 
        # or inside write_files/runcmd which is caught above)
        
        return risks
    
    def scan_commands(self, commands: list, context: str) -> List[RiskItem]:
        """Scan a list of commands against all risk patterns."""
        risks = []
        for i, cmd in enumerate(commands):
            cmd_str = ""
            if isinstance(cmd, str):
                cmd_str = cmd
            elif isinstance(cmd, list):
                cmd_str = " ".join(str(c) for c in cmd)
                
            if cmd_str:
                risks.extend(self.scan_string(cmd_str, context=f"{context}[{i}]"))
                
        return risks
    
    def scan_string(self, text: str, context: str) -> List[RiskItem]:
        """Scan a single string against all risk patterns using regex."""
        risks = []
        for pattern_def in self.patterns:
            try:
                if re.search(pattern_def["pattern"], text, re.IGNORECASE):
                    risks.append(RiskItem(
                        command=text[:100] + ("..." if len(text) > 100 else ""),
                        level=RiskLevel(pattern_def["level"]),
                        description=pattern_def["description"],
                        context=context,
                        suggestion=pattern_def["suggestion"]
                    ))
            except re.error:
                continue
        return risks
    
    def scan_write_files(self, files: list) -> List[RiskItem]:
        """Scan file content and permissions for risks."""
        risks = []
        for i, file_obj in enumerate(files):
            if not isinstance(file_obj, dict):
                continue
                
            context_prefix = f"write_files[{i}]"
            
            # Check permissions
            perms = str(file_obj.get("permissions", ""))
            if perms:
                # E.g. chmod 777 equivalent check
                if "777" in perms:
                    risks.append(RiskItem(
                        command=f"permissions: '{perms}'",
                        level=RiskLevel.HIGH,
                        description="World-writable file permissions configured",
                        context=f"{context_prefix}.permissions",
                        suggestion="Use restrictive permissions like '0644' or '0600'"
                    ))
            
            # Check content
            content = file_obj.get("content", "")
            if content and isinstance(content, str):
                risks.extend(self.scan_string(content, context=f"{context_prefix}.content"))
                
        return risks
    
    def calculate_risk_score(self, items: List[RiskItem]) -> int:
        """Calculate 0-100 risk score. Cap at 100."""
        score = sum(RISK_WEIGHTS.get(item.level.value, 0) for item in items)
        return min(score, 100)
    
    def calculate_risk_level(self, score: int) -> RiskLevel:
        """Convert numeric score to RiskLevel enum."""
        if score >= 60:
            return RiskLevel.CRITICAL
        elif score >= 35:
            return RiskLevel.HIGH
        elif score >= 15:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
