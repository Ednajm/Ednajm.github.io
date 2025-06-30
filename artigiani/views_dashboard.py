from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    ProfiloArtigiano, FotoLavoro, RecensioneArtigiano, RichiestaPreventivo, 
    CategoriaArtigiano, OrarioDisponibilita, Appuntamento, EccezioneOrario,
    DocumentoArtigiano, VideoArtigiano, MessaggioCliente, SuggerimentoIA
)
from .forms import (
    ProfiloArtigianoForm, FotoLavoroForm, OrarioDisponibilitaForm, 
    AppuntamentoForm, EccezioneOrarioForm, DocumentoArtigianoForm, VideoArtigianoForm,
    RispostaMessaggioForm, ProfiloArtigianoCompletoForm
)


@login_required
def dashboard_artigiano(request):
    """Dashboard principale dell'artigiano"""
    
    # Verifica se l'utente ha un profilo artigiano
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        # Reindirizza alla creazione del profilo
        return redirect('artigiani:crea_profilo')
    
    # Statistiche dashboard
    oggi = timezone.now().date()
    inizio_mese = oggi.replace(day=1)
    inizio_settimana = oggi - timedelta(days=oggi.weekday())
    
    stats = {
        'visualizzazioni_totali': profilo.visualizzazioni_profilo,
        'visualizzazioni_settimana': profilo.visualizzazioni_profilo // 7,  # Simulato
        'contatti_totali': profilo.contatti_ricevuti,
        'contatti_mese': profilo.contatti_ricevuti // 4,  # Simulato
        'recensioni_totali': profilo.numero_recensioni,
        'voto_medio': profilo.voto_medio,
        'foto_lavori': profilo.foto_lavori.count(),
        'posizione_ricerca': calculate_search_position(profilo),
        # Nuove statistiche
        'messaggi_nuovi': profilo.messaggi_ricevuti.filter(stato='nuovo').count(),
        'messaggi_totali': profilo.messaggi_ricevuti.count(),
        'documenti_verificati': profilo.documenti.filter(stato_verifica='verificato').count(),
        'documenti_totali': profilo.documenti.count(),
        'video_totali': profilo.video.count(),
        'certificazioni_attive': profilo.certificazioni.filter(attiva=True).count(),
        'suggerimenti_attivi': profilo.suggerimenti_ia.filter(applicato=False).count(),
        'punteggio_certificazione': sum(cert.punteggio for cert in profilo.certificazioni.filter(attiva=True)),
    }
    
    # Richieste preventivo recenti
    richieste_recenti = RichiestaPreventivo.objects.filter(
        categoria=profilo.categoria_principale,
        citta__icontains=profilo.citta
    ).order_by('-data_creazione')[:5]
    
    # Recensioni recenti
    recensioni_recenti = profilo.recensioni.filter(
        verificata=True
    ).order_by('-data_recensione')[:5]
    
    # Attività recenti (simulata)
    attivita_recenti = [
        {
            'tipo': 'view',
            'icona': 'fas fa-eye',
            'titolo': 'Nuovo visitatore',
            'descrizione': f'Il tuo profilo è stato visualizzato da un cliente',
            'data': timezone.now() - timedelta(hours=2),
        },
        {
            'tipo': 'contact',
            'icona': 'fas fa-phone',
            'titolo': 'Richiesta contatto',
            'descrizione': f'Un cliente ha richiesto il tuo contatto',
            'data': timezone.now() - timedelta(hours=5),
        },
        {
            'tipo': 'review',
            'icona': 'fas fa-star',
            'titolo': 'Nuova recensione',
            'descrizione': f'Hai ricevuto una nuova recensione da un cliente',
            'data': timezone.now() - timedelta(days=1),
        },
    ]
    
    context = {
        'profilo': profilo,
        'stats': stats,
        'richieste_recenti': richieste_recenti,
        'recensioni_recenti': recensioni_recenti,
        'attivita_recenti': attivita_recenti,
    }
    
    return render(request, 'artigiani/dashboard/home.html', context)


@login_required
def profilo_artigiano_edit(request):
    """Modifica profilo artigiano"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = ProfiloArtigianoForm(request.POST, request.FILES, instance=profilo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo aggiornato con successo!')
            return redirect('artigiani:dashboard_home')
    else:
        form = ProfiloArtigianoForm(instance=profilo)
    
    context = {
        'form': form,
        'profilo': profilo,
        'categorie': CategoriaArtigiano.objects.filter(attiva=True),
    }
    
    return render(request, 'artigiani/dashboard/profilo_edit.html', context)


@login_required
def crea_profilo_artigiano(request):
    """Creazione nuovo profilo artigiano"""
    
    # Verifica che l'utente non abbia già un profilo
    if hasattr(request.user, 'profiloartigiano'):
        return redirect('artigiani:dashboard_home')
    
    if request.method == 'POST':
        form = ProfiloArtigianoForm(request.POST, request.FILES)
        if form.is_valid():
            profilo = form.save(commit=False)
            profilo.utente = request.user
            profilo.save()
            form.save_m2m()  # Per salvare le relazioni many-to-many
            
            messages.success(request, 'Profilo creato con successo! Benvenuto nella community degli artigiani.')
            return redirect('artigiani:dashboard_home')
    else:
        form = ProfiloArtigianoForm()
    
    context = {
        'form': form,
        'categorie': CategoriaArtigiano.objects.filter(attiva=True),
    }
    
    return render(request, 'artigiani/dashboard/crea_profilo.html', context)


@login_required
def foto_lavori_gestione(request):
    """Gestione foto lavori"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    foto_lavori = profilo.foto_lavori.all().order_by('-in_evidenza', 'ordine')
    
    context = {
        'profilo': profilo,
        'foto_lavori': foto_lavori,
    }
    
    return render(request, 'artigiani/dashboard/foto_lavori.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_foto_lavoro(request):
    """Upload nuova foto lavoro"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profilo non trovato'})
    
    if request.FILES.get('immagine'):
        foto = FotoLavoro.objects.create(
            artigiano=profilo,
            immagine=request.FILES['immagine'],
            titolo=request.POST.get('titolo', ''),
            descrizione=request.POST.get('descrizione', ''),
            categoria=profilo.categoria_principale,
            in_evidenza=request.POST.get('in_evidenza') == 'true'
        )
        
        return JsonResponse({
            'success': True,
            'foto_id': foto.id,
            'url': foto.immagine.url,
            'message': 'Foto caricata con successo!'
        })
    
    return JsonResponse({'success': False, 'error': 'Nessuna immagine selezionata'})


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def elimina_foto_lavoro(request, foto_id):
    """Elimina foto lavoro"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        foto = get_object_or_404(FotoLavoro, id=foto_id, artigiano=profilo)
        foto.delete()
        
        return JsonResponse({'success': True, 'message': 'Foto eliminata'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def recensioni_gestione(request):
    """Gestione recensioni"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    recensioni = profilo.recensioni.all().order_by('-data_recensione')
    
    # Paginazione
    paginator = Paginator(recensioni, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiche recensioni
    stats_recensioni = {
        'totali': recensioni.count(),
        'verificate': recensioni.filter(verificata=True).count(),
        'media_voto': profilo.voto_medio,
        'media_qualita': recensioni.aggregate(Avg('qualita_lavoro'))['qualita_lavoro__avg'] or 0,
        'media_puntualita': recensioni.aggregate(Avg('puntualita'))['puntualita__avg'] or 0,
        'media_cortesia': recensioni.aggregate(Avg('cortesia'))['cortesia__avg'] or 0,
        'media_rapporto_qp': recensioni.aggregate(Avg('rapporto_qualita_prezzo'))['rapporto_qualita_prezzo__avg'] or 0,
    }
    
    context = {
        'profilo': profilo,
        'page_obj': page_obj,
        'stats_recensioni': stats_recensioni,
    }
    
    return render(request, 'artigiani/dashboard/recensioni.html', context)


@login_required
def richieste_preventivo_gestione(request):
    """Gestione richieste preventivo"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Trova richieste nella zona dell'artigiano
    richieste = RichiestaPreventivo.objects.filter(
        Q(categoria=profilo.categoria_principale) |
        Q(categoria__in=profilo.categorie_secondarie.all()),
        citta__icontains=profilo.citta
    ).order_by('-data_creazione')
    
    # Filtri
    stato = request.GET.get('stato')
    if stato:
        richieste = richieste.filter(stato=stato)
    
    # Paginazione
    paginator = Paginator(richieste, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profilo': profilo,
        'page_obj': page_obj,
        'stati_choices': RichiestaPreventivo.STATO_CHOICES,
        'filtro_stato': stato,
    }
    
    return render(request, 'artigiani/dashboard/richieste.html', context)


@login_required
def impostazioni_artigiano(request):
    """Impostazioni account artigiano"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        # Gestisci aggiornamenti impostazioni
        if 'toggle_attivo' in request.POST:
            profilo.attivo = not profilo.attivo
            profilo.save()
            status = 'attivato' if profilo.attivo else 'disattivato'
            messages.success(request, f'Profilo {status} con successo!')
        
        elif 'aggiorna_password' in request.POST:
            # Logica cambio password
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if request.user.check_password(old_password):
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password aggiornata con successo!')
                else:
                    messages.error(request, 'Le password non coincidono')
            else:
                messages.error(request, 'Password attuale non corretta')
    
    context = {
        'profilo': profilo,
    }
    
    return render(request, 'artigiani/dashboard/impostazioni.html', context)


@login_required
def statistiche_dettagliate(request):
    """Statistiche dettagliate per l'artigiano"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Dati per grafici (simulati)
    labels_mesi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu']
    visualizzazioni_mesi = [45, 67, 89, 123, 145, 167]
    contatti_mesi = [5, 8, 12, 18, 22, 28]
    
    context = {
        'profilo': profilo,
        'labels_mesi': json.dumps(labels_mesi),
        'visualizzazioni_mesi': json.dumps(visualizzazioni_mesi),
        'contatti_mesi': json.dumps(contatti_mesi),
    }
    
    return render(request, 'artigiani/dashboard/statistiche.html', context)


@login_required
def orari_disponibilita(request):
    """Gestione orari di disponibilità settimanali"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Ottieni o crea gli orari per tutti i giorni della settimana
    orari_settimana = []
    for giorno in range(7):  # 0=Lunedì, 6=Domenica
        orario, created = OrarioDisponibilita.objects.get_or_create(
            artigiano=profilo,
            giorno_settimana=giorno,
            defaults={
                'attivo': giorno < 5,  # Lun-Ven attivi di default
                'ora_inizio_mattina': timezone.datetime.strptime('08:00', '%H:%M').time() if giorno < 5 else None,
                'ora_fine_mattina': timezone.datetime.strptime('12:00', '%H:%M').time() if giorno < 5 else None,
                'ora_inizio_pomeriggio': timezone.datetime.strptime('14:00', '%H:%M').time() if giorno < 5 else None,
                'ora_fine_pomeriggio': timezone.datetime.strptime('18:00', '%H:%M').time() if giorno < 5 else None,
                'pausa_pranzo': True,
            }
        )
        orari_settimana.append(orario)
    
    if request.method == 'POST':
        forms_valid = True
        forms = []
        
        for orario in orari_settimana:
            form = OrarioDisponibilitaForm(
                request.POST, 
                instance=orario, 
                prefix=f'giorno_{orario.giorno_settimana}'
            )
            forms.append(form)
            if not form.is_valid():
                forms_valid = False
        
        if forms_valid:
            for form in forms:
                form.save()
            messages.success(request, 'Orari di disponibilità aggiornati con successo!')
            return redirect('artigiani:orari_disponibilita')
        else:
            messages.error(request, 'Errori nella compilazione del modulo.')
    else:
        forms = []
        for orario in orari_settimana:
            form = OrarioDisponibilitaForm(
                instance=orario, 
                prefix=f'giorno_{orario.giorno_settimana}'
            )
            forms.append(form)
    
    # Crea lista combinata di orari e form
    orari_con_forms = list(zip(orari_settimana, forms))
    
    # Eccezioni orario attive
    eccezioni_attive = profilo.eccezioni_orario.filter(
        data_fine__gte=timezone.now().date()
    ).order_by('data_inizio')
    
    context = {
        'profilo': profilo,
        'orari_con_forms': orari_con_forms,
        'eccezioni_attive': eccezioni_attive,
    }
    
    return render(request, 'artigiani/dashboard/orari.html', context)


@login_required
def appuntamenti_lista(request):
    """Lista degli appuntamenti"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Filtri
    stato_filter = request.GET.get('stato', '')
    data_filter = request.GET.get('data', '')
    
    appuntamenti = profilo.appuntamenti.all()
    
    if stato_filter:
        appuntamenti = appuntamenti.filter(stato=stato_filter)
    
    if data_filter == 'oggi':
        appuntamenti = appuntamenti.filter(data_appuntamento=timezone.now().date())
    elif data_filter == 'settimana':
        inizio_settimana = timezone.now().date() - timedelta(days=timezone.now().weekday())
        fine_settimana = inizio_settimana + timedelta(days=6)
        appuntamenti = appuntamenti.filter(
            data_appuntamento__range=[inizio_settimana, fine_settimana]
        )
    elif data_filter == 'futuro':
        appuntamenti = appuntamenti.filter(data_appuntamento__gte=timezone.now().date())
    
    appuntamenti = appuntamenti.order_by('data_appuntamento', 'ora_inizio')
    
    # Paginazione
    paginator = Paginator(appuntamenti, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiche veloci
    stats = {
        'totali': profilo.appuntamenti.count(),
        'confermati': profilo.appuntamenti.filter(stato='confermato').count(),
        'oggi': profilo.appuntamenti.filter(data_appuntamento=timezone.now().date()).count(),
        'settimana': profilo.appuntamenti.filter(
            data_appuntamento__range=[
                timezone.now().date() - timedelta(days=timezone.now().weekday()),
                timezone.now().date() - timedelta(days=timezone.now().weekday()) + timedelta(days=6)
            ]
        ).count(),
    }
    
    context = {
        'profilo': profilo,
        'page_obj': page_obj,
        'stats': stats,
        'stato_filter': stato_filter,
        'data_filter': data_filter,
        'stati_choices': Appuntamento.STATO_CHOICES,
    }
    
    return render(request, 'artigiani/dashboard/appuntamenti.html', context)


@login_required
def appuntamento_nuovo(request):
    """Crea nuovo appuntamento"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = AppuntamentoForm(request.POST, artigiano=profilo)
        if form.is_valid():
            appuntamento = form.save(commit=False)
            appuntamento.artigiano = profilo
            appuntamento.save()
            messages.success(request, 'Appuntamento creato con successo!')
            return redirect('artigiani:appuntamenti')
        else:
            messages.error(request, 'Errori nella compilazione del modulo.')
    else:
        form = AppuntamentoForm(artigiano=profilo)
    
    context = {
        'profilo': profilo,
        'form': form,
        'title': 'Nuovo Appuntamento',
    }
    
    return render(request, 'artigiani/dashboard/appuntamento_form.html', context)


@login_required
def appuntamento_edit(request, appuntamento_id):
    """Modifica appuntamento esistente"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    appuntamento = get_object_or_404(
        Appuntamento, 
        id=appuntamento_id, 
        artigiano=profilo
    )
    
    if request.method == 'POST':
        form = AppuntamentoForm(
            request.POST, 
            instance=appuntamento, 
            artigiano=profilo
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Appuntamento modificato con successo!')
            return redirect('artigiani:appuntamenti')
        else:
            messages.error(request, 'Errori nella compilazione del modulo.')
    else:
        form = AppuntamentoForm(instance=appuntamento, artigiano=profilo)
    
    context = {
        'profilo': profilo,
        'form': form,
        'appuntamento': appuntamento,
        'title': 'Modifica Appuntamento',
    }
    
    return render(request, 'artigiani/dashboard/appuntamento_form.html', context)


@login_required
@require_http_methods(["POST"])
def appuntamento_cambia_stato(request, appuntamento_id):
    """Cambia stato di un appuntamento (AJAX)"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        appuntamento = get_object_or_404(
            Appuntamento, 
            id=appuntamento_id, 
            artigiano=profilo
        )
        
        data = json.loads(request.body)
        nuovo_stato = data.get('stato')
        
        if nuovo_stato in dict(Appuntamento.STATO_CHOICES):
            appuntamento.stato = nuovo_stato
            appuntamento.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Stato appuntamento cambiato in "{appuntamento.get_stato_display()}"',
                'nuovo_stato': nuovo_stato,
                'nuovo_stato_display': appuntamento.get_stato_display(),
                'classe_stato': appuntamento.get_stato_display_class()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Stato non valido'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Errore: {str(e)}'
        })


@login_required
def eccezioni_orario(request):
    """Gestione eccezioni agli orari (ferie, chiusure, ecc.)"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = EccezioneOrarioForm(request.POST)
        if form.is_valid():
            eccezione = form.save(commit=False)
            eccezione.artigiano = profilo
            eccezione.save()
            messages.success(request, 'Eccezione orario aggiunta con successo!')
            return redirect('artigiani:eccezioni_orario')
        else:
            messages.error(request, 'Errori nella compilazione del modulo.')
    else:
        form = EccezioneOrarioForm()
    
    # Lista eccezioni esistenti
    eccezioni = profilo.eccezioni_orario.order_by('data_inizio')
    
    # Separa eccezioni passate e future
    oggi = timezone.now().date()
    eccezioni_future = eccezioni.filter(data_fine__gte=oggi)
    eccezioni_passate = eccezioni.filter(data_fine__lt=oggi)
    
    context = {
        'profilo': profilo,
        'form': form,
        'eccezioni_future': eccezioni_future,
        'eccezioni_passate': eccezioni_passate,
    }
    
    return render(request, 'artigiani/dashboard/eccezioni_orario.html', context)


@login_required
@require_http_methods(["POST"])
def eccezione_elimina(request, eccezione_id):
    """Elimina eccezione orario (AJAX)"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        eccezione = get_object_or_404(
            EccezioneOrario, 
            id=eccezione_id, 
            artigiano=profilo
        )
        
        eccezione.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Eccezione orario eliminata con successo'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Errore: {str(e)}'
        })


@login_required
def calendario_appuntamenti(request):
    """Vista calendario degli appuntamenti"""
    
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Ottieni mese corrente o quello richiesto
    anno = int(request.GET.get('anno', timezone.now().year))
    mese = int(request.GET.get('mese', timezone.now().month))
    
    # Appuntamenti del mese
    from calendar import monthrange
    primo_giorno = timezone.datetime(anno, mese, 1).date()
    ultimo_giorno = timezone.datetime(anno, mese, monthrange(anno, mese)[1]).date()
    
    appuntamenti_mese = profilo.appuntamenti.filter(
        data_appuntamento__range=[primo_giorno, ultimo_giorno]
    ).order_by('data_appuntamento', 'ora_inizio')
    
    # Organizza appuntamenti per giorno
    appuntamenti_per_giorno = {}
    for app in appuntamenti_mese:
        giorno = app.data_appuntamento.day
        if giorno not in appuntamenti_per_giorno:
            appuntamenti_per_giorno[giorno] = []
        appuntamenti_per_giorno[giorno].append(app)
    
    # Eccezioni del mese
    eccezioni_mese = profilo.eccezioni_orario.filter(
        Q(data_inizio__lte=ultimo_giorno) & Q(data_fine__gte=primo_giorno)
    )
    
    context = {
        'profilo': profilo,
        'anno': anno,
        'mese': mese,
        'appuntamenti_per_giorno': appuntamenti_per_giorno,
        'eccezioni_mese': eccezioni_mese,
        'mese_precedente': (anno, mese - 1) if mese > 1 else (anno - 1, 12),
        'mese_successivo': (anno, mese + 1) if mese < 12 else (anno + 1, 1),
    }
    
    return render(request, 'artigiani/dashboard/calendario.html', context)


# ===================== DOCUMENT MANAGEMENT =====================

@login_required
def documenti_gestione(request):
    """Gestione documenti per certificazione"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    documenti = profilo.documenti.all().order_by('-data_caricamento')
    
    context = {
        'profilo': profilo,
        'documenti': documenti,
        'documenti_richiesti': [
            'documento_identita',
            'partita_iva',
            'certificato_competenza',
            'assicurazione'
        ]
    }
    
    return render(request, 'artigiani/dashboard/documenti.html', context)


@login_required
def upload_documento(request):
    """Upload nuovo documento"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = DocumentoArtigianoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.artigiano = profilo
            documento.save()
            
            messages.success(request, 'Documento caricato con successo!')
            return redirect('artigiani:documenti')
        else:
            messages.error(request, 'Errore nel caricamento del documento.')
    else:
        form = DocumentoArtigianoForm()
    
    context = {
        'profilo': profilo,
        'form': form
    }
    
    return render(request, 'artigiani/dashboard/upload_documento.html', context)


@login_required
def elimina_documento(request, documento_id):
    """Elimina documento"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        documento = get_object_or_404(DocumentoArtigiano, id=documento_id, artigiano=profilo)
        
        documento.delete()
        messages.success(request, 'Documento eliminato con successo!')
        
    except ProfiloArtigiano.DoesNotExist:
        messages.error(request, 'Profilo non trovato.')
    
    return redirect('artigiani:documenti')


# ===================== VIDEO MANAGEMENT =====================

@login_required
def video_gestione(request):
    """Gestione video dell'artigiano"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    video = profilo.video.all().order_by('-data_caricamento')
    
    context = {
        'profilo': profilo,
        'video': video
    }
    
    return render(request, 'artigiani/dashboard/video.html', context)


@login_required
def upload_video(request):
    """Upload nuovo video"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = VideoArtigianoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.artigiano = profilo
            video.save()
            
            messages.success(request, 'Video caricato con successo!')
            return redirect('artigiani:video')
        else:
            messages.error(request, 'Errore nel caricamento del video.')
    else:
        form = VideoArtigianoForm()
    
    context = {
        'profilo': profilo,
        'form': form
    }
    
    return render(request, 'artigiani/dashboard/upload_video.html', context)


@login_required
def elimina_video(request, video_id):
    """Elimina video"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        video = get_object_or_404(VideoArtigiano, id=video_id, artigiano=profilo)
        
        video.delete()
        messages.success(request, 'Video eliminato con successo!')
        
    except ProfiloArtigiano.DoesNotExist:
        messages.error(request, 'Profilo non trovato.')
    
    return redirect('artigiani:video')


# ===================== CLIENT MESSAGES =====================

@login_required
def messaggi_clienti(request):
    """Gestione messaggi dai clienti"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    stato_filtro = request.GET.get('stato', 'tutti')
    
    messaggi = profilo.messaggi_ricevuti.all()
    
    if stato_filtro != 'tutti':
        messaggi = messaggi.filter(stato=stato_filtro)
    
    messaggi = messaggi.order_by('-data_invio')
    
    # Paginazione
    paginator = Paginator(messaggi, 20)
    page_number = request.GET.get('page')
    messaggi_page = paginator.get_page(page_number)
    
    # Statistiche
    stats = {
        'totali': profilo.messaggi_ricevuti.count(),
        'nuovi': profilo.messaggi_ricevuti.filter(stato='nuovo').count(),
        'letti': profilo.messaggi_ricevuti.filter(stato='letto').count(),
        'risposti': profilo.messaggi_ricevuti.filter(stato='risposto').count(),
    }
    
    context = {
        'profilo': profilo,
        'messaggi': messaggi_page,
        'stato_filtro': stato_filtro,
        'stats': stats
    }
    
    return render(request, 'artigiani/dashboard/messaggi.html', context)


@login_required
def dettaglio_messaggio(request, messaggio_id):
    """Dettaglio e risposta messaggio"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        messaggio = get_object_or_404(MessaggioCliente, id=messaggio_id, artigiano=profilo)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Segna come letto se è nuovo
    if messaggio.stato == 'nuovo':
        messaggio.stato = 'letto'
        messaggio.save()
    
    if request.method == 'POST':
        form = RispostaMessaggioForm(request.POST)
        if form.is_valid():
            messaggio.risposta = form.cleaned_data['risposta']
            messaggio.data_risposta = timezone.now()
            messaggio.stato = 'risposto'
            messaggio.save()
            
            # TODO: Invia email al cliente con la risposta
            
            messages.success(request, 'Risposta inviata con successo!')
            return redirect('artigiani:messaggi')
    else:
        form = RispostaMessaggioForm()
    
    context = {
        'profilo': profilo,
        'messaggio': messaggio,
        'form': form
    }
    
    return render(request, 'artigiani/dashboard/dettaglio_messaggio.html', context)


@login_required
def archivia_messaggio(request, messaggio_id):
    """Archivia messaggio"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        messaggio = get_object_or_404(MessaggioCliente, id=messaggio_id, artigiano=profilo)
        
        messaggio.stato = 'archiviato'
        messaggio.save()
        
        messages.success(request, 'Messaggio archiviato.')
        
    except ProfiloArtigiano.DoesNotExist:
        messages.error(request, 'Profilo non trovato.')
    
    return redirect('artigiani:messaggi')


# ===================== AI SUGGESTIONS =====================

@login_required
def suggerimenti_ia(request):
    """Gestione suggerimenti IA"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    # Genera suggerimenti automatici se non esistono già
    genera_suggerimenti_automatici(profilo)
    
    suggerimenti = profilo.suggerimenti_ia.filter(applicato=False).order_by('-priorita', '-data_creazione')
    
    # Raggruppa per priorità
    suggerimenti_per_priorita = {
        'critica': suggerimenti.filter(priorita='critica'),
        'alta': suggerimenti.filter(priorita='alta'),
        'media': suggerimenti.filter(priorita='media'),
        'bassa': suggerimenti.filter(priorita='bassa'),
    }
    
    context = {
        'profilo': profilo,
        'suggerimenti': suggerimenti,
        'suggerimenti_per_priorita': suggerimenti_per_priorita
    }
    
    return render(request, 'artigiani/dashboard/suggerimenti_ia.html', context)


@login_required
def applica_suggerimento(request, suggerimento_id):
    """Segna suggerimento come applicato"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
        suggerimento = get_object_or_404(SuggerimentoIA, id=suggerimento_id, artigiano=profilo)
        
        suggerimento.applicato = True
        suggerimento.data_applicazione = timezone.now()
        suggerimento.save()
        
        messages.success(request, 'Suggerimento marcato come applicato!')
        
    except ProfiloArtigiano.DoesNotExist:
        messages.error(request, 'Profilo non trovato.')
    
    return redirect('artigiani:suggerimenti')


# ===================== CERTIFICATION MANAGEMENT =====================

@login_required
def certificazioni_gestione(request):
    """Gestione certificazioni"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    certificazioni = profilo.certificazioni.all().order_by('-data_ottenimento')
    
    # Calcola punteggio certificazione
    punteggio_totale = sum(cert.punteggio for cert in certificazioni if cert.attiva)
    
    context = {
        'profilo': profilo,
        'certificazioni': certificazioni,
        'punteggio_totale': punteggio_totale
    }
    
    return render(request, 'artigiani/dashboard/certificazioni.html', context)


# ===================== HELPER FUNCTIONS =====================

def genera_suggerimenti_automatici(profilo):
    """Genera suggerimenti automatici basati sullo stato del profilo"""
    from .models import SuggerimentoIA
    
    suggerimenti_da_creare = []
    
    # Controlla completezza profilo
    if not profilo.descrizione or len(profilo.descrizione) < 100:
        if not profilo.suggerimenti_ia.filter(tipo_suggerimento='descrizione_migliorabile', applicato=False).exists():
            suggerimenti_da_creare.append(SuggerimentoIA(
                artigiano=profilo,
                tipo_suggerimento='descrizione_migliorabile',
                titolo='Migliora la descrizione del tuo profilo',
                descrizione='Una descrizione dettagliata aumenta la fiducia dei clienti del 60%.',
                azione_consigliata='Scrivi almeno 100 parole che descrivono i tuoi servizi, la tua esperienza e cosa ti distingue.',
                priorita='alta'
            ))
    
    # Controlla foto
    if profilo.foto_lavori.count() < 3:
        if not profilo.suggerimenti_ia.filter(tipo_suggerimento='foto_mancanti', applicato=False).exists():
            suggerimenti_da_creare.append(SuggerimentoIA(
                artigiano=profilo,
                tipo_suggerimento='foto_mancanti',
                titolo='Aggiungi più foto dei tuoi lavori',
                descrizione='Gli artigiani con almeno 5 foto ricevono il 40% di contatti in più.',
                azione_consigliata='Carica foto di alta qualità dei tuoi lavori migliori.',
                priorita='alta'
            ))
    
    # Controlla documenti
    if profilo.documenti.filter(stato_verifica='verificato').count() < 2:
        if not profilo.suggerimenti_ia.filter(tipo_suggerimento='documenti_scaduti', applicato=False).exists():
            suggerimenti_da_creare.append(SuggerimentoIA(
                artigiano=profilo,
                tipo_suggerimento='certificazione_mancante',
                titolo='Completa la verifica dei documenti',
                descrizione='I profili verificati ricevono 3 volte più contatti.',
                azione_consigliata='Carica i tuoi documenti di identità e certificazioni professionali.',
                priorita='critica'
            ))
    
    # Controlla video di presentazione
    if not profilo.video.filter(tipo_video='presentazione').exists():
        if not profilo.suggerimenti_ia.filter(tipo_suggerimento='video_consigliato', applicato=False).exists():
            suggerimenti_da_creare.append(SuggerimentoIA(
                artigiano=profilo,
                tipo_suggerimento='video_consigliato',
                titolo='Crea un video di presentazione',
                descrizione='I video di presentazione aumentano la conversione del 80%.',
                azione_consigliata='Registra un breve video (1-2 minuti) dove ti presenti e mostri il tuo lavoro.',
                priorita='media'
            ))
    
    # Crea tutti i suggerimenti in batch
    if suggerimenti_da_creare:
        SuggerimentoIA.objects.bulk_create(suggerimenti_da_creare)


@login_required
def completa_profilo_artigiano(request):
    """Completa il profilo artigiano dopo la registrazione"""
    try:
        profilo = ProfiloArtigiano.objects.get(utente=request.user)
    except ProfiloArtigiano.DoesNotExist:
        return redirect('artigiani:crea_profilo')
    
    if request.method == 'POST':
        form = ProfiloArtigianoCompletoForm(request.POST, request.FILES, instance=profilo)
        if form.is_valid():
            profilo = form.save()
            
            # Genera suggerimenti iniziali
            genera_suggerimenti_automatici(profilo)
            
            messages.success(
                request, 
                'Profilo completato con successo! Ora puoi iniziare a ricevere richieste dai clienti.'
            )
            return redirect('artigiani:dashboard_home')
        else:
            messages.error(request, 'Correggi gli errori nel modulo.')
    else:
        form = ProfiloArtigianoCompletoForm(instance=profilo)
    
    context = {
        'form': form,
        'profilo': profilo,
        'step': 'completa_profilo'
    }
    
    return render(request, 'artigiani/dashboard/completa_profilo.html', context)
