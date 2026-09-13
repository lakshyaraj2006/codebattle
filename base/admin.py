from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from base.models import Submission, User, Event

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if obj:
            fieldsets = list(fieldsets)
            fieldsets[1] = (
                "Personal info",
                {
                    "fields": (
                        *fieldsets[1][1]["fields"],
                        "name",
                        "bio",
                        "hackathon_participant",
                        "avatar"
                    )
                },
            )

        return fieldsets

admin.site.register(Event)
admin.site.register(Submission)