# OSCAR EMR - real HL7v2 ER7 messages

---

## 1. ORU^R01 - CBC lab result from provincial lab

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260401090000||ORU^R01^ORU_R01|OSC00001|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||1234567890^^^ON_HCN^JHN||Tremblay^Anne^Marie^^Mme||19770315|F|||42 Maple Ave^^Kitchener^ON^N2H 3G5^CA||^^PH^5195551234
OBR|1|ORD001^OSCAR|SPE001^LIFELABS|CBC^Complete Blood Count^LN|||20260401074500|||||||||1234567890^Tremblay^Anne M^^^^||||||20260401090000||LAB|F
OBX|1|NM|6690-2^WBC^LN||7.5|x10*9/L|4.0-11.0|N|||F
OBX|2|NM|789-8^RBC^LN||4.38|x10*12/L|3.80-5.80|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||132|g/L|120-160|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||0.39|L/L|0.36-0.46|N|||F
OBX|5|NM|777-3^Platelets^LN||215|x10*9/L|150-400|N|||F
OBX|6|NM|787-2^MCV^LN||89.0|fL|80.0-100.0|N|||F
```

## 2. ORU^R01 - lipid panel with abnormal cholesterol

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260402103000||ORU^R01^ORU_R01|OSC00002|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||2345678901^^^ON_HCN^JHN||Gauthier^Robert^Michel^^Mr||19620810|M|||18 King St^^Guelph^ON^N1H 1B6^CA||^^PH^5195552345
OBR|1|ORD002^OSCAR|SPE002^GAMMA_DYNACARE|LIPID^Lipid Panel^LN|||20260402080000|||||||||2345678901^Gauthier^Robert M^^^^||||||20260402103000||LAB|F
OBX|1|NM|2093-3^Total Cholesterol^LN||6.8|mmol/L|<5.2|H|||F
OBX|2|NM|2571-8^Triglycerides^LN||2.4|mmol/L|<1.7|H|||F
OBX|3|NM|2085-9^HDL Cholesterol^LN||1.05|mmol/L|>1.0|N|||F
OBX|4|NM|13457-7^LDL Cholesterol^LN||4.66|mmol/L|<3.4|H|||F
OBX|5|NM|9830-1^Total/HDL Ratio^LN||6.5||<4.0|H|||F
NTE|1||Patient fasting for 12 hours prior to sample collection.
```

## 3. ORU^R01 - thyroid function tests

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260403141500||ORU^R01^ORU_R01|OSC00003|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||3456789012^^^ON_HCN^JHN||Deschenes^Louise^Marie^^Mme||19880923|F|||77 Water St^^St. Catharines^ON^L2R 2A3^CA||^^PH^9055553456
OBR|1|ORD003^OSCAR|SPE003^LIFELABS|THYR^Thyroid Panel^LN|||20260403080000|||||||||3456789012^Deschenes^Louise M^^^^||||||20260403141500||LAB|F
OBX|1|NM|3016-3^TSH^LN||8.75|mIU/L|0.35-5.50|H|||F
OBX|2|NM|3026-2^Free T4^LN||9.1|pmol/L|10.0-25.0|L|||F
OBX|3|NM|3024-7^Free T3^LN||3.2|pmol/L|3.5-6.5|L|||F
NTE|1||Suggest clinical correlation. Results consistent with primary hypothyroidism.
```

## 4. ORU^R01 - urinalysis result

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260404110000||ORU^R01^ORU_R01|OSC00004|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||4567890123^^^ON_HCN^JHN||Park^Jae-Won^^^Mr||19950417|M|||55 Charles St^^Brampton^ON^L6Y 1T3^CA||^^PH^9055554567
OBR|1|ORD004^OSCAR|SPE004^LIFELABS|UA^Urinalysis^LN|||20260404083000|||||||||4567890123^Park^Jae-Won^^^^||||||20260404110000||LAB|F
OBX|1|ST|5778-6^Color^LN||Yellow||||||F
OBX|2|ST|5767-9^Appearance^LN||Clear||||||F
OBX|3|NM|5803-2^pH^LN||6.0||5.0-8.0|N|||F
OBX|4|NM|5811-5^Specific Gravity^LN||1.020||1.005-1.030|N|||F
OBX|5|ST|5804-0^Protein^LN||Negative||Negative|N|||F
OBX|6|ST|5792-7^Glucose^LN||Negative||Negative|N|||F
OBX|7|NM|5821-4^WBC^LN||2|/HPF|0-5|N|||F
OBX|8|NM|13945-1^RBC^LN||0|/HPF|0-3|N|||F
```

## 5. ORU^R01 - HbA1c diabetes monitoring

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260405093000||ORU^R01^ORU_R01|OSC00005|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||5678901234^^^ON_HCN^JHN||Kaur^Harpreet^^^Ms||19700630|F|||310 Queen St^^Mississauga^ON^L5B 1C2^CA||^^PH^9055555678
OBR|1|ORD005^OSCAR|SPE005^GAMMA_DYNACARE|HBA1C^Hemoglobin A1c^LN|||20260405074500|||||||||5678901234^Kaur^Harpreet^^^^||||||20260405093000||LAB|F
OBX|1|NM|4548-4^Hemoglobin A1c^LN||0.078|fraction|<=0.070|H|||F
OBX|2|NM|2345-7^Glucose Fasting^LN||8.2|mmol/L|3.3-5.5|HH|||F
NTE|1||HbA1c of 7.8% corresponds to an estimated average glucose of 9.8 mmol/L.
```

## 6. ORU^R01 - liver function panel

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260406144500||ORU^R01^ORU_R01|OSC00006|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||6789012345^^^ON_HCN^JHN||Lafleur^Guy^Pierre^^Mr||19530102|M|||200 Richmond St^^London^ON^N6A 3L4^CA||^^PH^5195556789
OBR|1|ORD006^OSCAR|SPE006^LIFELABS|LIVER^Hepatic Function Panel^LN|||20260406081000|||||||||6789012345^Lafleur^Guy P^^^^||||||20260406144500||LAB|F
OBX|1|NM|1742-6^ALT^LN||85|U/L|7-56|H|||F
OBX|2|NM|1920-8^AST^LN||72|U/L|10-40|H|||F
OBX|3|NM|6768-6^Alkaline Phosphatase^LN||110|U/L|44-147|N|||F
OBX|4|NM|1975-2^Total Bilirubin^LN||28|umol/L|5-21|H|||F
OBX|5|NM|2885-2^Total Protein^LN||68|g/L|60-83|N|||F
OBX|6|NM|1751-7^Albumin^LN||35|g/L|35-52|N|||F
NTE|1||Elevated transaminases and bilirubin. Suggest hepatobiliary workup.
```

## 7. ORU^R01 - prenatal screening results

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260407101500||ORU^R01^ORU_R01|OSC00007|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||7890123456^^^ON_HCN^JHN||Bergeron^Chloe^Sylvie^^Mme||19950812|F|||63 Sussex Dr^^Ottawa^ON^K1N 6Z6^CA||^^PH^6135557890
OBR|1|ORD007^OSCAR|SPE007^GAMMA_DYNACARE|PNS^Prenatal Screening^LN|||20260407080000|||||||||7890123456^Bergeron^Chloe S^^^^||||||20260407101500||LAB|F
OBX|1|NM|48803-1^AFP^LN||32.5|kU/L|10.0-150.0|N|||F
OBX|2|NM|2106-3^Beta hCG^LN||45000|IU/L||||F
OBX|3|NM|2243-4^Estriol^LN||5.2|nmol/L||||F
OBX|4|ST|49246-2^Screen Result^LN||Screen Negative||||||F
NTE|1||Risk assessment: Trisomy 21 <1:10000, Trisomy 18 <1:10000, ONTD <1:10000.
```

## 8. ORU^R01 - INR coagulation result for warfarin monitoring

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260408134500||ORU^R01^ORU_R01|OSC00008|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||8901234567^^^ON_HCN^JHN||Leblanc^Raymond^Andre^^Mr||19480318|M|||25 Main St^^Stratford^ON^N5A 1S1^CA||^^PH^5195558901
OBR|1|ORD008^OSCAR|SPE008^LIFELABS|COAG^Coagulation Panel^LN|||20260408074500|||||||||8901234567^Leblanc^Raymond A^^^^||||||20260408134500||LAB|F
OBX|1|NM|5902-2^PT^LN||18.5|s|11.0-13.5|H|||F
OBX|2|NM|6301-6^INR^LN||2.8||2.0-3.0|N|||F
NTE|1||Therapeutic range for mechanical valve. Patient on warfarin 5mg daily.
```

## 9. ORU^R01 - clinical document with embedded PDF report

```
MSH|^~\&|OSCAR|Default Facility|REPO|DOC_REPO|20260409150000||ORU^R01^ORU_R01|OSC00009|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||9012345678^^^ON_HCN^JHN||Charbonneau^Nathalie^Louise^^Mme||19820504|F|||100 Wellington St^^Barrie^ON^L4M 3A3^CA||^^PH^7055559012
OBR|1|ORD009^OSCAR|DOC009^DOC_REPO|CONSULT^Consultation Report^LN|||20260409120000|||||||||9012345678^Charbonneau^Nathalie L^^^^||||||20260409150000||DOC|F
OBX|1|ED|PDF^Consultation Report PDF^LN||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq||||||F
NTE|1||Cardiology consultation report for Dr. Gauthier re: atrial fibrillation management.
```

## 10. ORU^R01 - electrolyte panel

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260410091500||ORU^R01^ORU_R01|OSC00010|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||0123456789^^^ON_HCN^JHN||Ouellet^Pierre^Jean^^Mr||19780922|M|||85 Albert St^^Waterloo^ON^N2L 3S1^CA||^^PH^5195550123
OBR|1|ORD010^OSCAR|SPE010^LIFELABS|ELEC^Electrolyte Panel^LN|||20260410074500|||||||||0123456789^Ouellet^Pierre J^^^^||||||20260410091500||LAB|F
OBX|1|NM|2951-2^Sodium^LN||128|mmol/L|136-145|LL|||F
OBX|2|NM|2823-3^Potassium^LN||5.6|mmol/L|3.5-5.1|H|||F
OBX|3|NM|2075-0^Chloride^LN||96|mmol/L|98-106|L|||F
OBX|4|NM|1963-8^Bicarbonate^LN||20|mmol/L|22-29|L|||F
NTE|1||Critical: Sodium 128 mmol/L. Physician notified at 0920.
```

## 11. ORU^R01 - renal function with eGFR

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260411113000||ORU^R01^ORU_R01|OSC00011|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||1122334455^^^ON_HCN^JHN||Ahmed^Fatima^Zahra^^Ms||19650713|F|||412 Dundas St W^^Toronto^ON^M5T 1G9^CA||^^PH^4165551122
OBR|1|ORD011^OSCAR|SPE011^GAMMA_DYNACARE|RENAL^Renal Function Panel^LN|||20260411081000|||||||||1122334455^Ahmed^Fatima Z^^^^||||||20260411113000||LAB|F
OBX|1|NM|2160-0^Creatinine^LN||182|umol/L|50-98|HH|||F
OBX|2|NM|48642-3^eGFR^LN||28|mL/min/1.73m2|>60|LL|||F
OBX|3|NM|3094-0^Urea^LN||18.5|mmol/L|2.1-8.5|HH|||F
NTE|1||eGFR 28 mL/min indicates Stage 4 CKD. Nephrology referral recommended.
```

## 12. ORU^R01 - Pap smear cytology result

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260412140000||ORU^R01^ORU_R01|OSC00012|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||2233445566^^^ON_HCN^JHN||Leclerc^Genevieve^Madeleine^^Mme||19850301|F|||90 Elgin St^^Ottawa^ON^K1P 5K1^CA||^^PH^6135552233
OBR|1|ORD012^OSCAR|SPE012^CML_HEALTHCARE|PAP^Papanicolaou Smear^LN|||20260412093000|||||||||2233445566^Leclerc^Genevieve M^^^^||||||20260412140000||CYT|F
OBX|1|ST|19762-4^General Categorization^LN||Epithelial Cell Abnormality||||||F
OBX|2|ST|19764-0^Statement of Adequacy^LN||Satisfactory for evaluation||||||F
OBX|3|FT|19765-7^Interpretation^LN||Low-grade squamous intraepithelial lesion (LSIL). HPV testing recommended.||||||F
```

## 13. ORU^R01 - PSA result with clinical notes

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260413100000||ORU^R01^ORU_R01|OSC00013|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||3344556677^^^ON_HCN^JHN||Martineau^Denis^Claude^^Mr||19560218|M|||340 Riverside Dr^^Windsor^ON^N9A 5K3^CA||^^PH^5195553344
OBR|1|ORD013^OSCAR|SPE013^LIFELABS|PSA^Prostate Specific Antigen^LN|||20260413074500|||||||||3344556677^Martineau^Denis C^^^^||||||20260413100000||LAB|F
OBX|1|NM|2857-1^PSA^LN||6.2|ug/L|0.0-4.0|H|||F
OBX|2|NM|10886-0^Free PSA^LN||0.9|ug/L||||F
OBX|3|NM|12841-3^Free/Total PSA Ratio^LN||0.15||>0.25|L|||F
NTE|1||PSA elevated. Free/Total ratio 15% suggests further investigation. Urology referral advised.
```

## 14. ORU^R01 - ECG report with embedded TIFF image

```
MSH|^~\&|OSCAR|Default Facility|REPO|DOC_REPO|20260414153000||ORU^R01^ORU_R01|OSC00014|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||4455667788^^^ON_HCN^JHN||Renaud^Sylvain^Michel^^Mr||19711105|M|||22 Front St^^Belleville^ON^K8N 2Y8^CA||^^PH^6135554455
OBR|1|ORD014^OSCAR|DOC014^DOC_REPO|ECG^Electrocardiogram^LN|||20260414100000|||||||||4455667788^Renaud^Sylvain M^^^^||||||20260414153000||CARD|F
OBX|1|FT|8601-7^ECG Interpretation^LN||Normal sinus rhythm. Rate 72 bpm. Normal axis. No ST changes. No Q waves. Normal intervals.||||||F
OBX|2|ED|IMG^ECG Tracing^LN||^IM^TIFF^Base64^SUkqAAgAAAAIAAABAwABAAAAoAYAAAEBAwABAAAAIAQAAAIBAwABAAAAAQAAAAMBAwABAAAABQAAAAYBAwABAAAAAQAAABEBBAABAAAACAAAABIBAwABAAAAAQAAABoBBQABAAAAcgAAABsBBQABAAAA||||||F
NTE|1||12-lead ECG performed. Compared to previous ECG from 20250901, no significant interval change.
```

## 15. ORU^R01 - vitamin D and B12 results

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260415091000||ORU^R01^ORU_R01|OSC00015|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||5566778899^^^ON_HCN^JHN||Wong^Mei-Lin^^^Ms||19830520|F|||150 Bloor St E^^Toronto^ON^M4W 1B8^CA||^^PH^4165555566
OBR|1|ORD015^OSCAR|SPE015^LIFELABS|VIT^Vitamin Panel^LN|||20260415074500|||||||||5566778899^Wong^Mei-Lin^^^^||||||20260415091000||LAB|F
OBX|1|NM|1989-3^Vitamin D 25-Hydroxy^LN||38|nmol/L|75-250|L|||F
OBX|2|NM|2132-9^Vitamin B12^LN||145|pmol/L|138-652|N|||F
NTE|1||Vitamin D insufficient. Consider supplementation 1000 IU daily.
```

## 16. ORU^R01 - iron studies with ferritin

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260416110000||ORU^R01^ORU_R01|OSC00016|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||6677889900^^^ON_HCN^JHN||Fortin^Isabelle^Claire^^Mme||19920808|F|||75 Brant St^^Burlington^ON^L7R 2H2^CA||^^PH^9055556677
OBR|1|ORD016^OSCAR|SPE016^GAMMA_DYNACARE|IRON^Iron Studies^LN|||20260416081000|||||||||6677889900^Fortin^Isabelle C^^^^||||||20260416110000||LAB|F
OBX|1|NM|2498-4^Iron^LN||6|umol/L|9-30|L|||F
OBX|2|NM|2502-3^Transferrin Saturation^LN||0.08|fraction|0.20-0.50|L|||F
OBX|3|NM|2276-4^Ferritin^LN||8|ug/L|12-150|L|||F
OBX|4|NM|2500-7^TIBC^LN||78|umol/L|45-72|H|||F
NTE|1||Iron deficiency anemia pattern. Consider GI evaluation if no obvious source.
```

## 17. ORU^R01 - cervical spine xray report with embedded PNG

```
MSH|^~\&|OSCAR|Default Facility|REPO|DOC_REPO|20260417140000||ORU^R01^ORU_R01|OSC00017|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||7788990011^^^ON_HCN^JHN||Caron^Michel^Andre^^Mr||19681220|M|||45 York St^^Hamilton^ON^L8R 3K2^CA||^^PH^9055557788
OBR|1|ORD017^OSCAR|DOC017^DOC_REPO|XSPINE^Cervical Spine Xray^LN|||20260417110000|||||||||7788990011^Caron^Michel A^^^^||||||20260417140000||RAD|F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||AP and lateral views of the cervical spine. Loss of normal lordosis. Degenerative disc disease at C5-C6 and C6-C7. No fracture or subluxation. Prevertebral soft tissues normal.||||||F
OBX|2|ED|IMG^Cervical Spine Image^LN||^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==||||||F
```

## 18. ORU^R01 - glucose tolerance test

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260418143000||ORU^R01^ORU_R01|OSC00018|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||8899001122^^^ON_HCN^JHN||Plante^Marie-Eve^^^Mme||19870215|F|||225 Laurier Blvd^^Gatineau^QC^J8X 3W8^CA||^^PH^8195558899
OBR|1|ORD018^OSCAR|SPE018^LIFELABS|GTT^Glucose Tolerance Test^LN|||20260418075000|||||||||8899001122^Plante^Marie-Eve^^^^||||||20260418143000||LAB|F
OBX|1|NM|1558-6^Glucose Fasting^LN||5.8|mmol/L|3.3-5.5|H|||F
OBX|2|NM|1518-0^Glucose 1h^LN||11.2|mmol/L|<10.0|H|||F
OBX|3|NM|1530-5^Glucose 2h^LN||8.9|mmol/L|<7.8|H|||F
NTE|1||Results consistent with gestational diabetes mellitus. Refer to diabetes education program.
```

## 19. ORU^R01 - allergy testing IgE panel

```
MSH|^~\&|OSCAR|Default Facility|OLIS|ONTARIO_HIS|20260419101500||ORU^R01^ORU_R01|OSC00019|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||9900112233^^^ON_HCN^JHN||Simard^Etienne^Paul^^Mr||20120901|M|||60 Parkdale Ave^^Ottawa^ON^K1Y 1E5^CA||^^PH^6135559900
OBR|1|ORD019^OSCAR|SPE019^GAMMA_DYNACARE|IGE^Allergen Specific IgE Panel^LN|||20260419083000|||||||||9900112233^Simard^Etienne P^^^^||||||20260419101500||LAB|F
OBX|1|NM|19113-0^Total IgE^LN||285|kU/L|0-100|H|||F
OBX|2|NM|6844-5^Cat Dander IgE^LN||18.5|kU/L|<0.35|H|||F
OBX|3|NM|6158-0^Dust Mite IgE^LN||12.3|kU/L|<0.35|H|||F
OBX|4|NM|6206-7^Peanut IgE^LN||0.08|kU/L|<0.35|N|||F
OBX|5|NM|6248-9^Timothy Grass IgE^LN||22.1|kU/L|<0.35|H|||F
NTE|1||Significant sensitization to cat dander, dust mite, and timothy grass. Peanut negative. Refer to allergist.
```

## 20. ORU^R01 - referral letter with embedded PDF and NTE base64 data

```
MSH|^~\&|OSCAR|Default Facility|REPO|DOC_REPO|20260420160000||ORU^R01^ORU_R01|OSC00020|P|2.6
SFT|OSCAR McMaster|19.12||OSCAR EMR||20260101
PID|||0011223344^^^ON_HCN^JHN||Hebert^Andre^Joseph^^Mr||19580415|M|||8 Rideau Canal Dr^^Ottawa^ON^K1S 5B6^CA||^^PH^6135550011
OBR|1|ORD020^OSCAR|DOC020^DOC_REPO|REF^Referral Letter^LN|||20260420130000|||||||||0011223344^Hebert^Andre J^^^^||||||20260420160000||DOC|F
OBX|1|FT|11488-4^Consultation Note^LN||Dear Dr. Morin: I am referring Mr. Hebert for assessment of progressive dyspnea on exertion and bilateral lower extremity edema. Echo suggested EF 35%. Please see attached report.||||||F
OBX|2|ED|PDF^Referral Letter PDF^LN||^AP^^Base64^JVBERi0xLjUKJdDUxdgKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIKPj4KZW5kb2Jq||||||F
NTE|1||Referral to cardiology, Dr. Morin, Ottawa Heart Institute. Urgent.
```
