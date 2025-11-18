"""
Database Schemas for Family Tree

Each Pydantic model maps to a MongoDB collection (collection name is the lowercase class name).

We store two main entities:
- Person: an individual in the family tree
- Photo: a family photo which can contain overlay tags pointing to persons

Tags are stored inside the Photo document as a list of items with coordinates and person reference.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class Person(BaseModel):
    full_name: str = Field(..., description="Person's full name")
    relation: Optional[str] = Field(None, description="Relation to you or the family (e.g., 'Father', 'Grandmother')")
    birth_year: Optional[int] = Field(None, ge=1800, le=2100)
    photo_url: Optional[str] = Field(None, description="Portrait or avatar URL")

class Tag(BaseModel):
    person_id: str = Field(..., description="Reference to a person document _id as string")
    x: float = Field(..., ge=0.0, le=1.0, description="X coordinate as a fraction of width (0..1)")
    y: float = Field(..., ge=0.0, le=1.0, description="Y coordinate as a fraction of height (0..1)")
    label: Optional[str] = Field(None, description="Optional label to show near the tag")

class Photo(BaseModel):
    title: str = Field(..., description="Photo title")
    url: str = Field(..., description="Photo URL")
    tags: List[Tag] = Field(default_factory=list, description="List of overlay tags for this photo")
