from django import forms
from django.contrib.auth.forms import AuthenticationForm
from repo_practice.models import Car


class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'price', 'in_stock']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter car make'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter car model'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter year'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter price'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'make': 'Car Make',
            'model': 'Car Model',
            'year': 'Year',
            'price': 'Price ($)',
            'in_stock': 'In Stock',
        }


class CustomLoginForm(AuthenticationForm):
    """
    Проста форма логіну
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть логін',
        })
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть пароль',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['password'].label = 'Пароль'


