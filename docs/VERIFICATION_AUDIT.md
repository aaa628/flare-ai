# BASS-II Data Verification Audit Report

This report audits `data/bass2_draft.csv` against the NASA TM-20210011385 report text.

## Overview
- Checked 126 rows from `data/bass2_draft.csv`.

## Missing Tests (P7, P11, T8)
- P7: Not found in source text export.
- P11: Not found in source text export.
- T8: Found in source text export.

## Exact Matches
110 rows were parsed perfectly with no QC flags, and all CSV fields were explicitly found in the source raw text.

## QC Flag Rows Requiring Special Attention
### BASSII-B14 (Page 103)
- **Flags:** o2_final_not_numeric
- **Values:** O2: 15.0 -> , Mode: Opposed
- **Observation:** HCl O, only brief ignition, flame extinguished
- **Raw Text:** `--------- 47 B14 174m 1-cm-wide, 200-µmthick PMMA Integral 2 Opposed ---------------- 5, 3, 2, extinction 250 --- NA NA N CL A –4 NA --- F2 1,000 Cont 5 ---- 15.0 ----- 14.1 ----- 0.00 ----- 0.2 ---- HCl O, only brief ignition, flame extinguished`

### BASSII-B2 (Page 104)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 22.2 -> 1.6, Mode: Opposed
- **Observation:** No stills taken, cable came loose; not quite a straight on edge view
- **Raw Text:** `8 B2 155 200-µm PMMA film, 2 cm wide Integral 2 Opposed 62 5 50 --- 8 NA N CL A –4 off --- F2 1,000 Cont 7 none 22.2 1.6 20.6 ----- 0.44 ----- 6 ---- No stills taken, cable came loose; not quite a straight on edge view`

### BASSII-F3 (Page 105)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 21.7 -> 0.9, Mode: Concurrent
- **Observation:** Brief ignition flash, no sustained flame; no postburn sensor readings taken
- **Raw Text:** `8:58:25 115 F3 229m Nomex® natural (Nomex III) Integral 1 Concurrent 61 8 50 NA NA N CL A –3 NA ------ F2 1,000 Cont 13 46 21.7 0.9 20.8 ------ 0.36 ------ 2 --- Brief ignition flash, no sustained flame; no postburn sensor readings taken`

### BASSII-P22a (Page 107)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 20.8 -> 0.6, Mode: Opposed
- **Observation:** Extinguished at higher flow, possibly rod not preheated enough by a bit, CO readings elevated, slow response
- **Raw Text:** `---------- 68 P22a 200m 9.525-mm black rod –35 2 Opposed 5, 0.36, 0.32 extinction after some time 5 down to extinction 250 > 50 ---- NA NA N CL A –3 NA ---- F2 1,000 Cont 6 83 20.8 0.6 20.2 ---- 0.32 ---- 4 ---- Extinguished at higher flow, possibly rod not preheated enough by a bit, CO readings elevated, slow response`

### BASSII-P22b (Page 107)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 20.0 -> 39.1, Mode: Opposed
- **Observation:** Extinguished at lower flow than P22a by a bit, longer slower decrease in flow, CO elevated, slow response
- **Raw Text:** `---------- 69 P22b 200m 9.525-mm black rod –35 2 Opposed 5, 0.36, 0.34, 0.33, 0.32, 0.31, extinction 5 down to extinction 50 ---- NA NA N CL A –3 NA ---- F2 1,000 Cont 6 155 20.0 39.1 ---- 19.1 ---- 1.09 ---- 236 Extinguished at lower flow than P22a by a bit, longer slower decrease in flow, CO elevated, slow response`

### BASSII-M5 (Page 109)
- **Flags:** o2_final_reading_suspect;hand_keyed
- **Values:** O2: 22.2 -> 19.0, Mode: Opposed
- **Observation:** Rick ignited while we were loss of signal and out of contact with ISS, unfortunately; ignition was ~3 min per his verbal call down when we came back; flame already burning ~1/3 of sample, both sides, long and sooty; more vapor jetting on bottom due to molten ball attached there, visible when lights on to change camera card; turned down to 10 cm/s, then further down in increments to 5 cm/s; extinguished at 5 cm/s after prolonged flashing; during soot cleaning, Rick noticed damage to front door corner by the switches; He sent pictures down for us to evaluate for damage; CO reading posttest was off-scale; came back during purge reading 500
- **Raw Text:** `--------- 18 M5 167 3-mm-thick PMMA, two-sided, 2 cm thick Integral 0 Opposed 20, 13, 10, 8, 5 50 ----------- ? NA N S A –4 Off ---- F2 1,000 Man 10, 14 300+ +102 22.2 19.0 20.6 17.4 0.44 3.22 9 >500 Rick ignited while we were loss of signal and out of contact with ISS, unfortunately; ignition was ~3 min per his verbal call down when we came back; flame already burning ~1/3 of sample, both sides, long and sooty; more vapor jetting on bottom due to molten ball attached there, visible when lights on to change camera card; turned down to 10 cm/s, then further down in increments to 5 cm/s; extinguished at 5 cm/s after prolonged flashing; during soot cleaning, Rick noticed damage to front door corner by the switches; He sent pictures down for us to evaluate for damage; CO reading posttest was off-scale; came back during purge reading 500`

### BASSII-O1 (Page 110)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 22.2 -> 21.7, Mode:
- **Observation:** Bracket test with decreasing flows; very sooty long flame at high flows; rod very thinned out and was wobbling due to vapor jetting later in test; Rick broke it off holder during readjustments
- **Raw Text:** `16:20- 5 O1 207 6.35-mm clear rod 0020-23 2 ? 89, 62, 50, 41 20, 10, 5, 2, 1 50 ---- 8 NA N CH A –5 9F 1.0 --- F4 1,600 7s 3 62 22.2 21.7 20.6 20.1 0.44 0.85 -1 51 Bracket test with decreasing flows; very sooty long flame at high flows; rod very thinned out and was wobbling due to vapor jetting later in test; Rick broke it off holder during readjustments`

### BASSII-O16 (Page 110)
- **Flags:** hand_keyed
- **Values:** O2: 14.5 -> 14.5, Mode: Stagnation
- **Observation:** Brief flame at end of first ignition, but no joy on sustained flame
- **Raw Text:** `-------- 106 O16 219m 9.525-mm clear rod –31 2 Stagnation 60 (2.6) 5 250 ---- NA NA N CL A –3 NA --- F2 1,000 Cont 7 10 postburn only 14.5 14.5 13.4 13.4 0.27 0.32 2 33 Brief flame at end of first ignition, but no joy on sustained flame`

### BASSII-O2 (Page 110)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 22.2 -> 21.9, Mode:
- **Observation:** Ignited at 2 cm/s, and got dim flame that got sooty with lots of vapor jetting, reduced flow to 1.5 pot and got less vapor jetting test; still sooty at these low flows
- **Raw Text:** `-------- 6 O2 204 6.35-mm clear rod 0020-23 2 ? 0.54 pot and 0.45 pot 0 50 ---- 8 NA N CL A –4 Off --- F4 1,600 Cont 3 287 22.2 21.9 20.6 20.3 0.44 0.59 –1 23 Ignited at 2 cm/s, and got dim flame that got sooty with lots of vapor jetting, reduced flow to 1.5 pot and got less vapor jetting test; still sooty at these low flows `

### BASSII-T1 (Page 112)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 18.5 -> 18.5, Mode:
- **Observation:** Compound Specific Analyzer-Combustion Products (CSACP) unit 1024; Carbon Dioxide Monitor (CDM) unit 1018; Prefill O2 reading = 20.9 percent; GN2 fill was from video display time 10:53 to 12:31 at maximum GN2 flow rate (pot = 10); Video display time is currently 1 day plus 6 min 10 s ahead of actual GMT; flow velocity held constant
- **Raw Text:** `1 T1 128 SIBAL 2 cm Integrated 2 1 80 10 50 0.97 maximum 10 0 N CL M NA NA 1/8 F2 1,000 100 s 2 85 18.5 18.5 17.3 17.3 0.35 0.41 0 40 Compound Specific Analyzer-Combustion Products (CSACP) unit 1024; Carbon Dioxide Monitor (CDM) unit 1018; Prefill O2 reading = 20.9 percent; GN2 fill was from video display time 10:53 to 12:31 at maximum GN2 flow rate (pot = 10); Video display time is currently 1 day plus 6 min 10 s ahead of actual GMT; flow velocity held constant`

### BASSII-T15 (Page 112)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 18.7 -> 18.7, Mode:
- **Observation:** Initial air reading is 15, but Rick did not wait long enough for the anemometer to stabilize; actual airspeed is about 9 cm/s; no flow restrictors installed, but flow only maxed out to 29 cm/s; no blowoff attained
- **Raw Text:** `4 T15 138 SIBAL 2 cm Integrated 0 1 80, 122 9, 29 50 1.68 maximum 10 0 N CL M NA NA 1/8 F2 1,000 100 s 5 46 18.7 18.7 17.5 17.5 0.45 0.51 72 102 Initial air reading is 15, but Rick did not wait long enough for the anemometer to stabilize; actual airspeed is about 9 cm/s; no flow restrictors installed, but flow only maxed out to 29 cm/s; no blowoff attained`

### BASSII-T2 (Page 112)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 18.5 -> 18.5, Mode:
- **Observation:** Flow velocity changed to 9 to 5 fairly early then very late in the burn changed to 4
- **Raw Text:** `2 T2 129 SIBAL 2 cm Integrated 2 1 80, 59, 55 9, 5, 4 50 0.64 maximum 10 0 N CL M NA NA 1/8 F2 1,000 100 s 2 100 18.5 18.5 17.3 17.3 0.41 0.45 40 78 Flow velocity changed to 9 to 5 fairly early then very late in the burn changed to 4`

### BASSII-T28a (Page 113)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 20.7 -> 0.9, Mode: Concurrent
- **Observation:** Tried to get one-sided ignition, but flame only briefly flashed then went out
- **Raw Text:** `17:21:03 123 T28a 144m 1 cm SIBAL 39 1 Concurrent 53 5 250 --------- NA NA N CL M NA NA 1/8 F2 1,000 Cont 5 19 20.7 0.9 19.8 ------ 0.41 ------ –1 ---- Tried to get one-sided ignition, but flame only briefly flashed then went out`

### BASSII-T28b (Page 113)
- **Flags:** o2_final_reading_suspect
- **Values:** O2: 20.7 -> 40.4, Mode: Concurrent
- **Observation:** Tried to get one-sided ignition, but again flame only briefly flashed then went out
- **Raw Text:** `17:29:49 124 T28b 144m 1 cm SIBAL 39 1 Concurrent 53 5 250 -------- NA NA N CL M NA NA 1/8 F2 1,000 Cont 5 27 20.7 40.4 ------ 19.7 ------ 0.42 ---- 2 Tried to get one-sided ignition, but again flame only briefly flashed then went out`

### BASSII-T3 (Page 113)
- **Flags:** hand_keyed
- **Values:** O2: 17.2 -> 16.8, Mode: Stagnation
- **Observation:** Multiple ignition attempts on card 3, brief flames go out
- **Raw Text:** `---------- 43 T3 182m 4 cm spherical section -24 broke, -25 2 Stagnation 63 10 250 -------- NA NA N CL A –4 NA 1/4 F4 1,000 Cont 3, 8 166 17.2 16.8 16.3 15.9 0.42 0.7 45 113 Multiple ignition attempts on card 3, brief flames go out`

### BASSII-T4 (Page 113)
- **Flags:** flow_mode_not_stated
- **Values:** O2: 18.7 -> 18.7, Mode:
- **Observation:** O2 reading creeped up slightly after a long pause in operations; flow velocity changed immediately after ignition down to 1 (fan pot 0.9); extinguished after turning into flamelet
- **Raw Text:** `3 T4 130 SIBAL 2 cm Integrated 2 1 80, 46 9,1 50 0.19 maximum 10 0 N CL M NA NA 1/8 F2 1,000 100 s 5 97 18.7 18.7 17.5 17.5 0.44 0.45 59 72 O2 reading creeped up slightly after a long pause in operations; flow velocity changed immediately after ignition down to 1 (fan pot 0.9); extinguished after turning into flamelet`

## Discrepancies and Mismatches
No extracted field mismatch found against raw text blocks.