# IHIE (Indiana Health Information Exchange) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission notification routed through IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|PARKVIEW|20250310145000||ADT^A01^ADT_A01|IHIE00001234|P|2.5.1|||AL|NE
EVN|A01|20250310145000
PID|1||MRN70005891^^^PKV^MR~IHIE90008412^^^IHIE^PI||Hargrove^Denise^Maureen||19620318|F|||345 Clinton St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4439017||ENG|M|LUT|SSN412-63-8901^^^SS
PV1|1|I|4WEST^401^A^PARKVIEW_RANDALLIA||||DKESSLER^Kessler^Douglas^W^^^MD|||MED|||7|||DKESSLER^Kessler^Douglas^W^^^MD|IP||||||||||||||||||PARKVIEW_RANDALLIA|||||20250310145000
PV2|||^Community-acquired pneumonia
DG1|1||J18.9^Pneumonia, unspecified organism^ICD10|||A
```

---

## 2. ORU^R01 - Lab result forwarded via IHIE from Parkview Health

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_OFFICE|20250312083000||ORU^R01^ORU_R01|IHIE00004567|P|2.5.1|||AL|NE
PID|1||MRN70005891^^^PKV^MR~IHIE90008412^^^IHIE^PI||Hargrove^Denise^Maureen||19620318|F|||345 Clinton St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4439017
PV1|1|I|4WEST^401^A^PARKVIEW_RANDALLIA||||DKESSLER^Kessler^Douglas^W^^^MD
ORC|RE|PKV_ORD001|PKV_RES001||CM||||20250312082500|||DKESSLER^Kessler^Douglas^W^^^MD
OBR|1|PKV_ORD001|PKV_RES001|24323-8^Comprehensive Metabolic Panel^LN|||20250312070000||||||||DKESSLER^Kessler^Douglas^W^^^MD||||||20250312083000|||F
OBX|1|NM|2345-7^Glucose^LN||145|mg/dL|70-99|H|||F|||20250312083000
OBX|2|NM|3094-0^BUN^LN||24|mg/dL|7-20|H|||F|||20250312083000
OBX|3|NM|2160-0^Creatinine^LN||1.6|mg/dL|0.7-1.3|H|||F|||20250312083000
OBX|4|NM|2951-2^Sodium^LN||136|mmol/L|136-145|N|||F|||20250312083000
OBX|5|NM|2823-3^Potassium^LN||5.0|mmol/L|3.5-5.1|N|||F|||20250312083000
OBX|6|NM|2075-0^Chloride^LN||100|mmol/L|98-106|N|||F|||20250312083000
OBX|7|NM|17861-6^Calcium^LN||8.9|mg/dL|8.5-10.5|N|||F|||20250312083000
```

---

## 3. ADT^A03 - Discharge notification distributed by IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|CHN_PCP|20250314160000||ADT^A03^ADT_A03|IHIE00007890|P|2.5.1|||AL|NE
EVN|A03|20250314160000
PID|1||MRN80226714^^^CHN^MR~IHIE90013579^^^IHIE^PI||Whitfield^Terrance^LeRoy||19840725|M|||678 College Ave^^Bloomington^IN^47401^US||^PRN^PH^^1^812^3387421||ENG|S|BAP|SSN531-84-2067^^^SS
PV1|1|I|MED^301^A^IU_HEALTH_BLOOMINGTON||||NFERRIS^Ferris^Natalie^C^^^MD|||MED|||7|||NFERRIS^Ferris^Natalie^C^^^MD|IP||||||||||||||||||IU_HEALTH_BLOOMINGTON|||||20250310120000|||20250314160000
PV2|||^Acute kidney injury
DG1|1||N17.9^Acute kidney failure, unspecified^ICD10|||A
DG1|2||E11.22^Type 2 diabetes mellitus with diabetic chronic kidney disease^ICD10|||A
```

---

## 4. MDM^T02 - Clinical document shared via IHIE DOCS4DOCS

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|SPECIALIST|20250315112000||MDM^T02^MDM_T02|IHIE00011234|P|2.5|||AL|NE
EVN|T02|20250315112000
PID|1||MRN60447823^^^ESK^MR~IHIE90024681^^^IHIE^PI||Pemberton^Gloria^Irene||19710914|F|||234 Massachusetts Ave^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^6629034||ENG|D|NON|SSN648-23-5190^^^SS
PV1|1|O|CARDIO^201^^ESKENAZI_HEALTH||||AVARGAS^Vargas^Alberto^R^^^MD|||CAR|||1|||AVARGAS^Vargas^Alberto^R^^^MD|OP
TXA|1|CN^Consultation Note|TX|20250315100000|AVARGAS^Vargas^Alberto^R^^^MD||20250315112000||AVARGAS^Vargas^Alberto^R^^^MD|||||IHIE_DOC001||AU|||
OBX|1|TX|11488-4^Consultation Note^LN||CARDIOLOGY CONSULTATION: 56yo female with new-onset atrial fibrillation. Rate controlled on metoprolol. CHA2DS2-VASc score 2. Recommend anticoagulation with apixaban. Follow-up echo in 4 weeks.||||||F
```

---

## 5. QBP^Q22 - Patient discovery query through IHIE

```
MSH|^~\&|QUERY_SYS|DR_BUCKNER|IHIE_HUB|IHIE|20250316093000||QBP^Q22^QBP_Q21|IHIE00014567|P|2.5|||AL|NE
QPD|Q22^FindCandidates^HL7|QRY001234|@PID.5.1^Hargrove~@PID.5.2^Denise~@PID.7^19620318~@PID.8^F~@PID.11.5^46802
RCP|I|10^RD
```

---

## 6. RSP^K22 - Patient discovery response from IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|QUERY_SYS|DR_BUCKNER|20250316093005||RSP^K22^RSP_K21|IHIE00014568|P|2.5|||AL|NE
MSA|AA|IHIE00014567
QAK|QRY001234|OK|Q22^FindCandidates^HL7|1
QPD|Q22^FindCandidates^HL7|QRY001234|@PID.5.1^Hargrove~@PID.5.2^Denise~@PID.7^19620318~@PID.8^F~@PID.11.5^46802
PID|1||MRN70005891^^^PKV^MR~IHIE90008412^^^IHIE^PI||Hargrove^Denise^Maureen||19620318|F|||345 Clinton St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^4439017||ENG|M|LUT|SSN412-63-8901^^^SS
```

---

## 7. ORU^R01 - Radiology result distributed via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_OKAFOR|20250317141500||ORU^R01^ORU_R01|IHIE00017890|P|2.5.1|||AL|NE
PID|1||MRN50339217^^^IUH^MR~IHIE90031748^^^IHIE^PI||Delgado^Enrique^Ramon||19580203|M|||890 West 38th St^^Indianapolis^IN^46208^US||^PRN^PH^^1^317^7714562||SPA|M|CAT|SSN739-05-4218^^^SS
PV1|1|O|RAD^101^^IU_HEALTH_METHODIST||||RGRAHAM^Graham^Patricia^E^^^MD|||RAD
ORC|RE|IUH_ORD002|IUH_RES002||CM||||20250317141000|||RGRAHAM^Graham^Patricia^E^^^MD
OBR|1|IUH_ORD002|IUH_RES002|71046^Chest X-Ray 2 Views^CPT|||20250317120000||||||||RGRAHAM^Graham^Patricia^E^^^MD||||||20250317141500|||F
OBX|1|TX|71046^Chest X-Ray 2 Views^CPT||IMPRESSION: Clear lungs bilaterally. No acute cardiopulmonary process. Heart size normal. No pleural effusion.||||||F
```

---

## 8. ADT^A08 - Patient demographics update via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|FRAN_INDY|20250318101000||ADT^A08^ADT_A08|IHIE00021234|P|2.5.1|||AL|NE
EVN|A08|20250318101000
PID|1||FMRN40562310^^^FRAN^MR~IHIE90042856^^^IHIE^PI||Yoon^Brandon^Hyun||19930415|M|||567 Massachusetts Ave^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^5520148|^WPN^PH^^1^317^9913067|KOR|S|BUD|SSN823-16-4097^^^SS
PD1|||FRANCISCAN HEALTH INDIANAPOLIS^^40562|CMURTHY^Murthy^Chandra^P^^^MD
NK1|1|Yoon^Soo Jin^Kyung|MTH|567 Massachusetts Ave^^Indianapolis^IN^46204^US|^PRN^PH^^1^317^5520149
IN1|1|ANTHEM03^Anthem|ANT001|Anthem Blue Cross Blue Shield||||||||20250101|20251231|||PPO|Yoon^Brandon^Hyun|Self|19930415|567 Massachusetts Ave^^Indianapolis^IN^46204^US
```

---

## 9. ORU^R01 - Pathology result with embedded PDF via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_OFFICE|20250319153000||ORU^R01^ORU_R01|IHIE00024567|P|2.5.1|||AL|NE
PID|1||MRN60881245^^^ESK^MR~IHIE90053912^^^IHIE^PI||Sandoval^Marisol^Estela||19750820|F|||1234 Prospect St^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^8847213||SPA|M|CAT|SSN917-40-6385^^^SS
PV1|1|I|SURG^401^^ESKENAZI_HEALTH||||SFOLTZ^Foltz^Steven^A^^^MD|||SUR
ORC|RE|ESK_ORD003|ESK_RES003||CM||||20250319152500|||SFOLTZ^Foltz^Steven^A^^^MD
OBR|1|ESK_ORD003|ESK_RES003|88305^Surgical Pathology^CPT|||20250317090000||||||||PMAHAJAN^Mahajan^Priya^K^^^MD||||||20250319153000|||F
OBX|1|TX|88305^Surgical Pathology^CPT||DIAGNOSIS: Uterus, total hysterectomy: Leiomyomata uteri, largest 4.2 cm. Endometrium - proliferative phase. Cervix - chronic cervicitis. No malignancy identified.||||||F
OBX|2|ED|PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 10. MDM^T02 - Discharge summary document via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_NOVAK|20250320110000||MDM^T02^MDM_T02|IHIE00027890|P|2.5|||AL|NE
EVN|T02|20250320110000
PID|1||MRN80226714^^^CHN^MR~IHIE90013579^^^IHIE^PI||Whitfield^Terrance^LeRoy||19840725|M|||678 College Ave^^Bloomington^IN^47401^US||^PRN^PH^^1^812^3387421
PV1|1|I|MED^301^A^IU_HEALTH_BLOOMINGTON||||NFERRIS^Ferris^Natalie^C^^^MD|||MED
TXA|1|DS^Discharge Summary|TX|20250314160000|NFERRIS^Ferris^Natalie^C^^^MD||20250320110000||NFERRIS^Ferris^Natalie^C^^^MD|||||IHIE_DOC002||AU|||
OBX|1|TX|18842-5^Discharge Summary^LN||Patient admitted with acute kidney injury secondary to dehydration and diabetic nephropathy. Treated with IV fluids, insulin adjustment. Creatinine improved from 3.2 to 1.8. Discharged with nephrology follow-up in 2 weeks.||||||F
```

---

## 11. ADT^A01 - Admission notification from IU Health Bloomington via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|PCP_NOTIFY|20250321190000||ADT^A01^ADT_A01|IHIE00031234|P|2.5.1|||AL|NE
EVN|A01|20250321190000
PID|1||MRN90471832^^^IUH^MR~IHIE90067215^^^IHIE^PI||O'Malley^Brendan^Thomas||19560710|M|||456 Walnut St^^Bloomington^IN^47403^US||^PRN^PH^^1^812^9914037||ENG|M|CAT|SSN284-71-5930^^^SS
PV1|1|E|ED^TRIAGE^^IU_HEALTH_BLOOMINGTON||||ECRAWFORD^Crawford^Eugene^B^^^MD|||EM|||1|||ECRAWFORD^Crawford^Eugene^B^^^MD|ER||||||||||||||||||IU_HEALTH_BLOOMINGTON|||||20250321190000
PV2|||^Acute chest pain
DG1|1||R07.9^Chest pain, unspecified^ICD10|||A
```

---

## 12. ORU^R01 - Microbiology result forwarded via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|INF_CONTROL|20250322093000||ORU^R01^ORU_R01|IHIE00034567|P|2.5.1|||AL|NE
PID|1||FMRN40117548^^^FRAN^MR~IHIE90078346^^^IHIE^PI||Engstrom^Dorothy^Vivian||19450128|F|||345 National Ave^^Indianapolis^IN^46227^US||^PRN^PH^^1^317^2216840||GER|W|LUT|SSN160-42-7839^^^SS
PV1|1|I|2SOUTH^208^A^FRANCISCAN_HEALTH_INDY||||DBANERJEE^Banerjee^Dipak^S^^^MD|||MED
ORC|RE|FRAN_ORD004|FRAN_RES004||CM||||20250322092500|||DBANERJEE^Banerjee^Dipak^S^^^MD
OBR|1|FRAN_ORD004|FRAN_RES004|87081^Urine Culture^LN|||20250320140000||||||||DBANERJEE^Banerjee^Dipak^S^^^MD||||||20250322093000|||F
OBX|1|ST|87081^Urine Culture^LN||>100,000 CFU/mL Escherichia coli||||||F|||20250322093000
OBX|2|ST|18861-5^Ampicillin Susceptibility^LN||Resistant||||||A|||F|||20250322093000
OBX|3|ST|18879-7^Ciprofloxacin Susceptibility^LN||Susceptible||||||F|||20250322093000
OBX|4|ST|18995-1^Nitrofurantoin Susceptibility^LN||Susceptible||||||F|||20250322093000
OBX|5|ST|18998-5^Trimethoprim-Sulfamethoxazole Susceptibility^LN||Resistant||||||A|||F|||20250322093000
```

---

## 13. QBP^Q11 - Immunization history query via IHIE to CHIRP

```
MSH|^~\&|IHIE_HUB|IHIE|CHIRP|ISDH|20250323100000||QBP^Q11^QBP_Q11|IHIE00037890|P|2.5.1|||AL|NE
QPD|Z44^Request Immunization History^CDCPHINVS|QRY002345|MRN70005891^^^PKV^MR~IHIE90008412^^^IHIE^PI|Hargrove^Denise^Maureen||19620318|F
RCP|I|99^RD
```

---

## 14. RSP^K11 - Immunization history response via IHIE from CHIRP

```
MSH|^~\&|CHIRP|ISDH|IHIE_HUB|IHIE|20250323100005||RSP^K11^RSP_K11|IHIE00037891|P|2.5.1|||AL|NE
MSA|AA|IHIE00037890
QAK|QRY002345|OK|Z44^Request Immunization History^CDCPHINVS
QPD|Z44^Request Immunization History^CDCPHINVS|QRY002345|MRN70005891^^^PKV^MR~IHIE90008412^^^IHIE^PI|Hargrove^Denise^Maureen||19620318|F
PID|1||CHIRP_ID005891^^^CHIRP^SR||Hargrove^Denise^Maureen||19620318|F|||345 Clinton St^^Fort Wayne^IN^46802^US
ORC|RE|CHIRP_IMM001||||||||||
RXA|0|1|20241001|20241001|141^Influenza, seasonal^CVX|0.5|mL|IM|||||||L4521B||SNF^Sanofi Pasteur
RXA|0|1|20230915|20230915|213^SARS-COV-2 (COVID-19) vaccine^CVX|0.5|mL|IM|||||||FA4321||MOD^Moderna
```

---

## 15. ADT^A04 - ER registration notification via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|NOTIFY_PCP|20250324213000||ADT^A04^ADT_A04|IHIE00041234|P|2.5.1|||AL|NE
EVN|A04|20250324213000
PID|1||MRN71283947^^^PKV^MR~IHIE90085614^^^IHIE^PI||Langston^Tiffany^Renee||19880912|F|||890 Dupont Rd^^Fort Wayne^IN^46825^US||^PRN^PH^^1^260^7730291||ENG|M|MET|SSN350-19-7462^^^SS
PV1|1|E|ED^TRIAGE^^PARKVIEW_RANDALLIA||||EHAWKINS^Hawkins^Elliott^T^^^MD|||EM|||1|||EHAWKINS^Hawkins^Elliott^T^^^MD|ER
PV2|||^Migraine with aura
DG1|1||G43.109^Migraine with aura, not intractable, without status migrainosus^ICD10|||A
```

---

## 16. ORU^R01 - Cardiac catheterization report with PDF via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_ALBRIGHT|20250325140000||ORU^R01^ORU_R01|IHIE00044567|P|2.5.1|||AL|NE
PID|1||MRN90471832^^^IUH^MR~IHIE90067215^^^IHIE^PI||O'Malley^Brendan^Thomas||19560710|M|||456 Walnut St^^Bloomington^IN^47403^US||^PRN^PH^^1^812^9914037
PV1|1|I|CCU^201^A^IU_HEALTH_METHODIST||||CMORENO^Moreno^Carlos^T^^^MD|||CAR
ORC|RE|IUH_ORD005|IUH_RES005||CM||||20250325135500|||CMORENO^Moreno^Carlos^T^^^MD
OBR|1|IUH_ORD005|IUH_RES005|93510^Left Heart Catheterization^CPT|||20250324100000||||||||CMORENO^Moreno^Carlos^T^^^MD||||||20250325140000|||F
OBX|1|TX|93510^Left Heart Catheterization^CPT||FINDINGS: 90% stenosis of LAD. 70% stenosis of RCA. LV EF 45%. RECOMMENDATION: CABG vs PCI discussion with cardiac surgery.||||||F
OBX|2|ED|PDF^Cardiac Catheterization Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 17. MDM^T02 - Consultation note shared via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|REFERRING_MD|20250326091000||MDM^T02^MDM_T02|IHIE00047890|P|2.5|||AL|NE
EVN|T02|20250326091000
PID|1||MRN71283947^^^PKV^MR~IHIE90085614^^^IHIE^PI||Langston^Tiffany^Renee||19880912|F|||890 Dupont Rd^^Fort Wayne^IN^46825^US||^PRN^PH^^1^260^7730291
PV1|1|O|NEURO^201^^PARKVIEW_RANDALLIA||||NQUACH^Quach^Linh^T^^^MD|||NEU
TXA|1|CN^Consultation Note|TX|20250325150000|NQUACH^Quach^Linh^T^^^MD||20250326091000||NQUACH^Quach^Linh^T^^^MD|||||IHIE_DOC003||AU|||
OBX|1|TX|11488-4^Consultation Note^LN||NEUROLOGY CONSULTATION: 36yo female with chronic migraines with visual aura, frequency 4-5/month. MRI brain normal. Currently on sumatriptan PRN. Starting topiramate 25mg daily, titrate to 100mg. Botox evaluation if no improvement in 3 months.||||||F
```

---

## 18. ADT^A03 - Discharge notification from Parkview via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|SNF_NOTIFY|20250327151500||ADT^A03^ADT_A03|IHIE00051234|P|2.5.1|||AL|NE
EVN|A03|20250327151500
PID|1||MRN72394610^^^PKV^MR~IHIE90091827^^^IHIE^PI||Dietrich^Evelyn^Mae||19380804|F|||234 Berry St^^Fort Wayne^IN^46802^US||^PRN^PH^^1^260^3310478||GER|W|LUT|SSN471-28-0364^^^SS
PV1|1|I|ORTHO^501^A^PARKVIEW_RANDALLIA||||OWINTERS^Winters^Oliver^E^^^MD|||ORT|||7|||OWINTERS^Winters^Oliver^E^^^MD|IP||||||||||||||||||PARKVIEW_RANDALLIA|||||20250324080000|||20250327151500
PV2|||^Right hip fracture, status post ORIF
DG1|1||S72.001A^Fracture of unspecified part of neck of right femur, initial encounter^ICD10|||A
DG1|2||Z96.641^Presence of right artificial hip joint^ICD10|||A
```

---

## 19. ORU^R01 - Newborn screening result via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|RECV_SYS|IUH_NICU|20250328110000||ORU^R01^ORU_R01|IHIE00054567|P|2.5.1|||AL|NE
PID|1||NB_MRN008341^^^IUH^MR~IHIE90103245^^^IHIE^PI||Whitaker^Baby Girl||20250326|F|||1234 Capitol Ave^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^4418902
PV1|1|I|NICU^101^A^IU_HEALTH_METHODIST||||NSRINIVASAN^Srinivasan^Nalini^S^^^MD|||NEO
ORC|RE|ISDH_NBS001|ISDH_NBSR001||CM||||20250328105500|||NSRINIVASAN^Srinivasan^Nalini^S^^^MD
OBR|1|ISDH_NBS001|ISDH_NBSR001|54089-8^Newborn Screening Panel^LN|||20250326120000||||||||NSRINIVASAN^Srinivasan^Nalini^S^^^MD||||||20250328110000|||F
OBX|1|ST|54090-6^Thyroid Stimulating Hormone^LN||Normal||Normal|N|||F|||20250328110000
OBX|2|ST|54091-4^Phenylalanine^LN||Normal||Normal|N|||F|||20250328110000
OBX|3|ST|54079-9^Hemoglobin Pattern^LN||FA (Normal)||FA|N|||F|||20250328110000
OBX|4|ST|57700-5^Cystic Fibrosis (IRT)^LN||Normal||Normal|N|||F|||20250328110000
OBX|5|ST|54078-1^Galactose^LN||Normal||Normal|N|||F|||20250328110000
OBX|6|ST|58232-0^Biotinidase^LN||Normal||Normal|N|||F|||20250328110000
```

---

## 20. ORU^R01 - Mammography report with embedded PDF via IHIE

```
MSH|^~\&|IHIE_HUB|IHIE|PCP_SYS|DR_ROWAN|20250329140000||ORU^R01^ORU_R01|IHIE00057890|P|2.5.1|||AL|NE
PID|1||MRN60881245^^^ESK^MR~IHIE90053912^^^IHIE^PI||Sandoval^Marisol^Estela||19750820|F|||1234 Prospect St^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^8847213
PV1|1|O|RAD^201^^ESKENAZI_HEALTH||||RWASHBURN^Washburn^Danielle^K^^^MD|||RAD
ORC|RE|ESK_ORD006|ESK_RES006||CM||||20250329135500|||RWASHBURN^Washburn^Danielle^K^^^MD
OBR|1|ESK_ORD006|ESK_RES006|77067^Screening Mammography Bilateral^CPT|||20250328090000||||||||RWASHBURN^Washburn^Danielle^K^^^MD||||||20250329140000|||F
OBX|1|TX|77067^Screening Mammography Bilateral^CPT||IMPRESSION: BI-RADS 1 - Negative. No suspicious masses, calcifications, or architectural distortion. Recommend annual screening mammography.||||||F
OBX|2|ED|PDF^Mammography Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```
