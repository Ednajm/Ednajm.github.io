from django.contrib import admin
from .models import (
    CategoriaIntervento, PacchettoRistrutturazione, ElementoPacchetto,
    DiagnosiImmobile, ConsulenzaVideo, Newsletter, Ordine, PagamentoRata, MetodoPagamento
)


@admin.register(CategoriaIntervento)
class CategoriaInterventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'attiva', 'ordine', 'colore')
    list_filter = ('attiva',)
    search_fields = ('nome', 'descrizione')
    list_editable = ('attiva', 'ordine')
    ordering = ('ordine', 'nome')


class ElementoPacchettoInline(admin.TabularInline):
    model = ElementoPacchetto
    extra = 3
    fields = ('nome', 'descrizione', 'incluso', 'opzionale', 'costo_aggiuntivo', 'ordine')


@admin.register(PacchettoRistrutturazione)
class PacchettoRistrutturazioneAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'prezzo_min', 'prezzo_max', 'attivo', 'in_evidenza', 'ordinamento')
    list_filter = ('categoria', 'attivo', 'in_evidenza', 'difficolta', 'include_bonus')
    search_fields = ('nome', 'descrizione_breve', 'descrizione_completa')
    list_editable = ('attivo', 'in_evidenza', 'ordinamento')
    ordering = ('ordinamento', 'nome')
    inlines = [ElementoPacchettoInline]
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('nome', 'categoria', 'descrizione_breve', 'descrizione_completa')
        }),
        ('Prezzi e Tempi', {
            'fields': ('prezzo_min', 'prezzo_max', 'durata_giorni_min', 'durata_giorni_max', 'difficolta')
        }),
        ('Caratteristiche', {
            'fields': ('include_progetto', 'include_pratiche', 'include_bonus')
        }),
        ('Immagini', {
            'fields': ('immagine_principale', 'immagine_prima', 'immagine_dopo')
        }),
        ('Visibilità', {
            'fields': ('attivo', 'in_evidenza', 'ordinamento')
        }),
    )


@admin.register(ElementoPacchetto)
class ElementoPacchettoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pacchetto', 'incluso', 'opzionale', 'costo_aggiuntivo', 'ordine')
    list_filter = ('incluso', 'opzionale', 'pacchetto__categoria')
    search_fields = ('nome', 'descrizione', 'pacchetto__nome')
    list_editable = ('incluso', 'opzionale', 'ordine')
    ordering = ('pacchetto', 'ordine', 'nome')


@admin.register(DiagnosiImmobile)
class DiagnosiImmobileAdmin(admin.ModelAdmin):
    list_display = ('utente', 'stato', 'stato_generale', 'priorita_intervento', 'data_creazione', 'data_completamento')
    list_filter = ('stato', 'stato_generale', 'priorita_intervento', 'data_creazione')
    search_fields = ('utente__username', 'utente__email', 'utente__first_name', 'utente__last_name')
    readonly_fields = ('data_creazione',)
    ordering = ('-data_creazione',)
    
    fieldsets = (
        ('Utente e Stato', {
            'fields': ('utente', 'stato', 'data_creazione', 'data_completamento')
        }),
        ('Input Utente', {
            'fields': ('foto_immobile', 'planimetria', 'note_utente')
        }),
        ('Analisi Problemi', {
            'fields': ('problemi_strutturali', 'problemi_elettrici', 'problemi_idraulici', 'problemi_termici')
        }),
        ('Valutazioni', {
            'fields': ('stato_generale', 'priorita_intervento')
        }),
        ('Stime', {
            'fields': ('stima_costi_min', 'stima_costi_max', 'stima_tempo_giorni')
        }),
        ('Bonus e Consigli', {
            'fields': ('bonus_applicabili', 'pacchetti_consigliati')
        }),
        ('Report', {
            'fields': ('report_completo',),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('pacchetti_consigliati',)


@admin.register(ConsulenzaVideo)
class ConsulenzaVideoAdmin(admin.ModelAdmin):
    list_display = ('utente', 'stato', 'data_preferita', 'data_confermata', 'tipo_intervento', 'urgenza')
    list_filter = ('stato', 'urgenza', 'tipo_intervento', 'data_richiesta')
    search_fields = ('utente__username', 'utente__email', 'descrizione_progetto')
    list_editable = ('stato',)
    ordering = ('-data_richiesta',)
    
    fieldsets = (
        ('Utente e Stato', {
            'fields': ('utente', 'stato', 'data_richiesta')
        }),
        ('Programmazione', {
            'fields': ('data_preferita', 'data_confermata', 'link_meeting')
        }),
        ('Dettagli Progetto', {
            'fields': ('tipo_intervento', 'descrizione_progetto', 'budget_orientativo', 'urgenza')
        }),
        ('Note e Feedback', {
            'fields': ('note_consulente', 'valutazione_cliente', 'feedback_cliente')
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'attiva', 'data_iscrizione', 'data_disiscrizione')
    list_filter = ('attiva', 'data_iscrizione', 'interesse_ristrutturazioni', 'interesse_bonus')
    search_fields = ('email', 'nome')
    list_editable = ('attiva',)
    ordering = ('-data_iscrizione',)
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('email', 'nome', 'attiva')
        }),
        ('Date', {
            'fields': ('data_iscrizione', 'data_disiscrizione')
        }),
        ('Interessi', {
            'fields': ('interesse_ristrutturazioni', 'interesse_bonus', 'interesse_consigli', 'interesse_novita')
        }),
    )
    
    readonly_fields = ('data_iscrizione',)


@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ['numero_ordine', 'cliente', 'pacchetto', 'status', 'payment_status', 'totale', 'data_creazione']
    list_filter = ['status', 'payment_status', 'data_creazione']
    search_fields = ['numero_ordine', 'cliente__username', 'cliente__email', 'pacchetto__nome']
    readonly_fields = ['numero_ordine', 'data_creazione', 'data_aggiornamento', 'stripe_payment_intent_id']
    
    fieldsets = [
        ('Informazioni Ordine', {
            'fields': ['numero_ordine', 'cliente', 'pacchetto', 'status', 'payment_status']
        }),
        ('Dettagli Immobile', {
            'fields': ['indirizzo_immobile', 'citta', 'cap', 'superficie_mq', 'note_aggiuntive']
        }),
        ('Prezzi e Pagamento', {
            'fields': ['prezzo_base', 'costi_aggiuntivi', 'sconto_applicato', 'totale', 'stripe_payment_intent_id']
        }),
        ('Date', {
            'fields': ['data_creazione', 'data_aggiornamento', 'data_inizio_prevista', 'data_fine_prevista']
        })
    ]


@admin.register(PagamentoRata)
class PagamentoRataAdmin(admin.ModelAdmin):
    list_display = ['ordine', 'numero_rata', 'importo', 'data_scadenza', 'status', 'data_pagamento']
    list_filter = ['status', 'data_scadenza']
    search_fields = ['ordine__numero_ordine', 'ordine__cliente__username']
    readonly_fields = ['data_creazione', 'data_aggiornamento', 'stripe_payment_intent_id']


@admin.register(MetodoPagamento)
class MetodoPagamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo', 'brand', 'last4', 'is_default', 'attivo']
    list_filter = ['tipo', 'brand', 'is_default', 'attivo']
    search_fields = ['cliente__username', 'cliente__email']
    readonly_fields = ['stripe_payment_method_id', 'data_creazione', 'data_aggiornamento']
