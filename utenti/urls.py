from django.urls import path
from . import views

app_name = 'utenti'

urlpatterns = [
    # Autenticazione
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Magic Link Authentication
    path('api/send-magic-link/', views.send_magic_link, name='send_magic_link'),
    path('magic-login/<str:token>/', views.magic_login, name='magic_login'),
    path('api/check-user/', views.check_user_exists, name='check_user_exists'),
    path('api/reset-password/', views.reset_password_request, name='reset_password_request'),
    
    # Quick Login Services (placeholder implementations)
    path('login/google/', views.google_login_redirect, name='google_login'),
    path('login/spid/', views.spid_login_redirect, name='spid_login'),
    path('login/cie/', views.cie_login_redirect, name='cie_login'),
    
    # Profili
    path('profilo/', views.profilo_view, name='profilo'),
    path('profilo/cliente/', views.profilo_cliente_view, name='profilo_cliente'),
    path('profilo/impresa/', views.profilo_impresa_view, name='profilo_impresa'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Imprese pubbliche
    path('imprese/', views.lista_imprese_view, name='lista_imprese'),
    path('imprese/<int:impresa_id>/', views.dettaglio_impresa_view, name='dettaglio_impresa'),
]
