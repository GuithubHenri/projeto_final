from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import CadastroForm
from django.contrib.auth.forms import AuthenticationForm

from .models import Pedido, Cliente, EventoRastreio
import random


# ==========================
# VIEWS PÚBLICAS
# ==========================

def home(request):
    return render(request, 'home.html')


def consulta(request):
    codigo = request.GET.get('codigo')
    resultado = None

    if codigo:
        try:
            resultado = Pedido.objects.get(codigo__iexact=codigo)
        except Pedido.DoesNotExist:
            resultado = None

    return render(request, 'consulta.html', {'resultado': resultado})


# ==========================
# AUTENTICAÇÃO
# ==========================

def login_view(request):
    # impede usuário logado de voltar ao login
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil'):
            if request.user.perfil.nivel in ['ADMIN', 'GESTOR']:
                return redirect('dashboard')
            return redirect('meus_pedidos')
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        if hasattr(user, 'perfil'):
            if user.perfil.nivel in ['ADMIN', 'GESTOR']:
                return redirect('dashboard')
            return redirect('meus_pedidos')

        return redirect('home')

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("home")


def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)

        if form.is_valid():
            user = form.save()

            # adiciona ao grupo CLIENTE (opcional)
            try:
                grupo_cliente = Group.objects.get(name='CLIENTE')
                user.groups.add(grupo_cliente)
            except Group.DoesNotExist:
                pass

            Cliente.objects.create(
                usuario=user,
                nome=user.username,
                email=user.email
            )

            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')
    else:
        form = CadastroForm()

    return render(request, 'registration/cadastro.html', {'form': form})

# ==========================
# VIEWS RESTRITAS
# ==========================

@login_required
def dashboard(request):
    # 🔒 CLIENTE NÃO PODE ACESSAR NEM VIA URL
    if request.user.perfil.nivel == 'USER':
        return HttpResponseForbidden("Acesso não autorizado.")

    ultimos_pedidos = Pedido.objects.all().order_by('-criado_em')[:5]

    contexto = {
        'ultimos_pacotes': ultimos_pedidos,
        'total': Pedido.objects.count(),
        'pendentes': Pedido.objects.exclude(status='ENTREGUE').count(),
        'atrasos': Pedido.objects.filter(status='ATRASADO').count(),
    }

    return render(request, 'dashboard.html', contexto)


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(
        cliente__usuario=request.user
    ).order_by('-criado_em')

    return render(request, 'meus_pedidos.html', {'pedidos': pedidos})


# ==========================
# ÁREAS ESPECÍFICAS (OPCIONAL)
# ==========================

@login_required
def area_admin(request):
    if request.user.perfil.nivel != 'ADMIN':
        return redirect('home')
    return render(request, 'admin.html')


@login_required
def area_gestor(request):
    if request.user.perfil.nivel != 'GESTOR':
        return redirect('home')
    return render(request, 'gestor.html')


@login_required
def area_usuario(request):
    if request.user.perfil.nivel != 'USER':
        return redirect('home')
    return render(request, 'usuario.html')
@login_required
def gerar_pacote_aleatorio(request):
    # Verifica se existe pelo menos um cliente para associar o pedido
    if not Cliente.objects.exists():
        messages.error(request, "Não há clientes cadastrados para gerar um pedido.")
        return redirect('dashboard') # Redireciona para um lugar seguro

    # 1. Seleciona um Cliente aleatoriamente
    # O truque '?' faz a seleção aleatória no banco de dados.
    cliente_aleatorio = Cliente.objects.order_by('?').first()

    # 2. Gera dados aleatórios para o pedido
    # Usando listas simples para simular locais
    LOCAIS = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Recife']
    STATUS_INICIAIS = ['CRIADO', 'COLETADO', 'TRANSITO']

    origem = random.choice(LOCAIS)
    destino = random.choice([l for l in LOCAIS if l != origem]) # Garante que origem e destino são diferentes
    status_inicial = random.choice(STATUS_INICIAIS)
    
    # 3. Cria o novo Pedido
    # O código e o primeiro EventoRastreio são gerados automaticamente no método Pedido.save()
    novo_pedido = Pedido.objects.create(
        cliente=cliente_aleatorio,
        origem=origem,
        destino=destino,
        status=status_inicial
    )
    
    # Opcional: para simular mais rastreio, podemos adicionar mais um evento
    if novo_pedido.status == 'TRANSITO':
        eventos = novo_pedido.EVENTOS_POR_STATUS.get('TRANSITO', [])
        if eventos:
            EventoRastreio.objects.create(
                pedido=novo_pedido,
                descricao=random.choice(eventos)
            )

    messages.success(request, f"Novo pacote aleatório gerado com sucesso! Código: **{novo_pedido.codigo}**")
    
    # Redireciona para a tela de consulta para ver o pacote gerado
    return redirect(f'/consulta/?codigo={novo_pedido.codigo}')
@login_required
def alterar_status_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # 🔐 Permissão
    if request.user.perfil.nivel not in ['ADMIN', 'GESTOR']:
        raise PermissionDenied

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        pedido.status = novo_status
        pedido.responsavel = request.user
        pedido.save()  # <-- cria EventoRastreio automaticamente

    return redirect('dashboard')