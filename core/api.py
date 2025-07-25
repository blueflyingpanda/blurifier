from ninja import Router
from .models import TextSubmission
from .tasks import process_text

router = Router()

from ninja import Schema

class SubmitTextSchema(Schema):
    text: str

@router.post("/submit/")
def submit_text(request, payload: SubmitTextSchema):
    obj = TextSubmission.objects.create(original_text=payload.text)
    process_text.delay(obj.id)
    return {"id": obj.id}


@router.get("/result/{submission_id}/")
def get_result(request, submission_id: int):
    obj = TextSubmission.objects.get(id=submission_id)
    return {
        "original": obj.original_text,
        "processed": obj.processed_text,
        "processed_dt": obj.updated_at,
    }
