from django.shortcuts import render, get_object_or_404, redirect
from .models import Inmueble,Agente
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .forms import InmuebleForm
from .forms import RegistroAgenteForm

# Create your views here.
def lista_inmuebles(request):
    inmuebles = Inmueble.objects.all() # select * from portal_inmueble
    #print(inmuebles)
    context = {
        'inmuebles':inmuebles
    }
    return render(request,'portal/index.html',context)

def detalle_inmueble(request,id):
    
    inmueble = get_object_or_404(Inmueble,id=id) # select * from portal_inmueble where id = id
    context = {
        'inmueble':inmueble
    }
    return render(request,'portal/detalle.html',context)

def registro_agente(request):
    context = {}
    if request.method == "POST":
        form = RegistroAgenteForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            Agente.objects.create(
                usuario=user,
                telefono=form.cleaned_data['telefono']
            )
            return redirect('login')
    else:
        form = RegistroAgenteForm()
        context = {
            'form':form
        }
    return render(request,'portal/registro.html',context)

def login_view(request):

    from .forms import LoginForm

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user:
                login(request, user)
                return redirect('/')

    else:
        form = LoginForm()

    return render(request, 'portal/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def crear_inmueble(request):
    if request.method == "POST":
        form = InmuebleForm()
    else:
        form = InmuebleForm()
        
    context = {
        'form': form
    }
    
    return render(request,'portal/crear_inmueble.html',context)
    
