import base64
import json
from typing import ClassVar, Dict, Optional

from services.external_api.client import ClientBase


class GatewayClient(ClientBase):
    prefix: ClassVar[str] = "/v1/gateway"

    async def add_job(
        self,
        customer_id: str,
        cairo_job_key: str,
        cairo_pie: bytes,
        max_waiting_time: Optional[int] = None,
    ):
        uri = f"/add_job?customer_id={customer_id}&cairo_job_key={cairo_job_key}"

        if max_waiting_time is not None:
            uri += f"&max_waiting_time={max_waiting_time}"

        cairo_pie_encoded = base64.b64encode(cairo_pie).decode("ascii")
        raw_response = await self._send_request(
            send_method="POST", uri=uri, data=cairo_pie_encoded
        )
        return json.loads(raw_response)

    async def get_status(self, customer_id: str, cairo_job_key: str) -> Dict[str, str]:
        uri = f"/get_status?customer_id={customer_id}&cairo_job_key={cairo_job_key}"
        raw_response = await self._send_request(send_method="GET", uri=uri)
        return json.loads(raw_response)

    async def get_gps_parameters(self):
        uri = f"/get_gps_parameters"
        raw_response = await self._send_request(send_method="GET", uri=uri)
        return json.loads(raw_response)
