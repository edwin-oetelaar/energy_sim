import simpy
import matplotlib.pyplot as plt
import try1_zon_opbrengst_model as zon_model
import try2_verbruik_model as verbruik_model

# Experiment 1 : Producer-consumer voor HTES
# Door : Edwin van den Oetelaar
# Datum : 7 maart 2026

class EnergieSysteem:
    """Vertegenwoordigt het energiesysteem inclusief de thuisbatterij en meetpunten."""
    def __init__(self, env, capaciteit, initiele_lading):
        self.env = env
        # De 'Container' dwingt de wet van behoud van energie af (vol=vol, leeg=leeg)
        # https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#containers
        self.batterij = simpy.Container(env, capacity=capaciteit, init=initiele_lading)
        
        # Lijsten om historische gegevens (per uur) bij te houden voor de grafiek
        self.tijd_log = []
        self.opwekking_log = []
        self.verbruik_log = []
        self.batterij_log = []
        self.net_levering_log = [] # Hoeveel we terugleveren aan het net
        self.net_afname_log = []   # Hoeveel we uit het net halen

    def log_status(self, actie):
        """Hulpfunctie om statusmeldingen met tijdstempel in de console te printen."""
        print(f"[{self.env.now:7.2f}] {actie:15} | Batterij: {self.batterij.level:7.2f} kWh")


def zonnepanelen_proces(env, systeem):
    """Genereert energie (opwekking) op basis van het zonnemodel en stopt dit in de batterij."""
    # 20 kWp maximaal PV vermogen bij volle zon
    Opgesteld_vermogen = 20 

    while True:
        dag = int(env.now // 24) + 1
        uur = env.now % 24
        
        # Ophalen van de relatieve opbrengst (0.0 tot 1.0) via het model
        fractie = zon_model.zon_opbrengst_nl(dag, uur)
        opwekking = fractie * Opgesteld_vermogen

        if opwekking > 0:
            systeem.log_status(f"Zon (Opwek: {opwekking:.2f}kW)")
            
            # Bereken de actuele beschikbare ruimte in de batterij
            vrije_ruimte = systeem.batterij.capacity - systeem.batterij.level
            te_laden = min(opwekking, vrije_ruimte)
            
            # Stop stroom in de batterij (mits er plek is)
            if te_laden > 0:
                yield systeem.batterij.put(te_laden)
                
            # Rest van de stroom wordt afgekeurd of teruggeleverd aan het net
            overschot = opwekking - te_laden
            # Registreren van levering aan netwerk voor de huidige simulatiestap (optioneel)
        else:
            systeem.log_status("Zon schijnt niet")
        
        # Wacht een uur tot de volgende simulatie update
        yield env.timeout(1)


def verbruiker_proces(env, systeem):
    """Verbruikt energie (belasting) op basis van het huishoudelijk verbruiksmodel."""
    while True:
        dag = int(env.now // 24) + 1
        uur = env.now % 24
        
        # Bepaal het benodigde huishoudelijke verbruik in dit uur (in kWh)
        verbruik = verbruik_model.stroom_verbruik_woning(uur)
        niveau = systeem.batterij.level
        
        # We proberen de elektriciteit primair uit de batterij te halen
        if niveau >= verbruik:
            # Batterij heeft voldoende capaciteit voor het verbruik van dit uur
            if verbruik > 0:
                yield systeem.batterij.get(verbruik)
        else:
            # Batterij heeft te weinig stroom, we halen hem helemaal leeg
            # De rest van de stroom kopen we bij het lichtnet.
            if niveau > 0:
                yield systeem.batterij.get(niveau)
            else:
                # Batterij is al leeg, we vragen 0 uit de container.
                # Dit doen we via timeout(0) in plaats van get(0) om ValueError van Simpy te vermijden
                yield env.timeout(0) 
                
        # Wacht een uur tot de volgende update
        yield env.timeout(1)


def monitor_proces(env, systeem):
    """Meet elk uur de status van het systeem en bewaart de waarden om later te kunnen plotten."""
    Opgesteld_vermogen = 20
    
    while True:
        dag = int(env.now // 24) + 1
        uur = env.now % 24
        
        # Bereken opwekking en verbruik op dit tijdstip met de modellen
        fractie = zon_model.zon_opbrengst_nl(dag, uur)
        opwekking = fractie * Opgesteld_vermogen
        verbruik = verbruik_model.stroom_verbruik_woning(uur)
        
        # Sla alle datapunten op
        systeem.tijd_log.append(env.now)
        systeem.opwekking_log.append(opwekking)
        systeem.verbruik_log.append(verbruik)
        systeem.batterij_log.append(systeem.batterij.level)
        
        # Wacht een uur tot de volgende meting
        yield env.timeout(1)


# ==============================================================================
# Simulatie Startpunt
# ==============================================================================
if __name__ == "__main__":
    # Simpy omgeving configureren
    env = simpy.Environment()
    
    # Maak systeem aan: Capaciteit van 10.0 kWh met initieel 5.0 kWh in de batterij
    mijn_systeem = EnergieSysteem(env, capaciteit=10.0, initiele_lading=5.0)
    
    # Koppel de processen (actoren) aan de omgeving
    env.process(zonnepanelen_proces(env, mijn_systeem))
    env.process(verbruiker_proces(env, mijn_systeem))
    env.process(monitor_proces(env, mijn_systeem))
    
    # Draai de simulatie voor een periode van 48 uur
    print("Start simulatie voor 48 uur...")
    env.run(until=48)
    print("Simulatie voltooid.")
    
    # ==============================================================================
    # Resultaten Plotten
    # ==============================================================================
    print("Genereren van de grafiek...")
    
    plt.figure(figsize=(12, 6))
    
    # Plot opwekking en verbruik in lijngrafieken
    plt.plot(mijn_systeem.tijd_log, mijn_systeem.opwekking_log, label='Opwekking (PV) [kW]', color='green', marker='o', markersize=4)
    plt.plot(mijn_systeem.tijd_log, mijn_systeem.verbruik_log, label='Verbruik (Huis) [kW]', color='red', marker='x', markersize=4)
    
    # Plot het batterijniveau als een stippellijn (dit is in kWh in plaats van de kW rates - 
    # omdat onze stapgrootte 1h is, zijn kW en kWh over het uur numeriek vrijwel uitwisselbaar in deze plot)
    plt.plot(mijn_systeem.tijd_log, mijn_systeem.batterij_log, label='Batterij Lading [kWh]', color='blue', linestyle='--', linewidth=2)
    
    # Opmaak
    plt.title('Simulatie: Energie Opwekking vs. Verbruik over 48 Uur')
    plt.xlabel('Tijd (Uren vanaf start)')
    plt.ylabel('Energie (kWh of kW)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Bestand opslaan
    output_filename = 'simulatie_resultaat.png'
    plt.savefig(output_filename)
    print(f"Grafiek is succesvol opgeslagen als '{output_filename}' in de huidige map.")