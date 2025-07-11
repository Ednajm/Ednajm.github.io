# Generated by Django 5.2.3 on 2025-06-30 22:35

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artigiani', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appuntamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente_nome', models.CharField(max_length=100, verbose_name='Nome Cliente')),
                ('cliente_email', models.EmailField(max_length=254, verbose_name='Email Cliente')),
                ('cliente_telefono', models.CharField(max_length=20, verbose_name='Telefono Cliente')),
                ('titolo', models.CharField(max_length=200, verbose_name='Titolo Appuntamento')),
                ('descrizione', models.TextField(blank=True, verbose_name='Descrizione')),
                ('tipo_appuntamento', models.CharField(choices=[('sopralluogo', 'Sopralluogo'), ('preventivo', 'Preventivo'), ('lavoro', 'Esecuzione Lavoro'), ('consulenza', 'Consulenza'), ('riparazione', 'Riparazione'), ('manutenzione', 'Manutenzione')], default='sopralluogo', max_length=20, verbose_name='Tipo Appuntamento')),
                ('data_appuntamento', models.DateField(verbose_name='Data Appuntamento')),
                ('ora_inizio', models.TimeField(verbose_name='Ora Inizio')),
                ('ora_fine', models.TimeField(verbose_name='Ora Fine')),
                ('durata_stimata', models.IntegerField(default=60, help_text='Durata stimata in minuti (15-480)', validators=[django.core.validators.MinValueValidator(15), django.core.validators.MaxValueValidator(480)], verbose_name='Durata Stimata (minuti)')),
                ('indirizzo', models.CharField(max_length=300, verbose_name='Indirizzo')),
                ('citta', models.CharField(max_length=100, verbose_name='Città')),
                ('cap', models.CharField(max_length=10, verbose_name='CAP')),
                ('stato', models.CharField(choices=[('richiesto', 'Richiesto'), ('confermato', 'Confermato'), ('in_corso', 'In Corso'), ('completato', 'Completato'), ('annullato', 'Annullato'), ('rimandato', 'Rimandato')], default='richiesto', max_length=20, verbose_name='Stato')),
                ('costo_stimato', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Costo Stimato (€)')),
                ('note_artigiano', models.TextField(blank=True, help_text="Note private dell'artigiano", verbose_name='Note Artigiano')),
                ('note_cliente', models.TextField(blank=True, help_text='Richieste specifiche del cliente', verbose_name='Note Cliente')),
                ('data_creazione', models.DateTimeField(auto_now_add=True, verbose_name='Data Creazione')),
                ('data_modifica', models.DateTimeField(auto_now=True, verbose_name='Ultima Modifica')),
                ('promemoria_inviato', models.BooleanField(default=False, verbose_name='Promemoria Inviato')),
                ('conferma_cliente', models.BooleanField(default=False, verbose_name='Confermato dal Cliente')),
                ('artigiano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appuntamenti', to='artigiani.profiloartigiano', verbose_name='Artigiano')),
            ],
            options={
                'verbose_name': 'Appuntamento',
                'verbose_name_plural': 'Appuntamenti',
                'ordering': ['data_appuntamento', 'ora_inizio'],
            },
        ),
        migrations.CreateModel(
            name='EccezioneOrario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inizio', models.DateField(verbose_name='Data Inizio')),
                ('data_fine', models.DateField(verbose_name='Data Fine')),
                ('tipo', models.CharField(choices=[('chiusura', 'Giorno di Chiusura'), ('ferie', 'Ferie'), ('malattia', 'Malattia'), ('emergenza', 'Emergenza'), ('orario_speciale', 'Orario Speciale')], max_length=20, verbose_name='Tipo Eccezione')),
                ('descrizione', models.CharField(blank=True, max_length=200, verbose_name='Descrizione')),
                ('ora_inizio_speciale', models.TimeField(blank=True, null=True, verbose_name='Ora Inizio Speciale')),
                ('ora_fine_speciale', models.TimeField(blank=True, null=True, verbose_name='Ora Fine Speciale')),
                ('data_creazione', models.DateTimeField(auto_now_add=True)),
                ('artigiano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eccezioni_orario', to='artigiani.profiloartigiano', verbose_name='Artigiano')),
            ],
            options={
                'verbose_name': 'Eccezione Orario',
                'verbose_name_plural': 'Eccezioni Orario',
                'ordering': ['data_inizio'],
            },
        ),
        migrations.CreateModel(
            name='OrarioDisponibilita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('giorno_settimana', models.IntegerField(choices=[(0, 'Lunedì'), (1, 'Martedì'), (2, 'Mercoledì'), (3, 'Giovedì'), (4, 'Venerdì'), (5, 'Sabato'), (6, 'Domenica')], verbose_name='Giorno della Settimana')),
                ('attivo', models.BooleanField(default=True, verbose_name='Giorno Attivo')),
                ('ora_inizio_mattina', models.TimeField(blank=True, help_text='Es. 08:00', null=True, verbose_name='Inizio Mattina')),
                ('ora_fine_mattina', models.TimeField(blank=True, help_text='Es. 12:00', null=True, verbose_name='Fine Mattina')),
                ('ora_inizio_pomeriggio', models.TimeField(blank=True, help_text='Es. 14:00', null=True, verbose_name='Inizio Pomeriggio')),
                ('ora_fine_pomeriggio', models.TimeField(blank=True, help_text='Es. 18:00', null=True, verbose_name='Fine Pomeriggio')),
                ('pausa_pranzo', models.BooleanField(default=True, help_text='Pausa tra mattina e pomeriggio', verbose_name='Pausa Pranzo')),
                ('note', models.CharField(blank=True, help_text='Es. Solo emergenze, Disponibile su chiamata', max_length=200, verbose_name='Note')),
                ('artigiano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orari_disponibilita', to='artigiani.profiloartigiano', verbose_name='Artigiano')),
            ],
            options={
                'verbose_name': 'Orario Disponibilità',
                'verbose_name_plural': 'Orari Disponibilità',
                'ordering': ['giorno_settimana'],
                'unique_together': {('artigiano', 'giorno_settimana')},
            },
        ),
    ]
