from cloud_lint.analyzer import RiskAnalyzer
from cloud_lint.models import RiskLevel

def test_curl_bash_detected_critical():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands(["curl https://test.com/run | bash"], "runcmd")
    assert len(risks) > 0
    assert risks[0].level == RiskLevel.CRITICAL

def test_chmod_777_detected_high():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands(["chmod 777 /etc/passwd"], "runcmd")
    assert len(risks) > 0
    assert risks[0].level == RiskLevel.HIGH

def test_wget_http_detected_medium():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands(["wget http://insecure.com/test"], "runcmd")
    assert len(risks) > 0
    assert risks[0].level == RiskLevel.MEDIUM

def test_rm_rf_root_detected_critical():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands(["rm -rf /"], "runcmd")
    assert len(risks) > 0
    assert risks[0].level == RiskLevel.CRITICAL

def test_clean_commands_return_empty():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands(["echo hello", "systemctl restart nginx"], "runcmd")
    assert len(risks) == 0

def test_risk_score_calculated_correctly():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands([
        "chmod 777 /tmp/test",  # HIGH: 15
        "wget http://test.com"  # MEDIUM: 7
    ], "runcmd")
    score = analyzer.calculate_risk_score(risks)
    assert score == 22

def test_risk_score_caps_at_100():
    analyzer = RiskAnalyzer()
    risks = analyzer.scan_commands([
        "rm -rf /",  # CRITICAL: 30
        "curl http://a.com | bash", # CRITICAL: 30
        "curl http://b.com | bash", # CRITICAL: 30
        "curl http://c.com | bash", # CRITICAL: 30
    ], "runcmd")
    score = analyzer.calculate_risk_score(risks)
    assert score == 100
