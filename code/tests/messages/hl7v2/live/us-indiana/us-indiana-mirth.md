# Mirth Connect (NextGen) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission routed through Mirth from Parkview Health

```
MSH|^~\&|MIRTH_ENGINE|PKV_ROUTER|DEST_SYS|IHIE|20250310073000||ADT^A01^ADT_A01|MIRTH00001234|P|2.4|||AL|NE
EVN|A01|20250310073000|||CARDMD^Garrison^Terrence^R^^^MD
PID|1||PKV_MRN60038291^^^PKV^MR||Engstrom^Dale^Robert||19580614|M|||2917 Calhoun St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4267193||ENG|M|MET|SSN314-58-7293^^^SS|||||||||||N
NK1|1|Engstrom^Colleen^Faye|SPO|2917 Calhoun St^^Fort Wayne^IN^46802^US|^PRN^PH^^1^260^4267194
PV1|1|I|CARDIO^402^A^PKV_RANDALLIA^^^^CARDIO||||CARDMD^Garrison^Terrence^R^^^MD|INTMD^Pham^Derek^C^^^MD||CAR|||7|||CARDMD^Garrison^Terrence^R^^^MD|IP||||||||||||||||||PKV_RANDALLIA|||||20250310073000
PV2|||^Unstable angina
IN1|1|ANTHEM1^Anthem BCBS|ANT001|Anthem Blue Cross Blue Shield||||||||20240101|20251231|||PPO|Engstrom^Dale^Robert|Self|19580614|2917 Calhoun St^^Fort Wayne^IN^46802^US
DG1|1||I20.0^Unstable angina^ICD10|||A
```

---

## 2. ORU^R01 - Lab result transformed and routed by Mirth

```
MSH|^~\&|MIRTH_ENGINE|LAB_ROUTER|PCP_EMR|DR_GARRISON|20250311153000||ORU^R01^ORU_R01|MIRTH00004567|P|2.4|||AL|NE
PID|1||PKV_MRN60038291^^^PKV^MR||Engstrom^Dale^Robert||19580614|M|||2917 Calhoun St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4267193
PV1|1|I|CARDIO^402^A^PKV_RANDALLIA||||CARDMD^Garrison^Terrence^R^^^MD
ORC|RE|MIRTH_ORD001|MIRTH_RES001||CM||||20250311152500|||CARDMD^Garrison^Terrence^R^^^MD
OBR|1|MIRTH_ORD001|MIRTH_RES001|2823-3^BNP^LN|||20250311140000||||||||CARDMD^Garrison^Terrence^R^^^MD||||||20250311153000|||F
OBX|1|NM|42637-9^BNP Natriuretic Peptide^LN||850|pg/mL|<100|H|||F|||20250311153000
OBX|2|NM|49563-0^Troponin I HS^LN||0.012|ng/mL|<0.040|N|||F|||20250311153000
OBX|3|NM|30313-1^Hemoglobin^LN||12.8|g/dL|13.5-17.5|L|||F|||20250311153000
OBX|4|NM|2093-3^Total Cholesterol^LN||245|mg/dL|<200|H|||F|||20250311153000
```

---

## 3. ORM^O01 - Pharmacy order routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|RX_ROUTER|PHARMACY_SYS|CVS_PHARM|20250312091500||ORM^O01^ORM_O01|MIRTH00007890|P|2.3|||AL|NE
PID|1||CHN_MRN70042618^^^CHN^MR||Kowalski^Andrea^Lynn||19920305|F|||3184 Keystone Ave^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^6819347||ENG|S|NON|SSN427-61-3948^^^SS
PV1|1|O|PCP^101^^CHN_NORTH||||FAMMD^Oglesby^Jeanette^M^^^MD|||FM|||1|||FAMMD^Oglesby^Jeanette^M^^^MD|OP
ORC|NW|MIRTH_ORD002||GRP_RX001|SC||||20250312091000|||FAMMD^Oglesby^Jeanette^M^^^MD
OBR|1|MIRTH_ORD002||RX_ORDER^Prescription^L|||20250312091000
RXO|METFORMIN^Metformin HCl 500mg^NDC||500|mg||PO^Oral^HL70162|1 tablet twice daily with meals|30|TAB|2
DG1|1||E11.9^Type 2 diabetes mellitus without complications^ICD10|||A
```

---

## 4. VXU^V04 - Immunization routed from clinic to CHIRP via Mirth

```
MSH|^~\&|MIRTH_ENGINE|IMM_ROUTER|CHIRP|ISDH|20250313143000||VXU^V04^VXU_V04|MIRTH00011234|P|2.5.1|||AL|NE
PID|1||CLINIC_MRN80051643^^^FWPED^MR||Ridenour^Caleb^Thomas||20200115|M|||1530 Sherman Blvd^^Fort Wayne^IN^46808^US||^PRN^PH^^1^260^7453812||ENG||NON|SSN508-83-4716^^^SS
PD1|||FORT WAYNE PEDIATRICS^^80051|PEDMD^Holbrook^Natalie^G^^^MD
NK1|1|Ridenour^Jessica^Ann|MTH|1530 Sherman Blvd^^Fort Wayne^IN^46808^US|^PRN^PH^^1^260^7453812
ORC|RE|MIRTH_IMM001||||||||||PEDMD^Holbrook^Natalie^G^^^MD
RXA|0|1|20250313142500|20250313142500|20^DTaP^CVX|0.5|mL|IM|RT^^Right Thigh||||||W3456A||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||20^DTaP^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
```

---

## 5. ADT^A08 - Patient update transformed by Mirth

```
MSH|^~\&|MIRTH_ENGINE|ADT_ROUTER|MPI_SYS|IHIE|20250314102000||ADT^A08^ADT_A08|MIRTH00014567|P|2.4|||AL|NE
EVN|A08|20250314102000|||REG_CLERK
PID|1||SBH_MRN90067241^^^SBH^MR||Wozniak^Theresa^Marie||19760918|F|||3417 Portage Ave^^South Bend^IN^46628^US||^PRN^PH^^1^574^2894163|^WPN^PH^^1^574^2897520|POL|M|CAT|SSN618-43-2917^^^SS
PD1|||MEMORIAL HOSPITAL PRIMARY^^90067|PRIMMD^Creighton^Alan^J^^^MD
NK1|1|Wozniak^Gerald^Edward|SPO|3417 Portage Ave^^South Bend^IN^46628^US|^PRN^PH^^1^574^2894164
IN1|1|UHC789^United Healthcare|UHC001|United Healthcare||||||||20250101|20251231|||HMO|Wozniak^Theresa^Marie|Self|19760918|3417 Portage Ave^^South Bend^IN^46628^US
```

---

## 6. ORU^R01 - Radiology result with embedded PDF routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|RAD_ROUTER|RECV_EMR|CHN_EAST|20250315162000||ORU^R01^ORU_R01|MIRTH00017890|P|2.4|||AL|NE
PID|1||CHN_MRN70042618^^^CHN^MR||Kowalski^Andrea^Lynn||19920305|F|||3184 Keystone Ave^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^6819347
PV1|1|O|RAD^201^^CHN_EAST||||RADMD^Villarreal^Gregory^S^^^MD|||RAD
ORC|RE|MIRTH_ORD003|MIRTH_RES003||CM||||20250315161500|||RADMD^Villarreal^Gregory^S^^^MD
OBR|1|MIRTH_ORD003|MIRTH_RES003|72148^MRI Lumbar Spine without Contrast^CPT|||20250315130000||||||||RADMD^Villarreal^Gregory^S^^^MD||||||20250315162000|||F
OBX|1|TX|72148^MRI Lumbar Spine without Contrast^CPT||IMPRESSION: 1. L4-L5 disc herniation with mild left neural foraminal narrowing. 2. L5-S1 disc desiccation without significant herniation. 3. No spinal stenosis.||||||F
OBX|2|ED|PDF^MRI Lumbar Spine Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 7. SIU^S12 - Appointment scheduled routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|SCHED_ROUTER|DEST_SCHED|PKV_SCHED|20250316084500||SIU^S12^SIU_S12|MIRTH00021234|P|2.4|||AL|NE
SCH|MAPT112233|MAPT112233|||FOLLOWUP^Follow-up Visit|ROUTINE^Routine||30|MIN|^^30^20250323100000^20250323103000|||||CARDMD^Garrison^Terrence^R^^^MD|^WPN^PH^^1^260^4267700|CARDIO^402^^PKV_RANDALLIA|||||BOOKED
PID|1||PKV_MRN60038291^^^PKV^MR||Engstrom^Dale^Robert||19580614|M|||2917 Calhoun St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4267193
PV1|1|O|CARDIO^402^^PKV_RANDALLIA||||CARDMD^Garrison^Terrence^R^^^MD|||CAR|||1|||CARDMD^Garrison^Terrence^R^^^MD|OP
RGS|1||CARDIO^402^^PKV_RANDALLIA
AIS|1||CARDIO_FU^Cardiology Follow-up|20250323100000|||30|MIN
AIP|1||CARDMD^Garrison^Terrence^R^^^MD|ATTENDING
```

---

## 8. ADT^A03 - Discharge routed through Mirth from South Bend hospital

```
MSH|^~\&|MIRTH_ENGINE|ADT_ROUTER|IHIE_HUB|IHIE|20250317144500||ADT^A03^ADT_A03|MIRTH00024567|P|2.4|||AL|NE
EVN|A03|20250317144500|||PRIMMD^Creighton^Alan^J^^^MD
PID|1||SBH_MRN90067241^^^SBH^MR||Wozniak^Theresa^Marie||19760918|F|||3417 Portage Ave^^South Bend^IN^46628^US||^PRN^PH^^1^574^2894163
PV1|1|I|OB^301^A^SBH_MAIN||||OBMD^Pennington^Irene^K^^^MD|||OB|||7|||OBMD^Pennington^Irene^K^^^MD|IP||||||||||||||||||SBH_MAIN|||||20250315060000|||20250317144500
PV2|||^Normal spontaneous vaginal delivery
DG1|1||O80^Encounter for full-term uncomplicated delivery^ICD10|||A
DG1|2||Z37.0^Single live birth^ICD10|||A
```

---

## 9. ORU^R01 - Drug screen results routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|TOX_ROUTER|RECV_EMR|EMPLOYER_OCC|20250318091000||ORU^R01^ORU_R01|MIRTH00027890|P|2.4|||AL|NE
PID|1||OCC_MRN10078532^^^OCC^MR||Fenwick^Travis^Ray||19890723|M|||4715 Lima Rd^^Fort Wayne^IN^46808^US||^PRN^PH^^1^260^7514893||ENG|S|NON|SSN734-29-5183^^^SS
PV1|1|O|OCC^101^^OCCMED||||OCCMD^Stanfield^Roger^W^^^MD|||OCC|||1|||OCCMD^Stanfield^Roger^W^^^MD|OP
ORC|RE|MIRTH_ORD004|MIRTH_RES004||CM||||20250318090500|||OCCMD^Stanfield^Roger^W^^^MD
OBR|1|MIRTH_ORD004|MIRTH_RES004|49587-9^Drug Screen Panel Urine^LN|||20250317150000||||||||OCCMD^Stanfield^Roger^W^^^MD||||||20250318091000|||F
OBX|1|ST|3397-7^Amphetamines Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|2|ST|3426-4^Barbiturates Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|3|ST|3398-5^Benzodiazepines Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|4|ST|3427-2^Cannabinoids Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|5|ST|3399-3^Cocaine Metabolite Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|6|ST|19659-2^Opiates Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
OBX|7|ST|8257-0^Phencyclidine Screen Urine^LN||Negative||Negative|N|||F|||20250318091000
```

---

## 10. VXU^V04 - School-age immunization routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|IMM_ROUTER|CHIRP|ISDH|20250319104500||VXU^V04^VXU_V04|MIRTH00031234|P|2.5.1|||AL|NE
PID|1||PED_MRN20089473^^^SBPED^MR||Harbaugh^Ethan^William||20140830|M|||2718 Lincolnway W^^Mishawaka^IN^46544^US||^PRN^PH^^1^574^2593174||ENG||CAT|SSN819-24-5637^^^SS
PD1|||MICHIANA PEDIATRICS^^20089|PEDMD^Navarro^Gina^L^^^MD
NK1|1|Harbaugh^Tamara^Joy|MTH|2718 Lincolnway W^^Mishawaka^IN^46544^US|^PRN^PH^^1^574^2593174
ORC|RE|MIRTH_IMM002||||||||||PEDMD^Navarro^Gina^L^^^MD
RXA|0|1|20250319104000|20250319104000|94^MMRV^CVX|0.5|mL|SC|LA^^Left Arm||||||M8821C||MSD^Merck Sharp & Dohme|||||A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
ORC|RE|MIRTH_IMM003||||||||||PEDMD^Navarro^Gina^L^^^MD
RXA|0|1|20250319104000|20250319104000|89^Polio IPV^CVX|0.5|mL|IM|RA^^Right Arm||||||J2345B||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC1^Medicaid^CDCPHINVS||||||F
```

---

## 11. ORM^O01 - Lab order routed from clinic to reference lab via Mirth

```
MSH|^~\&|MIRTH_ENGINE|ORDER_ROUTER|REF_LAB|QUEST|20250320081500||ORM^O01^ORM_O01|MIRTH00034567|P|2.3|||AL|NE
PID|1||CLINIC_MRN30096815^^^INDY_UC^MR||Driscoll^Vernon^Keith||19700212|M|||4220 W Washington St^^Indianapolis^IN^46241^US||^PRN^PH^^1^317^2467518||ENG|M|BAP|SSN215-47-8362^^^SS
PV1|1|O|UC^101^^INDY_UC||||UCMD^Billings^Kenneth^F^^^MD|||FM|||1|||UCMD^Billings^Kenneth^F^^^MD|OP
ORC|NW|MIRTH_ORD005||GRP_LAB001|SC||||20250320081000|||UCMD^Billings^Kenneth^F^^^MD
OBR|1|MIRTH_ORD005||24323-8^Comprehensive Metabolic Panel^LN|||20250320081500||||||||UCMD^Billings^Kenneth^F^^^MD
OBR|2|MIRTH_ORD005||57021-8^CBC with Differential^LN|||20250320081500||||||||UCMD^Billings^Kenneth^F^^^MD
OBR|3|MIRTH_ORD005||3094-0^HbA1c^LN|||20250320081500||||||||UCMD^Billings^Kenneth^F^^^MD
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
```

---

## 12. ADT^A04 - Patient registration routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|REG_ROUTER|MPI_SYS|IHIE|20250321074000||ADT^A04^ADT_A04|MIRTH00037890|P|2.4|||AL|NE
EVN|A04|20250321074000|||REG_CLERK
PID|1||PKV_MRN60081374^^^PKV^MR||Prescott^Monica^Jane||19810604|F|||5612 Stellhorn Rd^^Fort Wayne^IN^46815^US||^PRN^PH^^1^260^4926174|^WPN^PH^^1^260^4920203|ENG|M|LUT|SSN309-64-7213^^^SS
PD1|||PARKVIEW WOMEN'S HEALTH^^60081|OBMD^Culbertson^Brenda^N^^^MD
NK1|1|Prescott^Wade^Steven|SPO|5612 Stellhorn Rd^^Fort Wayne^IN^46815^US|^PRN^PH^^1^260^4926175
PV1|1|O|OBGYN^201^^PKV_RANDALLIA||||OBMD^Culbertson^Brenda^N^^^MD|||OBG|||1|||OBMD^Culbertson^Brenda^N^^^MD|OP
IN1|1|BCBS456^Blue Cross Blue Shield|BCBS001|Blue Cross Blue Shield of Indiana||||||||20250101|20251231|||PPO|Prescott^Monica^Jane|Self|19810604|5612 Stellhorn Rd^^Fort Wayne^IN^46815^US
```

---

## 13. ORU^R01 - ABG results routed through Mirth from ICU

```
MSH|^~\&|MIRTH_ENGINE|CRIT_ROUTER|ICU_EMR|PKV_ICU|20250322031500||ORU^R01^ORU_R01|MIRTH00041234|P|2.4|||AL|NE
PID|1||PKV_MRN60038291^^^PKV^MR||Engstrom^Dale^Robert||19580614|M|||2917 Calhoun St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4267193
PV1|1|I|ICU^101^A^PKV_RANDALLIA||||ICUMD^Matsuda^Leonard^H^^^MD|||CC|||7|||ICUMD^Matsuda^Leonard^H^^^MD|IP
ORC|RE|MIRTH_ORD006|MIRTH_RES006||CM||||20250322031000|||ICUMD^Matsuda^Leonard^H^^^MD
OBR|1|MIRTH_ORD006|MIRTH_RES006|24336-0^Arterial Blood Gas^LN|||20250322030000|||||STAT||||||ICUMD^Matsuda^Leonard^H^^^MD||||||20250322031500|||F
OBX|1|NM|2744-1^pH Arterial^LN||7.32||7.35-7.45|L|||F|||20250322031500
OBX|2|NM|2019-8^pCO2 Arterial^LN||52|mmHg|35-45|H|||F|||20250322031500
OBX|3|NM|2703-7^pO2 Arterial^LN||68|mmHg|80-100|L|||F|||20250322031500
OBX|4|NM|1959-6^Bicarbonate Arterial^LN||26|mmol/L|22-26|N|||F|||20250322031500
OBX|5|NM|20564-1^Oxygen Saturation Arterial^LN||91|%|95-100|L|||F|||20250322031500
```

---

## 14. SIU^S15 - Appointment cancelled routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|SCHED_ROUTER|DEST_SCHED|CHN_SCHED|20250323090000||SIU^S15^SIU_S12|MIRTH00044567|P|2.4|||AL|NE
SCH|MAPT223344|MAPT223344|||OFFICE^Office Visit|ROUTINE^Routine||20|MIN|^^20^20250330093000^20250330095000|||||FAMMD^Oglesby^Jeanette^M^^^MD|^WPN^PH^^1^317^6818800|PCP^101^^CHN_NORTH|||||CANCELLED
PID|1||CHN_MRN70042618^^^CHN^MR||Kowalski^Andrea^Lynn||19920305|F|||3184 Keystone Ave^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^6819347
PV1|1|O|PCP^101^^CHN_NORTH||||FAMMD^Oglesby^Jeanette^M^^^MD|||FM|||1|||FAMMD^Oglesby^Jeanette^M^^^MD|OP
```

---

## 15. ORU^R01 - Prenatal lab panel routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|LAB_ROUTER|OB_EMR|PKV_OB|20250324112000||ORU^R01^ORU_R01|MIRTH00047890|P|2.4|||AL|NE
PID|1||PKV_MRN60081374^^^PKV^MR||Prescott^Monica^Jane||19810604|F|||5612 Stellhorn Rd^^Fort Wayne^IN^46815^US||^PRN^PH^^1^260^4926174
PV1|1|O|OBGYN^201^^PKV_RANDALLIA||||OBMD^Culbertson^Brenda^N^^^MD|||OBG
ORC|RE|MIRTH_ORD007|MIRTH_RES007||CM||||20250324111500|||OBMD^Culbertson^Brenda^N^^^MD
OBR|1|MIRTH_ORD007|MIRTH_RES007|56850-4^Prenatal Panel^LN|||20250324080000||||||||OBMD^Culbertson^Brenda^N^^^MD||||||20250324112000|||F
OBX|1|ST|882-1^ABO Group^LN||A||||||F|||20250324112000
OBX|2|ST|10331-7^Rh Type^LN||Positive||||||F|||20250324112000
OBX|3|ST|890-4^Antibody Screen^LN||Negative||Negative|N|||F|||20250324112000
OBX|4|NM|718-7^Hemoglobin^LN||12.4|g/dL|11.0-16.0|N|||F|||20250324112000
OBX|5|NM|4544-3^Hematocrit^LN||37.2|%|33.0-45.0|N|||F|||20250324112000
OBX|6|ST|5196-1^Hepatitis B Surface Antigen^LN||Nonreactive||Nonreactive|N|||F|||20250324112000
OBX|7|ST|20507-0^HIV 1/2 Antibody^LN||Nonreactive||Nonreactive|N|||F|||20250324112000
OBX|8|ST|22462-6^Syphilis RPR^LN||Nonreactive||Nonreactive|N|||F|||20250324112000
OBX|9|NM|27353-2^Glucose 1 Hour^LN||128|mg/dL|<140|N|||F|||20250324112000
```

---

## 16. ADT^A01 - Newborn admission routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|ADT_ROUTER|NURSERY_SYS|SBH_NURS|20250325190000||ADT^A01^ADT_A01|MIRTH00051234|P|2.4|||AL|NE
EVN|A01|20250325190000|||OBMD^Pennington^Irene^K^^^MD
PID|1||SBH_NB002314^^^SBH^MR||Wozniak^Baby Boy||20250325|M|||3417 Portage Ave^^South Bend^IN^46628^US||^PRN^PH^^1^574^2894163||ENG|S||SSN000-00-0000^^^SS|||||||||||N
NK1|1|Wozniak^Theresa^Marie|MTH|3417 Portage Ave^^South Bend^IN^46628^US|^PRN^PH^^1^574^2894163
PV1|1|I|NURSERY^101^A^SBH_MAIN^^^^NURSERY||||OBMD^Pennington^Irene^K^^^MD|PEDMD^Lockhart^Nathan^R^^^MD||NB|||7|||PEDMD^Lockhart^Nathan^R^^^MD|IP||||||||||||||||||SBH_MAIN|||||20250325190000
DG1|1||Z38.00^Single liveborn infant, delivered vaginally^ICD10|||A
```

---

## 17. ORU^R01 - Wound culture result routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|MICRO_ROUTER|RECV_EMR|DEAC_MED|20250326101500||ORU^R01^ORU_R01|MIRTH00054567|P|2.4|||AL|NE
PID|1||DEAC_MRN50123781^^^DEAC^MR||Hudgins^Ralph^Victor||19650830|M|||2415 Stringtown Rd^^Evansville^IN^47711^US||^PRN^PH^^1^812^4738291||ENG|D|PRO|SSN547-81-4925^^^SS
PV1|1|I|WOUND^201^A^DEAC_EVN||||WNDMD^Tillman^Craig^E^^^MD|||SUR|||7|||WNDMD^Tillman^Craig^E^^^MD|IP
ORC|RE|MIRTH_ORD008|MIRTH_RES008||CM||||20250326101000|||WNDMD^Tillman^Craig^E^^^MD
OBR|1|MIRTH_ORD008|MIRTH_RES008|6462-6^Wound Culture^LN|||20250324090000||||||||WNDMD^Tillman^Craig^E^^^MD||||||20250326101500|||F
OBX|1|ST|6462-6^Wound Culture^LN||Moderate growth Pseudomonas aeruginosa||||||F|||20250326101500
OBX|2|ST|18862-3^Gentamicin Susceptibility^LN||Susceptible (MIC 2.0 mcg/mL)||||||F|||20250326101500
OBX|3|ST|18943-1^Piperacillin-Tazobactam Susceptibility^LN||Susceptible (MIC 8.0 mcg/mL)||||||F|||20250326101500
OBX|4|ST|18879-7^Ciprofloxacin Susceptibility^LN||Intermediate (MIC 2.0 mcg/mL)||||||A|||F|||20250326101500
OBX|5|ST|18906-8^Meropenem Susceptibility^LN||Susceptible (MIC 1.0 mcg/mL)||||||F|||20250326101500
```

---

## 18. ORM^O01 - CT scan order routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|ORDER_ROUTER|RAD_SYS|PKV_RAD|20250327142000||ORM^O01^ORM_O01|MIRTH00057890|P|2.3|||AL|NE
PID|1||PKV_MRN60119847^^^PKV^MR||Sutherland^Denise^Lorraine||19730411|F|||3209 Hobson Rd^^Fort Wayne^IN^46815^US||^PRN^PH^^1^260^4862193||ENG|M|LUT|SSN368-17-9241^^^SS
PV1|1|E|ED^TRIAGE^^PKV_RANDALLIA||||EMERMD^Ashcraft^Donald^T^^^MD|||EM|||1|||EMERMD^Ashcraft^Donald^T^^^MD|ER
ORC|NW|MIRTH_ORD009||GRP_RAD002|SC||||20250327141500|||EMERMD^Ashcraft^Donald^T^^^MD|ED^TRIAGE^^PKV_RANDALLIA
OBR|1|MIRTH_ORD009||74178^CT Abdomen Pelvis with Contrast^CPT|||20250327143000|||||STAT||||||EMERMD^Ashcraft^Donald^T^^^MD||||||||||1^^^20250327143000^^S
DG1|1||R10.31^Right lower quadrant pain^ICD10|||A
```

---

## 19. ORU^R01 - Sleep study report with embedded PDF routed through Mirth

```
MSH|^~\&|MIRTH_ENGINE|SLEEP_ROUTER|PCP_EMR|DR_PRIMMD|20250328093000||ORU^R01^ORU_R01|MIRTH00061234|P|2.4|||AL|NE
PID|1||SBH_MRN90067241^^^SBH^MR||Wozniak^Theresa^Marie||19760918|F|||3417 Portage Ave^^South Bend^IN^46628^US||^PRN^PH^^1^574^2894163
PV1|1|O|SLEEP^101^^SBH_MAIN||||SLEEPMD^Fonseca^Patricia^V^^^MD|||PUL
ORC|RE|MIRTH_ORD010|MIRTH_RES010||CM||||20250328092500|||SLEEPMD^Fonseca^Patricia^V^^^MD
OBR|1|MIRTH_ORD010|MIRTH_RES010|95810^Polysomnography^CPT|||20250326210000||||||||SLEEPMD^Fonseca^Patricia^V^^^MD||||||20250328093000|||F
OBX|1|TX|95810^Polysomnography^CPT||INTERPRETATION: Moderate obstructive sleep apnea. AHI 22.4 events/hour. Lowest SpO2 82%. Recommend CPAP titration study. Significant improvement in supine avoidance position.||||||F
OBX|2|ED|PDF^Sleep Study Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 20. VXU^V04 - COVID booster vaccination routed through Mirth to CHIRP

```
MSH|^~\&|MIRTH_ENGINE|IMM_ROUTER|CHIRP|ISDH|20250329140000||VXU^V04^VXU_V04|MIRTH00064567|P|2.5.1|||AL|NE
PID|1||PHARM_MRN40135682^^^WLGRN^MR||Clevenger^Donna^Ruth||19550219|F|||1824 Sagamore Pkwy S^^West Lafayette^IN^47906^US||^PRN^PH^^1^765^4291538||ENG|W|MET|SSN679-12-4836^^^SS
PD1|||WALGREENS PHARMACY 5821^^40135|PHARMD^Bhatia^Priya^S^^^PharmD
ORC|RE|MIRTH_IMM004||||||||||PHARMD^Bhatia^Priya^S^^^PharmD
RXA|0|1|20250329135500|20250329135500|300^COVID-19 Vaccine mRNA BV^CVX|0.5|mL|IM|LA^^Left Arm||||||GH5678A||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||300^COVID-19 Vaccine mRNA BV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20240812||||||F
```
