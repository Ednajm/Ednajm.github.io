from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import (
    CategoriaArtigiano, ProfiloArtigiano, FotoLavoro, 
    RecensioneArtigiano, RichiestaPreventivo, RispostaPreventivo
)


def ricerca_artigiani(request):
    """Vista principale per la ricerca degli artigiani"""
    
    # Filtri di ricerca
    categoria_id = request.GET.get('categoria')
    citta = request.GET.get('citta', '').strip()
    cap = request.GET.get('cap', '').strip()
    fascia_prezzo = request.GET.get('fascia_prezzo')
    esperienza_min = request.GET.get('esperienza_min')
    lingue = request.GET.getlist('lingue')
    ordinamento = request.GET.get('ordinamento', 'rilevanza')
    
    # Query base
    artigiani = ProfiloArtigiano.objects.filter(attivo=True)
    
    # Applica filtri
    if categoria_id:
        artigiani = artigiani.filter(
            Q(categoria_principale_id=categoria_id) | 
            Q(categorie_secondarie__id=categoria_id)
        ).distinct()
    
    if citta:
        artigiani = artigiani.filter(citta__icontains=citta)
    
    if cap:
        artigiani = artigiani.filter(cap__startswith=cap)
    
    if fascia_prezzo:
        artigiani = artigiani.filter(fascia_prezzo=fascia_prezzo)
    
    if esperienza_min:
        try:
            exp_min = int(esperienza_min)
            artigiani = artigiani.filter(anni_esperienza__gte=exp_min)
        except ValueError:
            pass
    
    # Filtro lingue
    if lingue:
        lingua_query = Q()
        for lingua in lingue:
            if lingua == 'italiano':
                lingua_query |= Q(italiano=True)
            elif lingua == 'inglese':
                lingua_query |= Q(inglese=True)
            elif lingua == 'francese':
                lingua_query |= Q(francese=True)
            elif lingua == 'arabo':
                lingua_query |= Q(arabo=True)
        if lingua_query:
            artigiani = artigiani.filter(lingua_query)
    
    # Ordinamento
    if ordinamento == 'prezzo_basso':
        artigiani = artigiani.order_by('prezzo_orario_min')
    elif ordinamento == 'prezzo_alto':
        artigiani = artigiani.order_by('-prezzo_orario_min')
    elif ordinamento == 'recensioni':
        # Ordina per numero di recensioni
        artigiani = artigiani.annotate(
            num_recensioni=Count('recensioni')
        ).order_by('-num_recensioni')
    elif ordinamento == 'esperienza':
        artigiani = artigiani.order_by('-anni_esperienza')
    else:  # rilevanza (default)
        artigiani = artigiani.order_by('-premium', '-verificato', '-numero_lavori_completati')
    
    # Paginazione
    paginator = Paginator(artigiani, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorie per il form di ricerca
    categorie = CategoriaArtigiano.objects.filter(attiva=True)
    
    context = {
        'page_obj': page_obj,
        'categorie': categorie,
        'filtri': {
            'categoria_id': categoria_id,
            'citta': citta,
            'cap': cap,
            'fascia_prezzo': fascia_prezzo,
            'esperienza_min': esperienza_min,
            'lingue': lingue,
            'ordinamento': ordinamento,
        },
        'fasce_prezzo': ProfiloArtigiano.FASCIA_PREZZO_CHOICES,
        'lingue_disponibili': [
            ('italiano', 'Italiano'),
            ('inglese', 'Inglese'),
            ('francese', 'Francese'),
            ('arabo', 'Arabo'),
        ],
        'opzioni_ordinamento': [
            ('rilevanza', 'Rilevanza'),
            ('prezzo_basso', 'Prezzo: dal più basso'),
            ('prezzo_alto', 'Prezzo: dal più alto'),
            ('recensioni', 'Più recensiti'),
            ('esperienza', 'Più esperti'),
        ]
    }
    
    return render(request, 'artigiani/ricerca.html', context)


def dettaglio_artigiano(request, artigiano_id):
    """Vista dettaglio di un singolo artigiano"""
    
    artigiano = get_object_or_404(ProfiloArtigiano, id=artigiano_id, attivo=True)
    
    # Incrementa visualizzazioni
    ProfiloArtigiano.objects.filter(id=artigiano_id).update(
        visualizzazioni_profilo=F('visualizzazioni_profilo') + 1
    )
    
    # Foto lavori in evidenza
    foto_evidenza = artigiano.foto_lavori.filter(in_evidenza=True)[:6]
    
    # Tutte le foto
    tutte_foto = artigiano.foto_lavori.all()
    
    # Recensioni recenti
    recensioni = artigiano.recensioni.filter(verificata=True).order_by('-data_recensione')[:10]
    
    # Calcola statistiche recensioni
    stats_recensioni = {
        'voto_medio': artigiano.voto_medio,
        'totale': artigiano.numero_recensioni,
        'qualita_media': recensioni.aggregate(Avg('qualita_lavoro'))['qualita_lavoro__avg'] or 0,
        'puntualita_media': recensioni.aggregate(Avg('puntualita'))['puntualita__avg'] or 0,
        'cortesia_media': recensioni.aggregate(Avg('cortesia'))['cortesia__avg'] or 0,
        'rapporto_qp_medio': recensioni.aggregate(Avg('rapporto_qualita_prezzo'))['rapporto_qualita_prezzo__avg'] or 0,
    }
    
    # Artigiani simili nella zona
    artigiani_simili = ProfiloArtigiano.objects.filter(
        categoria_principale=artigiano.categoria_principale,
        attivo=True,
        citta=artigiano.citta
    ).exclude(id=artigiano.id)[:3]
    
    context = {
        'artigiano': artigiano,
        'foto_evidenza': foto_evidenza,
        'tutte_foto': tutte_foto,
        'recensioni': recensioni,
        'stats_recensioni': stats_recensioni,
        'artigiani_simili': artigiani_simili,
    }
    
    return render(request, 'artigiani/dettaglio.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def contatta_artigiano(request, artigiano_id):
    """Contatto diretto dell'artigiano (senza registrazione)"""
    
    try:
        data = json.loads(request.body)
        
        artigiano = get_object_or_404(ProfiloArtigiano, id=artigiano_id, attivo=True)
        
        # Incrementa contatti ricevuti
        ProfiloArtigiano.objects.filter(id=artigiano_id).update(
            contatti_ricevuti=F('contatti_ricevuti') + 1
        )
        
        # Per ora simuliamo l'invio (in produzione inviare email/SMS)
        messaggio_successo = f"""
        Messaggio inviato a {artigiano.nome_attivita}!
        
        Riceverai una risposta a: {data.get('email')}
        
        Il tuo messaggio:
        "{data.get('messaggio')}"
        
        Contatti artigiano:
        📞 Tel: {artigiano.telefono}
        {f"📱 WhatsApp: {artigiano.whatsapp}" if artigiano.whatsapp else ""}
        {f"✉️ Email: {artigiano.email_lavoro}" if artigiano.email_lavoro else ""}
        """
        
        return JsonResponse({
            'success': True,
            'message': messaggio_successo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Errore nell\'invio del messaggio: {str(e)}'
        })


def richiedi_preventivo(request):
    """Form per richiedere un preventivo automatico"""
    
    if request.method == 'POST':
        try:
            # Raccoglie i dati del form
            categoria_id = request.POST.get('categoria')
            superficie = request.POST.get('superficie')
            citta = request.POST.get('citta')
            cap = request.POST.get('cap')
            
            # Crea la richiesta
            richiesta = RichiestaPreventivo.objects.create(
                cliente_nome=request.POST.get('nome'),
                cliente_email=request.POST.get('email'),
                cliente_telefono=request.POST.get('telefono'),
                categoria_id=categoria_id,
                titolo=request.POST.get('titolo'),
                descrizione=request.POST.get('descrizione'),
                citta=citta,
                cap=cap,
                indirizzo=request.POST.get('indirizzo', ''),
                superficie_mq=float(superficie) if superficie else None,
                budget_min=float(request.POST.get('budget_min')) if request.POST.get('budget_min') else None,
                budget_max=float(request.POST.get('budget_max')) if request.POST.get('budget_max') else None,
                urgenza=request.POST.get('urgenza', 'media'),
            )
            
            # Salva le foto se presenti
            for i in range(1, 4):
                foto = request.FILES.get(f'foto{i}')
                if foto:
                    setattr(richiesta, f'foto{i}', foto)
            
            richiesta.save()
            
            # Trova artigiani idonei nella zona
            artigiani_idonei = ProfiloArtigiano.objects.filter(
                Q(categoria_principale_id=categoria_id) | 
                Q(categorie_secondarie__id=categoria_id),
                attivo=True,
                citta__iexact=citta
            ).distinct()[:3]
            
            # Simula invio ai 3 artigiani più vicini
            for artigiano in artigiani_idonei:
                # In produzione: invia notifica email/SMS
                pass
            
            messages.success(
                request, 
                f'Richiesta inviata con successo! Contatteremo {len(artigiani_idonei)} artigiani nella tua zona.'
            )
            
            return redirect('artigiani:dettaglio_richiesta', richiesta_id=richiesta.id)
            
        except Exception as e:
            messages.error(request, f'Errore nella creazione della richiesta: {str(e)}')
    
    # GET: mostra il form
    categorie = CategoriaArtigiano.objects.filter(attiva=True)
    
    context = {
        'categorie': categorie,
        'urgenze': RichiestaPreventivo.URGENZA_CHOICES,
    }
    
    return render(request, 'artigiani/richiedi_preventivo.html', context)


def dettaglio_richiesta(request, richiesta_id):
    """Mostra i dettagli di una richiesta di preventivo"""
    
    richiesta = get_object_or_404(RichiestaPreventivo, id=richiesta_id)
    
    # Risposte ricevute
    risposte = richiesta.rispostapreventivo_set.all().order_by('prezzo_offerto')
    
    context = {
        'richiesta': richiesta,
        'risposte': risposte,
    }
    
    return render(request, 'artigiani/dettaglio_richiesta.html', context)


def categorie_artigiani(request):
    """Vista per mostrare tutte le categorie di artigiani"""
    
    categorie = CategoriaArtigiano.objects.filter(attiva=True).annotate(
        numero_artigiani=Count('profiloartigiano')
    )
    
    context = {
        'categorie': categorie,
    }
    
    return render(request, 'artigiani/categorie.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def genera_preventivo_ai(request):
    """Genera un preventivo automatico con AI"""
    
    try:
        data = json.loads(request.body)
        
        categoria = data.get('categoria')
        superficie = float(data.get('superficie', 0))
        zona = data.get('zona')
        
        # Simulazione AI per calcolo preventivo
        # In produzione: integrare con servizio AI vero
        
        prezzi_base = {
            'muratore': {'min': 25, 'max': 45},  # €/mq
            'pittore': {'min': 15, 'max': 35},
            'idraulico': {'min': 30, 'max': 60},
            'elettricista': {'min': 25, 'max': 50},
            'piastrellista': {'min': 20, 'max': 40},
            'pavimentista': {'min': 30, 'max': 70},
        }
        
        prezzo_base = prezzi_base.get(categoria, {'min': 25, 'max': 50})
        
        # Calcolo con fattori zona
        fattore_zona = {
            'milano': 1.3,
            'roma': 1.2,
            'napoli': 1.0,
            'torino': 1.1,
            'bologna': 1.15,
        }.get(zona.lower(), 1.0)
        
        prezzo_min = superficie * prezzo_base['min'] * fattore_zona
        prezzo_max = superficie * prezzo_base['max'] * fattore_zona
        
        # Giorni stimati
        giorni_stimati = max(1, int(superficie / 10))
        
        preventivo = {
            'prezzo_min': round(prezzo_min, 2),
            'prezzo_max': round(prezzo_max, 2),
            'giorni_stimati': giorni_stimati,
            'categoria': categoria,
            'superficie': superficie,
            'zona': zona,
            'dettagli': f"""
            Preventivo automatico per {categoria} - {superficie} mq
            
            🏠 Zona: {zona.title()}
            📏 Superficie: {superficie} mq
            ⏱️ Durata stimata: {giorni_stimati} giorni
            
            💰 Costo stimato: €{prezzo_min:.0f} - €{prezzo_max:.0f}
            
            ⚠️ Questo è un preventivo indicativo generato automaticamente.
            Per un preventivo preciso, contatta direttamente gli artigiani.
            """
        }
        
        return JsonResponse({
            'success': True,
            'preventivo': preventivo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Errore nel calcolo: {str(e)}'
        })


@csrf_exempt  
@require_http_methods(["POST"])
def analizza_foto_ai(request):
    """Analizza una foto caricata e suggerisce il tipo di lavoro"""
    
    try:
        if 'foto' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Nessuna foto caricata'
            })
        
        foto = request.FILES['foto']
        
        # Simulazione analisi AI
        # In produzione: integrare con servizio di computer vision
        
        suggerimenti_sample = [
            {
                'categoria': 'pittore',
                'confidenza': 85,
                'descrizione': 'Rilevate pareti che necessitano di tinteggiatura',
                'lavori_suggeriti': ['Tinteggiatura pareti', 'Ritocco vernice', 'Imbiancatura completa']
            },
            {
                'categoria': 'piastrellista', 
                'confidenza': 70,
                'descrizione': 'Pavimento danneggiato che richiede intervento',
                'lavori_suggeriti': ['Sostituzione piastrelle', 'Rifugatura', 'Posa nuovo pavimento']
            },
            {
                'categoria': 'idraulico',
                'confidenza': 60,
                'descrizione': 'Possibili problemi idraulici visibili',
                'lavori_suggeriti': ['Riparazione perdite', 'Sostituzione rubinetti', 'Manutenzione impianto']
            }
        ]
        
        # Per la demo, restituisce un suggerimento casuale
        import random
        suggerimento = random.choice(suggerimenti_sample)
        
        # Salva temporaneamente l'analisi per utilizzo futuro
        analisi = {
            'nome_file': foto.name,
            'categoria_suggerita': suggerimento['categoria'],
            'confidenza': suggerimento['confidenza'],
            'descrizione': suggerimento['descrizione'],
            'lavori_suggeriti': suggerimento['lavori_suggeriti']
        }
        
        return JsonResponse({
            'success': True,
            'analisi': analisi
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Errore nell\'analisi: {str(e)}'
        })


def cerca_per_citta(request):
    """API per cercare artigiani per città (autocomplete)"""
    
    term = request.GET.get('term', '').strip()
    
    if len(term) < 2:
        return JsonResponse({'citta': []})
    
    # Cerca città uniche negli artigiani attivi
    citta = ProfiloArtigiano.objects.filter(
        attivo=True,
        citta__icontains=term
    ).values_list('citta', flat=True).distinct()[:10]
    
    return JsonResponse({
        'citta': list(citta)
    })


def statistiche_dashboard(request):
    """Dashboard con statistiche del sistema (per admin)"""
    
    if not request.user.is_staff:
        messages.error(request, 'Accesso non autorizzato')
        return redirect('core:home')
    
    stats = {
        'totale_artigiani': ProfiloArtigiano.objects.filter(attivo=True).count(),
        'artigiani_verificati': ProfiloArtigiano.objects.filter(attivo=True, verificato=True).count(),
        'totale_richieste': RichiestaPreventivo.objects.count(),
        'richieste_oggi': RichiestaPreventivo.objects.filter(
            data_creazione__date=timezone.now().date()
        ).count(),
        'categorie_attive': CategoriaArtigiano.objects.filter(attiva=True).count(),
        'recensioni_totali': RecensioneArtigiano.objects.filter(verificata=True).count(),
    }
    
    # Artigiani per categoria
    categorie_stats = CategoriaArtigiano.objects.filter(attiva=True).annotate(
        numero_artigiani=Count('profiloartigiano', filter=Q(profiloartigiano__attivo=True))
    ).order_by('-numero_artigiani')
    
    # Città più attive
    citta_stats = ProfiloArtigiano.objects.filter(attivo=True).values('citta').annotate(
        numero_artigiani=Count('id')
    ).order_by('-numero_artigiani')[:10]
    
    context = {
        'stats': stats,
        'categorie_stats': categorie_stats,
        'citta_stats': citta_stats,
    }
    
    return render(request, 'artigiani/dashboard_stats.html', context)
