# Rhapsody - real HL7v2 ER7 messages

## 1. ADT^A01 - patient admit to ICU (Rhapsody integration engine)

```
MSH|^~\&|EPIC|UMCU|LAB_SYS|PATHOLOGY|202603011430||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||AL|NE
EVN|A01|202603011430|||ADMIN^Wolters^Femke^^^RN
PID|1||MRN12345^^^UMCU^MR||Bakker^Daan^Willem||19800115|M||2106-3^White^HL70005|Oudegracht 42^^Utrecht^^3511AR^NL||^PRN^PH^^^^^030-2514789||NLD^Dutch^HL70296|S^Single^HL70002||ACCT98765^^^UMCU^AN
PV1|1|I|ICU^0101^01^UMCU^^^^NURS|E^Emergency^HL70007|||ATT1234^Meijer^Johanna^^^MD|REF5678^Timmerman^Adriaan^^^MD||MED^Medical^HL70069||||7|||ATT1234^Meijer^Johanna^^^MD|IP^Inpatient^HL70004||||||||||||||||||UMCU||A|||202603011415
NK1|1|Bakker^Lotte^A|SPO^Spouse^HL70063|Oudegracht 42^^Utrecht^^3511AR^NL|^PRN^PH^^^^^030-2514790
IN1|1|ZK001^Zilveren Kruis|ZK|Postbus 444^^Leiden^^2300AK^NL|^WPN^PH^^^^^071-5249000||GRP54321|||||||20230101|20261231||SELF^Self^HL70063|Bakker^Daan^Willem|SELF|19800115
AL1|1|DA^Drug Allergy^HL70127|PCN^Penicillin^HL70127|SV^Severe^HL70128|Anaphylaxis
```

---

## 2. ORU^R01 - comprehensive metabolic panel result (Rhapsody integration engine)

```
MSH|^~\&|LAB_SYS|UMCU|EPIC|UMCU|202603011630||ORU^R01^ORU_R01|LAB00042|P|2.5.1|||AL|NE
PID|1||MRN12345^^^UMCU^MR||Bakker^Daan^Willem||19800115|M
PV1|1|I|ICU^0101^01^UMCU
ORC|RE|ORD5678^EPIC|FIL9012^LAB_SYS||CM
OBR|1|ORD5678^EPIC|FIL9012^LAB_SYS|24323-8^CMP^LN|||202603011445|||||||ATT1234^Meijer^Johanna^^^MD||||||202603011615||LAB|F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.6-1.2|N|||F
OBX|3|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F
OBX|4|NM|2951-2^Sodium^LN||140|mEq/L|136-145|N|||F
OBX|5|NM|2823-3^Potassium^LN||4.2|mEq/L|3.5-5.0|N|||F
OBX|6|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F
OBX|7|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F
```

---

## 3. ORM^O01 - STAT CBC order (Rhapsody integration engine)

```
MSH|^~\&|EPIC|UMCU|LAB_SYS|PATHOLOGY|202603011400||ORM^O01^ORM_O01|ORD00123|P|2.5.1|||AL|NE
PID|1||MRN12345^^^UMCU^MR||Bakker^Daan^Willem||19800115|M
PV1|1|I|ICU^0101^01^UMCU||||ATT1234^Meijer^Johanna^^^MD
ORC|NW|ORD5678^EPIC||GRP001^EPIC|||||202603011400|||ATT1234^Meijer^Johanna^^^MD
OBR|1|ORD5678^EPIC||58410-2^CBC with Diff^LN|||202603011400|||||||||ATT1234^Meijer^Johanna^^^MD|||||||||||^STAT
DG1|1||R50.9^Fever, unspecified^I10
NTE|1||Patient febrile x 24hrs, rule out infection.
```

---

## 4. ORM^O01 - urinalysis order (Rhapsody documentation)

```
MSH|^~\&|HIS|Radboudumc|LIS|Radboudumc|20060307110114||ORM^O01|MSGID20060307110114|P|2.3
PID|||12001||de Vries^Pieter^^^dhr.||19670824|M|||Plompetorengracht 8^^Utrecht^^3512CA^NL
PV1||O|OP^PAREG^||||2342^Brouwer^Geert|||OP|||||||||2|||||||||||||||||||||||||20060307110111|
ORC|NW|20060307110114
OBR|1|20060307110114||003038^Urinalysis^L|||20060307110114
```

---

## 5. SIU^S12 - new appointment (Rhapsody integration engine)

```
MSH|^~\&|SCHED_SYS|UMCU|EPIC|UMCU|202603051000||SIU^S12^SIU_S12|SCH00456|P|2.5.1|||AL|NE
SCH|APT78901^SCHED_SYS|APT78901^EPIC|||||ROUTINE^Routine^HL70277|OFFICE^Office Visit^LOCAL|30|MIN|^^30^202603101400^202603101430|||||ATT1234^Meijer^Johanna^^^MD|^WPN^PH^^^^^030-2345678|MAIN_CLINIC^UMCU||Booked
PID|1||MRN12345^^^UMCU^MR||Bakker^Daan^Willem||19800115|M
PV1|1|O|MAIN_CLINIC^EXAM3^01^UMCU||||ATT1234^Meijer^Johanna^^^MD
RGS|1|A
AIS|1|A|OFFICE_VISIT^Office Visit^LOCAL|||202603101400|0|MIN|30|MIN
AIP|1|A|ATT1234^Meijer^Johanna^^^MD|ATT^Attending^HL70443
AIL|1|A|MAIN_CLINIC^EXAM3^01^UMCU||202603101400|0|MIN|30|MIN
```

---

## 6. MDM^T02 - operative note document notification (Rhapsody integration engine)

```
MSH|^~\&|TRANS_SYS|UMCU|EPIC|UMCU|202603021000||MDM^T02^MDM_T02|DOC00321|P|2.5.1|||AL|NE
EVN|T02|202603021000
PID|1||MRN12345^^^UMCU^MR||Bakker^Daan^Willem||19800115|M
PV1|1|I|SURG^OR3^01^UMCU||||SUR5678^Visser^Hendrik^^^MD
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||202603011600|||||SUR5678^Visser^Hendrik^^^MD||||DOC54321||AU^Authenticated^HL70271||202603021000
OBX|1|TX|OP_NOTE^Operative Note^LOCAL||Procedure: Laparoscopic cholecystectomy\.br\Patient tolerated procedure well\.br\No complications\.br\EBL: 50mL\.br\Specimens sent to pathology.||||||F
```

---

## 7. ORU^R01 - Dutch lab results with BSN via Rhapsody (HL7 Nederland format)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~283716495^^^NLMINBIZA^NNNLD||van den Berg&&van den Berg&&^Cornelia^^^^^L~van den Berg&&van den Berg^Cornelia^^^^^B||19500101|F|||Herengracht 88&Herengracht&88^^Amsterdam^^1015BS^NL^M~Herengracht 88&Herengracht&88^^Amsterdam^^1015BS^NL^L||020-6234891^PRN^PH~^^^cornelia@voorbeeld.nl|||M|||||||Amsterdam|Y|2||||""|N|N|||||||
OBX|1|ST|882-1^ABO+Rh group||O pos||||||F
PV1|1|I|0RGC2||||
OBR|1|123|20050701015070^Labosys||||200507010907||||||""|||3004^Timmerman||||200507010907||201708220955||S|F||^^^^^R
OBX|1|ST|266^Bezinking^L^BSE||2|mm/uur|0 - 15|""|||F
OBX|2|ST|325^Leucocyten^L^LEU||6.7|/nl|4.0 - 10.0|""|||F
OBX|3|ST|323^Hemoglobine^L^HB||10.2|mmol/l|8.5 - 11.0|""|||F
OBX|4|ST|324^Hematocriet^L^HT||0.48|l/l|0.41 - 0.51|""|||F
OBX|5|ST|326^Ery's^L^ERY||5.2|/pl|4.4 - 5.8|""|||F
OBX|6|ST|328^MCV^L^MCV1||92|fl|80 - 100|""|||F
OBX|7|ST|329^MCH^L^MCH||1.97|fmol|1.60 - 2.10|""|||F
OBX|8|ST|330^MCHC^L^MCHC||21.3|mmol/l|19.0 - 23.0|""|||F
OBX|9|ST|648^Ureum^L^UR||3.9|mmol/l|2.5 - 7.5|""|||F
OBX|10|ST|630^Kreatinine^L^KR||99|umol/l|70 - 110|""|||F
OBX|11|ST|638^Natrium^L^NA||139|mmol/l|135 - 145|""|||F
OBX|12|ST|628^Kalium^L^K||3.9|mmol/l|3.5 - 5.0|""|||F
OBX|13|ST|2325^Alk.fosf.^L^AF||52|U/l|0 - 120|""|||F
OBX|14|ST|2326^Gamma GT^L^GGT||29|U/l| - 50|""|||F
OBX|15|ST|2327^ASAT^L^ASAT||19|U/l|0 - 40|""|||F
OBX|16|ST|2328^ALAT^L^ALAT||20|U/l|0 - 45|""|||F
OBX|17|ST|614^Glucose^L^GLUS||10.3|mmol/l|4.0 - 7.8|H|||F
OBX|18|ST|34^TSH^L^TSH||0.78|mU/l|0.4 - 4.0|""|||F
```

---

## 8. ADT^A01 - patient admit with insurance (Rhapsody HL7 v2.8.2 base standard)

```
MSH|^~\&|REGADT|AMC|IFENG||199112311501||ADT^A01^ADT_A01|000001|P|2.8.2
EVN|A01|199112310500
PID|||191919^^^AMC^MR~194826537^^^NLMINBIZA^NNNLD||Jansen^Willem^G||19610615|M|||Vondelstraat 12^^Amsterdam^^1054GE^NL||(020)6823456|||S||100-01|||||||||||N
NK1|1|Jansen^Theodora^M|WI^Wife||||||NK^Next of Kin
PV1||I|W^389^1^AMC|3|||0148^Dekker^Margaretha^^^MD|REF5678^Bos^Jacobus^^^MD||SUR||||ADM|A0
IN1|1|1|137HM|VGZ|Postbus 5040^^Arnhem^^6802EA^NL||||||||||Jansen^Willem^G|19610615|Vondelstraat 12^^Amsterdam^^1054GE^NL|||||||||||||||||194826537
```

---

## 9. ADT^A04 - outpatient registration (Rhapsody HL7 v2.5 format)

```
MSH|^~\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|200504301430||ADT^A04^ADT_A04|MSG000100|P|2.5
EVN|A04|200504301430
PID|||12345^^^VUMC^MR||Smit^Thijs^B||19750101|M|||Amstelveenseweg 200^^Amsterdam^^1075XR^NL||020-3051234||S|||347291856
PV1||O|CLINIC^ROOM1^BED1|R|||9876^van Dijk^Elisabeth^^^MD
```

---

## 10. ADT^A08 - patient information update (Rhapsody format)

```
MSH|^~\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|200504301535||ADT^A08^ADT_A08|MSG000101|P|2.5
EVN|A08|200504301535
PID|||12345^^^VUMC^MR||Smit^Thijs^B||19750101|M|||Leidsestraat 55^^Amsterdam^^1017NX^NL||020-3059876||S|||347291856
PV1||O|CLINIC^ROOM1^BED1||||9876^van Dijk^Elisabeth^^^MD
```

---

## 11. ADT^A34 - merge patients by patient ID (Rhapsody)

```
MSH|^~\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|200504301545||ADT^A34^ADT_A34|MSG000102|P|2.5
EVN|A34|200504301545
PID|||12345^^^VUMC^MR||Smit^Thijs^B||19750101|M
MRG|67890^^^VUMC^MR
```

---

## 12. ORU^R01 - multi-OBR lab result (Rhapsody integration)

```
MSH|^~\&|LAB|LUMC|EMR|LUMC|200905151340||ORU^R01^ORU_R01|MSG00002|P|2.5.1
PID|1||P500001^^^LUMC^MR||de Jong^Saskia^W||19690220|F
PV1|1|O|OUTPT^CLINIC5^01
ORC|RE|ORD100^EMR|FILL200^LAB||CM
OBR|1|ORD100^EMR|FILL200^LAB|57021-8^CBC W Differential^LN|||200905150800|||||||1234^Wolters^Geert^^^MD||||||200905151330||LAB|F
OBX|1|NM|6690-2^WBC^LN||7.8|10*3/uL|4.5-11.0|N|||F
OBX|2|NM|789-8^RBC^LN||4.65|10*6/uL|4.00-5.50|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||14.2|g/dL|12.0-16.0|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||42.1|%|36.0-46.0|N|||F
OBX|5|NM|787-2^MCV^LN||90.5|fL|80.0-100.0|N|||F
OBX|6|NM|785-6^MCH^LN||30.5|pg|27.0-33.0|N|||F
OBX|7|NM|786-4^MCHC^LN||33.7|g/dL|32.0-36.0|N|||F
OBX|8|NM|777-3^Platelets^LN||245|10*3/uL|150-400|N|||F
```

---

## 13. DFT^P03 - financial charge transaction (Rhapsody)

```
MSH|^~\&|HIS|Erasmus MC|BILLING|Erasmus MC|200603011400||DFT^P03|DFT000001|P|2.5
EVN|P03|200603011400
PID|||12345^^^Erasmus MC^MR||Mulder^Bram^H||19700515|M
PV1||I|ICU^101^1||||1234^de Groot^Anneke^^^MD
FT1|1|CRG001||200603011400|200603011400|CG|99213^Office Visit Level 3^CPT4|||1||||||||||||||||||99213
```

---

## 14. MFN^M02 - provider master file notification (Rhapsody)

```
MSH|^~\&|STAFFSYS|Radboudumc|RECVSYS|Radboudumc|200603011400||MFN^M02|MFN000001|P|2.5
MFI|PRA^Practitioner Master File^HL70175||UPD|||AL
MFE|MAD|1234^Brouwer^Floor^^^MD||CWE|PL
STF|1234|P111^Brouwer^Floor^K^^MD||Brouwer^Floor^K||F|19600101|A|MD|29384756^NPI^NPI||^WPN^PH^^31^30^2345678|Domplein 1^^Utrecht^^3512JC^NL|20000101
PRA|1234||Radboudumc|Y||MED^Medicine
```

---

## 15. ADT^A05 - pre-admit patient (Rhapsody)

```
MSH|^~\&|ADMITSYS|MUMC+|RECSYS|MUMC+|200605301500||ADT^A05^ADT_A05|PREADMIT01|P|2.5
EVN|A05|200605301500
PID|||98765^^^MUMC+^MR||Dekker^Maria^J||19820312|F|||Tongersestraat 25^^Maastricht^^6211LL^NL||043-3214567||M|||518273946
PV1||I|SURG^201^1||||5678^Verhoeven^Adriaan^^^MD
NK1|1|Dekker^Jan^P|SPO^Spouse|Tongersestraat 25^^Maastricht^^6211LL^NL|043-3214568
```

---

## 16. ADT^A28 - add person information (Rhapsody)

```
MSH|^~\&|ADTSYS|OLVG|MASTER|OLVG|200607150900||ADT^A28^ADT_A28|ADDPAT01|P|2.5
EVN|A28|200607150900
PID|||54321^^^OLVG^MR||van der Meer^Hendrik^F||19900723|M|||Prinsengracht 150^^Amsterdam^^1016GV^NL||020-7774321||S|||625183947
```

---

## 17. RDE^O01 - pharmacy order (Rhapsody)

```
MSH|^~\&|CPOE|Erasmus MC|RX|PHARMACY|200605011200||RDE^O01^RDE_O01|RDE00001|P|2.5
PID|||12345^^^Erasmus MC^MR||Mulder^Bram^H||19700515|M
PV1||I|ICU^101^1||||1234^de Groot^Anneke^^^MD
ORC|NW|RX001^CPOE||GRP001^CPOE|||||200605011200|||1234^de Groot^Anneke^^^MD
RXE|1^BID&&HL70335^20060501^20060515||5111-1^Amoxicillin 500mg^NDC|500||mg|CAP|1||||10||||||||||||||||||||||||||||||||||
RXR|PO^Oral^HL70162
```

---

## 18. ORU^R01 with embedded PDF report (Rhapsody document transmission)

```
MSH|^~\&|RIS|RHAPSODY|EMR|LUMC|20230915141200||ORU^R01^ORU_R01|RIS20230915001|P|2.5.1|||AL|NE
PID|1||PAT44556^^^LUMC^MR~461829375^^^NLMINBIZA^NNNLD||Visser^Femke^M||19650310|F|||Rapenburg 70^^Leiden^^2311EZ^NL^H||071-5278901
PV1|1|O|RAD^ROOM2^01^LUMC||||RAD001^Hoekstra^Willem^^^MD
ORC|RE|ORD8899^EMR|FIL3344^RIS||CM
OBR|1|ORD8899^EMR|FIL3344^RIS|71020^Chest X-ray^CPT|||20230915100000|||||||RAD001^Hoekstra^Willem^^^MD||||||20230915140000||RAD|F
OBX|1|TX|71020^Chest X-ray^CPT||Heart and lungs within normal limits. No acute findings.||||||F
OBX|2|ED|PDF^Radiology Report^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhZGlvbG9naWUgUmFwcG9ydCkKL0NyZWF0b3IgKFJoYXBzb2R5IEludGVncmF0aW9uIEVuZ2luZSkKL1Byb2R1Y2VyIChSaGFwc29keSBQREYgR2VuZXJhdG9yKQovQ3JlYXRpb25EYXRlIChEOjIwMjMwOTE1MTQxMjAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooTm9ybWFhbCB0aG9yYXggcm9udGdlbikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAxNTggMDAwMDAgbiAKMDAwMDAwMDIwNyAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA0OTkgMDAwMDAgbiAKMDAwMDAwMDU5MyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjY3MQolJUVPRgo=||||||F
```

---

## 19. ORU^R01 with embedded DICOM/JPEG image (Rhapsody imaging integration)

```
MSH|^~\&|PACS|RHAPSODY|EMR|Erasmus MC|20231020090000||ORU^R01^ORU_R01|PACS20231020001|P|2.5.1|||AL|NE
PID|1||PAT77889^^^Erasmus MC^MR~738291456^^^NLMINBIZA^NNNLD||Bos^Anneke^G||19780520|F|||Witte de Withstraat 30^^Rotterdam^^3012BR^NL^H||010-4367890
PV1|1|O|RAD^CT1^01^Erasmus MC||||RAD002^Mulder^Jacobus^^^MD
ORC|RE|ORD1122^EMR|FIL5566^PACS||CM
OBR|1|ORD1122^EMR|FIL5566^PACS|74177^CT Abdomen with contrast^CPT|||20231020080000|||||||RAD002^Mulder^Jacobus^^^MD||||||20231020085500||RAD|F
OBX|1|TX|74177^CT Abdomen^CPT||Liver, spleen, and kidneys appear normal. No masses or fluid collections identified.||||||F
OBX|2|ED|IMG^CT Key Image^LOCAL||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SFhSRTKTc/7EAaOCw==||||||F
```

---

## 20. MDM^T02 - Dutch discharge summary with embedded PDF (Rhapsody document workflow)

```
MSH|^~\&|EPD|RHAPSODY|ARCHIVE|Catharina|20231105160000||MDM^T02^MDM_T02|MDM20231105001|P|2.5.1|||AL|NE
EVN|T02|20231105160000
PID|1||PAT33221^^^Catharina^MR~592847163^^^NLMINBIZA^NNNLD||de Jong^Geert^W||19550815|M|||Michelangelolaan 2^^Eindhoven^^5623EJ^NL^H||040-2398765
PV1|1|I|CARD^301^1^Catharina||||INT001^van Beek^Margaretha^^^MD
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191||20231105150000|||||INT001^van Beek^Margaretha^^^MD||||DOC99887||AU^Authenticated^HL70271||20231105160000
OBX|1|TX|DS_NOTE^Discharge Summary^LOCAL||Patient was admitted for unstable angina. Underwent coronary angiography with stent placement. Discharged on aspirin, clopidogrel, atorvastatin.||||||F
OBX|2|ED|DS_PDF^Discharge Letter^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE9udHNsYWdicmllZikKL0NyZWF0b3IgKFJoYXBzb2R5IEludGVncmF0aW9uIEVuZ2luZSkKL1Byb2R1Y2VyIChSaGFwc29keSBQREYgR2VuZXJhdG9yKQovQ3JlYXRpb25EYXRlIChEOjIwMjMxMTA1MTYwMDAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooT250c2xhZ2JyaWVmIGthcmRpb2xvZ2llKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjYgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE1OCAwMDAwMCBuIAowMDAwMDAwMjA3IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQ5OSAwMDAwMCBuIAowMDAwMDAwNTkzIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKNjcxCiUlRU9GCg==||||||F
```
