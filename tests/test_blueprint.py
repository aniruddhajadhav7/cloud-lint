from cloud_lint.blueprint import BlueprintEngine

def test_blueprint_generates_valid_config(basic_yaml):
    engine = BlueprintEngine()
    report = engine.analyze_string(basic_yaml)
    
    assert report.valid is True
    assert report.total_packages == 2
    assert report.total_commands == 1
    assert "nginx" in [p.name for p in report.packages]
    assert report.execution_steps[1].module == "packages"
    assert report.execution_steps[2].module == "runcmd"

def test_users_expanded_with_details(users_yaml):
    engine = BlueprintEngine()
    report = engine.analyze_string(users_yaml)
    
    assert report.total_users == 1
    assert report.users[0].name == "ubuntu"
    assert len(report.users[0].ssh_authorized_keys) == 1

def test_write_files_shows_path_and_permissions():
    engine = BlueprintEngine()
    content = """
#cloud-config
write_files:
  - path: /test.txt
    permissions: "0600"
"""
    report = engine.analyze_string(content)
    assert report.total_files == 1
    assert report.write_files[0].path == "/test.txt"
    assert report.write_files[0].permissions == "0600"
