#  Cloud-Lint

> **"Understand exactly what your cloud-init will do — before launching a single VM."**

Cloud-Lint is an offline CLI developer tool designed to validate, explain, and visualize your `cloud-init` configurations before they are deployed to a virtual machine. It completely eliminates the tedious deploy-wait-debug cycle by parsing your YAML and simulating the execution blueprint locally in milliseconds.

## ✨ Features

- **✅ Offline Validation:** Validates both YAML syntax and standard `cloud-init` JSON schemas instantly.
- **🛡️ Security Risk Analysis:** Detects dangerous patterns like `curl | bash`, world-writable permissions (`chmod 777`), destructive commands (`rm -rf /`), and hardcoded credentials.
- **🗺️ Execution Blueprinting:** Maps out exactly which modules run in which order across the five cloud-init stages (Generator, Local, Network, Config, Final).
- **📊 Interactive HTML Reports:** Generates self-contained, beautiful HTML reports containing a visual timeline, module breakdowns, and a Mermaid.js dependency graph.
- **🤖 CI/CD Ready:** Provides strict exit codes and structured JSON output for seamless integration into your deployment pipelines.

##  Installation

Cloud-Lint is built using Python 3.12+ and packaged with `hatchling`. You can easily install it locally or in a virtual environment.

Using `uv` (recommended):
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Or using standard `pip`:
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

##  Usage

Analyze a `cloud-init` file right in your terminal with rich visualization:
```bash
cloud-lint analyze user-data.yaml
```

Generate a standalone, interactive HTML report:
```bash
cloud-lint report user-data.yaml --output my-report.html
```

Output raw JSON for integration into CI/CD workflows:
```bash
cloud-lint json-out user-data.yaml
```

View only the execution blueprint (Stage & Action map):
```bash
cloud-lint blueprint user-data.yaml
```

View only the security risk analysis:
```bash
cloud-lint risks user-data.yaml
```

Generate a Mermaid.js DSL string of the dependency graph:
```bash
cloud-lint graph user-data.yaml
```

##  Architecture

Cloud-Lint is powered by:
- **Typer & Rich:** For a beautiful, intuitive CLI interface.
- **ruamel.yaml:** For high-fidelity YAML parsing that preserves structure and comments.
- **jsonschema:** For rigorous validation against cloud-init specs.
- **Pydantic V2:** For robust internal data modeling.
- **Jinja2:** For generating interactive HTML reports.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Make sure to run tests before submitting:
```bash
uv pip install -e ".[dev]"
pytest --cov=cloud_lint tests/
mypy cloud_lint
```

## 📄 License

This project is licensed under the Apache 2.0 License.
