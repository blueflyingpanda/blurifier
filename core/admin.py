from django.contrib import admin
from .models import TextSubmission

@admin.register(TextSubmission)
class TextSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_text', 'processed_text', 'created_at', 'updated_at', 'text_hash')
    readonly_fields = ('text_hash',)
