from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from PIL import Image

User = get_user_model()

class CategoriaArtigiano(models.Model):
    """Categorie di artigiani (muratore, pittore, idraulico, ecc.)"""
    
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome Categoria')
    descrizione = models.TextField(blank=True, verbose_name='Descrizione')
    icona = models.CharField(
        max_length=50, 
        blank=True, 
        help_text='Classe CSS per l\'icona (es. fas fa-hammer)',
        verbose_name='Icona CSS'
    )
    colore = models.CharField(
        max_length=7, 
        default='#007bff',
        help_text='Codice colore esadecimale',
        verbose_name='Colore'
    )
    attiva = models.BooleanField(default=True, verbose_name='Categoria Attiva')
    ordine = models.IntegerField(default=0, verbose_name='Ordine')
    
    class Meta:
        verbose_name = 'Categoria Artigiano'
        verbose_name_plural = 'Categorie Artigiani'
        ordering = ['ordine', 'nome']
    
    def __str__(self):
        return self.nome


class ProfiloArtigiano(models.Model):
    """Profilo dettagliato dell'artigiano"""
    
    FASCIA_PREZZO_CHOICES = [
        ('economico', '€ - Economico'),
        ('medio', '€€ - Medio'),
        ('alto', '€€€ - Alto'),
        ('premium', '€€€€ - Premium'),
    ]
    
    DISPONIBILITA_CHOICES = [
        ('mattina', 'Solo Mattina (8:00-12:00)'),
        ('pomeriggio', 'Solo Pomeriggio (14:00-18:00)'),
        ('sera', 'Anche Sera (fino alle 20:00)'),
        ('weekend', 'Anche Weekend'),
        ('flessibile', 'Orari Flessibili'),
    ]
    
    utente = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Utente')
    categoria_principale = models.ForeignKey(
        CategoriaArtigiano, 
        on_delete=models.CASCADE, 
        verbose_name='Categoria Principale'
    )
    categorie_secondarie = models.ManyToManyField(
        CategoriaArtigiano,
        blank=True,
        related_name='artigiani_secondari',
        verbose_name='Altre Competenze'
    )
    
    # Informazioni base
    nome_attivita = models.CharField(max_length=200, verbose_name='Nome Attività/Ditta')
    partita_iva = models.CharField(max_length=20, blank=True, verbose_name='Partita IVA')
    ha_partita_iva = models.BooleanField(default=False, verbose_name='Ha Partita IVA')
    
    # Localizzazione
    citta = models.CharField(max_length=100, verbose_name='Città')
    cap = models.CharField(max_length=10, verbose_name='CAP')
    indirizzo = models.CharField(max_length=200, blank=True, verbose_name='Indirizzo')
    raggio_azione_km = models.IntegerField(
        default=20, 
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Raggio di Azione (km)'
    )
    
    # Descrizione e competenze
    descrizione = models.TextField(verbose_name='Descrizione Servizi')
    descrizione_ai_generata = models.TextField(
        blank=True, 
        verbose_name='Descrizione Generata da AI'
    )
    usa_descrizione_ai = models.BooleanField(
        default=False, 
        verbose_name='Usa Descrizione AI'
    )
    
    # Pricing e disponibilità
    fascia_prezzo = models.CharField(
        max_length=20, 
        choices=FASCIA_PREZZO_CHOICES,
        default='medio',
        verbose_name='Fascia di Prezzo'
    )
    prezzo_orario_min = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Prezzo Orario Minimo (€)'
    )
    prezzo_orario_max = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Prezzo Orario Massimo (€)'
    )
    disponibilita = models.CharField(
        max_length=20,
        choices=DISPONIBILITA_CHOICES,
        default='flessibile',
        verbose_name='Disponibilità Oraria'
    )
    
    # Lingue parlate
    italiano = models.BooleanField(default=True, verbose_name='Italiano')
    inglese = models.BooleanField(default=False, verbose_name='Inglese')
    francese = models.BooleanField(default=False, verbose_name='Francese')
    arabo = models.BooleanField(default=False, verbose_name='Arabo')
    altre_lingue = models.CharField(max_length=200, blank=True, verbose_name='Altre Lingue')
    
    # Esperienza
    anni_esperienza = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name='Anni di Esperienza'
    )
    numero_lavori_completati = models.IntegerField(default=0, verbose_name='Lavori Completati')
    
    # Foto profilo e banner
    foto_profilo = models.ImageField(
        upload_to='artigiani/profili/', 
        blank=True, 
        verbose_name='Foto Profilo'
    )
    foto_banner = models.ImageField(
        upload_to='artigiani/banner/', 
        blank=True, 
        verbose_name='Foto Banner'
    )
    
    # Contatti
    telefono = models.CharField(max_length=20, verbose_name='Telefono')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp')
    email_lavoro = models.EmailField(blank=True, verbose_name='Email di Lavoro')
    sito_web = models.URLField(blank=True, verbose_name='Sito Web')
    
    # Stato del profilo
    verificato = models.BooleanField(default=False, verbose_name='Profilo Verificato')
    attivo = models.BooleanField(default=True, verbose_name='Profilo Attivo')
    premium = models.BooleanField(default=False, verbose_name='Account Premium')
    data_registrazione = models.DateTimeField(default=timezone.now, verbose_name='Data Registrazione')
    ultimo_accesso = models.DateTimeField(null=True, blank=True, verbose_name='Ultimo Accesso')
    
    # Statistiche
    visualizzazioni_profilo = models.IntegerField(default=0, verbose_name='Visualizzazioni Profilo')
    contatti_ricevuti = models.IntegerField(default=0, verbose_name='Contatti Ricevuti')
    
    class Meta:
        verbose_name = 'Profilo Artigiano'
        verbose_name_plural = 'Profili Artigiani'
        ordering = ['-premium', '-verificato', '-numero_lavori_completati', 'nome_attivita']
    
    def __str__(self):
        return f"{self.nome_attivita} - {self.categoria_principale.nome}"
    
    @property
    def voto_medio(self):
        """Calcola il voto medio delle recensioni"""
        recensioni = self.recensioni.all()
        if recensioni:
            return sum([r.voto for r in recensioni]) / len(recensioni)
        return 0
    
    @property
    def numero_recensioni(self):
        """Numero totale di recensioni"""
        return self.recensioni.count()
    
    @property
    def lingue_parlate_lista(self):
        """Lista delle lingue parlate"""
        lingue = []
        if self.italiano: lingue.append('Italiano')
        if self.inglese: lingue.append('Inglese')
        if self.francese: lingue.append('Francese')
        if self.arabo: lingue.append('Arabo')
        if self.altre_lingue:
            lingue.extend([l.strip() for l in self.altre_lingue.split(',')])
        return lingue


class FotoLavoro(models.Model):
    """Foto dei lavori dell'artigiano"""
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano, 
        on_delete=models.CASCADE, 
        related_name='foto_lavori',
        verbose_name='Artigiano'
    )
    immagine = models.ImageField(upload_to='artigiani/lavori/', verbose_name='Immagine')
    titolo = models.CharField(max_length=200, verbose_name='Titolo')
    descrizione = models.TextField(blank=True, verbose_name='Descrizione')
    data_lavoro = models.DateField(null=True, blank=True, verbose_name='Data Lavoro')
    categoria = models.ForeignKey(
        CategoriaArtigiano, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Categoria Lavoro'
    )
    in_evidenza = models.BooleanField(default=False, verbose_name='In Evidenza')
    ordine = models.IntegerField(default=0, verbose_name='Ordine')
    
    class Meta:
        verbose_name = 'Foto Lavoro'
        verbose_name_plural = 'Foto Lavori'
        ordering = ['-in_evidenza', 'ordine', '-data_lavoro']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.titolo}"


class RecensioneArtigiano(models.Model):
    """Recensioni degli artigiani"""
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano, 
        on_delete=models.CASCADE, 
        related_name='recensioni',
        verbose_name='Artigiano'
    )
    cliente_nome = models.CharField(max_length=100, verbose_name='Nome Cliente')
    cliente_email = models.EmailField(verbose_name='Email Cliente')
    cliente_telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono Cliente')
    
    voto = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Voto (1-5)'
    )
    titolo = models.CharField(max_length=200, verbose_name='Titolo Recensione')
    commento = models.TextField(verbose_name='Commento')
    
    # Valutazioni specifiche
    qualita_lavoro = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Qualità Lavoro'
    )
    puntualita = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Puntualità'
    )
    cortesia = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Cortesia'
    )
    rapporto_qualita_prezzo = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rapporto Qualità/Prezzo'
    )
    
    verificata = models.BooleanField(default=False, verbose_name='Recensione Verificata')
    data_recensione = models.DateTimeField(default=timezone.now, verbose_name='Data Recensione')
    data_verifica = models.DateTimeField(null=True, blank=True, verbose_name='Data Verifica')
    
    class Meta:
        verbose_name = 'Recensione Artigiano'
        verbose_name_plural = 'Recensioni Artigiani'
        ordering = ['-data_recensione']
        unique_together = ['artigiano', 'cliente_email']  # Un cliente può recensire una sola volta
    
    def __str__(self):
        return f"{self.cliente_nome} - {self.artigiano.nome_attivita} ({self.voto}/5)"


class RichiestaPreventivo(models.Model):
    """Richieste di preventivo dai clienti"""
    
    STATO_CHOICES = [
        ('nuova', 'Nuova'),
        ('vista', 'Vista'),
        ('risposta', 'Risposta Inviata'),
        ('accettata', 'Accettata'),
        ('rifiutata', 'Rifiutata'),
        ('completata', 'Completata'),
    ]
    
    URGENZA_CHOICES = [
        ('bassa', 'Non Urgente'),
        ('media', 'Medio'),
        ('alta', 'Urgente'),
        ('immediata', 'Immediata'),
    ]
    
    # Dati cliente
    cliente_nome = models.CharField(max_length=100, verbose_name='Nome Cliente')
    cliente_email = models.EmailField(verbose_name='Email Cliente')
    cliente_telefono = models.CharField(max_length=20, verbose_name='Telefono Cliente')
    
    # Dettagli richiesta
    categoria = models.ForeignKey(
        CategoriaArtigiano, 
        on_delete=models.CASCADE,
        verbose_name='Categoria Lavoro'
    )
    titolo = models.CharField(max_length=200, verbose_name='Titolo Lavoro')
    descrizione = models.TextField(verbose_name='Descrizione Dettagliata')
    
    # Localizzazione
    citta = models.CharField(max_length=100, verbose_name='Città')
    cap = models.CharField(max_length=10, verbose_name='CAP')
    indirizzo = models.CharField(max_length=200, blank=True, verbose_name='Indirizzo')
    
    # Dettagli tecnici
    superficie_mq = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Superficie (mq)'
    )
    budget_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Budget Minimo (€)'
    )
    budget_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Budget Massimo (€)'
    )
    
    urgenza = models.CharField(
        max_length=20,
        choices=URGENZA_CHOICES,
        default='media',
        verbose_name='Urgenza'
    )
    data_inizio_preferita = models.DateField(null=True, blank=True, verbose_name='Data Inizio Preferita')
    
    # Foto allegate
    foto1 = models.ImageField(upload_to='richieste/', blank=True, verbose_name='Foto 1')
    foto2 = models.ImageField(upload_to='richieste/', blank=True, verbose_name='Foto 2')
    foto3 = models.ImageField(upload_to='richieste/', blank=True, verbose_name='Foto 3')
    
    # Analisi AI
    analisi_ai = models.TextField(blank=True, verbose_name='Analisi AI della Foto')
    categoria_suggerita_ai = models.ForeignKey(
        CategoriaArtigiano,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='richieste_suggerite',
        verbose_name='Categoria Suggerita da AI'
    )
    
    # Stato e tracking
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='nuova',
        verbose_name='Stato'
    )
    data_creazione = models.DateTimeField(default=timezone.now, verbose_name='Data Creazione')
    data_ultima_modifica = models.DateTimeField(auto_now=True, verbose_name='Ultima Modifica')
    
    # Artigiani contattati
    artigiani_contattati = models.ManyToManyField(
        ProfiloArtigiano,
        through='RispostaPreventivo',
        verbose_name='Artigiani Contattati'
    )
    
    class Meta:
        verbose_name = 'Richiesta Preventivo'
        verbose_name_plural = 'Richieste Preventivi'
        ordering = ['-data_creazione']
    
    def __str__(self):
        return f"{self.cliente_nome} - {self.titolo}"


class RispostaPreventivo(models.Model):
    """Risposte degli artigiani alle richieste di preventivo"""
    
    STATO_CHOICES = [
        ('inviata', 'Inviata'),
        ('vista', 'Vista dal Cliente'),
        ('accettata', 'Accettata'),
        ('rifiutata', 'Rifiutata'),
    ]
    
    richiesta = models.ForeignKey(
        RichiestaPreventivo, 
        on_delete=models.CASCADE,
        verbose_name='Richiesta'
    )
    artigiano = models.ForeignKey(
        ProfiloArtigiano, 
        on_delete=models.CASCADE,
        verbose_name='Artigiano'
    )
    
    # Dettagli offerta
    prezzo_offerto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Prezzo Offerto (€)'
    )
    giorni_completamento = models.IntegerField(verbose_name='Giorni per Completamento')
    data_inizio_proposta = models.DateField(verbose_name='Data Inizio Proposta')
    
    descrizione_offerta = models.TextField(verbose_name='Descrizione Offerta')
    materiali_inclusi = models.BooleanField(default=False, verbose_name='Materiali Inclusi')
    garanzia_mesi = models.IntegerField(default=12, verbose_name='Garanzia (mesi)')
    
    # Stato
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='inviata',
        verbose_name='Stato'
    )
    data_invio = models.DateTimeField(default=timezone.now, verbose_name='Data Invio')
    data_vista = models.DateTimeField(null=True, blank=True, verbose_name='Data Vista')
    
    class Meta:
        verbose_name = 'Risposta Preventivo'
        verbose_name_plural = 'Risposte Preventivi'
        ordering = ['prezzo_offerto', '-data_invio']
        unique_together = ['richiesta', 'artigiano']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.richiesta.titolo} (€{self.prezzo_offerto})"


class OrarioDisponibilita(models.Model):
    """Orari di disponibilità dell'artigiano per ogni giorno della settimana"""
    
    GIORNI_SETTIMANA = [
        (0, 'Lunedì'),
        (1, 'Martedì'),
        (2, 'Mercoledì'),
        (3, 'Giovedì'),
        (4, 'Venerdì'),
        (5, 'Sabato'),
        (6, 'Domenica'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano, 
        on_delete=models.CASCADE, 
        related_name='orari_disponibilita',
        verbose_name='Artigiano'
    )
    giorno_settimana = models.IntegerField(
        choices=GIORNI_SETTIMANA,
        verbose_name='Giorno della Settimana'
    )
    attivo = models.BooleanField(default=True, verbose_name='Giorno Attivo')
    ora_inizio_mattina = models.TimeField(
        null=True, blank=True,
        verbose_name='Inizio Mattina',
        help_text='Es. 08:00'
    )
    ora_fine_mattina = models.TimeField(
        null=True, blank=True,
        verbose_name='Fine Mattina',
        help_text='Es. 12:00'
    )
    ora_inizio_pomeriggio = models.TimeField(
        null=True, blank=True,
        verbose_name='Inizio Pomeriggio',
        help_text='Es. 14:00'
    )
    ora_fine_pomeriggio = models.TimeField(
        null=True, blank=True,
        verbose_name='Fine Pomeriggio',
        help_text='Es. 18:00'
    )
    pausa_pranzo = models.BooleanField(
        default=True,
        verbose_name='Pausa Pranzo',
        help_text='Pausa tra mattina e pomeriggio'
    )
    note = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Note',
        help_text='Es. Solo emergenze, Disponibile su chiamata'
    )
    
    class Meta:
        verbose_name = 'Orario Disponibilità'
        verbose_name_plural = 'Orari Disponibilità'
        unique_together = ['artigiano', 'giorno_settimana']
        ordering = ['giorno_settimana']
    
    def __str__(self):
        giorno = dict(self.GIORNI_SETTIMANA)[self.giorno_settimana]
        if not self.attivo:
            return f"{self.artigiano.nome_attivita} - {giorno} (Chiuso)"
        
        orari = []
        if self.ora_inizio_mattina and self.ora_fine_mattina:
            orari.append(f"{self.ora_inizio_mattina.strftime('%H:%M')}-{self.ora_fine_mattina.strftime('%H:%M')}")
        if self.ora_inizio_pomeriggio and self.ora_fine_pomeriggio:
            orari.append(f"{self.ora_inizio_pomeriggio.strftime('%H:%M')}-{self.ora_fine_pomeriggio.strftime('%H:%M')}")
        
        orari_str = ", ".join(orari) if orari else "Orari non definiti"
        return f"{self.artigiano.nome_attivita} - {giorno}: {orari_str}"
    
    def get_orari_giorno(self):
        """Restituisce una lista degli orari disponibili per questo giorno"""
        orari = []
        if self.attivo:
            if self.ora_inizio_mattina and self.ora_fine_mattina:
                orari.append({
                    'periodo': 'mattina',
                    'inizio': self.ora_inizio_mattina,
                    'fine': self.ora_fine_mattina
                })
            if self.ora_inizio_pomeriggio and self.ora_fine_pomeriggio:
                orari.append({
                    'periodo': 'pomeriggio',
                    'inizio': self.ora_inizio_pomeriggio,
                    'fine': self.ora_fine_pomeriggio
                })
        return orari


class Appuntamento(models.Model):
    """Appuntamenti prenotati con l'artigiano"""
    
    STATO_CHOICES = [
        ('richiesto', 'Richiesto'),
        ('confermato', 'Confermato'),
        ('in_corso', 'In Corso'),
        ('completato', 'Completato'),
        ('annullato', 'Annullato'),
        ('rimandato', 'Rimandato'),
    ]
    
    TIPO_CHOICES = [
        ('sopralluogo', 'Sopralluogo'),
        ('preventivo', 'Preventivo'),
        ('lavoro', 'Esecuzione Lavoro'),
        ('consulenza', 'Consulenza'),
        ('riparazione', 'Riparazione'),
        ('manutenzione', 'Manutenzione'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='appuntamenti',
        verbose_name='Artigiano'
    )
    cliente_nome = models.CharField(max_length=100, verbose_name='Nome Cliente')
    cliente_email = models.EmailField(verbose_name='Email Cliente')
    cliente_telefono = models.CharField(max_length=20, verbose_name='Telefono Cliente')
    
    titolo = models.CharField(max_length=200, verbose_name='Titolo Appuntamento')
    descrizione = models.TextField(blank=True, verbose_name='Descrizione')
    tipo_appuntamento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='sopralluogo',
        verbose_name='Tipo Appuntamento'
    )
    
    data_appuntamento = models.DateField(verbose_name='Data Appuntamento')
    ora_inizio = models.TimeField(verbose_name='Ora Inizio')
    ora_fine = models.TimeField(verbose_name='Ora Fine')
    durata_stimata = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(480)],
        verbose_name='Durata Stimata (minuti)',
        help_text='Durata stimata in minuti (15-480)'
    )
    
    indirizzo = models.CharField(max_length=300, verbose_name='Indirizzo')
    citta = models.CharField(max_length=100, verbose_name='Città')
    cap = models.CharField(max_length=10, verbose_name='CAP')
    
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='richiesto',
        verbose_name='Stato'
    )
    
    costo_stimato = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Stimato (€)'
    )
    
    note_artigiano = models.TextField(
        blank=True,
        verbose_name='Note Artigiano',
        help_text='Note private dell\'artigiano'
    )
    note_cliente = models.TextField(
        blank=True,
        verbose_name='Note Cliente',
        help_text='Richieste specifiche del cliente'
    )
    
    # Metadati
    data_creazione = models.DateTimeField(auto_now_add=True, verbose_name='Data Creazione')
    data_modifica = models.DateTimeField(auto_now=True, verbose_name='Ultima Modifica')
    
    # Promemoria
    promemoria_inviato = models.BooleanField(default=False, verbose_name='Promemoria Inviato')
    conferma_cliente = models.BooleanField(default=False, verbose_name='Confermato dal Cliente')
    
    class Meta:
        verbose_name = 'Appuntamento'
        verbose_name_plural = 'Appuntamenti'
        ordering = ['data_appuntamento', 'ora_inizio']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.cliente_nome} ({self.data_appuntamento} {self.ora_inizio})"
    
    def get_durata_ore(self):
        """Restituisce la durata in formato ore:minuti"""
        ore = self.durata_stimata // 60
        minuti = self.durata_stimata % 60
        if ore > 0:
            return f"{ore}h {minuti}m" if minuti > 0 else f"{ore}h"
        return f"{minuti}m"
    
    def is_today(self):
        """Controlla se l'appuntamento è oggi"""
        return self.data_appuntamento == timezone.now().date()
    
    def is_upcoming(self):
        """Controlla se l'appuntamento è futuro"""
        return self.data_appuntamento >= timezone.now().date()
    
    def can_be_cancelled(self):
        """Controlla se l'appuntamento può essere annullato"""
        return self.stato in ['richiesto', 'confermato'] and self.is_upcoming()
    
    def get_stato_display_class(self):
        """Restituisce la classe CSS per il colore dello stato"""
        status_classes = {
            'richiesto': 'warning',
            'confermato': 'info',
            'in_corso': 'primary',
            'completato': 'success',
            'annullato': 'danger',
            'rimandato': 'secondary',
        }
        return status_classes.get(self.stato, 'secondary')


class EccezioneOrario(models.Model):
    """Eccezioni agli orari standard (ferie, giorni di chiusura, ecc.)"""
    
    TIPO_CHOICES = [
        ('chiusura', 'Giorno di Chiusura'),
        ('ferie', 'Ferie'),
        ('malattia', 'Malattia'),
        ('emergenza', 'Emergenza'),
        ('orario_speciale', 'Orario Speciale'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='eccezioni_orario',
        verbose_name='Artigiano'
    )
    data_inizio = models.DateField(verbose_name='Data Inizio')
    data_fine = models.DateField(verbose_name='Data Fine')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo Eccezione'
    )
    descrizione = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descrizione'
    )
    
    # Per orari speciali
    ora_inizio_speciale = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Ora Inizio Speciale'
    )
    ora_fine_speciale = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Ora Fine Speciale'
    )
    
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Eccezione Orario'
        verbose_name_plural = 'Eccezioni Orario'
        ordering = ['data_inizio']
    
    def __str__(self):
        if self.data_inizio == self.data_fine:
            return f"{self.artigiano.nome_attivita} - {self.get_tipo_display()} ({self.data_inizio})"
        return f"{self.artigiano.nome_attivita} - {self.get_tipo_display()} ({self.data_inizio} - {self.data_fine})"
    
    def is_active_today(self):
        """Controlla se l'eccezione è attiva oggi"""
        oggi = timezone.now().date()
        return self.data_inizio <= oggi <= self.data_fine


class DocumentoArtigiano(models.Model):
    """Documenti caricati dall'artigiano per la certificazione"""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('documento_identita', 'Documento di Identità'),
        ('patente', 'Patente di Guida'),
        ('codice_fiscale', 'Codice Fiscale'),
        ('partita_iva', 'Partita IVA'),
        ('visura_camerale', 'Visura Camerale'),
        ('certificato_competenza', 'Certificato di Competenza'),
        ('attestato_corso', 'Attestato Corso Professionale'),
        ('licenza_lavoro', 'Licenza/Abilitazione'),
        ('assicurazione', 'Assicurazione Professionale'),
        ('altro', 'Altro Documento'),
    ]
    
    STATO_VERIFICA_CHOICES = [
        ('in_attesa', 'In Attesa di Verifica'),
        ('verificato', 'Verificato'),
        ('rifiutato', 'Rifiutato'),
        ('scaduto', 'Scaduto'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='documenti',
        verbose_name='Artigiano'
    )
    tipo_documento = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name='Tipo Documento'
    )
    file_documento = models.FileField(
        upload_to='artigiani/documenti/',
        verbose_name='File Documento'
    )
    nome_file = models.CharField(
        max_length=255,
        verbose_name='Nome File'
    )
    descrizione = models.TextField(
        blank=True,
        verbose_name='Descrizione'
    )
    data_caricamento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Caricamento'
    )
    data_scadenza = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data Scadenza'
    )
    stato_verifica = models.CharField(
        max_length=15,
        choices=STATO_VERIFICA_CHOICES,
        default='in_attesa',
        verbose_name='Stato Verifica'
    )
    note_verifica = models.TextField(
        blank=True,
        verbose_name='Note Verifica'
    )
    verificato_da = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documenti_verificati',
        verbose_name='Verificato Da'
    )
    data_verifica = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data Verifica'
    )
    
    class Meta:
        verbose_name = 'Documento Artigiano'
        verbose_name_plural = 'Documenti Artigiani'
        ordering = ['-data_caricamento']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.get_tipo_documento_display()}"
    
    @property
    def is_scaduto(self):
        """Controlla se il documento è scaduto"""
        if self.data_scadenza:
            return timezone.now().date() > self.data_scadenza
        return False


class VideoArtigiano(models.Model):
    """Video di presentazione e lavori dell'artigiano"""
    
    TIPO_VIDEO_CHOICES = [
        ('presentazione', 'Video di Presentazione'),
        ('lavoro_in_corso', 'Lavoro in Corso'),
        ('lavoro_completato', 'Lavoro Completato'),
        ('testimonial', 'Testimonial Cliente'),
        ('tutorial', 'Tutorial/Dimostrazione'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='video',
        verbose_name='Artigiano'
    )
    titolo = models.CharField(
        max_length=200,
        verbose_name='Titolo Video'
    )
    descrizione = models.TextField(
        blank=True,
        verbose_name='Descrizione'
    )
    tipo_video = models.CharField(
        max_length=20,
        choices=TIPO_VIDEO_CHOICES,
        default='presentazione',
        verbose_name='Tipo Video'
    )
    file_video = models.FileField(
        upload_to='artigiani/video/',
        verbose_name='File Video',
        help_text='Formati supportati: MP4, AVI, MOV (max 100MB)'
    )
    miniatura = models.ImageField(
        upload_to='artigiani/miniature/',
        blank=True,
        verbose_name='Miniatura Video'
    )
    durata = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Durata (secondi)'
    )
    in_evidenza = models.BooleanField(
        default=False,
        verbose_name='In Evidenza'
    )
    pubblico = models.BooleanField(
        default=True,
        verbose_name='Pubblico nel Profilo'
    )
    data_caricamento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Caricamento'
    )
    visualizzazioni = models.IntegerField(
        default=0,
        verbose_name='Visualizzazioni'
    )
    
    class Meta:
        verbose_name = 'Video Artigiano'
        verbose_name_plural = 'Video Artigiani'
        ordering = ['-in_evidenza', '-data_caricamento']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.titolo}"


class CertificazioneArtigiano(models.Model):
    """Certificazioni e badge dell'artigiano"""
    
    TIPO_CERTIFICAZIONE_CHOICES = [
        ('identita_verificata', 'Identità Verificata'),
        ('documenti_verificati', 'Documenti Verificati'),
        ('competenze_verificate', 'Competenze Verificate'),
        ('assicurazione_attiva', 'Assicurazione Attiva'),
        ('recensioni_positive', 'Recensioni Positive'),
        ('lavori_completati', 'Lavori Completati'),
        ('risposta_rapida', 'Risposta Rapida'),
        ('prezzo_trasparente', 'Prezzo Trasparente'),
        ('professionista_premium', 'Professionista Premium'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='certificazioni',
        verbose_name='Artigiano'
    )
    tipo_certificazione = models.CharField(
        max_length=30,
        choices=TIPO_CERTIFICAZIONE_CHOICES,
        verbose_name='Tipo Certificazione'
    )
    attiva = models.BooleanField(
        default=True,
        verbose_name='Certificazione Attiva'
    )
    data_ottenimento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Ottenimento'
    )
    data_scadenza = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data Scadenza'
    )
    punteggio = models.IntegerField(
        default=10,
        verbose_name='Punteggio Badge'
    )
    descrizione = models.TextField(
        blank=True,
        verbose_name='Descrizione Certificazione'
    )
    
    class Meta:
        verbose_name = 'Certificazione Artigiano'
        verbose_name_plural = 'Certificazioni Artigiani'
        unique_together = ['artigiano', 'tipo_certificazione']
        ordering = ['-data_ottenimento']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.get_tipo_certificazione_display()}"
    
    @property
    def is_scaduta(self):
        """Controlla se la certificazione è scaduta"""
        if self.data_scadenza:
            return timezone.now().date() > self.data_scadenza
        return False


class MessaggioCliente(models.Model):
    """Messaggi inviati dai clienti agli artigiani"""
    
    STATO_MESSAGGIO_CHOICES = [
        ('nuovo', 'Nuovo'),
        ('letto', 'Letto'),
        ('risposto', 'Risposto'),
        ('archiviato', 'Archiviato'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='messaggi_ricevuti',
        verbose_name='Artigiano'
    )
    nome_cliente = models.CharField(
        max_length=100,
        verbose_name='Nome Cliente'
    )
    email_cliente = models.EmailField(
        verbose_name='Email Cliente'
    )
    telefono_cliente = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefono Cliente'
    )
    oggetto = models.CharField(
        max_length=200,
        verbose_name='Oggetto'
    )
    messaggio = models.TextField(
        verbose_name='Messaggio'
    )
    data_invio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Invio'
    )
    stato = models.CharField(
        max_length=15,
        choices=STATO_MESSAGGIO_CHOICES,
        default='nuovo',
        verbose_name='Stato Messaggio'
    )
    risposta = models.TextField(
        blank=True,
        verbose_name='Risposta'
    )
    data_risposta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data Risposta'
    )
    
    class Meta:
        verbose_name = 'Messaggio Cliente'
        verbose_name_plural = 'Messaggi Clienti'
        ordering = ['-data_invio']
    
    def __str__(self):
        return f"{self.nome_cliente} -> {self.artigiano.nome_attivita}: {self.oggetto}"


class SuggerimentoIA(models.Model):
    """Suggerimenti automatici generati dall'IA per migliorare il profilo"""
    
    TIPO_SUGGERIMENTO_CHOICES = [
        ('profilo_incompleto', 'Profilo Incompleto'),
        ('foto_mancanti', 'Foto Mancanti'),
        ('descrizione_migliorabile', 'Descrizione Migliorabile'),
        ('prezzi_non_competitivi', 'Prezzi Non Competitivi'),
        ('risposta_lenta', 'Risposta Lenta ai Clienti'),
        ('recensioni_negative', 'Recensioni Negative'),
        ('documenti_scaduti', 'Documenti Scaduti'),
        ('video_consigliato', 'Video Consigliato'),
        ('certificazione_mancante', 'Certificazione Mancante'),
        ('zona_espansione', 'Zona di Espansione'),
    ]
    
    PRIORITA_CHOICES = [
        ('bassa', 'Bassa'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Critica'),
    ]
    
    artigiano = models.ForeignKey(
        ProfiloArtigiano,
        on_delete=models.CASCADE,
        related_name='suggerimenti_ia',
        verbose_name='Artigiano'
    )
    tipo_suggerimento = models.CharField(
        max_length=30,
        choices=TIPO_SUGGERIMENTO_CHOICES,
        verbose_name='Tipo Suggerimento'
    )
    titolo = models.CharField(
        max_length=200,
        verbose_name='Titolo Suggerimento'
    )
    descrizione = models.TextField(
        verbose_name='Descrizione Suggerimento'
    )
    azione_consigliata = models.TextField(
        verbose_name='Azione Consigliata'
    )
    priorita = models.CharField(
        max_length=10,
        choices=PRIORITA_CHOICES,
        default='media',
        verbose_name='Priorità'
    )
    data_creazione = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Creazione'
    )
    letto = models.BooleanField(
        default=False,
        verbose_name='Letto'
    )
    applicato = models.BooleanField(
        default=False,
        verbose_name='Applicato'
    )
    data_applicazione = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data Applicazione'
    )
    
    class Meta:
        verbose_name = 'Suggerimento IA'
        verbose_name_plural = 'Suggerimenti IA'
        ordering = ['-priorita', '-data_creazione']
    
    def __str__(self):
        return f"{self.artigiano.nome_attivita} - {self.titolo}"
