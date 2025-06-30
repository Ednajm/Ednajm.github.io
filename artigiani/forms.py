from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import (
    ProfiloArtigiano, FotoLavoro, CategoriaArtigiano, 
    OrarioDisponibilita, Appuntamento, EccezioneOrario,
    DocumentoArtigiano, VideoArtigiano, MessaggioCliente
)


class ProfiloArtigianoForm(forms.ModelForm):
    """Form per creazione/modifica profilo artigiano"""
    
    class Meta:
        model = ProfiloArtigiano
        fields = [
            'categoria_principale', 'categorie_secondarie', 'nome_attivita', 
            'partita_iva', 'ha_partita_iva', 'citta', 'cap', 'indirizzo',
            'raggio_azione_km', 'descrizione', 'fascia_prezzo', 
            'prezzo_orario_min', 'prezzo_orario_max', 'disponibilita',
            'italiano', 'inglese', 'francese', 'arabo', 'altre_lingue',
            'anni_esperienza', 'foto_profilo', 'foto_banner',
            'telefono', 'whatsapp', 'email_lavoro', 'sito_web'
        ]
        
        widgets = {
            'categoria_principale': forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'required': True
            }),
            'categorie_secondarie': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'nome_attivita': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Es. Edilizia Rossi, Idraulica Bianchi...'
            }),
            'partita_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. IT12345678901'
            }),
            'ha_partita_iva': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'citta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Milano'
            }),
            'cap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. 20100'
            }),
            'indirizzo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Via, numero civico (opzionale)'
            }),
            'raggio_azione_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'value': 20
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrivi i tuoi servizi, la tua esperienza e cosa ti distingue...'
            }),
            'fascia_prezzo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prezzo_orario_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 10,
                'placeholder': 'Es. 25.00'
            }),
            'prezzo_orario_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 10,
                'placeholder': 'Es. 40.00'
            }),
            'disponibilita': forms.Select(attrs={
                'class': 'form-control'
            }),
            'italiano': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            }),
            'inglese': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'francese': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'arabo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'altre_lingue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Spagnolo, Tedesco...'
            }),
            'anni_esperienza': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'foto_profilo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_banner': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 333 1234567'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 333 1234567'
            }),
            'email_lavoro': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'lavoro@email.com'
            }),
            'sito_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.tuosito.it'
            }),
        }
        
        help_texts = {
            'categoria_principale': 'Seleziona la tua specializzazione principale',
            'categorie_secondarie': 'Aggiungi altre competenze per ricevere più richieste',
            'raggio_azione_km': 'Distanza massima che sei disposto a percorrere per un lavoro',
            'prezzo_orario_min': 'Prezzo minimo per ora di lavoro (€)',
            'prezzo_orario_max': 'Prezzo massimo per ora di lavoro (€)',
            'foto_profilo': 'Carica una foto professionale (consigliato)',
            'foto_banner': 'Immagine di copertina per il tuo profilo',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        prezzo_min = cleaned_data.get('prezzo_orario_min')
        prezzo_max = cleaned_data.get('prezzo_orario_max')
        
        if prezzo_min and prezzo_max and prezzo_min >= prezzo_max:
            raise ValidationError(
                'Il prezzo massimo deve essere superiore al prezzo minimo'
            )
        
        ha_partita_iva = cleaned_data.get('ha_partita_iva')
        partita_iva = cleaned_data.get('partita_iva')
        
        if ha_partita_iva and not partita_iva:
            raise ValidationError(
                'Inserisci la partita IVA se hai dichiarato di averla'
            )
        
        return cleaned_data


class FotoLavoroForm(forms.ModelForm):
    """Form per upload foto lavori"""
    
    class Meta:
        model = FotoLavoro
        fields = ['immagine', 'titolo', 'descrizione', 'categoria', 'in_evidenza']
        
        widgets = {
            'immagine': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'titolo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Ristrutturazione bagno moderno'
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrivi il lavoro realizzato...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'in_evidenza': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        help_texts = {
            'immagine': 'Carica un\'immagine di alta qualità (JPG, PNG)',
            'in_evidenza': 'Le foto in evidenza appaiono per prime nel profilo',
        }


class RicercaArtigianiForm(forms.Form):
    """Form per ricerca artigiani nella dashboard admin"""
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaArtigiano.objects.filter(attiva=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    citta = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Città'
        })
    )
    
    verificato = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    attivo = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ImpostazioniProfiloForm(forms.ModelForm):
    """Form per impostazioni profilo"""
    
    class Meta:
        model = ProfiloArtigiano
        fields = [
            'attivo', 'email_lavoro', 'telefono', 'whatsapp',
            'disponibilita', 'raggio_azione_km'
        ]
        
        widgets = {
            'attivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_lavoro': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'disponibilita': forms.Select(attrs={
                'class': 'form-control'
            }),
            'raggio_azione_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
        }


class OrarioDisponibilitaForm(forms.ModelForm):
    """Form per gestione orari di disponibilità giornalieri"""
    
    class Meta:
        model = OrarioDisponibilita
        fields = [
            'giorno_settimana', 'attivo', 'ora_inizio_mattina', 'ora_fine_mattina',
            'ora_inizio_pomeriggio', 'ora_fine_pomeriggio', 'pausa_pranzo', 'note'
        ]
        
        widgets = {
            'giorno_settimana': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'attivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'orario-toggle'
            }),
            'ora_inizio_mattina': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'  # 15 minuti
            }),
            'ora_fine_mattina': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'
            }),
            'ora_inizio_pomeriggio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'
            }),
            'ora_fine_pomeriggio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'
            }),
            'pausa_pranzo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Solo emergenze, Su appuntamento...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        attivo = cleaned_data.get('attivo')
        
        if attivo:
            ora_inizio_mattina = cleaned_data.get('ora_inizio_mattina')
            ora_fine_mattina = cleaned_data.get('ora_fine_mattina')
            ora_inizio_pomeriggio = cleaned_data.get('ora_inizio_pomeriggio')
            ora_fine_pomeriggio = cleaned_data.get('ora_fine_pomeriggio')
            
            # Almeno un orario deve essere definito
            if not ((ora_inizio_mattina and ora_fine_mattina) or 
                    (ora_inizio_pomeriggio and ora_fine_pomeriggio)):
                raise ValidationError(
                    'Definisci almeno un orario (mattina o pomeriggio)'
                )
            
            # Validazione orario mattina
            if ora_inizio_mattina and ora_fine_mattina:
                if ora_inizio_mattina >= ora_fine_mattina:
                    raise ValidationError(
                        'L\'ora di fine mattina deve essere successiva all\'ora di inizio'
                    )
            
            # Validazione orario pomeriggio
            if ora_inizio_pomeriggio and ora_fine_pomeriggio:
                if ora_inizio_pomeriggio >= ora_fine_pomeriggio:
                    raise ValidationError(
                        'L\'ora di fine pomeriggio deve essere successiva all\'ora di inizio'
                    )
            
            # Validazione pausa pranzo
            pausa_pranzo = cleaned_data.get('pausa_pranzo')
            if (pausa_pranzo and ora_fine_mattina and ora_inizio_pomeriggio and 
                ora_fine_mattina >= ora_inizio_pomeriggio):
                raise ValidationError(
                    'Con la pausa pranzo, l\'orario pomeridiano deve iniziare dopo quello mattutino'
                )
        
        return cleaned_data


class AppuntamentoForm(forms.ModelForm):
    """Form per creazione/modifica appuntamenti"""
    
    class Meta:
        model = Appuntamento
        fields = [
            'cliente_nome', 'cliente_email', 'cliente_telefono', 'titolo',
            'descrizione', 'tipo_appuntamento', 'data_appuntamento',
            'ora_inizio', 'durata_stimata', 'indirizzo', 'citta', 'cap',
            'costo_stimato', 'note_cliente', 'note_artigiano'
        ]
        
        widgets = {
            'cliente_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome e cognome del cliente'
            }),
            'cliente_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@cliente.com'
            }),
            'cliente_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 333 1234567'
            }),
            'titolo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Sopralluogo per ristrutturazione bagno'
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dettagli dell\'appuntamento...'
            }),
            'tipo_appuntamento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_appuntamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'ora_inizio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'  # 15 minuti
            }),
            'durata_stimata': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 480,
                'step': 15,
                'value': 60
            }),
            'indirizzo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Via Roma 123'
            }),
            'citta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Milano'
            }),
            'cap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '20100'
            }),
            'costo_stimato': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00'
            }),
            'note_cliente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Richieste specifiche del cliente...'
            }),
            'note_artigiano': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Note private per te...'
            }),
        }
        
        help_texts = {
            'durata_stimata': 'Durata in minuti (15-480)',
            'costo_stimato': 'Costo stimato in euro (opzionale)',
            'note_artigiano': 'Queste note sono visibili solo a te',
        }
    
    def __init__(self, *args, **kwargs):
        self.artigiano = kwargs.pop('artigiano', None)
        super().__init__(*args, **kwargs)
        
        # Se stiamo modificando un appuntamento esistente, 
        # non limitiamo la data minima
        if self.instance and self.instance.pk:
            self.fields['data_appuntamento'].widget.attrs.pop('min', None)
    
    def clean(self):
        cleaned_data = super().clean()
        data_appuntamento = cleaned_data.get('data_appuntamento')
        ora_inizio = cleaned_data.get('ora_inizio')
        durata_stimata = cleaned_data.get('durata_stimata')
        
        if data_appuntamento and ora_inizio:
            # Non permettere appuntamenti nel passato (solo per nuovi appuntamenti)
            if not (self.instance and self.instance.pk):
                now = timezone.now()
                appuntamento_datetime = timezone.make_aware(
                    datetime.combine(data_appuntamento, ora_inizio)
                )
                
                if appuntamento_datetime <= now:
                    raise ValidationError(
                        'Non puoi creare appuntamenti nel passato'
                    )
            
            # Calcola ora fine
            if durata_stimata:
                ora_fine = (datetime.combine(data_appuntamento, ora_inizio) + 
                           timedelta(minutes=durata_stimata)).time()
                cleaned_data['ora_fine'] = ora_fine
        
        return cleaned_data


class EccezioneOrarioForm(forms.ModelForm):
    """Form per gestione eccezioni agli orari (ferie, chiusure, ecc.)"""
    
    class Meta:
        model = EccezioneOrario
        fields = [
            'data_inizio', 'data_fine', 'tipo', 'descrizione',
            'ora_inizio_speciale', 'ora_fine_speciale'
        ]
        
        widgets = {
            'data_inizio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'data_fine': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'data-toggle': 'eccezione-tipo'
            }),
            'descrizione': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Ferie estive, Chiusura per malattia...'
            }),
            'ora_inizio_speciale': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'
            }),
            'ora_fine_speciale': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '900'
            }),
        }
        
        help_texts = {
            'tipo': 'Seleziona il tipo di eccezione',
            'ora_inizio_speciale': 'Solo per "Orario Speciale"',
            'ora_fine_speciale': 'Solo per "Orario Speciale"',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_inizio = cleaned_data.get('data_inizio')
        data_fine = cleaned_data.get('data_fine')
        tipo = cleaned_data.get('tipo')
        ora_inizio_speciale = cleaned_data.get('ora_inizio_speciale')
        ora_fine_speciale = cleaned_data.get('ora_fine_speciale')
        
        # Validazione date
        if data_inizio and data_fine:
            if data_inizio > data_fine:
                raise ValidationError(
                    'La data di fine deve essere successiva o uguale alla data di inizio'
                )
        
        # Validazione orari speciali
        if tipo == 'orario_speciale':
            if not (ora_inizio_speciale and ora_fine_speciale):
                raise ValidationError(
                    'Per orario speciale devi specificare inizio e fine'
                )
            if ora_inizio_speciale >= ora_fine_speciale:
                raise ValidationError(
                    'L\'ora di fine deve essere successiva all\'ora di inizio'
                )
        elif ora_inizio_speciale or ora_fine_speciale:
            # Se non è orario speciale, pulisci gli orari
            cleaned_data['ora_inizio_speciale'] = None
            cleaned_data['ora_fine_speciale'] = None
        
        return cleaned_data


class PrenotazioneAppuntamentoForm(forms.Form):
    """Form semplificato per prenotazione appuntamento da parte del cliente"""
    
    cliente_nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Il tuo nome e cognome'
        })
    )
    cliente_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'La tua email'
        })
    )
    cliente_telefono = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+39 333 1234567'
        })
    )
    tipo_appuntamento = forms.ChoiceField(
        choices=Appuntamento.TIPO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    data_appuntamento = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    ora_inizio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'step': '900'
        })
    )
    titolo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Es. Sopralluogo per ristrutturazione'
        })
    )
    descrizione = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descrivi brevemente il lavoro da svolgere...'
        })
    )
    indirizzo = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dove si trova il lavoro da fare'
        })
    )
    citta = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Città'
        })
    )
    cap = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CAP'
        })
    )
    note_cliente = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Eventuali richieste specifiche...'
        })
    )


class DocumentoArtigianoForm(forms.ModelForm):
    """Form per caricare documenti di certificazione"""
    
    class Meta:
        model = DocumentoArtigiano
        fields = ['tipo_documento', 'file_documento', 'descrizione', 'data_scadenza']
        
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'file_documento': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'required': True
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrizione del documento (opzionale)...'
            }),
            'data_scadenza': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        help_texts = {
            'file_documento': 'Formati supportati: PDF, JPG, PNG, DOC, DOCX (max 10MB)',
            'data_scadenza': 'Inserisci solo se il documento ha una scadenza',
        }
    
    def save(self, commit=True):
        documento = super().save(commit=False)
        if self.cleaned_data['file_documento']:
            documento.nome_file = self.cleaned_data['file_documento'].name
        if commit:
            documento.save()
        return documento


class VideoArtigianoForm(forms.ModelForm):
    """Form per caricare video di presentazione e lavori"""
    
    class Meta:
        model = VideoArtigiano
        fields = ['titolo', 'descrizione', 'tipo_video', 'file_video', 'miniatura', 'pubblico']
        
        widgets = {
            'titolo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. La mia presentazione, Ristrutturazione bagno...',
                'required': True
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrivi cosa mostri nel video...'
            }),
            'tipo_video': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file_video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.mp4,.avi,.mov,.wmv',
                'required': True
            }),
            'miniatura': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'pubblico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        help_texts = {
            'file_video': 'Formati supportati: MP4, AVI, MOV (max 100MB)',
            'miniatura': 'Immagine di anteprima per il video (opzionale)',
            'pubblico': 'Il video apparirà nel tuo profilo pubblico',
        }


class MessaggioClienteForm(forms.ModelForm):
    """Form per inviare messaggi agli artigiani"""
    
    class Meta:
        model = MessaggioCliente
        fields = ['nome_cliente', 'email_cliente', 'telefono_cliente', 'oggetto', 'messaggio']
        
        widgets = {
            'nome_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Il tuo nome e cognome',
                'required': True
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'la-tua-email@esempio.it',
                'required': True
            }),
            'telefono_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 333 1234567 (opzionale)'
            }),
            'oggetto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Richiesta preventivo ristrutturazione bagno',
                'required': True
            }),
            'messaggio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descrivi il lavoro che ti serve e le tue esigenze...',
                'required': True
            }),
        }


class RispostaMessaggioForm(forms.Form):
    """Form per rispondere ai messaggi dei clienti"""
    
    risposta = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Scrivi la tua risposta al cliente...',
            'required': True
        }),
        label='Risposta'
    )


class ProfiloArtigianoCompletoForm(forms.ModelForm):
    """Form completo per la registrazione iniziale dell'artigiano"""
    
    # Campi aggiuntivi per la registrazione
    accetta_termini = forms.BooleanField(
        required=True,
        label='Accetto i Termini di Servizio per Artigiani',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    accetta_commissioni = forms.BooleanField(
        required=True,
        label='Accetto le commissioni del 3% sui lavori ottenuti tramite la piattaforma',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = ProfiloArtigiano
        fields = [
            'categoria_principale', 'nome_attivita', 'citta', 'cap', 
            'indirizzo', 'raggio_azione_km', 'descrizione', 
            'anni_esperienza', 'telefono', 'ha_partita_iva', 'partita_iva',
            'foto_profilo'
        ]
        
        widgets = {
            'categoria_principale': forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'required': True
            }),
            'nome_attivita': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Es. Edilizia Rossi, Mario Idraulico...',
                'required': True
            }),
            'citta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Roma',
                'required': True
            }),
            'cap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00100',
                'required': True
            }),
            'indirizzo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Via, numero civico (opzionale)'
            }),
            'raggio_azione_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'value': 20
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Presenta i tuoi servizi e la tua esperienza...',
                'required': True
            }),
            'anni_esperienza': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+39 333 1234567',
                'required': True
            }),
            'ha_partita_iva': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'partita_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IT12345678901'
            }),
            'foto_profilo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        
        help_texts = {
            'categoria_principale': 'Seleziona la tua specializzazione principale',
            'raggio_azione_km': 'Quanto lontano sei disposto ad andare per un lavoro?',
            'foto_profilo': 'Una foto professionale aumenta la fiducia dei clienti',
            'ha_partita_iva': 'Spunta se hai una partita IVA',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        ha_partita_iva = cleaned_data.get('ha_partita_iva')
        partita_iva = cleaned_data.get('partita_iva')
        
        if ha_partita_iva and not partita_iva:
            raise ValidationError(
                'Inserisci la partita IVA se hai dichiarato di averla'
            )
        
        return cleaned_data
