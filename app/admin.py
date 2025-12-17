from django.contrib import admin
from .models import Perfil, Cliente, Pedido, EventoRastreio


# ==========================
# INLINE DE EVENTOS
# ==========================
class EventoInline(admin.TabularInline):
    model = EventoRastreio
    extra = 0
    readonly_fields = ('descricao', 'criado_em')
    can_delete = False


# ==========================
# AÇÕES EM MASSA
# ==========================
@admin.action(description='Marcar como ENTREGUE')
def marcar_como_entregue(modeladmin, request, queryset):
    for pedido in queryset:
        pedido.responsavel = request.user
        pedido.status = 'ENTREGUE'
        pedido.save()


@admin.action(description='Marcar como ATRASADO')
def marcar_como_atrasado(modeladmin, request, queryset):
    for pedido in queryset:
        pedido.responsavel = request.user
        pedido.status = 'ATRASADO'
        pedido.save()


# ==========================
# ADMIN DE PEDIDOS
# ==========================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'status',
        'cliente',
        'origem',
        'destino',
        'responsavel',
        'criado_em'
    )

    list_editable = ('status',)
    list_filter = ('status', 'criado_em')
    search_fields = ('codigo', 'cliente__nome')
    ordering = ('-criado_em',)

    readonly_fields = (
        'codigo',
        'criado_em',
        'atualizado_em',
    )

    inlines = [EventoInline]

    actions = [
        marcar_como_entregue,
        marcar_como_atrasado
    ]

    # 🔐 define automaticamente quem alterou
    def save_model(self, request, obj, form, change):
        if change:
            obj.responsavel = request.user
        super().save_model(request, obj, form, change)

    # 🔐 Somente ADMIN pode deletar
    def has_delete_permission(self, request, obj=None):
        return hasattr(request.user, 'perfil') and request.user.perfil.nivel == 'ADMIN'


# ==========================
# CLIENTE
# ==========================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')


# ==========================
# PERFIL
# ==========================
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nivel')
    list_filter = ('nivel',)
