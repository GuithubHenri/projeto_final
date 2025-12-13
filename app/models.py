from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid # Necessário para gerar códigos únicos

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
        blank=True, # Permite deixar vazio para gerar automático
        editable=False # Impede edição manual após criado
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

    # --- LÓGICA AUTOMÁTICA ---
    def save(self, *args, **kwargs):
        # 1. Detecta se é criação ou edição
        is_new = self.pk is None
        old_status = None

        if not is_new:
            # Busca o status antigo no banco para comparar
            old_instance = Pedido.objects.get(pk=self.pk)
            old_status = old_instance.status

        # 2. Gera código único se não existir (Ex: LP-A1B2C3)
        if not self.codigo:
            self.codigo = "LP-" + str(uuid.uuid4()).upper()[:8]

        # 3. Salva o Pedido
        super().save(*args, **kwargs)

        # 4. Cria Eventos na Timeline Automaticamente
        if is_new:
            EventoRastreio.objects.create(
                pedido=self, 
                descricao="Pedido criado no sistema."
            )
        elif self.status != old_status:
            # Se o status mudou, registra o evento
            EventoRastreio.objects.create(
                pedido=self, 
                descricao=f"Status atualizado para: {self.get_status_display()}"
            )

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
        ordering = ['-criado_em'] # O mais recente aparece primeiro

    def __str__(self):
        return f"{self.pedido.codigo} - {self.descricao}"