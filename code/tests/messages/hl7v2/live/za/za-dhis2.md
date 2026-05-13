# DHIS2 (District Health Information System) - real HL7v2 ER7 messages

---

## 1. ADT^A04 - Patient registration for disease notification

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_JHB_DH|NICD_RCV|NOTIFIABLE|20260310080000||ADT^A04^ADT_A01|DHIS00001|P|2.3
EVN|A04|20260310080000
PID|||8908185432087^^^RSA_ID^NI||Kubheka^Sifiso^M^^Mr||19890818|M|||44 Rissik Street^^Johannesburg CBD^^2001^ZAF||^^CP^0739876543||ZU|S|||||||||||||ZAF
PV1||O|SURV^NOTIFY^1^CITY_OF_JHB_DH||||DOC800^Nkambule^Phindile^^^Dr||||PH||||A0||VIS20260310001|||||||||||||||||||||||||||20260310080000
```

---

## 2. ADT^A04 - Registration for immunization campaign

```
MSH|^~\&|DHIS2_TRACKER|ETHEKWINI_DH|EPI_SYS|KZN_DOH|20260312090000||ADT^A04^ADT_A01|DHIS00002|P|2.3
EVN|A04|20260312090000
PID|||2207145432082^^^RSA_ID^NI||Zondi^Nhlanhla^T^^Master||20220714|M|||33 Umgeni Road^^Durban^^4001^ZAF||^^CP^0845678901||ZU|S|||||||||||||ZAF
PV1||O|EPI^CAMP^1^ETHEKWINI_DH||||PROV100^Mkhwanazi^Thandeka^^^Sr||||EPI||||A0||VIS20260312001|||||||||||||||||||||||||||20260312090000
```

---

## 3. ORU^R01 - Measles case notification

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_JHB_DH|NICD_RCV|NOTIFIABLE|20260311100000||ORU^R01|DHIS00003|P|2.3
PID|||2105225432083^^^RSA_ID^NI||Mthiyane^Enhle^S^^Miss||20210522|F|||67 Eloff Street^^Johannesburg^^2001^ZAF||^^CP^0726789012||ZU|S|||||||||||||ZAF
PV1||O|SURV^NOTIFY^1^CITY_OF_JHB_DH||||DOC800^Nkambule^Phindile^^^Dr||||PH||||A0||VIS20260311001
OBR|1|NOT20260311001^DHIS2_TRACKER||NOTIFY^Disease Notification^L|||20260311083000|||||||||DOC800^Nkambule^Phindile^^^Dr||||||20260311100000|||F
OBX|1|CE|56831-1^Condition Notified^LN||14189004^Measles^SCT||||||F
OBX|2|TS|11368-8^Onset Date^LN||20260308||||||F
OBX|3|CE|67187-5^Vaccination Status^LN||373066001^Not immunized^SCT||||||F
OBX|4|TX|NOTIFY^Case Notes^L||Confirmed measles. Rash onset 3 days ago. No travel history. Contact tracing initiated for creche.||||||F
```

---

## 4. ORU^R01 - Cholera surveillance report

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_TSHWANE_DH|NICD_RCV|NOTIFIABLE|20260315110000||ORU^R01|DHIS00004|P|2.3
PID|||8010165432086^^^RSA_ID^NI||Phiri^Johannes^B^^Mr||19801016|M|||55 Mamelodi West Road^^Mamelodi^^0122^ZAF||^^CP^0813456789||NS|M|||||||||||||ZAF
PV1||O|SURV^NOTIFY^1^CITY_OF_TSHWANE_DH||||DOC810^Pretorius^Annemarie^^^Dr||||PH||||A0||VIS20260315001
OBR|1|NOT20260315001^DHIS2_TRACKER||NOTIFY^Disease Notification^L|||20260315080000|||||||||DOC810^Pretorius^Annemarie^^^Dr||||||20260315110000|||F
OBX|1|CE|56831-1^Condition Notified^LN||63650001^Cholera^SCT||||||F
OBX|2|TS|11368-8^Onset Date^LN||20260313||||||F
OBX|3|CE|LAB_CONFIRM^Lab Confirmation^L||260373001^Culture positive V. cholerae O1^SCT||||||F
OBX|4|TX|NOTIFY^Case Notes^L||Severe dehydration. Admitted to hospital. Water source investigation underway in Mamelodi East.||||||F
```

---

## 5. ORU^R01 - Weekly disease surveillance summary

```
MSH|^~\&|DHIS2_HIS|CITY_OF_JHB_DH|NICD_RCV|SURVEILLANCE|20260317160000||ORU^R01|DHIS00005|P|2.3
PID|||AGGREGATE^^^CITY_OF_JHB^AG||City of Johannesburg^District^Health^^Aggregate||||||||||||||||||||||||||||||GP
PV1||O|SURV^WEEKLY^1^CITY_OF_JHB_DH||||ADMIN^District Office^^^^^Admin||||PH||||A0||RPT20260317001
OBR|1|WK20260317001^DHIS2_HIS||WEEKLY_SURV^Weekly Surveillance Summary^L|||20260310000000|20260316235959||||||||ADMIN^District Office^^^^^Admin||||||20260317160000|||F
OBX|1|NM|MEASLES_CASES^Measles cases this week^L||3|cases|||||F
OBX|2|NM|TB_NEW^New TB cases this week^L||47|cases|||||F
OBX|3|NM|DIARRHOEA_U5^Diarrhoea under-5 this week^L||128|cases|||||F
OBX|4|NM|MALARIA_CASES^Malaria cases this week^L||0|cases|||||F
OBX|5|NM|COVID_CASES^COVID-19 cases this week^L||12|cases|||||F
```

---

## 6. ORU^R01 - Immunization coverage report

```
MSH|^~\&|DHIS2_HIS|ETHEKWINI_DH|EPI_SYS|KZN_DOH|20260320140000||ORU^R01|DHIS00006|P|2.3
PID|||AGGREGATE^^^ETHEKWINI^AG||eThekwini^District^Health^^Aggregate||||||||||||||||||||||||||||||KZN
PV1||O|EPI^REPORT^1^ETHEKWINI_DH||||ADMIN^District EPI^^^^^Admin||||EPI||||A0||RPT20260320001
OBR|1|EPI20260320001^DHIS2_HIS||EPI_COV^EPI Coverage Report^L|||20260201000000|20260228235959||||||||ADMIN^District EPI^^^^^Admin||||||20260320140000|||F
OBX|1|NM|BCG_COV^BCG Coverage^L||97.2|%|>90|N|||F
OBX|2|NM|PENTA3_COV^Pentavalent 3rd Dose Coverage^L||82.4|%|>90|L|||F
OBX|3|NM|MEASLES1_COV^Measles 1st Dose Coverage^L||88.1|%|>90|L|||F
OBX|4|NM|PCV3_COV^PCV13 3rd Dose Coverage^L||79.8|%|>90|L|||F
OBX|5|NM|RV2_COV^Rotavirus 2nd Dose Coverage^L||85.3|%|>90|L|||F
```

---

## 7. ADT^A04 - TB case registration for tracking

```
MSH|^~\&|DHIS2_TRACKER|MANGAUNG_DH|TB_REG|FS_DOH|20260322080000||ADT^A04^ADT_A01|DHIS00007|P|2.3
EVN|A04|20260322080000
PID|||9203085432080^^^RSA_ID^NI||Tsiu^Masabata^D^^Ms||19920308|F|||18 Nelson Mandela Drive^^Bloemfontein^^9301^ZAF||^^CP^0534567890||ST|S|||||||||||||ZAF
PV1||O|TB^REG^1^MANGAUNG_DH||||DOC820^Coetzee^Adriaan^^^Dr||||TB||||A0||VIS20260322001|||||||||||||||||||||||||||20260322080000
```

---

## 8. ORU^R01 - TB treatment outcome report

```
MSH|^~\&|DHIS2_TRACKER|MANGAUNG_DH|TB_REG|FS_DOH|20260401100000||ORU^R01|DHIS00008|P|2.3
PID|||9203085432080^^^RSA_ID^NI||Tsiu^Masabata^D^^Ms||19920308|F|||18 Nelson Mandela Drive^^Bloemfontein^^9301^ZAF||^^CP^0534567890||ST|S|||||||||||||ZAF
PV1||O|TB^REG^1^MANGAUNG_DH||||DOC820^Coetzee^Adriaan^^^Dr||||TB||||A0||VIS20260322001
OBR|1|TB20260401001^DHIS2_TRACKER||TB_OUTCOME^TB Treatment Outcome^L|||20260322080000|||||||||DOC820^Coetzee^Adriaan^^^Dr||||||20260401100000|||F
OBX|1|CE|TB_CAT^TB Category^L||NEW^New pulmonary TB^L||||||F
OBX|2|CE|TB_DIAG^Diagnostic Method^L||GENEXPERT^GeneXpert positive^L||||||F
OBX|3|TS|TB_START^Treatment Start Date^L||20260322||||||F
OBX|4|CE|TB_REG^Regimen^L||2HRZE/4HR^Standard 6-month regimen^L||||||F
OBX|5|TX|TB_NOTES^Notes^L||Sputum conversion at month 2. Adherent to treatment. Scheduled for month 5 follow-up.||||||F
```

---

## 9. ORU^R01 - HIV programme data report

```
MSH|^~\&|DHIS2_HIS|BUFFALO_CITY_DH|HIV_SYS|EC_DOH|20260405150000||ORU^R01|DHIS00009|P|2.3
PID|||AGGREGATE^^^BUFFALO_CITY^AG||Buffalo City^District^Health^^Aggregate||||||||||||||||||||||||||||||EC
PV1||O|HIV^REPORT^1^BUFFALO_CITY_DH||||ADMIN^District HIV^^^^^Admin||||HIV||||A0||RPT20260405001
OBR|1|HIV20260405001^DHIS2_HIS||HIV_PROG^HIV Programme Report^L|||20260301000000|20260331235959||||||||ADMIN^District HIV^^^^^Admin||||||20260405150000|||F
OBX|1|NM|HIV_NEW^New HIV diagnoses^L||234|patients|||||F
OBX|2|NM|ART_INIT^ART initiations^L||218|patients|||||F
OBX|3|NM|VL_DONE^Viral loads done^L||1567|tests|||||F
OBX|4|NM|VL_SUPP^Viral loads suppressed^L||1389|patients|||||F
OBX|5|NM|LTFU^Lost to follow-up^L||45|patients|||||F
```

---

## 10. ADT^A04 - Birth registration for vital statistics

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_CAPE_TOWN_DH|VITAL_REG|WC_DOH|20260408100000||ADT^A04^ADT_A01|DHIS00010|P|2.3
EVN|A04|20260408100000
PID|||2604085432088^^^RSA_ID^NI||Daniels^Caleb^R^^Master||20260408|M|||15 Belgravia Road^^Athlone^^7764^ZAF||^^CP^0849876543||AF|S|||||||||||||ZAF
PV1||O|VITAL^BIRTH^1^CITY_OF_CAPE_TOWN_DH||||MW100^Petersen^Rashieda^^^Sr||||MAT||||A0||VIS20260408001|||||||||||||||||||||||||||20260408100000
```

---

## 11. ORU^R01 - Maternal death notification

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_JHB_DH|MDSR_SYS|NDOH|20260410090000||ORU^R01|DHIS00011|P|2.3
PID|||9012185432082^^^RSA_ID^NI||Sithole^Nontobeko^Z^^Ms||19901218|F|||33 Pretoria Road^^Midrand^^1685^ZAF||^^CP^0786543210||ZU|M|||||||||||||ZAF
PV1||I|MAT^ICU^1^CITY_OF_JHB_DH||||DOC850^Zwane^Thembinkosi^^^Dr||||OBS||||A0||ADM20260408001
OBR|1|MDSR20260410001^DHIS2_TRACKER||MAT_DEATH^Maternal Death Notification^L|||20260409210000|||||||||DOC850^Zwane^Thembinkosi^^^Dr||||||20260410090000|||F
OBX|1|CE|MAT_CAUSE^Primary Cause^L||15938005^Eclampsia^SCT||||||F
OBX|2|CE|MAT_TIME^Timing of Death^L||POSTPARTUM^Within 42 days postpartum^L||||||F
OBX|3|NM|MAT_GEST^Gestational Age at Delivery^L||36|weeks|||||F
OBX|4|TX|MAT_NOTES^Narrative^L||Emergency caesarean for eclampsia at 36 weeks. PPH post-delivery. Died in ICU 18 hours post-op.||||||F
```

---

## 12. ORU^R01 - Antimicrobial resistance surveillance

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_TSHWANE_DH|AMR_SYS|NICD|20260412110000||ORU^R01|DHIS00012|P|2.3
PID|||7705195432083^^^RSA_ID^NI||Lekoane^Mpho^S^^Mr||19770519|M|||28 Church Street^^Pretoria^^0002^ZAF||^^CP^0829876543||NS|M|||||||||||||ZAF
PV1||I|MED^ICU^3^CITY_OF_TSHWANE_DH||||DOC860^Van Rensburg^Marius^^^Dr||||MED||||A0||ADM20260410001
OBR|1|AMR20260412001^DHIS2_TRACKER||AMR^Antimicrobial Resistance Report^L|||20260411080000|||||||||DOC860^Van Rensburg^Marius^^^Dr||||||20260412110000|||F
OBX|1|CE|AMR_ORG^Organism^L||84210007^Klebsiella pneumoniae^SCT||||||F
OBX|2|CE|AMR_CARB^Carbapenem Resistance^L||260373001^Resistant^SCT||||||F
OBX|3|CE|AMR_MECH^Resistance Mechanism^L||NDM^NDM-1 producing^L||||||F
OBX|4|TX|AMR_NOTES^Notes^L||CRE isolated from blood culture. IPC measures in place. Reported to NICD GERMS-SA surveillance.||||||F
```

---

## 13. ORU^R01 - Monthly aggregate facility report with PDF

```
MSH|^~\&|DHIS2_HIS|ETHEKWINI_DH|REPORT_SYS|KZN_DOH|20260415160000||ORU^R01|DHIS00013|P|2.3
PID|||AGGREGATE^^^ETHEKWINI^AG||eThekwini^District^Health^^Aggregate||||||||||||||||||||||||||||||KZN
PV1||O|ADMIN^REPORT^1^ETHEKWINI_DH||||ADMIN^District Office^^^^^Admin||||PH||||A0||RPT20260415001
OBR|1|MNTH20260415001^DHIS2_HIS||MONTHLY^Monthly Facility Report^L|||20260301000000|20260331235959||||||||ADMIN^District Office^^^^^Admin||||||20260415160000|||F
OBX|1|NM|OPD_VISITS^OPD Headcount^L||45672|visits|||||F
OBX|2|NM|ANC_FIRST^ANC First Visits^L||1234|visits|||||F
OBX|3|NM|DELIVERIES^Deliveries in facility^L||567|deliveries|||||F
OBX|4|NM|IMMU_FULL^Fully immunized under-1^L||890|children|||||F
OBX|5|ED|PDF^Monthly Report PDF^DHIS2||^AP^^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCi9NZXRhZGF0YSAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tp||||||F
```

---

## 14. ADT^A04 - Death registration for vital statistics

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_CAPE_TOWN_DH|VITAL_REG|WC_DOH|20260418090000||ADT^A04^ADT_A01|DHIS00014|P|2.3
EVN|A04|20260418090000
PID|||5711155432086^^^RSA_ID^NI||Bosman^Willem^J^^Mr||19571115|M|||12 Kensington Crescent^^Kensington^^7405^ZAF||^^PH^0219876543||AF|M|||||||||||||ZAF
PV1||O|VITAL^DEATH^1^CITY_OF_CAPE_TOWN_DH||||DOC870^Du Toit^Christiaan^^^Dr||||PH||||A0||VIS20260418001|||||||||||||||||||||||||||20260418090000
```

---

## 15. ORU^R01 - Acute flaccid paralysis surveillance

```
MSH|^~\&|DHIS2_TRACKER|BUFFALO_CITY_DH|AFP_SYS|NICD|20260420100000||ORU^R01|DHIS00015|P|2.3
PID|||2111035432088^^^RSA_ID^NI||Gqirana^Yanga^N^^Master||20211103|M|||19 Oxford Street^^East London^^5201^ZAF||^^CP^0437890123||XH|S|||||||||||||ZAF
PV1||I|PAED^NEURO^2^BUFFALO_CITY_DH||||DOC880^Mlotshwa^Lindiwe^^^Dr||||PED||||A0||ADM20260419001
OBR|1|AFP20260420001^DHIS2_TRACKER||AFP^Acute Flaccid Paralysis Investigation^L|||20260419140000|||||||||DOC880^Mlotshwa^Lindiwe^^^Dr||||||20260420100000|||F
OBX|1|CE|AFP_TYPE^AFP Classification^L||CONFIRMED^Confirmed AFP case^L||||||F
OBX|2|NM|AFP_AGE^Age at onset^L||54|months|||||F
OBX|3|CE|AFP_VACC^Polio vaccination history^L||COMPLETE^4 doses OPV received^L||||||F
OBX|4|TX|AFP_NOTES^Investigation Notes^L||Sudden onset left leg weakness. Stool samples collected. Awaiting enterovirus culture at NICD.||||||F
```

---

## 16. ORU^R01 - Foodborne illness outbreak report

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_JHB_DH|OUTBREAK_SYS|NICD|20260422140000||ORU^R01|DHIS00016|P|2.3
PID|||OUTBREAK^^^CITY_OF_JHB^OB||City of Johannesburg^Outbreak^Investigation^^Cluster||||||||||||||||||||||||||||||GP
PV1||O|SURV^OUTBREAK^1^CITY_OF_JHB_DH||||DOC800^Nkambule^Phindile^^^Dr||||PH||||A0||VIS20260422001
OBR|1|OB20260422001^DHIS2_TRACKER||OUTBREAK^Outbreak Investigation^L|||20260420000000|||||||||DOC800^Nkambule^Phindile^^^Dr||||||20260422140000|||F
OBX|1|CE|OB_TYPE^Outbreak Type^L||255345001^Foodborne illness^SCT||||||F
OBX|2|NM|OB_CASES^Number of Cases^L||23|cases|||||F
OBX|3|TX|OB_SOURCE^Suspected Source^L||School feeding scheme. Common exposure: cooked chicken served 20 April. Stool samples pending.||||||F
OBX|4|CE|OB_STATUS^Outbreak Status^L||ACTIVE^Under investigation^L||||||F
```

---

## 17. ORU^R01 - Malaria elimination programme report

```
MSH|^~\&|DHIS2_HIS|VHEMBE_DH|MALARIA_SYS|LP_DOH|20260425100000||ORU^R01|DHIS00017|P|2.3
PID|||AGGREGATE^^^VHEMBE^AG||Vhembe^District^Health^^Aggregate||||||||||||||||||||||||||||||LP
PV1||O|MALARIA^REPORT^1^VHEMBE_DH||||ADMIN^District Malaria^^^^^Admin||||PH||||A0||RPT20260425001
OBR|1|MAL20260425001^DHIS2_HIS||MALARIA_ELIM^Malaria Elimination Report^L|||20260301000000|20260331235959||||||||ADMIN^District Malaria^^^^^Admin||||||20260425100000|||F
OBX|1|NM|MAL_CONF^Confirmed malaria cases^L||8|cases|||||F
OBX|2|NM|MAL_LOCAL^Locally acquired^L||2|cases|||||F
OBX|3|NM|MAL_IMPORT^Imported cases^L||6|cases|||||F
OBX|4|NM|MAL_IRS^Households sprayed (IRS)^L||12450|households|||||F
OBX|5|TX|MAL_NOTES^Programme Notes^L||Cases concentrated in Musina sub-district near Zimbabwe border. Cross-border movement main risk factor.||||||F
```

---

## 18. ORU^R01 - Surveillance dashboard export with image

```
MSH|^~\&|DHIS2_HIS|CITY_OF_JHB_DH|DASH_SYS|GP_DOH|20260428160000||ORU^R01|DHIS00018|P|2.3
PID|||AGGREGATE^^^CITY_OF_JHB^AG||City of Johannesburg^District^Health^^Aggregate||||||||||||||||||||||||||||||GP
PV1||O|ADMIN^DASHBOARD^1^CITY_OF_JHB_DH||||ADMIN^District Office^^^^^Admin||||PH||||A0||RPT20260428001
OBR|1|DASH20260428001^DHIS2_HIS||DASHBOARD^Surveillance Dashboard Export^L|||20260401000000|20260427235959||||||||ADMIN^District Office^^^^^Admin||||||20260428160000|||F
OBX|1|TX|DASH^Dashboard Summary^L||Weekly notifiable diseases trend for April 2026. TB notifications stable. No outbreaks declared.||||||F
OBX|2|ED|IMG^Surveillance Map Screenshot^DHIS2||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDABsSFBcUERsXFhceHBsgKEIrKCUlKFE6PTBCYFVlZF9VXVtqeJmBanGQc1tdhbWGkJ6jq62rZ4C8ybqmx5moq6T/2wBDARweHigjKE4rK06kbl1upKSkpKSk||||||F
```

---

## 19. ADT^A04 - Contact tracing registration

```
MSH|^~\&|DHIS2_TRACKER|CITY_OF_JHB_DH|TRACE_SYS|GP_DOH|20260312140000||ADT^A04^ADT_A01|DHIS00019|P|2.3
EVN|A04|20260312140000
PID|||9607145432085^^^RSA_ID^NI||Mothibi^Kabelo^R^^Mr||19960714|M|||22 Twist Street^^Hillbrow^^2001^ZAF||^^CP^0729876543||ST|S|||||||||||||ZAF
PV1||O|SURV^TRACE^1^CITY_OF_JHB_DH||||CHW001^Mabena^Nkosazana^^^CHW||||PH||||A0||VIS20260312001|||||||||||||||||||||||||||20260312140000
```

---

## 20. ORU^R01 - Notifiable medical conditions weekly summary

```
MSH|^~\&|DHIS2_HIS|CITY_OF_TSHWANE_DH|NICD_RCV|NDOH|20260430160000||ORU^R01|DHIS00020|P|2.3
PID|||AGGREGATE^^^CITY_OF_TSHWANE^AG||City of Tshwane^District^Health^^Aggregate||||||||||||||||||||||||||||||GP
PV1||O|SURV^NMC^1^CITY_OF_TSHWANE_DH||||ADMIN^District Office^^^^^Admin||||PH||||A0||RPT20260430001
OBR|1|NMC20260430001^DHIS2_HIS||NMC^Notifiable Medical Conditions Summary^L|||20260421000000|20260427235959||||||||ADMIN^District Office^^^^^Admin||||||20260430160000|||F
OBX|1|NM|NMC_TB^TB notifications^L||89|cases|||||F
OBX|2|NM|NMC_HIV^New HIV diagnoses^L||156|cases|||||F
OBX|3|NM|NMC_MEASLES^Measles cases^L||0|cases|||||F
OBX|4|NM|NMC_TYPHOID^Typhoid cases^L||2|cases|||||F
OBX|5|NM|NMC_RABIES^Rabies exposures^L||4|cases|||||F
OBX|6|NM|NMC_FOOD^Foodborne illness^L||11|cases|||||F
```
