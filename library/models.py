from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel


class AmazonError(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


# ── Feeds ──────────────────────────────────────────────────

class CreateFeedDocumentResponse(BaseModel):
    feedDocumentId: str
    url: str


class CreateFeedResponse(BaseModel):
    feedId: str


class FeedStatusResponse(BaseModel):
    feedId: str
    feedType: str
    marketplaceIds: list[str]
    createdTime: str
    processingStatus: Literal["IN_QUEUE", "IN_PROGRESS", "DONE", "CANCELLED", "FATAL"]
    processingStartTime: Optional[str] = None
    processingEndTime:   Optional[str] = None
    resultFeedDocumentId: Optional[str] = None


class FeedDocumentResponse(BaseModel):
    feedDocumentId: str
    url: str
    compressionAlgorithm: Optional[str] = None


# ── Reports ────────────────────────────────────────────────

class ReportStatusResponse(BaseModel):
    reportId: str
    reportType: str
    marketplaceIds: list[str]
    createdTime: str
    processingStatus: Literal["IN_QUEUE", "IN_PROGRESS", "DONE", "CANCELLED", "FATAL"]
    processingStartTime: Optional[str] = None
    processingEndTime:   Optional[str] = None
    reportDocumentId:    Optional[str] = None


class ReportDocumentResponse(BaseModel):
    reportDocumentId: str
    url: str
    compressionAlgorithm: Optional[str] = None


class CreateReportResponse(BaseModel):
    reportId: str


class ReportRun(BaseModel):
    """Resultado de la cadena create -> poll -> download de AmazonClient.run_report.

    content es None cuando el reporte terminó sin documento (período sin datos).
    """
    reportId: str
    reportDocumentId: Optional[str] = None
    content: Optional[str] = None


# ── Tokens ─────────────────────────────────────────────────

class RestrictedDataTokenResponse(BaseModel):
    restrictedDataToken: str
