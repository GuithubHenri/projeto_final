from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .models import Pedido


@login_required
def home(request):
    perfil = request.user.perfil

    contexto = {
        'usuario': request.user,
        'perfil': perfil
    }

    return render(request, 'home.html', contexto)
    
@login_required

def area_admin(request):
    if not request.user.perfil.is_admin():
        return HttpResponseForbidden('Acesso negado')

    return render(request, 'admin.html')
@login_required
def area_gestor(request):
    perfil = request.user.perfil

    if perfil.nivel not in ['ADMIN', 'GESTOR']:
        return HttpResponseForbidden('Acesso negado')

    return render(request, 'gestor.html')
@login_required
def area_usuario(request):
    return render(request, 'usuario.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')


def consulta(request):
    # lógica futura de rastreio
    return render(request, 'consulta.html')


@login_required
def dashboard(request):
    # depois você pode popular com dados reais
    contexto = {
        'ultimas': []
    }
    return render(request, 'dashboard.html', contexto)

def home(request):
    return render(request, 'home.html')

def consulta(request):
    codigo = request.GET.get('codigo')
    resultado = None

    if codigo:
        # Simulação (depois vira banco)
        if codigo.upper().startswith("LP"):
            resultado = {
                "status": "Em trânsito",
                "timeline": [
                    {"timestamp": "12/12/2025 08:20", "description": "Pedido coletado"},
                    {"timestamp": "12/12/2025 13:40", "description": "Centro de distribuição"},
                    {"timestamp": "13/12/2025 09:10", "description": "Saiu para entrega"},
                ]
            }

    return render(request, 'consulta.html', {"resultado": resultado})
@login_required
def dashboard(request):
    ultimas = [
        {"codigo": "LP001", "cliente": "João Silva", "status": "Entregue", "atualizado": "Hoje"},
        {"codigo": "LP002", "cliente": "Maria Lima", "status": "Em trânsito", "atualizado": "Ontem"},
    ]
    return render(request, 'dashboard.html', {"ultimas": ultimas})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("home")
    
def consulta(request):
    codigo = request.GET.get('codigo')
    resultado = None

    if codigo:
        try:
            pedido = Pedido.objects.get(codigo__iexact=codigo)
            resultado = {
                "status": pedido.get_status_display(),
                "timeline": pedido.eventos.all()
            }
        except Pedido.DoesNotExist:
            resultado = None

    return render(request, 'consulta.html', {
        "resultado": resultado
    })
    
from django.contrib.auth.decorators import login_required
from .models import Pedido


@login_required
def dashboard(request):
    ultimas = Pedido.objects.select_related('cliente').order_by('-atualizado_em')[:5]

    context = {
        "ultimas": ultimas,
        "total": Pedido.objects.count(),
        "pendentes": Pedido.objects.exclude(status='ENTREGUE').count(),
        "atrasos": Pedido.objects.filter(status='ATRASADO').count(),
    }

    return render(request, 'dashboard.html', context)

def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
            return redirect('cadastro')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Conta criada com sucesso!')
        return redirect('login')

    return render(request, 'cadastro.html')
@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user)

    return render(request, 'meus_pedidos.html', {
        'pedidos': pedidos
    })
