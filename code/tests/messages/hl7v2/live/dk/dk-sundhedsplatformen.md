# Sundhedsplatformen (Epic) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Indlæggelse (inpatient admission)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LANDSPATIENTREGISTERET|SST|20260401070000||ADT^A01^ADT_A01|EPICMSG00001|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A01|20260401070000
PID|||1207892500^^^CPR^NNDN||Kristensen^Astrid^Lykke^^||19890712|F|||Tolderlundsvej 121^^Viborg^^8800^DK||^^PH^+4572516961~^^CP^+4542586458
PV1||I|RH^HÆMA^H3041^S01||||10001^Nielsen^Susanne^^^Dr.|||HÆMA||||7|||10001^Nielsen^Susanne^^^Dr.||RH202604010001||||||||||||||||||||||||20260401070000
PV2|||^Akut myeloid leukæmi
NK1|1|Kristensen^Pia|SPO^Ægtefælle||^^CP^+4528314167
IN1|1||REGSYG|Region Hovedstaden|Kongens Vænge 2^^Hillerød^^3400^DK
```

---

## 2. ADT^A02 - Overflytning (patient transfer)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LANDSPATIENTREGISTERET|SST|20260402103000||ADT^A02^ADT_A02|EPICMSG00002|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A02|20260402103000
PID|||1207892500^^^CPR^NNDN||Kristensen^Astrid^Lykke^^||19890712|F|||Tolderlundsvej 121^^Viborg^^8800^DK||^^PH^+4572516961~^^CP^+4542586458
PV1||I|RH^INT^I2051^S03||||20002^Christiansen^Preben^^^Dr.|||INT||||7|||20002^Christiansen^Preben^^^Dr.||RH202604010001||||||||||||||||||||||||20260402103000
```

---

## 3. ADT^A03 - Udskrivelse (discharge)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LANDSPATIENTREGISTERET|SST|20260408160000||ADT^A03^ADT_A03|EPICMSG00003|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A03|20260408160000
PID|||1207892500^^^CPR^NNDN||Kristensen^Astrid^Lykke^^||19890712|F|||Tolderlundsvej 121^^Viborg^^8800^DK||^^PH^+4572516961~^^CP^+4542586458
PV1||I|RH^INT^I2051^S03||||20002^Christiansen^Preben^^^Dr.|||INT||||7|||20002^Christiansen^Preben^^^Dr.||RH202604010001||||||||||||||||||||||||20260408160000
PV2|||^Akut myeloid leukæmi
```

---

## 4. ADT^A04 - Ambulant registrering (outpatient registration)

```
MSH|^~\&|EPIC|HERLEV_HOSPITAL|LANDSPATIENTREGISTERET|SST|20260409081500||ADT^A04^ADT_A01|EPICMSG00004|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A04|20260409081500
PID|||0504766217^^^CPR^NNDN||Vestergaard^Simon^Ejvind^^||19760405|M|||Amagerbrogade 18^^Charlottenlund^^2920^DK||^^PH^+4576932249~^^CP^+4522975169
PV1||O|HEH^DER^AMB01||||30003^Johansen^Clara^^^Dr.|||DER||||||||||HEH202604090001||||||||||||||||||||||||20260409081500
PV2|||^Kontrol - malignt melanom
```

---

## 5. ADT^A08 - Opdatering af patientdata (update patient information)

```
MSH|^~\&|EPIC|HERLEV_HOSPITAL|LANDSPATIENTREGISTERET|SST|20260410091000||ADT^A08^ADT_A01|EPICMSG00005|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A08|20260410091000
PID|||0504766217^^^CPR^NNDN||Vestergaard^Simon^Ejvind^^||19760405|M|||Tolderlundsvej 34^^Risskov^^8240^DK||^^PH^+4556683349~^^CP^+4522975169
PV1||O|HEH^DER^AMB01||||30003^Johansen^Clara^^^Dr.|||DER||||||||||HEH202604090001||||||||||||||||||||||||20260410091000
```

---

## 6. ADT^A31 - Opdatering af stamdata (update person information)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|CPR_REGISTERET|SST|20260411080000||ADT^A31^ADT_A05|EPICMSG00006|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A31|20260411080000
PID|||2309684042^^^CPR^NNDN||Friis^Mette^Lykke^^||19680923|F|||Valby Langgade 141^^Horsens^^8700^DK||^^PH^+4567932328~^^CP^+4553591793
PD1||||40004^Bruun^Frederik^^^Dr.
```

---

## 7. ADT^A40 - Sammenlægning af patientidentiteter (merge patient)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|MPI|SST|20260412060000||ADT^A40^ADT_A39|EPICMSG00007|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A40|20260412060000
PID|||1110936519^^^CPR^NNDN||Henriksen^Jesper^Vagn^^||19931011|M|||Roskildevej 188^^Aalborg SØ^^9220^DK||^^PH^+4540563712
MRG|1837148912^^^CPR^NNDN||RH202601200001
```

---

## 8. ORM^O01 - Laboratorierekvisition (laboratory order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LABKA|KBA|20260413081500||ORM^O01|EPICMSG00008|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2202756426^^^CPR^NNDN||Skov^Tove^Kristine^^||19750222|F|||Frederikssundsvej 123^^København SV^^2450^DK||^^PH^+4591671935
PV1||I|RH^NEF^N4021^S02||||50005^Mortensen^Mikkel^^^Dr.|||NEF||||||||||RH202604130001
ORC|NW|ORD20260413001^EPIC||||||20260413081500|||50005^Mortensen^Mikkel^^^Dr.
OBR|1|ORD20260413001^EPIC||CREAT^Kreatinin og eGFR^LN|||20260413081500||||||||50005^Mortensen^Mikkel^^^Dr.
OBR|2|ORD20260413001^EPIC||URINE^Urinstix og mikroskopi^LN|||20260413081500||||||||50005^Mortensen^Mikkel^^^Dr.
```

---

## 9. ORU^R01 - Laboratoriesvar (laboratory result)

```
MSH|^~\&|LABKA|KBA|EPIC|RIGSHOSPITALET|20260413141500||ORU^R01^ORU_R01|EPICMSG00009|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2202756426^^^CPR^NNDN||Skov^Tove^Kristine^^||19750222|F|||Frederikssundsvej 123^^København SV^^2450^DK||^^PH^+4591671935
PV1||I|RH^NEF^N4021^S02||||50005^Mortensen^Mikkel^^^Dr.|||NEF||||||||||RH202604130001
ORC|RE|ORD20260413001^EPIC||||||20260413141500
OBR|1|ORD20260413001^EPIC||CREAT^Kreatinin og eGFR^LN|||20260413081500||||||||50005^Mortensen^Mikkel^^^Dr.||||||20260413141500|||F
OBX|1|NM|CREA^Kreatinin^LN||198|umol/L|45-105|H|||F
OBX|2|NM|EGFR^Estimeret GFR^LN||28|mL/min/1.73m2|>60|L|||F
OBX|3|NM|UREA^Karbamid^LN||18.5|mmol/L|2.6-6.4|H|||F
```

---

## 10. ORU^R01 - Epikrisenotat med PDF (discharge summary with embedded PDF)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|SUNDHED_DK|NSP|20260414100000||ORU^R01^ORU_R01|EPICMSG00010|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1207892500^^^CPR^NNDN||Kristensen^Astrid^Lykke^^||19890712|F|||Tolderlundsvej 121^^Viborg^^8800^DK||^^PH^+4572516961
PV1||I|RH^INT^I2051^S03||||20002^Christiansen^Preben^^^Dr.|||INT||||||||||RH202604010001
ORC|RE|DOC20260414001^EPIC||||||20260414100000
OBR|1|DOC20260414001^EPIC||EPIKRISE^Epikrise - hæmatologi^LN|||20260408160000||||||||20002^Christiansen^Preben^^^Dr.||||||20260414100000|||F
OBX|1|ED|PDF^Epikrisenotat^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. SIU^S12 - Aftale-booking (appointment scheduling notification)

```
MSH|^~\&|EPIC|HERLEV_HOSPITAL|PATIENTPORTAL|SUNDHED_DK|20260415080000||SIU^S12|EPICMSG00011|P|2.5|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^EPIC|||||ROUTINE^^HL70276|MRI_SCAN^MR-scanning^^^EPIC|60|MIN|^^60^20260501100000^20260501110000||||||30003^Johansen^Clara^^^Dr.|^^PH^+4543253881|HEH^RAD^MR01|30003^Johansen^Clara^^^Dr.|^^PH^+4543253881|HEH^RAD^MR01
PID|||0504766217^^^CPR^NNDN||Vestergaard^Simon^Ejvind^^||19760405|M|||Tolderlundsvej 34^^Risskov^^8240^DK||^^CP^+4522975169
AIS|1||MRI^MR-scanning af cerebrum^LOCAL|20260501100000||60|MIN
AIL|1||HEH^RAD^MR01
AIP|1||30003^Johansen^Clara^^^Dr.
```

---

## 12. SIU^S14 - Aftaleændring (appointment modification)

```
MSH|^~\&|EPIC|HERLEV_HOSPITAL|PATIENTPORTAL|SUNDHED_DK|20260416090000||SIU^S14|EPICMSG00012|P|2.5|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^EPIC|||||ROUTINE^^HL70276|MRI_SCAN^MR-scanning^^^EPIC|60|MIN|^^60^20260508100000^20260508110000||||||30003^Johansen^Clara^^^Dr.|^^PH^+4543253881|HEH^RAD^MR01|30003^Johansen^Clara^^^Dr.|^^PH^+4543253881|HEH^RAD^MR01
PID|||0504766217^^^CPR^NNDN||Vestergaard^Simon^Ejvind^^||19760405|M|||Tolderlundsvej 34^^Risskov^^8240^DK||^^CP^+4522975169
AIS|1||MRI^MR-scanning af cerebrum^LOCAL|20260508100000||60|MIN
AIL|1||HEH^RAD^MR01
AIP|1||30003^Johansen^Clara^^^Dr.
```

---

## 13. ORM^O01 - Røntgenrekvisition (radiology order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|SECTRA_RIS|RH_RAD|20260417091000||ORM^O01|EPICMSG00013|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108808105^^^CPR^NNDN||Svendsen^Mikkel^Frode^^||19800811|M|||Amagerbrogade 231^^Odense N^^5200^DK||^^PH^+4561662884
PV1||E|RH^AKM^AK101||||60006^Møller^Camilla^^^Dr.|||AKM||||||||||RH202604170001
ORC|NW|ORD20260417001^EPIC||||||20260417091000|||60006^Møller^Camilla^^^Dr.
OBR|1|ORD20260417001^EPIC||CTABD^CT af abdomen med kontrast^LOCAL|||20260417091000||||||Akut abdomen, mistanke om ileus|60006^Møller^Camilla^^^Dr.
```

---

## 14. ORU^R01 - Radiologibeskrivelse med PDF (radiology report with embedded PDF)

```
MSH|^~\&|SECTRA_RIS|RH_RAD|EPIC|RIGSHOSPITALET|20260417141500||ORU^R01^ORU_R01|EPICMSG00014|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108808105^^^CPR^NNDN||Svendsen^Mikkel^Frode^^||19800811|M|||Amagerbrogade 231^^Odense N^^5200^DK||^^PH^+4561662884
PV1||E|RH^AKM^AK101||||60006^Møller^Camilla^^^Dr.|||AKM||||||||||RH202604170001
ORC|RE|ORD20260417001^EPIC||||||20260417141500
OBR|1|ORD20260417001^EPIC||CTABD^CT af abdomen med kontrast^LOCAL|||20260417091000||||||||60006^Møller^Camilla^^^Dr.||||||20260417141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||CT abdomen med iv kontrast: Ingen tegn på ileus. Normal tarmmotilitet. Ingen fri luft. Leverparenchymet normalt. Ingen hydronefrose. Konkl: Normalt fund.||||||F
OBX|2|ED|PDF^Radiologirapport^LN||^application^pdf^Base64^JVBERi0xLjQKJcfsDecKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 15. MDM^T02 - Klinisk dokument (clinical document notification)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|DOKUMENTDELING|NSP|20260418120000||MDM^T02|EPICMSG00015|P|2.5|||AL|NE||UNICODE UTF-8
EVN|T02|20260418120000
PID|||1207892500^^^CPR^NNDN||Kristensen^Astrid^Lykke^^||19890712|F|||Tolderlundsvej 121^^Viborg^^8800^DK||^^PH^+4572516961
PV1||I|RH^HÆMA^H3041^S01||||10001^Nielsen^Susanne^^^Dr.|||HÆMA||||||||||RH202604010001
TXA|1|CN^Klinisk notat|TX|20260418120000|10001^Nielsen^Susanne^^^Dr.||20260418120000|||||DOC20260418001||||||AU
OBX|1|TX|NOTE^Klinisk notat^LN||Patienten har gennemført 2. serie kemoterapi. Tolererer behandlingen godt. Ingen tegn på infektion. Næste serie planlagt om 3 uger. Blodprøvekontrol inden da.||||||F
```

---

## 16. ORU^R01 - Koagulationssvar (coagulation result)

```
MSH|^~\&|LABKA|KBA|EPIC|RIGSHOSPITALET|20260419101500||ORU^R01^ORU_R01|EPICMSG00016|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1506833631^^^CPR^NNDN||Krogh^Karsten^Bo^^||19830615|M|||Torvegade 102^^Vanløse^^2720^DK||^^PH^+4563121640
PV1||I|RH^KIR^K5031^S04||||70007^Svendsen^Freja^^^Dr.|||KIR||||||||||RH202604190001
ORC|RE|ORD20260419001^LABKA||||||20260419101500
OBR|1|ORD20260419001^LABKA||KOAG^Koagulationstal^LN|||20260419083000||||||||70007^Svendsen^Freja^^^Dr.||||||20260419101500|||F
OBX|1|NM|INR^International Normalised Ratio^LN||2.8||0.8-1.2|H|||F
OBX|2|NM|APTT^Aktiveret partiel tromboplastintid^LN||42|sek|25-38|H|||F
OBX|3|NM|FBLOOD^Fibrinogen^LN||4.2|g/L|1.8-4.0|H|||F
OBX|4|NM|DDIMER^D-dimer^LN||1.8|mg/L FEU|<0.5|H|||F
```

---

## 17. ADT^A01 - Akut indlæggelse (emergency admission)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LANDSPATIENTREGISTERET|SST|20260420013000||ADT^A01^ADT_A01|EPICMSG00017|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A01|20260420013000
PID|||2801904893^^^CPR^NNDN||Christensen^Knud^Verner^^||19900128|M|||Vibevej 204^^Odense V^^5210^DK||^^CP^+4521449448
PV1||E|RH^AKM^AK101||||60006^Møller^Camilla^^^Dr.|||AKM||||1|||60006^Møller^Camilla^^^Dr.||RH202604200001||||||||||||||||||||||||20260420013000
PV2|||^Trafikuheld - polytrauma
NK1|1|Møller^Anders|SIS^Søster||^^CP^+4550365330
```

---

## 18. ORM^O01 - Blodprøverekvisition (blood test order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|LABKA|KBA|20260420020000||ORM^O01|EPICMSG00018|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2801904893^^^CPR^NNDN||Christensen^Knud^Verner^^||19900128|M|||Vibevej 204^^Odense V^^5210^DK||^^CP^+4521449448
PV1||E|RH^AKM^AK101||||60006^Møller^Camilla^^^Dr.|||AKM||||||||||RH202604200001
ORC|NW|ORD20260420001^EPIC||||||20260420020000|||60006^Møller^Camilla^^^Dr.
OBR|1|ORD20260420001^EPIC||TRAUMA^Traumepakke^LN|||20260420020000||||||||60006^Møller^Camilla^^^Dr.
OBR|2|ORD20260420001^EPIC||FORLIG^Forligelighedsprøve^LN|||20260420020000||||||AKUT - 4 SAG blod bestilt|60006^Møller^Camilla^^^Dr.
```

---

## 19. ORU^R01 - Blodgassvar (blood gas result)

```
MSH|^~\&|LABKA|KBA|EPIC|RIGSHOSPITALET|20260420023000||ORU^R01^ORU_R01|EPICMSG00019|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2801904893^^^CPR^NNDN||Christensen^Knud^Verner^^||19900128|M|||Vibevej 204^^Odense V^^5210^DK||^^CP^+4521449448
PV1||E|RH^AKM^AK101||||60006^Møller^Camilla^^^Dr.|||AKM||||||||||RH202604200001
ORC|RE|ORD20260420002^LABKA||||||20260420023000
OBR|1|ORD20260420002^LABKA||ABGAS^Arteriel blodgas^LN|||20260420021500||||||||60006^Møller^Camilla^^^Dr.||||||20260420023000|||F
OBX|1|NM|PH^pH^LN||7.31||7.35-7.45|L|||F
OBX|2|NM|PCO2^pCO2^LN||5.8|kPa|4.7-6.0|N|||F
OBX|3|NM|PO2^pO2^LN||8.2|kPa|10.0-13.3|L|||F
OBX|4|NM|HCO3^Bikarbonat^LN||19.5|mmol/L|22-26|L|||F
OBX|5|NM|LACT^Laktat^LN||4.2|mmol/L|0.5-2.0|H|||F
OBX|6|NM|BE^Base Excess^LN||-6.5|mmol/L|-3.0-3.0|L|||F
```

---

## 20. ORU^R01 - Thyroideasvar (thyroid function result)

```
MSH|^~\&|LABKA|KBA|EPIC|HERLEV_HOSPITAL|20260421100000||ORU^R01^ORU_R01|EPICMSG00020|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2309684042^^^CPR^NNDN||Friis^Mette^Lykke^^||19680923|F|||Valby Langgade 141^^Horsens^^8700^DK||^^PH^+4567932328
PV1||O|HEH^END^AMB01||||40004^Bruun^Frederik^^^Dr.|||END||||||||||HEH202604210001
ORC|RE|ORD20260421001^LABKA||||||20260421100000
OBR|1|ORD20260421001^LABKA||THYR^Thyroideatal^LN|||20260421083000||||||||40004^Bruun^Frederik^^^Dr.||||||20260421100000|||F
OBX|1|NM|TSH^Thyreoideastimulerende hormon^LN||0.08|mIU/L|0.27-4.20|L|||F
OBX|2|NM|FT4^Frit thyroxin^LN||32.5|pmol/L|12.0-22.0|H|||F
OBX|3|NM|FT3^Frit trijodthyronin^LN||9.8|pmol/L|3.1-6.8|H|||F
```
