from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CategoriaArtigiano, ProfiloArtigiano, FotoLavoro, 
    RecensioneArtigiano, RichiestaPreventivo, RispostaPreventivo
)


@admin.register(CategoriaArtigiano)
class CategoriaArtigianoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icona_display', 'colore_display', 'attiva', 'ordine']
    list_filter = ['attiva']
    search_fields = ['nome', 'descrizione']
    ordering = ['ordine', 'nome']
    
    def icona_display(self, obj):
        if obj.icona:
            return format_html('<i class="{}"></i> {}', obj.icona, obj.icona)
        return '-'
    icona_display.short_description = 'Icona'
    
    def colore_display(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.colore, obj.colore
        )
    colore_display.short_description = 'Colore'


class FotoLavoroInline(admin.TabularInline):
    model = FotoLavoro
    extra = 0
    fields = ['immagine', 'titolo', 'categoria', 'in_evidenza', 'ordine']


@admin.register(ProfiloArtigiano)
class ProfiloArtigianoAdmin(admin.ModelAdmin):
    list_display = [
        'nome_attivita', 'categoria_principale', 'citta', 
        'verificato', 'premium', 'attivo', 'voto_medio_display',
        'numero_recensioni', 'data_registrazione'
    ]
    list_filter = [
        'verificato', 'premium', 'attivo', 'categoria_principale',
        'fascia_prezzo', 'ha_partita_iva', 'disponibilita'
    ]
    search_fields = [
        'nome_attivita', 'utente__first_name', 'utente__last_name',
        'citta', 'cap', 'descrizione'
    ]
    readonly_fields = [
        'data_registrazione', 'ultimo_accesso', 'visualizzazioni_profilo',
        'contatti_ricevuti', 'voto_medio', 'numero_recensioni'
    ]
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('utente', 'nome_attivita', 'categoria_principale', 'categorie_secondarie')
        }),
        ('Localizzazione', {
            'fields': ('citta', 'cap', 'indirizzo', 'raggio_azione_km')
        }),
        ('Attività', {
            'fields': ('partita_iva', 'ha_partita_iva', 'descrizione', 'descrizione_ai_generata', 'usa_descrizione_ai')
        }),
        ('Prezzi e Disponibilità', {
            'fields': ('fascia_prezzo', 'prezzo_orario_min', 'prezzo_orario_max', 'disponibilita')
        }),
        ('Competenze e Lingue', {
            'fields': ('anni_esperienza', 'italiano', 'inglese', 'francese', 'arabo', 'altre_lingue')
        }),
        ('Immagini', {
            'fields': ('foto_profilo', 'foto_banner')
        }),
        ('Contatti', {
            'fields': ('telefono', 'whatsapp', 'email_lavoro', 'sito_web')
        }),
        ('Stato', {
            'fields': ('verificato', 'attivo', 'premium')
        }),
        ('Statistiche', {
            'fields': ('numero_lavori_completati', 'visualizzazioni_profilo', 'contatti_ricevuti', 'data_registrazione', 'ultimo_accesso'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FotoLavoroInline]
    
    def voto_medio_display(self, obj):
        voto = obj.voto_medio
        if voto > 0:
            stars = '★' * int(voto) + '☆' * (5 - int(voto))
            return format_html('{} ({:.1f})', stars, voto)
        return '-'
    voto_medio_display.short_description = 'Voto Medio'
    
    actions = ['verifica_artigiani', 'rimuovi_verifica', 'attiva_premium', 'disattiva_premium']
    
    def verifica_artigiani(self, request, queryset):
        updated = queryset.update(verificato=True)
        self.message_user(request, f'{updated} artigiani verificati.')
    verifica_artigiani.short_description = "Verifica artigiani selezionati"
    
    def rimuovi_verifica(self, request, queryset):
        updated = queryset.update(verificato=False)
        self.message_user(request, f'{updated} artigiani non più verificati.')
    rimuovi_verifica.short_description = "Rimuovi verifica"
    
    def attiva_premium(self, request, queryset):
        updated = queryset.update(premium=True)
        self.message_user(request, f'{updated} artigiani impostati come Premium.')
    attiva_premium.short_description = "Attiva Premium"
    
    def disattiva_premium(self, request, queryset):
        updated = queryset.update(premium=False)
        self.message_user(request, f'{updated} artigiani non più Premium.')
    disattiva_premium.short_description = "Disattiva Premium"


@admin.register(FotoLavoro)
class FotoLavoroAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'artigiano', 'categoria', 'in_evidenza', 'data_lavoro', 'ordine']
    list_filter = ['in_evidenza', 'categoria', 'data_lavoro']
    search_fields = ['titolo', 'descrizione', 'artigiano__nome_attivita']
    ordering = ['-in_evidenza', 'ordine', '-data_lavoro']


@admin.register(RecensioneArtigiano)
class RecensioneArtigianoAdmin(admin.ModelAdmin):
    list_display = [
        'cliente_nome', 'artigiano', 'voto', 'verificata', 
        'data_recensione', 'data_verifica'
    ]
    list_filter = ['verificata', 'voto', 'data_recensione']
    search_fields = [
        'cliente_nome', 'cliente_email', 'artigiano__nome_attivita',
        'titolo', 'commento'
    ]
    readonly_fields = ['data_recensione']
    ordering = ['-data_recensione']
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente_nome', 'cliente_email', 'cliente_telefono')
        }),
        ('Recensione', {
            'fields': ('artigiano', 'voto', 'titolo', 'commento')
        }),
        ('Valutazioni Dettagliate', {
            'fields': ('qualita_lavoro', 'puntualita', 'cortesia', 'rapporto_qualita_prezzo')
        }),
        ('Stato', {
            'fields': ('verificata', 'data_recensione', 'data_verifica')
        }),
    )
    
    actions = ['verifica_recensioni']
    
    def verifica_recensioni(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(verificata=True, data_verifica=timezone.now())
        self.message_user(request, f'{updated} recensioni verificate.')
    verifica_recensioni.short_description = "Verifica recensioni selezionate"


@admin.register(RichiestaPreventivo)
class RichiestaPreventivoAdmin(admin.ModelAdmin):
    list_display = [
        'cliente_nome', 'titolo', 'categoria', 'citta', 
        'stato', 'urgenza', 'data_creazione'
    ]
    list_filter = ['stato', 'urgenza', 'categoria', 'data_creazione']
    search_fields = [
        'cliente_nome', 'cliente_email', 'titolo', 
        'descrizione', 'citta'
    ]
    readonly_fields = ['data_creazione', 'data_ultima_modifica']
    ordering = ['-data_creazione']
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente_nome', 'cliente_email', 'cliente_telefono')
        }),
        ('Richiesta', {
            'fields': ('categoria', 'titolo', 'descrizione', 'urgenza')
        }),
        ('Localizzazione', {
            'fields': ('citta', 'cap', 'indirizzo')
        }),
        ('Dettagli Tecnici', {
            'fields': ('superficie_mq', 'budget_min', 'budget_max', 'data_inizio_preferita')
        }),
        ('Foto', {
            'fields': ('foto1', 'foto2', 'foto3')
        }),
        ('AI', {
            'fields': ('analisi_ai', 'categoria_suggerita_ai'),
            'classes': ('collapse',)
        }),
        ('Stato', {
            'fields': ('stato', 'data_creazione', 'data_ultima_modifica')
        }),
    )


@admin.register(RispostaPreventivo)
class RispostaPrevenzivoAdmin(admin.ModelAdmin):
    list_display = [
        'artigiano', 'richiesta_cliente', 'prezzo_offerto', 
        'giorni_completamento', 'stato', 'data_invio'
    ]
    list_filter = ['stato', 'materiali_inclusi', 'data_invio']
    search_fields = [
        'artigiano__nome_attivita', 'richiesta__cliente_nome',
        'richiesta__titolo', 'descrizione_offerta'
    ]
    readonly_fields = ['data_invio', 'data_vista']
    ordering = ['-data_invio']
    
    def richiesta_cliente(self, obj):
        return f"{obj.richiesta.cliente_nome} - {obj.richiesta.titolo}"
    richiesta_cliente.short_description = 'Cliente/Richiesta'
