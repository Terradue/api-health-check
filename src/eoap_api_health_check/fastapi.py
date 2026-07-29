#   Copyright 2026 EOAP
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an 'AS IS' BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from . import HealthyResponse, UnhealthyResponse, WarnResponse

CACHE_CONTROL_HEADER = "Cache-Control"

HEALTH_JSON_MEDIA_TYPE = "application/health+json"


class HealthJSONResponse(JSONResponse):
    media_type = HEALTH_JSON_MEDIA_TYPE

    def __init__(
        self,
        content: HealthyResponse | UnhealthyResponse | WarnResponse,
        *,
        status_code: int = HTTPStatus.OK.value,
        cache_control: str | None = "max-age=60",
    ) -> None:
        super().__init__(
            content=content.model_dump(
                by_alias=True,
                mode="json",
                exclude_none=True,
            ),
            status_code=status_code,
            headers={CACHE_CONTROL_HEADER: cache_control} if cache_control else {},
        )
