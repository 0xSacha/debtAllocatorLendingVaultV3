import base64
import json

import urllib3
from starkware.cairo.lang.vm.cairo_pie import CairoPie

from sharp.lambda_function import add_job, get_status


class ClientLib:
    """
    Communicates with the SHARP.
    This is a slim wrapper around the SHARP API.
    """

    def __init__(self, service_url: str):
        """
        service_url is the SHARP url.
        """
        self.service_url = service_url

    def add_job(self, cairo_pie: CairoPie) -> str:
        """
        Sends a job to the SHARP.
        cairo_pie is the product of running the corresponding Cairo program locally
        (using cairo-run --cairo_pie_output).
        Returns job_key - a unique id of the job in the SHARP system.
        """

        return add_job({"cairo_pie": base64.b64encode(cairo_pie.serialize()).decode("ascii")})

    def get_status(self, job_key: str) -> str:
        """
        Fetches the job status from the SHARP.
        job_key: used to query the state of the job in the system - returned by 'add_job'.
        """

        res = get_status({"cairo_job_key": job_key})
        assert (
            "status" in res
        ), f"Error when checking status of job with key '{job_key}': {res}."
        return res["status"]

    def _send(self, action: str, payload: dict) -> dict:
        """
        Auxiliary function used to communicate with the SHARP.
        action: the action to be sent to the SHARP.
        payload: action specific parameters.
        """

        data = {
            "action": action,
            "request": payload,
        }

        CA_CERTS = ("client-2048.crt", "client-2048.key")

        http = urllib3.PoolManager(cert_reqs="REQUIRED", ca_certs=CA_CERTS)

        res = http.request(
            method="POST", url=self.service_url, body=json.dumps(data).encode("utf-8")
        )
        return json.loads(res.data.decode("utf-8"))
