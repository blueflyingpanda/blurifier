import pytest
from core.models import TextSubmission

@pytest.mark.django_db
def test_submit_text(client):
    url = "/api/submit/"
    response = client.post(url, {"text": "this is a damn test"}, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

    submission = TextSubmission.objects.get(id=data["id"])
    assert submission.original_text == "this is a damn test"
    assert submission.processed_text == "this is a **** test"

@pytest.mark.django_db
def test_get_result(client):
    submission = TextSubmission.objects.create(
        original_text="fuck shit",
        processed_text="f*** s***",
    )

    url = f"/api/result/{submission.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "fuck shit"
    assert data["processed"] == "f*** s***"
