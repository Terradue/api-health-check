# Copyright 2026 EOAP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest
from http import HTTPStatus

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from eoap_api_health_check import HealthyResponse, HealthyStatus, UnhealthyResponse
from eoap_api_health_check.fastapi import (
    HEALTH_JSON_MEDIA_TYPE,
    HealthJSONResponse,
)


class HealthJSONResponseTests(unittest.TestCase):
    def test_serializes_health_model_with_wire_format_defaults(self) -> None:
        response = HealthJSONResponse(
            HealthyResponse(service_id="catalogue-api"),
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.media_type, HEALTH_JSON_MEDIA_TYPE)
        self.assertEqual(response.headers["cache-control"], "max-age=60")
        self.assertEqual(
            json.loads(response.body),
            {"status": "up", "serviceId": "catalogue-api"},
        )

    def test_supports_custom_status_and_disabling_cache_control(self) -> None:
        response = HealthJSONResponse(
            UnhealthyResponse(output="Database unavailable"),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            cache_control=None,
        )

        self.assertEqual(response.status_code, HTTPStatus.SERVICE_UNAVAILABLE)
        self.assertNotIn("cache-control", response.headers)


class FastAPIIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_response_is_returned_by_fastapi(self) -> None:
        app = FastAPI()

        @app.get("/health", response_class=HealthJSONResponse)
        async def health() -> HealthJSONResponse:
            return HealthJSONResponse(
                HealthyResponse(
                    status=HealthyStatus.PASS,
                    service_id="catalogue-api",
                )
            )

        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/health")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.headers["content-type"],
            HEALTH_JSON_MEDIA_TYPE,
        )
        self.assertEqual(response.headers["cache-control"], "max-age=60")
        self.assertEqual(
            response.json(),
            {"status": "pass", "serviceId": "catalogue-api"},
        )
        self.assertIn(
            HEALTH_JSON_MEDIA_TYPE,
            app.openapi()["paths"]["/health"]["get"]["responses"]["200"]["content"],
        )


if __name__ == "__main__":
    unittest.main()
