from hashlib import sha256

from django.db import models


class TextSubmission(models.Model):
    original_text = models.TextField()
    processed_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def text_hash(self) -> str:
        # TODO: separate column for text hash in order to avoid recalculating it and adding records to db
        return sha256(self.original_text.encode()).hexdigest()
