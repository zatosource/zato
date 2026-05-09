# MedLIS (Medical Laboratory Information System) - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Full blood count result (Beaumont Hospital, first MedLIS site)

```
MSH|^~\&|MEDLIS|BEAUMONT|HEALTHLINK|HSE|20240820141200||ORU^R01^ORU_R01|ML00001|P|2.4|||AL|AL||8859/1
PID|1||4781203^^^BEAUMONT^MRN~3218764TA^^^PPS^PPS~9000078341^^^IHI^IHI||GALLAGHER^CIARÁN^EOGHAN^^^^L||19550318|M|||27 Clontarf Road^^Dublin 3^^D03 T8K2^IRL^H||+353 1 8532176^HOME||en|M
PV1|1|I|SURG1^Bay3^Bed12^BEAUMONT^^BED|E|||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC|||SUR|||||||||V100234^^^BEAUMONT^VN
ORC|RE|ORD10001^iPMS|ML-R10001^MEDLIS||CM||||20240820141200|||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC
OBR|1|ORD10001^iPMS|ML-R10001^MEDLIS|58410-2^CBC panel - Blood^LN^FBC^Full Blood Count^L|||20240819093000|||||||||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC||||||20240820141200||HEM|F
OBX|1|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||14.1|g/dL^grams per deciliter^UCUM|13.0-17.0|N|||F|||20240820|||||20240820141200
OBX|2|NM|6690-2^Leukocytes [#/volume] in Blood^LN||8.2|10*3/uL^thousands per microliter^UCUM|4.0-11.0|N|||F|||20240820|||||20240820141200
OBX|3|NM|777-3^Platelets [#/volume] in Blood^LN||210|10*3/uL^thousands per microliter^UCUM|150-400|N|||F|||20240820|||||20240820141200
OBX|4|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.8|10*6/uL^millions per microliter^UCUM|4.5-6.0|N|||F|||20240820|||||20240820141200
OBX|5|NM|787-2^MCV [Entitic volume]^LN||89.5|fL^femtoliters^UCUM|80-100|N|||F|||20240820|||||20240820141200
OBX|6|NM|786-4^MCHC [Mass/volume]^LN||33.8|g/dL^grams per deciliter^UCUM|32.0-36.0|N|||F|||20240820|||||20240820141200
OBX|7|NM|785-6^MCH [Entitic mass]^LN||29.4|pg^picograms^UCUM|27.0-33.0|N|||F|||20240820|||||20240820141200
SPM|1|SPM-10001&iPMS^SPM-ML10001&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20240819093000
```

---

## 2. ORU^R01 - Lipid panel (Beaumont Hospital)

```
MSH|^~\&|MEDLIS|BEAUMONT|HEALTHLINK|HSE|20240821100500||ORU^R01^ORU_R01|ML00002|P|2.4|||AL|AL||8859/1
PID|1||6209387^^^BEAUMONT^MRN~4517823PA^^^PPS^PPS||BYRNE^AOIFE^^^^^L||19850921|F|||56 Drumcondra Road^^Dublin 9^^D09 N4R7^IRL^H||+353 1 8367421^HOME||en|S
PV1|1|O|HAEM-OPD^^^BEAUMONT^^AMB|R|||C7612^Brennan^Lorcan^^^Dr^^^IMC
ORC|RE|ORD20002^iPMS|ML-R10002^MEDLIS||CM||||20240821100500|||C7612^Brennan^Lorcan^^^Dr^^^IMC
OBR|1|ORD20002^iPMS|ML-R10002^MEDLIS|24331-1^Lipid 1996 panel in Serum or Plasma^LN^LIPID^Lipid Profile^L|||20240820|||||||||C7612^Brennan^Lorcan^^^Dr^^^IMC||||||20240821100500||CHM|F
OBX|1|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||5.2|mmol/L^millimoles per liter^UCUM|<5.0|H|||F|||20240821|||||20240821100500
OBX|2|NM|2571-8^Triglycerides [Mass/volume] in Serum or Plasma^LN||1.4|mmol/L^millimoles per liter^UCUM|<1.7|N|||F|||20240821|||||20240821100500
OBX|3|NM|2085-9^HDL Cholesterol [Mass/volume] in Serum or Plasma^LN||1.5|mmol/L^millimoles per liter^UCUM|>1.0|N|||F|||20240821|||||20240821100500
OBX|4|NM|2089-1^LDL Cholesterol [Mass/volume] in Serum or Plasma^LN||3.1|mmol/L^millimoles per liter^UCUM|<3.0|H|||F|||20240821|||||20240821100500
OBX|5|NM|13457-7^LDL/HDL ratio^LN||2.1||<3.5|N|||F|||20240821|||||20240821100500
SPM|1|SPM-20002&iPMS^SPM-ML20002&MEDLIS||119364003^Serum specimen^SCT|||||||||||||||20240820
```

---

## 3. ORU^R01 - Liver function tests (Cavan and Monaghan Hospital)

```
MSH|^~\&|MEDLIS|CAVAN|HEALTHLINK|HSE|20251015083000||ORU^R01^ORU_R01|ML00003|P|2.4|||AL|AL||8859/1
PID|1||3395017^^^CAVAN^MRN~7823451UA^^^PPS^PPS||MORAN^TADHG^^^^^L||19720830|M|||15 Farnham Street^^Cavan^^H12 K4P6^IRL^H||+353 49 4378912^HOME
PV1|1|I|MED1^Room5^Bed2^CAVAN^^BED|E|||C2198^Healy^Fionnuala^^^Dr^^^IMC|||MED
ORC|RE|ORD30003^iPMS|ML-R10003^MEDLIS||CM||||20251015083000|||C2198^Healy^Fionnuala^^^Dr^^^IMC
OBR|1|ORD30003^iPMS|ML-R10003^MEDLIS|24325-3^Hepatic function panel^LN^LFT^Liver Function Tests^L|||20251014|||||||||C2198^Healy^Fionnuala^^^Dr^^^IMC||||||20251015083000||CHM|F
OBX|1|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L^units per liter^UCUM|10-40|N|||F|||20251015
OBX|2|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||35|U/L^units per liter^UCUM|7-56|N|||F|||20251015
OBX|3|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||75|U/L^units per liter^UCUM|44-147|N|||F|||20251015
OBX|4|NM|1975-2^Bilirubin total [Mass/volume] in Serum or Plasma^LN||12|umol/L^micromoles per liter^UCUM|<21|N|||F|||20251015
OBX|5|NM|2885-2^Protein total [Mass/volume] in Serum or Plasma^LN||72|g/L^grams per liter^UCUM|60-83|N|||F|||20251015
OBX|6|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||42|g/L^grams per liter^UCUM|35-52|N|||F|||20251015
SPM|1|SPM-30003&iPMS^SPM-ML30003&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20251014
```

---

## 4. ORU^R01 - Renal function panel (Our Lady of Lourdes, Drogheda)

```
MSH|^~\&|MEDLIS|DROGHEDA|HEALTHLINK|HSE|20251120143000||ORU^R01^ORU_R01|ML00004|P|2.4|||AL|AL||8859/1
PID|1||5512890^^^DROGHEDA^MRN~6140278VA^^^PPS^PPS||QUINN^SAOIRSE^^^^^L||19880504|F|||22 Laurence Street^^Drogheda^Louth^A92 F7H3^IRL^H||+353 41 9874562^HOME
PV1|1|O|NEPH-OPD^^^DROGHEDA^^AMB|R|||C5743^Crowley^Pádraig^^^Dr^^^IMC
ORC|RE|ORD40004^iPMS|ML-R10004^MEDLIS||CM||||20251120143000|||C5743^Crowley^Pádraig^^^Dr^^^IMC
OBR|1|ORD40004^iPMS|ML-R10004^MEDLIS|51990-0^Basic metabolic panel^LN^UE^Urea and Electrolytes^L|||20251119|||||||||C5743^Crowley^Pádraig^^^Dr^^^IMC||||||20251120143000||CHM|F
OBX|1|NM|2947-0^Sodium [Moles/volume] in Blood^LN||140|mmol/L^millimoles per liter^UCUM|136-145|N|||F|||20251120
OBX|2|NM|6298-4^Potassium [Moles/volume] in Blood^LN||4.2|mmol/L^millimoles per liter^UCUM|3.5-5.1|N|||F|||20251120
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||72|umol/L^micromoles per liter^UCUM|45-84|N|||F|||20251120
OBX|4|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||5.8|mmol/L^millimoles per liter^UCUM|2.5-7.1|N|||F|||20251120
OBX|5|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||101|mmol/L^millimoles per liter^UCUM|98-107|N|||F|||20251120
OBX|6|NM|33914-3^eGFR^LN||88|mL/min/1.73m2^milliliter per minute per 1.73 square meter^UCUM|>60|N|||F|||20251120
SPM|1|SPM-40004&iPMS^SPM-ML40004&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20251119
```

---

## 5. ORU^R01 - Coagulation screen (University Hospital Galway)

```
MSH|^~\&|MEDLIS|UHG|HEALTHLINK|HSE|20240925110000||ORU^R01^ORU_R01|ML00005|P|2.4|||AL|AL||8859/1
PID|1||7834102^^^UHG^MRN~2956014WA^^^PPS^PPS||DOYLE^DECLAN^^^^^L||19640312|M|||8 Shop Street^^Galway^^H91 E3K7^IRL^H||+353 91 563478^HOME
PV1|1|I|SURG2^Ward3^Bed6^UHG^^BED|E|||C8234^Sullivan^Niamh^^^Dr^^^IMC|||SUR
ORC|RE|ORD50005^iPMS|ML-R10005^MEDLIS||CM||||20240925110000|||C8234^Sullivan^Niamh^^^Dr^^^IMC
OBR|1|ORD50005^iPMS|ML-R10005^MEDLIS|62854-3^Coagulation panel^LN^COAG^Coagulation Screen^L|||20240924|||||||||C8234^Sullivan^Niamh^^^Dr^^^IMC||||||20240925110000||HEM|F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||12.5|s^seconds^UCUM|11.0-13.5|N|||F|||20240925
OBX|2|NM|6301-6^INR^LN||1.0||0.8-1.2|N|||F|||20240925
OBX|3|NM|3173-2^APTT^LN||28.3|s^seconds^UCUM|25.0-35.0|N|||F|||20240925
OBX|4|NM|3255-7^Fibrinogen [Mass/volume] in Platelet poor plasma^LN||3.2|g/L^grams per liter^UCUM|2.0-4.0|N|||F|||20240925
SPM|1|SPM-50005&iPMS^SPM-ML50005&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20240924
```

---

## 6. ORU^R01 - Thyroid function tests (St James's Hospital)

```
MSH|^~\&|MEDLIS|STJAMES|HEALTHLINK|HSE|20240730093000||ORU^R01^ORU_R01|ML00006|P|2.4|||AL|AL||8859/1
PID|1||8901564^^^STJAMES^MRN~5639218XA^^^PPS^PPS||NOLAN^GRÁINNE^^^^^L||19780215|F|||101 Thomas Street^^Dublin 8^^D08 W2X3^IRL^H||+353 1 4539876^HOME
PV1|1|O|ENDO-OPD^^^STJAMES^^AMB|R|||C3892^Dunne^Oisín^^^Dr^^^IMC
ORC|RE|ORD60006^iPMS|ML-R10006^MEDLIS||CM||||20240730093000|||C3892^Dunne^Oisín^^^Dr^^^IMC
OBR|1|ORD60006^iPMS|ML-R10006^MEDLIS|11579-0^TSH panel^LN^TFT^Thyroid Function Tests^L|||20240729|||||||||C3892^Dunne^Oisín^^^Dr^^^IMC||||||20240730093000||CHM|F
OBX|1|NM|11580-8^Thyrotropin [Units/volume] in Serum or Plasma^LN||2.5|mIU/L^milli international units per liter^UCUM|0.4-4.0|N|||F|||20240730
OBX|2|NM|3024-7^Free T4 [Mass/volume] in Serum or Plasma^LN||15.2|pmol/L^picomoles per liter^UCUM|9.0-19.0|N|||F|||20240730
OBX|3|NM|3053-6^Free T3 [Mass/volume] in Serum or Plasma^LN||4.8|pmol/L^picomoles per liter^UCUM|2.6-5.7|N|||F|||20240730
SPM|1|SPM-60006&iPMS^SPM-ML60006&MEDLIS||119364003^Serum specimen^SCT|||||||||||||||20240729
```

---

## 7. OML^O21 - Laboratory order (Beaumont Hospital)

```
MSH|^~\&|iPMS|BEAUMONT|MEDLIS|BEAUMONT|20240819090000||OML^O21^OML_O21|ML-O00001|P|2.4|||AL|AL||8859/1
PID|1||4781203^^^BEAUMONT^MRN~3218764TA^^^PPS^PPS||GALLAGHER^CIARÁN^EOGHAN^^^^L||19550318|M|||27 Clontarf Road^^Dublin 3^^D03 T8K2^IRL^H||+353 1 8532176^HOME
PV1|1|I|SURG1^Bay3^Bed12^BEAUMONT^^BED|E|||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC|||SUR|||||||||V100234^^^BEAUMONT^VN
ORC|NW|ORD10001^iPMS||GRP10001^iPMS|||||20240819090000|||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC
OBR|1|ORD10001^iPMS||58410-2^CBC panel - Blood^LN^FBC^Full Blood Count^L|||20240819|||||||||C4481^Fitzgerald^Deirdre^^^Dr^^^IMC
OBX|1|CWE|49541-6^Fasting status^LN||N^No^HL70136||||||O
SPM|1|SPM-10001&iPMS||119297000^Blood specimen^SCT|||||||||||||||20240819090000
```

---

## 8. OML^O21 - Urgent laboratory order (Cork University Hospital)

```
MSH|^~\&|iPMS|CUH|MEDLIS|CUH|20240925081500||OML^O21^OML_O21|ML-O00002|P|2.4|||AL|AL||8859/1
PID|1||2047653^^^CUH^MRN~8174923HA^^^PPS^PPS||O'CONNOR^FIACHRA^^^^^L||19710205|M|||23 Western Road^^Cork^^T12 N6E8^IRL^H
PV1|1|E|ED^Resus^Bed1^CUH^^BED|E|||C6017^Walsh^Sorcha^^^Dr^^^IMC|||EMR
ORC|NW|ORD70002^iPMS||GRP70002^iPMS|||||20240925081500|||C6017^Walsh^Sorcha^^^Dr^^^IMC||||||||S^STAT^HL70078
OBR|1|ORD70002^iPMS||51990-0^Basic metabolic panel^LN^UE^Urea and Electrolytes^L|||20240925||||S|||||||C6017^Walsh^Sorcha^^^Dr^^^IMC
OBR|2|ORD70002^iPMS||24331-1^Lipid panel^LN^LIPID^Lipid Profile^L|||20240925||||S|||||||C6017^Walsh^Sorcha^^^Dr^^^IMC
OBR|3|ORD70002^iPMS||24362-6^Renal function panel^LN^RENAL^Renal Panel^L|||20240925||||S|||||||C6017^Walsh^Sorcha^^^Dr^^^IMC
DG1|1||N17.9^Acute renal failure unspecified^ICD10||20240925|A
SPM|1|SPM-70002&iPMS||119297000^Blood specimen^SCT|||||||||||||||20240925081500
```

---

## 9. ORU^R01 - Microbiology culture result (Beaumont Hospital)

```
MSH|^~\&|MEDLIS|BEAUMONT|HEALTHLINK|HSE|20240902160000||ORU^R01^ORU_R01|ML00009|P|2.4|||AL|AL||8859/1
PID|1||9012478^^^BEAUMONT^MRN~6451203YA^^^PPS^PPS||DALY^COLM^^^^^L||19560720|M|||44 Swords Road^^Dublin 9^^D09 J3R8^IRL^H||+353 1 8407612^HOME
PV1|1|I|MED3^Room7^Bed1^BEAUMONT^^BED|E|||C9156^McCarthy^Roisín^^^Dr^^^IMC|||MED
ORC|RE|ORD80009^iPMS|ML-R10009^MEDLIS||CM||||20240902160000|||C9156^McCarthy^Roisín^^^Dr^^^IMC
OBR|1|ORD80009^iPMS|ML-R10009^MEDLIS|630-4^Bacteria identified^LN^BCUL^Blood Culture^L|||20240830|||||||||C9156^McCarthy^Roisín^^^Dr^^^IMC||||||20240902160000||MCB|F
OBX|1|CWE|630-4^Bacteria identified in Blood by Culture^LN||3092008^Staphylococcus aureus^SCT||||||F|||20240902
OBX|2|ST|18907-6^Gram stain^LN||Gram positive cocci in clusters||||||F|||20240901
OBX|3|CWE|18900-1^Amoxicillin/clavulanate susceptibility^LN||S^Susceptible^HL70078||||||F|||20240902
OBX|4|CWE|18961-0^Flucloxacillin susceptibility^LN||S^Susceptible^HL70078||||||F|||20240902
OBX|5|CWE|18993-3^Vancomycin susceptibility^LN||S^Susceptible^HL70078||||||F|||20240902
OBX|6|CWE|18964-4^Gentamicin susceptibility^LN||S^Susceptible^HL70078||||||F|||20240902
NTE|1||Two sets of blood cultures drawn. One of two bottles positive after 18 hours incubation.
SPM|1|SPM-80009&iPMS^SPM-ML80009&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20240830
```

---

## 10. ORU^R01 - HbA1c result (Connolly Hospital Blanchardstown)

```
MSH|^~\&|MEDLIS|CONNOLLY|HEALTHLINK|HSE|20241010113000||ORU^R01^ORU_R01|ML00010|P|2.4|||AL|AL||8859/1
PID|1||1478562^^^CONNOLLY^MRN~9305618ZA^^^PPS^PPS||KAVANAGH^BRÍD^^^^^L||19650412|F|||33 Main Street^^Blanchardstown^Dublin 15^D15 C7V2^IRL^H||+353 1 8204539^HOME
PV1|1|O|DIAB-OPD^^^CONNOLLY^^AMB|R|||C1347^Ryan^Diarmuid^^^Dr^^^IMC
ORC|RE|ORD90010^iPMS|ML-R10010^MEDLIS||CM||||20241010113000|||C1347^Ryan^Diarmuid^^^Dr^^^IMC
OBR|1|ORD90010^iPMS|ML-R10010^MEDLIS|4548-4^Hemoglobin A1c/Hemoglobin total in Blood^LN^HBA1C^HbA1c^L|||20241009|||||||||C1347^Ryan^Diarmuid^^^Dr^^^IMC||||||20241010113000||CHM|F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||7.2|%^percent^UCUM|<6.5|H|||F|||20241010
OBX|2|NM|59261-8^Hemoglobin A1c/Hemoglobin.total in Blood by IFCC^LN||55|mmol/mol^millimoles per mole^UCUM|<48|H|||F|||20241010
NTE|1||Target HbA1c <53 mmol/mol (7.0%) for most adults with Type 2 diabetes.
SPM|1|SPM-90010&iPMS^SPM-ML90010&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20241009
```

---

## 11. ORU^R01 - Cardiac troponin (University Hospital Waterford)

```
MSH|^~\&|MEDLIS|UHW|HEALTHLINK|HSE|20241106010500||ORU^R01^ORU_R01|ML00011|P|2.4|||AL|AL||8859/1
PID|1||6723451^^^UHW^MRN~1847290QA^^^PPS^PPS||HEALY^PÁDRAIG^^^^^L||19420315|M|||71 The Quay^^Waterford^^X91 H5N8^IRL^H||+353 51 876341^HOME
PV1|1|E|ED^Majors^Bed4^UHW^^BED|E|||C7413^Buckley^Caoimhe^^^Dr^^^IMC|||EMR
ORC|RE|ORD11001^iPMS|ML-R11001^MEDLIS||CM||||20241106010500|||C7413^Buckley^Caoimhe^^^Dr^^^IMC
OBR|1|ORD11001^iPMS|ML-R11001^MEDLIS|49563-0^Troponin I.cardiac [Mass/volume] in Serum or Plasma by High sensitivity^LN^HSTNI^HS Troponin I^L|||20241106|||||||||C7413^Buckley^Caoimhe^^^Dr^^^IMC||||||20241106010500||CHM|F
OBX|1|NM|49563-0^Troponin I.cardiac [Mass/volume] in Serum or Plasma^LN||245|ng/L^nanograms per liter^UCUM|<14|HH|||F|||20241106
NTE|1||hs-Troponin I significantly elevated. Suggest serial sampling at 3 hours. Clinical correlation required.
SPM|1|SPM-11001&iPMS^SPM-ML11001&MEDLIS||119364003^Serum specimen^SCT|||||||||||||||20241106
```

---

## 12. ORU^R01 - Urinalysis (Mater Misericordiae University Hospital)

```
MSH|^~\&|MEDLIS|MATER|HEALTHLINK|HSE|20240618150000||ORU^R01^ORU_R01|ML00012|P|2.4|||AL|AL||8859/1
PID|1||2360178^^^MATER^MRN~7451892AB^^^PPS^PPS||SULLIVAN^ORLA^^^^^L||19900303|F|||15 Phibsborough Road^^Dublin 7^^D07 E4K9^IRL^H||+353 1 8305471^HOME
PV1|1|O|NEUR-OPD^^^MATER^^AMB|R|||C2671^O'Brien^Conor^^^Dr^^^IMC
ORC|RE|ORD12001^iPMS|ML-R12001^MEDLIS||CM||||20240618150000|||C2671^O'Brien^Conor^^^Dr^^^IMC
OBR|1|ORD12001^iPMS|ML-R12001^MEDLIS|24356-8^Urinalysis panel^LN^URINE^Urinalysis^L|||20240617|||||||||C2671^O'Brien^Conor^^^Dr^^^IMC||||||20240618150000||CHM|F
OBX|1|CWE|5778-6^Color of Urine^LN||YEL^Yellow^HL70393||||||F|||20240618
OBX|2|CWE|5767-9^Appearance of Urine^LN||CLR^Clear^HL70394||||||F|||20240618
OBX|3|NM|2756-5^pH of Urine^LN||6.0||5.0-8.0|N|||F|||20240618
OBX|4|NM|2965-2^Specific gravity of Urine^LN||1.020||1.005-1.030|N|||F|||20240618
OBX|5|CWE|5792-7^Glucose [Mass/volume] in Urine by Test strip^LN||NEG^Negative^HL70395||||||F|||20240618
OBX|6|CWE|20454-5^Protein [Mass/volume] in Urine by Test strip^LN||NEG^Negative^HL70395||||||F|||20240618
OBX|7|CWE|5794-3^Hemoglobin [Presence] in Urine by Test strip^LN||NEG^Negative^HL70395||||||F|||20240618
SPM|1|SPM-12001&iPMS^SPM-ML12001&MEDLIS||122575003^Urine specimen^SCT|||||||||||||||20240617
```

---

## 13. ORU^R01 - Blood group and antibody screen (St James's Hospital)

```
MSH|^~\&|MEDLIS|STJAMES|HEALTHLINK|HSE|20240505120000||ORU^R01^ORU_R01|ML00013|P|2.4|||AL|AL||8859/1
PID|1||8901564^^^STJAMES^MRN~5639218BC^^^PPS^PPS||NOLAN^GRÁINNE^^^^^L||19800910|M|||88 Patrick Street^^Dublin 8^^D08 P7J4^IRL^H||+353 1 4537812^HOME
PV1|1|I|SURG2^Ward5^Bed3^STJAMES^^BED|E|||C3892^Dunne^Oisín^^^Dr^^^IMC|||SUR
ORC|RE|ORD13001^iPMS|ML-R13001^MEDLIS||CM||||20240505120000|||C3892^Dunne^Oisín^^^Dr^^^IMC
OBR|1|ORD13001^iPMS|ML-R13001^MEDLIS|882-1^ABO and Rh group^LN^GS^Group and Screen^L|||20240504|||||||||C3892^Dunne^Oisín^^^Dr^^^IMC||||||20240505120000||BB|F
OBX|1|CWE|883-9^ABO group [Type] in Blood^LN||278149003^Blood group A^SCT||||||F|||20240505
OBX|2|CWE|10331-7^Rh [Type] in Blood^LN||165747007^Rh positive^SCT||||||F|||20240505
OBX|3|CWE|890-4^Antibody screen [Interpretation] in Serum or Plasma^LN||NEG^Negative^HL70395||||||F|||20240505
NTE|1||No clinically significant antibodies detected.
SPM|1|SPM-13001&iPMS^SPM-ML13001&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20240504
```

---

## 14. ORU^R01 - CSF analysis (Beaumont Hospital, neurology)

```
MSH|^~\&|MEDLIS|BEAUMONT|HEALTHLINK|HSE|20241205153000||ORU^R01^ORU_R01|ML00014|P|2.4|||AL|AL||8859/1
PID|1||4781203^^^BEAUMONT^MRN~3218764CD^^^PPS^PPS||GALLAGHER^CIARÁN^EOGHAN^^^^L||19750928|F|||33 Howth Road^^Dublin 5^^D05 R2M7^IRL^H||+353 1 8324517^HOME
PV1|1|I|NEUR^Ward2^Bed5^BEAUMONT^^BED|E|||C5209^Kelly^Muireann^^^Dr^^^IMC|||NEU
ORC|RE|ORD14001^iPMS|ML-R14001^MEDLIS||CM||||20241205153000|||C5209^Kelly^Muireann^^^Dr^^^IMC
OBR|1|ORD14001^iPMS|ML-R14001^MEDLIS|49546-9^CSF analysis panel^LN^CSF^CSF Analysis^L|||20241204|||||||||C5209^Kelly^Muireann^^^Dr^^^IMC||||||20241205153000||CHM|F
OBX|1|CWE|5769-5^Appearance of CSF^LN||CLR^Clear^HL70394||||||F|||20241205
OBX|2|NM|26464-8^Leukocytes [#/volume] in CSF^LN||2|10*6/L^millions per liter^UCUM|0-5|N|||F|||20241205
OBX|3|NM|2342-4^Glucose [Mass/volume] in CSF^LN||3.5|mmol/L^millimoles per liter^UCUM|2.2-4.4|N|||F|||20241205
OBX|4|NM|2880-3^Protein [Mass/volume] in CSF^LN||0.35|g/L^grams per liter^UCUM|0.15-0.45|N|||F|||20241205
OBX|5|ST|630-4^Bacteria identified in CSF by Culture^LN||No organisms seen||||||F|||20241205
SPM|1|SPM-14001&iPMS^SPM-ML14001&MEDLIS||258450006^Cerebrospinal fluid specimen^SCT|||||||||||||||20241204
```

---

## 15. ORU^R01 - Preliminary result with correction (University Hospital Limerick)

```
MSH|^~\&|MEDLIS|UHL|HEALTHLINK|HSE|20241018091500||ORU^R01^ORU_R01|ML00015|P|2.4|||AL|AL||8859/1
PID|1||3901274^^^UHL^MRN~4512067DE^^^PPS^PPS||O'BRIEN^DARRAGH^^^^^L||19600928|M|||5 O'Connell Street^^Limerick^^V94 C6D7^IRL^H
PV1|1|I|MED1^Room3^Bed4^UHL^^BED|E|||C8901^Gallagher^Siobhán^^^Dr^^^IMC|||MED
ORC|RE|ORD15001^iPMS|ML-R15001^MEDLIS||CM||||20241018091500|||C8901^Gallagher^Siobhán^^^Dr^^^IMC
OBR|1|ORD15001^iPMS|ML-R15001^MEDLIS|51990-0^Basic metabolic panel^LN^UE^Urea and Electrolytes^L|||20241017|||||||||C8901^Gallagher^Siobhán^^^Dr^^^IMC||||||20241018091500||CHM|C
OBX|1|NM|2947-0^Sodium^LN||138|mmol/L^millimoles per liter^UCUM|136-145|N|||F|||20241018
OBX|2|NM|6298-4^Potassium^LN||4.8|mmol/L^millimoles per liter^UCUM|3.5-5.1|N|||C|||20241018
NTE|1||Potassium corrected from 6.2 mmol/L (haemolysed sample). Repeat specimen collected.
OBX|3|NM|2160-0^Creatinine^LN||95|umol/L^micromoles per liter^UCUM|62-106|N|||F|||20241018
OBX|4|NM|3094-0^Urea^LN||6.1|mmol/L^millimoles per liter^UCUM|2.5-7.1|N|||F|||20241018
SPM|1|SPM-15001&iPMS^SPM-ML15001&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20241017
```

---

## 16. ORU^R01 - Histopathology report (St James's Hospital)

```
MSH|^~\&|MEDLIS|STJAMES|HEALTHLINK|HSE|20241112140000||ORU^R01^ORU_R01|ML00016|P|2.4|||AL|AL||8859/1
PID|1||7145823^^^STJAMES^MRN~2098734EF^^^PPS^PPS||WALSH^CATHAL^^^^^L||19580614|M|||55 Meath Street^^Dublin 8^^D08 V3N9^IRL^H||+353 1 4536289^HOME
PV1|1|I|SURG1^Ward2^Bed8^STJAMES^^BED|E|||C4128^Daly^Eoin^^^Dr^^^IMC|||SUR
ORC|RE|ORD16001^iPMS|ML-R16001^MEDLIS||CM||||20241112140000|||C4128^Daly^Eoin^^^Dr^^^IMC
OBR|1|ORD16001^iPMS|ML-R16001^MEDLIS|11529-5^Surgical pathology study^LN^HISTO^Histopathology^L|||20241105|||||||||C4128^Daly^Eoin^^^Dr^^^IMC||||||20241112140000||AP|F
OBX|1|FT|22634-0^Pathology report^LN||SPECIMEN: Right hemicolectomy specimen\.br\\.br\MACROSCOPIC: Right hemicolectomy specimen measuring 25cm in length. A tumour is identified in the caecum measuring 4.5 x 3.2 x 2.8cm.\.br\\.br\MICROSCOPIC: Sections show a moderately differentiated adenocarcinoma of the caecum invading through the muscularis propria into the pericolonic fat. Proximal and distal resection margins are clear. 14 lymph nodes identified, 1 of 14 contains metastatic carcinoma.\.br\\.br\DIAGNOSIS: Moderately differentiated adenocarcinoma of caecum, pT3 N1a (1/14) Mx.||||||F|||20241112
NTE|1||Synoptic report to follow. Case discussed at MDT 14/11/2024.
SPM|1|SPM-16001&iPMS^SPM-ML16001&MEDLIS||119376003^Tissue specimen^SCT|||||||||||||||20241105
```

---

## 17. ORU^R01 - Laboratory report with embedded PDF (Connolly Hospital)

```
MSH|^~\&|MEDLIS|CONNOLLY|GP_SYSTEM|HEALTHLINK|20241025160000||ORU^R01^ORU_R01|ML00017|P|2.4|||AL|AL||8859/1
PID|1||5283419^^^CONNOLLY^MRN~3679012FG^^^PPS^PPS||CROWLEY^AISLING^^^^^L||19880101|F|||12 Main Street^^Blanchardstown^Dublin 15^D15 H4T6^IRL^H
PV1|1|O|GEN-OPD^^^CONNOLLY^^AMB|R|||C6524^Murphy^Ruairí^^^Dr^^^IMC
ORC|RE|ORD17001^iPMS|ML-R17001^MEDLIS||CM||||20241025160000|||C6524^Murphy^Ruairí^^^Dr^^^IMC
OBR|1|ORD17001^iPMS|ML-R17001^MEDLIS|58410-2^CBC panel^LN^FBC^Full Blood Count^L|||20241024|||||||||C6524^Murphy^Ruairí^^^Dr^^^IMC||||||20241025160000||HEM|F
OBX|1|NM|718-7^Hemoglobin^LN||11.8|g/dL^grams per deciliter^UCUM|12.0-16.0|L|||F|||20241025
OBX|2|NM|6690-2^WBC^LN||6.5|10*3/uL^thousands per microliter^UCUM|4.0-11.0|N|||F|||20241025
OBX|3|NM|777-3^Platelets^LN||198|10*3/uL^thousands per microliter^UCUM|150-400|N|||F|||20241025
OBX|4|ED|PDF^Cumulative Lab Report PDF^L||CONNOLLY^IM^PDF^Base64^JVBERi0xLjUKJdDUxdgKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PiA+PgplbmRvYmoKMiAwIG9iago8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzMgMCBSXSAvQ291bnQgMSAvTWVkaWFCb3ggWzAgMCA1OTUgODQyXSA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDIgMCBSIC9SZXNvdXJjZXMgPDwgL0ZvbnQgPDwgL0YxIDQgMCBSID4+ID4+IC9Db250ZW50cyA1IDAgUiA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCjUgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjUwIDc4MCBUZAooTGFiIFJlcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9i||||||F|||20241025
SPM|1|SPM-17001&iPMS^SPM-ML17001&MEDLIS||119297000^Blood specimen^SCT|||||||||||||||20241024
```

---

## 18. ORU^R01 - Microbiology sensitivity report with embedded PDF (Cavan)

```
MSH|^~\&|MEDLIS|CAVAN|GP_SYSTEM|HEALTHLINK|20251020110000||ORU^R01^ORU_R01|ML00018|P|2.4|||AL|AL||8859/1
PID|1||4019832^^^CAVAN^MRN~5012478GH^^^PPS^PPS||BRENNAN^MAEVE^^^^^L||19550812|F|||7 Bridge Street^^Cavan^^H12 N7C3^IRL^H||+353 49 4375681^HOME
PV1|1|O|GEN-OPD^^^CAVAN^^AMB|R|||C2198^Healy^Fionnuala^^^Dr^^^IMC
ORC|RE|ORD18001^iPMS|ML-R18001^MEDLIS||CM||||20251020110000|||C2198^Healy^Fionnuala^^^Dr^^^IMC
OBR|1|ORD18001^iPMS|ML-R18001^MEDLIS|630-4^Bacteria identified^LN^UCUL^Urine Culture^L|||20251018|||||||||C2198^Healy^Fionnuala^^^Dr^^^IMC||||||20251020110000||MCB|F
OBX|1|CWE|630-4^Bacteria identified in Urine by Culture^LN||112283007^Escherichia coli^SCT||||||F|||20251020
OBX|2|NM|564-5^Colony count [#/volume] in Urine^LN||100000|CFU/mL^colony forming units per milliliter^UCUM|<10000|H|||F|||20251020
OBX|3|CWE|18862-3^Ampicillin susceptibility^LN||R^Resistant^HL70078||||||F|||20251020
OBX|4|CWE|18906-8^Trimethoprim susceptibility^LN||R^Resistant^HL70078||||||F|||20251020
OBX|5|CWE|18928-2^Nitrofurantoin susceptibility^LN||S^Susceptible^HL70078||||||F|||20251020
OBX|6|CWE|18868-0^Ciprofloxacin susceptibility^LN||S^Susceptible^HL70078||||||F|||20251020
OBX|7|ED|PDF^Antibiogram Report PDF^L||CAVAN^IM^PDF^Base64^JVBERi0xLjQKJcfsj6IKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSAgNCAwIFIgPj4gPj4gL0NvbnRlbnRzIDUgMCBSID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKNSAwIG9iago=||||||F|||20251020
NTE|1||Significant growth of E. coli. ESBL screen negative. Recommend nitrofurantoin for uncomplicated UTI.
SPM|1|SPM-18001&iPMS^SPM-ML18001&MEDLIS||122575003^Urine specimen^SCT|||||||||||||||20251018
```

---

## 19. OML^O21 - Histopathology order with clinical details (St James's Hospital)

```
MSH|^~\&|iPMS|STJAMES|MEDLIS|STJAMES|20241105093000||OML^O21^OML_O21|ML-O00019|P|2.4|||AL|AL||8859/1
PID|1||7145823^^^STJAMES^MRN~2098734EF^^^PPS^PPS||WALSH^CATHAL^^^^^L||19580614|M|||55 Meath Street^^Dublin 8^^D08 V3N9^IRL^H
PV1|1|I|SURG1^Ward2^Bed8^STJAMES^^BED|E|||C4128^Daly^Eoin^^^Dr^^^IMC|||SUR
ORC|NW|ORD19001^iPMS||GRP19001^iPMS|||||20241105093000|||C4128^Daly^Eoin^^^Dr^^^IMC
OBR|1|ORD19001^iPMS||11529-5^Surgical pathology study^LN^HISTO^Histopathology^L|||20241105|||||||||C4128^Daly^Eoin^^^Dr^^^IMC
NTE|1||Right hemicolectomy. Caecal mass. Known malignancy on biopsy.
DG1|1||C18.0^Malignant neoplasm of caecum^ICD10||20241015|A
SPM|1|SPM-19001&iPMS||119376003^Tissue specimen^SCT|||||||||||||||20241105093000
```

---

## 20. ORU^R01 - COVID-19 PCR result (Connolly Hospital)

```
MSH|^~\&|MEDLIS|CONNOLLY|HEALTHLINK|HSE|20241201143000||ORU^R01^ORU_R01|ML00020|P|2.4|||AL|AL||8859/1
PID|1||8347261^^^CONNOLLY^MRN~7128453HI^^^PPS^PPS||KELLY^CLODAGH^^^^^L||19910117|F|||22 Church Street^^Blanchardstown^Dublin 15^D15 M8W4^IRL^H||+353 1 8209317^HOME
PV1|1|E|ED^Assessment^Bed2^CONNOLLY^^BED|E|||C6524^Murphy^Ruairí^^^Dr^^^IMC|||EMR
ORC|RE|ORD20001^iPMS|ML-R20001^MEDLIS||CM||||20241201143000|||C6524^Murphy^Ruairí^^^Dr^^^IMC
OBR|1|ORD20001^iPMS|ML-R20001^MEDLIS|94500-6^SARS-CoV-2 RNA panel^LN^COVID^SARS-CoV-2 PCR^L|||20241201|||||||||C6524^Murphy^Ruairí^^^Dr^^^IMC||||||20241201143000||MCB|F
OBX|1|CWE|94500-6^SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen^LN||260385009^Negative^SCT||||||F|||20241201
OBX|2|ST|94558-4^SARS-CoV-2 Ag [Presence] in Respiratory specimen^LN||Not detected||||||F|||20241201
NTE|1||Sample type: Nasopharyngeal swab. Method: RT-PCR. Target genes: ORF1ab, N gene. Both targets not detected.
SPM|1|SPM-20001&iPMS^SPM-ML20001&MEDLIS||258500001^Nasopharyngeal swab^SCT|||||||||||||||20241201
```

---
