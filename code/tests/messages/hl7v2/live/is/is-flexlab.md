# FlexLab (Inpeco/Siemens) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Incoming lab order (CBC)

```
MSH|^~\&|SAGA|LANDSPITALI|FLEXLAB|RANNSOKN_LSH|20250312091500||ORM^O01|MSG00001|P|2.5
PID|1||1203761845^^^LSH^KT||Hreinsson^Stefán^Vilberg^^Hr.||19760312|M|||Hjarðarhagi 22^^Reykjavík^^107^IS||+3545551278
PV1|1|O|DEILD4A^^^LSH||||12345^Pálmadóttir^Ragna^Þorbjörg|||||||||||V00098732|||||||||||||||||||||||||20250312090000
ORC|NW|ORD20250312001|||||^^^20250312091500^^R||20250312091500|12345^Pálmadóttir^Ragna^Þorbjörg
OBR|1|ORD20250312001||58410-2^CBC panel - Blood by Automated count^LN|||20250312091000||||A|||||12345^Pálmadóttir^Ragna^Þorbjörg||||||||||^Blood
```

---

## 2. ORM^O01 - Incoming lab order (metabolic panel)

```
MSH|^~\&|SAGA|LANDSPITALI|FLEXLAB|RANNSOKN_LSH|20250312093000||ORM^O01|MSG00002|P|2.5
PID|1||0905831290^^^LSH^KT||Sturludóttir^Guðríður^Sólrún^^Frú||19830509|F|||Furugrund 8^^Kópavogur^^200^IS||+3545542391
PV1|1|I|DEILD6B^^^LSH||||23456^Vigfússon^Bjarni^Hörður|||||||||||V00098801|||||||||||||||||||||||||20250312080000
ORC|NW|ORD20250312002|||||^^^20250312093000^^R||20250312093000|23456^Vigfússon^Bjarni^Hörður
OBR|1|ORD20250312002||24323-8^Comprehensive metabolic 2000 panel - Serum or Plasma^LN|||20250312092000||||A|||||23456^Vigfússon^Bjarni^Hörður||||||||||^Serum
```

---

## 3. ORU^R01 - CBC result

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250312103000||ORU^R01|MSG00003|P|2.5
PID|1||1203761845^^^LSH^KT||Hreinsson^Stefán^Vilberg^^Hr.||19760312|M|||Hjarðarhagi 22^^Reykjavík^^107^IS||+3545551278
PV1|1|O|DEILD4A^^^LSH||||12345^Pálmadóttir^Ragna^Þorbjörg
ORC|RE|ORD20250312001||CM
OBR|1|ORD20250312001||58410-2^CBC panel - Blood by Automated count^LN|||20250312091000|||||||||||||||20250312103000|||F
OBX|1|NM|26464-8^Leukocytes [#/volume] in Blood by Automated count^LN||7.2|10*9/L|4.0-11.0|N|||F
OBX|2|NM|26453-1^Erythrocytes [#/volume] in Blood by Automated count^LN||4.85|10*12/L|4.5-5.5|N|||F
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||145|g/L|130-170|N|||F
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood by Automated count^LN||0.43|L/L|0.39-0.50|N|||F
OBX|5|NM|787-2^MCV [Entitic volume] by Automated count^LN||89|fL|80-100|N|||F
OBX|6|NM|785-6^MCH [Entitic mass] by Automated count^LN||30.0|pg|27-33|N|||F
OBX|7|NM|786-4^MCHC [Mass/volume] by Automated count^LN||337|g/L|320-360|N|||F
OBX|8|NM|26515-7^Platelets [#/volume] in Blood by Automated count^LN||245|10*9/L|150-400|N|||F
```

---

## 4. ORU^R01 - Comprehensive metabolic panel

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250312120000||ORU^R01|MSG00004|P|2.5
PID|1||0905831290^^^LSH^KT||Sturludóttir^Guðríður^Sólrún^^Frú||19830509|F|||Furugrund 8^^Kópavogur^^200^IS||+3545542391
PV1|1|I|DEILD6B^^^LSH||||23456^Vigfússon^Bjarni^Hörður
ORC|RE|ORD20250312002||CM
OBR|1|ORD20250312002||24323-8^Comprehensive metabolic 2000 panel - Serum or Plasma^LN|||20250312092000|||||||||||||||20250312120000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||5.4|mmol/L|3.9-6.1|N|||F
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||5.8|mmol/L|2.5-7.1|N|||F
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||72|umol/L|53-97|N|||F
OBX|4|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||2.35|mmol/L|2.15-2.55|N|||F
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||140|mmol/L|136-145|N|||F
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L|3.5-5.1|N|||F
OBX|7|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||103|mmol/L|98-107|N|||F
OBX|8|NM|2028-9^Carbon dioxide, total [Moles/volume] in Serum or Plasma^LN||24|mmol/L|22-29|N|||F
OBX|9|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||42|g/L|35-50|N|||F
OBX|10|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||12|umol/L|5-21|N|||F
OBX|11|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||68|U/L|40-129|N|||F
OBX|12|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||22|U/L|7-56|N|||F
OBX|13|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||25|U/L|10-40|N|||F
```

---

## 5. ORU^R01 - Lipid panel

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250313080000||ORU^R01|MSG00005|P|2.5
PID|1||2811551078^^^LSH^KT||Bergmann^Páll^Eyvindur^^Hr.||19551128|M|||Skipholt 41^^Reykjavík^^105^IS||+3545553487
PV1|1|O|DEILD2C^^^LSH||||34567^Þorsteinsdóttir^Hildur^Brá
ORC|RE|ORD20250313001||CM
OBR|1|ORD20250313001||24331-1^Lipid panel - Serum or Plasma^LN|||20250313073000|||||||||||||||20250313080000|||F
OBX|1|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||5.8|mmol/L|<5.2|H|||F
OBX|2|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN||1.6|mmol/L|<1.7|N|||F
OBX|3|NM|2085-9^Cholesterol in HDL [Mass/volume] in Serum or Plasma^LN||1.4|mmol/L|>1.0|N|||F
OBX|4|NM|13457-7^Cholesterol in LDL [Mass/volume] in Serum or Plasma^LN||3.7|mmol/L|<3.4|H|||F
OBX|5|NM|13458-5^Cholesterol in VLDL [Mass/volume] in Serum or Plasma^LN||0.7|mmol/L|0.1-1.0|N|||F
```

---

## 6. ORU^R01 - Thyroid function

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250313094500||ORU^R01|MSG00006|P|2.5
PID|1||1706891523^^^LSH^KT||Hauksdóttir^Þórdís^Rán^^Frú||19890617|F|||Sólvallagata 12^^Selfoss^^800^IS||+3544825612
PV1|1|O|DEILD3A^^^LSH||||45678^Bergsson^Stefán^Hjörtur
ORC|RE|ORD20250313002||CM
OBR|1|ORD20250313002||80439-8^Thyroid function panel - Serum or Plasma^LN|||20250313090000|||||||||||||||20250313094500|||F
OBX|1|NM|3016-3^Thyrotropin [Units/volume] in Serum or Plasma^LN||2.1|mIU/L|0.4-4.0|N|||F
OBX|2|NM|3026-2^Thyroxine (T4) free [Mass/volume] in Serum or Plasma^LN||15.2|pmol/L|12.0-22.0|N|||F
OBX|3|NM|3053-6^Triiodothyronine (T3) free [Mass/volume] in Serum or Plasma^LN||4.8|pmol/L|3.1-6.8|N|||F
```

---

## 7. ORU^R01 - Liver function

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250313110000||ORU^R01|MSG00007|P|2.5
PID|1||0402720934^^^LSH^KT||Eggertsson^Bjarki^Heimir^^Hr.||19720204|M|||Lyngheiði 7^^Akureyri^^600^IS||+3544625683
PV1|1|I|DEILD5A^^^LSH||||56789^Reynisdóttir^Sigríður^Þórgunnur
ORC|RE|ORD20250313003||CM
OBR|1|ORD20250313003||24325-3^Hepatic function panel - Serum or Plasma^LN|||20250313100000|||||||||||||||20250313110000|||F
OBX|1|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||85|U/L|7-56|H|||F
OBX|2|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||92|U/L|10-40|H|||F
OBX|3|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||110|U/L|40-129|N|||F
OBX|4|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||28|umol/L|5-21|H|||F
OBX|5|NM|1968-7^Bilirubin.direct [Mass/volume] in Serum or Plasma^LN||10|umol/L|0-5|H|||F
OBX|6|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||34|g/L|35-50|L|||F
OBX|7|NM|2532-0^Lactate dehydrogenase [Enzymatic activity/volume] in Serum or Plasma^LN||198|U/L|120-246|N|||F
OBX|8|NM|2336-6^Gamma glutamyl transferase [Enzymatic activity/volume] in Serum or Plasma^LN||78|U/L|8-61|H|||F
```

---

## 8. ORU^R01 - Coagulation (PT/INR)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250314081500||ORU^R01|MSG00008|P|2.5
PID|1||2209680412^^^LSH^KT||Friðriksson^Ólafur^Brandur^^Hr.||19680922|M|||Norðurgata 14^^Hafnarfjörður^^220^IS||+3545656712
PV1|1|I|DEILD7C^^^LSH||||67890^Sturludóttir^Kristbjörg^Áslaug
ORC|RE|ORD20250314001||CM
OBR|1|ORD20250314001||5902-2^Prothrombin time (PT)^LN|||20250314080000|||||||||||||||20250314081500|||F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||13.2|s|11.0-13.5|N|||F
OBX|2|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||1.1||0.8-1.2|N|||F
OBX|3|NM|3173-2^aPTT in Blood by Coagulation assay^LN||29|s|25-35|N|||F
OBX|4|NM|3255-7^Fibrinogen [Mass/volume] in Platelet poor plasma by Coagulation assay^LN||3.2|g/L|2.0-4.0|N|||F
```

---

## 9. ORU^R01 - Urinalysis

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250314100000||ORU^R01|MSG00009|P|2.5
PID|1||1501940267^^^LSH^KT||Aðalbjarnardóttir^Hildur^Eik^^Frú||19940115|F|||Kirkjubraut 22^^Akranes^^300^IS||+3544315678
PV1|1|O|DEILD2A^^^LSH||||78901^Hjálmarsson^Jón^Ragnar
ORC|RE|ORD20250314002||CM
OBR|1|ORD20250314002||24356-8^Urinalysis complete panel - Urine^LN|||20250314093000|||||||||||||||20250314100000|||F
OBX|1|NM|5811-5^Specific gravity of Urine by Test strip^LN||1.018||1.005-1.030|N|||F
OBX|2|NM|2756-5^pH of Urine by Test strip^LN||6.0||5.0-8.0|N|||F
OBX|3|CE|20405-7^Urobilinogen [Mass/volume] in Urine by Test strip^LN||Normal||Normal|N|||F
OBX|4|CE|5770-3^Bilirubin.total [Presence] in Urine by Test strip^LN||Negative||Negative|N|||F
OBX|5|CE|2349-9^Glucose [Presence] in Urine by Test strip^LN||Negative||Negative|N|||F
OBX|6|CE|5804-0^Protein [Presence] in Urine by Test strip^LN||Trace||Negative|A|||F
OBX|7|CE|20408-1^Nitrite [Presence] in Urine by Test strip^LN||Negative||Negative|N|||F
OBX|8|NM|5821-4^Leukocytes [#/area] in Urine sediment by Microscopy high power field^LN||3|/HPF|0-5|N|||F
OBX|9|NM|13945-1^Erythrocytes [#/area] in Urine sediment by Microscopy high power field^LN||1|/HPF|0-3|N|||F
```

---

## 10. ORU^R01 - HbA1c result

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250314113000||ORU^R01|MSG00010|P|2.5
PID|1||1108770689^^^LSH^KT||Snorrason^Gunnar^Tjörvi^^Hr.||19770811|M|||Lyngás 9^^Garðabær^^210^IS||+3545568912
PV1|1|O|DEILD3B^^^LSH||||89012^Bjarnadóttir^Ingibjörg^Ósk
ORC|RE|ORD20250314003||CM
OBR|1|ORD20250314003||4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20250314110000|||||||||||||||20250314113000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||7.2|%|<7.0|H|||F
OBX|2|NM|59261-8^Hemoglobin A1c/Hemoglobin.total in Blood by IFCC protocol^LN||55|mmol/mol|<53|H|||F
```

---

## 11. ORU^R01 - Blood culture (microbiology)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250315090000||ORU^R01|MSG00011|P|2.5
PID|1||1904850156^^^LSH^KT||Tryggvason^Einar^Hákon^^Hr.||19850419|M|||Borgarbraut 32^^Borgarnes^^310^IS||+3544379012
PV1|1|I|GJORGAESLA^^^LSH||||90123^Þorvaldsdóttir^Ragnheiður^Lára
ORC|RE|ORD20250314010||CM
OBR|1|ORD20250314010||600-7^Bacteria identified in Blood by Culture^LN|||20250314160000|||||||||||||||20250315090000|||F
OBX|1|CE|600-7^Bacteria identified in Blood by Culture^LN||Staphylococcus aureus|||A|||F
OBX|2|CE|18769-0^Microbial susceptibility tests Set^LN||Oxacillin: Sensitive|||N|||F
OBX|3|CE|18769-0^Microbial susceptibility tests Set^LN||Vancomycin: Sensitive|||N|||F
OBX|4|CE|18769-0^Microbial susceptibility tests Set^LN||Clindamycin: Sensitive|||N|||F
OBX|5|CE|18769-0^Microbial susceptibility tests Set^LN||Trimethoprim-Sulfamethoxazole: Sensitive|||N|||F
OBX|6|ST|19994-3^Culture method^LN||BacT/ALERT FA Plus aerobic bottle, positive at 14 hours|||N|||F
```

---

## 12. ORU^R01 - Drug level (therapeutic drug monitoring)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250315103000||ORU^R01|MSG00012|P|2.5
PID|1||2507600823^^^LSH^KT||Hilmarsdóttir^Sigþrúður^Erla^^Frú||19600725|F|||Skarðshlíð 14^^Akureyri^^600^IS||+3544625231
PV1|1|I|DEILD8A^^^FSA||||01234^Þórólfsson^Hákon^Bergþór
ORC|RE|ORD20250315001||CM
OBR|1|ORD20250315001||4090-7^Vancomycin [Mass/volume] in Serum or Plasma^LN|||20250315100000|||||||||||||||20250315103000|||F
OBX|1|NM|4090-7^Vancomycin [Mass/volume] in Serum or Plasma^LN||14.5|mg/L|10.0-20.0|N|||F
OBX|2|ST|DOSE_INFO^Dose information^L||1000 mg IV q12h, trough drawn 30 min before 4th dose|||N|||F
```

---

## 13. ORU^R01 - Troponin result (critical)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250315142000||ORU^R01|MSG00013|P|2.5
PID|1||0103500478^^^LSH^KT||Markússon^Helgi^Brynjólfur^^Hr.||19500301|M|||Vesturgata 7^^Reykjanesbær^^230^IS||+3545427345
PV1|1|E|BRÁÐAMÓTTAKA^^^LSH||||12345^Pálmadóttir^Ragna^Þorbjörg
ORC|RE|ORD20250315005||CM
OBR|1|ORD20250315005||89579-7^Troponin I.cardiac [Mass/volume] in Serum or Plasma by High sensitivity method^LN|||20250315140000|||||||||||||||20250315142000|||F
OBX|1|NM|89579-7^Troponin I.cardiac [Mass/volume] in Serum or Plasma by High sensitivity method^LN||285|ng/L|<26|HH|||F
OBX|2|ST|CRIT_NOTE^Critical value notification^L||Critical value called to Dr. Pálmadóttir at 14:20 on 2025-03-15|||N|||F
```

---

## 14. ORU^R01 - Blood typing result

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250316080000||ORU^R01|MSG00014|P|2.5
PID|1||1108920345^^^LSH^KT||Sigfúsdóttir^Margrét^Halla^^Frú||19920811|F|||Strandgata 18^^Hafnarfjörður^^220^IS||+3545657134
PV1|1|I|DEILD9B^^^LSH||||23456^Vigfússon^Bjarni^Hörður
ORC|RE|ORD20250316001||CM
OBR|1|ORD20250316001||882-1^ABO and Rh group [Type] in Blood^LN|||20250316073000|||||||||||||||20250316080000|||F
OBX|1|CE|882-1^ABO and Rh group [Type] in Blood^LN||A Positive|||N|||F
OBX|2|CE|883-9^ABO group [Type] in Blood^LN||A|||N|||F
OBX|3|CE|10331-7^Rh [Type] in Blood^LN||Positive|||N|||F
OBX|4|CE|1018-1^Direct antiglobulin test.IgG specific reagent [Interpretation] in Blood^LN||Negative|||N|||F
```

---

## 15. ORM^O01 - Incoming order (blood gas)

```
MSH|^~\&|SAGA|LANDSPITALI|FLEXLAB|RANNSOKN_LSH|20250316091000||ORM^O01|MSG00015|P|2.5
PID|1||0606780190^^^LSH^KT||Þorláksson^Eiríkur^Hjalti^^Hr.||19780606|M|||Engjavellir 9^^Hafnarfjörður^^220^IS||+3545652456
PV1|1|E|BRÁÐAMÓTTAKA^^^LSH||||34567^Þorsteinsdóttir^Hildur^Brá
ORC|NW|ORD20250316002|||||^^^20250316091000^^S||20250316091000|34567^Þorsteinsdóttir^Hildur^Brá
OBR|1|ORD20250316002||24336-0^Gas panel - Arterial blood^LN|||20250316090500||||A|||||34567^Þorsteinsdóttir^Hildur^Brá||||||||||^Arterial blood
```

---

## 16. ORU^R01 - Blood gas result

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250316093000||ORU^R01|MSG00016|P|2.5
PID|1||0606780190^^^LSH^KT||Þorláksson^Eiríkur^Hjalti^^Hr.||19780606|M|||Engjavellir 9^^Hafnarfjörður^^220^IS||+3545652456
PV1|1|E|BRÁÐAMÓTTAKA^^^LSH||||34567^Þorsteinsdóttir^Hildur^Brá
ORC|RE|ORD20250316002||CM
OBR|1|ORD20250316002||24336-0^Gas panel - Arterial blood^LN|||20250316090500|||||||||||||||20250316093000|||F
OBX|1|NM|2744-1^pH of Arterial blood^LN||7.38||7.35-7.45|N|||F
OBX|2|NM|2019-8^Carbon dioxide [Partial pressure] in Arterial blood^LN||5.1|kPa|4.7-6.0|N|||F
OBX|3|NM|2703-7^Oxygen [Partial pressure] in Arterial blood^LN||11.2|kPa|10.0-13.3|N|||F
OBX|4|NM|1959-6^Bicarbonate [Moles/volume] in Arterial blood^LN||23|mmol/L|22-26|N|||F
OBX|5|NM|2708-6^Oxygen saturation in Arterial blood^LN||96|%|95-99|N|||F
OBX|6|NM|1925-7^Base excess in Arterial blood by calculation^LN||-1.2|mmol/L|-2.0-2.0|N|||F
OBX|7|NM|2532-0^Lactate [Mass/volume] in Arterial blood^LN||1.1|mmol/L|0.5-2.2|N|||F
```

---

## 17. ORU^R01 - Lab report with base64 ED OBX (PDF cumulative report)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|SAGA|LANDSPITALI|20250316150000||ORU^R01|MSG00017|P|2.5
PID|1||2811551078^^^LSH^KT||Bergmann^Páll^Eyvindur^^Hr.||19551128|M|||Skipholt 41^^Reykjavík^^105^IS||+3545553487
PV1|1|O|DEILD2C^^^LSH||||34567^Þorsteinsdóttir^Hildur^Brá
ORC|RE|ORD20250316010||CM
OBR|1|ORD20250316010||11502-2^Laboratory report.total^LN|||20250316140000|||||||||||||||20250316150000|||F
OBX|1|ED|PDF^Cumulative Lab Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEN1bXVsYXRpdmUgTGFiIFJlcG9ydCkgVGoKRVQKZW5kc3RyZWFt||||||F
```

---

## 18. ORU^R01 - Pathology result with base64 ED OBX (PDF)

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|HEKLA|LANDSPITALI|20250317100000||ORU^R01|MSG00018|P|2.5
PID|1||1302880756^^^LSH^KT||Indriðadóttir^Vigdís^Embla^^Frú||19880213|F|||Lyngholt 22^^Mosfellsbær^^270^IS||+3545664712
PV1|1|I|DEILD10A^^^LSH||||45678^Bergsson^Stefán^Hjörtur
ORC|RE|ORD20250317001||CM
OBR|1|ORD20250317001||11529-5^Surgical pathology study^LN|||20250314120000|||||||||||||||20250317100000|||F
OBX|1|CE|22637-3^Pathology report final diagnosis^LN||Benign fibroadenoma, left breast|||N|||F
OBX|2|ST|22636-5^Pathology report gross description^LN||Specimen: left breast core biopsy, two cores 1.2 cm and 0.9 cm|||N|||F
OBX|3|ST|22635-7^Pathology report microscopic observation^LN||Well-circumscribed fibroepithelial lesion with bland stromal and epithelial components, no atypia or mitotic activity identified|||N|||F
OBX|4|ED|PDF^Pathology Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFBhdGhvbG9neSBSZXBvcnQgLSBGaW5hbCkgVGoKRVQKZW5kc3RyZWFt||||||F
```

---

## 19. ADT^A04 - Lab patient registration

```
MSH|^~\&|SAGA|LANDSPITALI|FLEXLAB|RANNSOKN_LSH|20250317113000||ADT^A04|MSG00019|P|2.5
EVN|A04|20250317113000
PID|1||1007014312^^^LSH^KT||Hauksdóttir^Ólöf^Sigríður^^Frú||20010710|F|||Heiðmörk 25^^Reykjanesbær^^230^IS||+3545425789|||S
NK1|1|Hauksson^Magnús^Geir^^Hr.|FTH|Heiðmörk 25^^Reykjanesbær^^230^IS|+3545425792
PV1|1|O|DEILD1A^^^LSH||||56789^Reynisdóttir^Sigríður^Þórgunnur|||||||||||V00099001|||||||||||||||||||||||||20250317113000
PV2|||Blóðrannsókn (Blood work)
```

---

## 20. ORU^R01 - CSF analysis result

```
MSH|^~\&|FLEXLAB|RANNSOKN_LSH|CAMBIO_CIS|LANDSPITALI|20250318090000||ORU^R01|MSG00020|P|2.5
PID|1||2304740534^^^LSH^KT||Skúlason^Ragnar^Birkir^^Hr.||19740423|M|||Kjarnagata 40^^Akureyri^^600^IS||+3544626890
PV1|1|I|TAUGADEILD^^^LSH||||67890^Sturludóttir^Kristbjörg^Áslaug
ORC|RE|ORD20250318001||CM
OBR|1|ORD20250318001||49581-7^CSF panel^LN|||20250317200000|||||||||||||||20250318090000|||F
OBX|1|NM|26464-8^Leukocytes [#/volume] in Cerebral spinal fluid^LN||3|10*6/L|0-5|N|||F
OBX|2|NM|2345-7^Glucose [Mass/volume] in Cerebral spinal fluid^LN||3.4|mmol/L|2.2-3.9|N|||F
OBX|3|NM|2880-3^Protein [Mass/volume] in Cerebral spinal fluid^LN||0.35|g/L|0.15-0.45|N|||F
OBX|4|NM|26453-1^Erythrocytes [#/volume] in Cerebral spinal fluid^LN||0|10*6/L|0|N|||F
OBX|5|CE|20993-2^Appearance of Cerebral spinal fluid^LN||Clear|||N|||F
OBX|6|CE|29257-8^Color of Cerebral spinal fluid^LN||Colorless|||N|||F
OBX|7|ST|600-7^Bacteria identified in Cerebral spinal fluid by Culture^LN||No growth at 48 hours|||N|||F
```
