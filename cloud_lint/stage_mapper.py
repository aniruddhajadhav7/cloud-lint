from typing import List, Any, Dict
from .models import ExecutionStep, CloudInitStage, StageGroup
from .constants import MODULE_STAGE_MAP, MODULE_ORDER


class StageMapper:
    def map(self, data: dict) -> List[ExecutionStep]:
        """Map all detected modules to their execution stages and steps."""
        steps = []
        
        # Always add Generator step
        steps.append(ExecutionStep(
            stage=CloudInitStage.GENERATOR,
            module="generator",
            action="Detect datasource",
            order=0,
            icon="⚡"
        ))

        for key, value in data.items():
            if key not in MODULE_STAGE_MAP:
                continue
                
            if key == "packages":
                steps.extend(self._map_packages(value))
            elif key == "users":
                steps.extend(self._map_users(value))
            elif key == "write_files":
                steps.extend(self._map_write_files(value))
            elif key == "runcmd":
                steps.extend(self._map_runcmd(value))
            elif key == "bootcmd":
                steps.extend(self._map_bootcmd(value))
            elif key == "power_state":
                steps.extend(self._map_power_state(value))
            else:
                steps.extend(self._map_generic(key, value))
                
        # Sort by order
        steps.sort(key=lambda x: x.order)
        return steps
    
    def _map_packages(self, packages: list) -> List[ExecutionStep]:
        if not packages:
            return []
        
        pkgs = [p if isinstance(p, str) else str(p) for p in packages if p]
        
        return [ExecutionStep(
            stage=CloudInitStage.CONFIG,
            module="packages",
            action=f"Install packages ({len(pkgs)} pkgs)",
            details=pkgs,
            order=MODULE_ORDER.get("packages", 50),
            icon="📦"
        )]
    
    def _map_users(self, users: list) -> List[ExecutionStep]:
        if not users:
            return []
            
        names = [u.get("name", "unknown") for u in users if isinstance(u, dict)]
        
        return [ExecutionStep(
            stage=CloudInitStage.CONFIG,
            module="users",
            action=f"Create users ({len(names)} user{'s' if len(names) != 1 else ''})",
            details=names,
            order=MODULE_ORDER.get("users", 20),
            icon="👤"
        )]
    
    def _map_write_files(self, files: list) -> List[ExecutionStep]:
        if not files:
            return []
            
        paths = [f.get("path", "unknown") for f in files if isinstance(f, dict)]
        
        return [ExecutionStep(
            stage=CloudInitStage.CONFIG,
            module="write_files",
            action=f"Write files ({len(paths)} file{'s' if len(paths) != 1 else ''})",
            details=paths,
            order=MODULE_ORDER.get("write_files", 50),
            icon="📄"
        )]
    
    def _map_runcmd(self, commands: list) -> List[ExecutionStep]:
        if not commands:
            return []
            
        cmds = []
        for c in commands:
            if isinstance(c, str):
                cmds.append(c)
            elif isinstance(c, list):
                cmds.append(" ".join(str(i) for i in c))
                
        return [ExecutionStep(
            stage=CloudInitStage.FINAL,
            module="runcmd",
            action=f"Run commands ({len(cmds)} cmd{'s' if len(cmds) != 1 else ''})",
            details=cmds,
            order=MODULE_ORDER.get("runcmd", 60),
            icon="🚀"
        )]
    
    def _map_bootcmd(self, commands: list) -> List[ExecutionStep]:
        if not commands:
            return []
            
        cmds = []
        for c in commands:
            if isinstance(c, str):
                cmds.append(c)
            elif isinstance(c, list):
                cmds.append(" ".join(str(i) for i in c))
                
        return [ExecutionStep(
            stage=CloudInitStage.LOCAL,
            module="bootcmd",
            action=f"Execute boot commands ({len(cmds)} cmd{'s' if len(cmds) != 1 else ''})",
            details=cmds,
            order=MODULE_ORDER.get("bootcmd", 1),
            icon="⚙️"
        )]
    
    def _map_power_state(self, config: dict) -> List[ExecutionStep]:
        if not config:
            return []
            
        mode = config.get("mode", "unknown")
        
        return [ExecutionStep(
            stage=CloudInitStage.FINAL,
            module="power_state",
            action=f"Power state: {mode}",
            order=MODULE_ORDER.get("power_state", 99),
            icon="🔌"
        )]
    
    def _map_generic(self, module: str, data: Any) -> List[ExecutionStep]:
        stage_name = MODULE_STAGE_MAP.get(module, "Config")
        stage_enum = CloudInitStage(stage_name)
        
        details = []
        if isinstance(data, (str, int, bool)):
            details.append(str(data))
        elif isinstance(data, list):
            details.extend([str(i) for i in data])
            
        return [ExecutionStep(
            stage=stage_enum,
            module=module,
            action=f"Configure {module}",
            details=details,
            order=MODULE_ORDER.get(module, 50),
            icon="🔧"
        )]
    
    def get_stage_groups(self, steps: List[ExecutionStep]) -> List[StageGroup]:
        """Group steps by stage preserving stage order."""
        stage_order = [
            CloudInitStage.GENERATOR,
            CloudInitStage.LOCAL,
            CloudInitStage.NETWORK,
            CloudInitStage.CONFIG,
            CloudInitStage.FINAL
        ]
        
        groups_dict: Dict[CloudInitStage, List[ExecutionStep]] = {stage: [] for stage in stage_order}
        
        for step in steps:
            groups_dict[step.stage].append(step)
            
        result = []
        for stage in stage_order:
            if groups_dict[stage] or stage == CloudInitStage.GENERATOR:
                result.append(StageGroup(stage=stage, steps=groups_dict[stage]))
                
        return result
