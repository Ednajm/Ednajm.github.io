import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from .models import PacchettoRistrutturazione, Ordine, PagamentoRata, MetodoPagamento
from .forms import OrdineForm

# Configura Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')


@login_required
def checkout_view(request, pacchetto_id):
    """Vista per il checkout di un pacchetto"""
    pacchetto = get_object_or_404(PacchettoRistrutturazione, id=pacchetto_id, attivo=True)
    
    if request.method == 'POST':
        form = OrdineForm(request.POST)
        if form.is_valid():
            # Crea ordine
            ordine = form.save(commit=False)
            ordine.cliente = request.user
            ordine.pacchetto = pacchetto
            ordine.prezzo_base = pacchetto.prezzo_max  # Usiamo il prezzo massimo
            ordine.totale = pacchetto.prezzo_max  # Verrà calcolato dinamicamente
            ordine.save()
            
            # Redirect al pagamento
            return redirect('core:payment', ordine_id=ordine.id)
    else:
        form = OrdineForm()
    
    # Calcoli per il pagamento (usiamo il prezzo massimo)
    prezzo_totale = pacchetto.prezzo_max
    acconto_30 = prezzo_totale * Decimal('0.30')
    saldo_rimanente = prezzo_totale * Decimal('0.70')
    
    context = {
        'pacchetto': pacchetto,
        'form': form,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_...'),
        'prezzo_totale': prezzo_totale,
        'acconto_30': acconto_30,
        'saldo_rimanente': saldo_rimanente,
    }
    
    return render(request, 'core/checkout.html', context)


@login_required
def payment_view(request, ordine_id):
    """Vista per il pagamento di un ordine"""
    ordine = get_object_or_404(Ordine, id=ordine_id, cliente=request.user)
    
    if ordine.payment_status == 'succeeded':
        return redirect('core:payment_success', ordine_id=ordine.id)
    
    # Crea Payment Intent con Stripe
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(ordine.importo_acconto * 100),  # Stripe usa centesimi
            currency='eur',
            metadata={
                'ordine_id': ordine.id,
                'tipo_pagamento': 'acconto'
            }
        )
        ordine.stripe_payment_intent_id = intent.id
        ordine.save()
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Errore nel processamento del pagamento: {str(e)}')
        return redirect('core:checkout', pacchetto_id=ordine.pacchetto.id)
    
    context = {
        'ordine': ordine,
        'client_secret': intent.client_secret,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_...'),
    }
    
    return render(request, 'core/payment.html', context)


@login_required
def payment_success_view(request, ordine_id):
    """Vista per conferma pagamento riuscito"""
    ordine = get_object_or_404(Ordine, id=ordine_id, cliente=request.user)
    
    context = {
        'ordine': ordine,
    }
    
    return render(request, 'core/payment_success.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Webhook per gestire gli eventi di Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Gestisci l'evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)
    
    return HttpResponse(status=200)


def handle_payment_success(payment_intent):
    """Gestisce un pagamento riuscito"""
    try:
        ordine_id = payment_intent['metadata'].get('ordine_id')
        if ordine_id:
            ordine = Ordine.objects.get(id=ordine_id)
            ordine.payment_status = 'succeeded'
            ordine.status = 'pagato'
            ordine.save()
            
            # Crea le rate successive se necessario
            crea_rate_pagamento(ordine)
            
    except Ordine.DoesNotExist:
        pass


def handle_payment_failure(payment_intent):
    """Gestisce un pagamento fallito"""
    try:
        ordine_id = payment_intent['metadata'].get('ordine_id')
        if ordine_id:
            ordine = Ordine.objects.get(id=ordine_id)
            ordine.payment_status = 'failed'
            ordine.save()
            
    except Ordine.DoesNotExist:
        pass


def crea_rate_pagamento(ordine):
    """Crea le rate di pagamento per un ordine"""
    from datetime import datetime, timedelta
    
    # Acconto già pagato, crea solo il saldo
    saldo = ordine.importo_saldo
    data_scadenza = datetime.now().date() + timedelta(days=30)  # Saldo dopo 30 giorni
    
    PagamentoRata.objects.get_or_create(
        ordine=ordine,
        numero_rata=2,
        defaults={
            'importo': saldo,
            'data_scadenza': data_scadenza,
            'descrizione': 'Saldo finale'
        }
    )


@login_required
def metodi_pagamento_view(request):
    """Vista per gestire i metodi di pagamento del cliente"""
    metodi = MetodoPagamento.objects.filter(cliente=request.user, attivo=True)
    
    context = {
        'metodi': metodi,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_...'),
    }
    
    return render(request, 'core/metodi_pagamento.html', context)


@login_required
@require_POST
def aggiungi_metodo_pagamento(request):
    """Aggiunge un nuovo metodo di pagamento"""
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        if payment_method_id:
            # Recupera dettagli da Stripe
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Salva nel database
            metodo = MetodoPagamento.objects.create(
                cliente=request.user,
                tipo='card',
                stripe_payment_method_id=payment_method_id,
                brand=payment_method.card.brand,
                last4=payment_method.card.last4,
                exp_month=payment_method.card.exp_month,
                exp_year=payment_method.card.exp_year,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Metodo di pagamento aggiunto con successo'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Errore: {str(e)}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Dati non validi'
    })


@login_required
def ordini_view(request):
    """Vista per visualizzare gli ordini del cliente"""
    ordini = Ordine.objects.filter(cliente=request.user)
    
    context = {
        'ordini': ordini,
    }
    
    return render(request, 'core/ordini.html', context)


@login_required
def dettaglio_ordine_view(request, ordine_id):
    """Vista per il dettaglio di un ordine"""
    ordine = get_object_or_404(Ordine, id=ordine_id, cliente=request.user)
    rate = PagamentoRata.objects.filter(ordine=ordine)
    
    context = {
        'ordine': ordine,
        'rate': rate,
    }
    
    return render(request, 'core/dettaglio_ordine.html', context)
