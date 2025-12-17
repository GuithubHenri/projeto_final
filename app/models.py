from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import random


# ==========================
# PERFIL
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
        Perfil.objects.create(
            usuario=instance,
            nivel='ADMIN' if instance.is_superuser else 'USER'
        )


# ==========================
# CLIENTE
# ==========================

class Cliente(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente',
        null=True,
        blank=True
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
        unique=True,
        blank=True,
        editable=False
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

    origem = models.CharField(max_length=100, blank=True)
    destino = models.CharField(max_length=100, blank=True)

    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_responsaveis'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    EVENTOS_POR_STATUS = {
        'CRIADO': ['Pedido criado no sistema.', 'Pagamento confirmado.'],
        'COLETADO': ['Pedido coletado pela transportadora.'],
        'TRANSITO': [
            'Pedido em trânsito.',
            'Pedido passou por centro logístico.',
            'Pedido a caminho do destino.'
        ],
        'ENTREGUE': ['Pedido entregue ao destinatário.'],
        'ATRASADO': [
            'Pedido atrasado devido a condições climáticas.',
            'Pedido retido para verificação.'
        ],
    }

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_status = Pedido.objects.get(pk=self.pk).status

        if not self.codigo:
            self.codigo = "LP-" + str(uuid.uuid4()).upper()[:8]

        super().save(*args, **kwargs)

        # 🔹 Criação automática do histórico
        if is_new:
            EventoRastreio.objects.create(
                pedido=self,
                descricao="Pedido criado no sistema."
            )
        elif old_status != self.status:
            eventos = self.EVENTOS_POR_STATUS.get(self.status, [])
            if eventos:
                EventoRastreio.objects.create(
                    pedido=self,
                    descricao=random.choice(eventos)
                )

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"{self.codigo} - {self.get_status_display()}"


# ==========================
# EVENTOS DE RASTREIO
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
        verbose_name = 'Evento de Rastreio'
        verbose_name_plural = 'Eventos de Rastreio'

    def __str__(self):
        return f"{self.pedido.codigo} - {self.descricao}"
