from django import forms
from .models import (
    DiagnosiImmobile, ConsulenzaVideo, Newsletter, Ordine, CategoriaIntervento
)


class DiagnosiForm(forms.ModelForm):
    """Form per la richiesta di diagnosi immobile"""
    
    class Meta:
        model = DiagnosiImmobile
        fields = ['foto_immobile', 'planimetria', 'note_utente']
        widgets = {
            'foto_immobile': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'planimetria': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'note_utente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrivi il tuo immobile, i problemi che hai notato o le tue esigenze specifiche...'
            }),
        }
        labels = {
            'foto_immobile': 'Foto dell\'Immobile *',
            'planimetria': 'Planimetria (opzionale)',
            'note_utente': 'Note e Richieste Specifiche',
        }
        help_texts = {
            'foto_immobile': 'Carica una o più foto rappresentative del tuo immobile',
            'planimetria': 'Se disponibile, carica la planimetria per un\'analisi più precisa',
            'note_utente': 'Fornisci tutti i dettagli che ritieni utili per la diagnosi',
        }


class ConsulenzaVideoForm(forms.ModelForm):
    """Form per prenotare una consulenza video"""
    
    class Meta:
        model = ConsulenzaVideo
        fields = [
            'data_preferita', 'tipo_intervento', 'descrizione_progetto', 
            'budget_orientativo', 'urgenza'
        ]
        widgets = {
            'data_preferita': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': '2024-01-01T09:00',
                'max': '2025-12-31T18:00'
            }),
            'tipo_intervento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descrizione_progetto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrivi il progetto che hai in mente, gli obiettivi e le tue aspettative...'
            }),
            'budget_orientativo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 100,
                'placeholder': '10000'
            }),
            'urgenza': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'data_preferita': 'Data e Ora Preferita *',
            'tipo_intervento': 'Tipo di Intervento',
            'descrizione_progetto': 'Descrizione del Progetto *',
            'budget_orientativo': 'Budget Orientativo (€)',
            'urgenza': 'Urgenza del Progetto',
        }
        help_texts = {
            'data_preferita': 'Scegli quando preferisci fare la videochiamata (orario lavorativo 9:00-18:00)',
            'budget_orientativo': 'Indicaci un budget orientativo per aiutarci a proporti le soluzioni migliori',
            'descrizione_progetto': 'Più dettagli fornisci, più potremo aiutarti durante la consulenza',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popoliamo le categorie attive
        self.fields['tipo_intervento'].queryset = CategoriaIntervento.objects.filter(attiva=True)
        
        # Aggiungiamo validazione personalizzata
        self.fields['data_preferita'].required = True
        self.fields['descrizione_progetto'].required = True


class NewsletterForm(forms.ModelForm):
    """Form per l'iscrizione alla newsletter"""
    
    privacy_consent = forms.BooleanField(
        required=True,
        label='Accetto la Privacy Policy',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Newsletter
        fields = ['email', 'nome']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'La tua email',
                'required': True
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Il tuo nome (opzionale)'
            }),
        }
        labels = {
            'email': 'Email *',
            'nome': 'Nome',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email=email, attiva=True).exists():
            raise forms.ValidationError('Questa email è già iscritta alla newsletter.')
        return email


class ContattiForm(forms.Form):
    """Form per i contatti"""
    
    ARGOMENTO_CHOICES = [
        ('info', 'Richiesta Informazioni'),
        ('preventivo', 'Richiesta Preventivo'),
        ('supporto', 'Supporto Tecnico'),
        ('collaborazione', 'Collaborazione/Partnership'),
        ('altro', 'Altro'),
    ]
    
    nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Il tuo nome'
        }),
        label='Nome *'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'La tua email'
        }),
        label='Email *'
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+39 123 456 7890'
        }),
        label='Telefono'
    )
    
    argomento = forms.ChoiceField(
        choices=ARGOMENTO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Argomento *'
    )
    
    messaggio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Scrivi qui il tuo messaggio...'
        }),
        label='Messaggio *'
    )
    
    privacy_consent = forms.BooleanField(
        required=True,
        label='Accetto la Privacy Policy e il trattamento dei dati',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class FiltriPacchettiForm(forms.Form):
    """Form per i filtri nella pagina pacchetti"""
    
    ORDINAMENTO_CHOICES = [
        ('ordinamento', 'Predefinito'),
        ('prezzo_asc', 'Prezzo: dal più basso'),
        ('prezzo_desc', 'Prezzo: dal più alto'),
        ('nome', 'Nome A-Z'),
    ]
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaIntervento.objects.filter(attiva=True),
        required=False,
        empty_label="Tutte le categorie",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Categoria'
    )
    
    prezzo_max = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Budget massimo'
        }),
        label='Budget Massimo (€)'
    )
    
    difficolta = forms.ChoiceField(
        choices=[('', 'Tutte le difficoltà')] + DiagnosiImmobile.PRIORITA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Difficoltà'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cerca pacchetti...'
        }),
        label='Cerca'
    )
    
    ordine = forms.ChoiceField(
        choices=ORDINAMENTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Ordina per'
    )


class OrdineForm(forms.ModelForm):
    """Form per creare un nuovo ordine"""
    
    class Meta:
        model = Ordine
        fields = [
            'indirizzo_immobile', 'citta', 'cap', 'superficie_mq', 'note_aggiuntive'
        ]
        widgets = {
            'indirizzo_immobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Via/Piazza e numero civico'
            }),
            'citta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Città'
            }),
            'cap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CAP'
            }),
            'superficie_mq': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Superficie in mq'
            }),
            'note_aggiuntive': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Eventuali note o richieste particolari...'
            }),
        }
        labels = {
            'indirizzo_immobile': 'Indirizzo immobile',
            'citta': 'Città',
            'cap': 'CAP',
            'superficie_mq': 'Superficie (mq)',
            'note_aggiuntive': 'Note aggiuntive',
        }
