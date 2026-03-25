from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TipoInmueble(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Agente(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.RESTRICT)
    telefono = models.CharField(max_length=20)
    
    def __str__(self):
        return self.usuario.username
    
class Inmueble(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(default='')
    precio = models.DecimalField(max_digits=10,decimal_places=2)
    habitaciones = models.IntegerField(default=1)
    tipo = models.ForeignKey(TipoInmueble,on_delete=models.RESTRICT)
    ciudad = models.ForeignKey(Ciudad,on_delete=models.RESTRICT,default=1)
    agente = models.ForeignKey(Agente,on_delete=models.RESTRICT,default=1)
    
    
    def __str__(self):
        return self.titulo