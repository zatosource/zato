# Altera Sunrise Clinical Manager - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Singapore General Hospital

```
MSH|^~\&|SUNRISE_CM|SGH|NEHR|IHIS|20260115083012||ADT^A01^ADT_A01|SGH20260115083012001|P|2.5|||AL|NE||UNICODE UTF-8|||SG_NEHR_ADT^IHISg^2.16.840.1.113883.3.3654^ISO
EVN|A01|20260115083012|||DR_CHEW^Chew^Kok Beng^^^^^SGH^^^^^NPI
PID|1||S8834521G^^^SGH^NRIC~20260115001^^^SGH^MRN||Krishnan^Deepa^^^^||19880314|F|||Blk 123 Ang Mo Kio Ave 3 #08-456^^Singapore^^560123^SG||+6591234567^PRN^PH|||M|||S8834521G|||||||SG||||N
PV1|1|I|SGH-W12^12-05^A^SGH||||23456^Chew^Kok Beng^^^^^SGH^^^^^NPI||MED||||1|||23456^Chew^Kok Beng^^^^^SGH^^^^^NPI|IP||C|||||||||||||||||||SGH|||20260115083000
PV2|||^Pneumonia||||||20260115|||||||||||||N
IN1|1|MEDI^Medisave^SG_SCHEME|CPFB|Central Provident Fund Board^^^^^^^^^^SG|Robinson Rd^^Singapore^^068914^SG|+6562270027|||||20260101|20261231|||S8834521G|Krishnan^Deepa^^^^|SELF|19880314|Blk 123 Ang Mo Kio Ave 3 #08-456^^Singapore^^560123^SG
NK1|1|Krishnan^Arjun^^^^|FTH|Blk 123 Ang Mo Kio Ave 3 #08-456^^Singapore^^560123^SG|+6598765432^PRN^PH
AL1|1|DA|PCN^Penicillin^SG_DRUG|MO||20200115
DG1|1||J18.9^Pneumonia, unspecified^ICD10SG|||A
```

---

## 2. ADT^A04 - Outpatient registration at Tan Tock Seng Hospital

```
MSH|^~\&|SUNRISE|TTSH|NEHR|IHIS|20260203140530||ADT^A04^ADT_A01|TTSH20260203140530002|P|2.5|||AL|NE||UNICODE UTF-8|||SG_NEHR_ADT^IHISg^2.16.840.1.113883.3.3654^ISO
EVN|A04|20260203140530|||REG_CLERK^Foo^Mei Yin^^^^^TTSH^^^^^STAFF
PID|1||T0234567J^^^TTSH^NRIC~30260203001^^^TTSH^MRN||Tay^Boon Huat^^^^||19720809|M|||Blk 456 Toa Payoh Lorong 8 #12-789^^Singapore^^310456^SG||+6581234567^PRN^PH|||S|||T0234567J|||||||SG||||N
PV1|1|O|TTSH-SOC^CLINIC-3A^^TTSH||||67890^Quek^Li Ping^^^^^TTSH^^^^^NPI||GEN||||1|||67890^Quek^Li Ping^^^^^TTSH^^^^^NPI|OP||B|||||||||||||||||||TTSH|||20260203140500
PV2|||^Diabetes Mellitus follow-up
IN1|1|CHAS^Community Health Assist Scheme^SG_SCHEME|MOH_SG|Ministry of Health^^^^^^^^^^SG|College Rd^^Singapore^^169854^SG|+6563259220|||||20260101|20261231|||T0234567J|Tay^Boon Huat^^^^|SELF|19720809|Blk 456 Toa Payoh Lorong 8 #12-789^^Singapore^^310456^SG
DG1|1||E11.9^Type 2 diabetes mellitus without complications^ICD10SG|||A
```

---

## 3. ADT^A08 - Patient information update at National University Hospital

```
MSH|^~\&|SUNRISE_CM|NUH|NEHR|IHIS|20260310091500||ADT^A08^ADT_A01|NUH20260310091500003|P|2.5|||AL|NE||UNICODE UTF-8|||SG_NEHR_ADT^IHISg^2.16.840.1.113883.3.3654^ISO
EVN|A08|20260310091500|||ADM_OFC^Poh^Siew Ting^^^^^NUH^^^^^STAFF
PID|1||F7654321K^^^NUH^NRIC~40260310001^^^NUH^MRN||Nair^Priya^^^^||19951120|F|||Blk 78 Jurong West St 42 #03-210^^Singapore^^640078^SG||+6597654321^PRN^PH~+6567654321^WPN^PH|||M|||F7654321K|||||||SG||||N
PV1|1|O|NUH-SOC^WOMEN-01^^NUH||||34567^Seah^Mei Ling^^^^^NUH^^^^^NPI||OBG||||1|||34567^Seah^Mei Ling^^^^^NUH^^^^^NPI|OP||C|||||||||||||||||||NUH|||20260310091000
NK1|1|Nair^Vikram^^^^|SPO|Blk 78 Jurong West St 42 #03-210^^Singapore^^640078^SG|+6596543210^PRN^PH
```

---

## 4. ADT^A03 - Discharge from Changi General Hospital

```
MSH|^~\&|ALTERA_SCM|CGH|NEHR|IHIS|20260418163045||ADT^A03^ADT_A03|CGH20260418163045004|P|2.5|||AL|NE||UNICODE UTF-8|||SG_NEHR_ADT^IHISg^2.16.840.1.113883.3.3654^ISO
EVN|A03|20260418163045|||45678^Chan^Keng Liang^^^^^CGH^^^^^NPI
PID|1||S7712345A^^^CGH^NRIC~50260418001^^^CGH^MRN||Pereira^Dominic^^^^||19770315|M|||Blk 234 Tampines St 21 #05-678^^Singapore^^520234^SG||+6589876543^PRN^PH|||M|||S7712345A|||||||SG||||N
PV1|1|I|CGH-W8^08-12^B^CGH||||45678^Chan^Keng Liang^^^^^CGH^^^^^NPI||SUR||||1|||45678^Chan^Keng Liang^^^^^CGH^^^^^NPI|IP||C|||||||||||||||20260412090000||20260418160000||||CGH|||20260412090000
PV2|||^Appendectomy recovery||||||20260412|20260418||||||||||||N
DG1|1||K35.80^Unspecified acute appendicitis^ICD10SG|||A
DG1|2||Z48.9^Encounter for other specified surgical aftercare^ICD10SG|||F
PR1|1||0DTJ4ZZ^Resection of Appendix, Percutaneous Endoscopic Approach^ICD10PCS|Laparoscopic appendectomy|20260412103000|||||45678^Chan^Keng Liang^^^^^CGH^^^^^NPI
```

---

## 5. ORU^R01 - Laboratory result from KK Women's and Children's Hospital

```
MSH|^~\&|SUNRISE_CM|KKH|LIS|KKH_LAB|20260122102300||ORU^R01^ORU_R01|KKH20260122102300005|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||G1234567N^^^KKH^NRIC~60260122001^^^KKH^MRN||Hamid^Nur Aisyah^^^^||20180506|F|||Blk 567 Bukit Batok West Ave 8 #11-345^^Singapore^^650567^SG||+6592345678^PRN^PH
PV1|1|O|KKH-PED^CLINIC-2B^^KKH||||56789^Wee^Soo Keng^^^^^KKH^^^^^NPI||PED||||1|||56789^Wee^Soo Keng^^^^^KKH^^^^^NPI|OP
ORC|RE|KKH-ORD-20260122-001|KKH-LAB-20260122-001||CM||||20260122093000|||56789^Wee^Soo Keng^^^^^KKH^^^^^NPI
OBR|1|KKH-ORD-20260122-001|KKH-LAB-20260122-001|58410-2^CBC panel^LN|||20260122093000|||||||||56789^Wee^Soo Keng^^^^^KKH^^^^^NPI||||||20260122102000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood^LN||8.5|10*3/uL|4.5-13.0||||F|||20260122102000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.8|10*6/uL|4.0-5.5||||F|||20260122102000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||12.6|g/dL|11.5-15.5||||F|||20260122102000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood^LN||37.8|%|35-45||||F|||20260122102000
OBX|5|NM|777-3^Platelets [#/volume] in Blood^LN||312|10*3/uL|150-400||||F|||20260122102000
```

---

## 6. ORU^R01 - Radiology result with embedded PDF report

```
MSH|^~\&|SUNRISE|SGH|RIS|SGH_RAD|20260225144500||ORU^R01^ORU_R01|SGH20260225144500006|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||S9045678B^^^SGH^NRIC~70260225001^^^SGH^MRN||Yusof^Faizal^^^^||19900222|M|||Blk 89 Queenstown Rd #06-123^^Singapore^^160089^SG||+6594567890^PRN^PH
PV1|1|I|SGH-W5^05-03^A^SGH||||78901^Pang^Ai Hua^^^^^SGH^^^^^NPI||RAD||||1|||78901^Pang^Ai Hua^^^^^SGH^^^^^NPI|IP
ORC|RE|SGH-ORD-20260225-001|SGH-RAD-20260225-001||CM||||20260225110000|||78901^Pang^Ai Hua^^^^^SGH^^^^^NPI
OBR|1|SGH-ORD-20260225-001|SGH-RAD-20260225-001|71046^Chest X-ray PA and lateral^LN|||20260225113000|||||||||78901^Pang^Ai Hua^^^^^SGH^^^^^NPI||||||20260225143000|||F
OBX|1|FT|71046^Chest X-ray PA and lateral^LN||Heart size is within normal limits. Lungs are clear bilaterally. No pleural effusion or pneumothorax. No acute osseous abnormality. Impression: Normal chest radiograph.||||||F|||20260225143000
OBX|2|ED|PDF^Radiology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F|||20260225143000
```

---

## 7. ORM^O01 - Laboratory order from Alexandra Hospital

```
MSH|^~\&|SUNRISE_CM|AH|LIS|AH_LAB|20260305081500||ORM^O01^ORM_O01|AH20260305081500007|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||S6523456D^^^AH^NRIC~80260305001^^^AH^MRN||Ang^Seng Chye^^^^||19650812|M|||Blk 12 Marine Parade Rd #01-456^^Singapore^^449269^SG||+6586543210^PRN^PH|||M|||S6523456D|||||||SG||||N
PV1|1|I|AH-W3^03-08^B^AH||||89012^Menon^Lakshmi^^^^^AH^^^^^NPI||MED||||1|||89012^Menon^Lakshmi^^^^^AH^^^^^NPI|IP
ORC|NW|AH-ORD-20260305-001|||IP||||20260305081500|||89012^Menon^Lakshmi^^^^^AH^^^^^NPI
OBR|1|AH-ORD-20260305-001||24323-8^Comprehensive metabolic panel^LN|||20260305081500|||||||||89012^Menon^Lakshmi^^^^^AH^^^^^NPI
OBR|2|AH-ORD-20260305-002||57021-8^CBC W Auto Differential panel^LN|||20260305081500|||||||||89012^Menon^Lakshmi^^^^^AH^^^^^NPI
OBR|3|AH-ORD-20260305-003||2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN|||20260305081500|||||||||89012^Menon^Lakshmi^^^^^AH^^^^^NPI
```

---

## 8. ORM^O01 - Radiology order from Khoo Teck Puat Hospital

```
MSH|^~\&|ALTERA_SCM|KTPH|RIS|KTPH_RAD|20260410093000||ORM^O01^ORM_O01|KTPH20260410093000008|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||T0345678K^^^KTPH^NRIC~90260410001^^^KTPH^MRN||Razali^Nurul Huda Binte^^^^||20030915|F|||Blk 345 Woodlands Ring Rd #09-567^^Singapore^^730345^SG||+6590123456^PRN^PH|||S|||T0345678K|||||||SG||||N
PV1|1|E|KTPH-ED^ED-TRAUMA^^KTPH||||90123^Chia^Kah Heng^^^^^KTPH^^^^^NPI||EM||||7|||90123^Chia^Kah Heng^^^^^KTPH^^^^^NPI|EM
ORC|NW|KTPH-ORD-20260410-001|||UR||||20260410093000|||90123^Chia^Kah Heng^^^^^KTPH^^^^^NPI
OBR|1|KTPH-ORD-20260410-001||36643-5^XR Chest 2 Views^LN|||20260410093000||||||HISTORY: Fall from height. Rule out rib fractures.||||90123^Chia^Kah Heng^^^^^KTPH^^^^^NPI
```

---

## 9. RDE^O11 - Pharmacy order for inpatient medication at Mount Elizabeth Hospital

```
MSH|^~\&|SUNRISE_CM|MEH|PHARM|MEH_RX|20260128103000||RDE^O11^RDE_O11|MEH20260128103000009|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||S7256789C^^^MEH^NRIC~10260128001^^^MEH^MRN||De Souza^Maria^^^^||19720430|F|||12 Cairnhill Rd #15-08^^Singapore^^229740^SG||+6593456789^PRN^PH|||M|||S7256789C|||||||SG||||N
PV1|1|I|MEH-W6^06-01^A^MEH||||12345^Heng^Boon Kiat^^^^^MEH^^^^^NPI||MED||||1|||12345^Heng^Boon Kiat^^^^^MEH^^^^^NPI|IP
AL1|1|DA|ASA^Aspirin^SG_DRUG|SV||20150601
ORC|NW|MEH-ORD-20260128-001|||IP||||20260128103000|||12345^Heng^Boon Kiat^^^^^MEH^^^^^NPI
RXE|1^BID^HL70335|318186^Amlodipine 5 MG Oral Tablet^RXNORM|5||mg|TAB||0||||||||||||||||||||||BID
RXR|PO^Oral^HL70162
RXC|B|318186^Amlodipine 5 MG Oral Tablet^RXNORM|5|mg
TQ1|1||BID^Twice daily^HL70335|0800&1400|20260128|20260228
```

---

## 10. RDE^O11 - Intravenous medication order at Sengkang General Hospital

```
MSH|^~\&|SUNRISE|SKH|PHARM|SKH_RX|20260220150000||RDE^O11^RDE_O11|SKH20260220150000010|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||G9876543M^^^SKH^NRIC~20260220001^^^SKH^MRN||Hassan^Bin Iskandar^^^^||19850717|M|||Blk 678 Sengkang East Way #04-321^^Singapore^^540678^SG||+6588765432^PRN^PH|||M|||G9876543M|||||||SG||||N
PV1|1|I|SKH-ICU^ICU-03^A^SKH||||23456^Yong^Chee Keong^^^^^SKH^^^^^NPI||MED||||1|||23456^Yong^Chee Keong^^^^^SKH^^^^^NPI|IP
ORC|NW|SKH-ORD-20260220-001|||IP||||20260220150000|||23456^Yong^Chee Keong^^^^^SKH^^^^^NPI
RXE|1^Q6H^HL70335|1596450^Piperacillin 4000 MG / Tazobactam 500 MG Injection^RXNORM|4.5||g|VL||0||||||||||||||||||||||Q6H
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXC|B|1596450^Piperacillin-Tazobactam 4.5g^RXNORM|4.5|g
RXC|A|400^Sodium Chloride 0.9% 100mL^LOCAL|100|mL
TQ1|1||Q6H^Every 6 hours^HL70335||20260220|20260227||30^min
```

---

## 11. SIU^S12 - Appointment booking at National Heart Centre Singapore

```
MSH|^~\&|SUNRISE_CM|NHCS|SCHED|NHCS_APT|20260318090000||SIU^S12^SIU_S12|NHCS20260318090000011|P|2.5|||AL|NE||UNICODE UTF-8
SCH|NHCS-APT-20260401-001|NHCS-APT-20260401-001|||||ROUTINE^Routine^HL70277|FOLLOWUP^Follow-up^HL70276|30|min|^^30^20260401093000^20260401100000||34567^Yeoh^Beng Seng^^^^^NHCS^^^^^NPI|+6563214567^WPN^PH|NHCS-CARDIOLOGY^101^^NHCS|34567^Yeoh^Beng Seng^^^^^NHCS^^^^^NPI||BOOKED
PID|1||S8123456H^^^NHCS^NRIC~30260318001^^^NHCS^MRN||Pillai^Karthik^^^^||19810605|M|||Blk 901 Hougang Ave 9 #07-234^^Singapore^^530901^SG||+6591122334^PRN^PH|||M|||S8123456H|||||||SG||||N
PV1|1|O|NHCS-CARDIOLOGY^CLINIC-01^^NHCS||||34567^Yeoh^Beng Seng^^^^^NHCS^^^^^NPI||CAR
RGS|1|A
AIS|1|A|CARDIOLOGY^Cardiology Consultation^LOCAL|20260401093000|0|min|30|min
AIG|1|A|34567^Yeoh^Beng Seng^^^^^NHCS^^^^^NPI|DOCTOR^Doctor^HL70443
AIL|1|A|NHCS-CARDIOLOGY^101^^NHCS|CLINIC^Clinic Room^HL70305
```

---

## 12. SIU^S14 - Appointment modification at National Dental Centre Singapore

```
MSH|^~\&|ALTERA_SCM|NDCS|SCHED|NDCS_APT|20260402110000||SIU^S14^SIU_S12|NDCS20260402110000012|P|2.5|||AL|NE||UNICODE UTF-8
SCH|NDCS-APT-20260415-001|NDCS-APT-20260415-001|||||ROUTINE^Routine^HL70277|FOLLOWUP^Follow-up^HL70276|45|min|^^45^20260415140000^20260415144500||56789^Low^Li Wen^^^^^NDCS^^^^^NPI|+6563248888^WPN^PH|NDCS-ENDO^203^^NDCS|56789^Low^Li Wen^^^^^NDCS^^^^^NPI||BOOKED
PID|1||F6543210L^^^NDCS^NRIC~40260402001^^^NDCS^MRN||Chng^Hui Min^^^^||19980303|F|||Blk 456 Clementi Ave 1 #10-890^^Singapore^^120456^SG||+6590998877^PRN^PH|||S|||F6543210L|||||||SG||||N
PV1|1|O|NDCS-ENDO^CLINIC-02^^NDCS||||56789^Low^Li Wen^^^^^NDCS^^^^^NPI||DEN
RGS|1|A
AIS|1|A|ENDODONTICS^Endodontics Consultation^LOCAL|20260415140000|0|min|45|min
AIG|1|A|56789^Low^Li Wen^^^^^NDCS^^^^^NPI|DOCTOR^Doctor^HL70443
AIL|1|A|NDCS-ENDO^203^^NDCS|CLINIC^Clinic Room^HL70305
```

---

## 13. MDM^T02 - Clinical document notification with embedded PDF from Singapore General Hospital

```
MSH|^~\&|SUNRISE_CM|SGH|NEHR|IHIS|20260215161200||MDM^T02^MDM_T02|SGH20260215161200013|P|2.5|||AL|NE||UNICODE UTF-8
EVN|T02|20260215161200
PID|1||S8345678E^^^SGH^NRIC~50260215001^^^SGH^MRN||Soh^Boon Heng^^^^||19830919|M|||Blk 234 Bishan St 22 #14-567^^Singapore^^570234^SG||+6596677889^PRN^PH|||M|||S8345678E|||||||SG||||N
PV1|1|I|SGH-W10^10-02^A^SGH||||67890^Toh^Ai Lian^^^^^SGH^^^^^NPI||MED||||1|||67890^Toh^Ai Lian^^^^^SGH^^^^^NPI|IP
TXA|1|DS^Discharge Summary^HL70270|TX|20260215160000||20260215161000|||||67890^Toh^Ai Lian^^^^^SGH^^^^^NPI||SGH-DOC-20260215-001||||AU
OBX|1|ED|PDF^Discharge Summary^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F|||20260215161000
```

---

## 14. MDM^T06 - Addendum to clinical document at Ng Teng Fong General Hospital

```
MSH|^~\&|SUNRISE|NTFGH|NEHR|IHIS|20260322143000||MDM^T06^MDM_T06|NTFGH20260322143000014|P|2.5|||AL|NE||UNICODE UTF-8
EVN|T06|20260322143000
PID|1||S9156789F^^^NTFGH^NRIC~60260322001^^^NTFGH^MRN||Selvam^Anitha^^^^||19910811|F|||Blk 567 Jurong East St 24 #08-901^^Singapore^^600567^SG||+6585566778^PRN^PH|||S|||S9156789F|||||||SG||||N
PV1|1|I|NTFGH-W7^07-15^B^NTFGH||||78901^Kwek^Wei Ming^^^^^NTFGH^^^^^NPI||MED||||1|||78901^Kwek^Wei Ming^^^^^NTFGH^^^^^NPI|IP
TXA|1|ADDENDUM^Addendum^HL70270|TX|20260322142000||20260322143000|||||78901^Kwek^Wei Ming^^^^^NTFGH^^^^^NPI||NTFGH-DOC-20260322-001|NTFGH-DOC-20260320-001|||AU
OBX|1|FT|18842-5^Discharge summary^LN||Addendum: Patient's potassium level corrected to 3.8 mmol/L following IV supplementation. Discharge medications updated to include oral potassium chloride 600mg TDS for 5 days. Follow-up appointment scheduled at NTFGH Medical Clinic in 2 weeks.||||||F|||20260322143000
```

---

## 15. ORU^R01 - Microbiology culture result from Tan Tock Seng Hospital

```
MSH|^~\&|SUNRISE_CM|TTSH|LIS|TTSH_LAB|20260205173000||ORU^R01^ORU_R01|TTSH20260205173000015|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||S7867890G^^^TTSH^NRIC~70260205001^^^TTSH^MRN||Oei^Mei Fong^^^^||19780124|F|||Blk 890 Woodlands Dr 50 #02-345^^Singapore^^730890^SG||+6582233445^PRN^PH|||M|||S7867890G|||||||SG||||N
PV1|1|I|TTSH-W14^14-07^A^TTSH||||89012^Sim^Chee Hean^^^^^TTSH^^^^^NPI||MED||||1|||89012^Sim^Chee Hean^^^^^TTSH^^^^^NPI|IP
ORC|RE|TTSH-ORD-20260203-001|TTSH-LAB-20260205-001||CM||||20260203140000|||89012^Sim^Chee Hean^^^^^TTSH^^^^^NPI
OBR|1|TTSH-ORD-20260203-001|TTSH-LAB-20260205-001|87040^Blood Culture^LN|||20260203140000|||||||||89012^Sim^Chee Hean^^^^^TTSH^^^^^NPI||||||20260205170000|||F
OBX|1|CWE|600-7^Bacteria identified in Blood by Culture^LN||ECO^Escherichia coli^ORGANISM||||||F|||20260205170000
OBX|2|ST|29576-6^Bacterial susceptibility panel^LN||See individual results below||||||F|||20260205170000
OBX|3|ST|18862-3^Ampicillin [Susceptibility]^LN||R^Resistant||||||F|||20260205170000
OBX|4|ST|18878-9^Ceftriaxone [Susceptibility]^LN||S^Susceptible||||||F|||20260205170000
OBX|5|ST|18906-8^Gentamicin [Susceptibility]^LN||S^Susceptible||||||F|||20260205170000
OBX|6|ST|18928-2^Meropenem [Susceptibility]^LN||S^Susceptible||||||F|||20260205170000
OBX|7|ST|18932-4^Ciprofloxacin [Susceptibility]^LN||R^Resistant||||||F|||20260205170000
```

---

## 16. ORU^R01 - Histopathology result with embedded PDF from National Cancer Centre Singapore

```
MSH|^~\&|ALTERA_SCM|NCCS|LIS|NCCS_PATH|20260312100000||ORU^R01^ORU_R01|NCCS20260312100000016|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||S6934567H^^^NCCS^NRIC~80260312001^^^NCCS^MRN||Chua^Siew Peng^^^^||19690228|F|||Blk 123 Bukit Merah View #09-567^^Singapore^^150123^SG||+6597788990^PRN^PH|||W|||S6934567H|||||||SG||||N
PV1|1|I|NCCS-W3^03-05^A^NCCS||||90123^Balakrishnan^Kee Huat^^^^^NCCS^^^^^NPI||ONC||||1|||90123^Balakrishnan^Kee Huat^^^^^NCCS^^^^^NPI|IP
ORC|RE|NCCS-ORD-20260308-001|NCCS-PATH-20260312-001||CM||||20260308110000|||90123^Balakrishnan^Kee Huat^^^^^NCCS^^^^^NPI
OBR|1|NCCS-ORD-20260308-001|NCCS-PATH-20260312-001|22637-3^Pathology report^LN|||20260308110000|||||||||90123^Balakrishnan^Kee Huat^^^^^NCCS^^^^^NPI||||||20260312095000|||F
OBX|1|FT|22637-3^Pathology report^LN||Specimen: Left breast, lumpectomy. Gross: 4.5 x 3.2 x 2.8 cm specimen. Micro: Invasive ductal carcinoma, Grade 2, Nottingham score 6/9. Tumor size 1.8 cm. Margins clear, closest 5mm. ER positive (90%), PR positive (70%), HER2 negative (1+). Ki-67 15%. AJCC pT1c. No lymphovascular invasion.||||||F|||20260312095000
OBX|2|ED|PDF^Histopathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F|||20260312095000
```

---

## 17. ORM^O01 - Medication order from Raffles Hospital

```
MSH|^~\&|SUNRISE_CM|RH|PHARM|RH_RX|20260418091500||ORM^O01^ORM_O01|RH20260418091500017|P|2.4|||AL|NE||UNICODE UTF-8
PID|1||S8478901D^^^RH^NRIC~90260418001^^^RH^MRN||Fernandez^Miguel^^^^||19840616|M|||28 Thomson Rd #22-05^^Singapore^^307660^SG||+6593344556^PRN^PH|||M|||S8478901D|||||||SG||||N
PV1|1|I|RH-W4^04-10^A^RH||||01234^Aw^Bee Leng^^^^^RH^^^^^NPI||MED||||1|||01234^Aw^Bee Leng^^^^^RH^^^^^NPI|IP
AL1|1|DA|SULFA^Sulfonamides^SG_DRUG|MO||20190301
ORC|NW|RH-ORD-20260418-001|||IP||||20260418091500|||01234^Aw^Bee Leng^^^^^RH^^^^^NPI
OBR|1|RH-ORD-20260418-001||RXO^Pharmacy Order^LOCAL|||20260418091500|||||||||01234^Aw^Bee Leng^^^^^RH^^^^^NPI
RXO|197361^Metformin 500 MG Oral Tablet^RXNORM|500|mg||TAB|E|1||0||||||01234^Aw^Bee Leng^^^^^RH^^^^^NPI
RXR|PO^Oral^HL70162
```

---

## 18. ADT^A02 - Patient transfer within National University Hospital

```
MSH|^~\&|SUNRISE|NUH|NEHR|IHIS|20260501142000||ADT^A02^ADT_A02|NUH20260501142000018|P|2.5|||AL|NE||UNICODE UTF-8|||SG_NEHR_ADT^IHISg^2.16.840.1.113883.3.3654^ISO
EVN|A02|20260501142000|||45678^Mak^Kok Wah^^^^^NUH^^^^^NPI
PID|1||S8590123E^^^NUH^NRIC~10260501001^^^NUH^MRN||Rajaram^Srinivasan^^^^||19851003|M|||Blk 678 Pasir Ris Dr 6 #11-234^^Singapore^^510678^SG||+6587654321^PRN^PH|||M|||S8590123E|||||||SG||||N
PV1|1|I|NUH-ICU^ICU-08^A^NUH||||45678^Mak^Kok Wah^^^^^NUH^^^^^NPI||MED||||1|||45678^Mak^Kok Wah^^^^^NUH^^^^^NPI|IP||C|||||||||||||||||||NUH|||20260428090000
PV2|||^Post-cardiac surgery monitoring
```

---

## 19. SIU^S15 - Appointment cancellation at Singapore National Eye Centre

```
MSH|^~\&|ALTERA_SCM|SNEC|SCHED|SNEC_APT|20260425160000||SIU^S15^SIU_S12|SNEC20260425160000019|P|2.5|||AL|NE||UNICODE UTF-8
SCH|SNEC-APT-20260502-001|SNEC-APT-20260502-001|||||ROUTINE^Routine^HL70277|FOLLOWUP^Follow-up^HL70276|20|min|^^20^20260502100000^20260502102000||67890^Gan^Mei Ling^^^^^SNEC^^^^^NPI|+6562277255^WPN^PH|SNEC-GLAUCOMA^305^^SNEC|67890^Gan^Mei Ling^^^^^SNEC^^^^^NPI||CANCELLED
PID|1||T0456789L^^^SNEC^NRIC~20260425001^^^SNEC^MRN||Abdullah^Bin Rashid^^^^||20050222|M|||Blk 123 Punggol Field #06-789^^Singapore^^820123^SG||+6588990011^PRN^PH|||S|||T0456789L|||||||SG||||N
PV1|1|O|SNEC-GLAUCOMA^CLINIC-03^^SNEC||||67890^Gan^Mei Ling^^^^^SNEC^^^^^NPI||OPH
RGS|1|A
AIS|1|A|GLAUCOMA^Glaucoma Follow-up^LOCAL|20260502100000|0|min|20|min
```

---

## 20. ORU^R01 - Cardiac biomarker results from National Heart Centre Singapore

```
MSH|^~\&|SUNRISE_CM|NHCS|LIS|NHCS_LAB|20260508082000||ORU^R01^ORU_R01|NHCS20260508082000020|P|2.5|||AL|NE||UNICODE UTF-8
PID|1||S7201234B^^^NHCS^NRIC~30260508001^^^NHCS^MRN||Kok^Teck Soon^^^^||19720415|M|||Blk 345 Bedok North Ave 3 #07-123^^Singapore^^460345^SG||+6591234098^PRN^PH|||M|||S7201234B|||||||SG||||N
PV1|1|E|NHCS-ED^ED-01^^NHCS||||78901^Devi^Boon Seng^^^^^NHCS^^^^^NPI||CAR||||7|||78901^Devi^Boon Seng^^^^^NHCS^^^^^NPI|EM
ORC|RE|NHCS-ORD-20260508-001|NHCS-LAB-20260508-001||CM||||20260508074500|||78901^Devi^Boon Seng^^^^^NHCS^^^^^NPI
OBR|1|NHCS-ORD-20260508-001|NHCS-LAB-20260508-001|89579-7^Troponin I cardiac panel^LN|||20260508074500|||||||||78901^Devi^Boon Seng^^^^^NHCS^^^^^NPI||||||20260508081500|||F
OBX|1|NM|10839-9^Troponin I.cardiac [Mass/volume] in Serum or Plasma^LN||0.045|ng/mL|<0.04|H|||F|||20260508081500
OBX|2|NM|33762-6^NT-proBNP [Mass/volume] in Serum or Plasma^LN||892|pg/mL|<125|HH|||F|||20260508081500
OBX|3|NM|2157-6^Creatine kinase-MB [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L|0-24|H|||F|||20260508081500
OBX|4|NM|30522-7^C reactive protein [Mass/volume] in Serum or Plasma^LN||12.5|mg/L|0.0-5.0|H|||F|||20260508081500
OBX|5|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L|3.5-5.0||||F|||20260508081500
OBX|6|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||138|mmol/L|136-145||||F|||20260508081500
OBX|7|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.3|mg/dL|0.7-1.2|H|||F|||20260508081500
```
