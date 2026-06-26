import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from .models import BlueprintReport
from .graph import MermaidGraphGenerator


class ReportGenerator:
    def __init__(self):
        # Look for templates in the same directory
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Add custom filters
        self.env.filters["tojson"] = lambda obj: json.dumps(
            obj.model_dump() if hasattr(obj, "model_dump") else obj, 
            indent=2
        )
        
    def generate_html(self, report: BlueprintReport) -> str:
        """Generate a complete standalone HTML report from a blueprint."""
        template = self.env.get_template("report.html.j2")
        
        # Generate mermaid graph
        graph_generator = MermaidGraphGenerator()
        mermaid_dsl = graph_generator.generate(report)
        
        # Build JSON string representing output for the Raw JSON block
        json_output = self._build_json_dict(report)
        raw_json_str = json.dumps(json_output, indent=2)
        
        return template.render(
            report=report,
            mermaid_dsl=mermaid_dsl,
            raw_json=raw_json_str
        )
        
    def _build_json_dict(self, report: BlueprintReport) -> dict:
        """Convert report to the JSON schema format specified for CI/CD."""
        return {
            "valid": report.valid,
            "yaml_valid": report.validation.yaml_valid,
            "schema_valid": report.validation.schema_valid,
            "cloud_init_compatible": report.validation.cloud_init_compatible,
            "warnings": report.warnings_count,
            "errors": report.errors_count,
            "risk_score": report.risk_score,
            "risk_level": report.risk_level.value,
            "modules": report.modules_detected,
            "packages": [p.name for p in report.packages],
            "users": [u.name for u in report.users],
            "files": [f.path for f in report.write_files],
            "commands": report.commands + report.bootcmds,
            "risks": [
                {
                    "command": r.command,
                    "level": r.level.value,
                    "description": r.description
                } for r in report.risk_items
            ],
            "execution_order": [
                f"{step.stage.value}: {step.action}" for step in report.execution_steps
            ],
            "dependencies": [
                {"source": d.source, "target": d.target, "reason": d.reason}
                for d in report.dependencies
            ]
        }
