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

class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    readonly_fields = ('user', 'project', 'created_at')

class SSOSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'active')
    readonly_fields = ('user', 'session_key', 'active')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'redirect_url', 'description')  


admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SSOSession, SSOSessionAdmin)
admin.site.register(LoginSession, LoginSessionAdmin)