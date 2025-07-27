import logging

from better_profanity import profanity
from celery import shared_task

from .models import TextSubmission

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

    processed_ids = [obj.id for obj in objs]
    logger.info(
        'Finished processing texts, total processed: %s, IDs: %s', total, processed_ids
    )
