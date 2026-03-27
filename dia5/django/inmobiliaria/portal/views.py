from django.shortcuts import render
from .models import Inmueble

# Create your views here.
def lista_inmuebles(request):
    inmuebles = Inmueble.objects.all() # select * from portal_inmueble
    #print(inmuebles)
    context = {
        'inmuebles':inmuebles
    }
    return render(request,'portal/index.html',context)
