import logging
from enum import StrEnum
from hashlib import sha256

from celery.result import AsyncResult
from django.core.cache import cache
from django.shortcuts import aget_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination

from core.elk import es_service
from core.models import TextSubmission
from core.schemas import (
    SearchResponseSchema,
    SubmitResponseSchema,
    SubmitTextSchema,
    ResultResponseSchema,
    ErrorResponseSchema,
)
from core.tasks import process_text

logger = logging.getLogger(__name__)
router = Router()

CACHE_TTL = 3600  # 1 hour in seconds


class TaskStatus(StrEnum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


@router.post('/submit/', response=SubmitResponseSchema)
async def submit_text(request, payload: SubmitTextSchema):
    text_hash = sha256(payload.text.encode()).hexdigest()

    obj, created = await TextSubmission.objects.aget_or_create(
        text_hash=text_hash, defaults={'original_text': payload.text}
    )

    if created and not obj.processed_text:
        process_text.apply_async(args=[text_hash], task_id=text_hash)

    return SubmitResponseSchema(text_id=text_hash)


@router.get(
    '/result/{text_hash}/',
    response={200: ResultResponseSchema, 404: ErrorResponseSchema},
)
async def get_result(request, text_hash: str):
    cache_key = f'result:{text_hash}'
    if cached_result := cache.get(cache_key):
        logger.info('Cache hit for text hash: %s', text_hash)
        return ResultResponseSchema(**cached_result)

    obj = await aget_object_or_404(TextSubmission, text_hash=text_hash)

    task_result = AsyncResult(text_hash)
    status = task_result.status

    if obj.processed_text:
        status = TaskStatus.SUCCESS

    result_data = {
        'status': status,
        'original': obj.original_text,
        'processed': obj.processed_text,
        'processed_dt': obj.updated_at,
        'detail': task_result.info if status == TaskStatus.FAILURE else '',
    }

    if status == TaskStatus.SUCCESS:
        cache.set(cache_key, result_data, timeout=CACHE_TTL)

    return ResultResponseSchema(**result_data)


@router.get(
    '/search/',
    response={
        200: list[SearchResponseSchema],
        400: ErrorResponseSchema,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@paginate(LimitOffsetPagination)
async def search_texts(request, query: str):
    created = await es_service.create_index()
    if not created:
        raise HttpError(500, 'Failed to create Elasticsearch index')

    if not query.strip():
        raise HttpError(400, 'Query parameter cannot be empty')

    # probably better to paginate this at the Elasticsearch level but for learning purposes we will paginate here
    results = await es_service.search_text(query)

    return results
