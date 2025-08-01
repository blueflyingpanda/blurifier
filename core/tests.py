import pytest
from core.models import TextSubmission


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_submit_text(async_client):
    url = '/api/submit/'
    response = await async_client.post(
        url, {'text': 'this is a damn test'}, content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert 'text_id' in data

    submission = await TextSubmission.objects.aget(text_hash=data['text_id'])
    assert submission.original_text == 'this is a damn test'


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_result(async_client):
    submission = await TextSubmission.objects.acreate(
        original_text='fuck shit',
        processed_text='f*** s***',
    )

    url = f'/api/result/{submission.text_hash}/'
    response = await async_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['original'] == 'fuck shit'
    assert data['processed'] == 'f*** s***'
