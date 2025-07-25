import logging

from better_profanity import profanity
from celery import shared_task
from django.core.cache import cache

from .models import TextSubmission

logger = logging.getLogger(__name__)
CACHE_TTL = 86400  # 1 day in seconds

def blur_text(text: str) -> str:
    return profanity.censor(text)

@shared_task
def process_text(submission_id):
    obj = TextSubmission.objects.get(id=submission_id)
    text_hash = obj.text_hash

    cached = cache.get(text_hash)
    if cached:
        obj.processed_text = cached
    else:
        result = blur_text(obj.original_text)
        obj.processed_text = result
        cache.set(text_hash, result, timeout=CACHE_TTL)

    obj.processed = True
    obj.save()
    return obj.id

@shared_task
def process_unprocessed_texts():
    objs = TextSubmission.objects.filter(processed_text__isnull=True)
    total = objs.count()
    logger.info(f'Starting to reprocess {total} texts')
    processed_count = 0
    for obj in objs:
        obj.processed_text = blur_text(obj.original_text)
        obj.processed = True
        obj.save()
        processed_count += 1
        logger.info(f'Processed TextSubmission id={obj.id}')
    logger.info(f'Finished reprocessing texts, total processed: {processed_count}')
