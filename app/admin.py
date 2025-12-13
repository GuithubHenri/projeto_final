from django.contrib import admin
from .models import Perfil, Cliente, Pedido, EventoRastreio

# Configura para os eventos aparecerem DENTRO do Pedido
class EventoInline(admin.TabularInline):
    model = EventoRastreio
    extra = 0 # Não cria linhas vazias
    readonly_fields = ('criado_em',) # Data não editável
    can_delete = False # Evita apagar histórico acidentalmente

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'status', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('codigo', 'cliente__nome')
    inlines = [EventoInline] # <--- A mágica acontece aqui

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')

admin.site.register(Perfil)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)
# admin.site.register(EventoRastreio) # Opcional, já está dentro do Pedido