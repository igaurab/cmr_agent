from typing import List, Optional

from pydantic import BaseModel, Field


class ServiceFeatureFlags(BaseModel):
    has_formats: Optional[bool] = False
    has_variables: Optional[bool] = False
    has_transforms: Optional[bool] = False
    has_combine: Optional[bool] = False
    has_spatial_subsetting: Optional[bool] = False
    has_temporal_subsetting: Optional[bool] = False


class ServiceFeatures(BaseModel):
    opendap: Optional[ServiceFeatureFlags] = None
    esi: Optional[ServiceFeatureFlags] = None
    harmony: Optional[ServiceFeatureFlags] = None


class Links(BaseModel):
    rel: str
    hreflang: Optional[str] = None
    href: str
    type: Optional[str] = None


class CollectionEntry(BaseModel):
    processing_level_id: Optional[str] = None
    cloud_hosted: Optional[bool] = False
    boxes: Optional[List[str]] = Field(default_factory=list)
    has_combine: Optional[bool] = False
    time_start: Optional[str] = None
    version_id: Optional[str] = None
    updated: Optional[str] = None
    dataset_id: Optional[str] = None
    entry_id: str
    has_spatial_subsetting: Optional[bool] = False
    has_transforms: Optional[bool] = False
    has_variables: Optional[bool] = False
    data_center: Optional[str] = None
    short_name: Optional[str] = None
    organizations: Optional[List[str]] = Field(default_factory=list)
    title: str
    coordinate_system: Optional[str] = None
    summary: Optional[str] = None
    time_end: Optional[str] = None
    service_features: Optional[ServiceFeatures] = None
    orbit_parameters: Optional[dict] = Field(default_factory=dict)
    id: str
    has_formats: Optional[bool] = False
    score: Optional[float] = None
    consortiums: Optional[List[str]] = Field(default_factory=list)
    original_format: Optional[str] = None
    archive_center: Optional[str] = None
    has_temporal_subsetting: Optional[bool] = False
    browse_flag: Optional[bool] = False
    platforms: Optional[List[str]] = Field(default_factory=list)
    online_access_flag: Optional[bool] = False
    links: Optional[List[Links]] = Field(default_factory=list)


class CollectionResponse(BaseModel):
    updated: str
    id: str
    title: str
    entry: List[CollectionEntry]
