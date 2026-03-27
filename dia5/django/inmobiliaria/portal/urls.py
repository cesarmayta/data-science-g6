from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_inmuebles, name='lista_inmuebles'),
    path('inmueble/<int:id>/', views.detalle_inmueble, name='detalle_inmueble'),
]
