# TennIIS (state immunization registry) - real HL7v2 ER7 messages

---

## 1. VXU^V04 - DTaP vaccination for infant at Nashville Pediatric Associates

```
MSH|^~\&|NASHPED|NASHVILLE_PED_ASSOC|TENNIIS|TN_DOH|20260509090000||VXU^V04^VXU_V04|NPA20260509090000001|P|2.5.1|||AL|NE
PID|1||TN40001^^^TENNIIS^SR~NP10234^^^NASHPED^MR||Harmon^Caleb^Wayne||20260115|M|||2410 Belmont Blvd^^Nashville^TN^37212^USA||^PRN^PH^^1^615^5551234||ENG|S
PD1||||4455667788^Greer^Denise^Suzanne^^MD^^NASHPED
NK1|1|Harmon^Kelsey^Dawn|MTH|2410 Belmont Blvd^^Nashville^TN^37212^USA|^PRN^PH^^1^615^5551235
ORC|RE|VAX20260509001||||||||||4455667788^Greer^Denise^Suzanne^^MD^^NASHPED
RXA|0|1|20260509085000|20260509085000|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U5501AB|20270301|SKB^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||20^DTaP^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20200101||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 2. VXU^V04 - Hepatitis B birth dose at Vanderbilt University Medical Center

```
MSH|^~\&|VUMC_EHR|VANDERBILT_UMC|TENNIIS|TN_DOH|20260509060000||VXU^V04^VXU_V04|VUMC20260509060000001|P|2.5.1|||AL|NE
PID|1||TN40002^^^TENNIIS^SR~VU55678^^^VUMC^MR||Benson^Baby Girl^||20260509|F|||308 Rosedale Ave^^Nashville^TN^37211^USA||^PRN^PH^^1^615^5556789||ENG|S
PD1||||3344556677^Okafor^Samuel^Nnamdi^^MD^^VUMC
NK1|1|Benson^Tanya^Renee|MTH|308 Rosedale Ave^^Nashville^TN^37211^USA|^PRN^PH^^1^615^5556790
ORC|RE|VAX20260509002||||||||||3344556677^Okafor^Samuel^Nnamdi^^MD^^VUMC
RXA|0|1|20260509050000|20260509050000|08^Hep B adolescent or pediatric^CVX|0.5|mL|IM|RT^Right Thigh||||||H6622CC|20270601|MSD^Merck Sharp and Dohme^MVX
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20200201||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 3. VXU^V04 - Influenza vaccination for adult at Memphis Family Practice

```
MSH|^~\&|MEMFP|MEMPHIS_FAM_PRAC|TENNIIS|TN_DOH|20260509110000||VXU^V04^VXU_V04|MFP20260509110000001|P|2.5.1|||AL|NE
PID|1||TN40003^^^TENNIIS^SR~MF44556^^^MEMFP^MR||Trent^Darius^Lamont^^Mr.||19780314|M|||1487 Union Ave^^Memphis^TN^38104^USA||^PRN^PH^^1^901^5557766||ENG|M
PD1||||5566778899^Kimball^Patricia^Elaine^^MD^^MEMFP
ORC|RE|VAX20260509003||||||||||5566778899^Kimball^Patricia^Elaine^^MD^^MEMFP
RXA|0|1|20260509103000|20260509103000|197^Influenza inactivated quadrivalent^CVX|0.5|mL|IM|LA^Left Arm||||||N8801DD|20270301|SNF^Sanofi Pasteur^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||197^Influenza inactivated quadrivalent^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
```

---

## 4. VXU^V04 - HPV vaccination for adolescent at Chattanooga Pediatric Group

```
MSH|^~\&|CHATPED|CHATT_PED_GRP|TENNIIS|TN_DOH|20260509130000||VXU^V04^VXU_V04|CPG20260509130000001|P|2.5.1|||AL|NE
PID|1||TN40004^^^TENNIIS^SR~CP22345^^^CHATPED^MR||Whitfield^Layla^Christine||20140610|F|||918 Market St^^Chattanooga^TN^37402^USA||^PRN^PH^^1^423^5553344||ENG|S
PD1||||6677889900^Pryor^Victor^Anthony^^MD^^CHATPED
NK1|1|Whitfield^Donna^Elise|MTH|918 Market St^^Chattanooga^TN^37402^USA|^PRN^PH^^1^423^5553345
ORC|RE|VAX20260509004||||||||||6677889900^Pryor^Victor^Anthony^^MD^^CHATPED
RXA|0|1|20260509123000|20260509123000|165^HPV9^CVX|0.5|mL|IM|LA^Left Arm||||||K9902EE|20270901|MSD^Merck Sharp and Dohme^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||165^HPV9^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20191015||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 5. VXU^V04 - Pneumococcal vaccination for elderly at Knoxville Senior Health

```
MSH|^~\&|KNOXSR|KNOXVILLE_SR_HLTH|TENNIIS|TN_DOH|20260509140000||VXU^V04^VXU_V04|KSH20260509140000001|P|2.5.1|||AL|NE
PID|1||TN40005^^^TENNIIS^SR~KS88901^^^KNOXSR^MR||Langford^Harold^Vernon^^Mr.||19530225|M|||5012 Chapman Hwy^^Knoxville^TN^37920^USA||^PRN^PH^^1^865^5556677||ENG|W
PD1||||7788990011^Ogden^Frances^Louise^^MD^^KNOXSR
ORC|RE|VAX20260509005||||||||||7788990011^Ogden^Frances^Louise^^MD^^KNOXSR
RXA|0|1|20260509133000|20260509133000|216^PCV20^CVX|0.5|mL|IM|LA^Left Arm||||||P3344FF|20271201|PFE^Pfizer Inc^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||216^PCV20^CVX||||||F
OBX|2|CE|59779-9^Immunization Schedule^LN||BD01^Primary Series^HL70396||||||F
```

---

## 6. VXU^V04 - Tdap vaccination for pregnant woman at Clarksville Women's Health

```
MSH|^~\&|CLKWH|CLARKSVILLE_WH|TENNIIS|TN_DOH|20260509143000||VXU^V04^VXU_V04|CWH20260509143000001|P|2.5.1|||AL|NE
PID|1||TN40006^^^TENNIIS^SR~CW56789^^^CLKWH^MR||Fuentes^Marisol^Adriana^^Mrs.||19940822|F|||2905 Wilma Rudolph Blvd^^Clarksville^TN^37040^USA||^PRN^PH^^1^931^5559876||SPA|M
PD1||||8899001122^Ballard^Gregory^Alan^^MD^^CLKWH
ORC|RE|VAX20260509006||||||||||8899001122^Ballard^Gregory^Alan^^MD^^CLKWH
RXA|0|1|20260509140000|20260509140000|115^Tdap^CVX|0.5|mL|IM|LA^Left Arm||||||T5566GG|20270601|GSK^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||115^Tdap^CVX||||||F
OBX|2|CE|30963-3^Vaccine administered during pregnancy^LN||Y^Yes^HL70136||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20200101||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 7. VXR^V03 - Immunization history response from TennIIS

```
MSH|^~\&|TENNIIS|TN_DOH|NASHPED|NASHVILLE_PED_ASSOC|20260509100000||VXR^V03^VXR_V03|TNIIS20260509100000001|P|2.5.1|||AL|NE
MSA|AA|QRY20260509001
QRD|20260509100000|R|I|Q20260509001|||1^RD|TN40001^^^TENNIIS^SR|VXI|
PID|1||TN40001^^^TENNIIS^SR||Harmon^Caleb^Wayne||20260115|M|||2410 Belmont Blvd^^Nashville^TN^37212^USA||^PRN^PH^^1^615^5551234||ENG|S
ORC|RE|TNIIS-H20260509001||||||||||4455667788^Greer^Denise^Suzanne^^MD^^NASHPED
RXA|0|1|20260115|20260115|08^Hep B adolescent or pediatric^CVX|0.5|mL|IM|RT^Right Thigh||||||H2233AA|20270601|MSD^Merck Sharp and Dohme^MVX
RXA|0|2|20260315|20260315|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U4455BB|20270301|SKB^GlaxoSmithKline^MVX
RXA|0|3|20260315|20260315|10^IPV^CVX|0.5|mL|SC|LT^Left Thigh||||||P6677CC|20270601|SNF^Sanofi Pasteur^MVX
RXA|0|4|20260315|20260315|133^PCV13^CVX|0.5|mL|IM|LT^Left Thigh||||||V8899DD|20270901|PFE^Pfizer Inc^MVX
RXA|0|5|20260315|20260315|116^Rotavirus pentavalent^CVX|2.0|mL|PO|||||||R1122EE|20270301|MSD^Merck Sharp and Dohme^MVX
RXA|0|6|20260509|20260509|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U5501AB|20270301|SKB^GlaxoSmithKline^MVX
```

---

## 8. VXQ^V01 - Immunization record query to TennIIS from Memphis clinic

```
MSH|^~\&|MEMFP|MEMPHIS_FAM_PRAC|TENNIIS|TN_DOH|20260509110000||VXQ^V01^VXQ_V01|MFP20260509110000002|P|2.5.1|||AL|NE
QRD|20260509110000|R|I|QRY20260509002|||1^RD|TN40003^^^TENNIIS^SR|VXI|
QRF|TENNIIS|20260509||20260509
```

---

## 9. ACK^V04 - Positive acknowledgment from TennIIS for VXU

```
MSH|^~\&|TENNIIS|TN_DOH|NASHPED|NASHVILLE_PED_ASSOC|20260509090100||ACK^V04^ACK|TNIISACK20260509090100001|P|2.5.1|||AL|NE
MSA|AA|NPA20260509090000001|Immunization record accepted and stored in TennIIS
```

---

## 10. ACK^V04 - Application error from TennIIS for invalid CVX code

```
MSH|^~\&|TENNIIS|TN_DOH|MEMFP|MEMPHIS_FAM_PRAC|20260509110100||ACK^V04^ACK|TNIISACK20260509110100001|P|2.5.1|||AL|NE
MSA|AE|MFP20260509110000001|Invalid vaccine code in RXA segment
ERR||RXA^1^5^1|103^Table value not found^HL70357|E||||CVX code 999 is not a recognized vaccine code in TennIIS. Please verify and resubmit.
```

---

## 11. QBP^Q11 - Immunization history query to TennIIS from Johnson City clinic

```
MSH|^~\&|JCITYPED|JOHNSON_CITY_PED|TN_IMMREG|TN_DOH|20260509120000||QBP^Q11^QBP_Q11|JCP20260509120000001|P|2.5.1|||AL|NE
QPD|Z34^Request Immunization History^CDCPHINVS|Q20260509006|TN40004^^^TENNIIS^SR^^^^~CP22345^^^CHATPED^MR^^^^|Whitfield^Layla^Christine|20140610|F|918 Market St^^Chattanooga^TN^37402^USA
RCP|I|10^RD
```

---

## 12. RSP^K11 - Immunization history query response from TennIIS

```
MSH|^~\&|TN_IMMREG|TN_DOH|JCITYPED|JOHNSON_CITY_PED|20260509120500||RSP^K11^RSP_K11|TNIIS20260509120500001|P|2.5.1|||AL|NE
MSA|AA|JCP20260509120000001
QAK|Q20260509006|OK|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20260509006|TN40004^^^TENNIIS^SR
PID|1||TN40004^^^TENNIIS^SR||Whitfield^Layla^Christine||20140610|F|||918 Market St^^Chattanooga^TN^37402^USA||^PRN^PH^^1^423^5553344
ORC|RE|TNIIS-H20260509004
RXA|0|1|20140810|20140810|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|2|20141010|20141010|20^DTaP^CVX|0.5|mL|IM|LT^Left Thigh
RXA|0|3|20141210|20141210|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|4|20150610|20150610|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|5|20180610|20180610|20^DTaP^CVX|0.5|mL|IM|LA^Left Arm
RXA|0|6|20260509|20260509|165^HPV9^CVX|0.5|mL|IM|LA^Left Arm
OBX|1|CE|59779-9^Immunization Schedule^LN||VXC16^DTaP series complete^CDCPHINVS||||||F
```

---

## 13. VXU^V04 - Zoster vaccination at Murfreesboro Senior Wellness

```
MSH|^~\&|MBOROSW|MURFREESBORO_SW|TENNIIS|TN_DOH|20260509153000||VXU^V04^VXU_V04|MSW20260509153000001|P|2.5.1|||AL|NE
PID|1||TN40007^^^TENNIIS^SR~MS90234^^^MBOROSW^MR||Cofield^Wanda^Irene^^Mrs.||19510418|F|||730 Memorial Blvd^^Murfreesboro^TN^37129^USA||^PRN^PH^^1^629^5554488||ENG|W
PD1||||1122334455^Rutledge^Philip^Dean^^MD^^MBOROSW
ORC|RE|VAX20260509007||||||||||1122334455^Rutledge^Philip^Dean^^MD^^MBOROSW
RXA|0|1|20260509150000|20260509150000|187^Zoster recombinant^CVX|0.5|mL|IM|LA^Left Arm||||||Z7788HH|20271201|GSK^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||187^Zoster recombinant^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20191015||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 14. VXU^V04 - Historical vaccination entry (data migration) at Franklin clinic

```
MSH|^~\&|FRANKLINPG|FRANKLIN_PED_GRP|TENNIIS|TN_DOH|20260509150000||VXU^V04^VXU_V04|FPG20260509150000001|P|2.5.1|||AL|NE
PID|1||TN40008^^^TENNIIS^SR~FP77812^^^FRANKLINPG^MR||Gentry^Travis^Allen^^Mr.||19960523|M|||510 Columbia Ave^^Franklin^TN^37064^USA||^PRN^PH^^1^615^5552233||ENG|S
PD1||||2233445566^Norwood^Janet^Faye^^MD^^FRANKLINPG
ORC|RE|VAX20260509008||||||||||2233445566^Norwood^Janet^Faye^^MD^^FRANKLINPG
RXA|0|1|20060101|20060101|08^Hep B adolescent or pediatric^CVX|999|mL|IM|||00^New immunization record^NIP001||||||||CP|A
OBX|1|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|2|CE|69764-9^Document type^LN||253088698300026411121116^Historical^cdcgs1vis||||||F
```

---

## 15. ACK^V04 - Acknowledgment with warning from TennIIS for duplicate vaccination

```
MSH|^~\&|TENNIIS|TN_DOH|CLKWH|CLARKSVILLE_WH|20260509143100||ACK^V04^ACK|TNIISACK20260509143100001|P|2.5.1|||AL|NE
MSA|AA|CWH20260509143000001|Immunization record accepted with warning
ERR||RXA^1^5|100^Segment sequence error^HL70357|W||||Possible duplicate vaccination detected. TennIIS already contains a Tdap record dated 20260509 for this patient. Record stored but flagged for review.
```

---

## 16. VXU^V04 - MMRV vaccination with OBX ED containing immunization certificate as base64

```
MSH|^~\&|TN_IIS|JACKSON_PED|TENNIIS|TN_DOH|20260509160000||VXU^V04^VXU_V04|JKP20260509160000001|P|2.5.1|||AL|NE
PID|1||TN40009^^^TENNIIS^SR~JP33456^^^JACKSONPED^MR||Millwood^Jaylen^Oliver||20200708|M|||780 Campbell St^^Jackson^TN^38301^USA||^PRN^PH^^1^731^5551122||ENG|S
PD1||||3344556677^Stokes^Renita^Diane^^MD^^JACKSONPED
NK1|1|Millwood^Shanice^Patrice|MTH|780 Campbell St^^Jackson^TN^38301^USA|^PRN^PH^^1^731^5551123
ORC|RE|VAX20260509009||||||||||3344556677^Stokes^Renita^Diane^^MD^^JACKSONPED
RXA|0|1|20260509153000|20260509153000|94^MMRV^CVX|0.5|mL|SC|LA^Left Arm||||||L9911JJ|20270601|MSD^Merck Sharp and Dohme^MVX
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||94^MMRV^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
OBX|3|ED|11369-6^Immunization Certificate^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4KZW5kb2Jq||||||F|||20260509160000
```

---

## 17. VXU^V04 - COVID-19 pediatric vaccination with VIS document as base64 ED

```
MSH|^~\&|TN_IIS|COOKEVILLE_FM|TENNIIS|TN_DOH|20260509163000||VXU^V04^VXU_V04|CFM20260509163000001|P|2.5.1|||AL|NE
PID|1||TN40010^^^TENNIIS^SR~CF44567^^^COOKEVILLEFM^MR||Vaughn^Sienna^Brooke||20210517|F|||310 S Willow Ave^^Cookeville^TN^38501^USA||^PRN^PH^^1^931^5553399||ENG|S
PD1||||4455667788^Ramsey^Kenneth^Lloyd^^MD^^COOKEVILLEFM
NK1|1|Vaughn^Heather^Jolene|MTH|310 S Willow Ave^^Cookeville^TN^38501^USA|^PRN^PH^^1^931^5553400
ORC|RE|VAX20260509010||||||||||4455667788^Ramsey^Kenneth^Lloyd^^MD^^COOKEVILLEFM
RXA|0|1|20260509160000|20260509160000|300^COVID-19 VACCINE MRNA BIVALENT^CVX|0.25|mL|IM|LA^Left Arm||||||M3355KK|20260901|MOD^ModernaTX Inc^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||300^COVID-19 Vaccine mRNA bivalent^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||3||||||F
OBX|3|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
OBX|4|ED|11369-6^Vaccine Information Statement^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdID4+||||||F|||20260509163000
```

---

## 18. RSP^K11 - No records found response from TennIIS

```
MSH|^~\&|TN_IMMREG|TN_DOH|MEMFP|MEMPHIS_FAM_PRAC|20260509112000||RSP^K11^RSP_K11|TNIIS20260509112000001|P|2.5.1|||AL|NE
MSA|AA|MFP20260509110000002
QAK|Q20260509007|NF|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20260509007|TN40099^^^TENNIIS^SR
```

---

## 19. RSP^K11 - Query response with complete immunization forecast from TennIIS

```
MSH|^~\&|TN_IMMREG|TN_DOH|NASHPED|NASHVILLE_PED_ASSOC|20260509101000||RSP^K11^RSP_K11|TNIIS20260509101000002|P|2.5.1|||AL|NE
MSA|AA|NPA20260509100000001
QAK|Q20260509008|OK|Z44^Request Evaluated History and Forecast^CDCPHINVS
QPD|Z44^Request Evaluated History and Forecast^CDCPHINVS|Q20260509008|TN40001^^^TENNIIS^SR
PID|1||TN40001^^^TENNIIS^SR||Harmon^Caleb^Wayne||20260115|M|||2410 Belmont Blvd^^Nashville^TN^37212^USA
ORC|RE|TNIIS-E20260509001
RXA|0|1|20260115|20260115|08^Hep B adolescent or pediatric^CVX|0.5|mL
OBX|1|CE|59781-5^Dose validity^LN||Y^Valid^HL70136||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|3|DT|30980-7^Date vaccination due^LN||20260515||||||F
OBX|4|CE|59783-1^Status in immunization series^LN||LA13422-3^On Schedule^LN||||||F
ORC|RE|TNIIS-F20260509001
RXA|0|999|20260509|20260509|998^No vaccine administered^CVX|999
OBX|1|CE|30956-7^Vaccine Type^LN||20^DTaP^CVX||||||F
OBX|2|DT|30980-7^Date vaccination due^LN||20260715||||||F
OBX|3|CE|59783-1^Status in immunization series^LN||LA13423-1^Overdue^LN||||||F
```

---

## 20. ACK^V04 - Rejection from TennIIS for missing patient identifier

```
MSH|^~\&|TENNIIS|TN_DOH|FRANKLINPG|FRANKLIN_PED_GRP|20260509150100||ACK^V04^ACK|TNIISACK20260509150100001|P|2.5.1|||AL|NE
MSA|AR|FPG20260509150000001|Message rejected - missing required patient identifier
ERR||PID^1^3|101^Required field missing^HL70357|E||||PID-3 (Patient Identifier List) is required and must contain at least one identifier with an assigning authority recognized by TennIIS. Resubmit with valid TennIIS or MRN identifier.
```
