# PHCIS (Primary Health Care Information System) - real HL7v2 ER7 messages

---

## 1. ADT^A04 - Patient registration at clinic visit

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|PROV_REG|WC_DOH|20260310080000||ADT^A04^ADT_A01|PHC00001|P|2.3
EVN|A04|20260310080000
PID|||9705185432081^^^RSA_ID^NI||Mabaso^Lungelo^T^^Mr||19970518|M|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|CLINIC^OPD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260310001|||||||||||||||||||||||||||20260310080000
```

---

## 2. ADT^A04 - Antenatal first visit registration

```
MSH|^~\&|PHCIS|HILLBROW_CHC|PROV_REG|GP_DOH|20260311090000||ADT^A04^ADT_A01|PHC00002|P|2.3
EVN|A04|20260311090000
PID|||0004085432088^^^RSA_ID^NI||Chauke^Nompilo^G^^Ms||20000408|F|||35 Kotze Street^^Hillbrow^^2001^ZAF||^^CP^0739876543||ZU|S|||||||||||||ZAF
PV1||O|ANC^MOU^1^HILLBROW_CHC||||MW001^Dlamini^Nothando^^^Sr||||ANC||||A0||VIS20260311001|||||||||||||||||||||||||||20260311090000
```

---

## 3. ADT^A04 - Child under-5 clinic visit

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|PROV_REG|WC_DOH|20260312080000||ADT^A04^ADT_A01|PHC00003|P|2.3
EVN|A04|20260312080000
PID|||2311215432083^^^RSA_ID^NI||Mabaso^Siyamthanda^K^^Miss||20231121|F|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|IMCI^CHILD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260312001|||||||||||||||||||||||||||20260312080000
```

---

## 4. ORU^R01 - HIV rapid test result

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|LAB_RCV|WC_DOH|20260310083000||ORU^R01|PHC00004|P|2.3
PID|||9705185432081^^^RSA_ID^NI||Mabaso^Lungelo^T^^Mr||19970518|M|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|CLINIC^OPD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260310001
OBR|1|HCT20260310001^PHCIS||75622-1^HIV-1 Ab Rapid^LN|||20260310081500|||||||||PROV001^Nkomo^Thembeka^^^Sr||||||20260310083000|||F
OBX|1|CE|75622-1^HIV-1 Ab Rapid Test^LN||260385009^Negative^SCT||||||F
OBX|2|TX|75622-1^HIV Test Counselling^LN||Pre and post-test counselling provided. Patient advised to retest in 3 months.||||||F
```

---

## 5. ORU^R01 - TB GeneXpert screening result

```
MSH|^~\&|PHCIS|HILLBROW_CHC|LAB_RCV|GP_DOH|20260313100000||ORU^R01|PHC00005|P|2.3
PID|||8412145432087^^^RSA_ID^NI||Phakoe^Thabo^J^^Mr||19841214|M|||72 Claim Street^^Hillbrow^^2001^ZAF||^^CP^0851234567||ST|M|||||||||||||ZAF
PV1||O|TB_SCREEN^OPD^2^HILLBROW_CHC||||PROV010^Molefe^Refiloe^^^Sr||||PHC||||A0||VIS20260313001
OBR|1|TB20260313001^PHCIS||94500-6^MTB RNA Xpert^LN|||20260313083000|||||||||PROV010^Molefe^Refiloe^^^Sr||||||20260313100000|||F
OBX|1|CE|94500-6^MTB RNA^LN||260373001^Detected^SCT||||||F
OBX|2|CE|94557-6^Rifampicin resistance^LN||260385009^Not detected^SCT||||||F
OBX|3|TX|94500-6^TB Screening Notes^LN||Sputum sample collected. MTB detected, Rif sensitive. Initiate standard treatment regimen.||||||F
```

---

## 6. ORU^R01 - Immunization record (6-week vaccines)

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|EPI_SYS|WC_DOH|20260312083000||ORU^R01|PHC00006|P|2.3
PID|||2311215432083^^^RSA_ID^NI||Mabaso^Siyamthanda^K^^Miss||20231121|F|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|IMCI^CHILD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260312001
OBR|1|IMM20260312001^PHCIS||30956-7^Immunization Record^LN|||20260312080000|||||||||PROV001^Nkomo^Thembeka^^^Sr||||||20260312083000|||F
OBX|1|CE|30956-7^DTaP-IPV-Hib-HBV^LN||GIVEN^Administered^L||||||F
OBX|2|TS|30956-7^DTaP-IPV-Hib-HBV Date^LN||20230727||||||F
OBX|3|CE|30956-7^OPV^LN||GIVEN^Administered^L||||||F
OBX|4|CE|30956-7^RV^LN||GIVEN^Administered^L||||||F
OBX|5|CE|30956-7^PCV^LN||GIVEN^Administered^L||||||F
```

---

## 7. ORU^R01 - Antenatal booking blood results

```
MSH|^~\&|PHCIS|HILLBROW_CHC|LAB_RCV|GP_DOH|20260312140000||ORU^R01|PHC00007|P|2.3
PID|||0004085432088^^^RSA_ID^NI||Chauke^Nompilo^G^^Ms||20000408|F|||35 Kotze Street^^Hillbrow^^2001^ZAF||^^CP^0739876543||ZU|S|||||||||||||ZAF
PV1||O|ANC^MOU^1^HILLBROW_CHC||||MW001^Dlamini^Nothando^^^Sr||||ANC||||A0||VIS20260311001
OBR|1|ANC20260311001^PHCIS||ANC_BLOODS^Antenatal Booking Bloods^L|||20260311093000|||||||||MW001^Dlamini^Nothando^^^Sr||||||20260312140000|||F
OBX|1|NM|718-7^Hemoglobin^LN||11.2|g/dL|10.0-15.0|N|||F
OBX|2|CE|75622-1^HIV Rapid Test^LN||260385009^Negative^SCT||||||F
OBX|3|CE|5196-1^Rh Type^LN||10828004^Positive^SCT||||||F
OBX|4|CE|882-1^ABO Group^LN||112144000^Type O^SCT||||||F
OBX|5|CE|20507-0^RPR^LN||260385009^Non-reactive^SCT||||||F
```

---

## 8. ORU^R01 - Blood pressure screening chronic disease

```
MSH|^~\&|PHCIS|MITCHELLS_PLAIN_CHC|CHRONIC_SYS|WC_DOH|20260315100000||ORU^R01|PHC00008|P|2.3
PID|||6703185432082^^^RSA_ID^NI||Isaacs^Nasiema^F^^Mrs||19670318|F|||55 AZ Berman Drive^^Mitchells Plain^^7785^ZAF||^^CP^0861234567||AF|M|||||||||||||ZAF
PV1||O|CHRONIC^CDM^1^MITCHELLS_PLAIN_CHC||||PROV020^Hendricks^Rashieda^^^Sr||||PHC||||A0||VIS20260315001
OBR|1|CDM20260315001^PHCIS||CHRONIC_SCREEN^Chronic Disease Monitoring^L|||20260315093000|||||||||PROV020^Hendricks^Rashieda^^^Sr||||||20260315100000|||F
OBX|1|NM|8480-6^Systolic BP^LN||148|mmHg|<140|H|||F
OBX|2|NM|8462-4^Diastolic BP^LN||92|mmHg|<90|H|||F
OBX|3|NM|2345-7^Glucose Fasting^LN||7.8|mmol/L|3.9-6.1|H|||F
OBX|4|NM|29463-7^Weight^LN||89.5|kg|||||F
OBX|5|NM|39156-5^BMI^LN||32.4|kg/m2|18.5-24.9|H|||F
```

---

## 9. ADT^A04 - Walk-in patient registration for acute care

```
MSH|^~\&|PHCIS|DELFT_CHC|PROV_REG|WC_DOH|20260317070000||ADT^A04^ADT_A01|PHC00009|P|2.3
EVN|A04|20260317070000
PID|||0408095432089^^^RSA_ID^NI||Abrahams^Ridwaan^T^^Mr||20040809|M|||44 Symphony Way^^Delft^^7100^ZAF||^^CP^0801234567||AF|S|||||||||||||ZAF
PV1||O|CLINIC^ACUTE^1^DELFT_CHC||||PROV030^Jacobs^Nuraan^^^Sr||||PHC||||A0||VIS20260317001|||||||||||||||||||||||||||20260317070000
```

---

## 10. ORU^R01 - Cervical cancer screening result

```
MSH|^~\&|PHCIS|MITCHELLS_PLAIN_CHC|LAB_RCV|WC_DOH|20260320150000||ORU^R01|PHC00010|P|2.3
PID|||6703185432082^^^RSA_ID^NI||Isaacs^Nasiema^F^^Mrs||19670318|F|||55 AZ Berman Drive^^Mitchells Plain^^7785^ZAF||^^CP^0861234567||AF|M|||||||||||||ZAF
PV1||O|WH^SCREEN^1^MITCHELLS_PLAIN_CHC||||PROV020^Hendricks^Rashieda^^^Sr||||PHC||||A0||VIS20260320001
OBR|1|PAP20260320001^PHCIS||10524-7^Cytology Cervical^LN|||20260320090000|||||||||PROV020^Hendricks^Rashieda^^^Sr||||||20260320150000|||F
OBX|1|CE|10524-7^Pap Smear Result^LN||373887005^NILM (Negative for intraepithelial lesion)^SCT||||||F
OBX|2|TX|10524-7^Cytology Notes^LN||Satisfactory specimen. No evidence of malignancy. Reschedule in 10 years per SA guidelines.||||||F
```

---

## 11. ORU^R01 - Growth monitoring for under-5

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|CHILD_SYS|WC_DOH|20260312084500||ORU^R01|PHC00011|P|2.3
PID|||2311215432083^^^RSA_ID^NI||Mabaso^Siyamthanda^K^^Miss||20231121|F|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|IMCI^CHILD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260312001
OBR|1|GRW20260312001^PHCIS||GROWTH^Growth Monitoring^L|||20260312081500|||||||||PROV001^Nkomo^Thembeka^^^Sr||||||20260312084500|||F
OBX|1|NM|29463-7^Weight^LN||12.8|kg|||||F
OBX|2|NM|8302-2^Height^LN||89.2|cm|||||F
OBX|3|NM|8287-5^Head Circumference^LN||49.1|cm|||||F
OBX|4|TX|GROWTH^Weight-for-age assessment^L||On 50th percentile. Growth on track.||||||F
```

---

## 12. ORU^R01 - Malaria rapid diagnostic test

```
MSH|^~\&|PHCIS|MAKHADO_CHC|LAB_RCV|LP_DOH|20260325090000||ORU^R01|PHC00012|P|2.3
PID|||8906215432080^^^RSA_ID^NI||Tshivhase^Ndivhuwo^A^^Mr||19890621|M|||18 Songozwi Road^^Makhado^^0920^ZAF||^^CP^0816543210||VE|M|||||||||||||ZAF
PV1||O|CLINIC^ACUTE^1^MAKHADO_CHC||||PROV040^Ramabulana^Mashudu^^^Sr||||PHC||||A0||VIS20260325001
OBR|1|MAL20260325001^PHCIS||32700-7^Malaria smear^LN|||20260325081000|||||||||PROV040^Ramabulana^Mashudu^^^Sr||||||20260325090000|||F
OBX|1|CE|32700-7^Malaria RDT^LN||260373001^Positive - P. falciparum^SCT||||||F
OBX|2|TX|32700-7^Malaria Notes^LN||Notifiable condition. Patient started on artemether/lumefantrine. Reported to district surveillance.||||||F
```

---

## 13. ADT^A04 - Mental health clinic visit

```
MSH|^~\&|PHCIS|DELFT_CHC|PROV_REG|WC_DOH|20260401090000||ADT^A04^ADT_A01|PHC00013|P|2.3
EVN|A04|20260401090000
PID|||8703135432086^^^RSA_ID^NI||Davids^Faizel^R^^Mr||19870313|M|||21 Belhar Road^^Belhar^^7493^ZAF||^^CP^0831234567||AF|S|||||||||||||ZAF
PV1||O|MH^PSYCH^1^DELFT_CHC||||PROV050^Petersen^Wendy^^^Sr||||MH||||A0||VIS20260401001|||||||||||||||||||||||||||20260401090000
```

---

## 14. ORU^R01 - Diabetes HbA1c monitoring with lab report PDF

```
MSH|^~\&|PHCIS|MITCHELLS_PLAIN_CHC|LAB_RCV|WC_DOH|20260318110000||ORU^R01|PHC00014|P|2.3
PID|||6703185432082^^^RSA_ID^NI||Isaacs^Nasiema^F^^Mrs||19670318|F|||55 AZ Berman Drive^^Mitchells Plain^^7785^ZAF||^^CP^0861234567||AF|M|||||||||||||ZAF
PV1||O|CHRONIC^CDM^1^MITCHELLS_PLAIN_CHC||||PROV020^Hendricks^Rashieda^^^Sr||||PHC||||A0||VIS20260318001
OBR|1|HBA20260318001^PHCIS||4548-4^HbA1c^LN|||20260315090000|||||||||PROV020^Hendricks^Rashieda^^^Sr||||||20260318110000|||F
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.2|%|<7.0|H|||F
OBX|2|TX|4548-4^HbA1c Interpretation^LN||Above target. Adjust oral hypoglycemics. Dietitian referral recommended.||||||F
OBX|3|ED|PDF^Lab Report PDF^NHLS||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKCL9NZWRpYUJveA||||||F
```

---

## 15. ORU^R01 - PMTCT infant PCR result

```
MSH|^~\&|PHCIS|HILLBROW_CHC|LAB_RCV|GP_DOH|20260405140000||ORU^R01|PHC00015|P|2.3
PID|||2603165432084^^^RSA_ID^NI||Mkhwanazi^Lwandle^S^^Master||20260316|M|||15 Abel Road^^Hillbrow^^2001^ZAF||^^CP^0749876543||ZU|S|||||||||||||ZAF
PV1||O|IMCI^CHILD^1^HILLBROW_CHC||||MW001^Dlamini^Nothando^^^Sr||||PHC||||A0||VIS20260405001
OBR|1|PCR20260405001^PHCIS||9836-8^HIV-1 DNA PCR^LN|||20260401080000|||||||||MW001^Dlamini^Nothando^^^Sr||||||20260405140000|||F
OBX|1|CE|9836-8^HIV-1 DNA PCR^LN||260385009^Not detected^SCT||||||F
OBX|2|TX|9836-8^PMTCT Notes^LN||Birth PCR negative. Continue breastfeeding monitoring. Repeat at 10 weeks.||||||F
```

---

## 16. ADT^A04 - Occupational health clinic visit

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|PROV_REG|WC_DOH|20260408080000||ADT^A04^ADT_A01|PHC00016|P|2.3
EVN|A04|20260408080000
PID|||7902145432088^^^RSA_ID^NI||Siyolo^Luyanda^M^^Mr||19790214|M|||8 Ntlazane Road^^Khayelitsha^^7784^ZAF||^^CP^0841234567||XH|M|||||||||||||ZAF
PV1||O|OCC_H^OHS^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||OHS||||A0||VIS20260408001|||||||||||||||||||||||||||20260408080000
```

---

## 17. ORU^R01 - STI syndromic management result

```
MSH|^~\&|PHCIS|DELFT_CHC|LAB_RCV|WC_DOH|20260410110000||ORU^R01|PHC00017|P|2.3
PID|||9301185432089^^^RSA_ID^NI||Kock^Cheslyn^R^^Ms||19930118|F|||66 Voorbrug Road^^Delft^^7100^ZAF||^^CP^0813456789||AF|S|||||||||||||ZAF
PV1||O|WH^STI^1^DELFT_CHC||||PROV030^Jacobs^Nuraan^^^Sr||||PHC||||A0||VIS20260410001
OBR|1|STI20260410001^PHCIS||STI_SCREEN^STI Syndromic Assessment^L|||20260410090000|||||||||PROV030^Jacobs^Nuraan^^^Sr||||||20260410110000|||F
OBX|1|CE|STI_SYNDROME^Vaginal discharge syndrome^L||PRESENT^Positive^L||||||F
OBX|2|TX|STI_SCREEN^Treatment^L||Syndromic management: Ceftriaxone 250mg IM stat + Azithromycin 1g PO stat + Metronidazole 2g PO stat. Partner notification issued.||||||F
```

---

## 18. ORU^R01 - Road to Health booklet scan with embedded image

```
MSH|^~\&|PHCIS|KHAYELITSHA_CHC|DOC_SYS|WC_DOH|20260312090000||ORU^R01|PHC00018|P|2.3
PID|||2311215432083^^^RSA_ID^NI||Mabaso^Siyamthanda^K^^Miss||20231121|F|||32 Mew Way^^Khayelitsha^^7784^ZAF||^^CP^0749876543||XH|S|||||||||||||ZAF
PV1||O|IMCI^CHILD^1^KHAYELITSHA_CHC||||PROV001^Nkomo^Thembeka^^^Sr||||PHC||||A0||VIS20260312001
OBR|1|RTH20260312001^PHCIS||RTH^Road to Health Booklet^L|||20260312081500|||||||||PROV001^Nkomo^Thembeka^^^Sr||||||20260312090000|||F
OBX|1|TX|RTH^Road to Health Notes^L||Growth chart updated. All immunizations up to date for age. No developmental concerns.||||||F
OBX|2|ED|IMG^Road to Health Scan^PHCIS||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEAYABgAAD/4QBaRXhpZgAATU0AKgAAAAgABQMBAAUAAAABAAAASgMDAAEAAAABAAAAAFEQAAEAAAABAQAAAFERAAQAAAABAAAOw1ESAAQAAAABAAAOwwAAAAD/2wBDAAgG||||||F
```

---

## 19. ORU^R01 - COVID-19 rapid antigen test

```
MSH|^~\&|PHCIS|MAKHADO_CHC|LAB_RCV|LP_DOH|20260415080000||ORU^R01|PHC00019|P|2.3
PID|||9307105432085^^^RSA_ID^NI||Mudau^Livhuwani^P^^Ms||19930710|F|||12 Krogh Street^^Makhado^^0920^ZAF||^^CP^0839876543||VE|S|||||||||||||ZAF
PV1||O|CLINIC^RESP^1^MAKHADO_CHC||||PROV040^Ramabulana^Mashudu^^^Sr||||PHC||||A0||VIS20260415001
OBR|1|COV20260415001^PHCIS||94558-4^SARS-CoV-2 Ag Rapid^LN|||20260415074500|||||||||PROV040^Ramabulana^Mashudu^^^Sr||||||20260415080000|||F
OBX|1|CE|94558-4^SARS-CoV-2 Ag^LN||260385009^Negative^SCT||||||F
OBX|2|TX|94558-4^COVID Notes^LN||Patient symptomatic with cough and fever. Ag test negative. Supportive management.||||||F
```

---

## 20. ADT^A04 - Family planning visit

```
MSH|^~\&|PHCIS|HILLBROW_CHC|PROV_REG|GP_DOH|20260420090000||ADT^A04^ADT_A01|PHC00020|P|2.3
EVN|A04|20260420090000
PID|||0004085432088^^^RSA_ID^NI||Chauke^Nompilo^G^^Ms||20000408|F|||35 Kotze Street^^Hillbrow^^2001^ZAF||^^CP^0739876543||ZU|S|||||||||||||ZAF
PV1||O|WH^FP^1^HILLBROW_CHC||||MW001^Dlamini^Nothando^^^Sr||||FP||||A0||VIS20260420001|||||||||||||||||||||||||||20260420090000
```
