# Mapping evidence

This document separates **established associations**, **uncertain interpretations** and **fields that cannot be resolved from the available installation**. The [sensor reference](sensors.md) describes implementation; enabling a sensor is not itself evidence of its physical meaning.

## Evidence basis and confidence

The main comparison used 40 paired EP20/cloud snapshots from one operating cycle on 19 November 2026, with 107 Z-keys per frame. An earlier two-frame session and a local English language export supplied supplementary evidence. Original captures, exports, exact timelines and reproducible audits stay local and ignored. Only field-level findings are published here; no device identifiers, credentials, raw frames or private network endpoints are included.

Cloud screens were read sequentially after the TCP frame, without individual measurement timestamps. No `livedata_ref` reuse occurred in the 40-frame session. Exact matches establish an association with a named reference in the observed installation; they do not independently calibrate a sensor or prove behavior on every controller. The historical collector does not reliably preserve TCP fragments, so its records are mapping evidence rather than parser fixtures; see [tool limitations](../tools/README.md).

Historical dynamic tests remain evidence even when a later recording is constant. Adopted units, observed equality and independently named matches are distinguished below. Earlier observations and superseded hypotheses remain in the [historical archive](archive/z-value-observations.md).

## 1. Established associations in the observed installation

| Keys | Association and supporting evidence | Limits |
| --- | --- | --- |
| z00 / z01 | Named Power / Power output references matched 40/40 at ×1 / ÷10. Language labels explicitly give % / kW. Example: z01=191 → 19.1 kW. | Relative configured output, not measured efficiency or electrical input. |
| z02 / z03 / z04 / z05 | Named boiler / drop shaft / chimney-smoke / oxygen references matched 40/40 at ÷10. Chart labels give °C / °C / °C / %. | z03 supersedes the earlier return-temperature hypothesis. |
| z18 | Named Hopper content reference #42 matched 40/40 at ×1; chart label gives %. Historical observation identifies `frontdata.hopperdistance`. | A different Hopper content reference (#16) is negative and is not this field; percentage does not establish the sensor's physical geometry. |
| z24 | Named O2 wanted matched 40/40 at ÷10; chart label gives %. A manual measured-O2 percent reading supports the oxygen scale. | Supersedes the pellet-dose countdown hypothesis. |
| z82 / z83 / z84 | Named O2 low/mid/high regulation matched 40/40 at ÷100. Supplied web screenshot shows %. Examples: 24100/17000/20500 → 241/170/205. | Reference values, not concentration setpoints. Controller meaning and thresholds remain open; no statistics class. |
| z121 / z123 | Named Fan Speed / Pressure matched 40/40 at ×1. Chart labels give % / Pa, consistent with the adopted units and historical pressure observations. | No independent physical calibration. z121 supersedes ignition-progress interpretation. |
| z10 | Observed stop → ignition → running → stop sequence agrees with codes 24 → 2 → 5 → 24; matching export labels exist. | Only three main-state codes were observed. Snapshot timing does not prove the exact event second. |
| z40 | Same-frame main/substate pairs and `lng_substate_*` identify the substate field. | Individual label evidence and the implemented compatibility lookup differ; see below. |
| z41 / z111 | Repeated phase countdowns and main-state timer resets support seconds remaining in phase / seconds in main state. Historical cooling observations agree. | Derived from behavior, not 40/40 matches to an independently named timer. Clock alignment remains approximate. |
| z50 / z60 / z59 / z70 / z71 | Observed equality to z02 / z02 / z00 / z05 / z24 in all 40 frames. | Equality does not prove the same physical function under other configurations. z59/z71 retain their raw contract. |

For z00, the 17 running samples additionally fit interpolation between configured 3.8 kW at 10% and 28 kW at 100%, with maximum deviation below 0.085 kW from z01/10. This supports relative output. Initial unit adoption by the user preceded the supplementary chart-label check; the evidence types are not interchangeable.

### State and timer evidence

z10 labels: 2 = `Ignition 1`, 5 = `Running`, 24 = `Stopped by external contact`. Other codes remain unknown. Same-frame pairs in the main/earlier sessions were `(2,1)` 1/0 times, `(2,4)` 2/1, `(5,0)` 17/0, `(24,6)` 11/0 and `(24,224)` 9/1.

| z40 | Export text | Observed context | Current implementation |
| --- | --- | --- | --- |
| 0 | Empty string | Running, z41=0 | Numeric unknown |
| 1 | Ignition ventilating | Early ignition, z41=14 s | Numeric unknown |
| 4 | Ignition | Timed ignition, z41=281→230 s | Numeric unknown |
| 6 | Extinguish the fire and cooling burner | Cooling, z41=535→20 s | Existing `Extinguish and cool` |
| 224 | One space | Stopped before ignition and after cooling; user reports blank web substate | Numeric unknown |

The export also names code 2 `Ignition preheat`, code 3 `Ignition pellets` and code 5 as empty. Those codes did not occur in the two sessions. The existing lookup retains code 2 and historical additional labels; code 3/4 texts in the old notes differ from the export. New labels require a deliberate compatibility decision rather than an automatic rewrite.

z41+z111 equals 379 for the observed z40=4 samples, including the earlier 274+105 pair; 560 in all eleven cooling samples; and 60 in the single z40=1 sample. These are phase deadlines relative to main-state entry, not universal phase durations. The manually noted cooling display of about 9:30 does not establish a 570-second constant.

z111 resets with main-state transitions and continues when cooling ends while the main state remains stopped (540 → 592 s). It is not total cycle runtime. Timer-derived transitions differ from manual notes by roughly 5–7 seconds; precise synchronization is unverified. Zero countdown alone does not identify a phase ending.

### Language-export cross-check

Display/translation numbers are not UART field numbers. Chart slots 00–02 happen to match Z suffixes, but slot 08 is z03, 06 is z04, 10 is z05 and 14 is z121. Slots 44–59 describe heating zones and 60–67 solar; slot 59 labels a valve while z59 follows power.

Named boiler display labels likewise use a different order: `lng_boil_7` is Drop shaft (z03), `lng_boil_3` Chimney/smoke (z04), `lng_boil_12` O2 (z05), `lng_boil_25` Fan Speed (z121) and `lng_boil_24` Pressure (z123). Same-number keys would misassign fields. An exact numeric-key search found no common direct-label family; shared `lng_setup_121/123/158` entries instead label a correction setting or are empty.

Useful corroborating chart labels include `graphics_name_11` Wanted O2 (%), `03` Wanted boiler (°C), `21` Hopper content (%), `17` Boiler vacuum (Pa) and `16` Ash box (%). A label proves that a display quantity exists; without a named value comparison it does not bind a UART field to it.

## 2. Supported or uncertain mappings: remaining evidence gaps

| Keys | Evidence and current conclusion | What is still needed |
| --- | --- | --- |
| z25 / z51 | Historical setpoint association; new session constant 700 against Boiler wanted=70 and menu setting 70. z51 equals z25. | Independent dynamic separation if further validation is needed; a constant does not invalidate the historical test. |
| z124 | Historical outdoor association (`weatherdata.1`), retained at ÷10 °C. New session constant 70. | Independent outdoor variation; one constant capture cannot reconfirm it. |
| z158 | Adopted as Consumption 24h, ÷10 kg. Named comparison exact in 28/40 frames, eleven +0.1 and one +0.2; later user-observed raw 29 matches 2.9 kg. Saved Trip 1/2 displays (4441/9681 while earlier z158=0) contradict the trip interpretation. | Exact rolling/calendar window and reset rules. `measurement` allows decreases; the label is not proof of the time-window algorithm. |
| z159 | Historical total association at ×1 kg. Named total agrees in 16/40 frames, with 24 raw readings one below the reference; both earlier frames match. | Lifetime scope, timing/rounding and reset behavior. Retained `total_increasing` is an implementation convention, not newly proved by this short session. |
| z96 | RPM interpretation unreliable: 1046 → 20 → 1047 while Fan Speed is 33 → 32 → 35; resting value 16. Developer mode exposes raw integers. | Independently named measurement or protocol definition. A bitmask remains a hypothesis. |
| z101 | z101+z158 is 228 in 38/40 main frames and both earlier frames, 227 in two main frames. Historical output-7 hypothesis also exists. | Named L7/quantity comparison; arithmetic alone establishes neither kg, scale nor physical meaning. |
| z102 | Historical igniter hypothesis: 100 in ignition/cooling, then 77/49/24/10 while running, 0 at rest. Export has an Igniter label. | Named output comparison and unit binding. Cooling=100 is already in historical evidence and does not alone refute it. |
| z54 / z55 / z57 | Running values 39–44 / 10 / 10–12, zero outside Running; export names actual auger time/pause. | Individual field assignment, scale and unit; named timing series were not recorded. |
| z56 | Varies with running; earlier air-setpoint hypothesis. | Named reference, meaning and scale. |
| z87 / z88 | Slowly varying values; earlier runtime/auger-counter hypotheses. | Named counter reference, unit and reset observations. |
| z160 | Strong variation during ignition and running; earlier pressure/fan hypotheses. | Independent reference; range alone cannot choose a function. |
| z163 | Raw values about 222–227 across both sessions could fit 22.2–22.7 °C. Return-temperature display label exists. | Independently named return reading to bind field, scale and unit. |
| z164 / z165 | Related varying values, historically attributed tentatively to fan/raw pressure quantities. | Independent reference and protocol meaning. |
| z115 | Historical ash-level association `frontdata.ashdist`; all 42 samples and unnamed reference #39 are constant 53. Export names Ash box (%). | Named changing ash reading. The new capture cannot discriminate the hypothesis. |

These fields are not all equally uncertain: existing historical mappings may be retained, adopted mappings may be usable with stated limits, and other fields remain raw. Their [implemented behavior](sensors.md) must be read separately from confidence.

## 3. Not resolvable from the available installation

The owner's installation supplies no informative variation for the following 66 unresolved fields in the 40-frame session. They remain unassigned. Repeated recording of the same zeros or sentinel-like constants on this unchanged installation cannot establish their function; this is an **installation evidence limit**, not merely unfinished analysis.

| Constant raw value | Fields | Keys |
| --- | ---: | --- |
| 0 | 51 | `z13`, `z14`, `z16`, `z19`, `z21`, `z22`, `z28`, `z42`, `z43`, `z44`, `z45`, `z48`, `z49`, `z89`, `z91`, `z97`, `z99`, `z103`, `z105`, `z106`, `z107`, `z119`, `z120`, `z127`, `z130`, `z131`, `z132`, `z133`, `z134`, `z135`, `z136`, `z137`, `z138`, `z139`, `z140`, `z141`, `z142`, `z143`, `z144`, `z145`, `z146`, `z147`, `z148`, `z149`, `z150`, `z151`, `z152`, `z153`, `z161`, `z166`, `z167` |
| 1 | 1 | `z47` |
| 10 | 1 | `z129` |
| 99 | 1 | `z104` |
| 100 | 3 | `z29`, `z108`, `z162` |
| 9990 | 1 | `z122` |
| 9999 | 8 | `z11`, `z12`, `z31`, `z32`, `z33`, `z34`, `z46`, `z128` |

`9999` and `9990` are observed constants, not verified protocol definitions for a sentinel or an unavailable value. Likewise, zero does not prove a disabled feature and 100 does not prove a percent unit. Unused expansion/heating-zone functions are possible explanations, not established mappings.

z25/z51, z115 and z124 are also constant in this session, but have distinct historical/reference evidence and are discussed separately above. Constancy in this recording does not erase that evidence.

### Fields with no received value

Only 107 distinct keys were present. Numeric gaps, for example z06–z09, z15 and z17, carry no evidence of a supported sensor or its meaning. A key absent from the available frames is different from a key explicitly received as zero or 9999. Neither absence nor a constant permits inventing a mapping.

On this installation, fields that remain absent or provide only uninformative constants cannot be resolved by additional interpretation of the same data. Progress requires another installation/configuration that actually supplies informative values, a verified named comparison or manufacturer protocol documentation. There is no requirement to resolve every such field before the known mappings can be documented or used, and no claim that they are universally unknowable on all NBE systems.

## Coverage and further evidence

The audit accounts for all 107 received keys: 30 other assessed keys, 11 varying unresolved keys (z54–z57, z87, z88, z102, z160, z163–z165) and the 66 constant unresolved keys above. Overall 37 keys vary and 70 are constant. z96 and z101 are included among the 30 assessed keys despite remaining uncertain.

Useful future evidence targets named changing values for the uncertain group, consumption over a longer time window and supported fields on other installations. Site-specific captures and exports remain private. Publishing a sanitized field-level finding does not publish or authorize access to its source data. History/statistics consequences belong to [compatibility](compatibility.md).
