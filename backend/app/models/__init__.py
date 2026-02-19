"""
Pydantic models pour validation et sérialisation API
"""
from .job_offer import JobOfferResponse, JobOfferDetail, JobOfferListResponse
from .filters import FilterRequest, FilterOptions

__all__ = [
    "JobOfferResponse",
    "JobOfferDetail",
    "JobOfferListResponse",
    "FilterRequest",
    "FilterOptions",
]
