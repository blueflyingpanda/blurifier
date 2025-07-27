from hashlib import sha256

from django.db import models


class TextSubmission(models.Model):
    original_text = models.TextField()
    processed_text = models.TextField(blank=True, null=True)
    text_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.text_hash:
            self.text_hash = sha256(self.original_text.encode()).hexdigest()
        super().save(*args, **kwargs)
