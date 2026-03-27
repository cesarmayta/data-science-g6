from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_inmuebles, name='lista_inmuebles'),
    path('inmueble/<int:id>/', views.detalle_inmueble, name='detalle_inmueble'),
    path('registro/',views.registro_agente,name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
