import simpy
import try1_zon_opbrengst_model as zon_model
# experiment 1 : producer consumer voor HTES
# door : Edwin van den Oetelaar
# datum : 7 maart 2026

class EnergieSysteem:
    def __init__(self, env, capaciteit, initiele_lading):
        self.env = env
        # De 'Container' dwingt de wet van behoud van energie af (vol=vol, leeg=leeg)
        # https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#containers

        self.batterij = simpy.Container(env, capacity=capaciteit, init=initiele_lading)
        self.balans_log = []

    def log_status(self, actie):
        print(f"[{self.env.now:7.2f}] {actie:15} | Batterij: {self.batterij.level:7.2f} kWh")

# def bron_proces(env, systeem):
#     """Genereert energie in discrete tijdsblokken."""
#     while True:
#         # Een niet-triviale, geparameteriseerde functie voor opwekking
#         opwekking = 5.0 if (env.now % 24) < 12 else 0.0 
#         if opwekking > 0:
#             yield systeem.batterij.put(opwekking)
#             systeem.log_status("Zon schijnt")
#         yield env.timeout(1) # Check elk uur

def zonnepanelen_proces(env, systeem):
    """Genereert energie in discrete tijdsblokken."""
    """Gebaseerd op try1_zon_opbrengst_model.py"""

    Opgesteld_vermogen = 1000 # 1000 KWp max (1 MWp) vermogen bij volle zon

    while True:

        # Een niet-triviale functie voor opwekking
        dag = int(env.now // 24) + 1
        uur = env.now % 24
        opwekking = zon_model.zon_opbrengst_nl(dag, uur)

        if opwekking > 0:
            systeem.log_status("Zon schijnt dag %d uur %d aantal %d %%  " % (dag,uur,opwekking * 100))
            yield systeem.batterij.put(opwekking * Opgesteld_vermogen)
        else:
            systeem.log_status("Zon schijnt niet")
        
        yield env.timeout(1) # Check elk uur

def verbruiker_proces(env, systeem, setpoint_high, setpoint_low):
    """Verbruikt energie op basis van setpoints (Hysteresis controller)."""
    apparaat_aan = False
    while True:
# Containers allow you to retrieve their current 'level' as well as their 'capacity'
#  (see GasStation.monitor_tank() and tanker()).
#  You can also access the list of waiting events via the 
# 'put_queue' and 
# 'get_queue' attributes (similar to Resource.queue).

        niveau = systeem.batterij.level # level is in kWh
        
        # Logica op basis van setpoints (discrete functies)
        if niveau > setpoint_high and not apparaat_aan:
            apparaat_aan = True
            systeem.log_status("Setpoint AAN")
        elif niveau < setpoint_low and apparaat_aan:
            apparaat_aan = False
            systeem.log_status("Setpoint UIT")

        if apparaat_aan:
            verbruik = 3.0 # is in kWh
            # De energiebalans wordt hier direct bijgewerkt
            # als er voldoende energie in zit voor een uur, onttrekken we deze
            if systeem.batterij.level >= verbruik:
                yield systeem.batterij.get(verbruik)
            else:
                apparaat_aan = False
                systeem.log_status("FORCEER UIT (leeg)")
        
        yield env.timeout(1)
# Simulatie Setup
# 
# 
env = simpy.Environment()

mijn_systeem = EnergieSysteem(env, capaciteit=50.0, initiele_lading=10.0) # waarden in kWh
# Start de processen
# env.process(bron_proces(env, mijn_systeem))
env.process(zonnepanelen_proces(env, mijn_systeem))
env.process(verbruiker_proces(env, mijn_systeem, setpoint_high=25.0, setpoint_low=5.0))
# Run voor 48 uur
# We kunnen ook een simulator maken voor minuut resolutie, dan moeten wel alles aanpassen
env.run(until=48)