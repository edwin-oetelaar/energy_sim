# Theoretisch verbruiksprofiel huishouden
# Gebaseerd op de 'duck curve' / dubbele piek
# Edwin van den Oetelaar / Gemini
# 7 maart 2026

import math
from dataclasses import dataclass, field

# def load_profile(t_h: float) -> float:
#     """
#     Eenvoudig huishoudelijk verbruiksprofiel in kW.
#     t_h loopt door in uren vanaf simulatiestart.
#     """
#     hour = t_h % 24

#     base = 0.4
#     morning_peak = 1.2 if 7 <= hour < 9 else 0.0
#     evening_peak = 1.8 if 18 <= hour < 22 else 0.0

#     return base + morning_peak + evening_peak

def stroom_verbruik_woning(dag: int, uur: float)-> float:
    """
    Berekent het benaderde stroomverbruik van een gemiddelde woning in kW.
    De curve volgt een basislast met een kleine ochtendpiek en een grote avondpiek.
    
    dag: 1-365 (integer)
    uur: 0-24 (decimaal, bijv. 7.5 = 07:30)
    return: vermogen in kW
    """
    # 1. Basislast (altijd sluipverbruik, koelkast, etc.)
    # Laten we aannemen dat dit in de nacht zo'n 200 Watt (0.2 kW) is 
    # en overdag iets oploopt naar 300 Watt (0.3 kW)
    basis = 0.2 + 0.1 * math.sin(math.pi * (uur / 24))
    
    # 2. Ochtendpiek (opstaan, koffie, douchen, etc.)
    # Piek rond 07:30 (7.5 uur), breedte (sigma) ca. 1.5 uur, hoogte ca. 0.6 kW extra
    ochtend_piek = 0.6 * math.exp(-0.5 * ((uur - 7.5) / 1.5) ** 2)
    
    # 3. Avondpiek (koken, wassen, tv, verlichting)
    # Piek rond 19:30 (19.5 uur), breedte (sigma) ca. 2.5 uur, hoogte ca. 1.5 kW extra
    # Iets naar rechts verschoven t.o.v. de zonnepiek zoals in de schets
    avond_piek = 1.5 * math.exp(-0.5 * ((uur - 19.5) / 2.5) ** 2)
    
    # Totaal verbruik is de som van deze componenten
    totaal_kW = basis + ochtend_piek + avond_piek
    
    return totaal_kW

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    uren = [i / 10 for i in range(240)] # 0.0 tot 24.0 in stapjes van 0.1 uur
    verbruik = [stroom_verbruik_woning(1, u) for u in uren]
    
    # Print wat voorbeelden
    print(f"Verbruik 03:00 (Nacht)  : {stroom_verbruik_woning(1, 3.0):.2f} kW")
    print(f"Verbruik 07:30 (Ochtend): {stroom_verbruik_woning(1, 7.5):.2f} kW")
    print(f"Verbruik 19:30 (Avond)  : {stroom_verbruik_woning(1, 19.5):.2f} kW")

    # Plot de curve
    plt.figure(figsize=(10, 6))
    plt.plot(uren, verbruik, label='Huishoudelijk stroomverbruik', color='darkblue', linewidth=3)
    
    # Voeg visueel de assen en labels toe zoals in de schets
    plt.title('Gemodelleerd Stroomverbruik Woning (Dubbele Piek)')
    plt.xlabel('Tijdstip (0 - 24 uur)')
    plt.ylabel('Stroomverbruik (kW)')
    
    # Pas de x-as labels aan (4u, 8u, 12u, 16u, 20u)
    plt.xticks([0, 4, 8, 12, 16, 20, 24], ['0u', '4u', '8u', '12u', '16u', '20u', '24u'])
    
    # Horizontale lijn op 0 ter referentie
    plt.axhline(0, color='black', linewidth=1)
    
    # Maak de ruimte onder de curve rood/oranje om het inzichtelijk te maken (net als op de plaatjes links)
    plt.fill_between(uren, 0, verbruik, color='coral', alpha=0.3, label='Aankoop/Verbruik gebied')
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()
