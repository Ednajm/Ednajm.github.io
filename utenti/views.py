from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils import timezone
from django.http import JsonResponse
from django.core.signing import Signer, BadSignature
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from datetime import datetime, timedelta
from .models import CustomUser, ProfiloCliente, ProfiloImpresa
from .register import (
    CustomUserCreationForm, CustomLoginForm, ProfiloClienteForm, 
    ProfiloImpresaForm, UserProfileForm
)


class CustomLoginView(LoginView):
    """Vista personalizzata per il login"""
    form_class = CustomLoginForm
    template_name = 'utenti/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Salva l'ultimo accesso dashboard"""
        response = super().form_valid(form)
        user = self.request.user
        user.ultimo_accesso_dashboard = timezone.now()
        user.save(update_fields=['ultimo_accesso_dashboard'])
        
        messages.success(self.request, f'Benvenuto, {user.nome_completo}!')
        return response
    
    def get_success_url(self):
        """Redirect personalizzato in base al tipo di utente"""
        user = self.request.user
        if user.user_type == 'admin':
            return reverse_lazy('admin:index')
        elif user.user_type == 'impresa':
            return reverse_lazy('core:dashboard_impresa')
        elif user.user_type == 'artigiano':
            return reverse_lazy('artigiani:dashboard')
        else:
            return reverse_lazy('core:dashboard')


@csrf_exempt
@require_http_methods(["POST"])
def send_magic_link(request):
    """Invia un magic link per l'accesso istantaneo"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email richiesta'})
        
        # Verifica se l'utente esiste
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Per sicurezza, non rivelare se l'utente esiste o meno
            return JsonResponse({
                'success': True, 
                'message': 'Se l\'email esiste nel nostro sistema, riceverai un link di accesso.'
            })
        
        # Genera token sicuro
        signer = Signer()
        token_data = {
            'user_id': user.id,
            'email': email,
            'timestamp': datetime.now().timestamp(),
            'uuid': str(uuid.uuid4())
        }
        
        token = signer.sign_object(token_data)
        
        # Crea URL del magic link
        magic_url = request.build_absolute_uri(f'/utenti/magic-login/{token}/')
        
        # Invia email
        subject = 'Accesso Istantaneo - RinnovoCasa'
        message = f"""
        Ciao {user.nome_completo},
        
        Hai richiesto l'accesso istantaneo al tuo account RinnovoCasa.
        
        Clicca sul link qui sotto per accedere immediatamente:
        {magic_url}
        
        Questo link è valido per 15 minuti e può essere utilizzato una sola volta.
        
        Se non hai richiesto questo accesso, puoi ignorare questa email.
        
        Il team RinnovoCasa
        """
        
        # In produzione, usa il sistema email configurato
        # Per ora, simula l'invio
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # Log dell'errore e fallback
            print(f"Errore invio email: {e}")
            # In sviluppo, mostra il link nella console
            print(f"Magic Link: {magic_url}")
        
        return JsonResponse({
            'success': True,
            'message': 'Link di accesso inviato! Controlla la tua email.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Errore del server'})


def magic_login(request, token):
    """Gestisce l'accesso tramite magic link"""
    try:
        signer = Signer()
        token_data = signer.unsign_object(token)
        
        # Verifica timestamp (15 minuti di validità)
        token_time = datetime.fromtimestamp(token_data['timestamp'])
        if datetime.now() - token_time > timedelta(minutes=15):
            messages.error(request, 'Link di accesso scaduto. Richiedi un nuovo link.')
            return redirect('utenti:login')
        
        # Verifica utente
        try:
            user = CustomUser.objects.get(
                id=token_data['user_id'],
                email=token_data['email']
            )
        except CustomUser.DoesNotExist:
            messages.error(request, 'Link di accesso non valido.')
            return redirect('utenti:login')
        
        # Login automatico
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Aggiorna ultimo accesso
        user.ultimo_accesso_dashboard = timezone.now()
        user.save(update_fields=['ultimo_accesso_dashboard'])
        
        messages.success(request, f'✨ Accesso istantaneo completato! Benvenuto, {user.nome_completo}!')
        
        # Redirect in base al tipo di utente
        if user.user_type == 'admin':
            return redirect('admin:index')
        elif user.user_type == 'impresa':
            return redirect('core:dashboard_impresa')
        else:
            return redirect('core:dashboard')
            
    except BadSignature:
        messages.error(request, 'Link di accesso non valido o manomesso.')
        return redirect('utenti:login')
    except Exception as e:
        messages.error(request, 'Errore durante l\'accesso. Riprova.')
        return redirect('utenti:login')


@csrf_exempt
@require_http_methods(["POST"])
def check_user_exists(request):
    """Verifica se un utente esiste nel sistema"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'exists': False})
        
        exists = CustomUser.objects.filter(email=email).exists()
        
        return JsonResponse({
            'exists': exists,
            'message': 'Utente riconosciuto' if exists else 'Nuovo utente'
        })
        
    except Exception as e:
        return JsonResponse({'exists': False, 'error': 'Errore del server'})


@csrf_exempt
@require_http_methods(["POST"])
def reset_password_request(request):
    """Richiesta reset password"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email richiesta'})
        
        # Verifica se l'utente esiste
        try:
            user = CustomUser.objects.get(email=email)
            
            # Genera token per reset password
            signer = Signer()
            token_data = {
                'user_id': user.id,
                'email': email,
                'timestamp': datetime.now().timestamp(),
                'action': 'reset_password'
            }
            
            token = signer.sign_object(token_data)
            reset_url = request.build_absolute_uri(f'/utenti/reset-password/{token}/')
            
            # Invia email di reset
            subject = 'Reset Password - RinnovoCasa'
            message = f"""
            Ciao {user.nome_completo},
            
            Hai richiesto il reset della tua password per RinnovoCasa.
            
            Clicca sul link qui sotto per impostare una nuova password:
            {reset_url}
            
            Questo link è valido per 30 minuti.
            
            Se non hai richiesto questo reset, puoi ignorare questa email.
            
            Il team RinnovoCasa
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Errore invio email: {e}")
                print(f"Reset Link: {reset_url}")
            
        except CustomUser.DoesNotExist:
            pass  # Non rivelare se l'utente esiste
        
        return JsonResponse({
            'success': True,
            'message': 'Se l\'email esiste, riceverai un link per il reset della password.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Errore del server'})


class CustomLogoutView(LogoutView):
    """Vista personalizzata per il logout"""
    next_page = reverse_lazy('core:home')
    http_method_names = ['get', 'post', 'options']  # Consente sia GET che POST
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Sei stato disconnesso con successo.')
        return super().dispatch(request, *args, **kwargs)


def register_view(request):
    """Vista per la registrazione di un nuovo utente"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Login automatico dopo la registrazione
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                messages.success(
                    request, 
                    f'Registrazione completata con successo! Benvenuto, {user.nome_completo}!'
                )
                
                # Redirect in base al tipo di utente
                if user.user_type == 'impresa':
                    messages.info(
                        request,
                        'Completa il tuo profilo impresa per essere verificato e ricevere richieste.'
                    )
                    return redirect('utenti:profilo_impresa')
                elif user.user_type == 'artigiano':
                    messages.info(
                        request,
                        'Completa il tuo profilo artigiano per essere verificato e ricevere richieste.'
                    )
                    return redirect('artigiani:profilo')
                else:
                    return redirect('core:dashboard')
            
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'utenti/register.html', {'form': form})


@login_required
def profilo_view(request):
    """Vista per visualizzare e modificare il profilo utente"""
    user = request.user
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profilo aggiornato con successo!')
            return redirect('utenti:profilo')
        else:
            messages.error(request, 'Errore nell\'aggiornamento del profilo.')
    
    else:
        user_form = UserProfileForm(instance=user)
    
    context = {
        'user_form': user_form,
        'user': user,
    }
    
    # Aggiungi form specifico in base al tipo di utente
    if user.user_type == 'cliente':
        profilo_cliente, created = ProfiloCliente.objects.get_or_create(utente=user)
        if request.method == 'POST' and 'profilo_cliente' in request.POST:
            cliente_form = ProfiloClienteForm(request.POST, instance=profilo_cliente)
            if cliente_form.is_valid():
                cliente_form.save()
                messages.success(request, 'Profilo immobile aggiornato con successo!')
                return redirect('utenti:profilo')
        else:
            cliente_form = ProfiloClienteForm(instance=profilo_cliente)
        
        context['cliente_form'] = cliente_form
        context['profilo_cliente'] = profilo_cliente
    
    elif user.user_type == 'impresa':
        try:
            profilo_impresa = ProfiloImpresa.objects.get(utente=user)
        except ProfiloImpresa.DoesNotExist:
            profilo_impresa = ProfiloImpresa.objects.create(
                utente=user,
                ragione_sociale='',
                partita_iva='',
                tipo_impresa='generale',
                descrizione='',
                zone_operative=''
            )
        
        if request.method == 'POST' and 'profilo_impresa' in request.POST:
            impresa_form = ProfiloImpresaForm(request.POST, instance=profilo_impresa)
            if impresa_form.is_valid():
                impresa_form.save()
                messages.success(request, 'Profilo impresa aggiornato con successo!')
                
                # Notifica se l'impresa non è ancora verificata
                if not profilo_impresa.abilitato:
                    messages.info(
                        request,
                        'Il tuo profilo è in attesa di verifica. Sarai contattato entro 2 giorni lavorativi.'
                    )
                
                return redirect('utenti:profilo')
        else:
            impresa_form = ProfiloImpresaForm(instance=profilo_impresa)
        
        context['impresa_form'] = impresa_form
        context['profilo_impresa'] = profilo_impresa
    
    return render(request, 'utenti/profilo.html', context)


@login_required
def profilo_cliente_view(request):
    """Vista dedicata per il profilo cliente"""
    if request.user.user_type != 'cliente':
        messages.error(request, 'Accesso non autorizzato.')
        return redirect('core:dashboard')
    
    profilo_cliente, created = ProfiloCliente.objects.get_or_create(utente=request.user)
    
    if request.method == 'POST':
        form = ProfiloClienteForm(request.POST, instance=profilo_cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo immobile salvato con successo!')
            return redirect('core:dashboard')
    else:
        form = ProfiloClienteForm(instance=profilo_cliente)
    
    return render(request, 'utenti/profilo_cliente.html', {
        'form': form,
        'profilo_cliente': profilo_cliente
    })


@login_required
def profilo_impresa_view(request):
    """Vista dedicata per il profilo impresa"""
    if request.user.user_type != 'impresa':
        messages.error(request, 'Accesso non autorizzato.')
        return redirect('core:dashboard')
    
    try:
        profilo_impresa = ProfiloImpresa.objects.get(utente=request.user)
    except ProfiloImpresa.DoesNotExist:
        profilo_impresa = ProfiloImpresa.objects.create(
            utente=request.user,
            ragione_sociale='',
            partita_iva='',
            tipo_impresa='generale',
            descrizione='',
            zone_operative=''
        )
    
    if request.method == 'POST':
        form = ProfiloImpresaForm(request.POST, instance=profilo_impresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo impresa salvato con successo!')
            
            if not profilo_impresa.abilitato:
                messages.info(
                    request,
                    'Il tuo profilo è in attesa di verifica. Sarai contattato entro 2 giorni lavorativi.'
                )
            
            return redirect('core:dashboard_impresa')
    else:
        form = ProfiloImpresaForm(instance=profilo_impresa)
    
    return render(request, 'utenti/profilo_impresa.html', {
        'form': form,
        'profilo_impresa': profilo_impresa
    })


def lista_imprese_view(request):
    """Vista pubblica per visualizzare le imprese verificate"""
    imprese = ProfiloImpresa.objects.filter(abilitato=True).order_by('-rating', 'ragione_sociale')
    
    # Filtri
    tipo_impresa = request.GET.get('tipo_impresa')
    zona = request.GET.get('zona')
    
    if tipo_impresa:
        imprese = imprese.filter(tipo_impresa=tipo_impresa)
    
    if zona:
        imprese = imprese.filter(zone_operative__icontains=zona)
    
    context = {
        'imprese': imprese,
        'tipi_impresa': ProfiloImpresa.TIPO_IMPRESA_CHOICES,
        'filtro_tipo': tipo_impresa,
        'filtro_zona': zona,
    }
    
    return render(request, 'utenti/lista_imprese.html', context)


def dettaglio_impresa_view(request, impresa_id):
    """Vista per i dettagli di una singola impresa"""
    profilo_impresa = get_object_or_404(ProfiloImpresa, id=impresa_id, abilitato=True)
    
    context = {
        'profilo_impresa': profilo_impresa,
        'utente_impresa': profilo_impresa.utente,
    }
    
    return render(request, 'utenti/dettaglio_impresa.html', context)


@login_required
def change_password_view(request):
    """Vista per cambiare la password dell'utente"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password cambiata con successo!')
            
            # Aggiorna la sessione per evitare il logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, form.user)
            
            return redirect('utenti:profilo')
        else:
            # Gestione errori più user-friendly
            if 'old_password' in form.errors:
                messages.error(request, 'La password attuale non è corretta.')
            if 'new_password2' in form.errors:
                for error in form.errors['new_password2']:
                    if 'didn\'t match' in str(error):
                        messages.error(request, 'Le nuove password non coincidono.')
                    else:
                        messages.error(request, 'La nuova password non è valida: ' + str(error))
            if 'new_password1' in form.errors:
                for error in form.errors['new_password1']:
                    messages.error(request, 'Password non valida: ' + str(error))
    
    return redirect('utenti:profilo')


# Quick Login Services (placeholder implementations)
@require_http_methods(["GET"])
def google_login_redirect(request):
    """Placeholder per login con Google"""
    messages.info(request, '🚧 Login con Google non ancora implementato. Usa email e password per ora.')
    return redirect('utenti:login')


@require_http_methods(["GET"])
def spid_login_redirect(request):
    """Placeholder per login con SPID"""
    messages.info(request, '🚧 Login con SPID non ancora implementato. Usa email e password per ora.')
    return redirect('utenti:login')


@require_http_methods(["GET"])
def cie_login_redirect(request):
    """Placeholder per login con CIE"""
    messages.info(request, '🚧 Login con CIE non ancora implementato. Usa email e password per ora.')
    return redirect('utenti:login')
