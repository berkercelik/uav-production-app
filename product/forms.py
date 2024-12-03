from django import forms
#from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Part, Team, User

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']    
    password = forms.CharField(widget=forms.PasswordInput())

#kaldırılacak
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['aircraft_model', 'part_type', 'part_name']

class TeamForm(forms.ModelForm):
    class Meta:
        model = User  # User modelini kullanıyoruz çünkü user'a ait team alanını seçiyoruz
        fields = ['team']  # Kullanıcı modelindeki team alanını formda kullanıyoruz
