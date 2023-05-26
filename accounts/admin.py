# accounts/admin.py
from django.contrib import admin


# from django.contrib.auth import get_user_model
# from .forms import CustomUserCreationForm, CustomUserChangeForm

# app modules
from accounts.models import TenantUser


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    pass

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = [
#         "email",
#         "username",
#         "is_superuser",
#         "is_staff",
#     ]
# admin.site.register(CustomUser, CustomUserAdmin)
