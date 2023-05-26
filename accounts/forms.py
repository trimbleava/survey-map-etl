# accounts/forms.py
# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from accounts.models import TenantUser

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         # we’ve imported CustomUser model via get_user_model which looks to our
# # AUTH_USER_MODEL config in settings.py
#         model = get_user_model()
#         fields = (
#             "email",
#             "username",
#         )


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = get_user_model()
#         # The password field is implicitly included by default
#         # and so does not need to be explicitly named here
#         fields = (
#             "email",
#             "username",
#         )
