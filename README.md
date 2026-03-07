# Projectoverzicht – Discrete Event Simulatie voor een Energy Digital Twin

**Door Edwin van den Oetelaar (zaterdagproject)**  
**Doelgroep:** collega engineers en researchers (HBO praktijkgericht onderzoek)

- **Lectoraat High Tech Embedded Software**
- *We do applied research on smart systems*

Zie ook [High Tech Embedded Software](https://hightechembeddedsoftware.nl/) 
En ook [nationaal energie dashboard](https://ned.nl/nl/datacatalogus)

---

## 1. Managementsamenvatting
Dit project verkent hoe een **digitale twin** van een integraal energiesysteem kan worden opgezet met focus op:
- zonne-energie (PV),
- warmteketen,
- CO2-naar-methaan conversie (power-to-gas),
- energieopslag,
- en netkoppeling.

De centrale keuze is om te starten met **discrete event simulatie (DES)** in plaats van uitsluitend continue differentiaalmodellen. De verwachting is dat DES in deze fase:
- eenvoudiger te implementeren en uit te leggen is,
- beter controleerbaar en valideerbaar is,
- flexibel genoeg is voor niet-lineaire bedrijfslogica en setpoints,
- en goed aansluit op onderwijs- en onderzoeksdoelen.

Er is reeds een eerste demo gemaakt met **SimPy** (zonnepanelen + verbruiker + batterijbuffer), als proof-of-concept van event-driven energiebalansmodellering.

---

## 2. Aanleiding en context
Voor nieuwe energiesystemen met meerdere subsystemen is het lastig om vroeg in het ontwerptraject snel te testen:
- welke regelstrategie stabiel is,
- waar knelpunten in opslag/conversie optreden,
- en wat de impact is op netafname/injectie.

In praktijkgericht onderzoek is bovendien belangrijk dat modellen:
1. transparant zijn voor studenten en stakeholders,
2. met beperkte middelen reproduceerbaar zijn,
3. en uitbreidbaar blijven naar realistischer scenarios.

Daarom wordt een modulaire simulatie-aanpak opgezet waarin meetdata, regelalgoritmen en technologiekeuzes iteratief kunnen worden vergeleken.

---

## 3. Probleemstelling
Welke simulatietechnologie en modelleeraanpak is het meest geschikt om een betrouwbare, toegankelijke en performante digitale twin van een hybride energiesysteem te ontwikkelen voor HBO-onderzoek en onderwijs?

---

## 4. Doelstelling
### Hoofddoel
Een onderbouwde keuze maken voor simulatietechnologie(ën) en een eerste werkende digitale-twin-kern realiseren die energiestromen en regelacties realistisch genoeg kan nabootsen voor ontwerpevaluatie.

### Subdoelen
- Technologie-selectie op basis van objectieve criteria.
- Minimaal twee proof-of-concepts (PoC) opzetten en vergelijken.
- Een valideerbare basisarchitectuur leveren voor vervolgfases.
- Documentatie opleveren die direct inzetbaar is in onderwijs en onderzoekscommunicatie.

---

## 5. Onderzoeksvragen
### Hoofdvraag
Welke open-source simulatietechnologie is het meest geschikt voor een controleerbare en schaalbare digital twin van een multisource energiesysteem?

### Deelvragen
1. In welke gevallen biedt discrete event simulatie voordelen boven continue modellering?
2. Welke bibliotheken/frameworks zijn toegankelijk, open source en voldoende performant?
3. Hoe kan behoud van energie systematisch worden geborgd in het model?
4. Welke validatie-aanpak is haalbaar met beschikbare data en tijd?
5. Hoe vertalen we de simulatie naar onderwijsbare modules (didactische inzetbaarheid)?

---

## 6. Afbakening (scope)
### In scope
- Simulatiekern voor energiebalans en dispatchlogica.
- Batterij/opslag als buffercomponent.
- Variabele opwek (PV-profielen).
- Verbruiksprofielen met setpoint-gestuurde regels.
- Globale representatie van methanatie- en warmteketen (eerste-orde modellen).
- Netkoppeling met import/export en eenvoudige tarifering.

### Out of scope (fase 1)
- Diep fysisch detailmodel van reactorchemie.
- CFD/thermodynamische high-fidelity modelvorming.
- Real-time hardware-in-the-loop implementatie.
- Juridische marktoptimalisatie op kwartier- of secondemarktniveau.

---

## 7. Functionele en niet-functionele eisen
### Functionele eisen
- Simuleren van tijdsafhankelijke energieflows tussen subsystemen.
- Ondersteunen van event-triggered regels (setpoints, drempels, hystereses).
- Scenariovergelijking met verschillende bron-/vraagprofielen.
- Export van resultaten naar CSV/plots voor analyse.

### Niet-functionele eisen
- **Toegankelijk:** laagdrempelig voor studenten en docenten.
- **Transparant:** modelaannames expliciet en herleidbaar.
- **Reproduceerbaar:** versiebeheer + vaste experimentconfiguraties.
- **Open source:** geen vendor lock-in.
- **Performant genoeg:** scenario-runs in redelijke tijd op standaard laptop.

---

## 8. Voorgestelde methodiek
1. **Inventarisatie technologieën** (DES, hybride aanpak, continue tools).  
2. **Selectiematrix** met criteria (toegankelijkheid, performance, community, licentie, validatiegemak).  
3. **PoC-ontwikkeling** van minimaal twee kandidaten.  
4. **Benchmark en validatie** op identieke scenario’s.  
5. **Advies en roadmap** voor implementatiefase.

### Beoordelingscriteria (voorbeeldweging)
- Open-source volwassenheid (20%)
- Leerbaarheid / onderwijsgeschiktheid (20%)
- Validatie- en traceerbaarheid (20%)
- Performance / schaalbaarheid (20%)
- Integratiemogelijkheden met data pipelines (20%)

---

## 9. Waarom discrete event simulatie als startpunt
Uit deze eerste opzet (SimPy-demo) volgen sterke argumenten:

1. **Discrete tijdstappen of pure events** zijn intuïtief bij operationele regels.  
2. **Behoud van energie** is direct af te dwingen via container/bufferlogica.  
3. **Complexe niet-lineaire bedrijfsregels** passen natuurlijk in conditionele eventlogica.  
4. **Validatie** wordt eenvoudiger doordat state-transities expliciet en logbaar zijn.

Voor fase 1 is DES daardoor een pragmatisch en controleerbaar vertrekpunt. Later kan een hybride architectuur worden toegevoegd (DES + continue deelmodellen) als fysische detailnauwkeurigheid dat vereist.

---

## 10. Systeemarchitectuur (conceptueel)
### Kerncomponenten
- **Source nodes:** PV, eventueel wind/inkoop.
- **Conversion nodes:** elektrolyse/methanatie (vereenvoudigd in fase 1).
- **Storage nodes:** batterij, gasopslag, thermische opslag.
- **Demand nodes:** gebouw/process load.
- **Grid interface:** import/export, limieten, tarieven.
- **Controller:** setpoints, prioriteiten, veiligheidsgrenzen.

### Simulatiepatroon
- Event queue met tijdstempel.
- Componenten publiceren state-updates.
- Controller triggert acties op thresholds/prijzen/voorspellingen.
- Resultaatlogger schrijft KPI’s per timestep/event.

---

## 11. Validatie- en verificatieplan
### Verificatie (bouwt het model wat bedoeld is?)
- Unit-tests op energiebalans per component.
- Invariant checks (geen negatieve voorraden, geen energie uit niets).
- Regressietests op referentiescenario’s.

### Validatie (komt het model overeen met werkelijkheid?)
- Kalibratie op historische datasets (PV, load, temperatuur, prijs).
- Vergelijking met gemeten systeemrespons op bekende bedrijfssituaties.
- Expert review met domeinspecialisten.

### KPI’s
- Energiebalansfout (%).
- Zelfconsumptie en zelfvoorzieningsgraad.
- Peak shaving / netafnamepieken.
- Cycli en benuttingsgraad opslag.
- Conversierendement (CO2→CH4-keten, geaggregeerd).

---

## 12. Data- en experimentmanagement
- Gebruik vaste scenario-definities (JSON/YAML/CSV).
- Scheid inputdata, modelconfiguratie en resultaten.
- Leg random seeds vast voor reproduceerbaarheid.
- Versioneer experimenten met duidelijke naming conventies.

**Aanbevolen datasets (fase 1):**
- Uur- of kwartierprofielen voor PV-opwek.
- Verbruiksprofielen per gebouw/proces.
- Basis prijs-/tariefreeksen.
- (Later) weerdata en operationele constraints.

---

## 13. Planning en fasering (indicatief)
### Fase 0 – Start en inventarisatie (1–2 weken)
- Use-cases vastleggen.
- Technologie short-list opstellen.

### Fase 1 – PoC discrete simulatie (2–4 weken)
- SimPy baseline uitbreiden met grid + opslag + controller.
- KPI-logging en scenario-runner toevoegen.

### Fase 2 – Vergelijkende evaluatie (2–3 weken)
- Tweede tool/aanpak als referentie.
- Selectiematrix invullen op meetbare criteria.

### Fase 3 – Rapportage en overdracht (1–2 weken)
- Adviesdocument + demo + onderwijsmaterialen.

---

## 14. Risico’s en mitigerende maatregelen
- **Te snelle modelcomplexiteit:** starten met minimale componentenset + iteratief uitbreiden.
- **Datakwaliteit onvoldoende:** synthetische baseline + later kalibratie met velddata.
- **Performanceproblemen:** profilering en vereenvoudiging van eventfrequenties.
- **Onvoldoende draagvlak:** periodieke reviewmomenten met engineers/docenten.

---

## 15. Beoogde deliverables
1. Technologieverkenning met onderbouwde keuze.
2. Werkende PoC-simulatie(s) inclusief scenario’s.
3. Validatie- en testdocumentatie.
4. Gebruikershandleiding voor collega’s/studenten.
5. Roadmap voor doorontwikkeling naar hogere TRL.

---

## 16. Voorstel directe vervolgstappen
1. Bestaande SimPy-demo structureren in modules (model, controller, io, kpi).  
2. Dataset-koppeling toevoegen (CSV-inlezing voor opwek/vraag/prijs).  
3. Minimaal 3 standaardscenario’s definiëren (zomer, winter, stress-case).  
4. KPI-dashboard (tabellen + grafieken) opleveren voor review met team.  
5. Eerste validatiesessie plannen met domeinexperts.

---

## 17. Korte herformulering van deze  opzet
De huidige SimPy-demo laat al goed zien dat een energiebalans als event-driven systeem praktisch werkt:
- batterij als buffer/integrator,
- variabele bron (PV),
- verbruiker op setpoints,
- discrete updates via tijdstappen/events,
- en ruimte voor complexe regelalgoritmen zonder zware continue afleidingen.

Dit is mijn brain-fart tot nu toe. (7 maart 2026)
