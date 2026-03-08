# ongevalideerde formule
# lijkt te werken, 's morgens vroeg en 's avonds laat is de opbrengst 0
# in de winter is de opbrengst lager dan in de zomer
# vibe code met gemini 7 maart 2026
# Edwin van den Oetelaar
# 
import math
from dataclasses import dataclass, field

def zon_opbrengst_nl(dag, uur):
    """
    Berekent genormaliseerde PV opbrengst voor Nederland.
    dag: 1-365
    uur: 0-24 (decimaal)
    return: 0.0 - 1.xx (Genormaliseerd t.o.v. 1 juni piek = 1.0)
    """
    # Constanten voor Nederland
    breedtegraad = 52.0
    piek_uur = 13.6  # Gemiddelde tijd zonnepiek (zomertijd)
    
    # Graden naar radialen conversie factor
    rad = math.pi / 180.0
    
    # 1. Declinatie (Seizoen)
    delta = 23.45 * math.sin(rad * (360/365) * (dag - 81))
    
    # 2. Uurhoek (Tijd van de dag)
    omega = (uur - piek_uur) * 15
    
    # 3. Zonnehoogte (Elevatie)
    # sin(alpha) = sin(lat)*sin(delta) + cos(lat)*cos(delta)*cos(omega)
    sin_alpha = (math.sin(rad * breedtegraad) * math.sin(rad * delta) + 
                 math.cos(rad * breedtegraad) * math.cos(rad * delta) * math.cos(rad * omega))
    
    # 4. Output (negatieve waarden zijn nacht -> 0)
    if sin_alpha <= 0:
        return 0.0
    
    # Normalisatie factor:
    # Op 1 juni (dag 152) is de max sin_alpha ca. 0.866 (60 graden). 
    # 1.0 / 0.866 = 1.154
    return 1.154 * sin_alpha

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Voorbeeld: 1 juni om 13:36
    print(f"Output 1 juni piek: {zon_opbrengst_nl(152, 13.6):.2f}") 
    # Output: 1.00
    print(f"Output 1 januari 12:00 : {zon_opbrengst_nl(1, 12.0):.2f}") 
    # Output: 0.24

    # Genereer data voor elke dag van het jaar om 12:00
    dagen = list(range(1, 366))
    opbrengsten_12_00 = [zon_opbrengst_nl(dag, 12.0) for dag in dagen]

    # Maak de plot
    plt.figure(figsize=(10, 6))
    plt.plot(dagen, opbrengsten_12_00, label='Zon opbrengst om 12:00', color='orange', linewidth=2)
    plt.title('Genormaliseerde zonne-opbrengst gedurende het jaar (om 12:00)')
    plt.xlabel('Dag van het jaar (1 - 365)')
    plt.ylabel('Genormaliseerde opbrengst (piek = 1.0)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()


