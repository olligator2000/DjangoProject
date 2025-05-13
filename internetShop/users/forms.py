from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from users.models import User
from django import forms


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-group',
                                                             'placeholder': "Введите имя пользователя", "required": False}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-group',
                                                             'placeholder': "Введите пароль", "required": False}))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-group',
                                                             'placeholder': "Введите имя", "required": False}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-group',
                                                               'placeholder': "Введите фамилию", "required": False}))

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-group', 'placeholder': "Введите имя пользователя",
                                                            "required": False}))

    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-group', 'placeholder': "Введите адрес эл. почты",
                                                            "required": False}))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-group',
                                                           'placeholder': "Введите пароль", "required": False}))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-group',
                                                           'placeholder': "Подтвердите пароль", "required": False}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
