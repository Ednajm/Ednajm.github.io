from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser, ProfiloCliente, ProfiloImpresa
# Import artigiani models
from artigiani.models import ProfiloArtigiano, CategoriaArtigiano


class CustomUserCreationForm(UserCreationForm):
    """Form per la registrazione di un nuovo utente"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Cognome')
    telefono = forms.CharField(max_length=15, required=False, label='Telefono')
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='cliente',
        label='Tipo di Account'
    )
    accetta_privacy = forms.BooleanField(
        required=True,
        label='Accetto la Privacy Policy'
    )
    accetta_marketing = forms.BooleanField(
        required=False,
        initial=False,
        label='Accetto di ricevere comunicazioni marketing'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'telefono', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizzazione dei widget
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome utente'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'email@esempio.it'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Il tuo nome'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Il tuo cognome'
        })
        self.fields['telefono'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+39 123 456 7890'
        })
        self.fields['user_type'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Conferma password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telefono = self.cleaned_data['telefono']
        user.user_type = self.cleaned_data['user_type']
        user.accetta_privacy = self.cleaned_data['accetta_privacy']
        user.accetta_marketing = self.cleaned_data['accetta_marketing']
        
        if commit:
            user.save()
            
            # Crea il profilo appropriato in base al tipo di utente
            if user.user_type == 'cliente':
                ProfiloCliente.objects.create(utente=user)
            elif user.user_type == 'impresa':
                ProfiloImpresa.objects.create(
                    utente=user,
                    ragione_sociale='',
                    partita_iva='',
                    tipo_impresa='generale',
                    descrizione='',
                    zone_operative=''
                )
            elif user.user_type == 'artigiano':
                # Create a basic artisan profile that will be completed later
                # Get the first available category as default
                default_category = CategoriaArtigiano.objects.filter(attiva=True).first()
                if not default_category:
                    # Create a default category if none exists
                    default_category = CategoriaArtigiano.objects.create(
                        nome='Generale',
                        descrizione='Categoria generale per artigiani'
                    )
                
                ProfiloArtigiano.objects.create(
                    utente=user,
                    categoria_principale=default_category,
                    nome_attivita='',
                    citta='',
                    cap='',
                    descrizione='',
                    telefono=user.telefono or '',
                    anni_esperienza=0
                )
        
        return user


class CustomLoginForm(forms.Form):
    """Form personalizzato per il login"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome utente o email'
        }),
        label='Nome utente o Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label='Password'
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Ricordami'
    )
    
    def __init__(self, request=None, *args, **kwargs):
        """Accetta il parametro request come Django's AuthenticationForm"""
        self.request = request
        super().__init__(*args, **kwargs)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Prova prima con username, poi con email
            user = authenticate(username=username, password=password)
            if user is None:
                # Prova con email
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user is None:
                raise forms.ValidationError("Nome utente/email o password non corretti.")
            elif not user.is_active:
                raise forms.ValidationError("Questo account è stato disattivato.")
        
        return self.cleaned_data


class ProfiloClienteForm(forms.ModelForm):
    """Form per aggiornare il profilo cliente"""
    
    class Meta:
        model = ProfiloCliente
        fields = [
            'tipo_immobile', 'proprieta', 'anno_costruzione', 'superficie_mq',
            'numero_vani', 'piano', 'ascensore', 'giardino', 'terrazza', 
            'garage', 'note_aggiuntive'
        ]
        widgets = {
            'tipo_immobile': forms.Select(attrs={'class': 'form-select'}),
            'proprieta': forms.Select(attrs={'class': 'form-select'}),
            'anno_costruzione': forms.NumberInput(attrs={'class': 'form-control', 'min': 1800, 'max': 2024}),
            'superficie_mq': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'numero_vani': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'piano': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'es. PT, 1°, 2°'}),
            'ascensore': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'giardino': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'terrazza': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'garage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'note_aggiuntive': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProfiloImpresaForm(forms.ModelForm):
    """Form per aggiornare il profilo impresa"""
    
    class Meta:
        model = ProfiloImpresa
        fields = [
            'ragione_sociale', 'partita_iva', 'codice_fiscale', 'tipo_impresa',
            'descrizione', 'anno_fondazione', 'numero_dipendenti', 'sito_web',
            'certificazioni', 'zone_operative'
        ]
        widgets = {
            'ragione_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'partita_iva': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 11}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 16}),
            'tipo_impresa': forms.Select(attrs={'class': 'form-select'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'anno_fondazione': forms.NumberInput(attrs={'class': 'form-control', 'min': 1800, 'max': 2024}),
            'numero_dipendenti': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'sito_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.esempio.it'}),
            'certificazioni': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zone_operative': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'es. Roma, Lazio; Milano, Lombardia'}),
        }
        
    def clean_partita_iva(self):
        partita_iva = self.cleaned_data.get('partita_iva')
        if partita_iva and len(partita_iva) != 11:
            raise forms.ValidationError("La partita IVA deve essere di 11 cifre.")
        return partita_iva
    
    def clean_codice_fiscale(self):
        codice_fiscale = self.cleaned_data.get('codice_fiscale')
        if codice_fiscale and len(codice_fiscale) != 16:
            raise forms.ValidationError("Il codice fiscale deve essere di 16 caratteri.")
        return codice_fiscale


class UserProfileForm(forms.ModelForm):
    """Form per aggiornare le informazioni base dell'utente"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'telefono', 'data_nascita',
            'indirizzo', 'citta', 'cap', 'provincia', 'foto_profilo',
            'accetta_marketing'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'indirizzo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'citta': forms.TextInput(attrs={'class': 'form-control'}),
            'cap': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 5}),
            'provincia': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2, 'placeholder': 'RM'}),
            'foto_profilo': forms.FileInput(attrs={'class': 'form-control'}),
            'accetta_marketing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }