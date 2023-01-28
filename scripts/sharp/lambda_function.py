import base64
import logging
import os
import re
import typing
import uuid

from .lambda_utils import send_cairo_job, send_get_status

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_CAIRO_PIE_SIZE = 20 * 2**20  # 20Mb.
# Lambda function version.
VERSION = 1


def add_job(request: dict) -> dict:
    # Cairo-pie is received as a base64 encoded string.
    cairo_job_key = str(uuid.uuid4())
    print("Cairo job key", cairo_job_key)
    cairo_pie_str = request["cairo_pie"]
    cairo_pie = base64.b64decode(cairo_pie_str.encode("ascii"))

    # Validate cairo-pie size.
    assert (
        len(cairo_pie) <= MAX_CAIRO_PIE_SIZE
    ), "Cairo PIE exceeds maximum allowed size."

    # Send Cairo job to sharp gateway.
    send_cairo_job(
        customer_id=os.environ["CUSTOMER_ID"],
        cairo_job_key=cairo_job_key,
        cairo_pie=cairo_pie,
    )

    return {"cairo_job_key": cairo_job_key}


def get_status(request: dict) -> dict:
    """
    Get_status action: Gets the cairo-job status from GPS and blockchain.
    """
    cairo_job_key, fact = parse_get_status_parameters(request)
    return send_get_status(
        customer_id=os.environ["CUSTOMER_ID"], cairo_job_key=cairo_job_key, fact=fact
    )


def parse_get_status_parameters(request: dict) -> typing.Tuple[str, str]:
    # Get cairo_job_key and check its validity.
    cairo_job_key = request.get("cairo_job_key", None)
    assert cairo_job_key is not None, "Missing cairo_job_key value."
    # Cairo_job_key value must be uuid4 string.
    assert isinstance(cairo_job_key, str), "Wrong type for variable cairo_job_key."
    UUID4_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(
        UUID4_REGEX, cairo_job_key
    ), f"Unexpected cairo_job_key value {cairo_job_key}."

    # Get fact and check its validity.
    fact = request.get("fact", None)
    if fact is not None:
        # Fact value must be hex-string with 1-64 digits.
        assert isinstance(fact, str), "Wrong type for variable fact."
        HEX_STR_REGEX = "^0x[a-fA-F0-9]{1,64}$"
        assert re.match(HEX_STR_REGEX, fact), f"Unexpected fact value {fact}."

    return cairo_job_key, fact
