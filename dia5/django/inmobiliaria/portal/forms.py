from django import forms
from django.contrib.auth.models import User
from .models import Agente

class RegistroAgenteForm(forms.ModelForm):
    
    username = forms.CharField(label='Usuario')
    email = forms.EmailField(label='Correo Electronico')
    password = forms.CharField(widget=forms.PasswordInput,label='contraseña')
    
    class Meta:
        model = Agente
        fields = ['telefono']
        
class LoginForm(forms.Form):

    username = forms.CharField(label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")