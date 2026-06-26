from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from enum import Enum
import datetime


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CloudInitStage(str, Enum):
    GENERATOR = "Generator"
    LOCAL = "Local"
    NETWORK = "Network"
    CONFIG = "Config"
    FINAL = "Final"


class ValidationError(BaseModel):
    field: Optional[str] = None
    message: str
    line: Optional[int] = None


class ValidationWarning(BaseModel):
    field: Optional[str] = None
    message: str
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    yaml_valid: bool = False
    schema_valid: bool = False
    cloud_init_compatible: bool = False
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []


class RiskItem(BaseModel):
    command: str
    level: RiskLevel
    description: str
    context: Optional[str] = None  # which module it was found in
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class ExecutionStep(BaseModel):
    stage: CloudInitStage
    module: str
    action: str
    details: List[str] = []
    order: int
    icon: str = "→"


class PackageInfo(BaseModel):
    name: str
    version: Optional[str] = None
    source: str = "apt"  # apt, snap, etc.


class UserInfo(BaseModel):
    name: str
    sudo: Optional[str] = None
    shell: Optional[str] = None
    ssh_authorized_keys: List[str] = []
    groups: List[str] = []
    lock_passwd: Optional[bool] = None
    home: Optional[str] = None


class WriteFileInfo(BaseModel):
    path: str
    permissions: str = "0644"
    owner: str = "root:root"
    content_preview: Optional[str] = None  # first 100 chars
    encoding: str = "text/plain"
    append: bool = False


class MountInfo(BaseModel):
    device: str
    mount_point: str
    filesystem: Optional[str] = None
    options: Optional[str] = None


class DependencyEdge(BaseModel):
    source: str
    target: str
    reason: str


class StageGroup(BaseModel):
    stage: CloudInitStage
    steps: List[ExecutionStep] = []


class BlueprintReport(BaseModel):
    # Identity
    filename: str = ""
    analyzed_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

    # Validation
    valid: bool = False
    validation: ValidationResult = Field(default_factory=ValidationResult)

    # Risk
    risk_items: List[RiskItem] = []
    risk_score: int = 0          # 0-100
    risk_level: RiskLevel = RiskLevel.LOW

    # Execution
    execution_steps: List[ExecutionStep] = []
    stage_groups: List[StageGroup] = []

    # Modules found
    modules_detected: List[str] = []
    packages: List[PackageInfo] = []
    users: List[UserInfo] = []
    write_files: List[WriteFileInfo] = []
    commands: List[str] = []
    bootcmds: List[str] = []
    mounts: List[MountInfo] = []

    # Dependencies
    dependencies: List[DependencyEdge] = []

    # Stats
    total_packages: int = 0
    total_users: int = 0
    total_files: int = 0
    total_commands: int = 0
    total_risks: int = 0
    warnings_count: int = 0
    errors_count: int = 0


class JSONOutput(BaseModel):
    """Compact JSON output for CI/CD"""
    valid: bool
    warnings: int
    errors: int
    risk_score: int
    risk_level: str
    packages: List[str] = []
    users: List[str] = []
    files: List[str] = []
    commands: List[str] = []
    risks: List[Dict[str, str]] = []
    modules: List[str] = []
    execution_order: List[str] = []
