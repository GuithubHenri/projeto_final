from django.contrib import admin
from .models import Perfil, Cliente, Pedido, EventoRastreio

admin.site.register(Perfil)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(EventoRastreio)
