# MIIC (Minnesota Immunization Information Connection) - real HL7v2 ER7 messages

## 1. VXU^V04 - Childhood DTaP vaccination at Hennepin Healthcare

```
MSH|^~\&|HCMC_EHR|HCMC|MIIC|MNDOH|20250415101530||VXU^V04^VXU_V04|HCMC20250415101530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E60234567^^^HCMC^MRN~2025MN0012345^^^MIIC^SR||HASSAN^Amira^Fatima^^^^L||20230915|F||2054-5^Black or African American^CDCREC|2814 Park Ave^^Minneapolis^MN^55407^US^L||^PRN^PH^^^612^8714567||som^Somali^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||HENNEPIN HEALTHCARE^^40001|6928041573^Lor^Pheng^K^^MD^^^NPI^^^^L
NK1|1|HASSAN^Fartun^Aden^^Mrs.|MTH^Mother^HL70063|2814 Park Ave^^Minneapolis^MN^55407^US|^PRN^PH^^^612^8714567
ORC|RE||MIIC20250415001^MIIC|||||||6928041573^Lor^Pheng^K^^MD^^^NPI^^^^L
RXA|0|1|20250415100000||20^DTaP^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||U1234AA^20260415^MSD|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|20^DTaP^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20200101||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250415||||||F
```

---

## 2. VXU^V04 - Infant Hepatitis B vaccination at Children's Minnesota

```
MSH|^~\&|CHILDMN_EHR|CHILDMNMPLS|MIIC|MNDOH|20250125140530||VXU^V04^VXU_V04|CMM20250125140530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E80012345^^^CHILDMN^MRN~2025MN0023456^^^MIIC^SR||YANG^Baby Girl^^^^^L||20250125|F||2028-9^Asian^CDCREC|4215 Blaisdell Ave^^Minneapolis^MN^55409^US^L||^PRN^PH^^^612^8254567||hmn^Hmong^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||CHILDREN'S MINNESOTA MINNEAPOLIS^^80001|3960517284^Vue^Koua^M^^MD^^^NPI^^^^L
NK1|1|YANG^Pahoua^Lia^^Mrs.|MTH^Mother^HL70063|4215 Blaisdell Ave^^Minneapolis^MN^55409^US|^PRN^PH^^^612^8254567
ORC|RE||MIIC20250125001^MIIC|||||||3960517284^Vue^Koua^M^^MD^^^NPI^^^^L
RXA|0|1|20250125130000||08^Hep B, adolescent or pediatric^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||U5678BB^20260601^MSD|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|08^Hep B, adolescent or pediatric^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20200101||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250125||||||F
```

---

## 3. VXU^V04 - MMR vaccination at Mayo Clinic Rochester (VFC eligible)

```
MSH|^~\&|MAYOCLINIC_EHR|MAYOCLINIC|MIIC|MNDOH|20250610091530||VXU^V04^VXU_V04|MCR20250610091530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E10567890^^^MAYO^MRN~2025MN0034567^^^MIIC^SR||FARAH^Maryan^Deeqa^^^^L||20240310|F||2054-5^Black or African American^CDCREC|1820 2nd St SW^^Rochester^MN^55902^US^L||^PRN^PH^^^507^2891234||som^Somali^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||MAYO CLINIC ROCHESTER^^10001|3187294560^Reinhardt^Thomas^C^^MD^^^NPI^^^^L
NK1|1|FARAH^Sagal^Hodan^^Mrs.|MTH^Mother^HL70063|1820 2nd St SW^^Rochester^MN^55902^US|^PRN^PH^^^507^2891234
ORC|RE||MIIC20250610001^MIIC|||||||3187294560^Reinhardt^Thomas^C^^MD^^^NPI^^^^L
RXA|0|1|20250610090000||03^MMR^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001|2960718345^Harstad^Judith^K^^MD^^^NPI|||||U9012CC^20260610^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|03^MMR^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20200101||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250610||||||F
```

---

## 4. VXU^V04 - Influenza vaccination at Allina Health Plymouth

```
MSH|^~\&|ALLINA_EHR|ALLINAPLYM|MIIC|MNDOH|20251015143045||VXU^V04^VXU_V04|APL20251015143045001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E20789012^^^ALLINA^MRN~2025MN0045678^^^MIIC^SR||SOLBERG^Dorothy^Violet^^^^L||19580220|F||2106-3^White^CDCREC|3720 Vicksburg Ln N^^Plymouth^MN^55447^US^L||^PRN^PH^^^763^5594567||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||ALLINA HEALTH PLYMOUTH CLINIC^^20002|3071425986^Engel^Patricia^R^^MD^^^NPI^^^^L
NK1|1|SOLBERG^Arvid^Gunnar^^Mr.|SPO^Spouse^HL70063|3720 Vicksburg Ln N^^Plymouth^MN^55447^US|^PRN^PH^^^763^5594568
ORC|RE||MIIC20251015001^MIIC|||||||3071425986^Engel^Patricia^R^^MD^^^NPI^^^^L
RXA|0|1|20251015142000||197^Influenza, high-dose, quadrivalent^CVX|0.7|mL^milliliter^UCUM||00^New immunization record^NIP001|3071425986^Engel^Patricia^R^^MD^^^NPI|||||W3456DD^20260415^SNF|SNF^Sanofi Pasteur^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|197^Influenza, high-dose, quadrivalent^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20240815||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20251015||||||F
```

---

## 5. VXU^V04 - COVID-19 booster at HealthPartners Bloomington

```
MSH|^~\&|HPARTNERS_EHR|HPBLOOM|MIIC|MNDOH|20251101100530||VXU^V04^VXU_V04|HPB20251101100530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E40890123^^^HPARTNERS^MRN~2025MN0056789^^^MIIC^SR||MUSSE^Yasmin^Ifrah^^^^L||19790305|F||2054-5^Black or African American^CDCREC|6801 Normandale Rd^^Bloomington^MN^55437^US^L||^PRN^PH^^^952^8831234||som^Somali^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||HEALTHPARTNERS BLOOMINGTON^^30002|5287340916^Braun^Lawrence^T^^MD^^^NPI^^^^L
ORC|RE||MIIC20251101001^MIIC|||||||5287340916^Braun^Lawrence^T^^MD^^^NPI^^^^L
RXA|0|1|20251101100000||308^COVID-19, mRNA, LNP-S, bivalent, PF, 30 mcg/0.3 mL^CVX|0.3|mL^milliliter^UCUM||00^New immunization record^NIP001|5287340916^Braun^Lawrence^T^^MD^^^NPI|||||X7890EE^20260501^MOD|MOD^Moderna US Inc^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|308^COVID-19, mRNA, LNP-S, bivalent^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20241001||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20251101||||||F
```

---

## 6. VXU^V04 - Tdap vaccination at Fairview Clinics Edina

```
MSH|^~\&|FVWEDINA_EHR|FVWEDINA|MIIC|MNDOH|20250820091530||VXU^V04^VXU_V04|FED20250820091530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E30890123^^^FVWEDINA^MRN~2025MN0067890^^^MIIC^SR||THAO^Xai^Neng^^^^L||19910507|M||2028-9^Asian^CDCREC|3845 Vicksburg Ln^^Plymouth^MN^55447^US^L||^PRN^PH^^^763^5551234||hmn^Hmong^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||FAIRVIEW CLINICS EDINA^^40002|3071425986^Engel^Patricia^R^^MD^^^NPI^^^^L
ORC|RE||MIIC20250820001^MIIC|||||||3071425986^Engel^Patricia^R^^MD^^^NPI^^^^L
RXA|0|1|20250820090000||115^Tdap^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||Y2345FF^20260820^GSK|SKB^GlaxoSmithKline^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|115^Tdap^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20200101||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250820||||||F
```

---

## 7. VXU^V04 - IPV vaccination at Essentia Health Duluth (VFC eligible)

```
MSH|^~\&|ESSENTIA_EHR|ESSENTIADL|MIIC|MNDOH|20250714102045||VXU^V04^VXU_V04|EDL20250714102045001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E50901234^^^ESSENTIA^MRN~2025MN0078901^^^MIIC^SR||ELLINGSON^Nolan^Bjorn^^^^L||20240201|M||2106-3^White^CDCREC|1028 E 2nd St^^Duluth^MN^55805^US^L||^PRN^PH^^^218^7281456||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||ESSENTIA HEALTH DULUTH^^30001|2065138947^Tveit^Henrik^S^^MD^^^NPI^^^^L
NK1|1|ELLINGSON^Donna^Astrid^^Mrs.|MTH^Mother^HL70063|1028 E 2nd St^^Duluth^MN^55805^US|^PRN^PH^^^218^7281456
ORC|RE||MIIC20250714001^MIIC|||||||2065138947^Tveit^Henrik^S^^MD^^^NPI^^^^L
RXA|0|1|20250714101000||10^IPV^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||Z6789GG^20260714^SNF|SNF^Sanofi Pasteur^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|10^IPV^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V03^VFC eligible - Uninsured^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20191029||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250714||||||F
```

---

## 8. QBP^Q11 - Immunization history query to MIIC from CentraCare

```
MSH|^~\&|CCSTCLOUD_EHR|CCSTCLOUD|MIIC|MNDOH|20250312081530||QBP^Q11^QBP_Q11|CC20250312081530001|P|2.5.1|||ER|AL|||||Z34^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20250312001|MRN30012345^^^CC^MRN~2024MN0098765^^^MIIC^SR|SCHULTZ^Vernon^Roy^^Mr.|19550818|M|3421 Clearwater Rd^^St. Cloud^MN^56301^US
RCP|I|5^RD&Records&HL70126
```

---

## 9. RSP^K11 - Immunization history response from MIIC to CentraCare

```
MSH|^~\&|MIIC|MNDOH|CCSTCLOUD_EHR|CCSTCLOUD|20250312081545||RSP^K11^RSP_K11|MIIC20250312081545001|P|2.5.1|||ER|AL|||||Z32^CDCPHINVS
MSA|AA|CC20250312081530001
QAK|Q20250312001|OK|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20250312001|MRN30012345^^^CC^MRN~2024MN0098765^^^MIIC^SR|SCHULTZ^Vernon^Roy^^Mr.|19550818|M|3421 Clearwater Rd^^St. Cloud^MN^56301^US
PID|1||2024MN0098765^^^MIIC^SR~MRN30012345^^^CC^MRN||SCHULTZ^Vernon^Roy^^Mr.||19550818|M||2106-3^White^CDCREC|3421 Clearwater Rd^^St. Cloud^MN^56301^US||^PRN^PH^^^320^2514567||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC
PD1|||CENTRACARE ST. CLOUD^^60002|1472503896^Daud^Mahad^E^^MD^^^NPI^^^^L|||||||02^Reminder/recall - any method^HL70215|N^No^HL70136||A^Active^HL70441
ORC|RE||MIICORD20230915001^MIIC
RXA|0|1|20230915100000||197^Influenza, high-dose, quadrivalent^CVX|0.7|mL^milliliter^UCUM||00^New immunization record^NIP001|||||||||SNF^Sanofi Pasteur^MVX||||CP^Complete^HL70322
OBX|1|CE|30956-7^Vaccine Type^LN|1|197^Influenza, high-dose, quadrivalent^CVX||||||F
ORC|RE||MIICORD20240301001^MIIC
RXA|0|1|20240301100000||33^Pneumococcal polysaccharide PPV23^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001|||||||||MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
OBX|2|CE|30956-7^Vaccine Type^LN|2|33^Pneumococcal polysaccharide PPV23^CVX||||||F
ORC|RE||MIICORD20241015001^MIIC
RXA|0|1|20241015100000||197^Influenza, high-dose, quadrivalent^CVX|0.7|mL^milliliter^UCUM||00^New immunization record^NIP001|||||||||SNF^Sanofi Pasteur^MVX||||CP^Complete^HL70322
OBX|3|CE|30956-7^Vaccine Type^LN|3|197^Influenza, high-dose, quadrivalent^CVX||||||F
OBX|4|ED|11369-6^Immunization History Report PDF^LN|4|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1JSUMgSW1tdW5pemF0aW9uIEhpc3RvcnkgUmVwb3J0KQovQXV0aG9yIChNaW5uZXNvdGEgRGVwYXJ0bWVudCBvZiBIZWFsdGgpCi9DcmVhdG9yIChNSUlDIFJlcG9ydCBHZW5lcmF0b3IpCi9Qcm9kdWNlciAoTUlJQyBQcmludCBTZXJ2aWNlKQovQ3JlYXRpb25EYXRlIChEOjIwMjUwMzEyMDgxNTQ1KQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgo+PgplbmRvYmoK||||||F
```

---

## 10. ACK - Positive acknowledgment from MIIC for VXU submission

```
MSH|^~\&|MIIC|MNDOH|HCMC_EHR|HCMC|20250415101545||ACK^V04^ACK|MIIC20250415101545001|P|2.5.1|||ER|AL|||||Z23^CDCPHINVS
MSA|AA|HCMC20250415101530001||0
```

---

## 11. ACK - Application error acknowledgment from MIIC

```
MSH|^~\&|MIIC|MNDOH|ALLINA_EHR|ALLINAPLYM|20251015143100||ACK^V04^ACK|MIIC20251015143100001|P|2.5.1|||ER|AL|||||Z23^CDCPHINVS
MSA|AE|APL20251015143045001||1
ERR||PID^1^3|101^Required field missing^HL70357|E||||Patient identifier is required for MIIC submission
```

---

## 12. VXU^V04 - Hepatitis A vaccination at CentraCare St. Cloud

```
MSH|^~\&|CCSTCLOUD_EHR|CCSTCLOUD|MIIC|MNDOH|20250520091530||VXU^V04^VXU_V04|CCS20250520091530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||MRN30123456^^^CC^MRN~2025MN0089012^^^MIIC^SR||CHANG^Mai^Ying^^^^L||20240115|F||2028-9^Asian^CDCREC|1020 Division St^^Waite Park^MN^56387^US^L||^PRN^PH^^^320^2534567||hmn^Hmong^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||CENTRACARE ST. CLOUD^^60002|1472503896^Daud^Mahad^E^^MD^^^NPI^^^^L
NK1|1|CHANG^Pang^Lia^^Mrs.|MTH^Mother^HL70063|1020 Division St^^Waite Park^MN^56387^US|^PRN^PH^^^320^2534567
ORC|RE||MIIC20250520001^MIIC|||||||1472503896^Daud^Mahad^E^^MD^^^NPI^^^^L
RXA|0|1|20250520090000||83^Hep A, ped/adol, 2 dose^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||A3456HH^20260520^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|83^Hep A, ped/adol, 2 dose^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20200101||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250520||||||F
```

---

## 13. VXU^V04 - Varicella vaccination at Olmsted Medical Center

```
MSH|^~\&|OMC_EHR|OMCROCH|MIIC|MNDOH|20250903101530||VXU^V04^VXU_V04|OMC20250903101530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||MRN40056789^^^OMC^MRN~2025MN0090123^^^MIIC^SR||STORLIE^Ava^Ingrid^^^^L||20240601|F||2106-3^White^CDCREC|2510 Broadway Ave N^^Rochester^MN^55906^US^L||^PRN^PH^^^507^2873456||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||OLMSTED MEDICAL CENTER^^50002|6305129847^Bjornson^Dagny^T^^MD^^^NPI^^^^L
NK1|1|STORLIE^Kristen^Ragna^^Ms.|MTH^Mother^HL70063|2510 Broadway Ave N^^Rochester^MN^55906^US|^PRN^PH^^^507^2873456
ORC|RE||MIIC20250903001^MIIC|||||||6305129847^Bjornson^Dagny^T^^MD^^^NPI^^^^L
RXA|0|1|20250903100000||21^Varicella^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||B7890JJ^20260903^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|21^Varicella^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20191025||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250903||||||F
```

---

## 14. QBP^Q11 - Immunization forecast query to MIIC from Allina Health

```
MSH|^~\&|ALLINA_EHR|ALLINAANW|MIIC|MNDOH|20250610140530||QBP^Q11^QBP_Q11|ANW20250610140530001|P|2.5.1|||ER|AL|||||Z44^CDCPHINVS
QPD|Z44^Request Evaluated History and Forecast^CDCPHINVS|Q20250610001|E20187643^^^ALLINA^MRN~2024MN0045678^^^MIIC^SR|HAUGEN^Britta^Solveig^^Mrs.|19850923|F|892 Summit Ave^^St. Paul^MN^55105^US
RCP|I|5^RD&Records&HL70126
```

---

## 15. RSP^K11 - Immunization forecast response from MIIC to Allina Health

```
MSH|^~\&|MIIC|MNDOH|ALLINA_EHR|ALLINAANW|20250610140545||RSP^K11^RSP_K11|MIIC20250610140545001|P|2.5.1|||ER|AL|||||Z42^CDCPHINVS
MSA|AA|ANW20250610140530001
QAK|Q20250610001|OK|Z44^Request Evaluated History and Forecast^CDCPHINVS
QPD|Z44^Request Evaluated History and Forecast^CDCPHINVS|Q20250610001|E20187643^^^ALLINA^MRN~2024MN0045678^^^MIIC^SR|HAUGEN^Britta^Solveig^^Mrs.|19850923|F|892 Summit Ave^^St. Paul^MN^55105^US
PID|1||2024MN0045678^^^MIIC^SR~E20187643^^^ALLINA^MRN||HAUGEN^Britta^Solveig^^Mrs.||19850923|F||2106-3^White^CDCREC|892 Summit Ave^^St. Paul^MN^55105^US||^PRN^PH^^^651^2274819||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC
PD1|||ALLINA HEALTH ABBOTT NORTHWESTERN^^20001|5309812746^Bremer^Kathleen^S^^MD^^^NPI^^^^L|||||||02^Reminder/recall - any method^HL70215|N^No^HL70136||A^Active^HL70441
ORC|RE||MIICEVAL20250610001^MIIC
RXA|0|1|20241015100000||197^Influenza, high-dose, quadrivalent^CVX|0.7|mL^milliliter^UCUM||00^New immunization record^NIP001|||||||||SNF^Sanofi Pasteur^MVX||||CP^Complete^HL70322
OBX|1|CE|30956-7^Vaccine Type^LN|1|197^Influenza, high-dose, quadrivalent^CVX||||||F
OBX|2|CE|59779-9^Immunization Schedule used^LN|1|VXC16^ACIP^CDCPHINVS||||||F
OBX|3|CE|30979-9^Vaccines due next^LN|2|197^Influenza, high-dose, quadrivalent^CVX||||||F
OBX|4|DT|30980-7^Date vaccine due^LN|2|20251001||||||F
OBX|5|CE|30979-9^Vaccines due next^LN|3|188^Zoster, recombinant^CVX||||||F
OBX|6|DT|30980-7^Date vaccine due^LN|3|20250923||||||F
OBX|7|CE|30979-9^Vaccines due next^LN|4|115^Tdap^CVX||||||F
OBX|8|DT|30980-7^Date vaccine due^LN|4|20250610||||||F
OBX|9|ED|11369-6^Immunization Forecast Report PDF^LN|5|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1JSUMgSW1tdW5pemF0aW9uIEZvcmVjYXN0IFJlcG9ydCkKL0F1dGhvciAoTWlubmVzb3RhIERlcGFydG1lbnQgb2YgSGVhbHRoKQovQ3JlYXRvciAoTUlJQyBGb3JlY2FzdCBFbmdpbmUpCi9Qcm9kdWNlciAoTUlJQyBQcmludCBTZXJ2aWNlKQovQ3JlYXRpb25EYXRlIChEOjIwMjUwNjEwMTQwNTQ1KQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAyMCAwIFIKPj4KPj4KPj4KZW5kb2JqCg==||||||F
```

---

## 16. VXU^V04 - Shingrix vaccination at HealthPartners Regions Hospital

```
MSH|^~\&|HPREGIONS_EHR|HPREGIONS|MIIC|MNDOH|20250901143045||VXU^V04^VXU_V04|HPR20250901143045001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E40901234^^^HPARTNERS^MRN~2025MN0101234^^^MIIC^SR||OVERBY^Kenneth^Wayne^^^^L||19640318|M||2106-3^White^CDCREC|3301 W 66th St^^Edina^MN^55435^US^L||^PRN^PH^^^952^9293847||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||HEALTHPARTNERS REGIONS HOSPITAL^^30003|9743016825^Storlie^Gregory^T^^MD^^^NPI^^^^L
ORC|RE||MIIC20250901001^MIIC|||||||9743016825^Storlie^Gregory^T^^MD^^^NPI^^^^L
RXA|0|1|20250901142000||188^Zoster, recombinant^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||C1234KK^20260901^GSK|SKB^GlaxoSmithKline^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|188^Zoster, recombinant^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20211019||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250901||||||F
```

---

## 17. VXU^V04 - PCV15 vaccination at Mayo Clinic Health System Mankato

```
MSH|^~\&|MCHS_EHR|MCHS_MANKATO|MIIC|MNDOH|20250814103045||VXU^V04^VXU_V04|MNK20250814103045001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E70345678^^^MCHS^MRN~2025MN0112345^^^MIIC^SR||ALI^Samira^Nasteho^^^^L||20240401|F||2054-5^Black or African American^CDCREC|201 N Broad St^^Mankato^MN^56001^US^L||^PRN^PH^^^507^3872345||som^Somali^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||MAYO CLINIC HEALTH SYSTEM MANKATO^^50001|8160247935^Engstrom^Sandra^A^^MD^^^NPI^^^^L
NK1|1|ALI^Ruqia^Faduma^^Mrs.|MTH^Mother^HL70063|201 N Broad St^^Mankato^MN^56001^US|^PRN^PH^^^507^3872345
ORC|RE||MIIC20250814001^MIIC|||||||8160247935^Engstrom^Sandra^A^^MD^^^NPI^^^^L
RXA|0|1|20250814102000||215^PCV15^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||D5678LL^20260814^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|215^PCV15^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20240301||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250814||||||F
```

---

## 18. VXU^V04 - Historical record submission (Rotavirus) to MIIC from Sanford Health Bemidji

```
MSH|^~\&|SANFORD_EHR|SANFORDBMJ|MIIC|MNDOH|20250601091530||VXU^V04^VXU_V04|SB20250601091530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||SAN30045678^^^SANFORD^MRN~2025MN0123456^^^MIIC^SR||KONG^Shoua^Yer^^^^L||20241201|F||2028-9^Asian^CDCREC|815 Irvine Ave NW^^Bemidji^MN^56601^US^L||^PRN^PH^^^218^7516789||hmn^Hmong^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||SANFORD HEALTH BEMIDJI^^60001|7394028156^Harstad^Glen^T^^MD^^^NPI^^^^L
NK1|1|KONG^Chia^Pang^^Mrs.|MTH^Mother^HL70063|815 Irvine Ave NW^^Bemidji^MN^56601^US|^PRN^PH^^^218^7516789
ORC|RE||MIIC20250601001^MIIC|||||||7394028156^Harstad^Glen^T^^MD^^^NPI^^^^L
RXA|0|1|20250401100000||116^Rotavirus, pentavalent^CVX|2.0|mL^milliliter^UCUM||01^Historical information - source unspecified^NIP001||||||E9012MM^20260401^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|PO^Oral^HL70162
OBX|1|CE|30956-7^Vaccine Type^LN|1|116^Rotavirus, pentavalent^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
```

---

## 19. VXU^V04 - HPV vaccination at Park Nicollet Clinic

```
MSH|^~\&|PNHP_EHR|PARKNICOLLET|MIIC|MNDOH|20250917101530||VXU^V04^VXU_V04|PN20250917101530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||PN40034567^^^PNHP^MRN~2025MN0134567^^^MIIC^SR||JAMA^Hamza^Abdirizak^^^^L||20140505|M||2054-5^Black or African American^CDCREC|4020 Minnetonka Blvd^^St. Louis Park^MN^55416^US^L||^PRN^PH^^^952^9274567||som^Somali^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||PARK NICOLLET CLINIC^^70001|4182536097^Ronning^Andrea^A^^MD^^^NPI^^^^L
NK1|1|JAMA^Sahra^Waris^^Mrs.|MTH^Mother^HL70063|4020 Minnetonka Blvd^^St. Louis Park^MN^55416^US|^PRN^PH^^^952^9274567
ORC|RE||MIIC20250917001^MIIC|||||||4182536097^Ronning^Andrea^A^^MD^^^NPI^^^^L
RXA|0|1|20250917100000||165^HPV9^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||F3456NN^20260917^MSD|MSD^Merck Sharp and Dohme Corp^MVX||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN|1|165^HPV9^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|DT|29768-9^Date vaccine information statement published^LN|3|20191015||||||F
OBX|4|DT|29769-7^Date vaccine information statement presented^LN|4|20250917||||||F
```

---

## 20. VXU^V04 - Pneumococcal PCV20 adult vaccination at Fairview UMMC with refusal

```
MSH|^~\&|FVWUMMC_EHR|FVWUMMC|MIIC|MNDOH|20250228141530||VXU^V04^VXU_V04|FUMMC20250228141530001|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||E30901234^^^FVWUMMC^MRN~2025MN0145678^^^MIIC^SR||NYGAARD^Greta^Solveig^^^^L||19640120|F||2106-3^White^CDCREC|2415 11th Ave NW^^Rochester^MN^55901^US^L||^PRN^PH^^^507^2897654||eng^English^ISO6392|||||||2186-5^Not Hispanic or Latino^CDCREC|||||||N
PD1|||FAIRVIEW UNIVERSITY OF MN MEDICAL CENTER^^40003|4053971826^Swanberg^Eric^L^^MD^^^NPI^^^^L
ORC|RE||MIIC20250228001^MIIC|||||||4053971826^Swanberg^Eric^L^^MD^^^NPI^^^^L
RXA|0|1|20250228140000||216^PCV20^CVX|999|||05^Refused^NIP001|||||||PFR^Pfizer Inc^MVX||||RE^Refused^HL70322
OBX|1|CE|30956-7^Vaccine Type^LN|1|216^PCV20^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN|2|V01^Not VFC eligible^HL70064||||||F
OBX|3|CE|30945-0^Contraindication or precaution^LN|3|00^No contraindication observed^HL70310||||||F
OBX|4|CE|31044-1^Reaction^LN|4|VXC9^Patient Objection^CDCPHINVS||||||F
```
