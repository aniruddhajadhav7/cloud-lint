import typer
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from . import __version__
from .models import BlueprintReport
from .blueprint import BlueprintEngine
from .report import ReportGenerator

app = typer.Typer(
    name="cloud-lint",
    help="Offline Cloud-Init Execution Blueprint Visualizer",
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True)

def get_engine() -> BlueprintEngine:
    return BlueprintEngine()

@app.command()
def version():
    """Show version info."""
    console.print(f"☁ Cloud-Lint v{__version__}")

@app.command()
def analyze(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Cloud-init YAML file"),
    strict: bool = typer.Option(False, "--strict", help="Fail on warnings too"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output (exit code only)")
):
    """Full analysis with beautiful terminal output"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    if quiet:
        sys.exit(get_exit_code(report, strict))

    # Header Panel
    console.print(Panel(
        f"[bold blue]☁  Cloud-Lint v{__version__}[/]\nOffline Cloud-Init Execution Blueprint",
        expand=False,
        border_style="blue"
    ))
    
    console.print(f"\nAnalyzing: [bold]{file.name}[/]\n")
    
    # Validation checks
    val = report.validation
    console.print(f"[{'green' if val.yaml_valid else 'red'}]✓{'[/]' if val.yaml_valid else '✗[/]'} YAML Valid")
    console.print(f"[{'green' if val.schema_valid else 'red'}]✓{'[/]' if val.schema_valid else '✗[/]'} Schema Valid")
    console.print(f"[{'green' if val.cloud_init_compatible else 'yellow'}]✓{'[/]' if val.cloud_init_compatible else '![/]'} Cloud-Init Compatible\n")
    
    if not report.valid:
        for err in val.errors:
            console.print(f"[red]Error:[/] {err.field or 'root'}: {err.message}")
        sys.exit(1)
        
    # Blueprint Panel
    blueprint_text = ""
    for step in report.execution_steps:
        blueprint_text += f"[bold cyan][{step.stage.value:^9}][/]  {step.action}\n"
        blueprint_text += "       ↓\n"
    blueprint_text += "[bold cyan][  Ready  ][/]  System ready"
    
    console.print(Panel(blueprint_text, title="Execution Blueprint", expand=False, border_style="cyan"))
    
    # Risk Panel
    risk_color = "green"
    if report.risk_level.value == "CRITICAL": risk_color = "red"
    elif report.risk_level.value == "HIGH": risk_color = "magenta"
    elif report.risk_level.value == "MEDIUM": risk_color = "yellow"
    
    risk_text = f"Risk Score: {report.risk_score}/100  [{risk_color}][{report.risk_level.value}][/]\n\n"
    for r in report.risk_items:
        risk_text += f"[bold {risk_color}]⚠ {r.level.value:^8}[/] {r.command[:30]:<30} {r.description}\n"
        
    console.print(Panel(risk_text.strip(), title="Risk Analysis", expand=False, border_style=risk_color))
    
    # Summary Panel
    summary_text = (
        f"Packages : {report.total_packages:<4} Users: {report.total_users:<4} "
        f"Files: {report.total_files:<4} Commands: {report.total_commands:<4}\n"
        f"Warnings : {report.warnings_count:<4} Errors: {report.errors_count:<4} "
        f"Risk: [{risk_color}]{report.risk_level.value}[/]"
    )
    console.print(Panel(summary_text, title="Summary", expand=False, border_style="white"))
    
    sys.exit(get_exit_code(report, strict))


@app.command()
def validate(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    strict: bool = typer.Option(False, "--strict", help="Fail on warnings")
):
    """Validation only (YAML + Schema)"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    if report.valid:
        console.print("[green]✓ File is valid[/]")
        sys.exit(get_exit_code(report, strict))
    else:
        console.print("[red]✗ File is invalid[/]")
        for err in report.validation.errors:
            console.print(f"  - {err.field or 'root'}: {err.message}")
        sys.exit(1)


@app.command()
def report(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    output: str = typer.Option("report.html", "--output", "-o", help="Output file path")
):
    """Generate interactive HTML report"""
    engine = get_engine()
    bp_report = engine.analyze_file(file)
    
    generator = ReportGenerator()
    html = generator.generate_html(bp_report)
    
    out_path = Path(output)
    out_path.write_text(html, encoding="utf-8")
    console.print(f"[green]Report generated at:[/] {out_path.absolute()}")


@app.command()
def json_out(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False)
):
    """JSON output for CI/CD"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    generator = ReportGenerator()
    data = generator._build_json_dict(report)
    
    console.print(json.dumps(data, indent=2))
    

@app.command()
def blueprint(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False)
):
    """Show execution blueprint only"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    table = Table(title="Execution Blueprint")
    table.add_column("Stage", style="cyan")
    table.add_column("Action", style="green")
    
    for step in report.execution_steps:
        table.add_row(step.stage.value, step.action)
        
    console.print(table)


@app.command()
def risks(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False)
):
    """Show risk analysis only"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    table = Table(title="Risk Analysis")
    table.add_column("Level", style="bold")
    table.add_column("Command")
    table.add_column("Description")
    
    for r in report.risk_items:
        color = "green"
        if r.level.value == "CRITICAL": color = "red"
        elif r.level.value == "HIGH": color = "magenta"
        elif r.level.value == "MEDIUM": color = "yellow"
        
        table.add_row(f"[{color}]{r.level.value}[/]", r.command, r.description)
        
    console.print(table)


@app.command()
def graph(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False)
):
    """Show dependency graph (Mermaid DSL)"""
    engine = get_engine()
    report = engine.analyze_file(file)
    
    from .graph import MermaidGraphGenerator
    g = MermaidGraphGenerator()
    dsl = g.generate(report)
    
    console.print(Syntax(dsl, "mermaid", theme="monokai", background_color="default"))


def get_exit_code(report: BlueprintReport, strict: bool) -> int:
    if not report.valid:
        return 1
    if report.risk_level.value in ("HIGH", "CRITICAL"):
        return 3
    if strict and report.warnings_count > 0:
        return 2
    return 0


if __name__ == "__main__":
    app()
