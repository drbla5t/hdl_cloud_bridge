from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectInfo:
    project_id: str
    name: str
    protocol_type: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceInfo:
    device_iot_id: str
    gateway_id: str
    sid: str
    name: str
    spk: str
    model: str
    online: bool
    attributes: List[Dict[str, Any]]
    status: List[Dict[str, Any]] | None
    mac: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)