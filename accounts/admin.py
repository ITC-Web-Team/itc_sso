# from django.contrib import admin

# # Register your models here.
# from .models import *
# admin.site.register(Profile)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
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
        if obj is not None and 'email_verified' in request.POST:
            return False
        return super().has_change_permission(request, obj)

# Unregister the default User admin
admin.site.unregister(User)

# Register the new User admin with Profile inline
admin.site.register(User, UserAdmin)

# Register the Profile model with custom admin
admin.site.register(Profile, ProfileAdmin)

admin.site.register(LoginSession)
# admin.site.unregister(Projects)


class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'redirect_url')  # Add the 'id' to the list display

admin.site.register(Projects, ProjectsAdmin)