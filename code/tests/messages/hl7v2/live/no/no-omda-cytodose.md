# Omda Cytodose - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Chemotherapy order for FOLFOX regimen

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|DIPS_ARENA|OUS|20240315091200||ORM^O01^ORM_O01|MSG00001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||12036748291^^^OUS^PI||Haugen^Kristine^Marie||19680312|F|||Kirkeveien 45^^Oslo^^0368^NO||47912345678|||||||||||||||||N
PV1|1|O|ONKO1^204^01^RADIUMHOSPITALET||||12345^Lindgren^Erik^Johan^^^dr|||ONK||||||||V123456|||||||||||||||||||||||||20240315
ORC|NW|CYT-2024-001|CYT-2024-001||CM||1^QD^D4||20240315091200|12345^Lindgren^Erik^Johan^^^dr||12345^Lindgren^Erik^Johan^^^dr|ONKO1
RXO|L01BC02^fluorouracil^ATC|400|mg/m2||IV||A^Infusjon over 46 timer||||||||||FOLFOX6^Syklus 3 av 12
RXO|L01XA03^oksaliplatin^ATC|85|mg/m2||IV||A^Infusjon over 2 timer||||||||||FOLFOX6^Syklus 3 av 12
RXO|L01BA04^kalsiumfolinat^ATC|400|mg/m2||IV||A^Infusjon over 2 timer||||||||||FOLFOX6^Syklus 3 av 12
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.82|m2|||||F
OBX|2|ST|PROTO^Protokoll^LOCAL||FOLFOX6 - Kolorektalcancer||||||F
```

---

## 2. ADT^A01 - Admission to chemotherapy day-unit

```
MSH|^~\&|CYTODOSE|HAUKELAND|DIPS_ARENA|HAUKELAND|20240410080000||ADT^A01^ADT_A01|MSG00002|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20240410080000||||20240410075500
PID|1||15057832145^^^HAUKELAND^PI||Olsen^Bjørn^Anders||19780515|M|||Nygårdsgaten 12^^Bergen^^5015^NO||47923456789|||||||||||||||||N
PV1|1|O|KJEMO1^301^02^HAUKELAND||||23456^Berge^Silje^Kristin^^^dr|||ONK||||||||V234567|||||||||||||||||||||||||20240410
DG1|1|ICD10|C34.1^Malign svulst i øvre lungelapp^ICD10||20240201|A
```

---

## 3. ORU^R01 - Pre-chemo CBC lab results

```
MSH|^~\&|CYTODOSE|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240522063000||ORU^R01^ORU_R01|MSG00003|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||08089143567^^^ST_OLAVS^PI||Nordmann^Ingrid^Sofie||19910808|F|||Elgeseter gate 22^^Trondheim^^7030^NO||47934567890|||||||||||||||||N
PV1|1|O|ONKO2^105^01^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK
ORC|RE|LAB-2024-103||LAB-2024-103|CM
OBR|1|LAB-2024-103||58410-2^CBC^LN|||20240522060000||||||||34567^Aasen^Per^Olav^^^dr
OBX|1|NM|6690-2^Leukocytter^LN||4.8|10*9/L|3.5-10.0||||F|||20240522063000
OBX|2|NM|789-8^Erytrocytter^LN||4.2|10*12/L|3.9-5.5||||F|||20240522063000
OBX|3|NM|777-3^Trombocytter^LN||185|10*9/L|145-390||||F|||20240522063000
OBX|4|NM|718-7^Hemoglobin^LN||12.8|g/dL|11.7-15.3||||F|||20240522063000
OBX|5|NM|26499-4^Nøytrofile^LN||3.1|10*9/L|1.5-7.5||||F|||20240522063000
```

---

## 4. RDE^O11 - Pharmacy dispensing order for carboplatin

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|APOTEK|OUS_APOTEK|20240318140000||RDE^O11^RDE_O11|MSG00004|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||22126789012^^^OUS^PI||Dahl^Henrik^Morten||19671222|M|||Sognsveien 85^^Oslo^^0855^NO||47945678901|||||||||||||||||N
PV1|1|O|ONKO1^204^03^RADIUMHOSPITALET||||45678^Sørensen^Marte^Helene^^^dr|||ONK
ORC|NW|PHA-2024-045|PHA-2024-045||IP||1^^D1||20240318140000|45678^Sørensen^Marte^Helene^^^dr
RXE|1^QD^D1|L01XA02^karboplatin^ATC|600|mg||IV|A^Infusjon over 60 min^HL70162|||||||||||||||AUC 5
RXR|IV^Intravenøs^HL70162||LA^Venstre arm^HL70163
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.95|m2|||||F
OBX|2|NM|GFR^Glomerulær filtrasjonsrate^LOCAL||88|mL/min|||||F
```

---

## 5. ORM^O01 - Paclitaxel order for breast cancer

```
MSH|^~\&|OMDA_CYTO|UNN|DIPS_ARENA|UNN|20240603100500||ORM^O01^ORM_O01|MSG00005|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||30048756234^^^UNN^PI||Johansen^Astrid^Elise||19870430|F|||Storgata 8^^Tromsø^^9008^NO||47956789012|||||||||||||||||N
PV1|1|O|KJEMO1^402^01^UNN||||56789^Hansen^Knut^Ivar^^^dr|||ONK||||||||V345678|||||||||||||||||||||||||20240603
ORC|NW|CYT-2024-088|CYT-2024-088||CM||1^Q1W^W12||20240603100500|56789^Hansen^Knut^Ivar^^^dr||56789^Hansen^Knut^Ivar^^^dr|KJEMO1
RXO|L01CD01^paklitaksel^ATC|80|mg/m2||IV||A^Infusjon over 60 min||||||||||EC-T^Syklus 5 av 12 (T-fase)
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.68|m2|||||F
OBX|2|ST|PROTO^Protokoll^LOCAL||EC-T - Brystcancer stadium III||||||F
OBX|3|ST|ALLERGI^Premedisinering^LOCAL||Deksametason 20mg + Klemastin 2mg gitt||||||F
```

---

## 6. ADT^A03 - Discharge from chemo day-unit

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|DIPS_ARENA|OUS|20240315163000||ADT^A03^ADT_A03|MSG00006|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20240315163000||||20240315162800
PID|1||12036748291^^^OUS^PI||Haugen^Kristine^Marie||19680312|F|||Kirkeveien 45^^Oslo^^0368^NO||47912345678|||||||||||||||||N
PV1|1|O|ONKO1^204^01^RADIUMHOSPITALET||||12345^Lindgren^Erik^Johan^^^dr|||ONK||||||||V123456|||||||||||||||||||||||20240315|20240315163000
DG1|1|ICD10|C18.2^Malign svulst i colon ascendens^ICD10||20231115|A
```

---

## 7. ORU^R01 - Liver function tests before docetaxel

```
MSH|^~\&|CYTODOSE|HAUKELAND|DIPS_ARENA|HAUKELAND|20240411055500||ORU^R01^ORU_R01|MSG00007|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||15057832145^^^HAUKELAND^PI||Olsen^Bjørn^Anders||19780515|M|||Nygårdsgaten 12^^Bergen^^5015^NO||47923456789|||||||||||||||||N
PV1|1|O|KJEMO1^301^02^HAUKELAND||||23456^Berge^Silje^Kristin^^^dr|||ONK
ORC|RE|LAB-2024-207||LAB-2024-207|CM
OBR|1|LAB-2024-207||24326-1^Leverfunksjon^LN|||20240411053000||||||||23456^Berge^Silje^Kristin^^^dr
OBX|1|NM|1742-6^ALAT^LN||28|U/L|10-70||||F|||20240411055500
OBX|2|NM|1920-8^ASAT^LN||32|U/L|15-45||||F|||20240411055500
OBX|3|NM|1975-2^Bilirubin total^LN||14|umol/L|5-25||||F|||20240411055500
OBX|4|NM|6768-6^Alkalisk fosfatase^LN||72|U/L|35-105||||F|||20240411055500
OBX|5|NM|2324-2^GGT^LN||45|U/L|10-80||||F|||20240411055500
```

---

## 8. ORM^O01 - Cisplatin/gemcitabine order for bladder cancer

```
MSH|^~\&|CYTODOSE|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240605083000||ORM^O01^ORM_O01|MSG00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||17115634789^^^ST_OLAVS^PI||Eriksen^Torbjørn^Åge||19561117|M|||Innherredsveien 72^^Trondheim^^7042^NO||47967890123|||||||||||||||||N
PV1|1|O|ONKO2^105^03^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK||||||||V456789|||||||||||||||||||||||||20240605
ORC|NW|CYT-2024-112|CYT-2024-112||CM||1^QD^D1||20240605083000|34567^Aasen^Per^Olav^^^dr||34567^Aasen^Per^Olav^^^dr|ONKO2
RXO|L01XA01^cisplatin^ATC|70|mg/m2||IV||A^Infusjon over 4 timer||||||||||GC^Syklus 2 av 6 Dag 1
RXO|L01BC05^gemcitabin^ATC|1000|mg/m2||IV||A^Infusjon over 30 min||||||||||GC^Syklus 2 av 6 Dag 1
OBX|1|NM|BSA^Body Surface Area^LOCAL||2.04|m2|||||F
OBX|2|NM|GFR^Glomerulær filtrasjonsrate^LOCAL||72|mL/min|||||F
OBX|3|ST|HYDRASJON^Hydrering^LOCAL||NaCl 1000ml pre og post cisplatin||||||F
```

---

## 9. ADT^A04 - Outpatient registration for chemo consultation

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|DIPS_ARENA|OUS|20240320093000||ADT^A04^ADT_A04|MSG00009|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20240320093000||||20240320092500
PID|1||05039245678^^^OUS^PI||Martinsen^Lars^Øyvind||19920305|M|||Grønlandsleiret 33^^Oslo^^0190^NO||47978901234|||||||||||||||||N
PV1|1|O|ONKO1^210^01^RADIUMHOSPITALET||||67890^Fredriksen^Anne^Cathrine^^^dr|||ONK||||||||V567890|||||||||||||||||||||||||20240320
DG1|1|ICD10|C62.1^Malign svulst i testikkel^ICD10||20240215|A
```

---

## 10. ORM^O01 - Doxorubicin/cyclophosphamide (AC) order

```
MSH|^~\&|OMDA_CYTO|HAUKELAND|DIPS_ARENA|HAUKELAND|20240417091500||ORM^O01^ORM_O01|MSG00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||28077845123^^^HAUKELAND^PI||Pedersen^Marit^Ågot||19780728|F|||Fjøsangerveien 19^^Bergen^^5054^NO||47989012345|||||||||||||||||N
PV1|1|O|KJEMO1^301^04^HAUKELAND||||23456^Berge^Silje^Kristin^^^dr|||ONK||||||||V678901|||||||||||||||||||||||||20240417
ORC|NW|CYT-2024-134|CYT-2024-134||CM||1^Q3W^W4||20240417091500|23456^Berge^Silje^Kristin^^^dr||23456^Berge^Silje^Kristin^^^dr|KJEMO1
RXO|L01DB01^doksorubicin^ATC|60|mg/m2||IV||A^Infusjon over 15 min||||||||||AC^Syklus 2 av 4
RXO|L01AA01^cyklofosfamid^ATC|600|mg/m2||IV||A^Infusjon over 30 min||||||||||AC^Syklus 2 av 4
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.72|m2|||||F
OBX|2|ST|KARDIO^Ekkokardiografi^LOCAL||LVEF 62% - innenfor normalområdet||||||F
```

---

## 11. ORU^R01 - Renal function before cisplatin with ED segment (treatment protocol PDF)

```
MSH|^~\&|CYTODOSE|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240606070000||ORU^R01^ORU_R01|MSG00011|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||17115634789^^^ST_OLAVS^PI||Eriksen^Torbjørn^Åge||19561117|M|||Innherredsveien 72^^Trondheim^^7042^NO||47967890123|||||||||||||||||N
PV1|1|O|ONKO2^105^03^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK
ORC|RE|LAB-2024-310||LAB-2024-310|CM
OBR|1|LAB-2024-310||33914-3^Nyrefunksjon^LN|||20240606063000||||||||34567^Aasen^Per^Olav^^^dr
OBX|1|NM|2160-0^Kreatinin^LN||98|umol/L|60-105||||F|||20240606070000
OBX|2|NM|33914-3^eGFR^LN||72|mL/min/1.73m2|>60||||F|||20240606070000
OBX|3|NM|2823-3^Kalium^LN||4.1|mmol/L|3.5-5.0||||F|||20240606070000
OBX|4|NM|2951-2^Natrium^LN||140|mmol/L|137-145||||F|||20240606070000
OBX|5|NM|17861-6^Kalsium^LN||2.35|mmol/L|2.15-2.55||||F|||20240606070000
OBX|6|ED|PDF^Behandlingsprotokoll^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEdDIFByb3Rva29sbCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F
```

---

## 12. RDE^O11 - Pharmacy order for 5-FU continuous infusion pump

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|APOTEK|OUS_APOTEK|20240316080000||RDE^O11^RDE_O11|MSG00012|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||12036748291^^^OUS^PI||Haugen^Kristine^Marie||19680312|F|||Kirkeveien 45^^Oslo^^0368^NO||47912345678|||||||||||||||||N
PV1|1|O|ONKO1^204^01^RADIUMHOSPITALET||||12345^Lindgren^Erik^Johan^^^dr|||ONK
ORC|NW|PHA-2024-078|PHA-2024-078||IP||1^^D2||20240316080000|12345^Lindgren^Erik^Johan^^^dr
RXE|1^^D2|L01BC02^fluorouracil^ATC|2400|mg||IV|C^Kontinuerlig infusjon 46t^HL70162|||||||||||||||Bærbar pumpe
RXR|IV^Intravenøs^HL70162||CVK^Sentralt venekateter^HL70163
RXE|2^^D1|L01BA04^kalsiumfolinat^ATC|400|mg||IV|A^Infusjon over 2 timer^HL70162
RXR|IV^Intravenøs^HL70162||CVK^Sentralt venekateter^HL70163
```

---

## 13. ORM^O01 - BEP chemotherapy for testicular cancer

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|DIPS_ARENA|OUS|20240321090000||ORM^O01^ORM_O01|MSG00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||05039245678^^^OUS^PI||Martinsen^Lars^Øyvind||19920305|M|||Grønlandsleiret 33^^Oslo^^0190^NO||47978901234|||||||||||||||||N
PV1|1|O|ONKO1^210^02^RADIUMHOSPITALET||||67890^Fredriksen^Anne^Cathrine^^^dr|||ONK||||||||V789012|||||||||||||||||||||||||20240321
ORC|NW|CYT-2024-055|CYT-2024-055||CM||1^QD^D5||20240321090000|67890^Fredriksen^Anne^Cathrine^^^dr||67890^Fredriksen^Anne^Cathrine^^^dr|ONKO1
RXO|L01XA01^cisplatin^ATC|20|mg/m2||IV||A^Infusjon over 1 time||||||||||BEP^Syklus 1 av 3 Dag 1-5
RXO|L01CB01^etoposid^ATC|100|mg/m2||IV||A^Infusjon over 1 time||||||||||BEP^Syklus 1 av 3 Dag 1-5
RXO|L01DC01^bleomycin^ATC|30|enheter||IV||A^Bolus over 10 min||||||||||BEP^Syklus 1 av 3 Dag 2,9,16
OBX|1|NM|BSA^Body Surface Area^LOCAL||2.01|m2|||||F
OBX|2|ST|PROTO^Protokoll^LOCAL||BEP - Germinalcelletumor stadium IIB||||||F
```

---

## 14. ORU^R01 - Tumor markers during chemo (AFP, hCG)

```
MSH|^~\&|CYTODOSE|RADIUMHOSPITALET|DIPS_ARENA|OUS|20240405070000||ORU^R01^ORU_R01|MSG00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||05039245678^^^OUS^PI||Martinsen^Lars^Øyvind||19920305|M|||Grønlandsleiret 33^^Oslo^^0190^NO||47978901234|||||||||||||||||N
PV1|1|O|ONKO1^210^02^RADIUMHOSPITALET||||67890^Fredriksen^Anne^Cathrine^^^dr|||ONK
ORC|RE|LAB-2024-412||LAB-2024-412|CM
OBR|1|LAB-2024-412||TUMOR^Tumormarkører^LOCAL|||20240405063000||||||||67890^Fredriksen^Anne^Cathrine^^^dr
OBX|1|NM|1834-1^AFP^LN||12.5|kU/L|<7.0|H|||F|||20240405070000
OBX|2|NM|19080-1^hCG^LN||3.2|IU/L|<5.0||||F|||20240405070000
OBX|3|NM|2532-0^LDH^LN||245|U/L|105-205|H|||F|||20240405070000
```

---

## 15. ADT^A01 - Admission for high-dose methotrexate

```
MSH|^~\&|OMDA_CYTO|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240610070000||ADT^A01^ADT_A01|MSG00015|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20240610070000||||20240610065500
PID|1||14029867345^^^ST_OLAVS^PI||Strand^Eirik^Håvard||19980214|M|||Wessels gate 5^^Trondheim^^7013^NO||47990123456|||||||||||||||||N
PV1|1|I|ONKO2^108^01^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK||||||||V890123|||||||||||||||||||||||||20240610
DG1|1|ICD10|C40.2^Malign svulst i lange rørknokler - underekstremitet^ICD10||20240501|A
DG1|2|ICD10|C40^Osteosarkom^ICD10||20240501|A
```

---

## 16. ORM^O01 - High-dose methotrexate with leucovorin rescue

```
MSH|^~\&|OMDA_CYTO|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240610090000||ORM^O01^ORM_O01|MSG00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||14029867345^^^ST_OLAVS^PI||Strand^Eirik^Håvard||19980214|M|||Wessels gate 5^^Trondheim^^7013^NO||47990123456|||||||||||||||||N
PV1|1|I|ONKO2^108^01^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK||||||||V890123|||||||||||||||||||||||||20240610
ORC|NW|CYT-2024-156|CYT-2024-156||CM||1^QD^D1||20240610090000|34567^Aasen^Per^Olav^^^dr||34567^Aasen^Per^Olav^^^dr|ONKO2
RXO|L01BA01^metotreksat^ATC|12000|mg/m2||IV||A^Infusjon over 4 timer||||||||||EURAMOS^Syklus 4 - HD-MTX
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.91|m2|||||F
OBX|2|ST|PROTO^Protokoll^LOCAL||EURAMOS - Osteosarkom HD-MTX med leukovorinrescue||||||F
OBX|3|ST|RESCUE^Leukovorin^LOCAL||Start 24t etter MTX-start, 15mg/m2 q6h inntil MTX <0.1 umol/L||||||F
OBX|4|ST|HYDRASJON^Hydrering^LOCAL||NaCl/Glukose 3000mL/m2/døgn, urin-pH >7.0||||||F
```

---

## 17. ORU^R01 - Methotrexate serum levels monitoring

```
MSH|^~\&|CYTODOSE|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240611180000||ORU^R01^ORU_R01|MSG00017|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||14029867345^^^ST_OLAVS^PI||Strand^Eirik^Håvard||19980214|M|||Wessels gate 5^^Trondheim^^7013^NO||47990123456|||||||||||||||||N
PV1|1|I|ONKO2^108^01^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK
ORC|RE|LAB-2024-488||LAB-2024-488|CM
OBR|1|LAB-2024-488||4084-5^Metotreksat serum^LN|||20240611174500||||||||34567^Aasen^Per^Olav^^^dr
OBX|1|NM|4084-5^MTX 24t^LN||8.5|umol/L|<10||||F|||20240611180000
OBX|2|NM|4084-5^MTX 48t^LN||0.45|umol/L|<1.0||||F|||20240611180000
OBX|3|NM|2160-0^Kreatinin^LN||92|umol/L|60-105||||F|||20240611180000
OBX|4|ST|URIN_PH^Urin pH^LOCAL||7.4||>7.0||||F|||20240611180000
```

---

## 18. ORM^O01 - Gemcitabine monotherapy with ED treatment plan document

```
MSH|^~\&|CYTODOSE|UNN|DIPS_ARENA|UNN|20240701083000||ORM^O01^ORM_O01|MSG00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||09064523891^^^UNN^PI||Karlsen^Ragnhild^Åse||19450609|F|||Sjøgata 14^^Tromsø^^9008^NO||47901234567|||||||||||||||||N
PV1|1|O|KJEMO1^402^03^UNN||||56789^Hansen^Knut^Ivar^^^dr|||ONK||||||||V901234|||||||||||||||||||||||||20240701
ORC|NW|CYT-2024-201|CYT-2024-201||CM||1^Q1W^W3||20240701083000|56789^Hansen^Knut^Ivar^^^dr||56789^Hansen^Knut^Ivar^^^dr|KJEMO1
RXO|L01BC05^gemcitabin^ATC|1000|mg/m2||IV||A^Infusjon over 30 min||||||||||GEM-MONO^Syklus 1 av 6 Dag 1,8,15
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.58|m2|||||F
OBX|2|ST|PROTO^Protokoll^LOCAL||Gemcitabin monoterapi - Pankreaskreft stadium IV||||||F
OBX|3|ED|PDF^Behandlingsplan^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1Nwo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEdlbWNpdGFiaW4gQmVoYW5kbGluZ3NwbGFuKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCg==||||||F
```

---

## 19. ADT^A03 - Discharge after HD-MTX with follow-up instructions

```
MSH|^~\&|OMDA_CYTO|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20240613140000||ADT^A03^ADT_A03|MSG00019|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20240613140000||||20240613135500
PID|1||14029867345^^^ST_OLAVS^PI||Strand^Eirik^Håvard||19980214|M|||Wessels gate 5^^Trondheim^^7013^NO||47990123456|||||||||||||||||N
PV1|1|I|ONKO2^108^01^ST_OLAVS||||34567^Aasen^Per^Olav^^^dr|||ONK||||||||V890123|||||||||||||||||||||||20240610|20240613140000
DG1|1|ICD10|C40.2^Malign svulst i lange rørknokler - underekstremitet^ICD10||20240501|A
OBX|1|ST|UTSKR^Utskrivningsnotat^LOCAL||MTX-nivå <0.1 umol/L. Kreatinin normal. Neste kur planlagt 20240624.||||||F
```

---

## 20. RDE^O11 - Pharmacy preparation of doxorubicin with dose verification

```
MSH|^~\&|OMDA_CYTO|HAUKELAND|APOTEK|HAUKELAND_APOTEK|20240418100000||RDE^O11^RDE_O11|MSG00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||28077845123^^^HAUKELAND^PI||Pedersen^Marit^Ågot||19780728|F|||Fjøsangerveien 19^^Bergen^^5054^NO||47989012345|||||||||||||||||N
PV1|1|O|KJEMO1^301^04^HAUKELAND||||23456^Berge^Silje^Kristin^^^dr|||ONK
ORC|NW|PHA-2024-112|PHA-2024-112||IP||1^^D1||20240418100000|23456^Berge^Silje^Kristin^^^dr
RXE|1^^D1|L01DB01^doksorubicin^ATC|103.2|mg||IV|A^Infusjon over 15 min^HL70162|||||||||||||||BSA 1.72 x 60mg/m2
RXR|IV^Intravenøs^HL70162||PORT^Veneport^HL70163
RXE|2^^D1|L01AA01^cyklofosfamid^ATC|1032|mg||IV|A^Infusjon over 30 min^HL70162|||||||||||||||BSA 1.72 x 600mg/m2
RXR|IV^Intravenøs^HL70162||PORT^Veneport^HL70163
OBX|1|NM|BSA^Body Surface Area^LOCAL||1.72|m2|||||F
OBX|2|ST|DOSE_VER^Doseverifikasjon^LOCAL||Kontrollert av farmasøyt Nilsen 20240418 kl 0945||||||F
```
