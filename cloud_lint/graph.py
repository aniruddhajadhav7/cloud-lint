from .models import BlueprintReport


class MermaidGraphGenerator:
    def generate(self, report: BlueprintReport) -> str:
        """Generate a Mermaid.js flowchart representing the execution dependencies."""
        lines = [
            "graph TD",
            "    %% Stages",
            "    subgraph Generator",
            "        S1[Detect Datasource]",
            "    end",
            "    subgraph Local",
            "        S2[Local Configuration]",
            "    end",
            "    subgraph Network",
            "        S3[Network Configuration]",
            "    end",
            "    subgraph Config",
            "        S4[Main Configuration]",
            "    end",
            "    subgraph Final",
            "        S5[Final Scripts/Commands]",
            "    end",
            "",
            "    %% Stage Execution Order",
            "    S1 --> S2 --> S3 --> S4 --> S5",
            "",
            "    %% Modules detected",
        ]

        # Add modules as nodes
        for mod in report.modules_detected:
            # Map module to stage node
            stage = self._get_stage_for_module(mod, report)
            lines.append(f"    {mod}([{mod}])")
            
            # Simple link to stage grouping for visualization
            if stage == "Generator":
                lines.append(f"    S1 -.- {mod}")
            elif stage == "Local":
                lines.append(f"    S2 -.- {mod}")
            elif stage == "Network":
                lines.append(f"    S3 -.- {mod}")
            elif stage == "Config":
                lines.append(f"    S4 -.- {mod}")
            else:
                lines.append(f"    S5 -.- {mod}")

        lines.append("")
        lines.append("    %% Dependencies")
        for dep in report.dependencies:
            lines.append(f"    {dep.source} -->|{dep.reason}| {dep.target}")

        # Add styling
        lines.extend([
            "",
            "    classDef default fill:#161b22,stroke:#30363d,stroke-width:2px,color:#e6edf3;",
            "    classDef stage fill:#0d1117,stroke:#58a6ff,stroke-width:2px,color:#58a6ff;",
            "    class S1,S2,S3,S4,S5 stage;"
        ])

        return "\n".join(lines)
        
    def _get_stage_for_module(self, mod: str, report: BlueprintReport) -> str:
        for group in report.stage_groups:
            for step in group.steps:
                if step.module == mod:
                    return group.stage.value
        return "Config"
