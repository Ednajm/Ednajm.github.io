from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os

User = get_user_model()


class CategoriaIntervento(models.Model):
    """Categorie di interventi di ristrutturazione"""
    
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome Categoria')
    descrizione = models.TextField(verbose_name='Descrizione')
    icona = models.CharField(
        max_length=50, 
        blank=True, 
        help_text='Classe CSS per l\'icona (es. fas fa-hammer)',
        verbose_name='Icona CSS'
    )
    colore = models.CharField(
        max_length=7, 
        default='#007bff',
        help_text='Codice colore esadecimale (es. #007bff)',
        verbose_name='Colore'
    )
    attiva = models.BooleanField(default=True, verbose_name='Categoria Attiva')
    ordine = models.IntegerField(default=0, verbose_name='Ordine di Visualizzazione')
    
    class Meta:
        verbose_name = 'Categoria Intervento'
        verbose_name_plural = 'Categorie Interventi'
        ordering = ['ordine', 'nome']
    
    def __str__(self):
        return self.nome


class PacchettoRistrutturazione(models.Model):
    """Pacchetti predefiniti di ristrutturazione"""
    
    DIFFICOLTA_CHOICES = [
        ('facile', 'Facile'),
        ('media', 'Media'),
        ('difficile', 'Difficile'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name='Nome Pacchetto')
    categoria = models.ForeignKey(
        CategoriaIntervento, 
        on_delete=models.CASCADE,
        related_name='pacchetti'
    )
    descrizione_breve = models.TextField(
        max_length=300,
        verbose_name='Descrizione Breve'
    )
    descrizione_completa = models.TextField(verbose_name='Descrizione Completa')
    
    # Prezzi
    prezzo_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Prezzo Minimo (€)'
    )
    prezzo_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Prezzo Massimo (€)'
    )
    
    # Tempi
    durata_giorni_min = models.IntegerField(
        verbose_name='Durata Minima (giorni)',
        validators=[MinValueValidator(1)]
    )
    durata_giorni_max = models.IntegerField(
        verbose_name='Durata Massima (giorni)',
        validators=[MinValueValidator(1)]
    )
    
    difficolta = models.CharField(
        max_length=10,
        choices=DIFFICOLTA_CHOICES,
        default='media',
        verbose_name='Difficoltà'
    )
    
    # Caratteristiche
    include_progetto = models.BooleanField(
        default=True,
        verbose_name='Include Progetto'
    )
    include_pratiche = models.BooleanField(
        default=True,
        verbose_name='Include Gestione Pratiche'
    )
    include_bonus = models.BooleanField(
        default=False,
        verbose_name='Gestione Bonus Fiscali'
    )
    
    # Immagini
    immagine_principale = models.ImageField(
        upload_to='pacchetti/',
        verbose_name='Immagine Principale'
    )
    immagine_prima = models.ImageField(
        upload_to='pacchetti/prima/',
        blank=True,
        null=True,
        verbose_name='Foto Prima'
    )
    immagine_dopo = models.ImageField(
        upload_to='pacchetti/dopo/',
        blank=True,
        null=True,
        verbose_name='Foto Dopo'
    )
    
    # Meta
    attivo = models.BooleanField(default=True, verbose_name='Pacchetto Attivo')
    in_evidenza = models.BooleanField(default=False, verbose_name='In Evidenza')
    ordinamento = models.IntegerField(default=0, verbose_name='Ordine')
    
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pacchetto Ristrutturazione'
        verbose_name_plural = 'Pacchetti Ristrutturazione'
        ordering = ['ordinamento', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.prezzo_min}€-{self.prezzo_max}€"
    
    @property
    def prezzo_medio(self):
        return (self.prezzo_min + self.prezzo_max) / 2
    
    @property
    def durata_media(self):
        return (self.durata_giorni_min + self.durata_giorni_max) / 2


class ElementoPacchetto(models.Model):
    """Elementi che compongono un pacchetto"""
    
    pacchetto = models.ForeignKey(
        PacchettoRistrutturazione,
        on_delete=models.CASCADE,
        related_name='elementi'
    )
    nome = models.CharField(max_length=200, verbose_name='Nome Elemento')
    descrizione = models.TextField(blank=True, verbose_name='Descrizione')
    incluso = models.BooleanField(default=True, verbose_name='Incluso nel Prezzo')
    opzionale = models.BooleanField(default=False, verbose_name='Elemento Opzionale')
    costo_aggiuntivo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Costo Aggiuntivo (€)'
    )
    ordine = models.IntegerField(default=0, verbose_name='Ordine')
    
    class Meta:
        verbose_name = 'Elemento Pacchetto'
        verbose_name_plural = 'Elementi Pacchetto'
        ordering = ['ordine', 'nome']
    
    def __str__(self):
        status = "✓" if self.incluso else "○"
        return f"{status} {self.nome}"


class DiagnosiImmobile(models.Model):
    """Diagnosi automatica tramite AI delle condizioni dell'immobile"""
    
    STATO_CHOICES = [
        ('in_elaborazione', 'In Elaborazione'),
        ('completata', 'Completata'),
        ('errore', 'Errore'),
    ]
    
    PRIORITA_CHOICES = [
        ('bassa', 'Bassa'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    utente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='diagnosi'
    )
    
    # Input dell'utente
    foto_immobile = models.ImageField(
        upload_to='diagnosi/foto/',
        verbose_name='Foto Immobile'
    )
    planimetria = models.ImageField(
        upload_to='diagnosi/planimetrie/',
        blank=True,
        null=True,
        verbose_name='Planimetria'
    )
    
    note_utente = models.TextField(
        blank=True,
        verbose_name='Note e Richieste Specifiche'
    )
    
    # Risultati della diagnosi
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='in_elaborazione',
        verbose_name='Stato Elaborazione'
    )
    
    # Problemi rilevati
    problemi_strutturali = models.TextField(blank=True, verbose_name='Problemi Strutturali')
    problemi_elettrici = models.TextField(blank=True, verbose_name='Problemi Elettrici')
    problemi_idraulici = models.TextField(blank=True, verbose_name='Problemi Idraulici')
    problemi_termici = models.TextField(blank=True, verbose_name='Problemi di Isolamento')
    
    # Valutazioni
    stato_generale = models.CharField(
        max_length=20,
        choices=[
            ('ottimo', 'Ottimo'),
            ('buono', 'Buono'),
            ('discreto', 'Discreto'),
            ('da_ristrutturare', 'Da Ristrutturare'),
            ('pessimo', 'Pessimo'),
        ],
        blank=True,
        verbose_name='Stato Generale'
    )
    
    priorita_intervento = models.CharField(
        max_length=10,
        choices=PRIORITA_CHOICES,
        blank=True,
        verbose_name='Priorità Intervento'
    )
    
    # Stime
    stima_costi_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Stima Costi Minimi (€)'
    )
    stima_costi_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Stima Costi Massimi (€)'
    )
    
    stima_tempo_giorni = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Stima Tempo (giorni)'
    )
    
    # Bonus applicabili
    bonus_applicabili = models.TextField(
        blank=True,
        verbose_name='Bonus Fiscali Applicabili'
    )
    
    # Pacchetti consigliati
    pacchetti_consigliati = models.ManyToManyField(
        PacchettoRistrutturazione,
        blank=True,
        verbose_name='Pacchetti Consigliati'
    )
    
    # Report finale
    report_completo = models.TextField(
        blank=True,
        verbose_name='Report Completo'
    )
    
    # Meta
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_completamento = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Diagnosi Immobile'
        verbose_name_plural = 'Diagnosi Immobili'
        ordering = ['-data_creazione']
    
    def __str__(self):
        return f"Diagnosi di {self.utente.nome_completo} - {self.get_stato_display()}"
    
    @property
    def stima_costi_media(self):
        if self.stima_costi_min and self.stima_costi_max:
            return (self.stima_costi_min + self.stima_costi_max) / 2
        return None


class ConsulenzaVideo(models.Model):
    """Prenotazioni per consulenze video gratuite"""
    
    STATO_CHOICES = [
        ('richiesta', 'Richiesta Inviata'),
        ('confermata', 'Confermata'),
        ('completata', 'Completata'),
        ('annullata', 'Annullata'),
        ('no_show', 'Cliente Assente'),
    ]
    
    utente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consulenze'
    )
    
    # Dettagli appuntamento
    data_richiesta = models.DateTimeField(auto_now_add=True)
    data_preferita = models.DateTimeField(verbose_name='Data e Ora Preferita')
    data_confermata = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data e Ora Confermata'
    )
    
    # Informazioni sul progetto
    tipo_intervento = models.ForeignKey(
        CategoriaIntervento,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Tipo di Intervento'
    )
    
    descrizione_progetto = models.TextField(
        verbose_name='Descrizione del Progetto'
    )
    
    budget_orientativo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Budget Orientativo (€)'
    )
    
    urgenza = models.CharField(
        max_length=20,
        choices=[
            ('nessuna', 'Nessuna Fretta'),
            ('entro_mese', 'Entro un Mese'),
            ('entro_settimana', 'Entro una Settimana'),
            ('urgente', 'Urgente'),
        ],
        default='nessuna',
        verbose_name='Urgenza'
    )
    
    # Stato consulenza
    stato = models.CharField(
        max_length=15,
        choices=STATO_CHOICES,
        default='richiesta',
        verbose_name='Stato'
    )
    
    # Link meeting (generato dal sistema)
    link_meeting = models.URLField(
        blank=True,
        verbose_name='Link Video Meeting'
    )
    
    # Note consulente
    note_consulente = models.TextField(
        blank=True,
        verbose_name='Note del Consulente'
    )
    
    # Valutazione
    valutazione_cliente = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Valutazione Cliente (1-5)'
    )
    
    feedback_cliente = models.TextField(
        blank=True,
        verbose_name='Feedback Cliente'
    )
    
    class Meta:
        verbose_name = 'Consulenza Video'
        verbose_name_plural = 'Consulenze Video'
        ordering = ['-data_richiesta']
    
    def __str__(self):
        return f"Consulenza {self.utente.nome_completo} - {self.data_preferita.strftime('%d/%m/%Y %H:%M')}"


class Newsletter(models.Model):
    """Iscrizioni alla newsletter"""
    
    email = models.EmailField(unique=True, verbose_name='Email')
    nome = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nome'
    )
    attiva = models.BooleanField(default=True, verbose_name='Iscrizione Attiva')
    data_iscrizione = models.DateTimeField(auto_now_add=True)
    data_disiscrizione = models.DateTimeField(blank=True, null=True)
    
    # Interessi
    interesse_ristrutturazioni = models.BooleanField(default=True)
    interesse_bonus = models.BooleanField(default=True)
    interesse_consigli = models.BooleanField(default=True)
    interesse_novita = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Iscrizione Newsletter'
        verbose_name_plural = 'Iscrizioni Newsletter'
        ordering = ['-data_iscrizione']
    
    def __str__(self):
        return f"{self.email} ({'Attiva' if self.attiva else 'Disattivata'})"


class Ordine(models.Model):
    """Modello per gestire gli ordini/prenotazioni"""
    
    STATUS_CHOICES = [
        ('in_attesa', 'In Attesa di Pagamento'),
        ('pagato', 'Pagato'),
        ('confermato', 'Confermata'),
        ('in_lavorazione', 'In Lavorazione'),
        ('completato', 'Completato'),
        ('annullato', 'Annullato'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'In Attesa'),
        ('processing', 'In Elaborazione'),
        ('succeeded', 'Completato'),
        ('failed', 'Fallito'),
        ('canceled', 'Annullato'),
        ('refunded', 'Rimborsato'),
    ]
    
    id = models.AutoField(primary_key=True)
    numero_ordine = models.CharField(max_length=20, unique=True, editable=False)
    cliente = models.ForeignKey(
        'utenti.CustomUser', 
        on_delete=models.CASCADE, 
        related_name='ordini'
    )
    pacchetto = models.ForeignKey(
        PacchettoRistrutturazione,
        on_delete=models.CASCADE,
        related_name='ordini'
    )
    
    # Dettagli progetto
    indirizzo_immobile = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    cap = models.CharField(max_length=5)
    superficie_mq = models.PositiveIntegerField()
    note_aggiuntive = models.TextField(blank=True)
    
    # Prezzi
    prezzo_base = models.DecimalField(max_digits=10, decimal_places=2)
    costi_aggiuntivi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sconto_applicato = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status e pagamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_attesa')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    
    # Date
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    data_inizio_prevista = models.DateField(null=True, blank=True)
    data_fine_prevista = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-data_creazione']
        verbose_name = 'Ordine'
        verbose_name_plural = 'Ordini'
    
    def __str__(self):
        return f"Ordine {self.numero_ordine} - {self.cliente.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.numero_ordine:
            self.numero_ordine = self.genera_numero_ordine()
        super().save(*args, **kwargs)
    
    def genera_numero_ordine(self):
        import random
        import string
        from datetime import datetime
        
        oggi = datetime.now()
        anno = str(oggi.year)[2:]
        mese = f"{oggi.month:02d}"
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"RC{anno}{mese}{random_part}"
    
    @property
    def importo_acconto(self):
        """Calcola l'acconto del 30%"""
        return self.totale * 0.30
    
    @property
    def importo_saldo(self):
        """Calcola il saldo rimanente"""
        return self.totale - self.importo_acconto


class PagamentoRata(models.Model):
    """Modello per gestire i pagamenti rateali"""
    
    STATUS_CHOICES = [
        ('pending', 'In Attesa'),
        ('processing', 'In Elaborazione'),
        ('succeeded', 'Completato'),
        ('failed', 'Fallito'),
        ('canceled', 'Annullato'),
    ]
    
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE, related_name='pagamenti')
    numero_rata = models.PositiveIntegerField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    data_scadenza = models.DateField()
    data_pagamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    descrizione = models.CharField(max_length=200)
    
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['numero_rata']
        unique_together = ['ordine', 'numero_rata']
        verbose_name = 'Pagamento Rata'
        verbose_name_plural = 'Pagamenti Rate'
    
    def __str__(self):
        return f"Rata {self.numero_rata} - {self.ordine.numero_ordine}"


class MetodoPagamento(models.Model):
    """Modello per salvare i metodi di pagamento dei clienti"""
    
    TIPO_CHOICES = [
        ('card', 'Carta di Credito/Debito'),
        ('bank_transfer', 'Bonifico Bancario'),
        ('paypal', 'PayPal'),
    ]
    
    cliente = models.ForeignKey(
        'utenti.CustomUser',
        on_delete=models.CASCADE,
        related_name='metodi_pagamento'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    stripe_payment_method_id = models.CharField(max_length=200, blank=True)
    
    # Per carte
    brand = models.CharField(max_length=20, blank=True)  # visa, mastercard, etc
    last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.PositiveIntegerField(null=True, blank=True)
    exp_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Per altri metodi
    dettagli_aggiuntivi = models.JSONField(default=dict, blank=True)
    
    is_default = models.BooleanField(default=False)
    attivo = models.BooleanField(default=True)
    
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-data_creazione']
        verbose_name = 'Metodo di Pagamento'
        verbose_name_plural = 'Metodi di Pagamento'
    
    def __str__(self):
        if self.tipo == 'card' and self.last4:
            return f"{self.get_tipo_display()} •••• {self.last4}"
        return self.get_tipo_display()
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Rimuovi default dagli altri metodi del cliente
            MetodoPagamento.objects.filter(
                cliente=self.cliente,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
