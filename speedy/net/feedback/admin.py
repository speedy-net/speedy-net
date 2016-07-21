from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['sender', 'sender_name', 'sender_email', 'type', 'text', 'report_entity', 'report_file']

    def has_add_permission(self, request):
        return False


admin.site.register(Feedback, FeedbackAdmin)
