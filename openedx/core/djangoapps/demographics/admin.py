"""
Django admin page for demographics
"""

from django.contrib import admin

from openedx.core.djangoapps.demographics.models import UserDemographics


class UserDemographicsAdmin(admin.ModelAdmin):
    """
    Admin for UserDemographics Model
    """
    list_display = ('user', 'call_to_action_dismissed')
    readonly_fields = ('user',)

    class Meta(object):
        model = UserDemographics


admin.site.register(UserDemographics, UserDemographicsAdmin)
