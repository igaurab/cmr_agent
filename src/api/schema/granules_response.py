from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Link(BaseModel):
    rel: str
    title: Optional[str] = None
    hreflang: str = Field(default="en-US")
    href: str
    inherited: Optional[bool] = None


class GranuleEntry(BaseModel):
    boxes: List[str]
    time_start: datetime
    updated: datetime
    dataset_id: str
    data_center: str
    title: str
    coordinate_system: str
    day_night_flag: str
    time_end: datetime
    id: str
    original_format: str
    granule_size: str
    browse_flag: bool
    collection_concept_id: str
    online_access_flag: bool
    links: List[Link]


class GranulesResponse(BaseModel):
    updated: datetime
    id: str
    title: str
    entry: List[GranuleEntry]
