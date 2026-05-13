# Lyfjavaki (Helix Health) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - New prescription order

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|LANDSPITALI|20260315091200||ORM^O01|MSG00001|P|2.4
PID|1||1808962742^^^ISLAND^KT||Hauksson^Tindur^Brynjar||19960818|M|||Suðurlandsbraut 30^^Reykjavík^^108^IS||+3545631927|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00012345|||||||||||||||||||||||||20260315091200
ORC|NW|RX20260315001|||||^^^20260315091200^^R||20260315091200|PHARM001^Védís^Tryggvadóttir|||||LYFJABUD_LAUGAVEGAR
RXO|00123^Amoxicillin 500mg capsules^ISLYF||500|mg|CAP^Capsule||^^Take one capsule three times daily for 10 days|G||30|CAP
```

---

## 2. ORM^O01 - Refill prescription order

```
MSH|^~\&|LYFJAVAKI|LYFJAVER_KOPAVOGS|SAGA|HEILSUGAESLAN|20260318140530||ORM^O01|MSG00002|P|2.4
PID|1||0407880156^^^ISLAND^KT||Magnúsdóttir^Bryndís^||19880704|F|||Skipholt 17^^Reykjavík^^105^IS||+3545712304|||IS
PV1|1|O|LYFJAVER_KOPAVOGS^^^^APOTK|||||||PHR||||||||V00023456|||||||||||||||||||||||||20260318140530
ORC|RF|RX20260101044||RX20260101044|||^^^20260318140530^^R||20260318140530|PHARM002^Hjalti^Birgisson|||||LYFJAVER_KOPAVOGS
RXO|00456^Metformin 850mg tablets^ISLYF||850|mg|TAB^Tablet||^^Take one tablet twice daily with meals|G||60|TAB
```

---

## 3. ORM^O01 - IV medication order

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260320083000||ORM^O01|MSG00003|P|2.4
PID|1||1411902375^^^ISLAND^KT||Steinarsson^Þórgnýr^||19901114|M|||Lambasel 22^^Reykjavík^^109^IS||+3545428706|||IS
PV1|1|I|LSH_10B^^^^BED5|||||||MED||||||||A00034567|||||||||||||||||||||||||20260319120000
ORC|NW|RX20260320005|||||^^^20260320083000^^S||20260320083000|PHARM003^Iðunn^Pálmadóttir|||||SJUKRAHUSAPOTEK_LSH
RXO|01200^Vancomycin 1g IV infusion^ISLYF||1000|mg|IV^Intravenous||^^Infuse 1g in 250mL NaCl 0.9% over 60 minutes every 12 hours|G||1|VIAL
RXR|IV^Intravenous
```

---

## 4. ORM^O01 - Antibiotic order

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|HEILSUGAESLAN|20260322101500||ORM^O01|MSG00004|P|2.4
PID|1||0508761439^^^ISLAND^KT||Bárðardóttir^Ragna^||19760805|F|||Holtsgata 9^^Reykjavík^^101^IS||+3545923418|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00045678|||||||||||||||||||||||||20260322101500
ORC|NW|RX20260322008|||||^^^20260322101500^^R||20260322101500|PHARM004^Vésteinn^Einarsson|||||LYFJABUD_LAUGAVEGAR
RXO|00789^Ciprofloxacin 500mg tablets^ISLYF||500|mg|TAB^Tablet||^^Take one tablet twice daily for 7 days|G||14|TAB
```

---

## 5. ADT^A04 - Pharmacy patient registration

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|LANDSPITALI|20260325090000||ADT^A04|MSG00005|P|2.4
EVN|A04|20260325090000
PID|1||0211003816^^^ISLAND^KT||Þorgrímsson^Sölvi^Andri||20001102|M|||Háteigsvegur 14^^Reykjavík^^105^IS||+3545348901|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00056789|||||||||||||||||||||||||20260325090000
```

---

## 6. ADT^A08 - Update medication patient info

```
MSH|^~\&|LYFJAVAKI|LYFJAVER_KOPAVOGS|SAGA|HEILSUGAESLAN|20260327143000||ADT^A08|MSG00006|P|2.4
EVN|A08|20260327143000
PID|1||0712912483^^^ISLAND^KT||Friðriksdóttir^Ragnhildur^Eyrún||19911207|F|||Smáragrund 6^^Akureyri^^603^IS||+3544668013||IS||IS
PV1|1|O|LYFJAVER_KOPAVOGS^^^^APOTK|||||||PHR||||||||V00067890|||||||||||||||||||||||||20260327143000
AL1|1|DA|00456^Penicillin^ISLYF|SV|Anaphylaxis|20240115
AL1|2|DA|01890^Sulfonamides^ISLYF|MI|Rash|20230301
```

---

## 7. ORU^R01 - Drug level monitoring result

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|FLEXLAB|LANDSPITALI|20260401110000||ORU^R01|MSG00007|P|2.4
PID|1||0903945812^^^ISLAND^KT||Tryggvason^Hjörvar^||19940309|M|||Trönuhraun 21^^Hafnarfjörður^^220^IS||+3545617408|||IS
PV1|1|I|LSH_8A^^^^BED2|||||||MED||||||||A00078901|||||||||||||||||||||||||20260330080000
ORC|RE|LAB20260401001|||||^^^20260401110000^^R||20260401110000|PHARM005^Snjólaug^Vésteinsdóttir|||||SJUKRAHUSAPOTEK_LSH
OBR|1|LAB20260401001||TDM^Therapeutic Drug Monitoring^ISLYF|||20260401100000|||||||||PHARM005^Snjólaug^Vésteinsdóttir||||||||F
OBX|1|NM|VANC_TROUGH^Vancomycin Trough Level^ISLYF||14.2|ug/mL|10-20|N|||F|||20260401103000
OBX|2|NM|VANC_PEAK^Vancomycin Peak Level^ISLYF||32.5|ug/mL|25-40|N|||F|||20260401103000
```

---

## 8. ORU^R01 - Allergy/adverse reaction notification

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|LYFJASTOFNUN|20260403153000||ORU^R01|MSG00008|P|2.4
PID|1||2509894125^^^ISLAND^KT||Þorláksdóttir^Hjördís^||19890925|F|||Garðatorg 6^^Garðabær^^210^IS||+3545830146|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00089012|||||||||||||||||||||||||20260403153000
ORC|RE|ADR20260403001|||||^^^20260403153000^^R||20260403153000|PHARM006^Bárður^Stefánsson|||||LYFJABUD_LAUGAVEGAR
OBR|1|ADR20260403001||ADR^Adverse Drug Reaction Report^ISLYF|||20260403150000|||||||||PHARM006^Bárður^Stefánsson||||||||F
OBX|1|CE|DRUG^Suspected Drug^ISLYF||00234^Ibuprofen 400mg^ISLYF||||||F|||20260403150000
OBX|2|TX|REACTION^Adverse Reaction Description^ISLYF||Severe gastric bleeding after 3 days of use||||||F|||20260403150000
OBX|3|CE|SEVERITY^Reaction Severity^ISLYF||SV^Severe^HL70078||||||F|||20260403150000
```

---

## 9. ORM^O01 - Controlled substance order

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|HEILSUGAESLAN|20260405091500||ORM^O01|MSG00009|P|2.4
PID|1||1810973862^^^ISLAND^KT||Reynisson^Andrés^||19971018|M|||Klébergsvegur 5^^Reykjavík^^104^IS||+3545204793|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00090123|||||||||||||||||||||||||20260405091500
ORC|NW|RX20260405012|||||^^^20260405091500^^R||20260405091500|PHARM007^Ásdís^Hauksdóttir|||||LYFJABUD_LAUGAVEGAR
RXO|02100^Morphine sulfate 10mg tablets^ISLYF||10|mg|TAB^Tablet||^^Take one tablet every 4-6 hours as needed for pain|G||20|TAB
NTE|1||Controlled substance - Class II. DEA verification completed. Prescription valid 30 days.
```

---

## 10. ORM^O01 - Chemotherapy medication order

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260408100000||ORM^O01|MSG00010|P|2.4
PID|1||0210651927^^^ISLAND^KT||Vilbergsdóttir^Sólveig^Hlín||19651002|F|||Hjarðarhagi 41^^Reykjavík^^107^IS||+3545923106|||IS
PV1|1|I|LSH_ONCO^^^^BED8|||||||ONC||||||||A00101234|||||||||||||||||||||||||20260407080000
ORC|NW|RX20260408015|||||^^^20260408100000^^S||20260408100000|PHARM008^Hilmar^Bragason|||||SJUKRAHUSAPOTEK_LSH
RXO|03400^Cyclophosphamide 600mg/m2 IV^ISLYF||1020|mg|IV^Intravenous||^^Infuse in 500mL NaCl 0.9% over 60 minutes, cycle 3 day 1|G||1|VIAL
RXR|IV^Intravenous
NTE|1||Protocol: AC regimen cycle 3/4. BSA 1.70m2. Pre-medicate with ondansetron 8mg IV 30 min prior.
```

---

## 11. ORU^R01 - Medication reconciliation report

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260410140000||ORU^R01|MSG00011|P|2.4
PID|1||0508421760^^^ISLAND^KT||Pálsson^Hjörleifur^Reynir||19420805|M|||Bárugata 6^^Reykjavík^^101^IS||+3545049217|||IS
PV1|1|I|LSH_6C^^^^BED11|||||||GER||||||||A00112345|||||||||||||||||||||||||20260409100000
ORC|RE|MEDREC20260410001|||||^^^20260410140000^^R||20260410140000|PHARM009^Þórgunnur^Ölvirsdóttir|||||SJUKRAHUSAPOTEK_LSH
OBR|1|MEDREC20260410001||MEDREC^Medication Reconciliation^ISLYF|||20260410130000|||||||||PHARM009^Þórgunnur^Ölvirsdóttir||||||||F
OBX|1|TX|HOMEMEDLIST^Home Medication List^ISLYF||Atorvastatin 40mg daily, Metoprolol 50mg twice daily, Aspirin 75mg daily, Omeprazole 20mg daily||||||F|||20260410133000
OBX|2|TX|DISCREPANCY^Identified Discrepancy^ISLYF||Lisinopril 10mg daily documented in primary care records but not reported by patient. Confirmed discontinued 2 months ago by GP.||||||F|||20260410133000
OBX|3|TX|RECOMMENDATION^Pharmacist Recommendation^ISLYF||Remove Lisinopril from active medication list. Continue current home medications unchanged.||||||F|||20260410133000
```

---

## 12. SIU^S12 - Schedule medication counselling

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|HEILSUGAESLAN|20260412090000||SIU^S12|MSG00012|P|2.4
SCH|APT20260415001|||||MEDCOUN^Medication Counselling^ISLYF|||||15|min|^^15^20260415100000^20260415101500|PHARM010^Þuríður^Marteinsdóttir|+3545551234|LYFJABUD_LAUGAVEGAR|||||Booked
PID|1||2306013478^^^ISLAND^KT||Þrastarsson^Friðrik^Hauk||20010623|M|||Furugrund 3^^Kópavogur^^200^IS||+3545438217|||IS
AIG|1||PHARM010^Þuríður^Marteinsdóttir^^^^^APOTK|PHR
AIL|1||LYFJABUD_LAUGAVEGAR^Counselling Room 1
NTE|1||New asthma inhaler technique counselling. Patient starting Symbicort Turbuhaler 200/6.
```

---

## 13. MDM^T02 - Pharmacist clinical note

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260414160000||MDM^T02|MSG00013|P|2.4
EVN|T02|20260414160000
PID|1||1908542913^^^ISLAND^KT||Höskuldsdóttir^Aðalbjörg^Lára||19540819|F|||Háahlíð 11^^Reykjavík^^105^IS||+3545672410|||IS
PV1|1|I|LSH_7B^^^^BED3|||||||MED||||||||A00123456|||||||||||||||||||||||||20260412090000
TXA|1|CN^Clinical Note|TX|20260414155000||20260414160000|||||PHARM011^Birta^Egilsdóttir||DOC20260414001||AU^Authenticated
OBX|1|TX|CLINICALNOTE^Pharmacist Clinical Note^ISLYF||Patient reviewed for warfarin management. Current INR 2.8 (target 2.0-3.0). Dose maintained at 5mg daily Mon-Fri, 2.5mg Sat-Sun. Patient counselled on dietary vitamin K consistency. Next INR check scheduled in 2 weeks.||||||F|||20260414155000
```

---

## 14. ORU^R01 - Drug interaction alert report

```
MSH|^~\&|LYFJAVAKI|LYFJAVER_KOPAVOGS|SAGA|HEILSUGAESLAN|20260416111500||ORU^R01|MSG00014|P|2.4
PID|1||2510721598^^^ISLAND^KT||Ingólfsdóttir^Lilja^Brá||19721025|F|||Garðstún 14^^Mosfellsbær^^270^IS||+3545384217|||IS
PV1|1|O|LYFJAVER_KOPAVOGS^^^^APOTK|||||||PHR||||||||V00134567|||||||||||||||||||||||||20260416111500
ORC|RE|DIA20260416001|||||^^^20260416111500^^R||20260416111500|PHARM012^Skúli^Bjarnason|||||LYFJAVER_KOPAVOGS
OBR|1|DIA20260416001||DIA^Drug Interaction Alert^ISLYF|||20260416111000|||||||||PHARM012^Skúli^Bjarnason||||||||F
OBX|1|CE|DRUG1^Interacting Drug 1^ISLYF||00890^Warfarin 5mg^ISLYF||||||F|||20260416111000
OBX|2|CE|DRUG2^Interacting Drug 2^ISLYF||01345^Fluconazole 150mg^ISLYF||||||F|||20260416111000
OBX|3|CE|SEVERITY^Interaction Severity^ISLYF||HI^High^HL70078||||||F|||20260416111000
OBX|4|TX|CLINEFF^Clinical Effect^ISLYF||Fluconazole inhibits CYP2C9, significantly increasing warfarin plasma levels. Risk of major bleeding. Recommend INR monitoring within 3 days and warfarin dose reduction of 25-50%.||||||F|||20260416111000
```

---

## 15. ORM^O01 - Parenteral nutrition order

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260418090000||ORM^O01|MSG00015|P|2.4
PID|1||2902491347^^^ISLAND^KT||Sturluson^Hávar^Egill||19490229|M|||Þingvallastræti 26^^Akureyri^^600^IS||+3544631208|||IS
PV1|1|I|LSH_ICU^^^^BED1|||||||ICU||||||||A00145678|||||||||||||||||||||||||20260416200000
ORC|NW|RX20260418022|||||^^^20260418090000^^S||20260418090000|PHARM013^Vala^Brynjarsdóttir|||||SJUKRAHUSAPOTEK_LSH
RXO|09900^TPN Central Formula^ISLYF||2000|mL|IV^Intravenous||^^Infuse over 24 hours via central venous catheter|G||1|BAG
RXR|IV^Intravenous^CVC^Central Venous Catheter
NTE|1||Composition: Dextrose 250g, Amino acids 100g, Lipids 50g, Na 80mEq, K 40mEq, Mg 12mEq, Ca 10mEq, Phos 20mmol, MVI 10mL, Trace elements 5mL. Infusion rate 83mL/hr.
```

---

## 16. ORU^R01 - Medication dispensing with base64 ED OBX (PDF dispensing record)

```
MSH|^~\&|LYFJAVAKI|LYFJABUD_LAUGAVEGAR|SAGA|HEILSUGAESLAN|20260420143000||ORU^R01|MSG00016|P|2.4
PID|1||0708912756^^^ISLAND^KT||Hreinsdóttir^Margrét^Salka||19910807|F|||Stararimi 19^^Reykjavík^^112^IS||+3545819204|||IS
PV1|1|O|LYFJABUD_LAUGAVEGAR^^^^APOTK|||||||PHR||||||||V00156789|||||||||||||||||||||||||20260420143000
ORC|RE|DISP20260420001|||||^^^20260420143000^^R||20260420143000|PHARM014^Heimir^Daðason|||||LYFJABUD_LAUGAVEGAR
OBR|1|DISP20260420001||DISP^Medication Dispensing Record^ISLYF|||20260420142500|||||||||PHARM014^Heimir^Daðason||||||||F
OBX|1|TX|RXDISP^Dispensed Medication^ISLYF||Methotrexate 2.5mg tablets, qty 12, weekly dosing 15mg||||||F|||20260420142500
OBX|2|TX|COUNSELLING^Patient Counselling Notes^ISLYF||Patient counselled on weekly dosing schedule, folic acid supplementation, avoiding NSAIDs, and signs of hepatotoxicity and myelosuppression||||||F|||20260420142500
OBX|3|ED|PDF^Dispensing Record PDF^ISLYF||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCg||||||F
```

---

## 17. ADT^A31 - Update patient allergies

```
MSH|^~\&|LYFJAVAKI|LYFJAVER_KOPAVOGS|SAGA|HEILSUGAESLAN|20260422100000||ADT^A31|MSG00017|P|2.4
EVN|A31|20260422100000
PID|1||0709881362^^^ISLAND^KT||Kristbergsdóttir^Heiða^Marín||19880907|F|||Smárahvammur 12^^Akranes^^300^IS||+3544318027|||IS
PV1|1|O|LYFJAVER_KOPAVOGS^^^^APOTK|||||||PHR||||||||V00167890|||||||||||||||||||||||||20260422100000
AL1|1|DA|00456^Penicillin^ISLYF|SV|Angioedema and urticaria|20220610
AL1|2|DA|01890^Sulfonamides^ISLYF|MO|Skin rash|20230115
AL1|3|DA|02567^Codeine^ISLYF|SV|Respiratory depression|20240820
```

---

## 18. ORU^R01 - Pharmacy report with base64 ED OBX (PDF compounding record)

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260424110000||ORU^R01|MSG00018|P|2.4
PID|1||1505733418^^^ISLAND^KT||Eyjólfsson^Brjánn^Aron||19730515|M|||Smáragata 4^^Reykjavík^^101^IS||+3545709318|||IS
PV1|1|I|LSH_5A^^^^BED6|||||||PED||||||||A00178901|||||||||||||||||||||||||20260423140000
ORC|RE|COMP20260424001|||||^^^20260424110000^^R||20260424110000|PHARM015^Sólveig^Ríkharðsdóttir|||||SJUKRAHUSAPOTEK_LSH
OBR|1|COMP20260424001||COMP^Compounding Record^ISLYF|||20260424100000|||||||||PHARM015^Sólveig^Ríkharðsdóttir||||||||F
OBX|1|TX|COMPOUND^Compounded Preparation^ISLYF||Omeprazole 2mg/mL oral suspension, 100mL. Compounded from omeprazole 20mg capsules in sodium bicarbonate 8.4% solution.||||||F|||20260424103000
OBX|2|TX|STABILITY^Stability and Storage^ISLYF||Store refrigerated 2-8C. Beyond-use date 14 days from compounding. Shake well before each use.||||||F|||20260424103000
OBX|3|ED|PDF^Compounding Record PDF^ISLYF||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKENvbXBvdW5kaW5nIFJlY29yZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago||||||F
```

---

## 19. ADT^A01 - Admission with medication list

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|HEKLA|LANDSPITALI|20260426180000||ADT^A01|MSG00019|P|2.4
EVN|A01|20260426180000
PID|1||1306561042^^^ISLAND^KT||Ólafsdóttir^Bergljót^Tinna||19560613|F|||Lerkimói 6^^Hafnarfjörður^^221^IS||+3545631920|||IS
PV1|1|I|LSH_9A^^^^BED4|||||||CAR||||||||A00189012|||||||||||||||||||||||||20260426180000
AL1|1|DA|00789^Aspirin^ISLYF|MI|Gastric ulceration|20200305
DG1|1||I25.1^Atherosclerotic heart disease^ICD10||20260426|A
RXO|00567^Atorvastatin 80mg tablets^ISLYF||80|mg|TAB^Tablet||^^Take one tablet daily at bedtime|G||30|TAB
RXO|01234^Clopidogrel 75mg tablets^ISLYF||75|mg|TAB^Tablet||^^Take one tablet daily|G||30|TAB
RXO|02345^Metoprolol succinate 100mg tablets^ISLYF||100|mg|TAB^Tablet||^^Take one tablet daily in the morning|G||30|TAB
RXO|03456^Ramipril 5mg capsules^ISLYF||5|mg|CAP^Capsule||^^Take one capsule daily|G||30|CAP
```

---

## 20. ORM^O01 - Discharge prescription

```
MSH|^~\&|LYFJAVAKI|SJUKRAHUSAPOTEK_LSH|SAGA|HEILSUGAESLAN|20260428120000||ORM^O01|MSG00020|P|2.4
PID|1||1907441685^^^ISLAND^KT||Þórbergsson^Ingjaldur^Smári||19440719|M|||Ásbraut 3^^Reykjanesbær^^230^IS||+3544207013|||IS
PV1|1|I|LSH_6A^^^^BED7|||||||MED||||||||A00190123|||||||||||||||||||||||||20260423090000
ORC|NW|RX20260428030|||||^^^20260428120000^^R||20260428120000|PHARM016^Védís^Tryggvadóttir|||||SJUKRAHUSAPOTEK_LSH
RXO|00567^Atorvastatin 20mg tablets^ISLYF||20|mg|TAB^Tablet||^^Take one tablet daily in the evening|G||90|TAB
RXO|01890^Amlodipine 5mg tablets^ISLYF||5|mg|TAB^Tablet||^^Take one tablet daily in the morning|G||90|TAB
RXO|02100^Pantoprazole 40mg tablets^ISLYF||40|mg|TAB^Tablet||^^Take one tablet daily before breakfast|G||90|TAB
NTE|1||Discharge prescription. 90-day supply for all medications. Follow-up with primary care physician within 2 weeks. Continue medication reconciliation at community pharmacy.
```
