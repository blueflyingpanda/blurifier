import logging

from ninja import Router
from .models import TextSubmission
from .tasks import process_text

logger = logging.getLogger(__name__)
router = Router()

from ninja import Schema

class SubmitTextSchema(Schema):
    text: str

@router.post("/submit/")
def submit_text(request, payload: SubmitTextSchema):
    # TODO: use single quotes for strings
    # TODO: figure out where are logs
    obj = TextSubmission.objects.create(original_text=payload.text)

    result = process_text.delay(obj.id)
    logger.info('Task queued successfully: %s', result.id)
    logger.debug('Task state: %s', result.state)
    logger.debug('Task ready: %s', result.ready())

    return {'id': obj.id}



@router.get("/result/{submission_id}/")
def get_result(request, submission_id: int):
    # TODO: validate submission_id and add status model for tasks
    obj = TextSubmission.objects.get(id=submission_id)
    return {
        "original": obj.original_text,
        "processed": obj.processed_text,
        "processed_dt": obj.updated_at,
    }
