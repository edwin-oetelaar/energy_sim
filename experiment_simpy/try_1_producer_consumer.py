import simpy
import math
from dataclasses import dataclass, field
from typing import Callable, List, Dict

import matplotlib.pyplot as plt
import production_v1 as zon_model
import consumption_v1 as verbruik_model
from batterij_sim_v1 import Battery

# Experiment 1 : Producer-consumer voor HTES
# Door : Edwin van den Oetelaar
# Datum : 7 maart 2026

# class EnergieSysteem:
#     """Vertegenwoordigt het energiesysteem inclusief de thuisbatterij en meetpunten."""
#     def __init__(self, env, capaciteit, initiele_lading):
#         self.env = env
#         # De 'Container' dwingt de wet van behoud van energie af (vol=vol, leeg=leeg)
#         # https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#containers
#         self.batterij = simpy.Container(env, capacity=capaciteit, init=initiele_lading)
        
#         # Lijsten om historische gegevens (per uur) bij te houden voor de grafiek
#         self.tijd_log = []
#         self.opwekking_log = []
#         self.verbruik_log = []
#         self.batterij_log = []
#         self.net_levering_log = [] # Hoeveel we terugleveren aan het net
#         self.net_afname_log = []   # Hoeveel we uit het net halen

#     def log_status(self, actie):
#         """Hulpfunctie om statusmeldingen met tijdstempel in de console te printen."""
#         print(f"[{self.env.now:7.2f}] {actie:15} | Batterij: {self.batterij.level:7.2f} kWh")


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


@dataclass
class EnergySystem:
    env: simpy.Environment
    battery: Battery
    load_profile: Callable[[int, float], float]   # functie van (dag, uur) -> kW
    pv_profile: Callable[[int, float], float]     # functie van (dag, uur) -> kW
    dt_minutes: int = 15

    history: List[Dict] = field(default_factory=list)

    def step(self):
        t_h = self.env.now / 60.0
        dt_h = self.dt_minutes / 60.0

        dag = int(t_h // 24) + 1
        uur = t_h % 24

        load_kw = self.load_profile(dag, uur)
        pv_kw = self.pv_profile(dag, uur)

        surplus_kw = pv_kw - load_kw

        batt_charge_kw = 0.0
        batt_discharge_kw = 0.0
        grid_import_kw = 0.0
        grid_export_kw = 0.0

        if surplus_kw > 0:
            # Eerst batterij laden
            batt_charge_kw = self.battery.charge(surplus_kw, dt_h)
            grid_export_kw = surplus_kw - batt_charge_kw

        else:
            deficit_kw = -surplus_kw
            # Eerst batterij ontladen
            batt_discharge_kw = self.battery.discharge(deficit_kw, dt_h)
            grid_import_kw = deficit_kw - batt_discharge_kw

        self.history.append({
            "time_h": t_h,
            "load_kw": load_kw,
            "pv_kw": pv_kw,
            "soc_kwh": self.battery.soc_kwh,
            "batt_charge_kw": batt_charge_kw,
            "batt_discharge_kw": batt_discharge_kw,
            "grid_import_kw": grid_import_kw,
            "grid_export_kw": grid_export_kw,
        })

    def run(self, duration_hours: float):
        n_steps = int(duration_hours * 60 / self.dt_minutes)
        for _ in range(n_steps):
            self.step()
            yield self.env.timeout(self.dt_minutes)

# ==============================================================================
# Simulatie Startpunt
# ==============================================================================

def load_profile(dag: int, uur: float) -> float:
    return verbruik_model.stroom_verbruik_woning(dag, uur)

def pv_profile(dag: int, uur: float) -> float:
    # 20 kWp maximaal PV vermogen bij volle zon
    Opgesteld_vermogen = 20 
    
    fractie = zon_model.zon_opbrengst_nl(dag, uur)
    return fractie * Opgesteld_vermogen


if __name__ == "__main__":
    # Simpy omgeving configureren
    env = simpy.Environment()

    battery = Battery(
        capacity_kwh=10.0,
        max_charge_kw=4.0,
        max_discharge_kw=4.0,
        eta_charge=0.95,
        eta_discharge=0.95,
        soc_kwh=5.0
    )

    system = EnergySystem(
        env=env,
        battery=battery,
        load_profile=load_profile,
        pv_profile=pv_profile,
        dt_minutes=15
    )

    env.process(system.run(duration_hours=48))
    env.run()  
 
    import pandas as pd
    
    # ==============================================================================
    # Resultaten Plotten
    # ==============================================================================
    print("Genereren van de grafiek...")
    
    # Converteer geschiedenis naar pandas DataFrame voor makkelijk plotten
    df = pd.DataFrame(system.history)
    
    plt.figure(figsize=(14, 8))
    
    # Plot opwekking en verbruik in lijngrafieken
    plt.plot(df["time_h"], df["pv_kw"], label='Opwekking (PV) [kW]', color='green', marker='o', markersize=3)
    plt.plot(df["time_h"], df["load_kw"], label='Verbruik (Huis) [kW]', color='red', marker='x', markersize=3)
    
    # Plot het batterijniveau als een stippellijn
    plt.plot(df["time_h"], df["soc_kwh"], label='Batterij SoC [kWh]', color='blue', linestyle='--', linewidth=2)
    
    # Voeg opladen/ontladen en netstromen toe
    plt.plot(df["time_h"], df["batt_charge_kw"], label='Batterij Laadt [kW]', color='cyan', linestyle=':', linewidth=1.5)
    plt.plot(df["time_h"], df["batt_discharge_kw"], label='Batterij Ontlaadt [kW]', color='purple', linestyle=':', linewidth=1.5)
    plt.plot(df["time_h"], df["grid_import_kw"], label='Net Import (Koop) [kW]', color='orange', linestyle='-', linewidth=1.5)
    plt.plot(df["time_h"], df["grid_export_kw"], label='Net Export (Verkoop) [kW]', color='pink', linestyle='-', linewidth=1.5)
    
    # Opmaak
    plt.title('Simulatie: Energie Opwekking vs. Verbruik vs. Batterij over 48 Uur')
    plt.xlabel('Tijd (Uren vanaf start)')
    plt.ylabel('Energie (kWh of kW)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Bestand opslaan
    output_filename = 'simulatie_resultaat.png'
    plt.savefig(output_filename)
    print(f"Grafiek is succesvol opgeslagen als '{output_filename}' in de huidige map.")