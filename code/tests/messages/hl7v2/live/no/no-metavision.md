# MetaVision (iMDsoft) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - ICU admission

```
MSH|^~\&|METAVISION|OUS_RIKSHOSP|DIPS_ARENA|OUS|20250312083015||ADT^A01^ADT_A01|MV20250312083015001|P|2.5|||AL|NE||UNICODE UTF-8|||
EVN|A01|20250312083015|||dsuch^Sørensen^Kari^L
PID|1||12038749832^^^OUS^MR~12038749832^^^FOLKEREG^FNR||Haugen^Ingrid^Marie^^Fru||19830312|F|||Kirkegata 14^^Oslo^^0153^NOR||+4722334455~+4791234567||NO|G|||12038749832||||Oslo|||
PV1|1|I|INTOV^4102^01^OUS_RIKSHOSP^^^^Intensivavdeling|||INTOV^4102^01|178432^Nilsen^Erik^Johan^^Dr|||INT||7|||178432^Nilsen^Erik^Johan^^Dr|I||SI|||||||||||||||||||OUS|||||20250312083000|||
PV2|||^Sepsis med multiorgansvikt||||||||3|||||||||||||||||||||||||
DG1|1||A41.9^Sepsis, uspesifisert^ICD-10||20250312|A|
IN1|1||7700^Helfo|||||||||||||||||||||||||||
```

---

## 2. ADT^A02 - Transfer from general ward to ICU

```
MSH|^~\&|METAVISION|HUS_HAUKELAND|DIPS_ARENA|HUS|20250415141230||ADT^A02^ADT_A02|MV20250415141230002|P|2.5|||AL|NE||UNICODE UTF-8|||
EVN|A02|20250415141230|||hberge^Berg^Henrik^M
PID|1||15075598321^^^HUS^MR~15075598321^^^FOLKEREG^FNR||Johansen^Lars^Henrik||19550715|M|||Bryggen 7^^Bergen^^5003^NOR||+4755667788~+4798765432||NO|G|||15075598321||||Bergen|||
PV1|1|I|INTM^3201^02^HUS_HAUKELAND^^^^Medisinsk intensiv|||KIR^2105^01|203876^Andersen^Marit^Sofie^^Dr|||INT||7|||203876^Andersen^Marit^Sofie^^Dr|I||SI|||||||||||||||||||HUS|||||20250415141200|||
PV2|||^Akutt respirasjonssvikt etter pneumoni||||||||4|||||||||||||||||||||||||
DG1|1||J96.0^Akutt respirasjonssvikt^ICD-10||20250415|A|
```

---

## 3. ORU^R01 - Arterial blood gas results

```
MSH|^~\&|METAVISION|STOLAV_TRONDHEIM|LABSYS|STOLAV|20250507091545||ORU^R01^ORU_R01|MV20250507091545003|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||08069234567^^^STOLAV^MR~08069234567^^^FOLKEREG^FNR||Ødegård^Astrid^Helene||19920608|F|||Munkegata 22^^Trondheim^^7011^NOR||+4773889900||NO||||||||Trondheim|||
PV1|1|I|INTA^5103^01^STOLAV^^^^Intensivavdeling|||||156743^Brekke^Olav^Petter^^Dr|||INT|||||156743^Brekke^Olav^Petter^^Dr||||||||||||||||||||||||
ORC|RE|BG250507-001|BG250507-001||CM||||20250507091500|||156743^Brekke^Olav^Petter^^Dr||||||INTA^5103^01^STOLAV
OBR|1|BG250507-001|BG250507-001|82803-7^Blodgass arteriell^LN|||20250507091200||||||||156743^Brekke^Olav^Petter^^Dr|||||||||F|||||||
OBX|1|NM|2744-1^pH arteriell^LN||7.31|[pH]|7.35-7.45|L|||F|||20250507091200||METAVISION
OBX|2|NM|2019-8^pCO2 arteriell^LN||6.8|kPa|4.7-6.0|H|||F|||20250507091200||METAVISION
OBX|3|NM|2703-7^pO2 arteriell^LN||9.2|kPa|10.0-13.3|L|||F|||20250507091200||METAVISION
OBX|4|NM|1963-8^Bikarbonat^LN||18.4|mmol/L|22.0-26.0|L|||F|||20250507091200||METAVISION
OBX|5|NM|1925-7^Base Excess^LN||-6.8|mmol/L|-2.0-2.0|L|||F|||20250507091200||METAVISION
OBX|6|NM|2713-6^Laktat^LN||4.2|mmol/L|0.5-2.2|H|||F|||20250507091200||METAVISION
OBX|7|NM|20564-1^SpO2^LN||91|%|95-100|L|||F|||20250507091200||METAVISION
```

---

## 4. ORU^R01 - Vital signs from bedside monitor

```
MSH|^~\&|METAVISION|UNN_TROMSO|DIPS_ARENA|UNN|20250322160030||ORU^R01^ORU_R01|MV20250322160030004|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||21128856743^^^UNN^MR~21128856743^^^FOLKEREG^FNR||Karlsen^Trond^Arvid||19881221|M|||Storgata 45^^Tromsø^^9008^NOR||+4777112233||NO||||||||Tromsø|||
PV1|1|I|INTK^6201^03^UNN_TROMSO^^^^Kirurgisk intensiv|||||189234^Holm^Silje^Kristin^^Dr|||INT|||||189234^Holm^Silje^Kristin^^Dr||||||||||||||||||||||||
ORC|RE|VS250322-001|VS250322-001||CM||||20250322160000|||189234^Holm^Silje^Kristin^^Dr||||||INTK^6201^03^UNN
OBR|1|VS250322-001|VS250322-001|VITALS^Vitale parametere^MV|||20250322155500||||||||189234^Holm^Silje^Kristin^^Dr|||||||||F|||||||
OBX|1|NM|8480-6^Systolisk blodtrykk^LN||132|mm[Hg]|90-140|N|||F|||20250322155500||METAVISION
OBX|2|NM|8462-4^Diastolisk blodtrykk^LN||78|mm[Hg]|60-90|N|||F|||20250322155500||METAVISION
OBX|3|NM|8867-4^Hjertefrekvens^LN||94|/min|60-100|N|||F|||20250322155500||METAVISION
OBX|4|NM|9279-1^Respirasjonsfrekvens^LN||22|/min|12-20|H|||F|||20250322155500||METAVISION
OBX|5|NM|8310-5^Kroppstemperatur^LN||38.6|Cel|36.0-37.5|H|||F|||20250322155500||METAVISION
OBX|6|NM|20564-1^SpO2^LN||96|%|95-100|N|||F|||20250322155500||METAVISION
OBX|7|NM|60985-9^MAP invasiv^LN||96|mm[Hg]|70-105|N|||F|||20250322155500||METAVISION
```

---

## 5. ORM^O01 - ICU medication order (Noradrenalin infusion)

```
MSH|^~\&|METAVISION|AHUS_NORDBYHAGEN|DIPS_ARENA|AHUS|20250218103045||ORM^O01^ORM_O01|MV20250218103045005|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||04027612345^^^AHUS^MR~04027612345^^^FOLKEREG^FNR||Sæther^Morten^Bjørn||19760204|M|||Lillestrømveien 88^^Lillestrøm^^2000^NOR||+4763554433||NO||||||||Lillestrøm|||
PV1|1|I|INTG^1302^01^AHUS^^^^Generell intensiv|||||213456^Larsen^Tone^Marie^^Dr|||INT|||||213456^Larsen^Tone^Marie^^Dr||||||||||||||||||||||||
ORC|NW|RX250218-001||RX250218-001|SC||||20250218103000|||213456^Larsen^Tone^Marie^^Dr||||||INTG^1302^01^AHUS
OBR|1|RX250218-001||MEDRX^Medikamentordinasjon^MV|||20250218103000||||||||213456^Larsen^Tone^Marie^^Dr|||||||||SC|||||||
RXO|C01CA03^Noradrenalin^ATC||0.12|mcg/kg/min|IV^Intravenøs^HL70162||||||||||||
RXR|IV^Intravenøs^HL70162|CVL^Sentralt venekateter^MV|||
NTE|1||Titreres etter MAP > 65 mmHg. Kontroller blodtrykk hvert 5. minutt ved doseendring.
```

---

## 6. ORU^R01 - Ventilator settings and readings

```
MSH|^~\&|MV_ICU|SUS_STAVANGER|DIPS_ARENA|SUS|20250610070015||ORU^R01^ORU_R01|MV20250610070015006|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||17049378234^^^SUS^MR~17049378234^^^FOLKEREG^FNR||Lunde^Grete^Elin||19930417|F|||Vågen 3^^Stavanger^^4006^NOR||+4751223344||NO||||||||Stavanger|||
PV1|1|I|INTM^4201^02^SUS_STAVANGER^^^^Medisinsk intensiv|||||198765^Mæland^Geir^Arne^^Dr|||INT|||||198765^Mæland^Geir^Arne^^Dr||||||||||||||||||||||||
ORC|RE|VENT250610-001|VENT250610-001||CM||||20250610070000|||198765^Mæland^Geir^Arne^^Dr||||||INTM^4201^02^SUS
OBR|1|VENT250610-001|VENT250610-001|VENT^Ventilatordata^MV|||20250610065500||||||||198765^Mæland^Geir^Arne^^Dr|||||||||F|||||||
OBX|1|ST|VENT_MODE^Ventilasjonsmodus^MV||BIPAP|||N|||F|||20250610065500||METAVISION
OBX|2|NM|PEEP^PEEP^MV||10|cm[H2O]|5-15|N|||F|||20250610065500||METAVISION
OBX|3|NM|FIO2^FiO2^MV||0.55||0.21-1.0|N|||F|||20250610065500||METAVISION
OBX|4|NM|TV_SET^Tidalvolum innstilt^MV||450|mL|400-600|N|||F|||20250610065500||METAVISION
OBX|5|NM|TV_EXP^Tidalvolum ekspirert^MV||438|mL|||N|||F|||20250610065500||METAVISION
OBX|6|NM|RR_SET^Frekvens innstilt^MV||16|/min|||N|||F|||20250610065500||METAVISION
OBX|7|NM|RR_TOT^Frekvens total^MV||18|/min|||N|||F|||20250610065500||METAVISION
OBX|8|NM|PPEAK^Topptrykk^MV||26|cm[H2O]|<35|N|||F|||20250610065500||METAVISION
OBX|9|NM|PMEAN^Middeltrykk^MV||14|cm[H2O]|||N|||F|||20250610065500||METAVISION
OBX|10|NM|MV_EXP^Minuttvolum ekspirert^MV||7.9|L/min|||N|||F|||20250610065500||METAVISION
```

---

## 7. ORU^R01 - Glasgow Coma Scale assessment

```
MSH|^~\&|METAVISION|OUS_ULLEVAL|DIPS_ARENA|OUS|20250129142200||ORU^R01^ORU_R01|MV20250129142200007|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||30118745612^^^OUS^MR~30118745612^^^FOLKEREG^FNR||Berntsen^Einar^Olaf||19871130|M|||Grønlandsleiret 19^^Oslo^^0190^NOR||+4722998877||NO||||||||Oslo|||
PV1|1|I|INTN^4108^01^OUS_ULLEVAL^^^^Nevrokirurgisk intensiv|||||167823^Fossum^Ragnhild^Elise^^Dr|||INT|||||167823^Fossum^Ragnhild^Elise^^Dr||||||||||||||||||||||||
ORC|RE|GCS250129-001|GCS250129-001||CM||||20250129142100|||167823^Fossum^Ragnhild^Elise^^Dr||||||INTN^4108^01^OUS
OBR|1|GCS250129-001|GCS250129-001|GCS^Glasgow Coma Scale^MV|||20250129141500||||||||167823^Fossum^Ragnhild^Elise^^Dr|||||||||F|||||||
OBX|1|NM|9267-6^Glasgow Coma Scale total^LN||9|{score}|3-15||||F|||20250129141500||METAVISION
OBX|2|NM|9270-0^GCS øyeåpning^LN||3|{score}|1-4||||F|||20250129141500||METAVISION
OBX|3|NM|9268-4^GCS motorisk^LN||4|{score}|1-6||||F|||20250129141500||METAVISION
OBX|4|NM|9270-8^GCS verbal^LN||2|{score}|1-5||||F|||20250129141500||METAVISION
OBX|5|ST|PUPIL_L^Pupill venstre^MV||3 mm, reaktiv|||N|||F|||20250129141500||METAVISION
OBX|6|ST|PUPIL_R^Pupill høyre^MV||4 mm, treg|||A|||F|||20250129141500||METAVISION
```

---

## 8. ORU^R01 - SOFA score

```
MSH|^~\&|METAVISION|HUS_HAUKELAND|DIPS_ARENA|HUS|20250803061500||ORU^R01^ORU_R01|MV20250803061500008|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||22049156789^^^HUS^MR~22049156789^^^FOLKEREG^FNR||Tangen^Berit^Solveig||19910422|F|||Nygårdsgaten 5^^Bergen^^5015^NOR||+4755443322||NO||||||||Bergen|||
PV1|1|I|INTM^3201^04^HUS_HAUKELAND^^^^Medisinsk intensiv|||||203876^Andersen^Marit^Sofie^^Dr|||INT|||||203876^Andersen^Marit^Sofie^^Dr||||||||||||||||||||||||
ORC|RE|SOFA250803-001|SOFA250803-001||CM||||20250803061400|||203876^Andersen^Marit^Sofie^^Dr||||||INTM^3201^04^HUS
OBR|1|SOFA250803-001|SOFA250803-001|SOFA^SOFA Score^MV|||20250803060000||||||||203876^Andersen^Marit^Sofie^^Dr|||||||||F|||||||
OBX|1|NM|SOFA_TOT^SOFA total^MV||11|{score}|0-24||||F|||20250803060000||METAVISION
OBX|2|NM|SOFA_RESP^SOFA respirasjon^MV||3|{score}|0-4||||F|||20250803060000||METAVISION
OBX|3|NM|SOFA_COAG^SOFA koagulasjon^MV||1|{score}|0-4||||F|||20250803060000||METAVISION
OBX|4|NM|SOFA_LIVER^SOFA lever^MV||2|{score}|0-4||||F|||20250803060000||METAVISION
OBX|5|NM|SOFA_CVS^SOFA kardiovaskulær^MV||3|{score}|0-4||||F|||20250803060000||METAVISION
OBX|6|NM|SOFA_CNS^SOFA sentralnervesystem^MV||1|{score}|0-4||||F|||20250803060000||METAVISION
OBX|7|NM|SOFA_RENAL^SOFA nyre^MV||1|{score}|0-4||||F|||20250803060000||METAVISION
```

---

## 9. ORM^O01 - Arterial blood gas order

```
MSH|^~\&|METAVISION|STOLAV_TRONDHEIM|LABSYS|STOLAV|20250914084530||ORM^O01^ORM_O01|MV20250914084530009|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||09037823456^^^STOLAV^MR~09037823456^^^FOLKEREG^FNR||Våge^Anders^Kristoffer||19780309|M|||Elgeseter gate 30^^Trondheim^^7030^NOR||+4773667788||NO||||||||Trondheim|||
PV1|1|I|INTA^5103^02^STOLAV^^^^Intensivavdeling|||||156743^Brekke^Olav^Petter^^Dr|||INT|||||156743^Brekke^Olav^Petter^^Dr||||||||||||||||||||||||
ORC|NW|LAB250914-001||LAB250914-001|SC||||20250914084500|||156743^Brekke^Olav^Petter^^Dr||||||INTA^5103^02^STOLAV
OBR|1|LAB250914-001||82803-7^Blodgass arteriell^LN|||20250914084500|||||||||156743^Brekke^Olav^Petter^^Dr|||||||||SC|||||||
NTE|1||Pasient på BIPAP, FiO2 60%. Vurder endring av ventilatorstøtte basert på resultat.
```

---

## 10. ADT^A03 - Discharge from ICU to general ward

```
MSH|^~\&|METAVISION|SSHF_KRISTIANSAND|DIPS_ARENA|SSHF|20250620153000||ADT^A03^ADT_A03|MV20250620153000010|P|2.5|||AL|NE||UNICODE UTF-8|||
EVN|A03|20250620153000|||pnord^Nordby^Per^A
PID|1||14068934521^^^SSHF^MR~14068934521^^^FOLKEREG^FNR||Kristiansen^Helga^Anette||19890614|F|||Markens gate 12^^Kristiansand^^4611^NOR||+4738119922||NO||||||||Kristiansand|||
PV1|1|I|INTG^7101^01^SSHF_KRISTIANSAND^^^^Generell intensiv||MED^3202^02^SSHF_KRISTIANSAND^^^^Medisinsk sengepost|INTG^7101^01|234567^Nordby^Per^Aleksander^^Dr|||INT||7|||234567^Nordby^Per^Aleksander^^Dr|I||SI|||||||||||||||||||SSHF|||||20250615080000||20250620153000||
PV2|||^Utskrivning fra intensiv etter stabilisering||||||||2|||||||||||||||||||||||||
DG1|1||J96.0^Akutt respirasjonssvikt^ICD-10||20250615|A|
DG1|2||J18.9^Pneumoni, uspesifisert^ICD-10||20250615|A|
```

---

## 11. ORU^R01 - Electrolytes and renal panel

```
MSH|^~\&|METAVISION|NLSH_BODO|LABSYS|NLSH|20250428112045||ORU^R01^ORU_R01|MV20250428112045011|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||25118267543^^^NLSH^MR~25118267543^^^FOLKEREG^FNR||Henriksen^Sverre^Magnus||19821125|M|||Sjøgata 18^^Bodø^^8006^NOR||+4775334455||NO||||||||Bodø|||
PV1|1|I|INTG^8101^01^NLSH_BODO^^^^Generell intensiv|||||245678^Strand^Anita^Kristin^^Dr|||INT|||||245678^Strand^Anita^Kristin^^Dr||||||||||||||||||||||||
ORC|RE|LAB250428-001|LAB250428-001||CM||||20250428112000|||245678^Strand^Anita^Kristin^^Dr||||||INTG^8101^01^NLSH
OBR|1|LAB250428-001|LAB250428-001|CHEM^Elektrolytter og nyrefunksjon^MV|||20250428110000||||||||245678^Strand^Anita^Kristin^^Dr|||||||||F|||||||
OBX|1|NM|2951-2^Natrium^LN||138|mmol/L|137-145|N|||F|||20250428110000||METAVISION
OBX|2|NM|2823-3^Kalium^LN||5.4|mmol/L|3.5-5.0|H|||F|||20250428110000||METAVISION
OBX|3|NM|2075-0^Klorid^LN||104|mmol/L|98-107|N|||F|||20250428110000||METAVISION
OBX|4|NM|3094-0^Urinstoff^LN||18.7|mmol/L|2.5-7.8|H|||F|||20250428110000||METAVISION
OBX|5|NM|2160-0^Kreatinin^LN||245|umol/L|60-105|H|||F|||20250428110000||METAVISION
OBX|6|NM|17861-6^Kalsium ionisert^LN||1.08|mmol/L|1.15-1.35|L|||F|||20250428110000||METAVISION
OBX|7|NM|2777-1^Fosfat^LN||1.92|mmol/L|0.85-1.50|H|||F|||20250428110000||METAVISION
OBX|8|NM|2532-0^Magnesium^LN||0.72|mmol/L|0.70-1.05|N|||F|||20250428110000||METAVISION
```

---

## 12. ORU^R01 - ICU flowsheet PDF report (ED datatype with base64)

```
MSH|^~\&|METAVISION|OUS_RIKSHOSP|DIPS_ARENA|OUS|20250715140000||ORU^R01^ORU_R01|MV20250715140000012|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||01029845678^^^OUS^MR~01029845678^^^FOLKEREG^FNR||Ås^Knut^Erling||19980201|M|||Sognsveien 77^^Oslo^^0855^NOR||+4722667788||NO||||||||Oslo|||
PV1|1|I|INTOV^4102^03^OUS_RIKSHOSP^^^^Intensivavdeling|||||178432^Nilsen^Erik^Johan^^Dr|||INT|||||178432^Nilsen^Erik^Johan^^Dr||||||||||||||||||||||||
ORC|RE|DOC250715-001|DOC250715-001||CM||||20250715135900|||178432^Nilsen^Erik^Johan^^Dr||||||INTOV^4102^03^OUS
OBR|1|DOC250715-001|DOC250715-001|DOC^Intensivrapport^MV|||20250715060000||||||||178432^Nilsen^Erik^Johan^^Dr|||||||||F|||||||
OBX|1|ED|PDF^Intensivrapport døgnrapport^MV||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEludGVuc2l2cmFwcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20250715060000||METAVISION
OBX|2|ST|DOC_TYPE^Dokumenttype^MV||Døgnrapport intensiv|||N|||F|||20250715060000||METAVISION
OBX|3|TS|DOC_PERIOD_START^Rapportperiode start^MV||20250714060000|||N|||F|||20250715060000||METAVISION
OBX|4|TS|DOC_PERIOD_END^Rapportperiode slutt^MV||20250715060000|||N|||F|||20250715060000||METAVISION
```

---

## 13. ORM^O01 - Continuous renal replacement therapy order

```
MSH|^~\&|METAVISION|HUS_HAUKELAND|DIPS_ARENA|HUS|20250901090000||ORM^O01^ORM_O01|MV20250901090000013|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||18057634987^^^HUS^MR~18057634987^^^FOLKEREG^FNR||Hågensen^Rolf^Ivar||19760518|M|||Sandviken 44^^Bergen^^5035^NOR||+4755889900||NO||||||||Bergen|||
PV1|1|I|INTM^3201^01^HUS_HAUKELAND^^^^Medisinsk intensiv|||||203876^Andersen^Marit^Sofie^^Dr|||INT|||||203876^Andersen^Marit^Sofie^^Dr||||||||||||||||||||||||
ORC|NW|CRRT250901-001||CRRT250901-001|SC||||20250901085900|||203876^Andersen^Marit^Sofie^^Dr||||||INTM^3201^01^HUS
OBR|1|CRRT250901-001||CRRT^Kontinuerlig nyreerstattende behandling^MV|||20250901085900||||||||203876^Andersen^Marit^Sofie^^Dr|||||||||SC|||||||
OBX|1|ST|CRRT_MODE^CRRT modus^MV||CVVHDF|||N|||F|||20250901085900||METAVISION
OBX|2|NM|CRRT_BFR^Blodfløde^MV||200|mL/min|||N|||F|||20250901085900||METAVISION
OBX|3|NM|CRRT_DFR^Dialysatfløde^MV||1500|mL/h|||N|||F|||20250901085900||METAVISION
OBX|4|NM|CRRT_RFR^Erstatningsfløde^MV||1000|mL/h|||N|||F|||20250901085900||METAVISION
OBX|5|ST|CRRT_ANTIC^Antikoagulasjon^MV||Sitrat regionalt|||N|||F|||20250901085900||METAVISION
NTE|1||Akutt nyresvikt med hyperkalemi 6.8 mmol/L og metabolsk acidose. Mål: ultrafiltrasjon 100 mL/t.
```

---

## 14. ADT^A02 - Transfer from ICU to step-down unit

```
MSH|^~\&|METAVISION|AHUS_NORDBYHAGEN|DIPS_ARENA|AHUS|20250503111500||ADT^A02^ADT_A02|MV20250503111500014|P|2.5|||AL|NE||UNICODE UTF-8|||
EVN|A02|20250503111500|||tlarsen^Larsen^Tone^M
PID|1||07098523456^^^AHUS^MR~07098523456^^^FOLKEREG^FNR||Dahl^Ragnhild^Synne||19850907|F|||Storgata 23^^Lillestrøm^^2000^NOR||+4763221100||NO||||||||Lillestrøm|||
PV1|1|I|OVK^1305^01^AHUS^^^^Overvåkningsavdeling||MED^1402^03^AHUS^^^^Medisinsk sengepost|INTG^1302^01|213456^Larsen^Tone^Marie^^Dr|||INT||7|||213456^Larsen^Tone^Marie^^Dr|I||SI|||||||||||||||||||AHUS|||||20250428090000|||
PV2|||^Overflytting til overvåkning etter langvarig intensivopphold||||||||3|||||||||||||||||||||||||
```

---

## 15. ORU^R01 - Hemodynamic monitoring (Swan-Ganz)

```
MSH|^~\&|MV_ICU|UNN_TROMSO|DIPS_ARENA|UNN|20250208183000||ORU^R01^ORU_R01|MV20250208183000015|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||19058712345^^^UNN^MR~19058712345^^^FOLKEREG^FNR||Pedersen^Bjørn^Halvard||19870519|M|||Sjømannsgata 8^^Tromsø^^9008^NOR||+4777556677||NO||||||||Tromsø|||
PV1|1|I|INTK^6201^01^UNN_TROMSO^^^^Kirurgisk intensiv|||||189234^Holm^Silje^Kristin^^Dr|||INT|||||189234^Holm^Silje^Kristin^^Dr||||||||||||||||||||||||
ORC|RE|HEMO250208-001|HEMO250208-001||CM||||20250208182900|||189234^Holm^Silje^Kristin^^Dr||||||INTK^6201^01^UNN
OBR|1|HEMO250208-001|HEMO250208-001|HEMO^Hemodynamisk monitorering^MV|||20250208182500||||||||189234^Holm^Silje^Kristin^^Dr|||||||||F|||||||
OBX|1|NM|PAP_SYS^PA systolisk^MV||38|mm[Hg]|15-30|H|||F|||20250208182500||MV_ICU
OBX|2|NM|PAP_DIA^PA diastolisk^MV||18|mm[Hg]|6-12|H|||F|||20250208182500||MV_ICU
OBX|3|NM|PAP_MEAN^PA middel^MV||25|mm[Hg]|10-20|H|||F|||20250208182500||MV_ICU
OBX|4|NM|PCWP^Kiletrykk^MV||16|mm[Hg]|6-12|H|||F|||20250208182500||MV_ICU
OBX|5|NM|CO_TD^Hjerteminuttvolum^MV||3.8|L/min|4.0-8.0|L|||F|||20250208182500||MV_ICU
OBX|6|NM|CI^Hjerteindeks^MV||2.0|L/min/m2|2.5-4.0|L|||F|||20250208182500||MV_ICU
OBX|7|NM|SVR^Systemisk vaskulær motstand^MV||1680|dyn.s/cm5|800-1200|H|||F|||20250208182500||MV_ICU
OBX|8|NM|SVO2^Blandet venøs O2-metning^MV||58|%|60-80|L|||F|||20250208182500||MV_ICU
```

---

## 16. ORM^O01 - Sedation protocol order

```
MSH|^~\&|METAVISION|STOLAV_TRONDHEIM|DIPS_ARENA|STOLAV|20250711143000||ORM^O01^ORM_O01|MV20250711143000016|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||23078934567^^^STOLAV^MR~23078934567^^^FOLKEREG^FNR||Aasen^Sigrid^Marie||19890723|F|||Ila 15^^Trondheim^^7018^NOR||+4773445566||NO||||||||Trondheim|||
PV1|1|I|INTA^5103^01^STOLAV^^^^Intensivavdeling|||||156743^Brekke^Olav^Petter^^Dr|||INT|||||156743^Brekke^Olav^Petter^^Dr||||||||||||||||||||||||
ORC|NW|SED250711-001||SED250711-001|SC||||20250711142900|||156743^Brekke^Olav^Petter^^Dr||||||INTA^5103^01^STOLAV
OBR|1|SED250711-001||SEDASJON^Sedasjonsprotokoll^MV|||20250711142900||||||||156743^Brekke^Olav^Petter^^Dr|||||||||SC|||||||
RXO|N05CD08^Midazolam^ATC||2-5|mg/h|IV^Intravenøs^HL70162||||||||||||
RXO|N01AH06^Remifentanil^ATC||0.05-0.15|mcg/kg/min|IV^Intravenøs^HL70162||||||||||||
NTE|1||Mål RASS -2 til 0. Daglig sedasjonsstopp kl. 08:00. Vurder spontanpusteprøve ved RASS 0.
```

---

## 17. ORU^R01 - Ventilator trend report PDF (ED datatype with base64)

```
MSH|^~\&|MV_ICU|SUS_STAVANGER|DIPS_ARENA|SUS|20250822080000||ORU^R01^ORU_R01|MV20250822080000017|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||11029467321^^^SUS^MR~11029467321^^^FOLKEREG^FNR||Bøe^Ingvar^Torstein||19940211|M|||Pedersgata 28^^Stavanger^^4013^NOR||+4751778899||NO||||||||Stavanger|||
PV1|1|I|INTM^4201^01^SUS_STAVANGER^^^^Medisinsk intensiv|||||198765^Mæland^Geir^Arne^^Dr|||INT|||||198765^Mæland^Geir^Arne^^Dr||||||||||||||||||||||||
ORC|RE|VTREND250822-001|VTREND250822-001||CM||||20250822075900|||198765^Mæland^Geir^Arne^^Dr||||||INTM^4201^01^SUS
OBR|1|VTREND250822-001|VTREND250822-001|VTREND^Ventilator trendrapport^MV|||20250821080000||||||||198765^Mæland^Geir^Arne^^Dr|||||||||F|||||||
OBX|1|ED|PDF^Ventilator trendrapport 24t^MV||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMDUKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihWZW50aWxhdG9yIFRyZW5kcmFwcG9ydCkgVGoKMTAwIDY4MCBUZAooUGVyaW9kZTogMjQuMDguMjAyNSAwODowMCAtIDI1LjA4LjIwMjUgMDg6MDApIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK||||||F|||20250821080000||MV_ICU
OBX|2|ST|DOC_TYPE^Dokumenttype^MV||Ventilator trendrapport 24 timer|||N|||F|||20250821080000||MV_ICU
OBX|3|TS|DOC_PERIOD_START^Rapportperiode start^MV||20250821080000|||N|||F|||20250821080000||MV_ICU
OBX|4|TS|DOC_PERIOD_END^Rapportperiode slutt^MV||20250822080000|||N|||F|||20250821080000||MV_ICU
```

---

## 18. ORU^R01 - Fluid balance and urine output

```
MSH|^~\&|METAVISION|SSHF_KRISTIANSAND|DIPS_ARENA|SSHF|20250306060000||ORU^R01^ORU_R01|MV20250306060000018|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||28117845632^^^SSHF^MR~28117845632^^^FOLKEREG^FNR||Lie^Hanne^Elisabeth||19781128|F|||Gyldenløves gate 9^^Kristiansand^^4612^NOR||+4738445566||NO||||||||Kristiansand|||
PV1|1|I|INTG^7101^02^SSHF_KRISTIANSAND^^^^Generell intensiv|||||234567^Nordby^Per^Aleksander^^Dr|||INT|||||234567^Nordby^Per^Aleksander^^Dr||||||||||||||||||||||||
ORC|RE|FLB250306-001|FLB250306-001||CM||||20250306055900|||234567^Nordby^Per^Aleksander^^Dr||||||INTG^7101^02^SSHF
OBR|1|FLB250306-001|FLB250306-001|FLUID^Væskebalanse 24t^MV|||20250305060000||||||||234567^Nordby^Per^Aleksander^^Dr|||||||||F|||||||
OBX|1|NM|FLUID_IN^Tilført totalt^MV||3450|mL|||N|||F|||20250305060000||METAVISION
OBX|2|NM|FLUID_IV^Intravenøst^MV||2800|mL|||N|||F|||20250305060000||METAVISION
OBX|3|NM|FLUID_PO^Per os^MV||650|mL|||N|||F|||20250305060000||METAVISION
OBX|4|NM|FLUID_OUT^Utskilt totalt^MV||2100|mL|||N|||F|||20250305060000||METAVISION
OBX|5|NM|URINE_24H^Urinproduksjon 24t^MV||1650|mL|||N|||F|||20250305060000||METAVISION
OBX|6|NM|URINE_RATE^Urinproduksjon/t^MV||0.45|mL/kg/h|>0.5|L|||F|||20250305060000||METAVISION
OBX|7|NM|FLUID_BAL^Væskebalanse netto^MV||+1350|mL|||N|||F|||20250305060000||METAVISION
OBX|8|NM|DRAIN_OUT^Drenstap^MV||450|mL|||N|||F|||20250305060000||METAVISION
```

---

## 19. ADT^A01 - Pediatric ICU admission

```
MSH|^~\&|METAVISION|OUS_RIKSHOSP|DIPS_ARENA|OUS|20250119201500||ADT^A01^ADT_A01|MV20250119201500019|P|2.5|||AL|NE||UNICODE UTF-8|||
EVN|A01|20250119201500|||enilsen^Nilsen^Erik^J
PID|1||15062178901^^^OUS^MR~15062178901^^^FOLKEREG^FNR||Olsen^Mikkel^Andre||20210615|M|||Frognerveien 34^^Oslo^^0263^NOR||+4722112233~+4795678901||NO|U|||15062178901||||Oslo|||
PV1|1|I|BARI^4110^01^OUS_RIKSHOSP^^^^Barneintensiv|||BARI^4110^01|178901^Engen^Lise^Marie^^Dr|||INT||7|||178901^Engen^Lise^Marie^^Dr|I||SI|||||||||||||||||||OUS|||||20250119201400|||
PV2|||^Akutt bronkiolitt med respirasjonssvikt||||||||5|||||||||||||||||||||||||
NK1|1|Olsen^Maria^Kristine|MTH^Mor|Frognerveien 34^^Oslo^^0263^NOR|+4795678901||
DG1|1||J21.0^Akutt bronkiolitt forårsaket av RS-virus^ICD-10||20250119|A|
DG1|2||J96.0^Akutt respirasjonssvikt^ICD-10||20250119|A|
```

---

## 20. ORU^R01 - Nursing assessment (pain, sedation, delirium scores)

```
MSH|^~\&|MV_ICU|NLSH_BODO|DIPS_ARENA|NLSH|20251004220000||ORU^R01^ORU_R01|MV20251004220000020|P|2.5|||AL|NE||UNICODE UTF-8|||
PID|1||03048756321^^^NLSH^MR~03048756321^^^FOLKEREG^FNR||Strøm^Vidar^Aleksander||19870403|M|||Dronningens gate 12^^Bodø^^8006^NOR||+4775998877||NO||||||||Bodø|||
PV1|1|I|INTG^8101^02^NLSH_BODO^^^^Generell intensiv|||||245678^Strand^Anita^Kristin^^Dr|||INT|||||245678^Strand^Anita^Kristin^^Dr||||||||||||||||||||||||
ORC|RE|NURS251004-001|NURS251004-001||CM||||20251004215900|||245678^Strand^Anita^Kristin^^Dr||||||INTG^8101^02^NLSH
OBR|1|NURS251004-001|NURS251004-001|NURSASMT^Sykepleiervurdering^MV|||20251004215000||||||||245678^Strand^Anita^Kristin^^Dr|||||||||F|||||||
OBX|1|NM|NRS^Numerisk smerteskala^MV||4|{score}|0-10||||F|||20251004215000||MV_ICU
OBX|2|NM|RASS^Richmond Agitation-Sedation Scale^MV||-1|{score}|-5-4||||F|||20251004215000||MV_ICU
OBX|3|NM|CAMICU^CAM-ICU delirium^MV||1|{score}|0-1||||F|||20251004215000||MV_ICU
OBX|4|ST|CAMICU_RES^CAM-ICU resultat^MV||Positiv - delirium påvist|||A|||F|||20251004215000||MV_ICU
OBX|5|NM|CPOT^Critical Care Pain Observation Tool^MV||3|{score}|0-8||||F|||20251004215000||MV_ICU
OBX|6|NM|BRADEN^Braden trykksårskala^MV||13|{score}|6-23||||F|||20251004215000||MV_ICU
OBX|7|ST|MOBIL^Mobiliseringsstatus^MV||Sengeleie, passiv bevegelsestrening|||N|||F|||20251004215000||MV_ICU
```
