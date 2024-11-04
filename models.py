from pydantic import BaseModel
from typing import List, Optional

class Node(BaseModel):
    id: int
    label: str
    name: Optional[str] = None
    screen_name: Optional[str] = None
    sex: Optional[int] = None
    city: Optional[str] = None

class Relationship(BaseModel):
    type: str
    end_node_id: int

class NodeWithRelationships(BaseModel):
    node: Node
    relationships: List[Relationship]
