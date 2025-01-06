from typing import List, Optional

from pydantic import BaseModel


class CMRQueryParam(BaseModel):
    temporal: Optional[List[str]] = None
    spatial: Optional[List[float]] = None
    keyword: Optional[str] = None

    def to_query_params(self) -> dict:
        params = {}
        if self.temporal:
            params["temporal[]"] = [t for t in self.temporal]
        if self.spatial:
            params["bounding_box[]"] = ",".join(map(str, self.spatial))
        if self.keyword:
            params["keyword"] = self.keyword
        return params
