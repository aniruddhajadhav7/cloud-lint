import json
from typer.testing import CliRunner
from cloud_lint.cli import app

runner = CliRunner()

def test_cloud_lint_analyze(tmp_path):
    config = tmp_path / "valid.yaml"
    config.write_text("#cloud-config\npackages:\n  - nginx")
    
    result = runner.invoke(app, ["analyze", str(config)])
    assert result.exit_code == 0
    assert "YAML Valid" in result.stdout

def test_cloud_lint_validate_invalid(tmp_path):
    config = tmp_path / "invalid.yaml"
    config.write_text("packages:\n  -")
    
    result = runner.invoke(app, ["validate", str(config)])
    # In strict testing or general testing, if schema validation fails, we should get exit code 1
    assert result.exit_code == 1

def test_cloud_lint_json(tmp_path):
    config = tmp_path / "valid.yaml"
    config.write_text("#cloud-config\npackages:\n  - nginx")
    
    result = runner.invoke(app, ["json-out", str(config)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["valid"] is True
    assert "nginx" in data["packages"]

def test_cloud_lint_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout
    assert "report" in result.stdout
