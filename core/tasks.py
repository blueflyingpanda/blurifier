import logging
from datetime import datetime, UTC

from asgiref.sync import async_to_sync
from better_profanity import profanity
from celery import shared_task

from core.elk import es_service
from core.models import TextSubmission

logger = logging.getLogger(__name__)


def blur_text(text: str) -> str:
    return profanity.censor(text)


@shared_task
def process_text(text_hash: str) -> str:
    # Get the unique submission by hash
    try:
        submission = TextSubmission.objects.get(text_hash=text_hash)
    except TextSubmission.DoesNotExist:
        raise ValueError(f'No submission found for hash {text_hash}')

    if submission.processed_text:
        return submission.processed_text

    result = blur_text(submission.original_text)

    submission.processed_text = result
    submission.save()

    return result


@shared_task
def process_unprocessed_texts():
    objs = list(TextSubmission.objects.filter(processed_text__isnull=True))
    total = len(objs)

    logger.info('Starting to process %s texts', total)

    for obj in objs:
        obj.processed_text = blur_text(obj.original_text)

    TextSubmission.objects.bulk_update(objs, ['processed_text'])

    logger.info(
        'Finished processing texts, total processed: %s, IDs: %s',
        len(objs),
        [obj.id for obj in objs],
    )


def index_document_sync(text_hash, original_text, processed_text=None) -> bool:
    return async_to_sync(es_service.index_document)(
        text_hash, original_text, processed_text
    )


@shared_task
def index_texts():
    texts_to_index = list(
        TextSubmission.objects.filter(
            processed_text__isnull=False,
            indexed_at__isnull=True,
        )
    )

    updated_texts = []
    current_time = datetime.now(UTC)

    for text in texts_to_index:
        success = index_document_sync(
            text_hash=text.text_hash,
            original_text=text.original_text,
            processed_text=text.processed_text,
        )
        if success:
            text.indexed_at = current_time
            text.updated_at = current_time
            updated_texts.append(text)

    if updated_texts:
        TextSubmission.objects.bulk_update(updated_texts, ['indexed_at', 'updated_at'])

    logger.info(
        'Finished indexing texts, total indexed: %s, IDs: %s',
        len(updated_texts),
        [obj.id for obj in updated_texts],
    )
