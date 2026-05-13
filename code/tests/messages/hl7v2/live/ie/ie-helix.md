# Helix Practice Manager - real HL7v2 ER7 messages

## 1

```
MSH|^~\&|LABSYS|OLLHD|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20001|20250518091530||ORU^R01|MSG20250518091530001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||OLLH-667788^^^OLLHD^MR~9203456712WA^^^PPSN^PPSN||Gallagher^Aoife^M^^Ms.||19920815|F|||7 Narrow West Street^^Drogheda^Co. Louth^A92 T4Y8^IRL^H||+353419823456^PRN^PH~+353857612345^PRN^CP||EN|S
PV1|1|O|HAEM^HAEM-OPD^1^OLLHD||||DOC201^Kavanagh^Ciarán^^^Dr.^MD
ORC|RE|HELORD20250517001|OLLHLAB20250518001||CM||||20250518090000
OBR|1|HELORD20250517001|OLLHLAB20250518001|58410-2^CBC panel^LN|||20250517143000||||||||DOC201^Kavanagh^Ciarán^^^Dr.^MD||||||20250518090000|||F
OBX|1|NM|6690-2^WBC^LN||12.4|10*9/L|4.0-11.0|H|||F|||20250518083000
OBX|2|NM|789-8^RBC^LN||4.15|10*12/L|3.8-5.5|N|||F|||20250518083000
OBX|3|NM|718-7^Haemoglobin^LN||10.8|g/dL|12.0-16.0|L|||F|||20250518083000
OBX|4|NM|4544-3^Haematocrit^LN||33.5|%|36.0-46.0|L|||F|||20250518083000
OBX|5|NM|787-2^MCV^LN||80.7|fL|80.0-100.0|N|||F|||20250518083000
OBX|6|NM|777-3^Platelets^LN||310|10*9/L|150-400|N|||F|||20250518083000
OBX|7|NM|770-8^Neutrophils^LN||8.6|10*9/L|2.0-7.5|H|||F|||20250518083000
OBX|8|NM|731-0^Lymphocytes^LN||2.2|10*9/L|1.0-4.0|N|||F|||20250518083000
NTE|1||Microcytic anaemia. Leucocytosis with neutrophilia. Suggest iron studies and consider infection screen.
```

---

## 2

```
MSH|^~\&|LABSYS|UHW|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20002|20250625114500||ORU^R01|MSG20250625114500001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||UHW-445512^^^UHW^MR~6809123456T^^^PPSN^PPSN||Crowley^Tadhg^R^^Mr.||19680719|M|||14 The Mall^^Waterford^^X91 K3R7^IRL^H||+353519234567^PRN^PH||EN|M
PV1|1|O|BIOCHEM^BIOCHEM-OPD^1^UHW||||DOC202^Sheehan^Orla^^^Dr.^MD
ORC|RE|HELORD20250624001|UHWLAB20250625001||CM||||20250625110000
OBR|1|HELORD20250624001|UHWLAB20250625001|24320-4^Basic metabolic panel^LN|||20250624083000||||||||DOC202^Sheehan^Orla^^^Dr.^MD||||||20250625110000|||F
OBX|1|NM|2951-2^Sodium^LN||128|mmol/L|136-145|LL|||F|||20250625103000
OBX|2|NM|2823-3^Potassium^LN||4.1|mmol/L|3.5-5.1|N|||F|||20250625103000
OBX|3|NM|2160-0^Creatinine^LN||92|umol/L|62-106|N|||F|||20250625103000
OBX|4|NM|3094-0^Urea^LN||6.2|mmol/L|2.5-7.8|N|||F|||20250625103000
OBX|5|NM|2345-7^Glucose^LN||5.4|mmol/L|3.9-5.8|N|||F|||20250625103000
OBX|6|NM|17861-6^Calcium^LN||2.18|mmol/L|2.15-2.55|N|||F|||20250625103000
NTE|1||Hyponatraemia. Suggest review medication list for potential causes (diuretics, SSRIs). Repeat in 48 hours if symptomatic.
```

---

## 3

```
MSH|^~\&|HELIX.HEALTH.HEALTHLINK.76|MCN.HL20002|SALESFORCE.HEALTHLINK.76|SALESFORCE.99994.L|20210412103000||VXU^V04|VXU20210412103000001|P|2.4|||AL
PID|1||7312987654B^^^PPSN^PPSN~PMS44521^^^HELIX^MR||Buckley^Siobhán^E^^Mrs.||19730906|F|||9 O'Connell Street^^Waterford^^X91 W6P2^IRL^H||||EN
PV1|1|O||||||||||||||||||||||||||||||||||||67890^GMS
ORC|RE||HELVAX20210412001
RXA|0|1|20210412|20210412|208^Pfizer-BioNTech^CDC|0.3|mL||DOC202^Sheehan^Orla^^^Dr.||^^^Waterford Medical Centre||||EL9264|20210630|PFR^^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RA^Right Upper Arm^HL70163
OBX|1|CE|X0058-0^Consent Given^LOCAL||Yes||||||F|||20210412
OBX|2|CE|X0059-0^Eligibility^LOCAL||Yes||||||F|||20210412
OBX|3|CE|X0064-1^Additional Factors^LOCAL||Frontline healthcare workers||||||F|||20210412
```

---

## 4

```
MSH|^~\&|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20003|UHG|UHG|20250805140015||REF^I12^REF_I12|REF20250805140015001|P|2.4|||AL|NE||UNICODE UTF-8
PRD|PP^Primary Care Provider||^^^Salthill Medical Centre^^C||DOC203^Healy^Diarmuid^^^Dr.^MD^^^GMS&GMS&L^IHPI
PID|1||6408765432D^^^PPSN^PPSN||Walsh^Pádraig^N^^Mr.||19641207|M|||22 Salthill Road^^Salthill^Galway^H91 K7P9^IRL^H||+353917823456^PRN^PH~+353879876543^PRN^CP||EN|M
PV1|1|O
RF1|P^Pending^HL70283|MED^Medical^HL70280|CARD^Cardiology^LOCAL|||20250805
NTE|1||Dear Colleague,\.br\60-year-old male with exertional chest tightness and exercise-limiting dyspnoea. Recent resting ECG shows T-wave inversion V4-V6. Troponin negative x2 in ED last month. Family history of IHD (father MI aged 52).\.br\\.br\PMH: Hypertension, Hyperlipidaemia, Ex-smoker (40 pack years, quit 2020)\.br\Current Meds: Amlodipine 10mg OD, Atorvastatin 40mg ON, Aspirin 75mg OD\.br\\.br\BP today: 148/88. BMI 31.\.br\Requesting assessment and consideration for stress testing.\.br\\.br\Dr. Diarmuid Healy
OBR|1|HELREF20250805001||68461-4^Referral note^LN|||20250805
OBX|1|FT|68461-4^Referral note^LN||Resting ECG 28/07/2025: Sinus rhythm, rate 72. T-wave inversion V4-V6.\.br\Total cholesterol 5.8 mmol/L, LDL 3.9 mmol/L (01/07/2025)\.br\HbA1c 42 mmol/mol\.br\eGFR >90||||||F
```

---

## 5

```
MSH|^~\&|P3048|UHK|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20004|20250910152500||ORU^R01|MSG20250910152500001|P|2.4|||AL|NE||8859/1
PID|1||UHK-889912^^^UHK^MR~8504321678E^^^PPSN^PPSN||Sullivan^Saoirse^C^^Ms.||19850324|F|||27 Castle Street^^Tralee^Co. Kerry^V92 T8N5^IRL^H||+353669812345^PRN^PH||EN|D
PV1|1|I|RESP^RESP-W1^5^UHK||||DOC204^Moriarty^Eoghan^^^Dr.^MD||RESP||||7|||DOC204^Moriarty^Eoghan^^^Dr.^MD|IN||GMS
ORC|RE||UHK-DC20250910001||CM||||20250910150000
OBR|1||UHK-DC20250910001|18842-5^Discharge Summary^LN|||20250906||||||||||||||20250910150000||MDOC|AU
OBX|1|FT|18842-5^Discharge Summary^LN||DISCHARGE SUMMARY\.br\\.br\Patient: Sullivan, Saoirse\.br\DOB: 24/03/1985 MRN: UHK-889912\.br\Admission: 06/09/2025 Discharge: 10/09/2025\.br\\.br\Diagnosis: Acute severe asthma exacerbation\.br\\.br\Presenting Complaint: Increasing wheeze and SOB over 3 days, not responding to salbutamol.\.br\Peak flow on admission: 35% predicted.\.br\\.br\Management: IV magnesium sulphate, nebulised salbutamol + ipratropium, IV hydrocortisone then oral prednisolone.\.br\\.br\Discharge Medications:\.br\- Prednisolone 40mg OD (5 day course remaining)\.br\- Seretide 250 Evohaler 2 puffs BD\.br\- Salbutamol MDI 2 puffs PRN\.br\- Montelukast 10mg ON\.br\\.br\Follow-up: GP review 1 week. Respiratory OPD 6 weeks. Ensure asthma action plan updated.||||||F
```

---

## 6

```
MSH|^~\&|LABSYS|LUH|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20005|20250712083045||ORU^R01|MSG20250712083045001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||LUH-221144^^^LUH^MR~9408765432F^^^PPSN^PPSN||Doherty^Roisín^K^^Ms.||19940617|F|||18 Port Road^^Letterkenny^Co. Donegal^F92 N8X2^IRL^H||+353749812345^PRN^PH~+353879823456^PRN^CP||EN|S
PV1|1|O|HAEM^HAEM-OPD^1^LUH||||DOC205^McLaughlin^Fiachra^^^Dr.^MD
ORC|RE|HELORD20250711001|LUHLAB20250712001||CM||||20250712080000
OBR|1|HELORD20250711001|LUHLAB20250712001|34528-7^Iron studies^LN|||20250711090000||||||||DOC205^McLaughlin^Fiachra^^^Dr.^MD||||||20250712080000|||F
OBX|1|NM|2498-4^Iron^LN||5.2|umol/L|9.0-30.4|L|||F|||20250712074500
OBX|2|NM|2499-2^TIBC^LN||78|umol/L|45-72|H|||F|||20250712074500
OBX|3|NM|2500-7^Transferrin saturation^LN||7|%|20-50|L|||F|||20250712074500
OBX|4|NM|2276-4^Ferritin^LN||6|ug/L|13-150|L|||F|||20250712074500
NTE|1||Iron deficiency confirmed. Low ferritin with low saturation and elevated TIBC. Suggest oral iron supplementation and investigate cause (menorrhagia, coeliac screen, GI assessment if indicated).
```

---

## 7

```
MSH|^~\&|HELIX.HEALTH.HEALTHLINK.13|MCN.HL20006|LABSYS|SUH|20250820080000||OML^O21^OML_O21|OML20250820080000001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||7206543218G^^^PPSN^PPSN||Brennan^Colm^D^^Mr.||19720115|M|||4 Grattan Street^^Sligo^^F91 Y3K8^IRL^H||+353719854321^PRN^PH||EN|M
PV1|1|O||||||DOC206^Gilroy^Niamh^^^Dr.^MD^^^GMS&GMS&L^IHPI
ORC|NW|HELORD20250820001||||||20250820080000|DOC206^Gilroy^Niamh^^^Dr.^MD
OBR|1|HELORD20250820001||24325-3^Hepatic function panel^LN|||20250820||||A||||DOC206^Gilroy^Niamh^^^Dr.^MD
ORC|NW|HELORD20250820002||||||20250820080000|DOC206^Gilroy^Niamh^^^Dr.^MD
OBR|2|HELORD20250820002||4548-4^HbA1c^LN|||20250820||||A||||DOC206^Gilroy^Niamh^^^Dr.^MD
ORC|NW|HELORD20250820003||||||20250820080000|DOC206^Gilroy^Niamh^^^Dr.^MD
OBR|3|HELORD20250820003||24331-1^Lipid panel^LN|||20250820||||A||||DOC206^Gilroy^Niamh^^^Dr.^MD
NTE|1||Annual diabetic review. Patient on metformin and statin. Fasting sample required for lipids.
```

---

## 8

```
MSH|^~\&|IPMS|MUH|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20007|20250903170045||ADT^A01^ADT_A01|ADT20250903170045001|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20250903170000
PID|1||MUH-778834^^^MUH^MR~7908654321H^^^PPSN^PPSN||Quinn^Lorcan^J^^Mr.||19790503|M|||11 Spencer Street^^Castlebar^Co. Mayo^F23 R4W6^IRL^H||+353949854321^PRN^PH||EN|M
PV1|1|I|SURG^SURG-W2^8^MUH||||DOC207^Duffy^Cathal^^^Mr.^FRCSI||GEN||||5|||DOC207^Duffy^Cathal^^^Mr.^FRCSI|EM||GMS|||||||||||||||||||MUH|||||20250903170000
DG1|1||K35.80^Acute appendicitis^ICD10||20250903|A
```

---

## 9

```
MSH|^~\&|LABSYS|CHICRUMLIN|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20008|20250715103000||ORU^R01|MSG20250715103000001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||CHI-445566^^^CHICRUMLIN^MR~1608765432I^^^PPSN^PPSN||Byrne^Oisín^D^^Master||20160223|M|||42 Kildare Road^^Crumlin^Dublin 12^D12 W8N3^IRL^H||+35314523456^PRN^PH||EN
PV1|1|O|PAED^PAED-GI^1^CHICRUMLIN||||DOC208^Fitzpatrick^Maeve^^^Dr.^MD
ORC|RE|HELORD20250714001|CHILAB20250715001||CM||||20250715100000
OBR|1|HELORD20250714001|CHILAB20250715001|31017-7^Coeliac panel^LN|||20250714110000||||||||DOC208^Fitzpatrick^Maeve^^^Dr.^MD||||||20250715100000|||F
OBX|1|NM|31017-7^Anti-tTG IgA^LN||128|U/mL|<7|HH|||F|||20250715093000
OBX|2|NM|56491-4^Anti-DGP IgG^LN||85|U/mL|<7|HH|||F|||20250715093000
OBX|3|NM|2458-8^Total IgA^LN||1.45|g/L|0.5-2.0|N|||F|||20250715093000
NTE|1||Strongly positive coeliac serology. Total IgA normal (valid screen). Recommend paediatric gastroenterology referral for OGD and biopsy.
```

---

## 10

```
MSH|^~\&|LABSYS|ROTUNDA|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20009|20250828091245||ORU^R01|MSG20250828091245001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||ROT-334455^^^ROTUNDA^MR~9607654321J^^^PPSN^PPSN||Fitzgerald^Caoimhe^A^^Ms.||19960211|F|||31 Drumcondra Road^^Dublin 9^^D09 K6R2^IRL^H||+35318723456^PRN^PH~+353876543218^PRN^CP||EN|S
PV1|1|O|ANTE^ANTE-OPD^1^ROTUNDA||||DOC209^Maguire^Deirdre^^^Dr.^MD
ORC|RE|HELORD20250827001|ROTLAB20250828001||CM||||20250828090000
OBR|1|HELORD20250827001|ROTLAB20250828001|56874-1^Antenatal panel^LN|||20250827100000||||||||DOC209^Maguire^Deirdre^^^Dr.^MD||||||20250828090000|||F
OBX|1|CE|882-1^ABO group^LN||A||||||F|||20250828083000
OBX|2|CE|10331-7^Rh type^LN||Positive||||||F|||20250828083000
OBX|3|CE|5196-1^Antibody screen^LN||Negative||||||F|||20250828083000
OBX|4|NM|718-7^Haemoglobin^LN||12.4|g/dL|11.0-16.0|N|||F|||20250828083000
OBX|5|CE|5195-3^Hepatitis B surface Ag^LN||Non-reactive||||||F|||20250828083000
OBX|6|CE|5292-8^Hepatitis C antibody^LN||Non-reactive||||||F|||20250828083000
OBX|7|CE|7917-8^HIV 1+2 Ag+Ab^LN||Non-reactive||||||F|||20250828083000
OBX|8|CE|20507-0^Syphilis screen^LN||Non-reactive||||||F|||20250828083000
OBX|9|CE|5334-8^Rubella IgG^LN||Immune||||||F|||20250828083000
NTE|1||Booking bloods complete. Group A Rh positive. Antibody screen negative. All infection screens non-reactive. Rubella immune.
```

---

## 11

```
MSH|^~\&|LABSYS|MRHT|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20010|20250905141530||ORU^R01|MSG20250905141530001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||MRHT-223344^^^MRHT^MR~6005678912K^^^PPSN^PPSN||Foley^Seán^T^^Mr.||19600913|M|||8 High Street^^Tullamore^Co. Offaly^R35 K2P8^IRL^H||+353579812345^PRN^PH||EN|M
PV1|1|O|URO^URO-OPD^1^MRHT||||DOC210^Egan^Sorcha^^^Dr.^MD
ORC|RE|HELORD20250904001|MRHTLAB20250905001||CM||||20250905140000
OBR|1|HELORD20250904001|MRHTLAB20250905001|2857-1^PSA^LN|||20250904091000||||||||DOC210^Egan^Sorcha^^^Dr.^MD||||||20250905140000|||F
OBX|1|NM|2857-1^PSA total^LN||8.2|ng/mL|<4.0|H|||F|||20250905133000
OBX|2|NM|19197-3^PSA free^LN||1.1|ng/mL|||||F|||20250905133000
OBX|3|NM|12841-3^Free/Total PSA ratio^LN||13|%|>25|L|||F|||20250905133000
NTE|1||Elevated PSA with low free/total ratio. Recommend urgent urology referral for further assessment.
```

---

## 12

```
MSH|^~\&|SWIFTQUEUE|UHG|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20003|20250822081000||SIU^S12^SIU_S12|SIU20250822081000001|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APPT20250822001|HELSCH20250822001||||ROUTINE^Routine^HL70277|||20|MIN|^^20^20250910140000^20250910142000|DOC211^Connolly^Ruairí^^^Dr.^MD|||DOC211^Connolly^Ruairí^^^Dr.^MD|RAD^RAD-MRI^1^UHG|Booked^Booked^HL70278
PID|1||UHG-556677^^^UHG^MR~6408765432D^^^PPSN^PPSN||Walsh^Pádraig^N^^Mr.||19641207|M|||22 Salthill Road^^Salthill^Galway^H91 K7P9^IRL^H||+353917823456^PRN^PH||EN|M
PV1|1|O|RAD^RAD-MRI^1^UHG||||DOC211^Connolly^Ruairí^^^Dr.^MD
RGS|1
AIP|1||DOC211^Connolly^Ruairí^^^Dr.^MD|Accept^Accept^HL70278
AIL|1||RAD^RAD-MRI^1^UHG|Accept^Accept^HL70278
NTE|1||MRI cardiac stress perfusion. Patient has exertional chest tightness. Contraindications checked - no pacemaker/metallic implants. Patient advised nil caffeine 24hrs prior.
```

---

## 13

```
MSH|^~\&|PULMSYS|BSHCORK|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20011|20250730110530||ORU^R01|MSG20250730110530001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||BSH-998811^^^BSHCORK^MR~6703456789L^^^PPSN^PPSN||Twomey^Declan^F^^Mr.||19670428|M|||15 MacCurtain Street^^Cork^^T12 N6E8^IRL^H||+353219854321^PRN^PH||EN|M
PV1|1|O|RESP^RESP-PFT^1^BSHCORK||||DOC212^O'Driscoll^Gráinne^^^Dr.^MD
ORC|RE|HELORD20250730001|BSHPFT20250730001||CM||||20250730110000
OBR|1|HELORD20250730001|BSHPFT20250730001|81459-0^Spirometry panel^LN|||20250730093000||||||||DOC212^O'Driscoll^Gráinne^^^Dr.^MD||||||20250730110000|||F
OBX|1|NM|20150-9^FEV1^LN||1.82|L|3.20-4.50|L|||F|||20250730100000
OBX|2|NM|20152-5^FEV1 percent predicted^LN||52|%|>80|L|||F|||20250730100000
OBX|3|NM|19868-9^FVC^LN||3.45|L|3.80-5.40|L|||F|||20250730100000
OBX|4|NM|19872-1^FEV1/FVC ratio^LN||53|%|>70|L|||F|||20250730100000
OBX|5|NM|69979-4^Post-bronchodilator FEV1^LN||1.95|L||||F|||20250730103000
OBX|6|NM|69981-0^Post-BD FEV1 change^LN||7|%|>12|N|||F|||20250730103000
NTE|1||Moderate obstructive pattern. Minimal bronchodilator reversibility (<12%). Findings consistent with COPD GOLD stage II. Suggest DLCO and CT thorax.
```

---

## 14

```
MSH|^~\&|LABSYS|STGH|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20012|20250918091000||ORU^R01|MSG20250918091000001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||STGH-112233^^^STGH^MR~5209876543M^^^PPSN^PPSN||Power^Bríd^G^^Mrs.||19520814|F|||6 Irishtown^^Clonmel^Co. Tipperary^E91 W7N3^IRL^H||+353529812345^PRN^PH||EN|W
PV1|1|O|RHEUM^RHEUM-OPD^1^STGH||||DOC213^Ryan^Conor^^^Dr.^MD
ORC|RE|HELORD20250917001|STGHLAB20250918001||CM||||20250918090000
OBR|1|HELORD20250917001|STGHLAB20250918001|24326-1^Bone profile^LN|||20250917083000||||||||DOC213^Ryan^Conor^^^Dr.^MD||||||20250918090000|||F
OBX|1|NM|17861-6^Calcium^LN||2.08|mmol/L|2.15-2.55|L|||F|||20250918083000
OBX|2|NM|17862-4^Calcium corrected^LN||2.12|mmol/L|2.15-2.55|L|||F|||20250918083000
OBX|3|NM|6768-6^ALP^LN||135|U/L|44-147|N|||F|||20250918083000
OBX|4|NM|14879-1^Phosphate^LN||0.72|mmol/L|0.81-1.45|L|||F|||20250918083000
OBX|5|NM|1751-7^Albumin^LN||36|g/L|35-52|N|||F|||20250918083000
OBX|6|NM|62292-8^25-OH Vitamin D^LN||18|nmol/L|>50|L|||F|||20250918083000
NTE|1||Low calcium and low vitamin D consistent with osteomalacia. Commence cholecalciferol 1000IU daily. Recheck bone profile and vitamin D in 3 months. Consider DEXA scan.
```

---

## 15

```
MSH|^~\&|LABSYS|NGH|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20013|20250822174500||ORU^R01|MSG20250822174500001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||NGH-667788^^^NGH^MR~7104567891N^^^PPSN^PPSN||Nolan^Darragh^P^^Mr.||19710802|M|||3 Sallins Road^^Naas^Co. Kildare^W91 T3K8^IRL^H||+353459834567^PRN^PH||EN|M
PV1|1|E|ED^ED-MAIN^1^NGH||||DOC214^Whelan^Aisling^^^Dr.^MD
ORC|RE|HELORD20250822001|NGHLAB20250822001||CM||||20250822170000
OBR|1|HELORD20250822001|NGHLAB20250822001|49563-0^Cardiac panel^LN|||20250822153000||||||||DOC214^Whelan^Aisling^^^Dr.^MD||||||20250822170000|||F
OBX|1|NM|10839-9^Troponin I^LN||0.015|ng/mL|<0.040|N|||F|||20250822163000
OBX|2|NM|30522-7^CRP^LN||8.5|mg/L|<5.0|H|||F|||20250822163000
OBX|3|NM|33762-6^NT-proBNP^LN||245|pg/mL|<125|H|||F|||20250822163000
OBX|4|NM|2157-6^CK^LN||180|U/L|39-308|N|||F|||20250822163000
NTE|1||Serial troponin negative. Elevated NT-proBNP may suggest diastolic dysfunction. Echocardiogram recommended.
```

---

## 16

```
MSH|^~\&|IPMS|WGH|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20014|20250701163500||ADT^A03^ADT_A03|ADT20250701163500001|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20250701163000
PID|1||WGH-889933^^^WGH^MR~8107654321O^^^PPSN^PPSN||Doyle^Muireann^T^^Mrs.||19810419|F|||12 South Main Street^^Wexford^^Y35 W4P8^IRL^H||+353539854321^PRN^PH||EN|M
PV1|1|I|MED^MED-W1^12^WGH||||DOC215^Roche^Eoin^^^Dr.^MD||GEN||||3|||DOC215^Roche^Eoin^^^Dr.^MD|IN||GMS|||||||||||||||||||WGH|||||20250628141500|||20250701163000
DG1|1||N39.0^Urinary tract infection^ICD10||20250628|A
DG1|2||E11.9^Type 2 diabetes mellitus^ICD10||20250628|A
```

---

## 17

```
MSH|^~\&|BEAUMONT|BEAUMONT|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20015|20251002091500||RRI^I12^RRI_I12|RRI20251002091500001|P|2.4|||AL|NE||UNICODE UTF-8
MSA|AA|REF20250918001
PRD|PP^Primary Care Provider||^^^Malahide Medical Centre^^C||DOC216^O'Brien^Fionnuala^^^Dr.^MD
PRD|RT^Referred to Provider||^^^BEAUMONT NEUROLOGY^^C||DOC217^Cassidy^Declan^^^Prof.^MD
PID|1||BMT-334455^^^BEAUMONT^MR~7812345678P^^^PPSN^PPSN||Murphy^Eoghan^L^^Mr.||19780226|M|||5 Church Road^^Malahide^Co. Dublin^K36 N2R8^IRL^H||+35318698765^PRN^PH||EN|M
PV1|1|O|NEURO^NEURO-OPD^1^BEAUMONT||||DOC217^Cassidy^Declan^^^Prof.^MD
RF1|A^Accepted^HL70283|MED^Medical^HL70280|NEURO^Neurology^LOCAL|||20251002
NTE|1||Referral accepted. Patient has been added to the urgent neurology clinic list. Appointment date: 20/10/2025 at 14:00. MRI brain has been pre-ordered. Patient should attend fasting.
```

---

## 18

```
MSH|^~\&|RIS|UHG|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20003|20250915103045||ORU^R01|MSG20250915103045001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||UHG-112299^^^UHG^MR~7812345678P^^^PPSN^PPSN||Murphy^Eoghan^L^^Mr.||19780226|M|||5 Church Road^^Malahide^Co. Dublin^K36 N2R8^IRL^H||+35318698765^PRN^PH||EN|M
PV1|1|O|RAD^RAD-MRI^1^UHG||||DOC218^Mannion^Clodagh^^^Dr.^MD
ORC|RE|HELORD20250915001|UGHRAD20250915001||CM||||20250915100000
OBR|1|HELORD20250915001|UGHRAD20250915001|70553^MRI Brain^CPT4|||20250915083000||||||||DOC218^Mannion^Clodagh^^^Dr.^MD||||||20250915100000|||F
OBX|1|FT|18748-4^Diagnostic imaging study^LN||MRI BRAIN WITH CONTRAST\.br\\.br\Clinical Indication: Recurrent headaches with visual aura. Rule out structural lesion.\.br\\.br\Technique: Multiplanar multisequence MRI brain with IV gadolinium.\.br\\.br\Findings:\.br\- No intracranial mass lesion.\.br\- Normal ventricular system.\.br\- Several punctate white matter hyperintensities on T2/FLAIR, non-specific, likely migrainous.\.br\- Normal pituitary. No Chiari malformation.\.br\- Normal intracranial vessels on MRA.\.br\\.br\Conclusion: No significant structural abnormality. Scattered white matter foci consistent with migraine.||||||F
OBX|2|ED|18748-4^Radiology report PDF^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1SSSBCcmFpbiBSZXBvcnQgLSBVbml2ZXJzaXR5IEhvc3BpdGFsIEdhbHdheSkKL0NyZWF0b3IgKFJhZGlvbG9neSBJbmZvcm1hdGlvbiBTeXN0ZW0pCi9Qcm9kdWNlciAoQWdmYSBPUkJJUyBSSVMgdjguMikKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDkxNTEwMzAwMCswMCcwMCcpCj4+CmVuZG9iagpNUkkgQlJBSU4gV0lUSCBDT05UUkFTVAotLS0tLS0tLS0tLS0tLS0tLS0tLS0tClVuaXZlcnNpdHkgSG9zcGl0YWwgR2Fsd2F5ClJhZGlvbG9neSBEZXBhcnRtZW50CgpQYXRpZW50OiBEb3lsZSwgRWFtb25uIFYuCkRPQjogMTIvMDkvMTk3NQpNUk46IFVHSy03Nzg4OTkKClN0dWR5IERhdGU6IDE1LzA5LzIwMjUKUmVwb3J0ZWQgYnk6IERyLiBSaWNoYXJkIEZhaHksIENvbnN1bHRhbnQgUmFkaW9sb2dpc3QKCkZpbmRpbmdzOgotIE5vIGludHJhY3JhbmlhbCBtYXNzIGxlc2lvbi4KLSBOb3JtYWwgdmVudHJpY3VsYXIgc3lzdGVtLgotIFNjYXR0ZXJlZCBwdW5jdGF0ZSB3aGl0ZSBtYXR0ZXIgaHlwZXJpbnRlbnNpdGllcyBvbiBUMi9GTEFJUi4KCkNvbmNsdXNpb246IE5vIHNpZ25pZmljYW50IHN0cnVjdHVyYWwgYWJub3JtYWxpdHku||||||F
```

---

## 19

```
MSH|^~\&|P3048|MERCYUNIVERSITYHOSPITAL|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20016|20250825152030||ORU^R01|MSG20250825152030001|P|2.4|||AL|NE||8859/1
PID|1||MUH-654321^^^MUH^MR~6209876543Q^^^PPSN^PPSN||O'Connor^Fionnuala^R^^Mrs.||19620518|F|||34 Washington Street^^Cork^^T12 X9K4^IRL^H||+353214567890^PRN^PH||EN|W
PV1|1|I|MED^MED-W5^3^MUH||||DOC219^Coughlan^Ronan^^^Dr.^MD
ORC|RE||MUH-DC20250825001||CM||||20250825150000
OBR|1||MUH-DC20250825001|18842-5^Discharge Summary^LN|||20250820||||||||||||||20250825150000||MDOC|AU
OBX|1|FT|18842-5^Discharge Summary^LN||DISCHARGE SUMMARY\.br\\.br\Patient: O'Connor, Fionnuala\.br\DOB: 18/05/1962 MRN: MUH-654321\.br\Admission: 20/08/2025 Discharge: 25/08/2025\.br\\.br\Diagnosis: Community acquired pneumonia (CURB-65 score 2)\.br\\.br\Management: IV co-amoxiclav then switched to oral after 48hrs. Supplemental O2 via nasal cannulae.\.br\\.br\Discharge Meds: Amoxicillin 500mg TDS (5 days remaining), Paracetamol 1g QDS PRN\.br\\.br\Follow-up: GP review 1 week. Repeat CXR 6 weeks.||||||F
OBX|2|ED|18842-5^Discharge letter PDF^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKERpc2NoYXJnZSBTdW1tYXJ5IC0gTWVyY3kgVW5pdmVyc2l0eSBIb3NwaXRhbCkKL0NyZWF0b3IgKENlcm5lciBNaWxsZW5uaXVtIERpc2NoYXJnZSBNb2R1bGUpCi9Qcm9kdWNlciAoQ2VybmVyIE1pbGxlbm5pdW0gdjIwMjUuMDEpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTA4MjUxNTIwMDArMDAnMDAnKQo+PgplbmRvYmoKRElTQ0hBUkdFIFNVTU1BUlkKLS0tLS0tLS0tLS0tLS0tLS0KTWVyY3kgVW5pdmVyc2l0eSBIb3NwaXRhbCwgQ29yawoKUGF0aWVudDogU2hlZWhhbiwgVGVyZXNhIE0uCkRPQjogMzAvMDMvMTk2NQpNUk46IE1VSC0xMjM0NTYKUFBTTjogNjUwMTIzNDU2N1EKCkFkbWlzc2lvbiBEYXRlOiAyMC8wOC8yMDI1CkRpc2NoYXJnZSBEYXRlOiAyNS8wOC8yMDI1CgpEaWFnbm9zaXM6IENvbW11bml0eSBhY3F1aXJlZCBwbmV1bW9uaWEKQ1VSQi02NSBTY29yZTogMgoKTWFuYWdlbWVudDogSVYgY28tYW1veGljbGF2IHRoZW4gb3JhbCBzdGVwLWRvd24uCkRpc2NoYXJnZSBNZWRpY2F0aW9uczogQW1veGljaWxsaW4gNTAwbWcgVERTICg1IGRheXMpLg==||||||F
```

---

## 20

```
MSH|^~\&|LABSYS|STJAMES|HELIX.HEALTH.HEALTHLINK.10|MCN.HL20017|20250604091530||ORU^R01|MSG20250604091530001|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||SJH-776655^^^STJAMES^MR~9803456789R^^^PPSN^PPSN||Moran^Clodagh^S^^Ms.||19980714|F|||45 Thomas Street^^Dublin 8^^D08 W2X3^IRL^H||+35316723456^PRN^PH~+353859876543^PRN^CP||EN|S
PV1|1|O|GUM^GUIDE-OPD^1^STJAMES||||DOC220^Kinsella^Aoife^^^Dr.^MD
ORC|RE|HELORD20250603001|SJHLAB20250604001||CM||||20250604090000
OBR|1|HELORD20250603001|SJHLAB20250604001|90235-8^STI panel^LN|||20250603110000||||||||DOC220^Kinsella^Aoife^^^Dr.^MD||||||20250604090000|||F
OBX|1|CE|6357-8^Chlamydia trachomatis NAAT^LN||Negative||||||F|||20250604083000
OBX|2|CE|21416-3^Neisseria gonorrhoeae NAAT^LN||Negative||||||F|||20250604083000
OBX|3|CE|5292-8^Hepatitis C antibody^LN||Non-reactive||||||F|||20250604083000
OBX|4|CE|5195-3^Hepatitis B surface Ag^LN||Non-reactive||||||F|||20250604083000
OBX|5|CE|7917-8^HIV 1+2 Ag+Ab^LN||Non-reactive||||||F|||20250604083000
OBX|6|CE|20507-0^Syphilis screen^LN||Non-reactive||||||F|||20250604083000
NTE|1||Full STI panel negative. No further action required. Routine repeat screening advised as per risk assessment.
```
