# Colorado Immunization Information System (CIIS) - real HL7v2 ER7 messages

---

## 1. VXU^V04 - DTaP vaccination for infant at Boulder Pediatrics

```
MSH|^~\&|BOULDERPED|BOULDER_PEDIATRICS|CIIS|CDPHE|20260509090000||VXU^V04^VXU_V04|BP20260509090000001|P|2.5.1|||AL|NE
PID|1||CIIS30001^^^CIIS^SR~BP10234^^^BOULDERPED^MR||Gallegos^Camila^Renata||20260102|F|||4710 Baseline Rd^^Boulder^CO^80303^USA||^PRN^PH^^1^303^4429817||SPA|S
PD1||||5528193047^Linden^Margaret^Elise^^MD^^BOULDERPED
NK1|1|Gallegos^Emilio^Javier|FTH|4710 Baseline Rd^^Boulder^CO^80303^USA|^PRN^PH^^1^303^4429818
ORC|RE|VAX20260509001||||||||||5528193047^Linden^Margaret^Elise^^MD^^BOULDERPED
RXA|0|1|20260509085000|20260509085000|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U1234AB|20270301|SKB^GlaxoSmithKline
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||20^DTaP^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20200101||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 2. VXU^V04 - Hepatitis B birth dose at Denver Health Newborn Nursery

```
MSH|^~\&|DENVERHEALTH|DH_NEWBORN|CIIS|CDPHE|20260509060000||VXU^V04^VXU_V04|DH20260509060000001|P|2.5.1|||AL|NE
PID|1||CIIS30002^^^CIIS^SR~DH55678^^^DENVERHEALTH^MR||Tran^Baby Boy^||20260509|M|||2340 Federal Blvd^^Denver^CO^80211^USA||^PRN^PH^^1^720^8836214||VIE|S
PD1||||7193206854^Orozco^Leticia^Dawn^^MD^^DENVERHEALTH
NK1|1|Tran^Huong^Mai|MTH|2340 Federal Blvd^^Denver^CO^80211^USA|^PRN^PH^^1^720^8836215
ORC|RE|VAX20260509002||||||||||7193206854^Orozco^Leticia^Dawn^^MD^^DENVERHEALTH
RXA|0|1|20260509050000|20260509050000|08^Hep B adolescent or pediatric^CVX|0.5|mL|IM|RT^Right Thigh||||||H5566CC|20270601|MSD^Merck Sharp and Dohme
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible - Medicaid/SCHIP^HL70064||||||F
```

---

## 3. VXU^V04 - Influenza vaccination for adult at Aurora Medical Center

```
MSH|^~\&|AURORAMC|AURORA_MED|CIIS|CDPHE|20260509110000||VXU^V04^VXU_V04|AM20260509110000001|P|2.5.1|||AL|NE
PID|1||CIIS30003^^^CIIS^SR~AM44556^^^AURORAMC^MR||Pham^Donna^Linh^^Mrs.||19750609|F|||16790 E Iliff Ave^^Aurora^CO^80013^USA||^PRN^PH^^1^720^3417952||ENG|M
PD1||||4081273965^Quintero^Alejandro^Ray^^MD^^AURORAMC
ORC|RE|VAX20260509003||||||||||4081273965^Quintero^Alejandro^Ray^^MD^^AURORAMC
RXA|0|1|20260509103000|20260509103000|197^Influenza inactivated quadrivalent^CVX|0.5|mL|IM|LA^Left Arm||||||N7788DD|20270301|SNF^Sanofi Pasteur
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||197^Influenza inactivated quadrivalent^CVX||||||F
OBX|2|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
```

---

## 4. VXU^V04 - HPV vaccination for adolescent at Fort Collins Family Medicine

```
MSH|^~\&|FCFM|FTCOLLINS_FM|CIIS|CDPHE|20260509130000||VXU^V04^VXU_V04|FCFM20260509130000001|P|2.5.1|||AL|NE
PID|1||CIIS30004^^^CIIS^SR~FC22345^^^FCFM^MR||Bjornstad^Sienna^Elaine||20140722|F|||1923 Remington St^^Fort Collins^CO^80525^USA||^PRN^PH^^1^970^6618470||ENG|S
PD1||||9130274856^Herrera^Diane^Nicole^^MD^^FCFM
NK1|1|Bjornstad^Carolyn^Ruth|MTH|1923 Remington St^^Fort Collins^CO^80525^USA|^PRN^PH^^1^970^6618471
ORC|RE|VAX20260509004||||||||||9130274856^Herrera^Diane^Nicole^^MD^^FCFM
RXA|0|1|20260509123000|20260509123000|165^HPV9^CVX|0.5|mL|IM|LA^Left Arm||||||K9900EE|20270901|MSD^Merck Sharp and Dohme
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||165^HPV9^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20191015||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 5. VXU^V04 - Pneumococcal vaccination for elderly at Colorado Springs Senior Care

```
MSH|^~\&|CSSC|COSPRINGS_SC|CIIS|CDPHE|20260509140000||VXU^V04^VXU_V04|CSSC20260509140000001|P|2.5.1|||AL|NE
PID|1||CIIS30005^^^CIIS^SR~CS88901^^^CSSC^MR||Padilla^Gerald^Wayne^^Mr.||19540318|M|||1840 Cheyenne Blvd^^Colorado Springs^CO^80906^USA||^PRN^PH^^1^719^5028134||ENG|W
PD1||||6247901538^Swanson^Kimberly^Faye^^MD^^CSSC
ORC|RE|VAX20260509005||||||||||6247901538^Swanson^Kimberly^Faye^^MD^^CSSC
RXA|0|1|20260509133000|20260509133000|216^PCV20^CVX|0.5|mL|IM|LA^Left Arm||||||P2233FF|20271201|PFE^Pfizer Inc
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||216^PCV20^CVX||||||F
OBX|2|CE|59779-9^Immunization Schedule^LN||BD01^Primary Series^HL70396||||||F
```

---

## 6. VXU^V04 - Tdap vaccination for pregnant woman at Pueblo Community Health

```
MSH|^~\&|PCH|PUEBLO_CH|CIIS|CDPHE|20260509143000||VXU^V04^VXU_V04|PCH20260509143000001|P|2.5.1|||AL|NE
PID|1||CIIS30006^^^CIIS^SR~PC56789^^^PCH^MR||Archuleta^Veronica^Celeste^^Mrs.||19930411|F|||618 W Abriendo Ave^^Pueblo^CO^81004^USA||^PRN^PH^^1^719^2450793||SPA|M
PD1||||8305127694^Montoya^Ricardo^Enrique^^MD^^PCH
ORC|RE|VAX20260509006||||||||||8305127694^Montoya^Ricardo^Enrique^^MD^^PCH
RXA|0|1|20260509140000|20260509140000|115^Tdap^CVX|0.5|mL|IM|LA^Left Arm||||||T4455GG|20270601|GSK^GlaxoSmithKline
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||115^Tdap^CVX||||||F
OBX|2|CE|30963-3^Vaccine administered during pregnancy^LN||Y^Yes^HL70136||||||F
```

---

## 7. VXR^V03 - Immunization history response from CIIS

```
MSH|^~\&|CIIS|CDPHE|BOULDERPED|BOULDER_PEDIATRICS|20260509100000||VXR^V03^VXR_V03|CIIS20260509100000001|P|2.5.1|||AL|NE
MSA|AA|QRY20260509001
QRD|20260509100000|R|I|Q20260509001|||1^RD|CIIS30001^^^CIIS^SR|VXI|
PID|1||CIIS30001^^^CIIS^SR||Gallegos^Camila^Renata||20260102|F|||4710 Baseline Rd^^Boulder^CO^80303^USA||^PRN^PH^^1^303^4429817||SPA|S
ORC|RE|CIIS-H20260509001||||||||||5528193047^Linden^Margaret^Elise^^MD^^BOULDERPED
RXA|0|1|20260102|20260102|08^Hep B adolescent or pediatric^CVX|0.5|mL|IM|RT^Right Thigh||||||H1122AA|20270601|MSD^Merck Sharp and Dohme
RXA|0|2|20260302|20260302|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U3344BB|20270301|SKB^GlaxoSmithKline
RXA|0|3|20260302|20260302|10^IPV^CVX|0.5|mL|SC|LT^Left Thigh||||||P5566CC|20270601|SNF^Sanofi Pasteur
RXA|0|4|20260302|20260302|133^PCV13^CVX|0.5|mL|IM|LT^Left Thigh||||||V7788DD|20270901|PFE^Pfizer Inc
RXA|0|5|20260302|20260302|116^Rotavirus pentavalent^CVX|2.0|mL|PO|||||||R9900EE|20270301|MSD^Merck Sharp and Dohme
RXA|0|6|20260509|20260509|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh||||||U1234AB|20270301|SKB^GlaxoSmithKline
```

---

## 8. VXQ^V01 - Immunization record query to CIIS from Denver Health

```
MSH|^~\&|DENVERHEALTH|DH|CIIS|CDPHE|20260509110000||VXQ^V01^VXQ_V01|DH20260509110000002|P|2.5.1|||AL|NE
QRD|20260509110000|R|I|QRY20260509002|||1^RD|CIIS30002^^^CIIS^SR|VXI|
QRF|CIIS|20260509||20260509
```

---

## 9. ACK^V04 - Positive acknowledgment from CIIS for VXU

```
MSH|^~\&|CIIS|CDPHE|BOULDERPED|BOULDER_PEDIATRICS|20260509090100||ACK^V04^ACK|CIISACK20260509090100001|P|2.5.1|||AL|NE
MSA|AA|BP20260509090000001|Immunization record accepted and stored in CIIS
```

---

## 10. ACK^V04 - Application error from CIIS for invalid CVX code

```
MSH|^~\&|CIIS|CDPHE|AURORAMC|AURORA_MED|20260509110100||ACK^V04^ACK|CIISACK20260509110100001|P|2.5.1|||AL|NE
MSA|AE|AM20260509110000001|Invalid vaccine code in RXA segment
ERR||RXA^1^5^1|103^Table value not found^HL70357|E||||CVX code 999 is not a recognized vaccine code in CIIS. Please verify and resubmit.
```

---

## 11. RSP^K11 - Immunization history query response from CIIS

```
MSH|^~\&|CDPHE_CIIS|CDPHE|FCFM|FTCOLLINS_FM|20260509131000||RSP^K11^RSP_K11|CIIS20260509131000001|P|2.5.1|||AL|NE
MSA|AA|FCFM20260509130000001
QAK|Q20260509003|OK|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20260509003|CIIS30004^^^CIIS^SR
PID|1||CIIS30004^^^CIIS^SR||Bjornstad^Sienna^Elaine||20140722|F|||1923 Remington St^^Fort Collins^CO^80525^USA||^PRN^PH^^1^970^6618470
ORC|RE|CIIS-H20260509003
RXA|0|1|20140922|20140922|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|2|20141122|20141122|20^DTaP^CVX|0.5|mL|IM|LT^Left Thigh
RXA|0|3|20150122|20150122|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|4|20150722|20150722|20^DTaP^CVX|0.5|mL|IM|RT^Right Thigh
RXA|0|5|20180722|20180722|20^DTaP^CVX|0.5|mL|IM|LA^Left Arm
OBX|1|CE|59779-9^Immunization Schedule^LN||VXC16^DTaP series complete^CDCPHINVS||||||F
```

---

## 12. VXU^V04 - Historical vaccination entry (data migration) at Greeley clinic

```
MSH|^~\&|GREELEYFM|GREELEY_FM|CIIS|CDPHE|20260509150000||VXU^V04^VXU_V04|GFM20260509150000001|P|2.5.1|||AL|NE
PID|1||CIIS30007^^^CIIS^SR~GF77812^^^GREELEYFM^MR||Kowalski^Nathan^Gregory^^Mr.||19950815|M|||2814 10th Ave^^Greeley^CO^80631^USA||^PRN^PH^^1^970^3569014||ENG|S
PD1||||1749203856^Duran^Patricia^Rose^^MD^^GREELEYFM
ORC|RE|VAX20260509007||||||||||1749203856^Duran^Patricia^Rose^^MD^^GREELEYFM
RXA|0|1|20050101|20050101|08^Hep B adolescent or pediatric^CVX|999|mL|IM|||00^New immunization record^NIP001||||||||CP|A
OBX|1|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|2|CE|69764-9^Document type^LN||253088698300026411121116^Historical^cdcgs1vis||||||F
```

---

## 13. VXU^V04 - Zoster vaccination at Lakewood Senior Health

```
MSH|^~\&|LAKEWOODSH|LAKEWOOD_SH|CIIS|CDPHE|20260509153000||VXU^V04^VXU_V04|LSH20260509153000001|P|2.5.1|||AL|NE
PID|1||CIIS30008^^^CIIS^SR~LW90234^^^LAKEWOODSH^MR||Thornburg^Gloria^Maxine^^Mrs.||19520627|F|||8350 W Colfax Ave^^Lakewood^CO^80215^USA||^PRN^PH^^1^303^2380547||ENG|W
PD1||||3692580147^Espinosa^Victor^Manuel^^MD^^LAKEWOODSH
ORC|RE|VAX20260509008||||||||||3692580147^Espinosa^Victor^Manuel^^MD^^LAKEWOODSH
RXA|0|1|20260509150000|20260509150000|187^Zoster recombinant^CVX|0.5|mL|IM|LA^Left Arm||||||Z6677HH|20271201|GSK^GlaxoSmithKline
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||187^Zoster recombinant^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||1||||||F
```

---

## 14. ACK^V04 - Acknowledgment with warning from CIIS for duplicate vaccination

```
MSH|^~\&|CIIS|CDPHE|PCH|PUEBLO_CH|20260509143100||ACK^V04^ACK|CIISACK20260509143100001|P|2.5.1|||AL|NE
MSA|AA|PCH20260509143000001|Immunization record accepted with warning
ERR||RXA^1^5|100^Segment sequence error^HL70357|W||||Possible duplicate vaccination detected. CIIS already contains a Tdap record dated 20260509 for this patient. Record stored but flagged for review.
```

---

## 15. RSP^K11 - No records found response from CIIS

```
MSH|^~\&|CDPHE_CIIS|CDPHE|DENVERHEALTH|DH|20260509112000||RSP^K11^RSP_K11|CIIS20260509112000001|P|2.5.1|||AL|NE
MSA|AA|DH20260509110000002
QAK|Q20260509004|NF|Z34^Request Immunization History^CDCPHINVS
QPD|Z34^Request Immunization History^CDCPHINVS|Q20260509004|CIIS30099^^^CIIS^SR
```

---

## 16. VXU^V04 - Immunization with OBX ED containing immunization certificate as base64

```
MSH|^~\&|COIMM|COSPRINGS_PED|CIIS|CDPHE|20260509160000||VXU^V04^VXU_V04|CSP20260509160000001|P|2.5.1|||AL|NE
PID|1||CIIS30009^^^CIIS^SR~CP33456^^^COSPRINGPED^MR||Vigil^Mateo^Andres||20200415|M|||2715 N Nevada Ave^^Colorado Springs^CO^80907^USA||^PRN^PH^^1^719^6304589||SPA|S
PD1||||2058419376^Callahan^Brenda^Sue^^MD^^COSPRINGPED
NK1|1|Vigil^Adriana^Paola|MTH|2715 N Nevada Ave^^Colorado Springs^CO^80907^USA|^PRN^PH^^1^719^6304590
ORC|RE|VAX20260509009||||||||||2058419376^Callahan^Brenda^Sue^^MD^^COSPRINGPED
RXA|0|1|20260509153000|20260509153000|94^MMRV^CVX|0.5|mL|IM|LA^Left Arm||||||L8899JJ|20270601|MSD^Merck Sharp and Dohme
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||94^MMRV^CVX||||||F
OBX|2|ED|11369-6^Immunization Certificate^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4KZW5kb2Jq||||||F|||20260509160000
```

---

## 17. VXU^V04 - COVID-19 pediatric vaccination with immunization certificate base64

```
MSH|^~\&|CO_IIS|DENVERPED|CIIS|CDPHE|20260509163000||VXU^V04^VXU_V04|DP20260509163000001|P|2.5.1|||AL|NE
PID|1||CIIS30010^^^CIIS^SR~DP44567^^^DENVERPED^MR||Sandoval^Lily^Christine||20210303|F|||3450 E Colfax Ave^^Denver^CO^80206^USA||^PRN^PH^^1^303^7715820||ENG|S
PD1||||6804213597^Whitfield^Jerome^Alan^^MD^^DENVERPED
NK1|1|Sandoval^Danielle^Marie|MTH|3450 E Colfax Ave^^Denver^CO^80206^USA|^PRN^PH^^1^303^7715821
ORC|RE|VAX20260509010||||||||||6804213597^Whitfield^Jerome^Alan^^MD^^DENVERPED
RXA|0|1|20260509160000|20260509160000|300^COVID-19 VACCINE MRNA BIVALENT^CVX|0.25|mL|IM|LA^Left Arm||||||M2244KK|20260901|MOD^ModernaTX Inc
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|30956-7^Vaccine Type^LN||300^COVID-19 Vaccine mRNA bivalent^CVX||||||F
OBX|2|NM|30973-2^Dose number in series^LN||3||||||F
OBX|3|ED|11369-6^Immunization Certificate^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdID4+||||||F|||20260509163000
```

---

## 18. VXQ^V01 - Immunization query from Broomfield pediatrics to CIIS

```
MSH|^~\&|BROOMFIELDPED|BROOMFIELD_PED|CIIS|CDPHE|20260509170000||VXQ^V01^VXQ_V01|BFP20260509170000001|P|2.5.1|||AL|NE
QRD|20260509170000|R|I|QRY20260509005|||1^RD|CIIS30004^^^CIIS^SR|VXI|
QRF|CIIS|20140101||20260509
```

---

## 19. RSP^K11 - Query response with complete immunization forecast from CIIS

```
MSH|^~\&|CDPHE_CIIS|CDPHE|BOULDERPED|BOULDER_PEDIATRICS|20260509101000||RSP^K11^RSP_K11|CIIS20260509101000002|P|2.5.1|||AL|NE
MSA|AA|BP20260509100000001
QAK|Q20260509005|OK|Z44^Request Evaluated History and Forecast^CDCPHINVS
QPD|Z44^Request Evaluated History and Forecast^CDCPHINVS|Q20260509005|CIIS30001^^^CIIS^SR
PID|1||CIIS30001^^^CIIS^SR||Gallegos^Camila^Renata||20260102|F|||4710 Baseline Rd^^Boulder^CO^80303^USA
ORC|RE|CIIS-E20260509001
RXA|0|1|20260102|20260102|08^Hep B adolescent or pediatric^CVX|0.5|mL
OBX|1|CE|59781-5^Dose validity^LN||Y^Valid^HL70136||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||08^Hep B adolescent or pediatric^CVX||||||F
OBX|3|DT|30980-7^Date vaccination due^LN||20260502||||||F
OBX|4|CE|59783-1^Status in immunization series^LN||LA13422-3^On Schedule^LN||||||F
ORC|RE|CIIS-F20260509001
RXA|0|999|20260509|20260509|998^No vaccine administered^CVX|999
OBX|1|CE|30956-7^Vaccine Type^LN||20^DTaP^CVX||||||F
OBX|2|DT|30980-7^Date vaccination due^LN||20260702||||||F
OBX|3|CE|59783-1^Status in immunization series^LN||LA13423-1^Overdue^LN||||||F
```

---

## 20. ACK^V04 - Rejection from CIIS for missing patient identifier

```
MSH|^~\&|CIIS|CDPHE|GREELEYFM|GREELEY_FM|20260509150100||ACK^V04^ACK|CIISACK20260509150100001|P|2.5.1|||AL|NE
MSA|AR|GFM20260509150000001|Message rejected - missing required patient identifier
ERR||PID^1^3|101^Required field missing^HL70357|E||||PID-3 (Patient Identifier List) is required and must contain at least one identifier with an assigning authority recognized by CIIS. Resubmit with valid CIIS or MRN identifier.
```
