from cloud_lint.stage_mapper import StageMapper
from cloud_lint.models import CloudInitStage

def test_packages_maps_to_config():
    mapper = StageMapper()
    steps = mapper.map({"packages": ["nginx"]})
    
    pkg_step = next(s for s in steps if s.module == "packages")
    assert pkg_step.stage == CloudInitStage.CONFIG

def test_runcmd_maps_to_final():
    mapper = StageMapper()
    steps = mapper.map({"runcmd": ["ls"]})
    
    cmd_step = next(s for s in steps if s.module == "runcmd")
    assert cmd_step.stage == CloudInitStage.FINAL

def test_bootcmd_maps_to_local():
    mapper = StageMapper()
    steps = mapper.map({"bootcmd": ["echo hello"]})
    
    boot_step = next(s for s in steps if s.module == "bootcmd")
    assert boot_step.stage == CloudInitStage.LOCAL

def test_power_state_highest_order():
    mapper = StageMapper()
    steps = mapper.map({
        "runcmd": ["echo ok"],
        "power_state": {"mode": "reboot"}
    })
    
    # Sort order checking
    assert steps[-1].module == "power_state"

def test_stage_order():
    mapper = StageMapper()
    steps = mapper.map({
        "packages": ["nginx"],
        "runcmd": ["ls"],
        "bootcmd": ["echo hello"],
        "network": {"version": 2}
    })
    
    groups = mapper.get_stage_groups(steps)
    # Filter out empty stages except generator
    stages_present = [g.stage for g in groups if g.steps or g.stage == CloudInitStage.GENERATOR]
    
    expected_order = [
        CloudInitStage.GENERATOR,
        CloudInitStage.LOCAL,
        CloudInitStage.NETWORK,
        CloudInitStage.CONFIG,
        CloudInitStage.FINAL
    ]
    
    assert [s for s in expected_order if s in stages_present] == stages_present
