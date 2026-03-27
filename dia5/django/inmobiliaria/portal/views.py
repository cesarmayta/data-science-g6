from django.shortcuts import render, get_object_or_404
from .models import Inmueble

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
        pass
    else:
        form = RegistroAgenteForm()
        context = {
            'form':form
        }
    return render(request,'portal/registro.html',context)
