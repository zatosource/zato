# PREHMIS (Patient Registration and Health Management Information System) - real HL7v2 ER7 messages

---

## 1. ADT^A04 - Outpatient registration at Groote Schuur

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|HIE_RCV|WC_DOH|20260310080000||ADT^A04^ADT_A01|PRE00001|P|2.4
EVN|A04|20260310080000
PID|||8007185432087^^^RSA_ID^NI||Carelse^Rushdi^M^^Mr||19800718|M|||33 Belmont Road^^Rondebosch^^7700^ZAF||^^PH^0214567890~^^CP^0839876543||AF|M|||||||||||||ZAF
PV1||O|MED_OPD^CLINIC^3^GROOTE_SCHUUR||||DOC900^Petersen^Faizel^^^Dr||||MED||||A0||VIS20260310001|||||||||||||||||||||||||||20260310080000
```

---

## 2. ADT^A01 - Inpatient admission at Tygerberg

```
MSH|^~\&|PREHMIS|TYGERBERG_HOSP|HIE_RCV|WC_DOH|20260311070000||ADT^A01^ADT_A01|PRE00002|P|2.4
EVN|A01|20260311070000
PID|||6510145432081^^^RSA_ID^NI||Van Wyk^Annelize^C^^Mrs||19651014|F|||18 Voortrekker Road^^Bellville^^7530^ZAF||^^PH^0219876543~^^CP^0841234567||AF|M|||||||||||||ZAF
PV1||I|CARD^ICU^2^TYGERBERG_HOSP||||DOC910^Du Plessis^Marius^^^Prof||||CARD||||A0||ADM20260311001|||||||||||||||||||||||||||20260311070000
NK1|1|Van Wyk^Danie^^Mr|SPO|18 Voortrekker Road^^Bellville^^7530^ZAF|^^CP^0843456789
```

---

## 3. ADT^A01 - Emergency admission at Karl Bremer

```
MSH|^~\&|PREHMIS|KARL_BREMER|HIE_RCV|WC_DOH|20260312022000||ADT^A01^ADT_A01|PRE00003|P|2.4
EVN|A01|20260312022000
PID|||9405105432084^^^RSA_ID^NI||Dyani^Zoleka^N^^Ms||19940510|F|||65 Frans Conradie Drive^^Parow^^7500^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||E|ER^RESUS^1^KARL_BREMER||||DOC920^Claassen^Riaan^^^Dr||||ER||||A0||EV20260312001|||||||||||||||||||||||||||20260312022000
```

---

## 4. ADT^A02 - Patient transfer within Groote Schuur

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|HIE_RCV|WC_DOH|20260313091500||ADT^A02^ADT_A02|PRE00004|P|2.4
EVN|A02|20260313091500
PID|||8702075432085^^^RSA_ID^NI||Samuels^Mogamat^Y^^Mr||19870207|M|||9 Hanover Street^^District Six^^8001^ZAF||^^CP^0856543210||AF|M|||||||||||||ZAF
PV1||I|NEURO^HDU^1^GROOTE_SCHUUR||||DOC930^Swanepoel^Jacobus^^^Dr||||NEURO||||A0||ADM20260311005|||||||||||||||||||||||||||20260313091500
PV2|||||||||||||||||||||||||||||||NEURO^WARD^4^GROOTE_SCHUUR
```

---

## 5. ADT^A03 - Discharge from Tygerberg

```
MSH|^~\&|PREHMIS|TYGERBERG_HOSP|HIE_RCV|WC_DOH|20260318140000||ADT^A03^ADT_A03|PRE00005|P|2.4
EVN|A03|20260318140000
PID|||6510145432081^^^RSA_ID^NI||Van Wyk^Annelize^C^^Mrs||19651014|F|||18 Voortrekker Road^^Bellville^^7530^ZAF||^^PH^0219876543~^^CP^0841234567||AF|M|||||||||||||ZAF
PV1||I|CARD^ICU^2^TYGERBERG_HOSP||||DOC910^Du Plessis^Marius^^^Prof||||CARD||||A0||ADM20260311001|||||||||||||||||||||||||||20260318140000
DG1|1||I21.0^Acute transmural MI anterior wall^I10||20260311|A
```

---

## 6. ADT^A08 - Update patient address

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|HIE_RCV|WC_DOH|20260320100000||ADT^A08^ADT_A01|PRE00006|P|2.4
EVN|A08|20260320100000
PID|||8007185432087^^^RSA_ID^NI||Carelse^Rushdi^M^^Mr||19800718|M|||33 Belmont Road^^Rondebosch^^7700^ZAF||^^PH^0214567890~^^CP^0839876543||AF|M|||||||||||||ZAF
PV1||O|MED_OPD^CLINIC^3^GROOTE_SCHUUR||||DOC900^Petersen^Faizel^^^Dr||||MED||||A0||VIS20260310001
```

---

## 7. ADT^A28 - Add person to provincial MPI

```
MSH|^~\&|PREHMIS|WC_PROVINCIAL|MPI_SYS|WC_DOH|20260322090000||ADT^A28^ADT_A05|PRE00007|P|2.4
EVN|A28|20260322090000
PID|||0703215432080^^^RSA_ID^NI||Jacobs^Ashraf^M^^Master||20070321|M|||11 Adderley Street^^Cape Town^^8001^ZAF||^^CP^0801234567||AF|S|||||||||||||ZAF
PV1||N
```

---

## 8. ORU^R01 - Full blood count from Groote Schuur lab

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|LAB_RCV|NHLS_GSH|20260311100000||ORU^R01|PRE00008|P|2.4
PID|||8007185432087^^^RSA_ID^NI||Carelse^Rushdi^M^^Mr||19800718|M|||33 Belmont Road^^Rondebosch^^7700^ZAF||^^PH^0214567890~^^CP^0839876543||AF|M|||||||||||||ZAF
PV1||O|MED_OPD^CLINIC^3^GROOTE_SCHUUR||||DOC900^Petersen^Faizel^^^Dr||||MED||||A0||VIS20260310001
OBR|1|LAB20260310001^PREHMIS|LR20260311001^NHLS_GSH|CBC^Full Blood Count^L|||20260310083000|||||||||DOC900^Petersen^Faizel^^^Dr||||||20260311100000|||F
OBX|1|NM|6690-2^WBC^LN||5.8|10*9/L|4.0-10.0|N|||F
OBX|2|NM|789-8^RBC^LN||5.1|10*12/L|4.5-5.5|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||15.2|g/dL|13.0-17.0|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||45.3|%|40.0-50.0|N|||F
OBX|5|NM|777-3^Platelet Count^LN||267|10*9/L|150-400|N|||F
```

---

## 9. ORU^R01 - Cardiac enzymes from Tygerberg

```
MSH|^~\&|PREHMIS|TYGERBERG_HOSP|LAB_RCV|NHLS_TBH|20260311073000||ORU^R01|PRE00009|P|2.4
PID|||6510145432081^^^RSA_ID^NI||Van Wyk^Annelize^C^^Mrs||19651014|F|||18 Voortrekker Road^^Bellville^^7530^ZAF||^^PH^0219876543~^^CP^0841234567||AF|M|||||||||||||ZAF
PV1||E|ER^RESUS^1^TYGERBERG_HOSP||||DOC910^Du Plessis^Marius^^^Prof||||ER||||A0||EV20260311001
OBR|1|LAB20260311001^PREHMIS|LR20260311001^NHLS_TBH|CARDIAC^Cardiac Markers^L|||20260311060000|||||||||DOC910^Du Plessis^Marius^^^Prof||||||20260311073000|||F
OBX|1|NM|49563-0^Troponin T hs^LN||892|ng/L|0-14|HH|||F
OBX|2|NM|2157-6^CK Total^LN||1245|U/L|30-200|H|||F
OBX|3|NM|32673-6^CK-MB^LN||98|U/L|0-25|H|||F
OBX|4|NM|30392-5^NT-proBNP^LN||4560|pg/mL|0-300|HH|||F
```

---

## 10. ORU^R01 - Renal function panel

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|LAB_RCV|NHLS_GSH|20260315110000||ORU^R01|PRE00010|P|2.3
PID|||7201285432082^^^RSA_ID^NI||Taliep^Faiez^H^^Mr||19720128|M|||42 Imam Haron Road^^Claremont^^7708^ZAF||^^CP^0831234567||AF|M|||||||||||||ZAF
PV1||O|RENAL^CLINIC^1^GROOTE_SCHUUR||||DOC940^Davids^Nasiema^^^Prof||||RENAL||||A0||VIS20260315001
OBR|1|LAB20260315001^PREHMIS|LR20260315001^NHLS_GSH|RENAL^Renal Function Panel^L|||20260315080000|||||||||DOC940^Davids^Nasiema^^^Prof||||||20260315110000|||F
OBX|1|NM|2160-0^Creatinine^LN||245|umol/L|60-110|H|||F
OBX|2|NM|3094-0^Urea^LN||18.5|mmol/L|2.5-7.1|H|||F
OBX|3|NM|33914-3^eGFR^LN||28|mL/min/1.73m2|>60|L|||F
OBX|4|NM|2823-3^Potassium^LN||5.8|mmol/L|3.5-5.1|H|||F
OBX|5|NM|17861-6^Calcium^LN||2.05|mmol/L|2.15-2.55|L|||F
```

---

## 11. ORU^R01 - HIV viral load from Karl Bremer

```
MSH|^~\&|PREHMIS|KARL_BREMER|LAB_RCV|NHLS_KB|20260318140000||ORU^R01|PRE00011|P|2.3
PID|||9008215432086^^^RSA_ID^NI||Peterson^Tasneem^A^^Ms||19900821|F|||44 Durban Road^^Bellville^^7530^ZAF||^^CP^0781234567||AF|S|||||||||||||ZAF
PV1||O|ARV^CLINIC^1^KARL_BREMER||||DOC950^Jacobs^Abduraghmaan^^^Dr||||ID||||A0||VIS20260318001
OBR|1|LAB20260318001^PREHMIS|VL20260318001^NHLS_KB|25836-8^HIV-1 RNA^LN|||20260318080000|||||||||DOC950^Jacobs^Abduraghmaan^^^Dr||||||20260318140000|||F
OBX|1|NM|25836-8^HIV-1 RNA^LN||<40|copies/mL|<40|N|||F
OBX|2|NM|24467-3^CD4 Count^LN||456|cells/uL|>200|N|||F
OBX|3|TX|25836-8^VL Interpretation^LN||Virally suppressed. Continue current ART regimen. Next VL in 12 months.||||||F
```

---

## 12. ORU^R01 - Cervical cytology from Groote Schuur

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|LAB_RCV|NHLS_GSH|20260320160000||ORU^R01|PRE00012|P|2.4
PID|||8305085432088^^^RSA_ID^NI||Williams^Fagmieda^R^^Mrs||19830508|F|||77 Wetton Road^^Wynberg^^7800^ZAF||^^CP^0861234567||AF|M|||||||||||||ZAF
PV1||O|GYNAE^CLINIC^2^GROOTE_SCHUUR||||DOC960^Louw^Annette^^^Dr||||GYN||||A0||VIS20260320001
OBR|1|CYT20260320001^PREHMIS|CYT20260320001^NHLS_GSH|10524-7^Cervical Cytology^LN|||20260320090000|||||||||DOC960^Louw^Annette^^^Dr||||||20260320160000|||F
OBX|1|CE|10524-7^Pap Result^LN||HSIL^High-grade squamous intraepithelial lesion^L||||||F
OBX|2|TX|10524-7^Cytology Recommendation^LN||HSIL identified. Refer for colposcopy within 2 weeks. Patient counselled.||||||F
```

---

## 13. ORU^R01 - Radiology report with embedded PDF from Tygerberg

```
MSH|^~\&|PREHMIS|TYGERBERG_HOSP|RAD_RCV|PACS_TBH|20260312100000||ORU^R01|PRE00013|P|2.4
PID|||6510145432081^^^RSA_ID^NI||Van Wyk^Annelize^C^^Mrs||19651014|F|||18 Voortrekker Road^^Bellville^^7530^ZAF||^^PH^0219876543~^^CP^0841234567||AF|M|||||||||||||ZAF
PV1||I|CARD^ICU^2^TYGERBERG_HOSP||||DOC910^Du Plessis^Marius^^^Prof||||CARD||||A0||ADM20260311001
OBR|1|RAD20260311001^PREHMIS|RAD20260312001^PACS_TBH|71046^CXR PA^CPT|||20260311080000|||||||||DOC910^Du Plessis^Marius^^^Prof||||||20260312100000|||F
OBX|1|TX|71046^CXR Report^CPT||Cardiomegaly. Upper lobe pulmonary venous congestion. Bilateral pleural effusions, small. Consistent with CCF.||||||F
OBX|2|ED|PDF^Radiology Report PDF^PREHMIS||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKCL9NZWRp||||||F
```

---

## 14. ADT^A04 - Ante-natal clinic visit at Mowbray Maternity

```
MSH|^~\&|PREHMIS|MOWBRAY_MATERNITY|HIE_RCV|WC_DOH|20260325090000||ADT^A04^ADT_A01|PRE00014|P|2.3
EVN|A04|20260325090000
PID|||9809215432089^^^RSA_ID^NI||Mpemba^Thembisa^A^^Ms||19980921|F|||22 Roodebloem Road^^Woodstock^^7925^ZAF||^^CP^0731234567||XH|S|||||||||||||ZAF
PV1||O|ANC^MOU^1^MOWBRAY_MATERNITY||||MW200^Magwaza^Nolusindiso^^^Sr||||ANC||||A0||VIS20260325001|||||||||||||||||||||||||||20260325090000
```

---

## 15. ORU^R01 - Antenatal booking bloods from Mowbray

```
MSH|^~\&|PREHMIS|MOWBRAY_MATERNITY|LAB_RCV|NHLS_MOW|20260326140000||ORU^R01|PRE00015|P|2.3
PID|||9809215432089^^^RSA_ID^NI||Mpemba^Thembisa^A^^Ms||19980921|F|||22 Roodebloem Road^^Woodstock^^7925^ZAF||^^CP^0731234567||XH|S|||||||||||||ZAF
PV1||O|ANC^MOU^1^MOWBRAY_MATERNITY||||MW200^Magwaza^Nolusindiso^^^Sr||||ANC||||A0||VIS20260325001
OBR|1|ANC20260325001^PREHMIS|LR20260326001^NHLS_MOW|ANC_BLOODS^Antenatal Booking Bloods^L|||20260325091500|||||||||MW200^Magwaza^Nolusindiso^^^Sr||||||20260326140000|||F
OBX|1|NM|718-7^Hemoglobin^LN||12.1|g/dL|10.0-15.0|N|||F
OBX|2|CE|75622-1^HIV Rapid^LN||260385009^Negative^SCT||||||F
OBX|3|CE|882-1^Blood Group^LN||278149003^A Positive^SCT||||||F
OBX|4|CE|20507-0^RPR^LN||260385009^Non-reactive^SCT||||||F
OBX|5|NM|2345-7^Glucose Random^LN||5.2|mmol/L|3.5-7.8|N|||F
```

---

## 16. ORU^R01 - TB sputum result from Karl Bremer

```
MSH|^~\&|PREHMIS|KARL_BREMER|LAB_RCV|NHLS_KB|20260401110000||ORU^R01|PRE00016|P|2.3
PID|||8403145432083^^^RSA_ID^NI||Adonis^Mogamat^R^^Mr||19840314|M|||15 Halt Road^^Elsies River^^7490^ZAF||^^CP^0843456789||AF|S|||||||||||||ZAF
PV1||O|TB^CLINIC^1^KARL_BREMER||||DOC970^Hendricks^Tarryn^^^Dr||||TB||||A0||VIS20260401001
OBR|1|TB20260401001^PREHMIS|LR20260401001^NHLS_KB|94500-6^GeneXpert MTB^LN|||20260401080000|||||||||DOC970^Hendricks^Tarryn^^^Dr||||||20260401110000|||F
OBX|1|CE|94500-6^MTB Result^LN||260373001^MTB Detected^SCT||||||F
OBX|2|CE|94557-6^Rif Resistance^LN||260385009^Not Detected^SCT||||||F
OBX|3|TX|94500-6^TB Notes^LN||MTB detected, rifampicin sensitive. Start standard regimen. Notify via PREHMIS. Contact tracing required.||||||F
```

---

## 17. ADT^A01 - Neonatal admission at Groote Schuur

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|HIE_RCV|WC_DOH|20260405060000||ADT^A01^ADT_A01|PRE00017|P|2.4
EVN|A01|20260405060000
PID|||2604055432090^^^RSA_ID^NI||Adams^Baby of Shahieda^^^^^NEWBORN||20260405|F|||12 Turfhall Road^^Rondebosch^^7700^ZAF||^^CP^0841234567||AF|S|||||||||||||ZAF
PV1||I|NICU^COT^5^GROOTE_SCHUUR||||DOC980^Paulsen^Helene^^^Dr||||NEO||||A0||ADM20260405001|||||||||||||||||||||||||||20260405060000
NK1|1|Adams^Shahieda^^Ms|MTH|12 Turfhall Road^^Rondebosch^^7700^ZAF|^^CP^0841234567
```

---

## 18. ORU^R01 - Neonatal screening results with scanned form

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|SCREEN_SYS|NHLS_GSH|20260407100000||ORU^R01|PRE00018|P|2.4
PID|||2604055432090^^^RSA_ID^NI||Adams^Baby of Shahieda^^^^^NEWBORN||20260405|F|||12 Turfhall Road^^Rondebosch^^7700^ZAF||^^CP^0841234567||AF|S|||||||||||||ZAF
PV1||I|NICU^COT^5^GROOTE_SCHUUR||||DOC980^Paulsen^Helene^^^Dr||||NEO||||A0||ADM20260405001
OBR|1|NBS20260407001^PREHMIS|NBS20260407001^NHLS_GSH|54089-8^Newborn Screen^LN|||20260406080000|||||||||DOC980^Paulsen^Helene^^^Dr||||||20260407100000|||F
OBX|1|CE|54090-6^TSH Newborn^LN||260385009^Normal^SCT||||||F
OBX|2|CE|54079-9^Phenylalanine Newborn^LN||260385009^Normal^SCT||||||F
OBX|3|CE|57700-5^Hearing Screen^LN||PASS^Both ears pass^L||||||F
OBX|4|ED|IMG^Newborn Screening Form Scan^PREHMIS||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7||||||F
```

---

## 19. ADT^A13 - Cancel discharge at Tygerberg

```
MSH|^~\&|PREHMIS|TYGERBERG_HOSP|HIE_RCV|WC_DOH|20260410160000||ADT^A13^ADT_A01|PRE00019|P|2.4
EVN|A13|20260410160000
PID|||7201285432082^^^RSA_ID^NI||Taliep^Faiez^H^^Mr||19720128|M|||42 Imam Haron Road^^Claremont^^7708^ZAF||^^CP^0831234567||AF|M|||||||||||||ZAF
PV1||I|RENAL^WARD^3^TYGERBERG_HOSP||||DOC940^Davids^Nasiema^^^Prof||||RENAL||||A0||ADM20260408001|||||||||||||||||||||||||||20260408070000
```

---

## 20. ORU^R01 - Discharge summary with embedded document from Groote Schuur

```
MSH|^~\&|PREHMIS|GROOTE_SCHUUR|DOC_SYS|HIE_WC|20260415150000||ORU^R01|PRE00020|P|2.4
PID|||8007185432087^^^RSA_ID^NI||Carelse^Rushdi^M^^Mr||19800718|M|||33 Belmont Road^^Rondebosch^^7700^ZAF||^^PH^0214567890~^^CP^0839876543||AF|M|||||||||||||ZAF
PV1||I|MED^WARD^8^GROOTE_SCHUUR||||DOC900^Petersen^Faizel^^^Dr||||MED||||A0||ADM20260410001
OBR|1|DS20260415001^PREHMIS|DS20260415001^DOC|28570-0^Discharge Summary^LN|||20260410080000|||||||||DOC900^Petersen^Faizel^^^Dr||||||20260415150000|||F
OBX|1|TX|28570-0^Discharge Summary^LN||Admitted with community-acquired pneumonia. IV antibiotics 5 days then step-down to oral. Sputum culture negative for TB. Discharge on oral amoxicillin.||||||F
OBX|2|ED|PDF^Discharge Summary PDF^PREHMIS||^AP^^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCi9PdXRsaW5lcyAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tp||||||F
```
