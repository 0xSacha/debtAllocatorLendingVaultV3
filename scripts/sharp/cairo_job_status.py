import json
from enum import Enum, auto
from typing import Dict, Type


class CairoJobStatus(Enum):
    # Cairo-job is not known by SHARP.
    UNKNOWN = auto()
    # Cairo job was received in the gateway, but it hasn't been created yet.
    NOT_CREATED = auto()
    # Cairo job is being processed.
    IN_PROGRESS = auto()
    # Cairo job handling has been completed.
    PROCESSED = auto()
    # Cairo job fact is written onchain.
    ONCHAIN = auto()
    # Cairo job validation failed.
    INVALID = auto()
    # Cairo job processing failed.
    FAILED = auto()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, CairoJobStatus):
            return NotImplemented

        self_not_comparable, other_not_comparable = (
            status in (CairoJobStatus.INVALID, CairoJobStatus.FAILED)
            for status in (self, other)
        )
        if self_not_comparable or other_not_comparable:
            raise NotImplementedError(
                f"Comparison is not supported between status {self.name} and {other.name}."
            )

        return get_status_order(status=self) >= get_status_order(status=other)

    def __lt__(self, other: object) -> bool:
        return not self >= other

    @property
    def causes_aborted_batch(self) -> int:
        return self in [
            CairoJobStatus.UNKNOWN,
            CairoJobStatus.INVALID,
            CairoJobStatus.FAILED,
        ]


# Dictionary that represents the CairoJobStatus valid flows.
# [UNKNOWN] -> [NOT_CREATED] -> [IN_PROGRESS] -> [PROCESSED, INVALID, FAILED]
# Refer GPS simulator assert_consistent_cairo_job_status function to see usage details.
cairo_job_status_layers_dict: Dict[CairoJobStatus, int] = {
    CairoJobStatus.UNKNOWN: 0,
    CairoJobStatus.NOT_CREATED: 1,
    CairoJobStatus.IN_PROGRESS: 2,
    CairoJobStatus.PROCESSED: 3,
    CairoJobStatus.INVALID: 3,
    CairoJobStatus.FAILED: 3,
}


def get_status_order(status: CairoJobStatus) -> int:
    return cairo_job_status_layers_dict[status]


class TrainStatus(Enum):
    NOT_CREATED = auto()
    CREATED = auto()
    SCHEDULED = auto()
    PROVED = auto()
    DISPATCHED = auto()
    WRITTEN_TO_BLOCKCHAIN = auto()
