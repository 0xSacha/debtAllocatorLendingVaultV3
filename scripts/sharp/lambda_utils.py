import asyncio
import logging
import os

from cairo_job_status import CairoJobStatus
from gateway_client import GatewayClient

logger = logging.getLogger(__name__)


def send_cairo_job(customer_id: str, cairo_job_key: str, cairo_pie: bytes):
    """
    Add_job action: Sends add_job request to GPS gateway.
    """

    # Call GPS gateway add_job.
    res = asyncio.run(
        gps_gateway().add_job(
            customer_id=customer_id, cairo_job_key=cairo_job_key, cairo_pie=cairo_pie
        )
    )
    logger.info(f"Add job {cairo_job_key} result: {res}")


def send_get_status(customer_id: str, cairo_job_key: str, fact: str) -> dict:
    # Call GPS gateway get_status.
    res = asyncio.run(
        gps_gateway().get_status(customer_id=customer_id, cairo_job_key=cairo_job_key)
    )

    # Check if fact is written onchain.
    if res["status"] == CairoJobStatus.PROCESSED.name and fact is not None:
        if check_fact_onchain(fact):
            logger.info(f"Fact {fact} is written onchain.")
            res["status"] = CairoJobStatus.ONCHAIN.name
        else:
            logger.info(f"Fact {fact} is not written onchain.")

    logger.info(f"Cairo job {cairo_job_key} status: {res}.")
    return res


def gps_gateway() -> GatewayClient:
    """
    Returns GatewayClient instance.
    """
    gateway_url = os.environ["GATEWAY_URL"]
    gateway_client = GatewayClient(url=gateway_url, certificates_path="../../certs")
    return gateway_client
