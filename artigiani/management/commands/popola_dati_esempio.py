from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from artigiani.models import (
    CategoriaArtigiano, ProfiloArtigiano, FotoLavoro, 
    RecensioneArtigiano, RichiestaPreventivo, RispostaPreventivo
)
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Popola il database con dati di esempio per artigiani'

    def handle(self, *args, **options):
        self.stdout.write('Inizio popolamento dati di esempio...')
        
        # Crea categorie
        categorie_data = [
            {'nome': 'Muratore', 'descrizione': 'Costruzione e ristrutturazione muraria', 'icona': 'fas fa-hammer'},
            {'nome': 'Idraulico', 'descrizione': 'Installazione e riparazione impianti idraulici', 'icona': 'fas fa-wrench'},
            {'nome': 'Elettricista', 'descrizione': 'Impianti elettrici e domotica', 'icona': 'fas fa-bolt'},
            {'nome': 'Pittore', 'descrizione': 'Tinteggiatura e decorazione', 'icona': 'fas fa-paint-roller'},
            {'nome': 'Falegname', 'descrizione': 'Mobili su misura e carpenteria', 'icona': 'fas fa-tools'},
            {'nome': 'Piastrellista', 'descrizione': 'Posa pavimenti e rivestimenti', 'icona': 'fas fa-th'},
            {'nome': 'Giardiniere', 'descrizione': 'Manutenzione giardini e spazi verdi', 'icona': 'fas fa-seedling'},
            {'nome': 'Infissi', 'descrizione': 'Installazione porte e finestre', 'icona': 'fas fa-door-open'},
        ]
        
        categorie = {}
        for cat_data in categorie_data:
            categoria, created = CategoriaArtigiano.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'descrizione': cat_data['descrizione'],
                    'icona': cat_data['icona']
                }
            )
            categorie[cat_data['nome']] = categoria
            if created:
                self.stdout.write(f'Categoria creata: {categoria.nome}')

        # Crea utenti e profili artigiani
        artigiani_data = [
            {
                'username': 'mario_muratore',
                'first_name': 'Mario',
                'last_name': 'Rossi',
                'email': 'mario.rossi@email.com',
                'categoria': 'Muratore',
                'nome_attivita': 'Edilizia Rossi',
                'citta': 'Milano',
                'cap': '20100',
                'telefono': '+39 333 1234567',
                'whatsapp': '+39 333 1234567',
                'descrizione': 'Muratore esperto con 15 anni di esperienza in ristrutturazioni e nuove costruzioni.',
                'prezzo_orario_min': '30.00',
                'prezzo_orario_max': '40.00',
                'anni_esperienza': 15,
                'inglese': True,
                'attivo': True,
            },
            {
                'username': 'giulia_idraulico',
                'first_name': 'Giulia',
                'last_name': 'Bianchi',
                'email': 'giulia.bianchi@email.com',
                'categoria': 'Idraulico',
                'nome_attivita': 'Idraulica Bianchi',
                'citta': 'Roma',
                'cap': '00100',
                'telefono': '+39 347 9876543',
                'whatsapp': '+39 347 9876543',
                'descrizione': 'Idraulico specializzato in caldaie e sistemi di riscaldamento moderni.',
                'prezzo_orario_min': '35.00',
                'prezzo_orario_max': '45.00',
                'anni_esperienza': 8,
                'francese': True,
                'attivo': True,
            },
            {
                'username': 'luca_elettricista',
                'first_name': 'Luca',
                'last_name': 'Verdi',
                'email': 'luca.verdi@email.com',
                'categoria': 'Elettricista',
                'nome_attivita': 'Elettro Verdi',
                'citta': 'Torino',
                'cap': '10100',
                'telefono': '+39 329 5555555',
                'whatsapp': '+39 329 5555555',
                'descrizione': 'Elettricista certificato, specialista in domotica e impianti smart home.',
                'prezzo_orario_min': '40.00',
                'prezzo_orario_max': '50.00',
                'anni_esperienza': 12,
                'inglese': True,
                'altre_lingue': 'Tedesco',
                'attivo': True,
            },
            {
                'username': 'anna_pittore',
                'first_name': 'Anna',
                'last_name': 'Neri',
                'email': 'anna.neri@email.com',
                'categoria': 'Pittore',
                'nome_attivita': 'Decorazioni Neri',
                'citta': 'Napoli',
                'cap': '80100',
                'telefono': '+39 338 7777777',
                'whatsapp': '+39 338 7777777',
                'descrizione': 'Pittore decoratore con specializzazione in tecniche antiche e moderne.',
                'prezzo_orario_min': '25.00',
                'prezzo_orario_max': '35.00',
                'anni_esperienza': 10,
                'altre_lingue': 'Spagnolo',
                'attivo': True,
            },
            {
                'username': 'francesco_falegname',
                'first_name': 'Francesco',
                'last_name': 'Bruno',
                'email': 'francesco.bruno@email.com',
                'categoria': 'Falegname',
                'nome_attivita': 'Falegnameria Bruno',
                'citta': 'Firenze',
                'cap': '50100',
                'telefono': '+39 349 3333333',
                'whatsapp': '+39 349 3333333',
                'descrizione': 'Falegname artigiano specializzato in mobili su misura e restauro.',
                'prezzo_orario_min': '45.00',
                'prezzo_orario_max': '55.00',
                'anni_esperienza': 20,
                'attivo': True,
            },
            {
                'username': 'sara_piastrellista',
                'first_name': 'Sara',
                'last_name': 'Gialli',
                'email': 'sara.gialli@email.com',
                'categoria': 'Piastrellista',
                'nome_attivita': 'Pavimenti Gialli',
                'citta': 'Bologna',
                'cap': '40100',
                'telefono': '+39 366 4444444',
                'whatsapp': '+39 366 4444444',
                'descrizione': 'Piastrellista esperta in pavimenti e rivestimenti di design.',
                'prezzo_orario_min': '35.00',
                'prezzo_orario_max': '45.00',
                'anni_esperienza': 7,
                'inglese': True,
                'attivo': True,
            },
        ]

        profili_creati = []
        for art_data in artigiani_data:
            # Crea utente
            user, created = User.objects.get_or_create(
                username=art_data['username'],
                defaults={
                    'first_name': art_data['first_name'],
                    'last_name': art_data['last_name'],
                    'email': art_data['email'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
            # Crea profilo artigiano
            profilo, created = ProfiloArtigiano.objects.get_or_create(
                utente=user,
                defaults={
                    'categoria_principale': categorie[art_data['categoria']],
                    'nome_attivita': art_data['nome_attivita'],
                    'citta': art_data['citta'],
                    'cap': art_data['cap'],
                    'telefono': art_data['telefono'],
                    'whatsapp': art_data['whatsapp'],
                    'descrizione': art_data['descrizione'],
                    'prezzo_orario_min': Decimal(art_data['prezzo_orario_min']),
                    'prezzo_orario_max': Decimal(art_data['prezzo_orario_max']),
                    'anni_esperienza': art_data['anni_esperienza'],
                    'inglese': art_data.get('inglese', False),
                    'francese': art_data.get('francese', False),
                    'altre_lingue': art_data.get('altre_lingue', ''),
                    'attivo': art_data['attivo'],
                    'verificato': True,
                    'numero_lavori_completati': random.randint(10, 100),
                }
            )
            
            if created:
                profili_creati.append(profilo)
                self.stdout.write(f'Profilo artigiano creato: {profilo.utente.get_full_name()}')

        # Crea recensioni per gli artigiani
        recensioni_esempio = [
            {'voto': 5, 'titolo': 'Ottimo lavoro!', 'commento': 'Lavoro eccellente, professionale e puntuale. Altamente raccomandato!'},
            {'voto': 4, 'titolo': 'Buon servizio', 'commento': 'Buon lavoro, piccoli ritardi ma risultato soddisfacente.'},
            {'voto': 5, 'titolo': 'Perfetto!', 'commento': 'Perfetto! Ha risolto il problema rapidamente e con competenza.'},
            {'voto': 4, 'titolo': 'Raccomandato', 'commento': 'Bravo artigiano, prezzo onesto e lavoro ben fatto.'},
            {'voto': 5, 'titolo': 'Molto soddisfatto', 'commento': 'Molto soddisfatto del risultato. Tornerò sicuramente da lui.'},
            {'voto': 3, 'titolo': 'Discreto', 'commento': 'Lavoro discreto, ma potrebbero migliorare i tempi.'},
            {'voto': 5, 'titolo': 'Eccezionale!', 'commento': 'Eccezionale! Attenzione ai dettagli e grande professionalità.'},
            {'voto': 4, 'titolo': 'Consigliato', 'commento': 'Consigliato. Buon rapporto qualità-prezzo.'},
        ]

        for profilo in profili_creati:
            # Crea 2-4 recensioni per ogni artigiano
            num_recensioni = random.randint(2, 4)
            for i in range(num_recensioni):
                recensione_data = random.choice(recensioni_esempio)
                
                # Crea un cliente fittizio per la recensione
                cliente_nome = random.choice(['Marco Russo', 'Laura Ferrari', 'Andrea Esposito', 'Chiara Bianchi', 'Roberto Romano'])
                cliente_email = f'cliente_{profilo.id}_{i}@email.com'
                
                RecensioneArtigiano.objects.create(
                    artigiano=profilo,
                    cliente_nome=cliente_nome,
                    cliente_email=cliente_email,
                    voto=recensione_data['voto'],
                    titolo=recensione_data['titolo'],
                    commento=recensione_data['commento'],
                    qualita_lavoro=recensione_data['voto'],
                    puntualita=random.randint(3, 5),
                    cortesia=random.randint(4, 5),
                    rapporto_qualita_prezzo=random.randint(3, 5),
                    verificata=True,
                    data_recensione=timezone.now() - timedelta(days=random.randint(1, 365))
                )

        # Crea alcune richieste di preventivo di esempio
        for i in range(5):
            cliente_nome = random.choice(['Paolo Conti', 'Elena Marino', 'Davide Greco', 'Simona Bruno', 'Matteo Galli'])
            cliente_email = f'cliente_preventivo_{i}@email.com'
            cliente_telefono = f'+39 3{random.randint(10, 99)} {random.randint(1000000, 9999999)}'
            
            categoria_random = random.choice(list(categorie.values()))
            richiesta = RichiestaPreventivo.objects.create(
                cliente_nome=cliente_nome,
                cliente_email=cliente_email,
                cliente_telefono=cliente_telefono,
                categoria=categoria_random,
                titolo=f'Lavoro di {categoria_random.nome.lower()}',
                descrizione=f'Richiesta preventivo per lavori di {categoria_random.nome.lower()} in casa.',
                citta=random.choice(['Milano', 'Roma', 'Napoli', 'Torino', 'Bologna']),
                cap=random.choice(['20100', '00100', '80100', '10100', '40100']),
                budget_max=Decimal(random.randint(500, 5000)),
                urgenza='media'
            )

        # Crea alcune foto lavori di esempio per alcuni artigiani
        foto_esempi = [
            {'titolo': 'Ristrutturazione bagno moderno', 'descrizione': 'Bagno completamente rinnovato con materiali di qualità'},
            {'titolo': 'Cucina su misura', 'descrizione': 'Cucina realizzata su misura con legno massello'},
            {'titolo': 'Impianto elettrico casa', 'descrizione': 'Rifacimento completo impianto elettrico'},
            {'titolo': 'Tinteggiatura appartamento', 'descrizione': 'Tinteggiatura pareti con pitture ecologiche'},
            {'titolo': 'Pavimentazione terrazza', 'descrizione': 'Posa nuova pavimentazione esterna'},
            {'titolo': 'Mobili restaurati', 'descrizione': 'Restauro mobili antichi con tecniche tradizionali'},
        ]
        
        for i, profilo in enumerate(profili_creati[:3]):  # Solo per i primi 3 artigiani
            for j in range(2):  # 2 foto per artigiano
                foto_data = foto_esempi[(i * 2 + j) % len(foto_esempi)]
                FotoLavoro.objects.create(
                    artigiano=profilo,
                    titolo=foto_data['titolo'],
                    descrizione=foto_data['descrizione'],
                    categoria=profilo.categoria_principale,
                    in_evidenza=j == 0,  # Prima foto in evidenza
                    ordine=j
                )

        self.stdout.write(self.style.SUCCESS('✓ Dati di esempio popolati con successo!'))
        self.stdout.write(f'✓ Categorie create: {len(categorie)}')
        self.stdout.write(f'✓ Artigiani creati: {len(profili_creati)}')
        self.stdout.write('✓ Recensioni e richieste preventivo create')
        self.stdout.write('\nCredenziali di accesso artigiani:')
        self.stdout.write('Username: mario_muratore, giulia_idraulico, luca_elettricista, anna_pittore, francesco_falegname, sara_piastrellista')
        self.stdout.write('Password: password123')
