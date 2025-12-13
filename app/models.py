from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================
# PERFIL DO USUÁRIO (NÍVEL)
# ==========================

class Perfil(models.Model):

    NIVEL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('USER', 'Usuário'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='USER'
    )

    def __str__(self):
        return f"{self.usuario.username} ({self.get_nivel_display()})"


@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


# ==========================
# CLIENTE
# ==========================

class Cliente(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente',
        null=True,
        blank=True   # 👈 evita erro em migrations futuras
    )

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


# ==========================
# PEDIDO
# ==========================

class Pedido(models.Model):

    STATUS_CHOICES = [
        ('CRIADO', 'Criado'),
        ('COLETADO', 'Coletado'),
        ('TRANSITO', 'Em trânsito'),
        ('ENTREGUE', 'Entregue'),
        ('ATRASADO', 'Atrasado'),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CRIADO'
    )

    origem = models.CharField(
        max_length=100,
        blank=True      # 👈 evita erro se adicionar depois
    )

    destino = models.CharField(
        max_length=100,
        blank=True
    )

    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_responsaveis'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"{self.codigo} - {self.get_status_display()}"


# ==========================
# EVENTOS DE RASTREAMENTO
# ==========================

class EventoRastreio(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    descricao = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.pedido.codigo} - {self.descricao}"
