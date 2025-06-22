from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from users.models import User


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите имя пользователя",
        "required": False
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите пароль",
        "required": False
    }))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите имя",
        "required": False
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите фамилию",
        "required": False
    }))

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите имя пользователя",
        "required": False
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите адрес эл. почты",
        "required": False
    }))

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите номер телефона",
        'value': '+7',
        "required": False
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-group',
        'placeholder': "Введите пароль",
        "required": False
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-group',
        'placeholder': "Подтвердите пароль",
        "required": False
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        "required": False
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        "required": False
    }))

    username = forms.CharField(widget=forms.TextInput(attrs={
        'readonly': True,
        'class': 'form-group',
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'readonly': True,
        'class': 'form-group',
    }))

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-group',
        'value': '+7',
        "required": False
    }))

    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'save-btn', 'id': 'photoUpload', 'hidden': True,
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'image')