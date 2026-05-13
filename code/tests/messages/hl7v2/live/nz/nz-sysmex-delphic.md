# Sysmex Delphic LIS - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Full blood count result with abnormal flags

```
MSH|^~\&|DELPHIC|AUCKLAND_LAB|MEDTECH32|DR_RAWIRI_SURGERY|20240315091200||ORU^R01^ORU_R01|MSG00001|P|2.4|||AL|NE||ASCII|||NZL
PID|1||XKR4827^^^NHI^NI||WHATUIRA^AROHA^WAIATA||19780514|F|||45 Jervois Road^^Auckland^^1011^NZ||^PRN^PH^^64^9^3768214||||||||||||||||N
PV1|1|O|||||DRJONES^Jonsson^Daniel^^^Dr|||||||||||V123456|||||||||||||||||||||||||20240314|||||||
ORC|RE||240315-0012||CM||||20240315091200|||DRJONES^Jonsson^Daniel^^^Dr
OBR|1||240315-0012|CBC^Full Blood Count^L|||20240314153000|||||||||DRJONES^Jonsson^Daniel^^^Dr||||||20240315091200|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood^LN||12.8|x10*9/L|4.0-11.0|H|||F|||20240315090000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.52|x10*12/L|3.80-5.80||||F|||20240315090000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||138|g/L|115-165||||F|||20240315090000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood^LN||0.41|L/L|0.36-0.46||||F|||20240315090000
OBX|5|NM|787-2^MCV [Entitic volume]^LN||91|fL|80-100||||F|||20240315090000
OBX|6|NM|777-3^Platelets [#/volume] in Blood^LN||245|x10*9/L|150-400||||F|||20240315090000
OBX|7|NM|770-8^Neutrophils [#/volume] in Blood^LN||9.2|x10*9/L|2.0-7.5|H|||F|||20240315090000
```

---

## 2. ORU^R01 - Lipid panel result

```
MSH|^~\&|DELPHIC_LIS|WAIKATO_PATH|MYINDICI|HAMILTON_MEDICAL|20240228143500||ORU^R01^ORU_R01|MSG00002|P|2.4|||AL|NE||ASCII|||NZL
PID|1||PMD6519^^^NHI^NI||TE PUNI^RAWIRI^MOANA||19650823|M|||38 Boundary Road^^Hamilton^^3204^NZ||^PRN^PH^^64^7^8384516||||||||||||||||N
PV1|1|O|||||DRBROWN^Brownlee^Saoirse^^^Dr|||||||||||V789012|||||||||||||||||||||||||20240227|||||||
ORC|RE||240228-0087||CM||||20240228143500|||DRBROWN^Brownlee^Saoirse^^^Dr
OBR|1||240228-0087|LIPID^Lipid Panel^L|||20240227100000|||||||||DRBROWN^Brownlee^Saoirse^^^Dr||||||20240228143500|||F
OBX|1|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||6.8|mmol/L|<5.0|H|||F|||20240228120000
OBX|2|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN||2.4|mmol/L|<1.7|H|||F|||20240228120000
OBX|3|NM|2085-9^HDL Cholesterol [Mass/volume] in Serum or Plasma^LN||1.1|mmol/L|>1.0||||F|||20240228120000
OBX|4|NM|13457-7^LDL Cholesterol [Mass/volume] in Serum or Plasma^LN||4.6|mmol/L|<3.0|H|||F|||20240228120000
OBX|5|NM|9830-1^Cholesterol.total/Cholesterol in HDL [Mass Ratio]^LN||6.2||<4.5|H|||F|||20240228120000
```

---

## 3. ORM^O01 - Laboratory test order for renal function

```
MSH|^~\&|MEDTECH32|DR_WILSON_CLINIC|DELPHIC|CANTERBURY_SCL|20240410080000||ORM^O01^ORM_O01|MSG00003|P|2.4|||AL|NE||ASCII|||NZL
PID|1||CFL9027^^^NHI^NI||MACKINTOSH^ISLA^CATRIONA||19520301|F|||52 Wharenui Road^^Christchurch^^8041^NZ||^PRN^PH^^64^3^3486319||||||||||||||||N
PV1|1|O|||||DRWILSON^Wilkinson^Margaret^^^Dr|||||||||||V345678|||||||||||||||||||||||||20240410|||||||
ORC|NW|ORD240410-001||||||20240410080000|||DRWILSON^Wilkinson^Margaret^^^Dr
OBR|1|ORD240410-001||RENAL^Renal Function^L|||20240410074500|||||||||DRWILSON^Wilkinson^Margaret^^^Dr|||||||||||||STAT
OBR|2|ORD240410-001||CBC^Full Blood Count^L|||20240410074500|||||||||DRWILSON^Wilkinson^Margaret^^^Dr
```

---

## 4. ORU^R01 - HbA1c diabetes monitoring result

```
MSH|^~\&|DELPHIC|SCL_CHRISTCHURCH|MEDTECH32|FENDALTON_MED|20240522101500||ORU^R01^ORU_R01|MSG00004|P|2.4|||AL|NE||ASCII|||NZL
PID|1||DSE3478^^^NHI^NI||HENARE^WIREMU^MAREKO||19700919|M|||74 Memorial Avenue^^Christchurch^^8023^NZ||^PRN^PH^^64^3^3669841||||||||||||||||N
PV1|1|O|||||DRPATEL^Pateliya^Rajeev^^^Dr|||||||||||V456789|||||||||||||||||||||||||20240521|||||||
ORC|RE||240522-0034||CM||||20240522101500|||DRPATEL^Pateliya^Rajeev^^^Dr
OBR|1||240522-0034|HBA1C^HbA1c^L|||20240521143000|||||||||DRPATEL^Pateliya^Rajeev^^^Dr||||||20240522101500|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||58|mmol/mol|<50|H|||F|||20240522090000
OBX|2|NM|17856-6^Hemoglobin A1c/Hemoglobin.total in Blood by HPLC^LN||7.5|%|<6.7|H|||F|||20240522090000
NTE|1||Target for most patients with diabetes: <53 mmol/mol
```

---

## 5. ORU^R01 - Thyroid function panel

```
MSH|^~\&|SYSMEX_DELPHIC|LABPLUS_ADHB|INDICI|NEWMARKET_MED|20240618155200||ORU^R01^ORU_R01|MSG00005|P|2.4|||AL|NE||ASCII|||NZL
PID|1||GHN5821^^^NHI^NI||COOPERSON^JESSICA^ANNABEL||19880212|F|||62 Victoria Avenue^^Auckland^^1050^NZ||^PRN^PH^^64^21^0987142||||||||||||||||N
PV1|1|O|||||DRLEE^Leeson^Michael^^^Dr|||||||||||V567890|||||||||||||||||||||||||20240617|||||||
ORC|RE||240618-0156||CM||||20240618155200|||DRLEE^Leeson^Michael^^^Dr
OBR|1||240618-0156|THYROID^Thyroid Function^L|||20240617090000|||||||||DRLEE^Leeson^Michael^^^Dr||||||20240618155200|||F
OBX|1|NM|3016-3^TSH [Units/volume] in Serum or Plasma^LN||8.7|mIU/L|0.4-4.0|H|||F|||20240618140000
OBX|2|NM|3026-2^Free T4 [Mass/volume] in Serum or Plasma^LN||9.2|pmol/L|10.0-20.0|L|||F|||20240618140000
OBX|3|NM|3051-0^Free T3 [Mass/volume] in Serum or Plasma^LN||3.8|pmol/L|3.5-6.5||||F|||20240618140000
NTE|1||Results consistent with primary hypothyroidism. Suggest clinical correlation.
```

---

## 6. ORU^R01 - Pathology report as embedded PDF

```
MSH|^~\&|DELPHIC|PATHLAB_WAIKATO|MEDTECH32|HILLCREST_MED|20240703112000||ORU^R01^ORU_R01|MSG00006|P|2.4|||AL|NE||ASCII|||NZL
PID|1||LRX2087^^^NZ^NHI||TAITUHA^BRENDAN^MARCUS||19451107|M|||52 Peachgrove Road^^Hamilton^^3216^NZ||^PRN^PH^^64^7^8562148||||||||||||||||N
PV1|1|O|||||DRSINGH^Singh^Amritpal^^^Dr|||||||||||V678901|||||||||||||||||||||||||20240702|||||||
ORC|RE||240703-0201||CM||||20240703112000|||DRSINGH^Singh^Amritpal^^^Dr
OBR|1||240703-0201|HISTOL^Histology Report^L|||20240628100000|||||||||DRSINGH^Singh^Amritpal^^^Dr||||||20240703112000|||F
OBX|1|ED|PDF^Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
NTE|1||Histology: Skin excision left forearm. Basal cell carcinoma, nodular type. Margins clear.
```

---

## 7. ORU^R01 - Liver function tests

```
MSH|^~\&|DELPHIC_LIS|SOUTHERN_PATH|MYINDICI|DUNEDIN_MED|20240815093000||ORU^R01^ORU_R01|MSG00007|P|2.4|||AL|NE||ASCII|||NZL
PID|1||PWQ8413^^^NHI^NI||ANDERSSEN^CRAIG^REUBEN||19830406|M|||84 King Edward Street^^Dunedin^^9012^NZ||^PRN^PH^^64^3^4773148||||||||||||||||N
PV1|1|O|||||DRMURPHY^Murcheson^Saoirse^^^Dr|||||||||||V789012|||||||||||||||||||||||||20240814|||||||
ORC|RE||240815-0045||CM||||20240815093000|||DRMURPHY^Murcheson^Saoirse^^^Dr
OBR|1||240815-0045|LFT^Liver Function Tests^L|||20240814080000|||||||||DRMURPHY^Murcheson^Saoirse^^^Dr||||||20240815093000|||F
OBX|1|NM|1742-6^ALT [Enzymatic activity/volume] in Serum or Plasma^LN||85|U/L|<45|H|||F|||20240815080000
OBX|2|NM|1920-8^AST [Enzymatic activity/volume] in Serum or Plasma^LN||62|U/L|<35|H|||F|||20240815080000
OBX|3|NM|6768-6^ALP [Enzymatic activity/volume] in Serum or Plasma^LN||98|U/L|30-120||||F|||20240815080000
OBX|4|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||22|umol/L|<20|H|||F|||20240815080000
OBX|5|NM|2885-2^Total Protein [Mass/volume] in Serum or Plasma^LN||72|g/L|60-80||||F|||20240815080000
OBX|6|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||38|g/L|35-50||||F|||20240815080000
OBX|7|NM|1968-7^GGT [Enzymatic activity/volume] in Serum or Plasma^LN||120|U/L|<60|H|||F|||20240815080000
```

---

## 8. ORM^O01 - Urgent order for troponin and D-dimer

```
MSH|^~\&|CONCERTO|WGTN_HOSPITAL_ED|DELPHIC|WELLINGTON_SCL|20240901221500||ORM^O01^ORM_O01|MSG00008|P|2.4|||AL|NE||ASCII|||NZL
PID|1||TBR1064^^^NHI^NI||RAUKAWA^TANE^JOSIAH||19580712|M|||74 Featherston Street^^Wellington^^6011^NZ||^PRN^PH^^64^4^4728912||||||||||||||||N
PV1|1|E|ED^BAY3^WGTN_HOSP||||DRCHENG^Cheng^Wei Ming^^^Dr|||||||||||V890123|||||||||||||||||||||||||20240901|||||||
ORC|NW|ORD240901-088||||||20240901221500|||DRCHENG^Cheng^Wei Ming^^^Dr
OBR|1|ORD240901-088||TROP^Troponin I^L|||20240901221000|||||||||DRCHENG^Cheng^Wei Ming^^^Dr|||||||||||||STAT
OBR|2|ORD240901-088||DDIMER^D-Dimer^L|||20240901221000|||||||||DRCHENG^Cheng^Wei Ming^^^Dr|||||||||||||STAT
OBR|3|ORD240901-088||CBC^Full Blood Count^L|||20240901221000|||||||||DRCHENG^Cheng^Wei Ming^^^Dr|||||||||||||STAT
```

---

## 9. ORU^R01 - Microbiology culture and sensitivity

```
MSH|^~\&|DELPHIC|MEDLAB_CENTRAL|MEDTECH32|PALMERSTON_NORTH_MED|20240420161000||ORU^R01^ORU_R01|MSG00009|P|2.4|||AL|NE||ASCII|||NZL
PID|1||SBR8159^^^NHI^NI||KINGSLEY^SAMANTHA^LEAH||19920815|F|||27 Russell Street^^Palmerston North^^4410^NZ||^PRN^PH^^64^6^3548217||||||||||||||||N
PV1|1|O|||||DRROBINSON^Roberts^Padraig^^^Dr|||||||||||V901234|||||||||||||||||||||||||20240418|||||||
ORC|RE||240420-0078||CM||||20240420161000|||DRROBINSON^Roberts^Padraig^^^Dr
OBR|1||240420-0078|URINE_CS^Urine Culture and Sensitivity^L|||20240418090000|||||||||DRROBINSON^Roberts^Padraig^^^Dr||||||20240420161000|||F
OBX|1|ST|630-4^Bacteria identified in Urine by Culture^LN||Escherichia coli||||||F|||20240420140000
OBX|2|ST|18769-0^Microbial colony count [#/volume] in Urine^LN||>10*8 CFU/L||||||F|||20240420140000
OBX|3|ST|18906-8^Amoxicillin [Susceptibility]^LN||Resistant||||||F|||20240420140000
OBX|4|ST|18928-2^Trimethoprim [Susceptibility]^LN||Sensitive||||||F|||20240420140000
OBX|5|ST|18932-4^Nitrofurantoin [Susceptibility]^LN||Sensitive||||||F|||20240420140000
OBX|6|ST|18860-7^Ciprofloxacin [Susceptibility]^LN||Sensitive||||||F|||20240420140000
NTE|1||Significant growth of E. coli. Suggest trimethoprim or nitrofurantoin.
```

---

## 10. ORU^R01 - Coagulation studies (INR monitoring)

```
MSH|^~\&|SYSMEX_DELPHIC|LABTEST_TAURANGA|MEDTECH32|TAURANGA_DOCTORS|20240305140000||ORU^R01^ORU_R01|MSG00010|P|2.4|||AL|NE||ASCII|||NZL
PID|1||VKB6172^^^NHI^NI||MORRIGAN^ELIZABETH^ROSALIND||19400223|F|||83 Eleventh Avenue^^Tauranga^^3110^NZ||^PRN^PH^^64^7^5786152||||||||||||||||N
PV1|1|O|||||DRTHOMPSON^Thomsen^Bruce^^^Dr|||||||||||V012345|||||||||||||||||||||||||20240304|||||||
ORC|RE||240305-0112||CM||||20240305140000|||DRTHOMPSON^Thomsen^Bruce^^^Dr
OBR|1||240305-0112|COAG^Coagulation Studies^L|||20240304110000|||||||||DRTHOMPSON^Thomsen^Bruce^^^Dr||||||20240305140000|||F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||18.5|seconds|11.0-15.0|H|||F|||20240305120000
OBX|2|NM|6301-6^INR in Platelet poor plasma^LN||2.8||2.0-3.0||||F|||20240305120000
OBX|3|NM|3173-2^aPTT in Platelet poor plasma^LN||32|seconds|25-37||||F|||20240305120000
NTE|1||INR within therapeutic range for AF. Continue warfarin 4mg daily.
```

---

## 11. QBP^Q11 - Query for patient laboratory results

```
MSH|^~\&|MEDTECH32|TARANAKI_BASE|DELPHIC|PATHLAB_TARANAKI|20240511083000||QBP^Q11^QBP_Q11|MSG00011|P|2.4|||AL|NE||ASCII|||NZL
QPD|Q11^Query by Patient ID^HL7|QRY240511-001|YHQ4926^^^NHI^NI
RCP|I|10^RD
```

---

## 12. ORU^R01 - Electrolytes and renal function

```
MSH|^~\&|DELPHIC|SCL_NELSON|MEDTECH32|NELSON_FAMILY_MED|20240127102000||ORU^R01^ORU_R01|MSG00012|P|2.4|||AL|NE||ASCII|||NZL
PID|1||DJV5803^^^NHI^NI||MITCHELLSON^PETER^WILFRED||19750530|M|||62 Hampden Street^^Nelson^^7010^NZ||^PRN^PH^^64^3^5462178||||||||||||||||N
PV1|1|O|||||DRWHITE^Whittington^Jennifer^^^Dr|||||||||||V123789|||||||||||||||||||||||||20240126|||||||
ORC|RE||240127-0023||CM||||20240127102000|||DRWHITE^Whittington^Jennifer^^^Dr
OBR|1||240127-0023|ELEC^Electrolytes and Renal Function^L|||20240126140000|||||||||DRWHITE^Whittington^Jennifer^^^Dr||||||20240127102000|||F
OBX|1|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||141|mmol/L|135-145||||F|||20240127090000
OBX|2|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||5.6|mmol/L|3.5-5.2|H|||F|||20240127090000
OBX|3|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||104|mmol/L|95-110||||F|||20240127090000
OBX|4|NM|1963-8^Bicarbonate [Moles/volume] in Serum or Plasma^LN||24|mmol/L|22-30||||F|||20240127090000
OBX|5|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||145|umol/L|60-110|H|||F|||20240127090000
OBX|6|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||12.5|mmol/L|2.5-7.8|H|||F|||20240127090000
OBX|7|NM|33914-3^eGFR [Volume Rate/Area] in Serum or Plasma^LN||42|mL/min/1.73m2|>90|L|||F|||20240127090000
NTE|1||eGFR <60 suggests CKD stage 3. Recommend repeat in 3 months.
```

---

## 13. ORM^O01 - Pregnancy screening order (first trimester)

```
MSH|^~\&|MEDTECH32|MIDWIFE_PRACTICE|DELPHIC|AUCKLAND_LAB|20240208094500||ORM^O01^ORM_O01|MSG00013|P|2.4|||AL|NE||ASCII|||NZL
PID|1||KFA2647^^^NHI^NI||PARATA^MEREANA^WAIATA||19950320|F|||58 Sandringham Road^^Auckland^^1024^NZ||^PRN^PH^^64^22^0456128||||||||||||||||N
PV1|1|O|||||MWHALL^Halley^Christine^^^MW|||||||||||V234567|||||||||||||||||||||||||20240208|||||||
ORC|NW|ORD240208-055||||||20240208094500|||MWHALL^Halley^Christine^^^MW
OBR|1|ORD240208-055||ANTENATAL^First Trimester Antenatal Screen^L|||20240208090000|||||||||MWHALL^Halley^Christine^^^MW
OBR|2|ORD240208-055||CBC^Full Blood Count^L|||20240208090000|||||||||MWHALL^Halley^Christine^^^MW
OBR|3|ORD240208-055||BGROUPAB^Blood Group and Antibody Screen^L|||20240208090000|||||||||MWHALL^Halley^Christine^^^MW
OBR|4|ORD240208-055||RUBELLA^Rubella Immunity^L|||20240208090000|||||||||MWHALL^Halley^Christine^^^MW
```

---

## 14. ORU^R01 - Troponin result (critical value)

```
MSH|^~\&|DELPHIC|WGTN_SCL|CONCERTO|WGTN_HOSPITAL_ED|20240901234500||ORU^R01^ORU_R01|MSG00014|P|2.4|||AL|NE||ASCII|||NZL
PID|1||TBR1064^^^NHI^NI||RAUKAWA^TANE^JOSIAH||19580712|M|||74 Featherston Street^^Wellington^^6011^NZ||^PRN^PH^^64^4^4728912||||||||||||||||N
PV1|1|E|ED^BAY3^WGTN_HOSP||||DRCHENG^Cheng^Wei Ming^^^Dr|||||||||||V890123|||||||||||||||||||||||||20240901|||||||
ORC|RE||240901-0302||CM||||20240901234500|||DRCHENG^Cheng^Wei Ming^^^Dr
OBR|1||240901-0302|TROP^High Sensitivity Troponin I^L|||20240901221000|||||||||DRCHENG^Cheng^Wei Ming^^^Dr||||||20240901234500|||F
OBX|1|NM|49563-0^Troponin I.cardiac [Mass/volume] in Serum or Plasma by High sensitivity method^LN||2850|ng/L|<26|HH|||F|||20240901233000
NTE|1||CRITICAL VALUE - Phoned to Dr Cheng at 23:35. Result confirmed on repeat analysis.
```

---

## 15. ORU^R01 - Cytology report as embedded PDF

```
MSH|^~\&|DELPHIC_LIS|NORTHLAND_PATH|MEDTECH32|WHANGAREI_WOMENS|20240812141500||ORU^R01^ORU_R01|MSG00015|P|2.4|||AL|NE||ASCII|||NZL
PID|1||MSV3690^^^NHI^NI||JOHANSEN^HANNAH^MARGARETE||19870614|F|||52 Mill Road^^Whangarei^^0110^NZ||^PRN^PH^^64^9^4382194||||||||||||||||N
PV1|1|O|||||DRCARTER^Cartwright^Lisa^^^Dr|||||||||||V345012|||||||||||||||||||||||||20240808|||||||
ORC|RE||240812-0067||CM||||20240812141500|||DRCARTER^Cartwright^Lisa^^^Dr
OBR|1||240812-0067|CYTOL^Cervical Cytology Report^L|||20240808100000|||||||||DRCARTER^Cartwright^Lisa^^^Dr||||||20240812141500|||F
OBX|1|ED|PDF^Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
OBX|2|ST|19762-4^General categories [Interpretation] of Cervical or vaginal smear^LN||NILM - Negative for Intraepithelial Lesion or Malignancy||||||F|||20240812130000
NTE|1||Satisfactory for evaluation. No evidence of HPV effect. Recommend routine recall in 5 years per NCSP guidelines.
```

---

## 16. ORU^R01 - Iron studies

```
MSH|^~\&|SYSMEX_DELPHIC|HAWKES_BAY_PATH|MEDTECH32|HASTINGS_HEALTH|20240619103000||ORU^R01^ORU_R01|MSG00016|P|2.4|||AL|NE||ASCII|||NZL
PID|1||QSL7290^^^NHI^NI||CAMPBELLSON^FIONA^JANNE||19680411|F|||38 Avenue Road^^Hastings^^4122^NZ||^PRN^PH^^64^6^8761843||||||||||||||||N
PV1|1|O|||||DRADAMS^Adamson^Richard^^^Dr|||||||||||V456012|||||||||||||||||||||||||20240618|||||||
ORC|RE||240619-0091||CM||||20240619103000|||DRADAMS^Adamson^Richard^^^Dr
OBR|1||240619-0091|IRON^Iron Studies^L|||20240618083000|||||||||DRADAMS^Adamson^Richard^^^Dr||||||20240619103000|||F
OBX|1|NM|2498-4^Iron [Mass/volume] in Serum or Plasma^LN||5|umol/L|10-30|L|||F|||20240619090000
OBX|2|NM|2502-3^Transferrin [Mass/volume] in Serum or Plasma^LN||4.2|g/L|2.0-3.6|H|||F|||20240619090000
OBX|3|NM|2500-7^Transferrin saturation [Mass Fraction] in Serum or Plasma^LN||0.05||0.15-0.45|L|||F|||20240619090000
OBX|4|NM|2276-4^Ferritin [Mass/volume] in Serum or Plasma^LN||8|ug/L|20-300|L|||F|||20240619090000
NTE|1||Iron deficiency confirmed. Recommend assessment for cause and iron replacement.
```

---

## 17. ORL^O22 - Order acknowledgement from laboratory

```
MSH|^~\&|DELPHIC|CANTERBURY_SCL|MEDTECH32|DR_WILSON_CLINIC|20240410081500||ORL^O22^ORL_O22|MSG00017|P|2.4|||AL|NE||ASCII|||NZL
MSA|AA|MSG00003
PID|1||CFL9027^^^NHI^NI||MACKINTOSH^ISLA^CATRIONA||19520301|F|||52 Wharenui Road^^Christchurch^^8041^NZ||^PRN^PH^^64^3^3486319||||||||||||||||N
ORC|OK|ORD240410-001||240410-LAB-001||||20240410081500
OBR|1|ORD240410-001|240410-LAB-001|RENAL^Renal Function^L|||20240410074500
```

---

## 18. ORU^R01 - PSA result with clinical notes

```
MSH|^~\&|DELPHIC|LABPLUS_ADHB|MEDTECH32|EPSOM_MED_CENTRE|20240930085500||ORU^R01^ORU_R01|MSG00018|P|2.4|||AL|NE||ASCII|||NZL
PID|1||VPC4197^^^NHI^NI||TAYLORSON^GRAHAM^PEREGRINE||19560918|M|||74 Gillies Avenue^^Epsom^^1023^NZ||^PRN^PH^^64^9^6231547||||||||||||||||N
PV1|1|O|||||DRGREEN^Greenacre^Philip^^^Dr|||||||||||V567012|||||||||||||||||||||||||20240929|||||||
ORC|RE||240930-0018||CM||||20240930085500|||DRGREEN^Greenacre^Philip^^^Dr
OBR|1||240930-0018|PSA^Prostate Specific Antigen^L|||20240929100000|||||||||DRGREEN^Greenacre^Philip^^^Dr||||||20240930085500|||F
OBX|1|NM|2857-1^PSA [Mass/volume] in Serum or Plasma^LN||6.8|ug/L|<4.0|H|||F|||20240930080000
OBX|2|NM|10886-0^Free PSA/PSA.total in Serum or Plasma^LN||0.12||>0.25|L|||F|||20240930080000
NTE|1||PSA elevated with low free/total ratio. Recommend urology referral for further assessment.
```

---

## 19. ORU^R01 - Blood group and antibody screen

```
MSH|^~\&|DELPHIC_LIS|NZBS_AUCKLAND|CONCERTO|MIDDLEMORE_HOSP|20240714160000||ORU^R01^ORU_R01|MSG00019|P|2.4|||AL|NE||ASCII|||NZL
PID|1||WGM5821^^^NHI^NI||RAPATA^AROHA^WIKITORIA||19910203|F|||128 Bairds Road^^Manukau^^2104^NZ||^PRN^PH^^64^21^0234128||||||||||||||||N
PV1|1|I|WARD5^BED12^MIDDLEMORE||||DRNGUYEN^Nguyen^Thuy^^^Dr|||||||||||V678012|||||||||||||||||||||||||20240714|||||||
ORC|RE||240714-0189||CM||||20240714160000|||DRNGUYEN^Nguyen^Thuy^^^Dr
OBR|1||240714-0189|BGROUPAB^Blood Group and Antibody Screen^L|||20240714080000|||||||||DRNGUYEN^Nguyen^Thuy^^^Dr||||||20240714160000|||F
OBX|1|ST|882-1^ABO group [Type] in Blood^LN||O||||||F|||20240714140000
OBX|2|ST|10331-7^Rh [Type] in Blood^LN||Positive||||||F|||20240714140000
OBX|3|ST|890-4^Blood group antibody screen [Presence] in Serum or Plasma^LN||Negative||||||F|||20240714140000
```

---

## 20. QBP^Q11 - Query for outstanding orders by provider

```
MSH|^~\&|INDICI|KAPITI_HEALTH|DELPHIC|WELLINGTON_SCL|20240625140000||QBP^Q11^QBP_Q11|MSG00020|P|2.4|||AL|NE||ASCII|||NZL
QPD|Q11^Query Outstanding Orders^HL7|QRY240625-001|^^^NHI^NI|||||DRKIM^Kim^Soyeon^^^Dr
RCP|I|25^RD
```
