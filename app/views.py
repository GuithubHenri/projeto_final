from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Pedido, Cliente, Perfil

# --- VIEWS PÚBLICAS ---

def home(request):
    return render(request, 'home.html')

def consulta(request):
    codigo = request.GET.get('codigo')
    resultado = None

    if codigo:
        try:
            # Busca pelo campo 'codigo' (conforme models.py)
            resultado = Pedido.objects.get(codigo__iexact=codigo) 
        except Pedido.DoesNotExist:
            resultado = None

    return render(request, 'consulta.html', {'resultado': resultado})

# --- VIEWS DE AUTENTICAÇÃO ---

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home") 
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    # ALTERADO AQUI: Adicionado 'registration/' no caminho
    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já existe.')
            return redirect('cadastro')

        # 1. Cria o usuário no Django
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # 2. Cria automaticamente o registro de Cliente para ele
        Cliente.objects.create(
            usuario=user, 
            nome=username, 
            email=email
        )

        messages.success(request, 'Conta criada com sucesso! Faça login.')
        return redirect('login')

    # ALTERADO AQUI: Adicionado 'registration/' no caminho
    return render(request, 'registration/cadastro.html')

# --- VIEWS RESTRITAS ---

@login_required
def dashboard(request):
    # Pega os 5 últimos pedidos do banco
    ultimos_pedidos = Pedido.objects.all().order_by('-criado_em')[:5]

    # Cálculos para os Cards coloridos
    total = Pedido.objects.count()
    pendentes = Pedido.objects.exclude(status='ENTREGUE').count()
    atrasos = Pedido.objects.filter(status='ATRASADO').count()

    contexto = {
        'ultimos_pacotes': ultimos_pedidos, # Lista da tabela
        'total': total,                     # Card Azul
        'pendentes': pendentes,             # Card Amarelo
        'atrasos': atrasos,                 # Card Vermelho
    }
    return render(request, 'dashboard.html', contexto)

@login_required
def meus_pedidos(request):
    # Filtra Pedido onde o CLIENTE está ligado ao USUÁRIO logado.
    pedidos = Pedido.objects.filter(cliente__usuario=request.user).order_by('-criado_em')

    return render(request, 'meus_pedidos.html', {
        'pedidos': pedidos
    })

# --- ÁREAS ESPECÍFICAS ---

@login_required
def area_admin(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.nivel != 'ADMIN':
        return redirect('home') 
    return render(request, 'admin.html')

@login_required
def area_gestor(request):
    return render(request, 'gestor.html')

@login_required
def area_usuario(request):
    return render(request, 'usuario.html')