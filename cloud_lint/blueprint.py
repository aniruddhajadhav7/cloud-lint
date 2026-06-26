from pathlib import Path
from typing import List, Any
import datetime

from .parser import CloudInitParser
from .validator import CloudInitValidator
from .stage_mapper import StageMapper
from .analyzer import RiskAnalyzer
from .models import (
    BlueprintReport, PackageInfo, UserInfo, WriteFileInfo,
    MountInfo, DependencyEdge, ValidationError
)
from .constants import SUPPORTED_MODULES


class BlueprintEngine:
    def __init__(self):
        self.parser = CloudInitParser()
        self.validator = CloudInitValidator()
        self.stage_mapper = StageMapper()
        self.analyzer = RiskAnalyzer()
    
    def analyze_file(self, path: Path) -> BlueprintReport:
        """Full analysis pipeline for a file. Never raises — errors go in report."""
        report = BlueprintReport(filename=path.name)
        try:
            content = self.parser.get_raw_content(path)
            return self.analyze_string(content, filename=path.name)
        except Exception as e:
            report.validation.yaml_valid = False
            report.validation.errors.append(ValidationError(field="file", message=str(e)))
            report.errors_count = 1
            return report
            
    def analyze_string(self, content: str, filename: str = "stdin") -> BlueprintReport:
        """Full analysis pipeline from string."""
        report = BlueprintReport(filename=filename)
        
        try:
            data = self.parser.parse_string(content)
            report.validation.yaml_valid = True
        except Exception as e:
            report.validation.yaml_valid = False
            report.validation.errors.append(ValidationError(field="yaml", message=str(e)))
            report.errors_count = 1
            return report
            
        # Validation
        val_result = self.validator.validate(content, data)
        report.validation = val_result
        report.valid = val_result.yaml_valid and val_result.schema_valid
        
        # Extracted basic counts & modules
        report.modules_detected = [k for k in data.keys() if k in SUPPORTED_MODULES or k == "runcmd"]
        
        # Risk Analysis
        report.risk_items = self.analyzer.analyze(data)
        report.risk_score = self.analyzer.calculate_risk_score(report.risk_items)
        report.risk_level = self.analyzer.calculate_risk_level(report.risk_score)
        report.total_risks = len(report.risk_items)
        
        # Data Extraction
        report.packages = self._extract_packages(data)
        report.users = self._extract_users(data)
        report.write_files = self._extract_write_files(data)
        report.commands = self._extract_commands(data)
        report.bootcmds = self._extract_bootcmds(data)
        report.mounts = self._extract_mounts(data)
        
        report.total_packages = len(report.packages)
        report.total_users = len(report.users)
        report.total_files = len(report.write_files)
        report.total_commands = len(report.commands) + len(report.bootcmds)
        
        report.errors_count = len(report.validation.errors)
        report.warnings_count = len(report.validation.warnings)
        
        # Execution Steps
        report.execution_steps = self.stage_mapper.map(data)
        report.stage_groups = self.stage_mapper.get_stage_groups(report.execution_steps)
        
        # Dependencies
        report.dependencies = self._build_dependencies(data)
        
        return report
        
    def _extract_packages(self, data: dict) -> List[PackageInfo]:
        packages = []
        pkgs = data.get("packages", [])
        if isinstance(pkgs, list):
            for p in pkgs:
                if isinstance(p, str):
                    packages.append(PackageInfo(name=p))
                elif isinstance(p, list) and len(p) > 0:
                    name = str(p[0])
                    version = str(p[1]) if len(p) > 1 else None
                    packages.append(PackageInfo(name=name, version=version))
        return packages
        
    def _extract_users(self, data: dict) -> List[UserInfo]:
        users = []
        user_list = data.get("users", [])
        if isinstance(user_list, list):
            for u in user_list:
                if isinstance(u, dict) and "name" in u:
                    users.append(UserInfo(
                        name=str(u.get("name", "unknown")),
                        sudo=u.get("sudo"),
                        shell=u.get("shell"),
                        ssh_authorized_keys=u.get("ssh_authorized_keys", []),
                        groups=u.get("groups", []),
                        lock_passwd=u.get("lock_passwd"),
                        home=u.get("home")
                    ))
        return users
        
    def _extract_write_files(self, data: dict) -> List[WriteFileInfo]:
        files = []
        wf_list = data.get("write_files", [])
        if isinstance(wf_list, list):
            for f in wf_list:
                if isinstance(f, dict) and "path" in f:
                    content = f.get("content", "")
                    content_preview = content[:100] + "..." if len(content) > 100 else content
                    files.append(WriteFileInfo(
                        path=str(f.get("path", "unknown")),
                        permissions=str(f.get("permissions", "0644")),
                        owner=f.get("owner", "root:root"),
                        content_preview=content_preview,
                        encoding=f.get("encoding", "text/plain"),
                        append=bool(f.get("append", False))
                    ))
        return files
        
    def _extract_commands(self, data: dict) -> List[str]:
        return self._extract_cmd_list(data.get("runcmd", []))
        
    def _extract_bootcmds(self, data: dict) -> List[str]:
        return self._extract_cmd_list(data.get("bootcmd", []))
        
    def _extract_cmd_list(self, cmds: Any) -> List[str]:
        result = []
        if isinstance(cmds, list):
            for c in cmds:
                if isinstance(c, str):
                    result.append(c)
                elif isinstance(c, list):
                    result.append(" ".join(str(i) for i in c))
        return result
        
    def _extract_mounts(self, data: dict) -> List[MountInfo]:
        mounts = []
        mount_list = data.get("mounts", [])
        if isinstance(mount_list, list):
            for m in mount_list:
                if isinstance(m, list) and len(m) >= 2:
                    mounts.append(MountInfo(
                        device=str(m[0]),
                        mount_point=str(m[1]),
                        filesystem=str(m[2]) if len(m) > 2 else None,
                        options=str(m[3]) if len(m) > 3 else None
                    ))
        return mounts
        
    def _build_dependencies(self, data: dict) -> List[DependencyEdge]:
        """Build a dependency graph based on module execution order and logical dependencies."""
        deps = []
        modules = set(data.keys())
        
        if "packages" in modules and "runcmd" in modules:
            deps.append(DependencyEdge(source="packages", target="runcmd", reason="Commands may depend on installed packages"))
            
        if "write_files" in modules and "runcmd" in modules:
            deps.append(DependencyEdge(source="write_files", target="runcmd", reason="Commands may modify written files"))
            
        if "bootcmd" in modules and "runcmd" in modules:
            deps.append(DependencyEdge(source="bootcmd", target="runcmd", reason="Early boot commands run before final commands"))
            
        if "users" in modules and "runcmd" in modules:
            deps.append(DependencyEdge(source="users", target="runcmd", reason="Commands might execute as newly created users"))
            
        return deps
