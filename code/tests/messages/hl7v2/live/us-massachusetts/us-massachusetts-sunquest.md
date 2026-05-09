# Sunquest Laboratory Information System - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Chemistry panel results from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250310080000||ORU^R01^ORU_R01|SQ00001|P|2.4|||AL|NE
PID|1||UMMC20123456^^^UMMC^MR||Khoury^Thomas^Richard^^Mr.||19670315|M||2106-3^White^HL70005|45 Lincoln St^^Worcester^MA^01605^US||^PRN^PH^^^508^7749321||M||VN20012345
PV1|1|I|MED^5W^A^UMMC|||48217^Phelan^Margaret^C^MD^^NPI|||||||||IN||||||||||||||||||UMMC||||20250308140000
ORC|RE|ORD10001|SQ50001||CM||||20250310080000|||48217^Phelan^Margaret^C^MD^^NPI
OBR|1|ORD10001|SQ50001|80053^Comprehensive Metabolic Panel^CPT|||20250310060000|||||||||48217^Phelan^Margaret^C^MD^^NPI||||||20250310080000||CH|F
OBX|1|NM|GLU^Glucose^L||156|mg/dL|70-100|H|||F|||20250310080000
OBX|2|NM|BUN^Blood Urea Nitrogen^L||32|mg/dL|7-20|H|||F|||20250310080000
OBX|3|NM|CREAT^Creatinine^L||1.8|mg/dL|0.7-1.3|H|||F|||20250310080000
OBX|4|NM|NA^Sodium^L||138|mmol/L|136-145||||F|||20250310080000
OBX|5|NM|K^Potassium^L||5.4|mmol/L|3.5-5.1|H|||F|||20250310080000
OBX|6|NM|CL^Chloride^L||104|mmol/L|98-106||||F|||20250310080000
OBX|7|NM|CO2^Carbon Dioxide^L||20|mmol/L|23-29|L|||F|||20250310080000
OBX|8|NM|CALCIUM^Calcium^L||9.2|mg/dL|8.5-10.5||||F|||20250310080000
OBX|9|NM|TBILI^Total Bilirubin^L||1.0|mg/dL|0.1-1.2||||F|||20250310080000
OBX|10|NM|ALB^Albumin^L||3.2|g/dL|3.5-5.0|L|||F|||20250310080000
```

---

## 2. ORM^O01 - Stat blood culture order from Lahey Hospital

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|LAB_RECV|LAHEY_HIS|20250312021500||ORM^O01^ORM_O01|SQ00002|P|2.4|||AL|NE
PID|1||LAH30234567^^^LAHEY^MR||Beauregard^Marc^Henri^^Mr.||19720819|M||2106-3^White^HL70005|78 Main St^^Burlington^MA^01803^US||^PRN^PH^^^781^3394718||M||VN30023456
PV1|1|I|MED^3N^B^LAHEY|||71843^Dhawan^Priti^N^MD^^NPI|||||||||IN||||||||||||||||||LAHEY||||20250311180000
ORC|NW|ORD20002||||||^^^20250312022000^^S||20250312021500|||71843^Dhawan^Priti^N^MD^^NPI
OBR|1|ORD20002||87040^Blood Culture^CPT|||20250312022000|||||||S|71843^Dhawan^Priti^N^MD^^NPI|||||||||||1^^^20250312022000^^S
DG1|1||R50.9^Fever, unspecified^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||Temp 39.2C, WBC 18.5, suspect line infection. Please draw from central line and peripheral site.||||||F
```

---

## 3. ORU^R01 - Hematology results from MetroWest Medical Center

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|LAB_RECV|MWMC_HIS|20250314093000||ORU^R01^ORU_R01|SQ00003|P|2.4|||AL|NE
PID|1||MWMC40345678^^^MWMC^MR||Medeiros^Catarina^Isabel^^Ms.||19890504|F||2106-3^White^HL70005|23 Waverly St^^Framingham^MA^01702^US||^PRN^PH^^^508^8572046||S||VN40034567
PV1|1|O|LAB^DRAW^A^MWMC|||62914^Yoon^Helen^J^MD^^NPI|||||||||OUT||||||||||||||||||MWMC||||20250314080000
ORC|RE|ORD30003|SQ60003||CM||||20250314093000|||62914^Yoon^Helen^J^MD^^NPI
OBR|1|ORD30003|SQ60003|85025^CBC with Differential^CPT|||20250314080000|||||||||62914^Yoon^Helen^J^MD^^NPI||||||20250314093000||HM|F
OBX|1|NM|WBC^White Blood Cell Count^L||3.2|x10E3/uL|4.5-11.0|L|||F|||20250314093000
OBX|2|NM|RBC^Red Blood Cell Count^L||3.1|x10E6/uL|4.0-5.5|L|||F|||20250314093000
OBX|3|NM|HGB^Hemoglobin^L||9.8|g/dL|12.0-16.0|L|||F|||20250314093000
OBX|4|NM|HCT^Hematocrit^L||29.5|%|36.0-46.0|L|||F|||20250314093000
OBX|5|NM|PLT^Platelet Count^L||95|x10E3/uL|150-400|L|||F|||20250314093000
OBX|6|NM|NEUT^Neutrophils^L||45|%|40-70||||F|||20250314093000
OBX|7|NM|LYMPH^Lymphocytes^L||40|%|20-40||||F|||20250314093000
OBX|8|NM|MONO^Monocytes^L||8|%|2-8||||F|||20250314093000
OBX|9|NM|EOS^Eosinophils^L||5|%|1-4|H|||F|||20250314093000
OBX|10|NM|BASO^Basophils^L||2|%|0-1|H|||F|||20250314093000
NTE|1||Pancytopenia noted. Recommend peripheral smear review and hematology consultation.
```

---

## 4. OML^O21 - Specimen management message from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|SPEC_RECV|UMMC_HIS|20250316101500||OML^O21^OML_O21|SQ00004|P|2.5|||AL|NE
PID|1||UMMC50456789^^^UMMC^MR||Pelletier^Claude^Rene^^Mr.||19800207|M||2106-3^White^HL70005|156 Park Ave^^Worcester^MA^01609^US||^PRN^PH^^^508^6178834||M||VN50045678
PV1|1|I|SURG^4E^A^UMMC|||53162^Okonkwo^Ngozi^A^MD^^NPI|||||||||IN||||||||||||||||||UMMC||||20250315060000
ORC|NW|ORD40004||||||^^^20250316103000^^R||20250316101500|||53162^Okonkwo^Ngozi^A^MD^^NPI
OBR|1|ORD40004||88305^Surgical Pathology^CPT|||20250316103000||||||||53162^Okonkwo^Ngozi^A^MD^^NPI
SPM|1|SPM001^SUNQUEST||TISS^Tissue^HL70487|||||||P^Patient^HL70369||||LEFT COLON^Left Colon Resection^L|20250315140000|20250316101500
SAC|1||CASS001|||||||||||FORMALIN
```

---

## 5. ORU^R01 - Microbiology culture results from Lahey Hospital

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|LAB_RECV|LAHEY_HIS|20250318160000||ORU^R01^ORU_R01|SQ00005|P|2.4|||AL|NE
PID|1||LAH60567890^^^LAHEY^MR||Wojcik^Helena^Maria^^Ms.||19650921|F||2106-3^White^HL70005|45 Bedford St^^Burlington^MA^01803^US||^PRN^PH^^^781^9785102||M||VN60056789
PV1|1|I|MED^2N^C^LAHEY|||84326^Callahan^Brendan^F^MD^^NPI|||||||||IN||||||||||||||||||LAHEY||||20250316100000
ORC|RE|ORD50005|SQ70005||CM||||20250318160000|||84326^Callahan^Brendan^F^MD^^NPI
OBR|1|ORD50005|SQ70005|87088^Urine Culture^CPT|||20250316120000|||||||||84326^Callahan^Brendan^F^MD^^NPI||||||20250318160000||MB|F
OBX|1|CE|CULTURE^Culture Result^L||Escherichia coli|||A|||F|||20250318160000
OBX|2|NM|COLONY^Colony Count^L||>100000|CFU/mL|<10000|H|||F|||20250318160000
OBX|3|TX|SUSCEPT^Susceptibility^L||Ampicillin: Resistant~Amoxicillin/Clavulanate: Sensitive~Ciprofloxacin: Sensitive~Nitrofurantoin: Sensitive~TMP/SMX: Resistant||||||F|||20250318160000
NTE|1||Significant bacteriuria. E. coli with resistance to ampicillin and TMP/SMX.
```

---

## 6. ORM^O01 - Stat troponin order from MetroWest

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|LAB_RECV|MWMC_HIS|20250320223000||ORM^O01^ORM_O01|SQ00006|P|2.4|||AL|NE
PID|1||MWMC70678901^^^MWMC^MR||Stavridis^Andreas^Nikolaos^^Mr.||19580412|M||2106-3^White^HL70005|89 Concord St^^Lowell^MA^01852^US||^PRN^PH^^^978^4136782||M||VN70067890
PV1|1|E|ED^BED07^A^MWMC|||39571^Reilly^Colleen^S^MD^^NPI|||||||||ER||||||||||||||||||MWMC||||20250320220000
ORC|NW|ORD60006||||||^^^20250320224000^^S||20250320223000|||39571^Reilly^Colleen^S^MD^^NPI
OBR|1|ORD60006||93971^Troponin I^L|||20250320224000|||||||S|39571^Reilly^Colleen^S^MD^^NPI|||||||||||1^^^20250320224000^^S
OBR|2|ORD60006||80048^Basic Metabolic Panel^CPT|||20250320224000|||||||S|39571^Reilly^Colleen^S^MD^^NPI
DG1|1||I20.9^Angina pectoris, unspecified^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||58 yo male with substernal chest pain x 2 hours. Hx HTN, hyperlipidemia, smoking.||||||F
```

---

## 7. ORU^R01 - HbA1c results from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250322091500||ORU^R01^ORU_R01|SQ00007|P|2.4|||AL|NE
PID|1||UMMC80789012^^^UMMC^MR||Desrosiers^Monique^Eliane^^Mrs.||19720830|F||2054-5^Black^HL70005|67 Chandler St^^Worcester^MA^01609^US||^PRN^PH^^^508^3397451||M||VN80078901
PV1|1|O|ENDO^CLINIC^A^UMMC|||27645^Ramachandran^Vikram^P^MD^^NPI|||||||||OUT||||||||||||||||||UMMC||||20250322080000
ORC|RE|ORD70007|SQ80007||CM||||20250322091500|||27645^Ramachandran^Vikram^P^MD^^NPI
OBR|1|ORD70007|SQ80007|83036^Hemoglobin A1c^CPT|||20250322080000|||||||||27645^Ramachandran^Vikram^P^MD^^NPI||||||20250322091500||CH|F
OBX|1|NM|HBA1C^Hemoglobin A1c^L||9.2|%|4.0-5.6|HH|||F|||20250322091500
OBX|2|NM|EGLUC^Estimated Average Glucose^L||218|mg/dL|<117|H|||F|||20250322091500
NTE|1||HbA1c significantly above target. Diabetes management optimization strongly recommended.
```

---

## 8. ORU^R01 - Coagulation results with embedded PDF from Lahey

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|LAB_RECV|LAHEY_HIS|20250324140000||ORU^R01^ORU_R01|SQ00008|P|2.4|||AL|NE
PID|1||LAH90890123^^^LAHEY^MR||Sullivan^Declan^James^^Mr.||19500314|M||2106-3^White^HL70005|34 Middlesex Tpke^^Burlington^MA^01803^US||^PRN^PH^^^781^8576293||W||VN90089012
PV1|1|I|CARD^4S^A^LAHEY|||95718^Papadimitriou^Elena^K^MD^^NPI|||||||||IN||||||||||||||||||LAHEY||||20250322160000
ORC|RE|ORD80008|SQ90008||CM||||20250324140000|||95718^Papadimitriou^Elena^K^MD^^NPI
OBR|1|ORD80008|SQ90008|85610^Coagulation Panel^CPT|||20250324120000|||||||||95718^Papadimitriou^Elena^K^MD^^NPI||||||20250324140000||HM|F
OBX|1|NM|PT^Prothrombin Time^L||24.5|seconds|11.0-13.5|HH|||F|||20250324140000
OBX|2|NM|INR^International Normalized Ratio^L||2.8||0.9-1.1|H|||F|||20250324140000
OBX|3|NM|PTT^Partial Thromboplastin Time^L||38.2|seconds|25.0-35.0|H|||F|||20250324140000
OBX|4|NM|DDIMER^D-Dimer^L||2.45|mg/L FEU|<0.50|HH|||F|||20250324140000
OBX|5|ED|COAG_RPT^Coagulation Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
NTE|1||Supratherapeutic INR on warfarin. D-Dimer markedly elevated. Clinical correlation for thrombosis vs DIC recommended.
```

---

## 9. OML^O21 - Specimen accessioning from MetroWest

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|SPEC_RECV|MWMC_HIS|20250326070000||OML^O21^OML_O21|SQ00009|P|2.5|||AL|NE
PID|1||MWMC01901234^^^MWMC^MR||Brennan^Siobhan^Maeve^^Ms.||19910825|F||2106-3^White^HL70005|45 Temple St^^Quincy^MA^02169^US||^PRN^PH^^^617^7742938||S||VN01090123
PV1|1|O|LAB^DRAW^A^MWMC|||46283^Ferreira^Antonio^R^MD^^NPI|||||||||OUT||||||||||||||||||MWMC||||20250326063000
ORC|NW|ORD90009||||||^^^20250326073000^^R||20250326070000|||46283^Ferreira^Antonio^R^MD^^NPI
OBR|1|ORD90009||80061^Lipid Panel^CPT|||20250326073000||||||||46283^Ferreira^Antonio^R^MD^^NPI
OBR|2|ORD90009||84443^TSH^CPT|||20250326073000||||||||46283^Ferreira^Antonio^R^MD^^NPI
SPM|1|SPM002^SUNQUEST||BLD^Blood^HL70487|||SST^Serum Separator Tube^HL70488||||||P^Patient^HL70369||20250326063000
SPM|2|SPM003^SUNQUEST||BLD^Blood^HL70487|||LAV^Lavender Top^HL70488||||||P^Patient^HL70369||20250326063000
```

---

## 10. ORU^R01 - Toxicology screen from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250328032000||ORU^R01^ORU_R01|SQ00010|P|2.4|||AL|NE
PID|1||UMMC02012345^^^UMMC^MR||Gomes^Rafael^Eduardo^^Mr.||19950216|M||2131-1^Hispanic^HL70005|234 Main St^^Brockton^MA^02301^US||^PRN^PH^^^508^7747183||S||VN02001234
PV1|1|E|ED^BED14^A^UMMC|||58491^Volkov^Natalia^S^MD^^NPI|||||||||ER||||||||||||||||||UMMC||||20250328020000
ORC|RE|ORD01010|SQ11010||CM||||20250328032000|||58491^Volkov^Natalia^S^MD^^NPI
OBR|1|ORD01010|SQ11010|80307^Drug Screen Panel^CPT|||20250328022000|||||||||58491^Volkov^Natalia^S^MD^^NPI||||||20250328032000||TOX|F
OBX|1|ST|AMP^Amphetamines^L||Negative||Negative||||F|||20250328032000
OBX|2|ST|BARB^Barbiturates^L||Negative||Negative||||F|||20250328032000
OBX|3|ST|BENZ^Benzodiazepines^L||Positive||Negative|A|||F|||20250328032000
OBX|4|ST|COCAINE^Cocaine Metabolite^L||Negative||Negative||||F|||20250328032000
OBX|5|ST|OPIATES^Opiates^L||Positive||Negative|A|||F|||20250328032000
OBX|6|ST|THC^Cannabinoids^L||Positive||Negative|A|||F|||20250328032000
OBX|7|ST|PCP^Phencyclidine^L||Negative||Negative||||F|||20250328032000
OBX|8|NM|ETOH^Ethanol Level^L||185|mg/dL|0-10|HH|||F|||20250328032000
NTE|1||Positive for benzodiazepines, opiates, and cannabinoids. Ethanol level significantly elevated.
```

---

## 11. ORM^O01 - Pathology tissue order from Lahey Hospital

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|PATH_RECV|LAHEY_HIS|20250330110000||ORM^O01^ORM_O01|SQ00011|P|2.4|||AL|NE
PID|1||LAH03123456^^^LAHEY^MR||Diamantopoulos^Elias^Christos^^Mr.||19680714|M||2106-3^White^HL70005|56 Winn St^^Peabody^MA^01960^US||^PRN^PH^^^978^3398561||M||VN03012345
PV1|1|I|SURG^5W^A^LAHEY|||72514^Thibodeau^Roland^G^MD^^NPI|||||||||IN||||||||||||||||||LAHEY||||20250330060000
ORC|NW|ORD11011||||||^^^20250330120000^^R||20250330110000|||72514^Thibodeau^Roland^G^MD^^NPI
OBR|1|ORD11011||88305^Surgical Pathology^CPT|||20250330120000||||||||72514^Thibodeau^Roland^G^MD^^NPI
OBX|1|TX|CLIN_INFO^Clinical Information^L||Right colectomy for ascending colon mass. CT showed 4.5 cm mass. CEA elevated at 12.5. No evidence of distant metastasis on imaging.||||||F
OBX|2|TX|SPEC_DESC^Specimen Description^L||Right hemicolectomy specimen||||||F
```

---

## 12. ORU^R01 - Cerebrospinal fluid analysis from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250401143000||ORU^R01^ORU_R01|SQ00012|P|2.4|||AL|NE
PID|1||UMMC04234567^^^UMMC^MR||Novotny^Pavel^Jiri^^Mr.||19450603|M||2106-3^White^HL70005|89 Shrewsbury St^^Worcester^MA^01604^US||^PRN^PH^^^508^8574216||W||VN04023456
PV1|1|I|NEUR^3E^B^UMMC|||36829^Gutierrez^Carmen^E^MD^^NPI|||||||||IN||||||||||||||||||UMMC||||20250401080000
ORC|RE|ORD12012|SQ22012||CM||||20250401143000|||36829^Gutierrez^Carmen^E^MD^^NPI
OBR|1|ORD12012|SQ22012|89050^CSF Cell Count^CPT|||20250401100000|||||||||36829^Gutierrez^Carmen^E^MD^^NPI||||||20250401143000||CH|F
OBX|1|NM|CSF_WBC^CSF WBC Count^L||285|cells/uL|0-5|HH|||F|||20250401143000
OBX|2|NM|CSF_RBC^CSF RBC Count^L||2|cells/uL|0||||F|||20250401143000
OBX|3|NM|CSF_PROT^CSF Protein^L||128|mg/dL|15-45|HH|||F|||20250401143000
OBX|4|NM|CSF_GLUC^CSF Glucose^L||32|mg/dL|40-70|L|||F|||20250401143000
OBX|5|NM|CSF_NEUT^CSF Neutrophils^L||82|%|0-6|HH|||F|||20250401143000
OBX|6|NM|CSF_LYMPH^CSF Lymphocytes^L||15|%||||F|||20250401143000
OBX|7|ST|CSF_GRAM^CSF Gram Stain^L||Gram positive diplococci seen||||||F|||20250401143000
NTE|1||CSF profile consistent with bacterial meningitis. Gram stain positive. Cultures pending.
```

---

## 13. ORU^R01 - Cardiac biomarkers from MetroWest

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|LAB_RECV|MWMC_HIS|20250403050000||ORU^R01^ORU_R01|SQ00013|P|2.4|||AL|NE
PID|1||MWMC05345678^^^MWMC^MR||Kazantzakis^Petros^Yannis^^Mr.||19580412|M||2106-3^White^HL70005|12 Walnut St^^Newton^MA^02460^US||^PRN^PH^^^617^5089314||M||VN05034567
PV1|1|I|CCU^BED02^A^MWMC|||81643^Flanagan^Deirdre^A^MD^^NPI|||||||||IN||||||||||||||||||MWMC||||20250320230000
ORC|RE|ORD13013|SQ33013||CM||||20250403050000|||81643^Flanagan^Deirdre^A^MD^^NPI
OBR|1|ORD13013|SQ33013|CARDIAC^Cardiac Biomarkers^L|||20250403040000|||||||||81643^Flanagan^Deirdre^A^MD^^NPI||||||20250403050000||CH|F
OBX|1|NM|TROP^Troponin I^L||2.45|ng/mL|0.00-0.04|HH|||F|||20250403050000
OBX|2|NM|BNP^Brain Natriuretic Peptide^L||1250|pg/mL|0-100|HH|||F|||20250403050000
OBX|3|NM|CK^Creatine Kinase^L||520|U/L|30-200|HH|||F|||20250403050000
OBX|4|NM|CKMB^CK-MB^L||45.8|ng/mL|0.0-5.0|HH|||F|||20250403050000
OBX|5|NM|MYO^Myoglobin^L||380|ng/mL|0-85|HH|||F|||20250403050000
NTE|1||Markedly elevated cardiac biomarkers consistent with acute STEMI. Cardiology notified.
```

---

## 14. ORM^O01 - Prenatal panel order from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250405091000||ORM^O01^ORM_O01|SQ00014|P|2.4|||AL|NE
PID|1||UMMC06456789^^^UMMC^MR||Osei^Abena^Nyarko^^Mrs.||19930610|F||2054-5^Black^HL70005|45 Pleasant St^^Worcester^MA^01609^US||^PRN^PH^^^508^4137829||M||VN06045678
PV1|1|O|OB^CLINIC^A^UMMC|||29473^Kowalski^Anna^T^MD^^NPI|||||||||OUT||||||||||||||||||UMMC||||20250405083000
ORC|NW|ORD14014||||||^^^20250405093000^^R||20250405091000|||29473^Kowalski^Anna^T^MD^^NPI
OBR|1|ORD14014||80055^Prenatal Panel^CPT|||20250405093000||||||||29473^Kowalski^Anna^T^MD^^NPI
OBR|2|ORD14014||86850^Antibody Screen^CPT|||20250405093000||||||||29473^Kowalski^Anna^T^MD^^NPI
OBR|3|ORD14014||86762^Rubella Antibody^CPT|||20250405093000||||||||29473^Kowalski^Anna^T^MD^^NPI
OBR|4|ORD14014||87340^Hepatitis B Surface Antigen^CPT|||20250405093000||||||||29473^Kowalski^Anna^T^MD^^NPI
DG1|1||Z34.01^Encounter for supervision of normal first pregnancy^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||G1P0, 10 weeks by LMP. Initial prenatal labs.||||||F
```

---

## 15. ORU^R01 - Pathology report with embedded PDF from Lahey

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|PATH_RECV|LAHEY_HIS|20250407163000||ORU^R01^ORU_R01|SQ00015|P|2.4|||AL|NE
PID|1||LAH03123456^^^LAHEY^MR||Diamantopoulos^Elias^Christos^^Mr.||19680714|M||2106-3^White^HL70005|56 Winn St^^Peabody^MA^01960^US||^PRN^PH^^^978^3398561||M||VN03012345
PV1|1|I|SURG^5W^A^LAHEY|||72514^Thibodeau^Roland^G^MD^^NPI|||||||||IN||||||||||||||||||LAHEY||||20250330060000
ORC|RE|ORD15015|PATH33015||CM||||20250407163000|||72514^Thibodeau^Roland^G^MD^^NPI
OBR|1|ORD15015|PATH33015|88305^Surgical Pathology^CPT|||20250330120000|||||||||72514^Thibodeau^Roland^G^MD^^NPI||||||20250407163000||AP|F
OBX|1|TX|PATH_DX^Pathology Diagnosis^L||RIGHT COLON, HEMICOLECTOMY:~Moderately differentiated adenocarcinoma, 4.5 cm greatest dimension.~Tumor invades through muscularis propria into pericolonic fat (pT3).~14 lymph nodes examined, 2 positive for metastatic carcinoma (pN1b).~Proximal and distal margins negative.~Lymphovascular invasion present. Perineural invasion absent.||||||F|||20250407163000
OBX|2|TX|PATH_STAGE^Pathological Stage^L||AJCC 8th Edition: pT3 N1b M0, Stage IIIB||||||F|||20250407163000
OBX|3|ED|PATH_PDF^Surgical Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
NTE|1||Recommend molecular testing for MSI/MMR status and KRAS/NRAS/BRAF given stage III disease.
```

---

## 16. ORU^R01 - Liver function tests from MetroWest

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|LAB_RECV|MWMC_HIS|20250409101500||ORU^R01^ORU_R01|SQ00016|P|2.4|||AL|NE
PID|1||MWMC07567890^^^MWMC^MR||Gallagher^Erin^Therese^^Mrs.||19710908|F||2106-3^White^HL70005|123 Edgell Rd^^Waltham^MA^02451^US||^PRN^PH^^^781^6179482||M||VN07056789
PV1|1|O|GI^CLINIC^A^MWMC|||57826^Nascimento^Carlos^M^MD^^NPI|||||||||OUT||||||||||||||||||MWMC||||20250409090000
ORC|RE|ORD16016|SQ44016||CM||||20250409101500|||57826^Nascimento^Carlos^M^MD^^NPI
OBR|1|ORD16016|SQ44016|80076^Hepatic Function Panel^CPT|||20250409090000|||||||||57826^Nascimento^Carlos^M^MD^^NPI||||||20250409101500||CH|F
OBX|1|NM|ALT^Alanine Aminotransferase^L||185|U/L|7-56|HH|||F|||20250409101500
OBX|2|NM|AST^Aspartate Aminotransferase^L||142|U/L|10-40|HH|||F|||20250409101500
OBX|3|NM|ALKP^Alkaline Phosphatase^L||345|U/L|44-147|HH|||F|||20250409101500
OBX|4|NM|TBILI^Total Bilirubin^L||3.8|mg/dL|0.1-1.2|HH|||F|||20250409101500
OBX|5|NM|DBILI^Direct Bilirubin^L||2.9|mg/dL|0.0-0.3|HH|||F|||20250409101500
OBX|6|NM|ALB^Albumin^L||2.8|g/dL|3.5-5.0|L|||F|||20250409101500
OBX|7|NM|TP^Total Protein^L||6.0|g/dL|6.3-7.9|L|||F|||20250409101500
OBX|8|NM|GGT^Gamma-Glutamyl Transferase^L||289|U/L|9-48|HH|||F|||20250409101500
NTE|1||Cholestatic pattern with markedly elevated ALP and direct bilirubin. ERCP may be indicated.
```

---

## 17. ORM^O01 - Molecular testing order from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|MOL_RECV|UMMC_HIS|20250411140000||ORM^O01^ORM_O01|SQ00017|P|2.4|||AL|NE
PID|1||UMMC08678901^^^UMMC^MR||Nguyen^Thanh^Huong^^Ms.||19850322|F||2028-9^Asian^HL70005|78 Grafton St^^Worcester^MA^01604^US||^PRN^PH^^^508^7743892||S||VN08067890
PV1|1|O|ONC^CLINIC^A^UMMC|||63479^Donahue^Kevin^R^MD^^NPI|||||||||OUT||||||||||||||||||UMMC||||20250411130000
ORC|NW|ORD17017||||||^^^20250412080000^^R||20250411140000|||63479^Donahue^Kevin^R^MD^^NPI
OBR|1|ORD17017||81210^BRCA1/BRCA2 Gene Analysis^CPT|||20250412080000||||||||63479^Donahue^Kevin^R^MD^^NPI
DG1|1||C50.912^Malignant neoplasm of unspecified site of left female breast^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||47 yo female with newly diagnosed left breast cancer, grade 3 IDC. Family history: mother with ovarian cancer at age 52. Genetic counseling completed.||||||F
```

---

## 18. ORU^R01 - Renal function panel from Lahey Hospital

```
MSH|^~\&|SUNQUEST|LAHEY^3002^NPI|LAB_RECV|LAHEY_HIS|20250413091000||ORU^R01^ORU_R01|SQ00018|P|2.4|||AL|NE
PID|1||LAH09789012^^^LAHEY^MR||Fitzpatrick^Colin^Edward^^Mr.||19600425|M||2106-3^White^HL70005|23 Cambridge St^^Salem^MA^01970^US||^PRN^PH^^^978^8574561||M||VN09078901
PV1|1|O|NEPH^CLINIC^A^LAHEY|||42198^Chandrasekhar^Arjun^V^MD^^NPI|||||||||OUT||||||||||||||||||LAHEY||||20250413080000
ORC|RE|ORD18018|SQ55018||CM||||20250413091000|||42198^Chandrasekhar^Arjun^V^MD^^NPI
OBR|1|ORD18018|SQ55018|80069^Renal Function Panel^CPT|||20250413080000|||||||||42198^Chandrasekhar^Arjun^V^MD^^NPI||||||20250413091000||CH|F
OBX|1|NM|BUN^Blood Urea Nitrogen^L||45|mg/dL|7-20|HH|||F|||20250413091000
OBX|2|NM|CREAT^Creatinine^L||3.2|mg/dL|0.7-1.3|HH|||F|||20250413091000
OBX|3|NM|GFR^Estimated GFR^L||18|mL/min/1.73m2|>60|L|||F|||20250413091000
OBX|4|NM|NA^Sodium^L||136|mmol/L|136-145||||F|||20250413091000
OBX|5|NM|K^Potassium^L||5.8|mmol/L|3.5-5.1|H|||F|||20250413091000
OBX|6|NM|PHOS^Phosphorus^L||5.9|mg/dL|2.5-4.5|H|||F|||20250413091000
OBX|7|NM|CA^Calcium^L||8.1|mg/dL|8.5-10.5|L|||F|||20250413091000
OBX|8|NM|URIC^Uric Acid^L||9.8|mg/dL|3.5-7.2|H|||F|||20250413091000
NTE|1||Stage 4 CKD (GFR 18). Hyperkalemia and hyperphosphatemia present. Nephrology follow-up recommended.
```

---

## 19. ORU^R01 - Thyroid function with reflex from MetroWest

```
MSH|^~\&|SUNQUEST|MWMC^3003^NPI|LAB_RECV|MWMC_HIS|20250415100000||ORU^R01^ORU_R01|SQ00019|P|2.4|||AL|NE
PID|1||MWMC10890123^^^MWMC^MR||Kedzierska^Marta^Zofia^^Ms.||19880117|F||2106-3^White^HL70005|56 Union Ave^^Marlborough^MA^01752^US||^PRN^PH^^^508^9784517||S||VN10089012
PV1|1|O|ENDO^CLINIC^A^MWMC|||85174^Tavares^Joana^F^MD^^NPI|||||||||OUT||||||||||||||||||MWMC||||20250415083000
ORC|RE|ORD19019|SQ66019||CM||||20250415100000|||85174^Tavares^Joana^F^MD^^NPI
OBR|1|ORD19019|SQ66019|84443^Thyroid Panel with Reflex^CPT|||20250415083000|||||||||85174^Tavares^Joana^F^MD^^NPI||||||20250415100000||CH|F
OBX|1|NM|TSH^Thyroid Stimulating Hormone^L||0.05|mIU/L|0.4-4.0|L|||F|||20250415100000
OBX|2|NM|FT4^Free T4^L||3.8|ng/dL|0.8-1.8|HH|||F|||20250415100000
OBX|3|NM|FT3^Free T3^L||8.2|pg/mL|2.3-4.2|HH|||F|||20250415100000
OBX|4|NM|T3TOTAL^Total T3^L||325|ng/dL|80-200|HH|||F|||20250415100000
NTE|1||TSH suppressed with elevated free T4 and T3 consistent with hyperthyroidism. TSI/TRAb recommended.
```

---

## 20. ORU^R01 - Vitamin D and calcium panel from UMass Memorial

```
MSH|^~\&|SUNQUEST|UMMC^3001^NPI|LAB_RECV|UMMC_HIS|20250417083000||ORU^R01^ORU_R01|SQ00020|P|2.4|||AL|NE
PID|1||UMMC11901234^^^UMMC^MR||Bouchard^Lorraine^Theresa^^Mrs.||19680901|F||2106-3^White^HL70005|34 Elm St^^Shrewsbury^MA^01545^US||^PRN^PH^^^508^6173847||M||VN11090123
PV1|1|O|ENDO^CLINIC^A^UMMC|||74162^Anand^Shalini^D^MD^^NPI|||||||||OUT||||||||||||||||||UMMC||||20250417073000
ORC|RE|ORD20020|SQ77020||CM||||20250417083000|||74162^Anand^Shalini^D^MD^^NPI
OBR|1|ORD20020|SQ77020|82306^Vitamin D 25-Hydroxy^CPT|||20250417073000|||||||||74162^Anand^Shalini^D^MD^^NPI||||||20250417083000||CH|F
OBX|1|NM|VITD^Vitamin D, 25-Hydroxy^L||12|ng/mL|30-100|L|||F|||20250417083000
OBX|2|NM|CA^Calcium^L||10.8|mg/dL|8.5-10.5|H|||F|||20250417083000
OBX|3|NM|CA_ION^Ionized Calcium^L||5.6|mg/dL|4.6-5.3|H|||F|||20250417083000
OBX|4|NM|PTH^Parathyroid Hormone^L||125|pg/mL|15-65|HH|||F|||20250417083000
OBX|5|NM|PHOS^Phosphorus^L||2.1|mg/dL|2.5-4.5|L|||F|||20250417083000
NTE|1||Vitamin D deficiency with elevated PTH and calcium. Pattern suggests primary hyperparathyroidism with concomitant vitamin D deficiency.
```
