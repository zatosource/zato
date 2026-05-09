# Healthlink - real HL7v2 ER7 messages

## 1

```
MSH|^~\&|P3048|MILL|VHI|VHI|20260115092547||ORU^R01|Q12617263T3610993||2.3||||||8859/1
PID|1|31728^^^MRN^MRN|31728^^^MRN^MRN||BRENNAN^CAOIMHE^^^^^CURRENT|Mother's Maiden Name|20030115|1|Surname at Birth^^^^^^BIRTH||12 Hazel Grove^Blackrock^^""^A94F7K3^IRL^HOME^Co. Dublin^Antrim|Antrim|(087)334-8821^HOME^""~^HOME^"^caoimhe.brennan@icloud.com~(085)219-7743^Mobile^"|(01)287-4590^BUSINESS^""|12|S|""|214178^^^Encounter Num^FINNBR|8234567WA|||||""|0|""|""|""||""
NTE|1|CD:469|15/1/2026 09:07:13 AM Comment by: Devlin , Lorcan Cerner \.br\Encounter Comments\.br\--------------------------------------\.br\\.br\
PD1|""|""|^^0|^Devlin^Lorcan^^^^^^^PRSNL|""||""|""
PV1|1|OUTPATIENT|CM Wellness^^^Carrickmines^^AMB^360 Clinic|""|||PHY Ext ID^Devlin^Lorcan^^^^^^External Id^PRSNL^^^EXTID^""~473821^Devlin^Lorcan^^^^^^Irish Medical Council^PRSNL^^^ORGDR^""|473826^Noonan^Fiachra^^^^^^Irish Medical Council^PRSNL^^^ORGDR^""||CAM Therapy Class|""|""|""|""|""|""||OUTPATIENT|24194^^^Attendance Num^VISITID|""||""||||||||||||||""|""|""|Carrickmines||ACTIVE|||20260115090236
ORC|RE||f78ffgd7-4d5b-55b1-97fe-5657b0721bb8^HNAM_CEREF~3668038^HNAM_EVENTID||||||20260115092546|EXT09234^Devlin^Lorcan^^^^^External Id^PRSNL^^^EXTID^""
OBR|1||f78ffgd7-4d5b-55b1-97fe-5657b0721bb8^HNAM_CEREF~3668038^HNAM_EVENTID|CD:18150760^Key Discharge Checklist Forms^^^UTC Discharge Summary|||20260115091858|20260115091858||||||||||||||20260115092546||MDOC|AU|||||||EXT09234&Devlin&Lorcan&&&&""&External Id&&EXTID||EXT09234&Devlin&Lorcan&&&&""&External Id&&EXTID
ZDS|SIG|EXT09234^Devlin^Lorcan^^^^^External Id^PRSNL^^^EXTID^""|20260115092546|COMP
ZDS|VER|EXT09234^Devlin^Lorcan^^^^^External Id^PRSNL^^^EXTID^""|20260115092546|COMP
ZDS|AU|EXT09234^Devlin^Lorcan^^^^^External Id^PRSNL^^^EXTID^""|Vhi 360 Carrickmines |COMP
OBX|1|FT|CD:18150760^Key Discharge Checklist Forms|| \.br\GP Practice\.br\ GP Practice information freetexted into the discharge summary\.br\ Patient and Visit Information\.br\ Patient Demographics\.br\ Name:BRENNAN, CAOIMHE\.br\ Address:\.br\ 12 Hazel Grove\.br\ Blackrock\.br\ Co. Dublin\.br\ A94F7K3\.br\ Gender:Male\.br\ Date of Birth:15/01/2003\.br\ Phone:3348821\.br\ Emergency Contact:DOYLE, SINEAD\.br\ Telephone: \.br\ 2197743\.br\ NHS: \.br\ 8234567WA\.br\ Other Identifier (MRN): \.br\ 31728\.br\|""||""||""|AU|||20260115092546||EXT09234^Devlin^Lorcan^^^^^External Id^PRSNL^^^EXTID^""
```

---

## 2

```
MSH|^~\&|ADASTRA.Healthlink.16|CAREDOC^06^L|Healthlink||202503271614||REF^I12|2194357|P|2.4|||AL
PRD|RP|Flanagan^Roisin^^^Dr.||CAREDOC^Medical Centre^Waterford Road^^Kilkenny^IRL|^^CAREDOC|^PRN^PH^^^^^^^(056)7725633|78901^IRL^IMC
PRD|PP|Healy^Tadhg^^^Dr.||Greenpark Medical Practice^Green Park^^Kilkenny^V95T2Y3^IRL|^^GREENPK|^PRN^PH^^^^^^^(056)7754678|23456^IRL^IMC
PID|1||KK567890^^^CAREDOC^PI~8601182456^^^PPS^PPSN||Whelan^Caoimhe^M^^Mrs.||19860118|F|||27 Rose Inn Street^^Kilkenny^^R95XD23^IRL^H||^PRN^PH^^^^^^^(056)7727891~^PRN^CP^^^^^^^(085)3456789|||||||||||||IRL
PV1|1|E|CAREDOC^^^CAREDOC||||78901^Flanagan^Roisin^^^Dr.^MD|||MED||||3|||78901^Flanagan^Roisin^^^Dr.^MD|||||||||||||||||||||||||||20250327154100
DG1|1||R10.4^Unspecified abdominal pain^I10||20250327
NTE|1||Patient presented with acute abdominal pain, right lower quadrant, 8 hours duration. Temperature 37.8C, localised tenderness with guarding. Suspect appendicitis. Referred for urgent surgical assessment.
OBR|1|CD202503270001||11488-4^Consultation note^LN|||20250327154100
OBX|1|FT|11488-4^Consultation note^LN||Hx: 28yo female, presented 21:03 with 8hr history RLQ abdominal pain, initially periumbilical now localised. Nausea x2, no vomiting. LMP 3 weeks ago. O/E: Temp 37.8, HR 92, BP 120/78. Abdomen soft, RLQ tenderness with rebound, positive Rovsing's sign. Alvarado score 7. Imp: Likely acute appendicitis. Plan: Urgent referral to surgical team St Luke's Hospital Kilkenny.||||||F
```

---

## 3

```
MSH|^~\&|IPMS.Healthlink.01|STLUKES^KILKENNY^L|Healthlink|MCN.GP12345|20260428093256||ADT^A01^ADT_A01|ADT20260428093256001|P|2.4|||AL
EVN|A01|20260428092600
PID|1||SLK890567^^^STLUKES^MR~9307261345^^^PPS^PPSN||Dunne^Cormac^J^^Mr.||19930726|M|||18 Castle Crescent^^Kilkenny^^R95FP34^IRL^H||^PRN^CP^^^^^^^(083)2345678|||S|||9307261345^^^PPS^PPSN||||IRL
PV1|1|E|ED^^^STLUKES^ED||||65432^Maguire^Sorcha^^^Dr.^MD^^^IMC|||MED||||1|||65432^Maguire^Sorcha^^^Dr.^MD|EM||GMS|||||||||||||||||||STLUKES|||||20260428092600
PV2|||^Chest pain on exertion||||||||2
```

---

## 4

```
MSH|^~\&|IPMS.Healthlink.01|MATER^DUBLIN^L|Healthlink|MCN.GP78901|20260509174156||ADT^A03^ADT_A03|ADT20260509174156001|P|2.4|||AL
EVN|A03|20260509171100
PID|1||MAT345678^^^MATER^MR~8914115789^^^PPS^PPSN||Connolly^Orla^A^^Ms.||19891411|F|||23 Iona Road^^Dublin 9^^D09E2V4^IRL^H||^PRN^PH^^^^^^^(01)8304567~^PRN^CP^^^^^^^(085)4567890|||M|||8914115789^^^PPS^PPSN||||IRL
PV1|1|I|CARD^WARD5B^BED12^MATER||||22334^Kilbane^Fergal^^^Prof.^MD^^^IMC||CAR||||7|||22334^Kilbane^Fergal^^^Prof.^MD|IN||GMS|||||||||||||||01^Home|||||||MATER|||||20260505101100|||20260509171100
PV2|||^Acute coronary syndrome||||||||||4
```

---

## 5

```
MSH|^~\&|P3048.Healthlink.01|BEAUMONT^DUBLIN^L|Healthlink|MCN.GP45678|20260623152641||REF^I12^REF_I12|REF20260623152641001|P|2.4|||AL
PRD|RP|Riordan^Aoife^^^Dr.||Beaumont Hospital^Beaumont Road^^Dublin 9^D09V2N0^IRL|^^BEAUMONT|^PRN^PH^^^^^^^(01)8093000|44556^IRL^IMC
PRD|PP|Hickey^Padraig^^^Dr.||Raheny Medical Centre^10 Howth Road^^Raheny, Dublin 5^D05X2T1^IRL|^^RAHENY|^PRN^PH^^^^^^^(01)8318901|33445^IRL^IMC
PID|1||BEA678901^^^BEAUMONT^MR~7805155678^^^PPS^PPSN||Cullen^Diarmuid^T^^Mr.||19780515|M|||37 Swords Road^^Dublin 9^^D09W4A3^IRL^H||^PRN^CP^^^^^^^(086)8765432|||M|||7805155678^^^PPS^PPSN||||IRL
PV1|1|I|RESP^WARD3A^BED07^BEAUMONT||||44556^Riordan^Aoife^^^Dr.^MD^^^IMC||RES||||7|||44556^Riordan^Aoife^^^Dr.^MD|IN||GMS||||||||||||||01^Home|||||||BEAUMONT|||||20260616131100|||20260623141100
DG1|1||J18.1^Lobar pneumonia^I10||20260616|A
DG1|2||J96.0^Acute respiratory failure^I10||20260616|A
NTE|1||Admitted with community-acquired pneumonia and acute respiratory failure. Required non-invasive ventilation for 48 hours. Treated with IV co-amoxiclav/clarithromycin, stepped down to oral amoxicillin on day 5. Chest X-ray clearing on discharge. Follow-up OPD respiratory clinic 4 weeks. Continue oral antibiotics for further 5 days.
OBR|1|BEA20260623001||18842-5^Discharge summary^LN|||20260623141100
OBX|1|FT|18842-5^Discharge summary^LN||Diagnosis: Community-acquired pneumonia (right middle lobe) with Type 1 respiratory failure\.br\Procedures: NIV (BiPAP) x 48hrs\.br\Medications on discharge:\.br\ - Amoxicillin 500mg TDS x 5 days\.br\ - Salbutamol 100mcg 2 puffs PRN\.br\ - Paracetamol 1g QDS PRN\.br\Follow-up: Respiratory OPD 4 weeks\.br\GP actions: Repeat CXR in 6 weeks, monitor CRP\.br\||||||F
```

---

## 6

```
MSH|^~\&|IPMS.Healthlink.01|CUH^CORK^L|Healthlink|MCN.GP23456|20260321104100||ADT^A03^ADT_A03|ADT20260321104100001|P|2.4|||AL
EVN|A03|20260321091100
PID|1||CUH456789^^^CUH^MR~4407168890^^^PPS^PPSN||Crowley^Nora^E^^Mrs.||19440716|F|||19 Shandon Street^^Cork^^T12DP83^IRL^H||^PRN^PH^^^^^^^(021)4275678|||W|||4407168890^^^PPS^PPSN||||IRL|||||||20260321085600|Y
PV1|1|I|GERI^WARD8^BED03^CUH||||66778^Linehan^Conal^^^Dr.^MD^^^IMC||GER||||5|||66778^Linehan^Conal^^^Dr.^MD|IN||GMS||||||||||||||20^Expired|||||||CUH|||||20260316151100|||20260321091100
PDA|I46.9^Cardiac arrest^I10~C34.9^Malignant neoplasm of bronchus/lung^I10|CUH^WARD8|||20260321085600|Y
PV2|||^End-stage lung carcinoma
```

---

## 7

```
MSH|^~\&|ADASTRA.Healthlink.16|SHANNONDOC^18^L|Healthlink|MCN.GP34567|20260213231456||REF^I12^REF_I12|REF20260213231456001|P|2.4|||AL
PRD|RP|Quinlan^Sinead^^^Dr.||SHANNONDOC^Ardnacrusha Health Centre^^Ardnacrusha, Co. Clare^V94Y8W2^IRL|^^SHANNONDOC|^PRN^PH^^^^^^^(061)459500|55667^IRL^IMC
PRD|PP|Considine^Niall^^^Dr.||Ennis Road Medical Centre^25 Ennis Road^^Limerick^V94D7T1^IRL|^^ENNISRD|^PRN^PH^^^^^^^(061)329012|44778^IRL^IMC
PID|1||SH890123^^^SHANNONDOC^PI~0309185432^^^PPS^PPSN||Hogan^Aisling^K^^Ms.||20030918|F|||31 O'Connell Avenue^^Limerick^^V94XK56^IRL^H||^PRN^CP^^^^^^^(083)8765432|||S
DG1|1||J06.9^Acute upper respiratory infection^I10||20260213
NTE|1||22yo female, presented 21:30 with 3-day history sore throat, fever, malaise. No stridor, no drooling. O/E: Temp 38.2, erythematous pharynx with bilateral tonsillar exudate. Centor score 3. Commenced phenoxymethylpenicillin 500mg QDS x 10 days. Advised to attend own GP if symptoms worsen or not improving after 48 hours.
OBR|1|SH20260213001||11488-4^Consultation note^LN|||20260213223100
OBX|1|FT|11488-4^Consultation note^LN||Assessment: Acute tonsillitis\.br\Centor score 3 (fever, tonsillar exudate, tender anterior cervical lymphadenopathy)\.br\Treatment: Phenoxymethylpenicillin 500mg QDS x 10 days\.br\Advice: Fluids, paracetamol PRN, GP review if worsening\.br\||||||F
```

---

## 8

```
MSH|^~\&|IPMS.Healthlink.01|TALLAGHT^DUBLIN^L|Healthlink|MCN.GP56789|20260717111100||SIU^S12^SIU_S12|SIU20260717111100001|P|2.4|||AL
SCH|APT20260717001|APT20260717001|||||ROUTINE^Routine^HL70276|^Cardiology OPD Review||30|min|^^30^20260823104100^20260823111100||88990^Gaffney^Siobhan^^^Dr.^MD
PID|1||TUH234567^^^TALLAGHT^MR~9710265678^^^PPS^PPSN||Farrell^Niamh^R^^Ms.||19971026|F|||42 Fortunestown Lane^^Tallaght, Dublin 24^^D24Y8N2^IRL^H||^PRN^CP^^^^^^^(086)2223344|||S
PV1|1|O|CARD^OPD-CARD^1^TALLAGHT||||88990^Gaffney^Siobhan^^^Dr.^MD|||CAR
RGS|1
AIP|1||88990^Gaffney^Siobhan^^^Dr.^MD
NTE|1||Follow-up cardiology review re: atrial fibrillation. Bring recent ECG results.
```

---

## 9

```
MSH|^~\&|IPMS.Healthlink.01|UHG^GALWAY^L|Healthlink|MCN.GP67890|20260831151100||SIU^S12^SIU_S12|SIU20260831151100001|P|2.4|||AL
SCH|WL20260831001|WL20260831001|||||ELECTIVE^Elective^HL70276|^Orthopaedic Surgery - Total Knee Replacement||0|min|^^0^20261114000000^20270228000000||99001^Mannion^Darragh^^^Mr.^MS
PID|1||UHG765432^^^UHG^MR~6511155789^^^PPS^PPSN||Fahy^Brendan^B^^Mr.||19651115|M|||11 Salthill Crescent^^Galway^^H91RK52^IRL^H||^PRN^PH^^^^^^^(091)528901~^PRN^CP^^^^^^^(085)8887766|||M
RGS|1
AIL|1||ORTH^THEATRE2^1^UHG
AIP|1||99001^Mannion^Darragh^^^Mr.^MS
NTE|1||Waiting list for elective left total knee replacement. Severe OA left knee. Pre-op assessment required prior to scheduling.
```

---

## 10

```
MSH|^~\&|LABSYS.Healthlink.03|ENNISLAB^ENNIS^L|Healthlink|MCN.GP34567|20260425105641||ORU^R01^ORU_R01|LRES20260425105641001|P|2.4|||AL
PID|1||LB567890^^^ENNISLAB^MR~8207261345^^^PPS^PPSN||Shanahan^Declan^P^^Mr.||19820726|M|||15 Abbey Street^^Ennis, Co. Clare^^V95TH34^IRL^H||^PRN^CP^^^^^^^(083)3334455
PV1|1|O|GP^^^ENNISRD||||44778^Considine^Niall^^^Dr.^MD^^^IMC
OBR|1|GP20260423001|LB20260424001|24326-1^Basic Metabolic Panel^LN|||20260423101100|||||||||44778^Considine^Niall^^^Dr.^MD^^^IMC||||||20260425105100|||F|||||||44778&Considine&Niall
OBX|1|NM|2345-7^Glucose (fasting)^LN||6.8|mmol/L|3.9-5.5|H|||F|||20260424091100
OBX|2|NM|2160-0^Creatinine^LN||88|umol/L|62-106|N|||F|||20260424091100
OBX|3|NM|3094-0^Urea^LN||5.8|mmol/L|2.5-7.1|N|||F|||20260424091100
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F|||20260424091100
OBX|5|NM|2823-3^Potassium^LN||4.5|mmol/L|3.5-5.1|N|||F|||20260424091100
OBX|6|NM|14647-2^Total Cholesterol^LN||6.2|mmol/L|<5.0|H|||F|||20260424091100
OBX|7|NM|4548-4^HbA1c^LN||48|mmol/mol|<42|H|||F|||20260424091100
NTE|1||Glucose and HbA1c elevated - consistent with pre-diabetic range. Recommend dietary advice and repeat in 3 months.
```

---

## 11

```
MSH|^~\&|LABSYS.Healthlink.03|STJAMES^DUBLIN^L|Healthlink|MCN.GP89012|20260515121100||ORU^R01^ORU_R01|LRES20260515121100001|P|2.4|||AL
PID|1||SJH902345^^^STJAMES^MR~7408075789^^^PPS^PPSN||Keogh^Eileen^M^^Mrs.||19740807|F|||46 Meath Street^^Dublin 8^^D08NF32^IRL^H||^PRN^PH^^^^^^^(01)4535678
PV1|1|O|GP^^^THOMASST||||55667^Mulligan^Cathal^^^Dr.^MD^^^IMC
OBR|1|GP20260513001|SJH20260514001|58410-2^CBC panel^LN|||20260513151100|||||||||55667^Mulligan^Cathal^^^Dr.^MD^^^IMC||||||20260515114100|||F||||||HM
OBX|1|NM|6690-2^WBC^LN||3.2|10*9/L|4.0-11.0|L|||F|||20260514101100
OBX|2|NM|789-8^RBC^LN||3.65|10*12/L|3.80-5.20|L|||F|||20260514101100
OBX|3|NM|718-7^Haemoglobin^LN||105|g/L|120-160|L|||F|||20260514101100
OBX|4|NM|4544-3^Haematocrit^LN||0.32|L/L|0.36-0.46|L|||F|||20260514101100
OBX|5|NM|787-2^MCV^LN||87.7|fL|80.0-100.0|N|||F|||20260514101100
OBX|6|NM|785-6^MCH^LN||28.8|pg|27.0-33.0|N|||F|||20260514101100
OBX|7|NM|777-3^Platelets^LN||180|10*9/L|150-400|N|||F|||20260514101100
NTE|1||Mild pancytopenia. Suggest B12/folate levels, reticulocyte count, ferritin. Clinical correlation advised.
```

---

## 12

```
MSH|^~\&|RADSYS.Healthlink.04|CUH^CORK^L|Healthlink|MCN.GP23456|20260404164100||ORU^R01^ORU_R01|RRES20260404164100001|P|2.4|||AL
PID|1||CUH012345^^^CUH^MR~7013204678^^^PPS^PPSN||Twomey^Finbarr^F^^Mr.||19701320|M|||28 South Mall^^Cork^^T23R9W1^IRL^H||^PRN^CP^^^^^^^(086)4445566
PV1|1|O|GP^^^WESTCORK||||66778^Linehan^Conal^^^Dr.^MD^^^IMC
OBR|1|GP20260401001|CUH20260403001|71020^Chest X-ray PA and lateral^LN|||20260403111100|||||||||66778^Linehan^Conal^^^Dr.^MD^^^IMC||||||20260404161100|||F||||||RAD
OBX|1|FT|71020^Chest X-ray PA and lateral^LN||PA and lateral chest radiograph\.br\\.br\Clinical indication: Persistent cough 6 weeks, weight loss\.br\\.br\Findings: The heart size is normal. There is a 2.5cm spiculated opacity in the right upper lobe consistent with a pulmonary mass. No pleural effusion. No rib destruction. Mediastinal contour is normal.\.br\\.br\Impression: Right upper lobe pulmonary mass suspicious for bronchogenic carcinoma. Urgent CT thorax recommended.\.br\\.br\Reported by: Dr. Roisin Buckley, Consultant Radiologist\.br\||||||F|||20260404161100
NTE|1||URGENT: Suspicious pulmonary mass. CT thorax requested. Patient to be contacted for urgent follow-up.
```

---

## 13

```
MSH|^~\&|HELIX.Healthlink.77|GP12345^RAHENY^L|Healthlink|ENNISLAB|20260618092600||OML^O21^OML_O21|OML20260618092600001|P|2.4|||AL
PID|1||GP456789^^^GP12345^PI~9405187890^^^PPS^PPSN||Moran^Saoirse^A^^Ms.||19940518|F|||12 Clontarf Road^^Raheny, Dublin 5^^D05T1K2^IRL^H||^PRN^CP^^^^^^^(085)6667788
PV1|1|O|GP^^^RAHENY||||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
ORC|NW|GP20260618001|||IP||||20260618082100|||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
OBR|1|GP20260618001||24331-1^Lipid Panel^LN|||20260618081100||||A|||||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
OBR|2|GP20260618001||4548-4^HbA1c^LN|||20260618081100||||A|||||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
OBR|3|GP20260618001||14927-8^Triglycerides^LN|||20260618081100||||A|||||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
DG1|1||E11.9^Type 2 diabetes mellitus^I10||20260618
NTE|1||Annual diabetic review bloods. Patient fasting. Please include eGFR.
```

---

## 14

```
MSH|^~\&|SALESFORCE.Healthlink.76|99994|Healthlink|MCN.GP12345|202204281541||VXU^V04^VXU_V04|VXU20220428154105004675|P|2.4|||AL
PID|1||8709154567^^^PPS^PPSN~PMS567890^^^PMS^PI||Treacy^Mairead^B^^Mrs.||19870915|F|||8 High Street^Flat 3^Killarney^^V93DK45^IRL^H^^^^Kerry|Kerry|^PRN^CP^^^^^^^(086)2345678~^PRN^PH^^^^^^^(064)6635678
PV1|1|O
ORC|RE|VAX20220428001||||||20220428
RXA|0|1|20220428151100||208^COVID-19, mRNA, spike protein, LNP, preservative free, 30 mcg/0.3mL dose^CVX|0.3|mL|00|^Treacy^Mairead||^HSE Vaccination Centre^Kerry|||||EW8237^Pfizer/BioNTech^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||208^COVID-19 mRNA^CVX||||||F
OBX|2|CE|59781-5^Dose Number^LN||1^First Dose^LN||||||F
OBX|3|TS|30952-6^Date vaccine information statement published^LN||20201210||||||F
OBX|4|CE|30963-3^Vaccine funding source^LN||PHC^Public health clinic^CDCPHINVS||||||F
NTE|1||Batch EW8237, Pfizer/BioNTech Comirnaty. No immediate adverse reaction. Second dose scheduled 20220519.
```

---

## 15

```
MSH|^~\&|COMPLETEGP.Healthlink.77|GP78901^DRUMCONDRA^L|Healthlink|MATER|20260803124100||REF^I12^REF_I12|REF20260803124100001|P|2.4|||AL
RF1|A^Active|R^Routine|MED^Medical||20260803
PRD|RP|Grealish^Emer^^^Dr.||Drumcondra Medical Centre^15 Dorset Street Upper^^Dublin 1^D01V2W8^IRL|^^DRUMCON|^PRN^PH^^^^^^^(01)8364567|66889^IRL^IMC
PRD|CP|Kilbane^Fergal^^^Prof.||Mater Misericordiae University Hospital^Eccles Street^^Dublin 7^D07R2WY^IRL|^^MATER|^PRN^PH^^^^^^^(01)8032000|22334^IRL^IMC
PID|1||GP678901^^^GP78901^PI~7613255789^^^PPS^PPSN||Redmond^Ciaran^D^^Mr.||19761325|M|||14 Drumcondra Road^^Glasnevin, Dublin 9^^D09PK12^IRL^H||^PRN^CP^^^^^^^(085)8889900|||M
PV1|1|O|GP^^^DRUMCON||||66889^Grealish^Emer^^^Dr.^MD^^^IMC
OBR|1|GP20260803001||57133-1^Referral Note^LN|||20260803121100
OBX|1|FT|57133-1^Referral Note^LN||Referral to Cardiology\.br\\.br\52yo male, 3 month history exertional chest pain, relieved by rest. Risk factors: smoker 30 pack-years, hypertension (controlled on Ramipril 5mg), BMI 32, FHx MI in father at age 55.\.br\\.br\ECG: Sinus rhythm, lateral ST depression (V5-V6).\.br\Bloods: Total cholesterol 6.8, LDL 4.2, HDL 1.0, Troponin <5.\.br\\.br\Current medications: Ramipril 5mg OD, Atorvastatin 40mg ON, Aspirin 75mg OD.\.br\\.br\Request: Assessment for possible angina, consideration for stress test/angiography.\.br\||||||F
NTE|1||Urgent referral. ECG attached. Patient informed of smoking cessation supports.
```

---

## 16

```
MSH|^~\&|P3048.Healthlink.01|MATER^DUBLIN^L|Healthlink|MCN.GP78901|20260818104100||RRI^I12^RRI_I12|RRI20260818104100001|P|2.4|||AL
RF1|A^Active|R^Routine|MED^Medical||20260803||20260816
PRD|CP|Kilbane^Fergal^^^Prof.||Mater Misericordiae University Hospital^Eccles Street^^Dublin 7^D07R2WY^IRL|^^MATER|^PRN^PH^^^^^^^(01)8032000|22334^IRL^IMC
PRD|PP|Grealish^Emer^^^Dr.||Drumcondra Medical Centre^15 Dorset Street Upper^^Dublin 1^D01V2W8^IRL|^^DRUMCON|^PRN^PH^^^^^^^(01)8364567|66889^IRL^IMC
PID|1||MAT890123^^^MATER^MR~7613255789^^^PPS^PPSN||Redmond^Ciaran^D^^Mr.||19761325|M|||14 Drumcondra Road^^Glasnevin, Dublin 9^^D09PK12^IRL^H
OBR|1|GP20260803001||57133-1^Referral Note^LN|||20260816151100
OBX|1|FT|57133-1^Referral Note^LN||Referral acknowledged. Seen in cardiology OPD 16/08/2026.\.br\Exercise stress test: Positive for ischaemia at 7 METS (ST depression 2mm leads V4-V6).\.br\Plan: Scheduled for coronary angiography 28/08/2026.\.br\Medications: Increased atorvastatin to 80mg ON, added Bisoprolol 2.5mg OD.\.br\Patient counselled on smoking cessation, referred to cardiac rehab.\.br\||||||F
NTE|1||Angiography date confirmed 28/08/2026 at Mater cath lab. Fasting from midnight. Contact Mater cardiac day ward for queries (01) 803 4556.
```

---

## 17

```
MSH|^~\&|LABSYS.Healthlink.03|STVINCENTS^DUBLIN^L|Healthlink|MCN.GP90123|20260414171100||ORU^R01^ORU_R01|LRES20260414171100001|P|2.4|||AL
PID|1||SVH567890^^^STVINCENTS^MR~5706131345^^^PPS^PPSN||Mulcahy^Padraig^J^^Mr.||19570613|M|||21 Merrion Square^^Dublin 4^^D04E5F7^IRL^H||^PRN^PH^^^^^^^(01)2698765
PV1|1|O|GP^^^MERRION||||77889^Costigan^Aisling^^^Dr.^MD^^^IMC
OBR|1|GP20260412001|SVH20260413001|24326-1^Basic Metabolic Panel^LN|||20260412101100|||||||||77889^Costigan^Aisling^^^Dr.^MD^^^IMC||||||20260414170100|||C||||||CH
OBX|1|NM|2823-3^Potassium^LN||4.3|mmol/L|3.5-5.1|N|||C|||20260413101100
NTE|1||CORRECTED RESULT: Previously reported potassium 6.8 mmol/L was due to haemolysed sample. Repeat non-haemolysed specimen: 4.3 mmol/L (normal). Original report dated 13/04/2026 should be disregarded.
OBX|2|NM|2951-2^Sodium^LN||141|mmol/L|136-145|N|||F|||20260413101100
OBX|3|NM|2160-0^Creatinine^LN||92|umol/L|62-106|N|||F|||20260413101100
OBX|4|NM|3094-0^Urea^LN||6.1|mmol/L|2.5-7.1|N|||F|||20260413101100
```

---

## 18

```
MSH|^~\&|HELIX.Healthlink.77|GP12345^RAHENY^L|Healthlink|HEALTHLINK_EXCHANGE|20260925154100||MDM^T02^MDM_T02|MDM20260925154100001|P|2.4|||AL
EVN|T02|20260925154100
PID|1||GP890123^^^GP12345^PI~9007261345^^^PPS^PPSN||Hennessy^Orla^A^^Ms.||19900726|F|||58 Vernon Avenue^^Dublin 3^^D03H2K5^IRL^H||^PRN^CP^^^^^^^(085)4325678
PV1|1|O|GP^^^RAHENY||||33445^Hickey^Padraig^^^Dr.^MD^^^IMC
TXA|1|PRESC|FT||33445^Hickey^Padraig^^^^^IMC|20260925154100||||||RX20260925001^^^GP12345^PLAC||||||||AU|||||33445^Hickey^Padraig^^^^^IMC&20260925154100
OBX|1|ED|PRESCRIPTION^Electronic Prescription^L||^TEXT^XML^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4NCjxDbGluaWNhbERvY3VtZW50IHhtbG5zPSJ1cm46aGw3LW9yZzp2MyI+DQogIDxpZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4yLjguMy43IiBleHRlbnNpb249IlJYMjAyNTA4MTIwMDEiLz4NCiAgPGNvZGUgY29kZT0iNTc4MzMtNiIgZGlzcGxheU5hbWU9IlByZXNjcmlwdGlvbiIgY29kZVN5c3RlbT0iMi4xNi44NDAuMS4xMTM4ODMuNi4xIi8+DQogIDx0aXRsZT5FbGVjdHJvbmljIFByZXNjcmlwdGlvbjwvdGl0bGU+DQogIDxlZmZlY3RpdmVUaW1lIHZhbHVlPSIyMDI1MDgxMjE0MzAwMCIvPg0KICA8Y29tcG9uZW50Pg0KICAgIDxzZWN0aW9uPg0KICAgICAgPHRleHQ+DQogICAgICAgIDxsaXN0Pg0KICAgICAgICAgIDxpdGVtPkFtb3hpY2lsbGluIDUwMG1nIGNhcHN1bGVzIC0gMSB0aHJlZSB0aW1lcyBkYWlseSB4IDcgZGF5cyAoMjEgY2Fwc3VsZXMpPC9pdGVtPg0KICAgICAgICAgIDxpdGVtPkxhbnNvcHJhem9sZSAzMG1nIGNhcHN1bGVzIC0gMSBkYWlseSB4IDI4IGRheXMgKDI4IGNhcHN1bGVzKTwvaXRlbT4NCiAgICAgICAgPC9saXN0Pg0KICAgICAgPC90ZXh0Pg0KICAgIDwvc2VjdGlvbj4NCiAgPC9jb21wb25lbnQ+DQo8L0NsaW5pY2FsRG9jdW1lbnQ+||||||F
```

---

## 19

```
MSH|^~\&|LABSYS.Healthlink.03|UHL^LIMERICK^L|Healthlink|MCN.GP34567|20260311131100||ORU^R01^ORU_R01|LRES20260311131100001|P|2.4|||AL
PID|1||UHL678901^^^UHL^MR~7911115789^^^PPS^PPSN||Halpin^Ronan^G^^Mr.||19791111|M|||37 Ennis Road^^Limerick^^V94N6K2^IRL^H||^PRN^CP^^^^^^^(086)5556677
PV1|1|O|GP^^^ENNISRD||||44778^Considine^Niall^^^Dr.^MD^^^IMC
OBR|1|GP20260308001|UHL20260310001|630-4^Urine culture^LN|||20260308111100|||||||||44778^Considine^Niall^^^Dr.^MD^^^IMC||||||20260311124100|||F||||||MB
OBX|1|FT|630-4^Urine culture^LN||Specimen: Midstream urine\.br\Culture: Heavy growth of Escherichia coli >10^5 CFU/mL\.br\Sensitivities:\.br\ Amoxicillin: Resistant\.br\ Co-amoxiclav: Sensitive\.br\ Trimethoprim: Resistant\.br\ Nitrofurantoin: Sensitive\.br\ Ciprofloxacin: Sensitive\.br\||||||F
OBX|2|ED|PDF^Sensitivity Report^L||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PC9GMSApPj4+Pj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyMTIKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNaWNyb2Jpb2xvZ3kgU2Vuc2l0aXZpdHkgUmVwb3J0KSBUago1MCA2NTAgVGQKKFNwZWNpbWVuOiBNaWRzdHJlYW0gVXJpbmUpIFRqCjUwIDYzMCBUZAooQ3VsdHVyZTogRS4gY29saSA+MTBeNSBDRlUvbUwpIFRqCjUwIDYxMCBUZAooQW1veGljaWxsaW46IFJlc2lzdGFudCkgVGoKNTAgNTkwIFRkCihOaXRyb2Z1cmFudG9pbjogU2Vuc2l0aXZlKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNjAgMDAwMDAgbiAKMDAwMDAwMDMyNSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjU4MwolJUVPRgo=||||||F
NTE|1||E. coli UTI confirmed. Resistant to amoxicillin and trimethoprim. Recommend nitrofurantoin 100mg MR BD x 5 days.
```

---

## 20

```
MSH|^~\&|LABSYS.Healthlink.03|STJAMES^DUBLIN^L|Healthlink|MCN.GP89012|20260502171100||ORU^R01^ORU_R01|LRES20260502171100001|P|2.4|||AL
PID|1||SJH012345^^^STJAMES^MR~6704205789^^^PPS^PPSN||Geraghty^Nuala^T^^Mrs.||19670420|F|||29 Cork Street^^Dublin 8^^D08Y4W2^IRL^H||^PRN^PH^^^^^^^(01)4539012
PV1|1|O|GP^^^THOMASST||||55667^Mulligan^Cathal^^^Dr.^MD^^^IMC
OBR|1|GP20260418001|SJH20260501001|22634-0^Pathology report^LN|||20260418151100|||||||||55667^Mulligan^Cathal^^^Dr.^MD^^^IMC||||||20260502161100|||F||||||SP
OBX|1|FT|22634-0^Pathology report^LN||Specimen: Skin punch biopsy right forearm\.br\Macroscopic: Skin ellipse 8x5x4mm with 6mm diameter pigmented lesion, central dark area.\.br\Microscopic: Sections show a compound melanocytic naevus with mild architectural atypia. Junctional component shows nesting without pagetoid spread. No mitoses identified. Margins clear.\.br\Diagnosis: Compound melanocytic naevus, mildly dysplastic (low grade). Excision margins clear.\.br\Reported by: Dr. Roisin Buckley, Consultant Histopathologist.\.br\||||||F
OBX|2|ED|PDF^Histopathology Report^L||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PC9GMSApPj4+Pj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihIaXN0b3BhdGhvbG9neSBSZXBvcnQgLSBTdCBKYW1lcydzIEhvc3BpdGFsKSBUago1MCA2NTAgVGQKKFNwZWNpbWVuOiBTa2luIHB1bmNoIGJpb3BzeSByaWdodCBmb3JlYXJtKSBUago1MCA2MzAgVGQKKERpYWdub3NpczogQ29tcG91bmQgbWVsYW5vY3l0aWMgbmFldnVzKSBUago1MCA2MTAgVGQKKG1pbGRseSBkeXNwbGFzdGljIC0gbG93IGdyYWRlKSBUago1MCA1OTAgVGQKKEV4Y2lzaW9uIG1hcmdpbnMgY2xlYXIpIFRqCjUwIDU3MCBUZAooUmVwb3J0ZWQgYnk6IERyIEFvaWZlIEtpbnNlbGxhKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNjAgMDAwMDAgbiAKMDAwMDAwMDMyNSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjYyMQolJUVPRgo=||||||F
NTE|1||Low-grade dysplastic naevus, completely excised. Recommend routine clinical surveillance, no further excision needed.
```
