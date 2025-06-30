from django.urls import path, include
from . import views, views_dashboard

app_name = 'artigiani'

urlpatterns = [
    # Ricerca e listing
    path('', views.ricerca_artigiani, name='ricerca'),
    path('categorie/', views.categorie_artigiani, name='categorie'),
    path('cerca-citta/', views.cerca_per_citta, name='cerca_citta'),
    
    # Dettaglio artigiano
    path('artigiano/<int:artigiano_id>/', views.dettaglio_artigiano, name='dettaglio'),
    path('contatta/<int:artigiano_id>/', views.contatta_artigiano, name='contatta'),
    
    # Preventivi
    path('preventivo/', views.richiedi_preventivo, name='richiedi_preventivo'),
    path('preventivo/<int:richiesta_id>/', views.dettaglio_richiesta, name='dettaglio_richiesta'),
    path('preventivo-ai/', views.genera_preventivo_ai, name='preventivo_ai'),
    
    # AI Features
    path('analizza-foto/', views.analizza_foto_ai, name='analizza_foto'),
    
    # Dashboard admin
    path('dashboard/stats/', views.statistiche_dashboard, name='dashboard_stats'),
    
    # Dashboard Artigiani
    path('dashboard/', include([
        path('', views_dashboard.dashboard_artigiano, name='dashboard_home'),
        path('profilo/modifica/', views_dashboard.profilo_artigiano_edit, name='profilo_edit'),
        path('profilo/completa/', views_dashboard.completa_profilo_artigiano, name='profilo'),
        path('profilo/crea/', views_dashboard.crea_profilo_artigiano, name='crea_profilo'),
        path('foto-lavori/', views_dashboard.foto_lavori_gestione, name='foto_lavori'),
        path('foto-lavori/upload/', views_dashboard.upload_foto_lavoro, name='upload_foto'),
        path('foto-lavori/elimina/<int:foto_id>/', views_dashboard.elimina_foto_lavoro, name='elimina_foto'),
        path('recensioni/', views_dashboard.recensioni_gestione, name='recensioni'),
        path('richieste/', views_dashboard.richieste_preventivo_gestione, name='richieste'),
        path('statistiche/', views_dashboard.statistiche_dettagliate, name='statistiche'),
        path('impostazioni/', views_dashboard.impostazioni_artigiano, name='impostazioni'),
        
        # Gestione Orari e Appuntamenti
        path('orari/', views_dashboard.orari_disponibilita, name='orari_disponibilita'),
        path('appuntamenti/', views_dashboard.appuntamenti_lista, name='appuntamenti'),
        path('appuntamenti/nuovo/', views_dashboard.appuntamento_nuovo, name='appuntamento_nuovo'),
        path('appuntamenti/modifica/<int:appuntamento_id>/', views_dashboard.appuntamento_edit, name='appuntamento_edit'),
        path('appuntamenti/stato/<int:appuntamento_id>/', views_dashboard.appuntamento_cambia_stato, name='appuntamento_stato'),
        path('calendario/', views_dashboard.calendario_appuntamenti, name='calendario'),
        path('eccezioni-orario/', views_dashboard.eccezioni_orario, name='eccezioni_orario'),
        path('eccezioni-orario/elimina/<int:eccezione_id>/', views_dashboard.eccezione_elimina, name='eccezione_elimina'),
        
        # Gestione Documenti per Certificazione
        path('documenti/', views_dashboard.documenti_gestione, name='documenti'),
        path('documenti/upload/', views_dashboard.upload_documento, name='upload_documento'),
        path('documenti/elimina/<int:documento_id>/', views_dashboard.elimina_documento, name='elimina_documento'),
        
        # Gestione Video
        path('video/', views_dashboard.video_gestione, name='video'),
        path('video/upload/', views_dashboard.upload_video, name='upload_video'),
        path('video/elimina/<int:video_id>/', views_dashboard.elimina_video, name='elimina_video'),
        
        # Messaggi dai Clienti
        path('messaggi/', views_dashboard.messaggi_clienti, name='messaggi'),
        path('messaggi/<int:messaggio_id>/', views_dashboard.dettaglio_messaggio, name='dettaglio_messaggio'),
        path('messaggi/archivia/<int:messaggio_id>/', views_dashboard.archivia_messaggio, name='archivia_messaggio'),
        
        # Suggerimenti IA
        path('suggerimenti/', views_dashboard.suggerimenti_ia, name='suggerimenti'),
        path('suggerimenti/applica/<int:suggerimento_id>/', views_dashboard.applica_suggerimento, name='applica_suggerimento'),
        
        # Certificazioni
        path('certificazioni/', views_dashboard.certificazioni_gestione, name='certificazioni'),
    ])),
]
