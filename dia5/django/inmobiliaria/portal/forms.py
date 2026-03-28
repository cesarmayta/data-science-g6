from django import forms
from django.contrib.auth.models import User
from .models import Agente,Inmueble

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
    
class InmuebleForm(forms.ModelForm):
    
    class Meta:
        model = Inmueble
        fields = ['titulo','descripcion','precio','habitaciones','tipo','ciudad']