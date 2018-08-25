from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['date_created', '__str__']
    readonly_fields = ['sender', 'sender_name', 'sender_email', 'type', 'text', 'report_entity', 'report_file']

    def has_add_permission(self, request):
        return False


admin.site.register(Feedback, FeedbackAdmin)


