from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    CategoriaIntervento, PacchettoRistrutturazione, DiagnosiImmobile,
    ConsulenzaVideo, Newsletter
)
from .forms import DiagnosiForm, ConsulenzaVideoForm, NewsletterForm


def home_view(request):
    """Vista per la homepage"""
    
    # Pacchetti in evidenza
    pacchetti_evidenza = PacchettoRistrutturazione.objects.filter(
        attivo=True, 
        in_evidenza=True
    ).order_by('ordinamento')[:6]
    
    # Categorie principali
    categorie = CategoriaIntervento.objects.filter(attiva=True).order_by('ordine')[:8]
    
    # Form newsletter per il footer
    newsletter_form = NewsletterForm()
    
    context = {
        'pacchetti_evidenza': pacchetti_evidenza,
        'categorie': categorie,
        'newsletter_form': newsletter_form,
    }
    
    return render(request, 'core/home.html', context)


def pacchetti_view(request):
    """Vista per visualizzare tutti i pacchetti"""
    
    pacchetti = PacchettoRistrutturazione.objects.filter(attivo=True)
    
    # Filtri
    categoria_id = request.GET.get('categoria')
    prezzo_max = request.GET.get('prezzo_max')
    difficolta = request.GET.get('difficolta')
    search = request.GET.get('search')
    
    if categoria_id:
        pacchetti = pacchetti.filter(categoria_id=categoria_id)
    
    if prezzo_max:
        try:
            prezzo_max = float(prezzo_max)
            pacchetti = pacchetti.filter(prezzo_max__lte=prezzo_max)
        except ValueError:
            pass
    
    if difficolta:
        pacchetti = pacchetti.filter(difficolta=difficolta)
    
    if search:
        pacchetti = pacchetti.filter(
            Q(nome__icontains=search) |
            Q(descrizione_breve__icontains=search) |
            Q(descrizione_completa__icontains=search)
        )
    
    # Ordinamento
    ordinamento = request.GET.get('ordine', 'ordinamento')
    if ordinamento == 'prezzo_asc':
        pacchetti = pacchetti.order_by('prezzo_min')
    elif ordinamento == 'prezzo_desc':
        pacchetti = pacchetti.order_by('-prezzo_max')
    elif ordinamento == 'nome':
        pacchetti = pacchetti.order_by('nome')
    else:
        pacchetti = pacchetti.order_by('ordinamento', 'nome')
    
    # Paginazione
    paginator = Paginator(pacchetti, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dati per i filtri
    categorie = CategoriaIntervento.objects.filter(attiva=True).order_by('ordine')
    
    context = {
        'page_obj': page_obj,
        'categorie': categorie,
        'filtro_categoria': categoria_id,
        'filtro_prezzo': prezzo_max,
        'filtro_difficolta': difficolta,
        'filtro_search': search,
        'ordinamento_selezionato': ordinamento,
    }
    
    return render(request, 'core/pacchetti.html', context)


def dettaglio_pacchetto_view(request, pacchetto_id):
    """Vista per i dettagli di un singolo pacchetto"""
    
    pacchetto = get_object_or_404(
        PacchettoRistrutturazione, 
        id=pacchetto_id, 
        attivo=True
    )
    
    # Pacchetti correlati della stessa categoria
    pacchetti_correlati = PacchettoRistrutturazione.objects.filter(
        categoria=pacchetto.categoria,
        attivo=True
    ).exclude(id=pacchetto.id)[:4]
    
    context = {
        'pacchetto': pacchetto,
        'pacchetti_correlati': pacchetti_correlati,
    }
    
    return render(request, 'core/dettaglio_pacchetto.html', context)


@login_required
def dashboard_view(request):
    """Dashboard principale per i clienti"""
    
    user = request.user
    
    # Statistiche utente
    diagnosi_count = DiagnosiImmobile.objects.filter(utente=user).count()
    consulenze_count = ConsulenzaVideo.objects.filter(utente=user).count()
    
    # Ultime diagnosi
    ultime_diagnosi = DiagnosiImmobile.objects.filter(
        utente=user
    ).order_by('-data_creazione')[:5]
    
    # Prossime consulenze
    prossime_consulenze = ConsulenzaVideo.objects.filter(
        utente=user,
        stato__in=['richiesta', 'confermata']
    ).order_by('data_preferita')[:5]
    
    # Pacchetti consigliati (basati su diagnosi precedenti)
    pacchetti_consigliati = []
    if ultime_diagnosi:
        ultima_diagnosi = ultime_diagnosi[0]
        pacchetti_consigliati = ultima_diagnosi.pacchetti_consigliati.all()[:4]
    
    if not pacchetti_consigliati:
        # Fallback ai pacchetti in evidenza
        pacchetti_consigliati = PacchettoRistrutturazione.objects.filter(
            attivo=True,
            in_evidenza=True
        )[:4]
    
    context = {
        'diagnosi_count': diagnosi_count,
        'consulenze_count': consulenze_count,
        'ultime_diagnosi': ultime_diagnosi,
        'prossime_consulenze': prossime_consulenze,
        'pacchetti_consigliati': pacchetti_consigliati,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def dashboard_impresa_view(request):
    """Dashboard per le imprese"""
    
    if request.user.user_type != 'impresa':
        messages.error(request, 'Accesso non autorizzato.')
        return redirect('core:dashboard')
    
    # TODO: Implementare statistiche specifiche per le imprese
    # - Progetti assegnati
    # - Valutazioni ricevute
    # - Guadagni
    # - Richieste in sospeso
    
    context = {
        'is_impresa': True,
    }
    
    return render(request, 'core/dashboard_impresa.html', context)


@login_required
def diagnosi_view(request):
    """Vista per creare una nuova diagnosi"""
    
    if request.method == 'POST':
        form = DiagnosiForm(request.POST, request.FILES)
        if form.is_valid():
            diagnosi = form.save(commit=False)
            diagnosi.utente = request.user
            diagnosi.save()
            
            messages.success(
                request,
                'Diagnosi caricata con successo! Riceverai i risultati entro 24 ore.'
            )
            
            return redirect('core:dashboard')
    else:
        form = DiagnosiForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'core/diagnosi.html', context)


@login_required
def lista_diagnosi_view(request):
    """Vista per visualizzare tutte le diagnosi dell'utente"""
    
    diagnosi = DiagnosiImmobile.objects.filter(
        utente=request.user
    ).order_by('-data_creazione')
    
    paginator = Paginator(diagnosi, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'core/lista_diagnosi.html', context)


@login_required
def dettaglio_diagnosi_view(request, diagnosi_id):
    """Vista per i dettagli di una diagnosi"""
    
    diagnosi = get_object_or_404(
        DiagnosiImmobile,
        id=diagnosi_id,
        utente=request.user
    )
    
    context = {
        'diagnosi': diagnosi,
    }
    
    return render(request, 'core/dettaglio_diagnosi.html', context)


@login_required
def consulenza_video_view(request):
    """Vista per prenotare una consulenza video"""
    
    if request.method == 'POST':
        form = ConsulenzaVideoForm(request.POST)
        if form.is_valid():
            consulenza = form.save(commit=False)
            consulenza.utente = request.user
            consulenza.save()
            
            messages.success(
                request,
                'Richiesta di consulenza inviata! Ti contatteremo entro 24 ore per confermare l\'appuntamento.'
            )
            
            return redirect('core:dashboard')
    else:
        form = ConsulenzaVideoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'core/consulenza_video.html', context)


@login_required
def lista_consulenze_view(request):
    """Vista per visualizzare tutte le consulenze dell'utente"""
    
    consulenze = ConsulenzaVideo.objects.filter(
        utente=request.user
    ).order_by('-data_richiesta')
    
    paginator = Paginator(consulenze, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'core/lista_consulenze.html', context)


@require_POST
def newsletter_signup_view(request):
    """Vista AJAX per l'iscrizione alla newsletter"""
    
    form = NewsletterForm(request.POST)
    
    if form.is_valid():
        try:
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Iscrizione alla newsletter completata con successo!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Questa email è già iscritta alla newsletter.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Errore nell\'iscrizione. Controlla l\'email inserita.'
    })


def come_funziona_view(request):
    """Vista per la pagina Come Funziona"""
    return render(request, 'core/come_funziona.html')


def bonus_fiscali_view(request):
    """Vista per la pagina Bonus Fiscali"""
    return render(request, 'core/bonus_fiscali.html')


def imprese_view(request):
    """Vista per la pagina Imprese"""
    return render(request, 'core/imprese.html')


def contatti_view(request):
    """Vista per la pagina Contatti"""
    newsletter_form = NewsletterForm()
    
    context = {
        'newsletter_form': newsletter_form,
    }
    
    return render(request, 'core/contatti.html', context)
