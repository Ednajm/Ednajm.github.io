from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfiloCliente, ProfiloImpresa


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informazioni Aggiuntive', {
            'fields': ('user_type', 'telefono', 'data_nascita', 'indirizzo', 
                      'citta', 'cap', 'provincia', 'foto_profilo')
        }),
        ('Preferenze', {
            'fields': ('accetta_marketing', 'accetta_privacy', 'ultimo_accesso_dashboard')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informazioni Aggiuntive', {
            'fields': ('user_type', 'email', 'telefono')
        }),
    )


class ProfiloClienteInline(admin.StackedInline):
    model = ProfiloCliente
    can_delete = False
    verbose_name_plural = 'Profilo Cliente'


class ProfiloImpresaInline(admin.StackedInline):
    model = ProfiloImpresa
    can_delete = False
    verbose_name_plural = 'Profilo Impresa'


@admin.register(ProfiloCliente)
class ProfiloClienteAdmin(admin.ModelAdmin):
    list_display = ('utente', 'tipo_immobile', 'proprieta', 'superficie_mq', 'anno_costruzione')
    list_filter = ('tipo_immobile', 'proprieta', 'ascensore', 'giardino')
    search_fields = ('utente__username', 'utente__email', 'utente__first_name', 'utente__last_name')
    raw_id_fields = ('utente',)


@admin.register(ProfiloImpresa)
class ProfiloImpresaAdmin(admin.ModelAdmin):
    list_display = ('ragione_sociale', 'tipo_impresa', 'partita_iva', 'abilitato', 'rating', 'numero_recensioni')
    list_filter = ('tipo_impresa', 'abilitato', 'data_verifica')
    search_fields = ('ragione_sociale', 'partita_iva', 'utente__username', 'utente__email')
    list_editable = ('abilitato',)
    raw_id_fields = ('utente',)
    readonly_fields = ('rating', 'numero_recensioni', 'data_verifica')
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('utente', 'ragione_sociale', 'partita_iva', 'codice_fiscale')
        }),
        ('Dettagli Impresa', {
            'fields': ('tipo_impresa', 'descrizione', 'anno_fondazione', 'numero_dipendenti')
        }),
        ('Contatti e Web', {
            'fields': ('sito_web', 'zone_operative')
        }),
        ('Certificazioni e Verifiche', {
            'fields': ('certificazioni', 'abilitato', 'data_verifica')
        }),
        ('Valutazioni', {
            'fields': ('rating', 'numero_recensioni'),
            'classes': ('collapse',)
        }),
    )
