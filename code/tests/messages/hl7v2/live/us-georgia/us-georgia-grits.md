# Georgia GRITS (Public Health) - real HL7v2 ER7 messages

---

## 1. VXU^V04 - Infant DTaP immunization from Fulton County Health Dept

```
MSH|^~\&|GRITS|FULTON_HD|GA_GRITS|GRITS_IIS|20260401091500||VXU^V04^VXU_V04|MSG40001|P|2.5.1|||AL|NE
PID|1||FU1001234^^^FULTON_HD_MRN^MR||Okonkwo^Amara^Sage||20250801|F|||10 Park Pl S^^Atlanta^GA^30303^US||^PRN^PH^^1^404^5551001||||S
PD1|||Fulton County Health Department^^FC001|70001^Blackwell^Terri^L^^^MD
NK1|1|Okonkwo^Keandra^Monique|MTH^Mother|10 Park Pl S^^Atlanta^GA^30303^US|^PRN^PH^^1^404^5551002
RXA|0|1|20260401090000|20260401090500|20^DTaP^CVX|0.5|mL||00^New immunization record^NIP001||||||A1234AA||SNF^Sanofi Pasteur^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC30^State funds^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine type^LN||20^DTaP^CVX||||||F
OBX|3|NM|30973-2^Dose number in series^LN||3||||||F
```

---

## 2. VXU^V04 - MMR vaccine at DeKalb County Board of Health

```
MSH|^~\&|GA_GRITS|DEKALB_BOH|GA_GRITS|GRITS_IIS|20260402100000||VXU^V04^VXU_V04|MSG40002|P|2.5.1|||AL|NE
PID|1||DK2002345^^^DEKALB_BOH_MRN^MR||Whitfield^Elijah^Corey||20210415|M|||2815 Candler Rd^^Decatur^GA^30034^US||^PRN^PH^^1^404^5552001||||S
NK1|1|Whitfield^Shanice^Monique|MTH^Mother|2815 Candler Rd^^Decatur^GA^30034^US|^PRN^PH^^1^404^5552002
RXA|0|1|20260402095000|20260402095500|03^MMR^CVX|0.5|mL||00^New immunization record^NIP001||||||B2345BB||MSD^Merck^MVX|||CP|A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 3. VXU^V04 - Hepatitis B birth dose at Grady Memorial Hospital

```
MSH|^~\&|GRITS|GRADY_MEM|GA_GRITS|GRITS_IIS|20260403023000||VXU^V04^VXU_V04|MSG40003|P|2.5.1|||AL|NE
PID|1||GM3003456^^^GRADY_MRN^MR||Calderon^Isabella^Noemi||20260403|F|||80 Jesse Hill Jr Dr SE^^Atlanta^GA^30303^US||^PRN^PH^^1^404^5553001||||S
NK1|1|Calderon^Ana^Beatriz|MTH^Mother|1245 Boulevard SE^^Atlanta^GA^30312^US|^PRN^PH^^1^404^5553002
RXA|0|1|20260403020000|20260403020500|08^Hep B, adolescent or pediatric^CVX|0.5|mL||00^New immunization record^NIP001||||||C3456CC||MSD^Merck^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC30^State funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
OBX|3|DT|29769-7^Date vaccine information statement published^LN||20200715||||||F
```

---

## 4. VXU^V04 - Influenza vaccine at Gwinnett County Health Dept

```
MSH|^~\&|GA_GRITS|GWINNETT_HD|GA_GRITS|GRITS_IIS|20260404083000||VXU^V04^VXU_V04|MSG40004|P|2.5.1|||AL|NE
PID|1||GW4004567^^^GWINNETT_HD_MRN^MR||Tran^Lily^Mai||20200119|F|||1588 Buford Hwy^^Lawrenceville^GA^30043^US||^PRN^PH^^1^770^5554001||||S
NK1|1|Tran^Hanh^Thuy|MTH^Mother|1588 Buford Hwy^^Lawrenceville^GA^30043^US|^PRN^PH^^1^770^5554002
RXA|0|1|20260404082000|20260404082500|141^Influenza, seasonal, injectable^CVX|0.25|mL||00^New immunization record^NIP001||||||D4567DD||SNF^Sanofi Pasteur^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 5. VXU^V04 - Tdap booster at Cobb County Board of Health

```
MSH|^~\&|GRITS|COBB_BOH|GA_GRITS|GRITS_IIS|20260405094500||VXU^V04^VXU_V04|MSG40005|P|2.5.1|||AL|NE
PID|1||CB5005678^^^COBB_BOH_MRN^MR||Nair^Arjun^Vikram||20140712|M|||2050 Lower Roswell Rd^^Marietta^GA^30068^US||^PRN^PH^^1^770^5555001||||S
NK1|1|Nair^Priya^Lakshmi|MTH^Mother|2050 Lower Roswell Rd^^Marietta^GA^30068^US|^PRN^PH^^1^770^5555002
RXA|0|1|20260405093500|20260405094000|115^Tdap^CVX|0.5|mL||00^New immunization record^NIP001||||||E5678EE||SNF^Sanofi Pasteur^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 6. VXU^V04 - HPV vaccine at Clayton County Health Dept

```
MSH|^~\&|GA_GRITS|CLAYTON_HD|GA_GRITS|GRITS_IIS|20260406101500||VXU^V04^VXU_V04|MSG40006|P|2.5.1|||AL|NE
PID|1||CL6006789^^^CLAYTON_HD_MRN^MR||Rutledge^Kayla^Simone||20130325|F|||7420 Jonesboro Rd^^Jonesboro^GA^30236^US||^PRN^PH^^1^770^5556001||||S
NK1|1|Rutledge^Tiffany^Denise|MTH^Mother|7420 Jonesboro Rd^^Jonesboro^GA^30236^US|^PRN^PH^^1^770^5556002
RXA|0|1|20260406100500|20260406101000|165^HPV9^CVX|0.5|mL||00^New immunization record^NIP001||||||F6789FF||MSD^Merck^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 7. VXU^V04 - COVID-19 booster at Chatham County Health Dept

```
MSH|^~\&|GRITS|CHATHAM_HD|GA_GRITS|GRITS_IIS|20260407140000||VXU^V04^VXU_V04|MSG40007|P|2.5.1|||AL|NE
PID|1||CH7007890^^^CHATHAM_HD_MRN^MR||Gentry^Clarence^Wayne^^Mr||19560823|M|||601 E 37th St^^Savannah^GA^31401^US||^PRN^PH^^1^912^5557001||||M
RXA|0|1|20260407135000|20260407135500|308^COVID-19, mRNA, updated, bivalent^CVX|0.5|mL||00^New immunization record^NIP001||||||G7890GG||MOD^Moderna^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RD^Right Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC2^Federal funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||5||||||F
```

---

## 8. VXU^V04 - Rotavirus vaccine at Richmond County Health Dept

```
MSH|^~\&|GA_GRITS|RICHMOND_HD|GA_GRITS|GRITS_IIS|20260408090000||VXU^V04^VXU_V04|MSG40008|P|2.5.1|||AL|NE
PID|1||RC8008901^^^RICHMOND_HD_MRN^MR||Langford^Caleb^Andrew||20260108|M|||1916 Central Ave^^Augusta^GA^30904^US||^PRN^PH^^1^706^5558001||||S
NK1|1|Langford^Ashley^Nicole|MTH^Mother|1916 Central Ave^^Augusta^GA^30904^US|^PRN^PH^^1^706^5558002
RXA|0|1|20260408085000|20260408085500|116^Rotavirus, pentavalent^CVX|2.0|mL||00^New immunization record^NIP001||||||H8901HH||MSD^Merck^MVX|||CP|A
RXR|PO^Oral^HL70162
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||2||||||F
```

---

## 9. VXR^V03 - Immunization history response from GRITS for Fulton County

```
MSH|^~\&|GRITS_IIS|GA_GRITS|GRITS|FULTON_HD|20260409103000||VXR^V03^VXR_V03|MSG40009|P|2.5.1|||AL|NE
MSA|AA|QRY40020|Record found
QRD|20260409102500|R|I|QRY40020|||1^RD|FU1001234^^^FULTON_HD_MRN^MR|VXI^Vaccine History^HL70048
PID|1||FU1001234^^^FULTON_HD_MRN^MR||Okonkwo^Amara^Sage||20250801|F|||10 Park Pl S^^Atlanta^GA^30303^US||^PRN^PH^^1^404^5551001||||S
RXA|0|1|20250801|20250801|08^Hep B, adolescent or pediatric^CVX|0.5|mL||00||||||||||CP|A
RXA|0|2|20251001|20251001|20^DTaP^CVX|0.5|mL||00||||||||||CP|A
RXA|0|3|20251001|20251001|10^IPV^CVX|0.5|mL||00||||||||||CP|A
RXA|0|4|20251001|20251001|133^PCV13^CVX|0.5|mL||00||||||||||CP|A
RXA|0|5|20251201|20251201|20^DTaP^CVX|0.5|mL||00||||||||||CP|A
RXA|0|6|20260401|20260401|20^DTaP^CVX|0.5|mL||00||||||||||CP|A
```

---

## 10. VXQ^V01 - Immunization history query from Bibb County clinic

```
MSH|^~\&|GRITS|BIBB_CLINIC|GA_GRITS|GRITS_IIS|20260410080000||VXQ^V01^VXQ_V01|MSG40010|P|2.5.1|||AL|NE
QRD|20260410075500|R|I|QRY40010|||1^RD|BB1001234^^^BIBB_CLINIC_MRN^MR|VXI^Vaccine History^HL70048
QRF|GA_GRITS|20200101|20260410
```

---

## 11. RSP^K11 - Query response with immunization forecast from GRITS

```
MSH|^~\&|GRITS_IIS|GA_GRITS|GRITS|BIBB_CLINIC|20260410080100||RSP^K11^RSP_K11|MSG40011|P|2.5.1|||AL|NE
MSA|AA|MSG40010|Query processed successfully
QAK|QRY40010|OK|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|QRY40010|BB1001234^^^BIBB_CLINIC_MRN^MR
PID|1||BB1001234^^^BIBB_CLINIC_MRN^MR||Kincaid^Aiden^Thomas||20230515|M|||305 Walnut St^^Macon^GA^31201^US||^PRN^PH^^1^478^5550101||||S
RXA|0|1|20230515|20230515|08^Hep B, adolescent or pediatric^CVX|0.5|mL||00||||||||||CP|A
RXA|0|2|20230715|20230715|20^DTaP^CVX|0.5|mL||00||||||||||CP|A
RXA|0|3|20230715|20230715|10^IPV^CVX|0.5|mL||00||||||||||CP|A
OBX|1|CE|30979-9^Vaccines due next^LN||20^DTaP^CVX||||||F
OBX|2|TS|30980-7^Date vaccine due^LN||20260515||||||F
OBX|3|CE|30979-9^Vaccines due next^LN||03^MMR^CVX||||||F
OBX|4|TS|30980-7^Date vaccine due^LN||20240515||||||F
```

---

## 12. ACK^V04 - Positive acknowledgment for VXU submission

```
MSH|^~\&|GRITS_IIS|GA_GRITS|GRITS|FULTON_HD|20260401091600||ACK^V04^ACK|MSG40012|P|2.5.1|||AL|NE
MSA|AA|MSG40001|Immunization record accepted and stored in GRITS
```

---

## 13. ACK^V04 - Negative acknowledgment for duplicate immunization

```
MSH|^~\&|GRITS_IIS|GA_GRITS|GA_GRITS|DEKALB_BOH|20260411091000||ACK^V04^ACK|MSG40013|P|2.5.1|||AL|NE
MSA|AE|MSG40050|Duplicate immunization record detected
ERR||RXA^1^5|101^Duplicate record^HL70357|W|||||Immunization record for CVX 03 on 20260402 already exists for this patient
```

---

## 14. VXU^V04 - Pneumococcal vaccine at Muscogee County Health Dept

```
MSH|^~\&|GRITS|MUSCOGEE_HD|GA_GRITS|GRITS_IIS|20260412093000||VXU^V04^VXU_V04|MSG40014|P|2.5.1|||AL|NE
PID|1||MU1401234^^^MUSCOGEE_HD_MRN^MR||Pressley^Mason^Anthony||20250614|M|||1601 2nd Ave^^Columbus^GA^31901^US||^PRN^PH^^1^706^5550201||||S
NK1|1|Pressley^Jasmine^Chantel|MTH^Mother|1601 2nd Ave^^Columbus^GA^31901^US|^PRN^PH^^1^706^5550202
RXA|0|1|20260412092000|20260412092500|133^PCV13^CVX|0.5|mL||00^New immunization record^NIP001||||||I9012II||PFR^Pfizer^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||3||||||F
```

---

## 15. VXU^V04 - Varicella vaccine at Hall County Health Dept

```
MSH|^~\&|GA_GRITS|HALL_HD|GA_GRITS|GRITS_IIS|20260413100000||VXU^V04^VXU_V04|MSG40015|P|2.5.1|||AL|NE
PID|1||HL1501234^^^HALL_HD_MRN^MR||Restrepo^Sofia^Daniela||20210830|F|||925 Jesse Jewell Pkwy^^Gainesville^GA^30501^US||^PRN^PH^^1^770^5550301||||S
NK1|1|Restrepo^Lucia^Elena|MTH^Mother|925 Jesse Jewell Pkwy^^Gainesville^GA^30501^US|^PRN^PH^^1^770^5550302
RXA|0|1|20260413095000|20260413095500|21^Varicella^CVX|0.5|mL||00^New immunization record^NIP001||||||J0123JJ||MSD^Merck^MVX|||CP|A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 16. VXU^V04 - Hepatitis A vaccine at Whitfield County Health Dept

```
MSH|^~\&|GRITS|WHITFIELD_HD|GA_GRITS|GRITS_IIS|20260414085000||VXU^V04^VXU_V04|MSG40016|P|2.5.1|||AL|NE
PID|1||WF1601234^^^WHITFIELD_HD_MRN^MR||Cho^Ethan^Christopher||20240301|M|||1801 Professional Blvd^^Dalton^GA^30720^US||^PRN^PH^^1^706^5550401||||S
NK1|1|Cho^Jennifer^Hye|MTH^Mother|1801 Professional Blvd^^Dalton^GA^30720^US|^PRN^PH^^1^706^5550402
RXA|0|1|20260414084000|20260414084500|83^Hep A, pediatric, 2 dose^CVX|0.5|mL||00^New immunization record^NIP001||||||K1234KK||MSD^Merck^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 17. VXU^V04 - Immunization with certificate PDF from Clarke County

```
MSH|^~\&|GA_GRITS|CLARKE_HD|GA_GRITS|GRITS_IIS|20260415110000||VXU^V04^VXU_V04|MSG40017|P|2.5.1|||AL|NE
PID|1||CK1701234^^^CLARKE_HD_MRN^MR||Pemberton^Olivia^Claire||20190507|F|||250 College Ave^^Athens^GA^30601^US||^PRN^PH^^1^706^5550501||||S
NK1|1|Pemberton^Marcus^Wayne|FTH^Father|250 College Ave^^Athens^GA^30601^US|^PRN^PH^^1^706^5550502
RXA|0|1|20260415105000|20260415105500|94^MMRV^CVX|0.5|mL||00^New immunization record^NIP001||||||L2345LL||MSD^Merck^MVX|||CP|A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||2||||||F
OBX|3|ED|11369-6^Immunization Certificate^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4KZW5kb2Jq||||||F
```

---

## 18. VXU^V04 - School-required immunization with certificate from Douglas County

```
MSH|^~\&|GRITS|DOUGLAS_HD|GA_GRITS|GRITS_IIS|20260416083000||VXU^V04^VXU_V04|MSG40018|P|2.5.1|||AL|NE
PID|1||DG1801234^^^DOUGLAS_HD_MRN^MR||Lockhart^Jaylen^Marcus||20200215|M|||8565 Hospital Dr^^Douglasville^GA^30134^US||^PRN^PH^^1^770^5550601||||S
NK1|1|Lockhart^Crystal^Denise|MTH^Mother|8565 Hospital Dr^^Douglasville^GA^30134^US|^PRN^PH^^1^770^5550602
RXA|0|1|20260416082000|20260416082500|21^Varicella^CVX|0.5|mL||00^New immunization record^NIP001||||||M3456MM||MSD^Merck^MVX|||CP|A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC30^State funds^CDCPHINVS||||||F
OBX|2|NM|30973-2^Dose number in series^LN||2||||||F
OBX|3|ED|11369-6^Immunization Certificate^LN||^application^pdf^Base64^JVBERi0xLjQKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxID4+CmVuZG9iag==||||||F
```

---

## 19. VXQ^V01 - Immunization query from CVS Pharmacy, Roswell

```
MSH|^~\&|GA_IMMREG|CVS_ROSWELL|GA_GRITS|GRITS_IIS|20260417141500||VXQ^V01^VXQ_V01|MSG40019|P|2.5.1|||AL|NE
QRD|20260417141000|R|I|QRY40019|||1^RD|^^^~Holbrook^Gregory^Nathan^^19800423|VXI^Vaccine History^HL70048
QRF|GA_GRITS|20100101|20260417
```

---

## 20. ACK^V04 - Acknowledgment with warning for age-inappropriate vaccine

```
MSH|^~\&|GRITS_IIS|GA_GRITS|GRITS|GWINNETT_HD|20260418091500||ACK^V04^ACK|MSG40020|P|2.5.1|||AL|NE
MSA|AA|MSG40060|Immunization record accepted with warning
ERR||RXA^1^5|207^Application error^HL70357|W|||||CVX 165 (HPV9) administered at age 8 years, recommended minimum age is 9 years per ACIP schedule
```
