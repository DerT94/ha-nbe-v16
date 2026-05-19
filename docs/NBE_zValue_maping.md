# NBE V16 – Z-Wert Mapping

***

## ✅ Sicher zugewiesene Z-Werte

Zuordnung durch exakte Wertkorrelation mit Livedata **und** Bestätigung über mehrere Snapshots mit Zustandsübergängen (Stopped → Ignition → Running → Cooling).
Die Snapshots wurden mithilfe von collect_stokercloud_data.ps1 erstellt. 
Das Skript liest die Inhalte aus der Cloud aus.

| Z-Wert | Name (HA) | Beschreibung | Faktor | Einheit | Anmerkung |
|--------|-----------|--------------|--------|---------|-----------|
| `z02` | `boiler_temp` | Kesseltemperatur (Ist) | ÷10 | °C | Primärwert; z50/z60 sind Spiegel |
| `z04` | `smoke_temp` | Abgastemperatur | ÷10 | °C | Ändert sich synchron mit Livedata `smoketemp` |
| `z05` | `oxygen` | Sauerstoffgehalt Abgas | ÷10 | % | Bestätigt via `frontdata.oxygen` |
| `z18` | `hopper_distance` | Silostand (Ultraschall-%) | ×1 | % | Bestätigt via `frontdata.hopperdistance` |
| `z25` | `boiler_temp_wanted` | Soll-Kesseltemperatur | ÷10 | °C | Konfigwert; z51 ist Spiegel |
| `z40` | `substate` | Substate-Integer des Controllers | ×1 | – | Entspricht direkt `lng_substate_XXX` |
| `z96` | `fan_rpm` | Abluftventilator RPM | ×1 | RPM | 0=Standby, ~1050=Running, ~1030=Cooling |
| `z102` | `igniter_power` | Zünder-Leistung | ×1 | % | 0=aus, 100=Vollast bei Zündung/Nachlöschen |
| `z111` | `state_seconds` | Sekunden im aktuellen State (Zähler) | ×1 | s | Zählt im Sekundentakt, Reset bei State-Wechsel |
| `z115` | `ash_dist` | Aschestand / Gegendruck | ×1 | % | Bestätigt via `frontdata.ashdist` |
| `z123` | `pressure` | Brennkammerdruck | ×1 | Pa | Ändert sich stark bei Zündung/Running |
| `z124` | `outdoor_temp` | Außentemperatur (Wetterstation) | ÷10 | °C | Bestätigt via `weatherdata.1` |
| `z158` | `pellet_consumption_trip` | Pelletverbrauch aktueller Trip | ÷10 | kg | Steigt während Betrieb, evtl. Reset pro Session |
| `z159` | `pellet_consumption_total` | Pellet-Gesamtverbrauch (Lifetime) | ×1 | kg | Bestätigt via `hopperdata_4`, `total_increasing` |

*** ✅ z40 State Mapping

| z40 raw | Klartext                                              |
| ------- | ----------------------------------------------------- |
| 2       | Ignition preheat                                      |
| 3       | (leer)                                                |
| 4       | (leer)                                                |
| 5       | (leer)                                                |
| 6       | Extinguish the fire and cooling burner                |
| 10      | Boiler valve 1 activate                               |
| 11      | Boiler valve 2 wait                                   |
| 12      | Boiler valve 2 activate                               |
| 13      | Burner valve wait                                     |
| 14      | Burner valve activate                                 |
| 15      | External contact                                      |
| 16      | Compressor cleaning                                   |
| 17      | Compressor start                                      |
| 18      | Pressure reached                                      |
| 19      | Burner valve active                                   |
| 20      | Pressurising                                          |
| 21      | Boiler valve 1 active                                 |
| 22      | Compressor depressurising                             |
| 208     | Low boiler temperature, check output or sensor        |
| 211     | Do not restart before the problem is found!!          |
| 212     | Burner plug or burner temperature sensor disconnected |
| 215     | No connection to the boiler temperature sensor        |
| 217     | Check connections on plug or burner                   |
| 220     | No fire - out of pellets?                             |


## ⚠️ Unsicher / Mehrdeutig zugewiesene Z-Werte

Wertkorrelation plausibel, aber keine eindeutige Bestätigung durch Namens- oder Einheitsmatch in den Livedaten. Zuordnung basiert auf Verhaltensmuster über Zustandsübergänge.

| Z-Wert | Vermutete Funktion | Faktor | Beobachtung / Begründung |
|--------|--------------------|--------|--------------------------|
| `z00` | Auger-Dosierzähler oder Leistung aktuell | ×1 | 0 im Standby, 16→42→50 während Running; identisch mit z59 |
| `z01` | Kumulativer Auger-Laufzähler | ×1 | 0 im Standby, 54→124→145 während Running; größere Werte als z00 |
| `z03` | Rücklauftemperatur (Ist) | ÷10 | raw=279–289 = ca. 27.9–28.9°C; stabil aber leicht variierend |
| `z10` | Außentemperatur-Mittelungszeitraum (h) | ×1 | Normalwert=24 (aus menudata `weather.avg_out_time`); springt bei Zündung auf 2–5 |
| `z41` | Kompressor-Kühlzeit Countdown | ×1 | 0 im Normalbetrieb; 453→299→144→0 exakt während Cooling-Phase (zählt runter) |
| `z101` | Kompressor-Ausgabe (output-7) | ÷10 | Idle=65 (6.5%), Running=300 (30%); korreliert mit `leftoutput.output-7` |
| `z163` | Rücklauftemperatur (alternativ) | ÷10 | raw ~226–229 = 22.6–22.9°C über alle States stabil; passt zu ungenutztem HK |
| `z164` | Lüfter-RAW oder Kompressor-Druck | ×1 | Idle~130, Ignition=1044, Running=1757; zu hoch für Temperatur, unklar |
| `z165` | Zugehöriger Sekundärwert zu z164 | ×1 | Verhält sich ähnlich wie z164 aber kleinere Werte; 0=Standby, Peak bei Running |

***

## ❓ Offene Z-Werte mit Beobachtungen

Keine plausible Zuordnung möglich. Werte sind entweder konstant, zu generisch (raw=100/0/1) oder zeigen kein eindeutiges Korrelationsmuster mit bekannten Livedaten.

| Z-Wert | raw (Beispiel) | Beobachtung / Hinweis |
|--------|----------------|----------------------|
| `z11` | 9999 | KONSTANT – nicht auswertbar |
| `z12` | 9999 | KONSTANT – nicht auswertbar |
| `z13` | 0 | KONSTANT – nicht auswertbar |
| `z14` | 0 | KONSTANT – nicht auswertbar |
| `z16` | 0 | KONSTANT – nicht auswertbar |
| `z19` | 0 | KONSTANT – nicht auswertbar |
| `z21` | 0 | KONSTANT – nicht auswertbar |
| `z22` | 0 | KONSTANT – nicht auswertbar |
| `z24` | 0 / 180→119 | Identisch mit z71; Countdown nur während Running aktiv; evtl. Sekunden bis nächste Pelletdosis |
| `z28` | 0 | KONSTANT – nicht auswertbar |
| `z29` | 100 | KONSTANT 100 – mehrdeutig; zu viele Parameter mit val=100 |
| `z31`–`z34` | 9999 | KONSTANT – nicht auswertbar |
| `z42`–`z45` | 0 | KONSTANT – nicht auswertbar |
| `z46` | 9999 | KONSTANT – nicht auswertbar |
| `z47` | 1 | KONSTANT 1 – mehrdeutig; zu viele Parameter mit val=1 |
| `z48`–`z49` | 0 | KONSTANT – nicht auswertbar |
| `z50` | wie z02 | Spiegel von z02 (Kesseltemperatur); möglicherweise Heizkreis-1-Vorlauf als Fallback |
| `z51` | wie z25 | Spiegel von z25 (Soll-Kesseltemperatur) |
| `z54` | 0 / 50 | Nur aktiv während Running; evtl. Auger-Einschaltdauer in % oder ms |
| `z55` | 0 / 10 | Nur aktiv während Running; evtl. Auger-Pausendauer |
| `z56` | 0 / 100 | Nur aktiv während Running; evtl. Verbrennungsluft-Sollwert % |
| `z57` | 0 / 11–12 | Nur aktiv während Running; evtl. Dosiertakt-Intervall |
| `z59` | wie z00 | Spiegel von z00 |
| `z60` | wie z02 | Spiegel von z02; möglicherweise Heizkreis-2-Vorlauf als Fallback |
| `z70` | wie z05 | Spiegel von z05 (Sauerstoff) |
| `z71` | wie z24 | Spiegel von z24 |
| `z82` | 7700 | KONSTANT – evtl. Konfigwert (Nennleistung? 7.7 kW × 1000?) |
| `z83` | 14800 | KONSTANT – evtl. Konfigwert (14.8 kW?) |
| `z84` | 17800 | KONSTANT – evtl. Konfigwert (17.8 kW?) |
| `z87` | 291–295 | Sehr langsame Änderung; evtl. Betriebsstundenzähler in 0.1h (29.1–29.5 h) |
| `z88` | 676 | Nahezu KONSTANT – evtl. kumulierter Auger-Betriebszähler |
| `z89` | 0 | KONSTANT – nicht auswertbar |
| `z91` | 0 | KONSTANT – nicht auswertbar |
| `z97` | 0 | KONSTANT – nicht auswertbar |
| `z99` | 0 | KONSTANT – nicht auswertbar |
| `z103` | 0 | KONSTANT – nicht auswertbar |
| `z104` | 100 | KONSTANT 100 – mehrdeutig (wie z29) |
| `z105`–`z107` | 0 | KONSTANT – nicht auswertbar |
| `z108` | 100 | KONSTANT 100 – mehrdeutig (wie z29) |
| `z119`–`z121` | 0 / variabel | z121 aktiv bei Zündung (100→19→24→32); evtl. Zündphasen-Fortschritt % |
| `z122` | 9990 | Nahezu KONSTANT 9990 – Sondersentinel? |
| `z127` | 0 | KONSTANT – nicht auswertbar |
| `z128` | 9999 | KONSTANT – nicht auswertbar |
| `z129` | 10 | KONSTANT 10 – mehrdeutig |
| `z130`–`z153` | 0 | KONSTANT – alle nicht auswertbar (wahrscheinlich unbenutzte Expansion-Slots) |
| `z160` | 3246 / 1070–1207 | Ändert sich bei Zündung stark (3246→1070); evtl. Gegendrucksensor roh oder Lüfter-Sollwert |
| `z161` | 0 | KONSTANT – nicht auswertbar |
| `z162` | 100 | KONSTANT 100 – mehrdeutig |
| `z166`–`z167` | 0 | KONSTANT – nicht auswertbar |

***

## Hinweise zur Weiterverwendung
