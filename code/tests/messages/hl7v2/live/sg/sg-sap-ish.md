# SAP IS-H (Industry Solution for Healthcare) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to inpatient ward

```
MSH|^~\&|SAP_ISH|SGH^Singapore General Hospital|NEHR|MOH_SG|20240315083022||ADT^A01^ADT_A01|SGH2024031508302201|P|2.4|||AL|AL|SGP
EVN|A01|20240315083000|||ADMITCLERK01^Chua^Bee Keng
PID|1||S8234921A^^^NRIC^SG~SGH0001234^^^SGH^MR||Rajendran^Kumaran||19820415|M|||Blk 342 Ang Mo Kio Ave 3 #08-1234^^Singapore^^560342^SG||+6591274583^PRN^PH|||M|||S8234921A|||||||SG||||N
PV1|1|I|4B^402^A^SGH^^^^N|||||||MED||||1|||CON0045^Dr Oei^Li Fang^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240315083000
PV2|||^Pneumonia|||||||2||||||||||||N
NK1|1|Rajendran^Meena||+6598761245^PRN^PH|||||||||||||||||||||||||SGP
IN1|1|MEDISHIELD^Medishield Life||CPF Board^1 Jurong East Street 21^^Singapore^^609546^SG|||||||||20240101|20241231|||F|Rajendran^Kumaran|Self|19820415|Blk 342 Ang Mo Kio Ave 3 #08-1234^^Singapore^^560342^SG
```

---

## 2. ADT^A02 - Patient transfer between wards

```
MSH|^~\&|SAP_ISH|TTSH^Tan Tock Seng Hospital|CPIS|MOH_SG|20240412141530||ADT^A02^ADT_A02|TTSH2024041214153001|P|2.4|||AL|AL|SGP
EVN|A02|20240412141500|||WARDCLERK02^Toh^Lay Hoon
PID|1||S7512983B^^^NRIC^SG~TTSH0098765^^^TTSH^MR||Nair^Suresh Babu||19750823|M|||23 Lorong 5 Toa Payoh #12-345^^Singapore^^310023^SG||+6581290374^PRN^PH|||M|||S7512983B|||||||SG||||N
PV1|1|I|6A^612^B^TTSH^^^^N|U|||CON0112^Dr Heng^Siew Cheng^^^Dr^^^SAP_ISH||CON0112^Dr Heng^Siew Cheng^^^Dr^^^SAP_ISH|MED||||1|||CON0112^Dr Heng^Siew Cheng^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240410090000
PV2|||^Acute Myocardial Infarction
```

---

## 3. ADT^A03 - Patient discharge from hospital

```
MSH|^~\&|SAP_ISH|NUH^National University Hospital|NEHR|MOH_SG|20240520163045||ADT^A03^ADT_A03|NUH2024052016304501|P|2.4|||AL|AL|SGP
EVN|A03|20240520163000|||DISCCLERK05^Zuraidah^Binte Mohd
PID|1||S9045216C^^^NRIC^SG~NUH0054321^^^NUH^MR||Wee^Sok Hiang||19900612|F|||Blk 123 Bishan Street 12 #05-678^^Singapore^^570123^SG||+6592387410^PRN^PH|||S|||S9045216C|||||||SG||||N
PV1|1|I|8C^815^A^NUH^^^^N|||||||SUR||||1|||CON0078^Dr Shanmugam^Anand^^^Dr^^^SAP_ISH||||||||||||||||||||20240515100000||||||||20240520163000
PV2|||^Appendectomy^I9C|||||||3||||||||||||N
DG1|1|I9|540.9^Appendicitis NOS^I9C||20240515|A
```

---

## 4. ADT^A04 - Patient registration (outpatient)

```
MSH|^~\&|SAP_ISH|CGH^Changi General Hospital|CPIS|MOH_SG|20240610091500||ADT^A04^ADT_A04|CGH2024061009150001|P|2.5|||AL|AL|SGP
EVN|A04|20240610091500|||REG001^Hakim^Bin Roslan
PID|1||S8567432D^^^NRIC^SG~CGH0076543^^^CGH^MR||Pereira^Maria Celeste||19850301|F|||45 Simei Street 6 #03-210^^Singapore^^529899^SG||+6596548723^PRN^PH|||M|||S8567432D|||||||SG||||N
PV1|1|O|OPD3^CLINIC^A^CGH^^^^N|||||||CARDIO||||3|||CON0023^Dr Balakrishnan^Deepak^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240610091500
PV2|||^Follow-up Cardiology Review
IN1|1|INTEGRATED_SHIELD^Prudential PRUShield||Prudential Assurance Company|30 Cecil Street #30-01^^Singapore^^049712^SG|||||||||20240101|20241231|||F|Pereira^Maria Celeste|Self|19850301|45 Simei Street 6 #03-210^^Singapore^^529899^SG
```

---

## 5. ADT^A08 - Update patient information

```
MSH|^~\&|SAP_ISH|KTPH^Khoo Teck Puat Hospital|NEHR|MOH_SG|20240718103012||ADT^A08^ADT_A08|KTPH2024071810301201|P|2.4|||AL|AL|SGP
EVN|A08|20240718103000|||REGUPD03^Chia^Suat Mei
PID|1||S6823014E^^^NRIC^SG~KTPH0032145^^^KTPH^MR||Hassan^Zulkifli||19680910|M|||Blk 789 Woodlands Drive 60 #14-321^^Singapore^^730789^SG||+6587610943^PRN^PH~+6563218704^WPN^PH|||D|||S6823014E|||||||SG||||N
PV1|1|O|OPD1^CLINIC^B^KTPH^^^^N|||||||ORTHO||||3|||CON0091^Dr Quek^Geok Lian^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240718100000
NK1|1|Hassan^Rohani||+6591126748^PRN^PH||||||Emergency Contact
```

---

## 6. ADT^A11 - Cancel admission

```
MSH|^~\&|SAP_ISH|SKH^Sengkang General Hospital|CPIS|MOH_SG|20240225112200||ADT^A11^ADT_A11|SKH2024022511220001|P|2.4|||AL|AL|SGP
EVN|A11|20240225112200|||ADMITCLERK04^Koay^Poh Lin
PID|1||S7934208F^^^NRIC^SG~SKH0011234^^^SKH^MR||Sundaram^Prakash||19790514|M|||52 Sengkang East Way #09-876^^Singapore^^541052^SG||+6584509361^PRN^PH|||M|||S7934208F|||||||SG||||N
PV1|1|I|3A^305^C^SKH^^^^N|||||||MED||||1|||CON0034^Dr Yong^Mei Hui^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240225090000
```

---

## 7. ADT^A13 - Cancel discharge

```
MSH|^~\&|SAP_ISH|SGH^Singapore General Hospital|NEHR|MOH_SG|20240803145530||ADT^A13^ADT_A13|SGH2024080314553001|P|2.4|||AL|AL|SGP
EVN|A13|20240803145500|||DISCCLERK02^Norhayati^Binte Kamal
PID|1||S8145290G^^^NRIC^SG~SGH0067890^^^SGH^MR||Lau^Boon Seng||19810220|M|||Blk 567 Bedok North Street 3 #06-432^^Singapore^^460567^SG||+6593470218^PRN^PH|||M|||S8145290G|||||||SG||||N
PV1|1|I|7D^718^A^SGH^^^^N|||||||MED||||1|||CON0056^Dr Menon^Priya^^^Dr^^^SAP_ISH||||||||||||||||||||20240730120000||||||||20240803140000
```

---

## 8. ADT^A28 - Add person information (pre-registration)

```
MSH|^~\&|SAP_HEALTHCARE|AH^Alexandra Hospital|NEHR|MOH_SG|20240901080000||ADT^A28^ADT_A28|AH2024090108000001|P|2.5|||AL|AL|SGP
EVN|A28|20240901080000|||PREREG01^Faridah^Binte Osman
PID|1||G1234809N^^^FIN^SG~AH0004321^^^AH^MR||Desilva^Marcus Anthony||19950718|M|||10 Alexandra Road #02-100^^Singapore^^159012^SG||+6590047821^PRN^PH|||S|||G1234809N|||||||IN||||N
NK1|1|Desilva^Jennifer||+6590053417^PRN^PH||||||Spouse
```

---

## 9. ADT^A40 - Merge patient (link identifiers)

```
MSH|^~\&|SAP_ISH|NUHS^National University Health System|NEHR|MOH_SG|20240422160000||ADT^A40^ADT_A40|NUHS2024042216000001|P|2.4|||AL|AL|SGP
EVN|A40|20240422160000|||MPIADMIN^Low^Hwee Ling
PID|1||S7256103H^^^NRIC^SG~NUH0098765^^^NUH^MR||Choo^Kian Beng||19720305|M|||Blk 890 Jurong West Street 81 #11-543^^Singapore^^640890^SG||+6585674290^PRN^PH|||M|||S7256103H|||||||SG||||N
MRG|S7256103H^^^NRIC^SG~NUH0043210^^^NUH^MR||||||Choo^Kian Beng
```

---

## 10. DFT^P03 - Post detail financial transaction (inpatient charges)

```
MSH|^~\&|SAP_ISH|SGH^Singapore General Hospital|BILLING|SGH_FIN|20240615143000||DFT^P03^DFT_P03|SGH2024061514300001|P|2.4|||AL|AL|SGP
EVN|P03|20240615143000
PID|1||S8556412J^^^NRIC^SG~SGH0045678^^^SGH^MR||Teo^Beng Chuan||19850112|M|||Blk 234 Toa Payoh Lorong 8 #07-890^^Singapore^^310234^SG||+6591287034^PRN^PH|||M|||S8556412J|||||||SG||||N
PV1|1|I|5A^502^B^SGH^^^^N|||||||SUR||||1|||CON0067^Dr Venkatesh^Arun^^^Dr^^^SAP_ISH||||||||||||||||||||20240610080000||||||||20240615120000
FT1|1|20240615|20240615143000|20240615143000|P|75000|SGD|||||SURG001^Laparoscopic Cholecystectomy^TOSP|||CON0067^Dr Venkatesh^Arun^^^Dr^^^SAP_ISH|5A^502^B^SGH|S8556412J^^^NRIC^SG|||||||||||||20240612
FT1|2|20240615|20240615143000|20240615143000|P|2500|SGD|||||WARD001^Class B2 Ward Charges^SGHFEE|||CON0067^Dr Venkatesh^Arun^^^Dr^^^SAP_ISH|5A^502^B^SGH|S8556412J^^^NRIC^SG|||||||||||||20240610
FT1|3|20240615|20240615143000|20240615143000|P|850|SGD|||||ANES001^General Anaesthesia^TOSP|||CON0089^Dr Soh^Lay Tin^^^Dr^^^SAP_ISH|5A^502^B^SGH|S8556412J^^^NRIC^SG|||||||||||||20240612
```

---

## 11. DFT^P03 - Post detail financial transaction (outpatient consultation)

```
MSH|^~\&|SAP_ISH|NTFGH^Ng Teng Fong General Hospital|BILLING|NTFGH_FIN|20240722101500||DFT^P03^DFT_P03|NTFGH2024072210150001|P|2.4|||AL|AL|SGP
EVN|P03|20240722101500
PID|1||S9167503K^^^NRIC^SG~NTFGH0023456^^^NTFGH^MR||Sim^Hui Fang||19910430|F|||Blk 456 Jurong West Street 42 #03-210^^Singapore^^640456^SG||+6598907612^PRN^PH|||S|||S9167503K|||||||SG||||N
PV1|1|O|OPD5^CLINIC^C^NTFGH^^^^N|||||||ENT||||3|||CON0102^Dr Abdullah^Farhan^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240722093000
FT1|1|20240722|20240722101500|20240722101500|P|12000|SGD|||||CONS001^Specialist Consultation^NTFGHFEE|||CON0102^Dr Abdullah^Farhan^^^Dr^^^SAP_ISH|OPD5^CLINIC^C^NTFGH|S9167503K^^^NRIC^SG|||||||||||||20240722
FT1|2|20240722|20240722101500|20240722101500|P|3500|SGD|||||PROC001^Nasal Endoscopy^TOSP|||CON0102^Dr Abdullah^Farhan^^^Dr^^^SAP_ISH|OPD5^CLINIC^C^NTFGH|S9167503K^^^NRIC^SG|||||||||||||20240722
```

---

## 12. BAR^P01 - Add patient account (billing account creation)

```
MSH|^~\&|SAP_ISH|TTSH^Tan Tock Seng Hospital|BILLING|TTSH_FIN|20240305091000||BAR^P01^BAR_P01|TTSH2024030509100001|P|2.4|||AL|AL|SGP
EVN|P01|20240305091000
PID|1||S7678530L^^^NRIC^SG~TTSH0087654^^^TTSH^MR||Yusof^Danial Hakim||19760829|M|||12 Novena Rise #05-01^^Singapore^^307438^SG||+6581127890^PRN^PH|||M|||S7678530L|||||||SG||||N
PV1|1|I|9B^905^A^TTSH^^^^N|||||||NEURO||||1|||CON0044^Dr Sng^Hwee Boon^^^Dr^^^SAP_ISH||||||||||||||||||||20240305080000
IN1|1|MEDISAVE^Medisave||CPF Board^1 Jurong East Street 21^^Singapore^^609546^SG|||||||||20240101|20251231|||F|Yusof^Danial Hakim|Self|19760829|12 Novena Rise #05-01^^Singapore^^307438^SG
IN1|2|MEDISHIELD^Medishield Life||CPF Board^1 Jurong East Street 21^^Singapore^^609546^SG|||||||||20240101|20251231|||F|Yusof^Danial Hakim|Self|19760829|12 Novena Rise #05-01^^Singapore^^307438^SG
```

---

## 13. BAR^P05 - Update patient account (billing update with subsidy)

```
MSH|^~\&|SAP_ISH|CGH^Changi General Hospital|BILLING|CGH_FIN|20240418153000||BAR^P05^BAR_P05|CGH2024041815300001|P|2.5|||AL|AL|SGP
EVN|P05|20240418153000
PID|1||S6589704M^^^NRIC^SG~CGH0034567^^^CGH^MR||Ho^Geok Tin||19650415|F|||Blk 678 Tampines Street 61 #02-543^^Singapore^^520678^SG||+6584329017^PRN^PH|||W|||S6589704M|||||||SG||||N
PV1|1|I|6C^610^C^CGH^^^^N|||||||MED||||1|||CON0076^Dr Pillai^Ramesh^^^Dr^^^SAP_ISH||||||||||||||||||||20240415090000
IN1|1|MEDIFUND^Medifund||Ministry of Health|16 College Road^^Singapore^^169854^SG|||||||||20240101|20241231|||F|Ho^Geok Tin|Self|19650415|Blk 678 Tampines Street 61 #02-543^^Singapore^^520678^SG
IN1|2|CHAS_BLUE^CHAS Blue||Ministry of Health|16 College Road^^Singapore^^169854^SG|||||||||20240101|20251231|||F|Ho^Geok Tin|Self|19650415|Blk 678 Tampines Street 61 #02-543^^Singapore^^520678^SG
```

---

## 14. ORM^O01 - Laboratory order (blood test)

```
MSH|^~\&|SAP_ISH|NUH^National University Hospital|LIS|NUH_LAB|20240508140000||ORM^O01^ORM_O01|NUH2024050814000001|P|2.4|||AL|AL|SGP
PID|1||S8278635N^^^NRIC^SG~NUH0056789^^^NUH^MR||Kwan^Poh Geok||19820715|F|||Blk 901 Bukit Batok West Ave 2 #10-234^^Singapore^^650901^SG||+6597608142^PRN^PH|||S|||S8278635N|||||||SG||||N
PV1|1|I|4A^410^B^NUH^^^^N|||||||MED||||1|||CON0088^Dr Rajagopal^Vivek^^^Dr^^^SAP_ISH||||||||||||||||||||20240507120000
ORC|NW|ORD20240508001^SAP_ISH|||||^^^20240508140000^^R||20240508140000|NURSE012^Aminah^Binte Rashid|||||||NUH^National University Hospital
OBR|1|ORD20240508001^SAP_ISH||CBC^Complete Blood Count^NUHLAB|||20240508140000|||||||||CON0088^Dr Rajagopal^Vivek^^^Dr^^^SAP_ISH||||||20240508|||F
OBR|2|ORD20240508001^SAP_ISH||RENAL^Renal Panel^NUHLAB|||20240508140000|||||||||CON0088^Dr Rajagopal^Vivek^^^Dr^^^SAP_ISH||||||20240508|||F
OBR|3|ORD20240508001^SAP_ISH||LFT^Liver Function Test^NUHLAB|||20240508140000|||||||||CON0088^Dr Rajagopal^Vivek^^^Dr^^^SAP_ISH||||||20240508|||F
```

---

## 15. ORM^O01 - Radiology order (CT scan)

```
MSH|^~\&|SAP_ISH|SKH^Sengkang General Hospital|RIS|SKH_RAD|20240619093000||ORM^O01^ORM_O01|SKH2024061909300001|P|2.4|||AL|AL|SGP
PID|1||S7389650P^^^NRIC^SG~SKH0021098^^^SKH^MR||Ang^Teck Soon||19730220|M|||38 Sengkang Square #15-432^^Singapore^^545038^SG||+6582309471^PRN^PH|||M|||S7389650P|||||||SG||||N
PV1|1|E|ED^RESUS^A^SKH^^^^N|||||||EMED||||5|||CON0055^Dr Chan^Mei Xuan^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240619090000
ORC|NW|ORD20240619001^SAP_ISH|||||^^^20240619093000^^S||20240619093000|DOC001^Dr Chan^Mei Xuan|||||||SKH^Sengkang General Hospital
OBR|1|ORD20240619001^SAP_ISH||CTABD^CT Abdomen Pelvis with Contrast^SKHRAD|||20240619093000|||||||||CON0055^Dr Chan^Mei Xuan^^^Dr^^^SAP_ISH|||||||20240619|||F|||||||^Acute abdominal pain, query appendicitis
```

---

## 16. ADT^A01 - Patient admission with billing summary PDF attachment

```
MSH|^~\&|ISH_ADT|SGH^Singapore General Hospital|NEHR|MOH_SG|20240912101000||ADT^A01^ADT_A01|SGH2024091210100001|P|2.5|||AL|AL|SGP
EVN|A01|20240912101000|||ADMITCLERK07^Syafiqah^Binte Jalil
PID|1||S8490751Q^^^NRIC^SG~SGH0078901^^^SGH^MR||Pang^Wai Kit||19840603|M|||Blk 456 Clementi Ave 3 #09-876^^Singapore^^120456^SG||+6590871234^PRN^PH|||M|||S8490751Q|||||||SG||||N
PV1|1|I|10A^1005^A^SGH^^^^N|||||||CARDIO||||1|||CON0033^Dr Liew^Peng Huat^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240912101000
PV2|||^Unstable Angina|||||||5||||||||||||N
NK1|1|Pang^Siew Eng||+6593210478^PRN^PH||||||Spouse
IN1|1|INTEGRATED_SHIELD^AIA HealthShield Gold Max||AIA Singapore|1 Robinson Road #13-00^^Singapore^^048542^SG|||||||||20240101|20241231|||F|Pang^Wai Kit|Self|19840603|Blk 456 Clementi Ave 3 #09-876^^Singapore^^120456^SG
OBX|1|ED|PDF^Billing Summary^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 17. ADT^A03 - Patient discharge with discharge summary PDF

```
MSH|^~\&|ISH_ADT|TTSH^Tan Tock Seng Hospital|NEHR|MOH_SG|20240828160000||ADT^A03^ADT_A03|TTSH2024082816000001|P|2.5|||AL|AL|SGP
EVN|A03|20240828160000|||DISCCLERK08^Liang^Mei Fen
PID|1||S7601482R^^^NRIC^SG~TTSH0054321^^^TTSH^MR||Dzulkarnain^Irfan||19760315|M|||Blk 123 Yishun Ring Road #08-456^^Singapore^^760123^SG||+6589076512^PRN^PH|||M|||S7601482R|||||||SG||||N
PV1|1|I|5B^512^B^TTSH^^^^N|||||||RESP||||1|||CON0099^Dr Ganesan^Sridhar^^^Dr^^^SAP_ISH||||||||||||||||||||20240820090000||||||||20240828160000
PV2|||^Community-acquired Pneumonia|||||||8||||||||||||N
DG1|1|I10|J18.9^Pneumonia, unspecified organism^I10||20240820|A
OBX|1|ED|PDF^Discharge Summary^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
OBX|2|TX|NOTE^Clinical Notes^LN||Patient recovered well post antibiotics. Follow up in 2 weeks at respiratory clinic.||||||F
```

---

## 18. ORM^O01 - Pharmacy order (medication)

```
MSH|^~\&|SAP_HEALTHCARE|KTPH^Khoo Teck Puat Hospital|PHARMA|KTPH_RX|20240704112000||ORM^O01^ORM_O01|KTPH2024070411200001|P|2.4|||AL|AL|SGP
PID|1||S8812093S^^^NRIC^SG~KTPH0045678^^^KTPH^MR||Mohamad^Rizwan Syahmi||19880225|M|||Blk 567 Admiralty Drive #12-098^^Singapore^^750567^SG||+6596783410^PRN^PH|||M|||S8812093S|||||||SG||||N
PV1|1|I|3C^308^A^KTPH^^^^N|||||||MED||||1|||CON0065^Dr Khoo^Swee Leng^^^Dr^^^SAP_ISH||||||||||||||||||||20240702090000
ORC|NW|ORD20240704001^SAP_HEALTHCARE|||||^^^20240704112000^^R||20240704112000|DOC002^Dr Khoo^Swee Leng|||||||KTPH^Khoo Teck Puat Hospital
OBR|1|ORD20240704001^SAP_HEALTHCARE||RXORD^Pharmacy Order^KTPHRX|||20240704112000|||||||||CON0065^Dr Khoo^Swee Leng^^^Dr^^^SAP_ISH||||||20240704|||F
RXO|AMOX500^Amoxicillin 500mg Cap^KTPHRX||500|mg|CAP^Capsule^KTPHRX||^^^20240704^^TID|||30|CAP^Capsule^KTPHRX||||1
RXO|OMEP20^Omeprazole 20mg Cap^KTPHRX||20|mg|CAP^Capsule^KTPHRX||^^^20240704^^BD|||14|CAP^Capsule^KTPHRX||||2
```

---

## 19. ADT^A31 - Update person information (NRIC/address change)

```
MSH|^~\&|SAP_ISH|AH^Alexandra Hospital|NEHR|MOH_SG|20241015142000||ADT^A31^ADT_A31|AH2024101514200001|P|2.5|||AL|AL|SGP
EVN|A31|20241015142000|||MPIUPD02^Neo^Ai Ling
PID|1||S6712097T^^^NRIC^SG~AH0009876^^^AH^MR||Maniam^Karthik||19670820|M|||Blk 234 Queenstown Avenue #04-567^^Singapore^^149234^SG||+6581230794^PRN^PH~+6564501287^WPN^PH|||M|||S6712097T|||||||SG||||N
PD1||||CON0021^Dr Goh^Teck Seng^^^Dr^^^SAP_ISH
NK1|1|Maniam^Revathi||+6590128347^PRN^PH||||||Wife
NK1|2|Maniam^Arjun||+6598760213^PRN^PH||||||Son
```

---

## 20. DFT^P03 - Post detail financial transaction (emergency department with Medisave claim)

```
MSH|^~\&|SAP_ISH|NUH^National University Hospital|BILLING|NUH_FIN|20240930220000||DFT^P03^DFT_P03|NUH2024093022000001|P|2.4|||AL|AL|SGP
EVN|P03|20240930220000
PID|1||S9301578U^^^NRIC^SG~NUH0089012^^^NUH^MR||Gwee^Shu Ting||19930408|F|||15 Kent Ridge Crescent #07-210^^Singapore^^119276^SG||+6594503817^PRN^PH|||S|||S9301578U|||||||SG||||N
PV1|1|E|ED^MAJOR^B^NUH^^^^N|||||||EMED||||5|||CON0101^Dr Fernandez^Adrian Joseph^^^Dr^^^SAP_ISH||||||||||||||||||||||||20240930193000
FT1|1|20240930|20240930220000|20240930220000|P|25000|SGD|||||EDATT001^Emergency Attendance Fee^NUHFEE|||CON0101^Dr Fernandez^Adrian Joseph^^^Dr^^^SAP_ISH|ED^MAJOR^B^NUH|S9301578U^^^NRIC^SG|||||||||||||20240930
FT1|2|20240930|20240930220000|20240930220000|P|15000|SGD|||||PROC002^Wound Suturing^TOSP|||CON0101^Dr Fernandez^Adrian Joseph^^^Dr^^^SAP_ISH|ED^MAJOR^B^NUH|S9301578U^^^NRIC^SG|||||||||||||20240930
FT1|3|20240930|20240930220000|20240930220000|P|8500|SGD|||||XRAY001^X-Ray Left Wrist^NUHRAD|||CON0101^Dr Fernandez^Adrian Joseph^^^Dr^^^SAP_ISH|ED^MAJOR^B^NUH|S9301578U^^^NRIC^SG|||||||||||||20240930
IN1|1|MEDISAVE^Medisave||CPF Board^1 Jurong East Street 21^^Singapore^^609546^SG|||||||||20240101|20251231|||F|Gwee^Shu Ting|Self|19930408|15 Kent Ridge Crescent #07-210^^Singapore^^119276^SG
```
