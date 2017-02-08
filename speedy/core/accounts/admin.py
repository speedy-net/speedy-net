from django.contrib import admin
from .models import User, Entity, UserEmailAddress

admin.site.register(User)
admin.site.register(Entity)
admin.site.register(UserEmailAddress)
