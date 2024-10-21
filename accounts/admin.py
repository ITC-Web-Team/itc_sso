# from django.contrib import admin

# # Register your models here.
# from .models import *
# admin.site.register(Profile)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'email_verified')
    readonly_fields = ('email_verified', 'verification_token')

def has_change_permission(self, request, obj=None):
    if obj and 'email_verified' in request.POST:
        messages.warning(request, 'You are not allowed to modify email verification status.')
        return False
    return super().has_change_permission(request, obj)


admin.site.unregister(User)


admin.site.register(User, UserAdmin)


admin.site.register(Profile, ProfileAdmin)

admin.site.register(LoginSession)
# admin.site.unregister(Projects)


class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'redirect_url')  

admin.site.register(Projects, ProjectsAdmin)