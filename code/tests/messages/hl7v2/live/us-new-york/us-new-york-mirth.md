# Mirth Connect (NextGen) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission routed through Mirth at Strong Memorial Rochester

```
MSH|^~\&|MIRTH_CONNECT|STRONG_MEM_ROCH|ADT_DEST|URMC_HIE|20250305113000||ADT^A01^ADT_A01|MC20250305113000001|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250305113000||ADM_TRIGGER|MWILSON^Wilson^Marcus^^^REG|20250305112800|STRONG_MEM_ROCH
PID|1||MRN11022345^^^URMC^MR~178-42-9301^^^SSA^SS||Jankowski^Marek^W^^Mr.||19570318|M||2106-3^White^CDCREC|245 Genesee St^^Rochester^NY^14611^US^H||^PRN^PH^^^585^4439812|^WPN^PH^^^585^4436207||M^Married^HL70002|||178-42-9301|||N^Non-Hispanic^HL70189||||||N
PD1|||STRONG MEMORIAL HOSPITAL^^14642|1938274650^Calloway^Denise^R^^^MD^NPI||||||||N
NK1|1|Jankowski^Lidia^E^^Mrs.|SPO^Spouse^HL70063||^PRN^PH^^^585^4439813||EC^Emergency Contact^HL70131
PV1|1|I|CARD3^C308^A^STRONG_MEM^^^^CARD3||||1938274650^Calloway^Denise^R^^^MD^NPI|2047385761^Mehta^Rajiv^P^^^MD^NPI|CARD||||7|||1938274650^Calloway^Denise^R^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250305113000|||||V
PV2|||^Congestive heart failure exacerbation||||||||2|||||||||N|||||||||||A|20250305113000
IN1|1|EXCELLUS001^Excellus BlueCross BlueShield|53228|Excellus BCBS|PO Box 22999^^Rochester^NY^14692^US|||GRP427801|||20240101||||Jankowski^Marek^W|SEL^Self^HL70063|19570318|245 Genesee St^^Rochester^NY^14611^US|||||A|||||||M||||||EXC630482917
DG1|1||I50.9^Heart failure unspecified^ICD10|||A
DG1|2||I11.0^Hypertensive heart disease with heart failure^ICD10|||A
GT1|1||Jankowski^Marek^W^^Mr.||245 Genesee St^^Rochester^NY^14611^US|^PRN^PH^^^585^4439812|||||SEL^Self^HL70063
```

---

## 2. ADT^A08 - Patient update at Albany Medical Center

```
MSH|^~\&|MIRTH_CONNECT|ALBANY_MED|ADT_ROUTE|HIXNY|20250418152000||ADT^A08^ADT_A08|MC20250418152000002|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20250418152000||INS_UPD|SYSTEM^Mirth^Channel^^^SYS|20250418152000|ALBANY_MED
PID|1||MRN12033456^^^ALBANY_MED^MR||Washington^Denise^L^^Mrs.||19640802|F||2054-5^Black or African American^CDCREC|1245 Western Ave^^Albany^NY^12203^US^H||^PRN^PH^^^518^7219034|||M^Married^HL70002|||284-51-7603|||N^Non-Hispanic^HL70189||||||N
PD1|||ALBANY MEDICAL CENTER^^12208|3150948276^Fitzpatrick^Sean^D^^^MD^NPI||||||||N
NK1|1|Washington^Terrence^J^^Mr.|SPO^Spouse^HL70063||^PRN^PH^^^518^7219035||EC^Emergency Contact^HL70131
PV1|1|I|ONCO2^O215^A^ALBANY_MED^^^^ONCO2||||3150948276^Fitzpatrick^Sean^D^^^MD^NPI||ONC||||7|||3150948276^Fitzpatrick^Sean^D^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250415080000|||||V
PV2|||^Breast cancer chemotherapy cycle 3||||||||4|||||||||N|||||||||||A|20250418152000
IN1|1|CDPHP001^CDPHP|14563|Capital District Physicians Health Plan|500 Patroon Creek Blvd^^Albany^NY^12206^US|||GRP618340|||20240101||||Washington^Denise^L|SEL^Self^HL70063|19640802|1245 Western Ave^^Albany^NY^12203^US|||||A|||||||F||||||CDP720539184
DG1|1||C50.911^Malignant neoplasm of unspecified site of right female breast^ICD10|||A
```

---

## 3. ORM^O01 - Lab order routed to Quest via Mirth at White Plains Hospital

```
MSH|^~\&|MIRTH_CONNECT|WHITE_PLAINS_HOSP|LAB_ROUTE|QUEST_NY|20250528091500||ORM^O01^ORM_O01|MC20250528091500003|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN13044567^^^WPH^MR||Goldfarb^Nathan^E^^Mr.||19750920|M||2106-3^White^CDCREC|55 Mamaroneck Ave^^White Plains^NY^10601^US^H||^PRN^PH^^^914^3027481|||M^Married^HL70002|||392-60-8154|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|CLINIC_A^^^WHITE_PLAINS^^^^CLINIC||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||MED||||1|||4261830597^Ramirez^Gabriela^N^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250528090000|||||V
ORC|NW|ORD20250528001^WPH|LAB20250528001^QUEST_NY||CM||||20250528091500|DNURSE^Nurse^Diane^^^RN||4261830597^Ramirez^Gabriela^N^^^MD^NPI|WHITE_PLAINS_HOSP|||20250528091500||WPH^White Plains Hospital^L|55 Mamaroneck Ave^^White Plains^NY^10601^US|^PRN^PH^^^914^3027481
OBR|1|ORD20250528001^WPH|LAB20250528001^QUEST_NY|82306^Vitamin D 25-Hydroxy^CPT4|||20250528091500|||||||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||||||20250528091500|||F
OBR|2|ORD20250528002^WPH|LAB20250528002^QUEST_NY|82728^Ferritin^CPT4|||20250528091500|||||||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||||||20250528091500|||F
OBR|3|ORD20250528003^WPH|LAB20250528003^QUEST_NY|84439^Thyroxine Free^CPT4|||20250528091500|||||||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||||||20250528091500|||F
DG1|1||E55.9^Vitamin D deficiency unspecified^ICD10|||W
```

---

## 4. ORU^R01 - Lab results with embedded PDF via Mirth

```
MSH|^~\&|MIRTH_CONNECT|QUEST_NY|RESULTS_RECV|WHITE_PLAINS_HOSP|20250605143000||ORU^R01^ORU_R01|MC20250605143000004|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN13044567^^^WPH^MR||Goldfarb^Nathan^E^^Mr.||19750920|M||2106-3^White^CDCREC|55 Mamaroneck Ave^^White Plains^NY^10601^US^H||^PRN^PH^^^914^3027481|||M^Married^HL70002|||392-60-8154|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|CLINIC_A^^^WHITE_PLAINS^^^^CLINIC||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||MED||||1|||4261830597^Ramirez^Gabriela^N^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250528090000|||||V
ORC|RE|ORD20250528001^WPH|LAB20250605001^QUEST_NY||CM||||20250605143000|||4261830597^Ramirez^Gabriela^N^^^MD^NPI|WHITE_PLAINS_HOSP
OBR|1|ORD20250528001^WPH|LAB20250605001^QUEST_NY|82306^Vitamin D 25-Hydroxy^CPT4|||20250528091500|||||||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||||||20250605143000|||F
OBX|1|NM|1989-3^Vitamin D 25-Hydroxy^LN||18|ng/mL|30-100|L|||F|||20250604120000
OBX|2|NM|2276-4^Ferritin^LN||245|ng/mL|12-300|N|||F|||20250604120000
OBX|3|NM|3024-7^Thyroxine Free^LN||1.2|ng/dL|0.8-1.7|N|||F|||20250604120000
OBX|4|ED|LAB_PDF^Laboratory Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKExhYm9yYXRvcnkgUmVzdWx0cyBSZXBvcnQpCi9BdXRob3IgKFF1ZXN0IERpYWdub3N0aWNzIE5ldyBZb3JrKQovQ3JlYXRvciAoTmV4dEdlbiBDb25uZWN0IERvY3VtZW50IEhhbmRsZXIpCi9Qcm9kdWNlciAoTWlydGggQ29ubmVjdCBQREYgR2VuZXJhdG9yIHY0LjMpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTA2MDUxNDMwMDApCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9DYXRhbG9nCi9QYWdlcyAzIDAgUgo+PgplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzQgMCBSXQovQ291bnQgMQo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCg==||||||F|||20250605143000
```

---

## 5. VXU^V04 - Immunization update via Mirth to NYSIIS

```
MSH|^~\&|MIRTH_CONNECT|PEDIATRICS_WP|IMM_ROUTE|NYSIIS|20250615101500||VXU^V04^VXU_V04|MC20250615101500005|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN13055678^^^WPH^MR||Delgado^Isabella^C^^||20220315|F||2106-3^White^CDCREC|12 Barker Ave^^White Plains^NY^10601^US^H||^PRN^PH^^^914^6081743|||S^Single^HL70002||||||H^Hispanic^HL70189||||||N
NK1|1|Delgado^Marisol^T^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^914^6081743||EC^Emergency Contact^HL70131
PV1|1|O|PED_CLINIC^^^WHITE_PLAINS^^^^PED||||5839401726^Tanaka^Keiko^A^^^MD^NPI||PED||||1|||5839401726^Tanaka^Keiko^A^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250615100000|||||V
ORC|RE|ORD20250615001^WPH||||||||||5839401726^Tanaka^Keiko^A^^^MD^NPI|PEDIATRICS_WP
RXA|0|1|20250615101500|20250615101500|141^Influenza Injectable Preservative Free^CVX|0.5|mL|IM^Intramuscular^NCIT||||||Y5842AB||SKB^GlaxoSmithKline^MVX|||CP^Complete^NIP001
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Program Eligibility^LN||V02^VFC eligible Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|2|TX|30956-7^Vaccine Type^LN||Influenza seasonal injectable preservative free||||||F
```

---

## 6. SIU^S12 - Scheduling at Buffalo General Medical Center

```
MSH|^~\&|MIRTH_CONNECT|BUFFALO_GENERAL|SCHED_ROUTE|KALEIDA_SCHED|20250708140000||SIU^S12^SIU_S12|MC20250708140000006|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20250708001^BGMC||||||SURGERY^Pre-Operative Assessment^KALEIDA_APPT|||60|MIN|^^60^20250722090000^20250722100000|||||6704218359^Kowalczyk^Adam^R^^^MD^NPI|^PRN^PH^^^716^8024617|100 High St^^Buffalo^NY^14203^US||CONFIRMED
PID|1||MRN14066789^^^KALEIDA^MR||Baptiste^Reginald^C^^Mr.||19630411|M||2054-5^Black or African American^CDCREC|1832 Seneca St^^Buffalo^NY^14210^US^H||^PRN^PH^^^716^3419087|||M^Married^HL70002|||541-73-8206|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|PREOP^^^BUFFALO_GENERAL^^^^PREOP||||6704218359^Kowalczyk^Adam^R^^^MD^NPI||SURG||||1|||6704218359^Kowalczyk^Adam^R^^^MD^NPI|PRE||SELF|||||||||||||||AI|||20250708140000|||||V
RGS|1||SURG_PREOP^Pre-Operative Assessment
AIS|1||PREOP_EVAL^Pre-Operative Evaluation^KALEIDA_APPT|20250722090000|||60|MIN
AIP|1||6704218359^Kowalczyk^Adam^R^^^MD^NPI|PS^Primary Surgeon^HL70286
AIL|1||PREOP_CLINIC^Room 201^Buffalo General Pre-Op^^BUFFALO_GENERAL|W
DG1|1||M17.11^Primary osteoarthritis right knee^ICD10|||A
```

---

## 7. ORU^R01 - Chemistry results routed via Mirth at Syracuse

```
MSH|^~\&|MIRTH_CONNECT|UPSTATE_MED_CTR|RESULTS_RECV|UPSTATE_EHR|20250812141500||ORU^R01^ORU_R01|MC20250812141500007|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN15077890^^^UPSTATE^MR||Okafor^Amara^N^^Mrs.||19820215|F||2054-5^Black or African American^CDCREC|312 Comstock Ave^^Syracuse^NY^13210^US^H||^PRN^PH^^^315^6130287|||M^Married^HL70002|||637-84-2905|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|ENDO_CLINIC^^^UPSTATE_MED^^^^ENDO||||7518302946^Donahue^Liam^F^^^MD^NPI||ENDO||||1|||7518302946^Donahue^Liam^F^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250812090000|||||V
ORC|RE|ORD20250812001^UPSTATE|LAB20250812001^UPSTATE_LAB||CM||||20250812141500|||7518302946^Donahue^Liam^F^^^MD^NPI|UPSTATE_MED_CTR
OBR|1|ORD20250812001^UPSTATE|LAB20250812001^UPSTATE_LAB|82947^Glucose Fasting^CPT4|||20250812080000|||||||||7518302946^Donahue^Liam^F^^^MD^NPI||||||20250812141500|||F
OBX|1|NM|1558-6^Fasting Glucose^LN||142|mg/dL|74-100|H|||F|||20250812120000
OBX|2|NM|4548-4^Hemoglobin A1c^LN||7.8|%|<5.7|H|||F|||20250812120000
OBX|3|NM|14749-6^Glucose 2 Hr Post 75g Glucose^LN||210|mg/dL|<140|H|||F|||20250812120000
OBX|4|NM|14771-0^Fasting Insulin^LN||28.5|uIU/mL|2.6-24.9|H|||F|||20250812120000
OBX|5|NM|56540-8^C-Peptide Fasting^LN||4.2|ng/mL|1.1-4.4|N|||F|||20250812120000
```

---

## 8. ADT^A01 - Admission via Mirth at Westchester Medical Center

```
MSH|^~\&|MIRTH_CONNECT|WESTCHESTER_MED|ADT_DEST|WMCHEALTH_HIE|20250905183000||ADT^A01^ADT_A01|MC20250905183000008|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250905183000||ADM_TRIGGER|TCARTER^Carter^Tamika^^^REG|20250905182500|WESTCHESTER_MED
PID|1||MRN16088901^^^WMC^MR||Prescott^Dwayne^K^^Mr.||19790918|M||2054-5^Black or African American^CDCREC|89 South Broadway^^Yonkers^NY^10701^US^H||^PRN^PH^^^914^2087341|||S^Single^HL70002|||740-85-2163|||N^Non-Hispanic^HL70189||||||N
PD1|||WESTCHESTER MEDICAL CENTER^^10595|8362041597^DiNapoli^Vincent^F^^^MD^NPI||||||||N
NK1|1|Prescott^Shanice^A^^Ms.|SIS^Sister^HL70063||^PRN^PH^^^914^2087342||EC^Emergency Contact^HL70131
PV1|1|I|TRAUMA^^^WESTCHESTER_MED^^^^TRAUMA||||8362041597^DiNapoli^Vincent^F^^^MD^NPI|9071456283^Krishnamurthy^Priya^S^^^MD^NPI|TRA||||1|||8362041597^DiNapoli^Vincent^F^^^MD^NPI|EM||SELF|||||||||||||||AI|||20250905183000|||||V
PV2|||^Motorcycle accident with multiple injuries||||||||1|||||||||Y|||||||||||A|20250905183000
IN1|1|AETNA001^Aetna|62308|Aetna Inc|151 Farmington Ave^^Hartford^CT^06156^US|||GRP502718|||20240301||||Prescott^Dwayne^K|SEL^Self^HL70063|19790918|89 South Broadway^^Yonkers^NY^10701^US|||||A|||||||M||||||AET839207154
DG1|1||S72.301A^Unspecified fracture of shaft of right femur^ICD10|||A
DG1|2||S27.0XXA^Traumatic pneumothorax initial^ICD10|||A
DG1|3||S06.5X0A^Traumatic subdural hemorrhage without LOC^ICD10|||W
GT1|1||Prescott^Dwayne^K^^Mr.||89 South Broadway^^Yonkers^NY^10701^US|^PRN^PH^^^914^2087341|||||SEL^Self^HL70063
```

---

## 9. ORU^R01 - Radiology results at Strong Memorial

```
MSH|^~\&|MIRTH_CONNECT|URMC_RAD|RESULTS_RECV|STRONG_MEM_ROCH|20250920163000||ORU^R01^ORU_R01|MC20250920163000009|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN11022345^^^URMC^MR||Jankowski^Marek^W^^Mr.||19570318|M||2106-3^White^CDCREC|245 Genesee St^^Rochester^NY^14611^US^H||^PRN^PH^^^585^4439812|||M^Married^HL70002|||178-42-9301|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|CARD3^C308^A^STRONG_MEM^^^^CARD3||||1938274650^Calloway^Denise^R^^^MD^NPI||CARD||||7|||1938274650^Calloway^Denise^R^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250305113000|||||V
ORC|RE|ORD20250920001^URMC|RAD20250920001^URMC_RAD||CM||||20250920163000|||1938274650^Calloway^Denise^R^^^MD^NPI|STRONG_MEM_ROCH
OBR|1|ORD20250920001^URMC|RAD20250920001^URMC_RAD|93307^Echocardiogram Complete^CPT4|||20250920100000|||||||||1938274650^Calloway^Denise^R^^^MD^NPI||||||20250920163000|||F
OBX|1|TX|93307^Echocardiogram^CPT4||LEFT VENTRICLE: Moderately dilated. Ejection fraction 30-35% by Simpson biplane method. Global hypokinesis with relative preservation of basal segments. Grade II diastolic dysfunction.||||||F|||20250920150000
OBX|2|TX|93307^Echocardiogram^CPT4||VALVES: Mild mitral regurgitation. Mild tricuspid regurgitation with estimated RVSP 42 mmHg. Aortic valve trileaflet without stenosis.||||||F|||20250920150000
OBX|3|TX|93307^Echocardiogram^CPT4||IMPRESSION: Moderately reduced LV systolic function with EF 30-35%. Moderate pulmonary hypertension. Recommend cardiology follow-up for heart failure management optimization.||||||F|||20250920150000
```

---

## 10. ORM^O01 - Pharmacy order via Mirth at Albany Med

```
MSH|^~\&|MIRTH_CONNECT|ALBANY_MED|PHARM_ROUTE|ALBANY_PHARM|20251003083000||ORM^O01^ORM_O01|MC20251003083000010|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN12033456^^^ALBANY_MED^MR||Washington^Denise^L^^Mrs.||19640802|F||2054-5^Black or African American^CDCREC|1245 Western Ave^^Albany^NY^12203^US^H||^PRN^PH^^^518^7219034|||M^Married^HL70002|||284-51-7603|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|ONCO2^O215^A^ALBANY_MED^^^^ONCO2||||3150948276^Fitzpatrick^Sean^D^^^MD^NPI||ONC||||7|||3150948276^Fitzpatrick^Sean^D^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250415080000|||||V
ORC|NW|ORD20251003001^ALBANY_MED|PHARM20251003001^ALBANY_PHARM||SC||||20251003083000|RNURSE^Nurse^Roselyn^^^RN||3150948276^Fitzpatrick^Sean^D^^^MD^NPI|ALBANY_MED|||20251003083000
OBR|1|ORD20251003001^ALBANY_MED|PHARM20251003001^ALBANY_PHARM|RX003^Chemotherapy Order^L|||20251003083000|||||||||3150948276^Fitzpatrick^Sean^D^^^MD^NPI
RXO|224905^Doxorubicin 60mg/m2 IV^RXNORM||90|mg||IV|ONCE^^^ONCE||G
RXR|IV^Intravenous^HL70162|CVL^Central Venous Line^HL70163
RXO|56946^Cyclophosphamide 600mg/m2 IV^RXNORM||900|mg||IV|ONCE^^^ONCE||G
RXR|IV^Intravenous^HL70162|CVL^Central Venous Line^HL70163
DG1|1||C50.911^Malignant neoplasm of unspecified site of right female breast^ICD10|||A
```

---

## 11. VXU^V04 - COVID vaccination to NYSIIS via Mirth

```
MSH|^~\&|MIRTH_CONNECT|RITE_AID_NY|IMM_ROUTE|NYSIIS|20251015141500||VXU^V04^VXU_V04|MC20251015141500011|P|2.5.1|||AL|NE||ASCII|||
PID|1||PAT20251015001^^^RITE_AID^MR||Espinal^Francisco^R^^Mr.||19520820|M||2106-3^White^CDCREC|4520 Broadway^^New York^NY^10040^US^H||^PRN^PH^^^212^7304198|||M^Married^HL70002|||815-93-4027|||H^Hispanic^HL70189||||||N
PV1|1|O|PHARMACY^^^RITE_AID^^^^PHARM||||9246801357^Nakamura^Yuki^H^^^PharmD^NPI||PHARM||||1|||9246801357^Nakamura^Yuki^H^^^PharmD^NPI|OP||SELF|||||||||||||||AI|||20251015140000|||||V
ORC|RE|ORD20251015001^RITE_AID||||||||||9246801357^Nakamura^Yuki^H^^^PharmD^NPI|RITE_AID_NY
RXA|0|1|20251015141500|20251015141500|308^COVID-19 Pfizer-BioNTech Updated 2025-2026^CVX|0.3|mL|IM^Intramuscular^NCIT||||||Y9823CD||PFR^Pfizer^MVX|||CP^Complete^NIP001
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine Funding Program Eligibility^LN||V01^Not VFC eligible^HL70064||||||F
OBX|2|DT|29768-9^Date Vaccine Information Statement Published^LN||20250901||||||F
OBX|3|CE|69764-9^Document Type^LN||253088698300026411^Pfizer-BioNTech COVID-19 Vaccine EUA^L||||||F
```

---

## 12. ADT^A08 - Patient demographics update via SHIN-NY

```
MSH|^~\&|MIRTH_CONNECT|SHIN_NY_HUB|ADT_ROUTE|STATEWIDE_MPI|20251028112000||ADT^A08^ADT_A08|MC20251028112000012|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20251028112000||MPI_SYNC|SYSTEM^Mirth^SHINNY^^^SYS|20251028112000|SHIN_NY_HUB
PID|1||MRN11022345^^^URMC^MR~MRN_ALB_99887^^^ALBANY_MED^MR~SHINNY_EMPI_990011^^^SHIN_NY^PI||Jankowski^Marek^W^^Mr.||19570318|M||2106-3^White^CDCREC|245 Genesee St^^Rochester^NY^14611^US^H||^PRN^PH^^^585^4439812|||M^Married^HL70002|||178-42-9301|||N^Non-Hispanic^HL70189||||||N
PD1|||STRONG MEMORIAL HOSPITAL^^14642|1938274650^Calloway^Denise^R^^^MD^NPI||||||||N
PV1|1|N||||||||||||||||||||||||||||||||||||||||||||||V
```

---

## 13. ORU^R01 - Prenatal screening results via Mirth

```
MSH|^~\&|MIRTH_CONNECT|PERINAT_LAB|RESULTS_RECV|BUFFALO_GENERAL|20251105153000||ORU^R01^ORU_R01|MC20251105153000013|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN14078901^^^KALEIDA^MR||Sobczak^Katarzyna^A^^Mrs.||19940823|F||2106-3^White^CDCREC|78 Elmwood Ave^^Buffalo^NY^14201^US^H||^PRN^PH^^^716^5083196|||M^Married^HL70002|||762-80-4139|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|OB_CLINIC^^^BUFFALO_GENERAL^^^^OB||||0394127586^Brennan^Colleen^T^^^MD^NPI||OB||||1|||0394127586^Brennan^Colleen^T^^^MD^NPI|OP||SELF|||||||||||||||AI|||20251105090000|||||V
ORC|RE|ORD20251105001^KALEIDA|LAB20251105001^PERINAT_LAB||CM||||20251105153000|||0394127586^Brennan^Colleen^T^^^MD^NPI|BUFFALO_GENERAL
OBR|1|ORD20251105001^KALEIDA|LAB20251105001^PERINAT_LAB|81420^Cell-Free DNA Prenatal Screen^CPT4|||20251028091500|||||||||0394127586^Brennan^Colleen^T^^^MD^NPI||||||20251105153000|||F
OBX|1|TX|99051^Fetal Fraction^L||12.5%||>4%|N|||F|||20251105120000
OBX|2|TX|99052^Trisomy 21 Risk^L||Low Risk (1:>10000)||Low Risk|N|||F|||20251105120000
OBX|3|TX|99053^Trisomy 18 Risk^L||Low Risk (1:>10000)||Low Risk|N|||F|||20251105120000
OBX|4|TX|99054^Trisomy 13 Risk^L||Low Risk (1:>10000)||Low Risk|N|||F|||20251105120000
OBX|5|TX|99055^Sex Chromosome Aneuploidy^L||No aneuploidy detected||No aneuploidy|N|||F|||20251105120000
OBX|6|TX|99056^Fetal Sex^L||Female||||||F|||20251105120000
OBX|7|TX|99057^Interpretation^L||NEGATIVE SCREEN: All results within normal limits. Standard obstetric care recommended.||||||F|||20251105120000
```

---

## 14. ADT^A01 - Pediatric admission via Mirth at Maria Fareri

```
MSH|^~\&|MIRTH_CONNECT|MARIA_FARERI|ADT_DEST|WMCHEALTH_HIE|20251120192000||ADT^A01^ADT_A01|MC20251120192000014|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20251120192000||ADM_TRIGGER|APETROV^Petrov^Anna^^^REG|20251120191500|MARIA_FARERI
PID|1||MRN17089012^^^MARIA_FARERI^MR||Cespedes^Alejandro^D^^||20180702|M||2106-3^White^CDCREC|234 Warburton Ave^^Yonkers^NY^10701^US^H||^PRN^PH^^^914^7250483|||S^Single^HL70002||||||H^Hispanic^HL70189||||||N
NK1|1|Cespedes^Xiomara^P^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^914^7250483||EC^Emergency Contact^HL70131
NK1|2|Cespedes^Ernesto^R^^Mr.|FTH^Father^HL70063||^PRN^PH^^^914^7250484||EC^Emergency Contact^HL70131
PV1|1|I|PICU^PICU04^A^MARIA_FARERI^^^^PICU||||1627503894^Abramowitz^Rachel^G^^^MD^NPI|2438619705^Santiago^Diego^M^^^MD^NPI|PED||||1|||1627503894^Abramowitz^Rachel^G^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251120192000|||||V
PV2|||^Status asthmaticus||||||||1|||||||||Y|||||||||||A|20251120192000
IN1|1|FIDEL_CHP001^Fidelis Care Child Health Plus|28211|Fidelis Care NY|95-25 Queens Blvd^^Rego Park^NY^11374^US|||||||20250101||||Cespedes^Xiomara^P|MTH^Mother^HL70063|19900415|234 Warburton Ave^^Yonkers^NY^10701^US|||||A|||||||M||||||FID_CHP_903271
DG1|1||J46^Status asthmaticus^ICD10|||A
GT1|1||Cespedes^Xiomara^P^^Mrs.||234 Warburton Ave^^Yonkers^NY^10701^US|^PRN^PH^^^914^7250483|||||MTH^Mother^HL70063
```

---

## 15. ORU^R01 - Microbiology via Mirth at Stony Brook

```
MSH|^~\&|MIRTH_CONNECT|STONY_BROOK_LAB|RESULTS_RECV|STONY_BROOK_EHR|20251205101500||ORU^R01^ORU_R01|MC20251205101500015|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN18090123^^^STONY_BROOK^MR||Ferrante^Giacomo^V^^Mr.||19480512|M||2106-3^White^CDCREC|45 Nicolls Rd^^Stony Brook^NY^11790^US^H||^PRN^PH^^^631^4087253|||W^Widowed^HL70002|||853-06-1472|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|MED4^M412^A^STONY_BROOK^^^^MED4||||3095184267^Blackwell^Trenton^H^^^MD^NPI||MED||||7|||3095184267^Blackwell^Trenton^H^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251202080000|||||V
ORC|RE|ORD20251205001^STONY_BROOK|MICRO20251205001^STONY_BROOK_LAB||CM||||20251205101500|||3095184267^Blackwell^Trenton^H^^^MD^NPI|STONY_BROOK
OBR|1|ORD20251205001^STONY_BROOK|MICRO20251205001^STONY_BROOK_LAB|87086^Urine Culture^CPT4|||20251202100000|||||||||3095184267^Blackwell^Trenton^H^^^MD^NPI||||||20251205101500|||F
OBX|1|TX|87086^Urine Culture^CPT4||Source: Clean catch midstream urine||||||F|||20251205090000
OBX|2|TX|87086^Urine Culture^CPT4||Organism: Escherichia coli||||||F|||20251205090000
OBX|3|TX|87086^Urine Culture^CPT4||Colony Count: >100,000 CFU/mL||||||F|||20251205090000
OBX|4|TX|87181^Antibiotic Susceptibility^CPT4||Ampicillin: Resistant||||||F|||20251205090000
OBX|5|TX|87181^Antibiotic Susceptibility^CPT4||Ciprofloxacin: Susceptible (MIC 0.25)||||||F|||20251205090000
OBX|6|TX|87181^Antibiotic Susceptibility^CPT4||Nitrofurantoin: Susceptible (MIC 16)||||||F|||20251205090000
OBX|7|TX|87181^Antibiotic Susceptibility^CPT4||Trimethoprim-Sulfamethoxazole: Susceptible||||||F|||20251205090000
OBX|8|TX|87181^Antibiotic Susceptibility^CPT4||Ceftriaxone: Susceptible (MIC 0.5)||||||F|||20251205090000
```

---

## 16. SIU^S12 - Telehealth appointment via Mirth

```
MSH|^~\&|MIRTH_CONNECT|TELEMED_WP|SCHED_ROUTE|WPH_SCHED|20251218140000||SIU^S12^SIU_S12|MC20251218140000016|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20251218001^WPH||||||TELEMED^Telehealth Visit^WPH_APPT|||30|MIN|^^30^20251223140000^20251223143000|||||4261830597^Ramirez^Gabriela^N^^^MD^NPI|^PRN^PH^^^914^3027481|55 Mamaroneck Ave^^White Plains^NY^10601^US||CONFIRMED
PID|1||MRN13044567^^^WPH^MR||Goldfarb^Nathan^E^^Mr.||19750920|M||2106-3^White^CDCREC|55 Mamaroneck Ave^^White Plains^NY^10601^US^H||^PRN^PH^^^914^3027481|||M^Married^HL70002|||392-60-8154|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|TELEMED^^^WHITE_PLAINS^^^^TELEMED||||4261830597^Ramirez^Gabriela^N^^^MD^NPI||MED||||1|||4261830597^Ramirez^Gabriela^N^^^MD^NPI|OP||SELF|||||||||||||||AI|||20251218140000|||||V
RGS|1||TELEMED_SLOT^Telehealth Slot
AIS|1||FOLLOWUP^Follow-Up Telehealth^WPH_APPT|20251223140000|||30|MIN
AIP|1||4261830597^Ramirez^Gabriela^N^^^MD^NPI|AD^Admitting^HL70286
AIL|1||TELEMED^Virtual Room^White Plains Telehealth^^WHITE_PLAINS|W
```

---

## 17. ORM^O01 - Referral order via Mirth at Rochester

```
MSH|^~\&|MIRTH_CONNECT|URMC_PRIMARY|REF_ROUTE|URMC_SPECIALTY|20260105091500||ORM^O01^ORM_O01|MC20260105091500017|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN11100234^^^URMC^MR||Bhatia^Vikram^S^^Mr.||19680415|M||2028-9^Asian^CDCREC|1200 East Ave^^Rochester^NY^14607^US^H||^PRN^PH^^^585^7201436|||M^Married^HL70002|||904-17-5238|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|PCP_CLINIC^^^URMC_PRIMARY^^^^PCP||||4705912836^O'Brien^Siobhan^M^^^MD^NPI||MED||||1|||4705912836^O'Brien^Siobhan^M^^^MD^NPI|OP||SELF|||||||||||||||AI|||20260105090000|||||V
ORC|NW|ORD20260105001^URMC_PCP|REF20260105001^URMC_SPECIALTY||SC||||20260105091500|||4705912836^O'Brien^Siobhan^M^^^MD^NPI|URMC_PRIMARY|||20260105091500||URMC^University of Rochester Medical Center^L|1200 East Ave^^Rochester^NY^14607^US|^PRN^PH^^^585^7201436
OBR|1|ORD20260105001^URMC_PCP|REF20260105001^URMC_SPECIALTY|99244^Office Consultation Level 4^CPT4|||20260105091500|||||||||4705912836^O'Brien^Siobhan^M^^^MD^NPI|||||5290386147^Whitfield^Gerard^T^^^MD^NPI|20260105091500|||F||||||^Persistent low back pain with radiculopathy
DG1|1||M54.16^Radiculopathy lumbar region^ICD10|||A
DG1|2||M51.16^Intervertebral disc degeneration lumbar region^ICD10|||A
```

---

## 18. ORU^R01 - Pathology with embedded PDF via Mirth

```
MSH|^~\&|MIRTH_CONNECT|ALBANY_PATH|RESULTS_RECV|ALBANY_MED|20260120160000||ORU^R01^ORU_R01|MC20260120160000018|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN12033456^^^ALBANY_MED^MR||Washington^Denise^L^^Mrs.||19640802|F||2054-5^Black or African American^CDCREC|1245 Western Ave^^Albany^NY^12203^US^H||^PRN^PH^^^518^7219034|||M^Married^HL70002|||284-51-7603|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|ONCO2^O215^A^ALBANY_MED^^^^ONCO2||||3150948276^Fitzpatrick^Sean^D^^^MD^NPI||ONC||||7|||3150948276^Fitzpatrick^Sean^D^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250415080000|||||V
ORC|RE|ORD20260120001^ALBANY_MED|PATH20260120001^ALBANY_PATH||CM||||20260120160000|||3150948276^Fitzpatrick^Sean^D^^^MD^NPI|ALBANY_MED
OBR|1|ORD20260120001^ALBANY_MED|PATH20260120001^ALBANY_PATH|88305^Surgical Pathology^CPT4|||20260115100000|||||||||3150948276^Fitzpatrick^Sean^D^^^MD^NPI||||||20260120160000|||F
OBX|1|TX|88305^Pathology^CPT4||SPECIMEN: Right breast, lumpectomy. GROSS: Received fresh is an oriented lumpectomy specimen measuring 6.5 x 4.2 x 3.8cm. Gross tumor identified in central portion measuring 1.8cm.||||||F|||20260120140000
OBX|2|TX|88305^Pathology^CPT4||MICROSCOPIC: Invasive ductal carcinoma, grade 2 (Nottingham score 6/9). Margins clear (closest margin 5mm superior). 0/3 sentinel lymph nodes positive for metastatic carcinoma.||||||F|||20260120140000
OBX|3|TX|88305^Pathology^CPT4||IHC: ER positive (95%), PR positive (80%), HER2 negative (1+), Ki-67 15%.||||||F|||20260120140000
OBX|4|TX|88305^Pathology^CPT4||STAGE: pT1c pN0 - Stage IA. Oncotype DX recommended for recurrence score.||||||F|||20260120140000
OBX|5|ED|PATH_PDF^Surgical Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFN1cmdpY2FsIFBhdGhvbG9neSBSZXBvcnQgLSBCcmVhc3QgTHVtcGVjdG9teSkKL0F1dGhvciAoQWxiYW55IE1lZGljYWwgQ2VudGVyIFBhdGhvbG9neSkKL0NyZWF0b3IgKE5leHRHZW4gQ29ubmVjdCBEb2N1bWVudCBIYW5kbGVyKQovUHJvZHVjZXIgKE1pcnRoIENvbm5lY3QgUERGIEdlbmVyYXRvciB2NC41KQovQ3JlYXRpb25EYXRlIChEOjIwMjYwMTIwMTYwMDAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgo+PgplbmRvYmoK||||||F|||20260120160000
```

---

## 19. ADT^A01 - Admission via Mirth at Saratoga Hospital

```
MSH|^~\&|MIRTH_CONNECT|SARATOGA_HOSP|ADT_DEST|HIXNY|20260202143000||ADT^A01^ADT_A01|MC20260202143000019|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20260202143000||ADM_TRIGGER|KJACKSON^Jackson^Karen^^^REG|20260202142800|SARATOGA_HOSP
PID|1||MRN19100345^^^SARATOGA^MR||Thornton^Gerald^W^^Mr.||19510923|M||2106-3^White^CDCREC|56 Lincoln Ave^^Saratoga Springs^NY^12866^US^H||^PRN^PH^^^518^2084671|||M^Married^HL70002|||021-38-7452|||N^Non-Hispanic^HL70189||||||N
PD1|||SARATOGA HOSPITAL^^12866|5831640279^Lindstrom^Erik^J^^^MD^NPI||||||||N
NK1|1|Thornton^Maureen^B^^Mrs.|SPO^Spouse^HL70063||^PRN^PH^^^518^2084672||EC^Emergency Contact^HL70131
PV1|1|I|MED2^M212^A^SARATOGA^^^^MED2||||5831640279^Lindstrom^Erik^J^^^MD^NPI||MED||||7|||5831640279^Lindstrom^Erik^J^^^MD^NPI|IN||SELF|||||||||||||||AI|||20260202143000|||||V
PV2|||^COPD exacerbation with acute respiratory failure||||||||1|||||||||N|||||||||||A|20260202143000
IN1|1|MEDICARE001^Medicare|00299|Medicare|PO Box 790000^^St Louis^MO^63179^US|||||||19810923||||Thornton^Gerald^W|SEL^Self^HL70063|19510923|56 Lincoln Ave^^Saratoga Springs^NY^12866^US|||||A|||||||M||||||MCR4180293756B
IN1|2|EXCELLUS001^Excellus BCBS|53228|Excellus BCBS|PO Box 22999^^Rochester^NY^14692^US|||GRP620174|||20200101||||Thornton^Gerald^W|SEL^Self^HL70063|19510923|56 Lincoln Ave^^Saratoga Springs^NY^12866^US|||||A|||||||M||||||EXC850174632
DG1|1||J44.1^COPD with acute exacerbation^ICD10|||A
DG1|2||J96.00^Acute respiratory failure unspecified^ICD10|||A
GT1|1||Thornton^Gerald^W^^Mr.||56 Lincoln Ave^^Saratoga Springs^NY^12866^US|^PRN^PH^^^518^2084671|||||SEL^Self^HL70063
```

---

## 20. ORU^R01 - ABG results via Mirth at Saratoga

```
MSH|^~\&|MIRTH_CONNECT|SARATOGA_LAB|RESULTS_RECV|SARATOGA_EHR|20260203061500||ORU^R01^ORU_R01|MC20260203061500020|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN19100345^^^SARATOGA^MR||Thornton^Gerald^W^^Mr.||19510923|M||2106-3^White^CDCREC|56 Lincoln Ave^^Saratoga Springs^NY^12866^US^H||^PRN^PH^^^518^2084671|||M^Married^HL70002|||021-38-7452|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|MED2^M212^A^SARATOGA^^^^MED2||||5831640279^Lindstrom^Erik^J^^^MD^NPI||MED||||7|||5831640279^Lindstrom^Erik^J^^^MD^NPI|IN||SELF|||||||||||||||AI|||20260202143000|||||V
ORC|RE|ORD20260203001^SARATOGA|LAB20260203001^SARATOGA_LAB||CM||||20260203061500|||5831640279^Lindstrom^Erik^J^^^MD^NPI|SARATOGA_HOSP
OBR|1|ORD20260203001^SARATOGA|LAB20260203001^SARATOGA_LAB|82803^Arterial Blood Gas^CPT4|||20260203050000|||||||||5831640279^Lindstrom^Erik^J^^^MD^NPI||||||20260203061500|||F
OBX|1|NM|2744-1^pH Arterial^LN||7.29||7.35-7.45|L|||F|||20260203055000
OBX|2|NM|2019-8^pCO2 Arterial^LN||62|mmHg|35-45|HH|||F|||20260203055000
OBX|3|NM|2703-7^pO2 Arterial^LN||55|mmHg|80-100|L|||F|||20260203055000
OBX|4|NM|1960-4^Bicarbonate Arterial^LN||28|mmol/L|22-26|H|||F|||20260203055000
OBX|5|NM|2708-6^O2 Saturation Arterial^LN||86|%|95-100|L|||F|||20260203055000
OBX|6|NM|1925-7^Base Excess^LN||2.5|mmol/L|-2 to 2|H|||F|||20260203055000
OBX|7|TX|INTERPRETATION^ABG Interpretation^L||Acute on chronic respiratory acidosis with hypoxemia. Consistent with COPD exacerbation. Recommend BiPAP and bronchodilator therapy.||||||F|||20260203061500
```
