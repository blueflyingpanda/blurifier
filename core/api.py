import logging
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from celery.result import AsyncResult
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from .models import TextSubmission
from .tasks import process_text

logger = logging.getLogger(__name__)
router = Router()

CACHE_TTL = 3600  # 1 hour in seconds


class TaskStatus(StrEnum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


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


class ErrorResponseSchema(Schema):
    detail: str


@router.post('/submit/', response=SubmitResponseSchema)
def submit_text(request, payload: SubmitTextSchema):
    text_hash = sha256(payload.text.encode()).hexdigest()

    obj, created = TextSubmission.objects.get_or_create(
        text_hash=text_hash, defaults={'original_text': payload.text}
    )

    # only create task if this is a new submission and not already processed
    if created and not obj.processed_text:
        process_text.apply_async(args=[text_hash], task_id=text_hash)

    return SubmitResponseSchema(text_id=text_hash)


@router.get(
    '/result/{text_hash}/',
    response={200: ResultResponseSchema, 404: ErrorResponseSchema},
)
def get_result(request, text_hash: str):
    cache_key = f'result:{text_hash}'
    if cached_result := cache.get(cache_key):
        logger.info('Cache hit for text hash: %s', text_hash)
        return ResultResponseSchema(**cached_result)

    obj = get_object_or_404(TextSubmission, text_hash=text_hash)

    task_result = AsyncResult(text_hash)
    status = task_result.status

    # could have been completed by periodic task or manual processing
    if obj.processed_text:
        status = TaskStatus.SUCCESS

    result_data = {
        'status': status,
        'original': obj.original_text,
        'processed': obj.processed_text,
        'processed_dt': obj.updated_at,
        'error': task_result.info if status == TaskStatus.FAILURE else '',
    }

    if status == TaskStatus.SUCCESS:
        cache.set(cache_key, result_data, timeout=CACHE_TTL)

    return ResultResponseSchema(**result_data)
