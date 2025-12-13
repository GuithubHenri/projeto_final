from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('consulta/', views.consulta, name='consulta'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('cadastro/', views.cadastro_view, name='cadastro'),

    # áreas por nível (se quiser manter)
    path('admin-area/', views.area_admin, name='area_admin'),
    path('gestor/', views.area_gestor, name='area_gestor'),
    path('usuario/', views.area_usuario, name='area_usuario'),
]
