from dataclasses import dataclass


@dataclass
class ProjectContext:
    project_id: str
    project_name: str
    home_id: int