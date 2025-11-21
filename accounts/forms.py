from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class SignUpForm(UserCreationForm):
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='성별'
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "gender",)

class LoginForm(AuthenticationForm):
    pass
