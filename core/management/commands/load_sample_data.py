from django.core.management.base import BaseCommand
from core.models import CategoriaIntervento, PacchettoRistrutturazione, ElementoPacchetto


class Command(BaseCommand):
    help = 'Carica dati di esempio per RinnovoCasa'

    def handle(self, *args, **options):
        self.stdout.write('Creazione dati di esempio...')
        
        # Crea categorie
        categorie_data = [
            {
                'nome': 'Bagno Accessibile',
                'descrizione': 'Ristrutturazione bagni per anziani e disabili',
                'icona': 'fas fa-bath',
                'colore': '#007bff',
                'ordine': 1
            },
            {
                'nome': 'Isolamento Termico',
                'descrizione': 'Cappotto termico e isolamento energetico',
                'icona': 'fas fa-thermometer-half',
                'colore': '#28a745',
                'ordine': 2
            },
            {
                'nome': 'Fotovoltaico',
                'descrizione': 'Impianti solari e energie rinnovabili',
                'icona': 'fas fa-solar-panel',
                'colore': '#ffc107',
                'ordine': 3
            },
            {
                'nome': 'Ristrutturazione Completa',
                'descrizione': 'Interventi completi su tutto l\'immobile',
                'icona': 'fas fa-home',
                'colore': '#dc3545',
                'ordine': 4
            },
            {
                'nome': 'Cucina',
                'descrizione': 'Rinnovamento cucina e elettrodomestici',
                'icona': 'fas fa-utensils',
                'colore': '#6f42c1',
                'ordine': 5
            },
            {
                'nome': 'Infissi',
                'descrizione': 'Sostituzione porte e finestre',
                'icona': 'fas fa-door-open',
                'colore': '#20c997',
                'ordine': 6
            }
        ]
        
        categorie = {}
        for cat_data in categorie_data:
            categoria, created = CategoriaIntervento.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            categorie[categoria.nome] = categoria
            if created:
                self.stdout.write(f'  ✓ Categoria: {categoria.nome}')
        
        # Crea pacchetti
        pacchetti_data = [
            {
                'nome': 'Bagno Accessibile Base',
                'categoria': 'Bagno Accessibile',
                'descrizione_breve': 'Trasforma il tuo bagno per renderlo sicuro e accessibile agli anziani.',
                'descrizione_completa': 'Pacchetto completo per la ristrutturazione di un bagno esistente con elementi di sicurezza per anziani: doccia con sedile, maniglioni, pavimenti antiscivolo e sanitari rialzati.',
                'prezzo_min': 4800,
                'prezzo_max': 6000,
                'durata_giorni_min': 7,
                'durata_giorni_max': 10,
                'difficolta': 'media',
                'include_progetto': True,
                'include_pratiche': True,
                'include_bonus': True,
                'in_evidenza': True,
                'ordinamento': 1,
                'elementi': [
                    'Rimozione vasca esistente',
                    'Installazione doccia con sedile',
                    'Maniglioni di sicurezza',
                    'Pavimento antiscivolo',
                    'Sanitari rialzati',
                    'Illuminazione LED'
                ]
            },
            {
                'nome': 'Isolamento Termico Cappotto',
                'categoria': 'Isolamento Termico',
                'descrizione_breve': 'Cappotto termico esterno per ridurre i consumi energetici fino al 40%.',
                'descrizione_completa': 'Sistema di isolamento termico a cappotto per pareti esterne con materiali certificati, finitura di qualità e garanzia 10 anni.',
                'prezzo_min': 8500,
                'prezzo_max': 12000,
                'durata_giorni_min': 15,
                'durata_giorni_max': 25,
                'difficolta': 'media',
                'include_progetto': True,
                'include_pratiche': True,
                'include_bonus': True,
                'in_evidenza': True,
                'ordinamento': 2,
                'elementi': [
                    'Isolamento in EPS 10cm',
                    'Rasatura armata',
                    'Finitura al quarzo',
                    'Ponteggi inclusi',
                    'APE finale',
                    'Garanzia 10 anni'
                ]
            },
            {
                'nome': 'Impianto Fotovoltaico 6kW',
                'categoria': 'Fotovoltaico',
                'descrizione_breve': 'Impianto fotovoltaico completo con batterie per l\'indipendenza energetica.',
                'descrizione_completa': 'Sistema fotovoltaico da 6kW con inverter di ultima generazione, sistema di accumulo e monitoraggio via app.',
                'prezzo_min': 12000,
                'prezzo_max': 16000,
                'durata_giorni_min': 3,
                'durata_giorni_max': 5,
                'difficolta': 'media',
                'include_progetto': True,
                'include_pratiche': True,
                'include_bonus': True,
                'in_evidenza': True,
                'ordinamento': 3,
                'elementi': [
                    '20 pannelli da 300W',
                    'Inverter SolarEdge',
                    'Batteria da 10kWh',
                    'Sistema di monitoraggio',
                    'Pratiche GSE incluse',
                    'Garanzia 25 anni'
                ]
            },
            {
                'nome': 'Cucina Moderna Completa',
                'categoria': 'Cucina',
                'descrizione_breve': 'Cucina su misura con elettrodomestici di classe A+++.',
                'descrizione_completa': 'Progettazione e realizzazione cucina moderna con mobili su misura, top in quarzo e elettrodomestici di ultima generazione.',
                'prezzo_min': 7500,
                'prezzo_max': 15000,
                'durata_giorni_min': 10,
                'durata_giorni_max': 15,
                'difficolta': 'media',
                'include_progetto': True,
                'include_pratiche': False,
                'include_bonus': False,
                'in_evidenza': False,
                'ordinamento': 4,
                'elementi': [
                    'Mobili su misura',
                    'Top in quarzo',
                    'Elettrodomestici A+++',
                    'Illuminazione LED',
                    'Impianto elettrico',
                    'Piastrelle incluse'
                ]
            },
            {
                'nome': 'Infissi PVC Premium',
                'categoria': 'Infissi',
                'descrizione_breve': 'Sostituzione completa di finestre e porte con infissi ad alta efficienza.',
                'descrizione_completa': 'Infissi in PVC a taglio termico con vetrocamera basso emissiva, maniglie antiscasso e garanzia 10 anni.',
                'prezzo_min': 5500,
                'prezzo_max': 8500,
                'durata_giorni_min': 5,
                'durata_giorni_max': 8,
                'difficolta': 'facile',
                'include_progetto': False,
                'include_pratiche': True,
                'include_bonus': True,
                'in_evidenza': True,
                'ordinamento': 5,
                'elementi': [
                    'Infissi PVC 5 camere',
                    'Vetrocamera basso emissiva',
                    'Maniglie antiscasso',
                    'Soglie in alluminio',
                    'Smaltimento vecchi infissi',
                    'Certificazione CE'
                ]
            },
            {
                'nome': 'Casa Ecosostenibile 110%',
                'categoria': 'Ristrutturazione Completa',
                'descrizione_breve': 'Ristrutturazione completa con Superbonus 110% - costo zero per te!',
                'descrizione_completa': 'Pacchetto completo per ristrutturazione con miglioramento di 2 classi energetiche: cappotto, fotovoltaico, pompa di calore, infissi e sismabonus.',
                'prezzo_min': 80000,
                'prezzo_max': 120000,
                'durata_giorni_min': 60,
                'durata_giorni_max': 90,
                'difficolta': 'difficile',
                'include_progetto': True,
                'include_pratiche': True,
                'include_bonus': True,
                'in_evidenza': True,
                'ordinamento': 1,
                'elementi': [
                    'Cappotto termico completo',
                    'Fotovoltaico 6kW + batterie',
                    'Pompa di calore',
                    'Infissi completi',
                    'Interventi antisismici',
                    'Gestione Superbonus 110%'
                ]
            }
        ]
        
        for pacco_data in pacchetti_data:
            elementi = pacco_data.pop('elementi')
            categoria_nome = pacco_data.pop('categoria')
            pacco_data['categoria'] = categorie[categoria_nome]
            
            pacchetto, created = PacchettoRistrutturazione.objects.get_or_create(
                nome=pacco_data['nome'],
                defaults=pacco_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Pacchetto: {pacchetto.nome}')
                
                # Aggiungi elementi
                for i, elemento_nome in enumerate(elementi):
                    ElementoPacchetto.objects.create(
                        pacchetto=pacchetto,
                        nome=elemento_nome,
                        descrizione=f'Dettagli per {elemento_nome}',
                        incluso=True,
                        ordine=i+1
                    )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Dati di esempio creati con successo!')
        )
