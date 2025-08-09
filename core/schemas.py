from datetime import datetime

from ninja import Schema


class ErrorResponseSchema(Schema):
    detail: str


class SubmitTextSchema(Schema):
    text: str


class SubmitResponseSchema(Schema):
    text_id: str


class ResultResponseSchema(Schema):
    status: str
    original: str
    processed: str | None = None
    processed_dt: datetime
    detail: str = ''


class SearchResponseSchema(Schema):
    text_hash: str
    original_text: str
    processed_text: str | None = None
