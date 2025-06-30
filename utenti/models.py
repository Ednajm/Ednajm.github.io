from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """Modello utente personalizzato per RinnovoCasa"""
    
    USER_TYPE_CHOICES = [
        ('cliente', 'Cliente'),
        ('impresa', 'Impresa'),
        ('artigiano', 'Artigiano'),
        ('admin', 'Amministratore'),
    ]
    
    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPE_CHOICES,
        default='cliente',
        verbose_name='Tipo Utente'
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True,
        verbose_name='Telefono'
    )
    
    data_nascita = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data di Nascita'
    )
    
    indirizzo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Indirizzo'
    )
    
    citta = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Città'
    )
    
    cap = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        verbose_name='CAP'
    )
    
    provincia = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name='Provincia'
    )
    
    foto_profilo = models.ImageField(
        upload_to='profili/',
        blank=True,
        null=True,
        verbose_name='Foto Profilo'
    )
    
    accetta_marketing = models.BooleanField(
        default=False,
        verbose_name='Accetta comunicazioni marketing'
    )
    
    accetta_privacy = models.BooleanField(
        default=True,
        verbose_name='Accetta privacy policy'
    )
    
    data_registrazione = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data Registrazione'
    )
    
    ultimo_accesso_dashboard = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Ultimo Accesso Dashboard'
    )
    
    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def nome_completo(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def indirizzo_completo(self):
        parts = [self.indirizzo, self.citta, self.cap, self.provincia]
        return ", ".join([part for part in parts if part])


class ProfiloCliente(models.Model):
    """Profilo esteso per i clienti"""
    
    TIPO_IMMOBILE_CHOICES = [
        ('appartamento', 'Appartamento'),
        ('villa', 'Villa'),
        ('villetta', 'Villetta a schiera'),
        ('ufficio', 'Ufficio'),
        ('negozio', 'Negozio'),
        ('altro', 'Altro'),
    ]
    
    PROPRIETA_CHOICES = [
        ('proprietario', 'Proprietario'),
        ('affittuario', 'Affittuario'),
        ('usufruttuario', 'Usufruttuario'),
        ('altro', 'Altro'),
    ]
    
    utente = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profilo_cliente'
    )
    
    tipo_immobile = models.CharField(
        max_length=20,
        choices=TIPO_IMMOBILE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo Immobile'
    )
    
    proprieta = models.CharField(
        max_length=20,
        choices=PROPRIETA_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo di Proprietà'
    )
    
    anno_costruzione = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Anno di Costruzione'
    )
    
    superficie_mq = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Superficie (mq)'
    )
    
    numero_vani = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Numero Vani'
    )
    
    piano = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Piano'
    )
    
    ascensore = models.BooleanField(
        default=False,
        verbose_name='Presenza Ascensore'
    )
    
    giardino = models.BooleanField(
        default=False,
        verbose_name='Presenza Giardino'
    )
    
    terrazza = models.BooleanField(
        default=False,
        verbose_name='Presenza Terrazza'
    )
    
    garage = models.BooleanField(
        default=False,
        verbose_name='Presenza Garage'
    )
    
    note_aggiuntive = models.TextField(
        blank=True,
        null=True,
        verbose_name='Note Aggiuntive'
    )
    
    class Meta:
        verbose_name = 'Profilo Cliente'
        verbose_name_plural = 'Profili Clienti'
        
    def __str__(self):
        return f"Profilo di {self.utente.nome_completo}"


class ProfiloImpresa(models.Model):
    """Profilo esteso per le imprese"""
    
    TIPO_IMPRESA_CHOICES = [
        ('edile', 'Impresa Edile'),
        ('elettrica', 'Impresa Elettrica'),
        ('idraulica', 'Impresa Idraulica'),
        ('termoidraulica', 'Termoidraulica'),
        ('infissi', 'Infissi e Serramenti'),
        ('pavimenti', 'Pavimenti e Rivestimenti'),
        ('pitture', 'Pitture e Decorazioni'),
        ('isolamento', 'Isolamento Termico'),
        ('fotovoltaico', 'Fotovoltaico'),
        ('generale', 'Impresa Generale'),
        ('altro', 'Altro'),
    ]
    
    utente = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profilo_impresa'
    )
    
    ragione_sociale = models.CharField(
        max_length=200,
        verbose_name='Ragione Sociale'
    )
    
    partita_iva = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='Partita IVA'
    )
    
    codice_fiscale = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name='Codice Fiscale'
    )
    
    tipo_impresa = models.CharField(
        max_length=20,
        choices=TIPO_IMPRESA_CHOICES,
        verbose_name='Tipo Impresa'
    )
    
    descrizione = models.TextField(
        verbose_name='Descrizione Azienda'
    )
    
    anno_fondazione = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Anno Fondazione'
    )
    
    numero_dipendenti = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Numero Dipendenti'
    )
    
    sito_web = models.URLField(
        blank=True,
        null=True,
        verbose_name='Sito Web'
    )
    
    certificazioni = models.TextField(
        blank=True,
        null=True,
        verbose_name='Certificazioni'
    )
    
    zone_operative = models.TextField(
        help_text='Inserire le province o regioni dove opera l\'impresa',
        verbose_name='Zone Operative'
    )
    
    abilitato = models.BooleanField(
        default=False,
        verbose_name='Impresa Verificata'
    )
    
    data_verifica = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data Verifica'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='Rating Medio'
    )
    
    numero_recensioni = models.IntegerField(
        default=0,
        verbose_name='Numero Recensioni'
    )
    
    class Meta:
        verbose_name = 'Profilo Impresa'
        verbose_name_plural = 'Profili Imprese'
        
    def __str__(self):
        return f"{self.ragione_sociale} - {self.get_tipo_impresa_display()}"
