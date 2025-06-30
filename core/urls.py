from django.urls import path
from . import views
from . import views_payments

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', views.home_view, name='home'),
    
    # Pacchetti
    path('pacchetti/', views.pacchetti_view, name='pacchetti'),
    path('pacchetti/<int:pacchetto_id>/', views.dettaglio_pacchetto_view, name='dettaglio_pacchetto'),
    
    # Pagine informative
    path('come-funziona/', views.come_funziona_view, name='come_funziona'),
    path('bonus-fiscali/', views.bonus_fiscali_view, name='bonus_fiscali'),
    path('imprese/', views.imprese_view, name='imprese'),
    path('contatti/', views.contatti_view, name='contatti'),
    
    # Pagamenti e ordini
    path('checkout/<int:pacchetto_id>/', views_payments.checkout_view, name='checkout'),
    path('payment/<int:ordine_id>/', views_payments.payment_view, name='payment'),
    path('payment-success/<int:ordine_id>/', views_payments.payment_success_view, name='payment_success'),
    path('webhooks/stripe/', views_payments.stripe_webhook, name='stripe_webhook'),
    
    # Gestione ordini e pagamenti
    path('ordini/', views_payments.ordini_view, name='ordini'),
    path('ordini/<int:ordine_id>/', views_payments.dettaglio_ordine_view, name='dettaglio_ordine'),
    path('metodi-pagamento/', views_payments.metodi_pagamento_view, name='metodi_pagamento'),
    path('api/aggiungi-metodo-pagamento/', views_payments.aggiungi_metodo_pagamento, name='aggiungi_metodo_pagamento'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/impresa/', views.dashboard_impresa_view, name='dashboard_impresa'),
    
    # Diagnosi
    path('diagnosi/nuova/', views.diagnosi_view, name='diagnosi'),
    path('diagnosi/', views.lista_diagnosi_view, name='lista_diagnosi'),
    path('diagnosi/<int:diagnosi_id>/', views.dettaglio_diagnosi_view, name='dettaglio_diagnosi'),
    
    # Consulenze Video
    path('consulenza/', views.consulenza_video_view, name='consulenza_video'),
    path('consulenze/', views.lista_consulenze_view, name='lista_consulenze'),
    
    # Newsletter
    path('newsletter/signup/', views.newsletter_signup_view, name='newsletter_signup'),
    path('come-funziona/', views.come_funziona_view, name='come_funziona'),
    path('bonus-fiscali/', views.bonus_fiscali_view, name='bonus_fiscali'),
    path('contatti/', views.contatti_view, name='contatti'),
    
    # Nuove pagine
    path('imprese/', views.imprese_view, name='imprese'),
]
