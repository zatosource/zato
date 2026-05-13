# iPMS/iPM (iSoft/DXC) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission (Beaumont Hospital)

```
MSH|^~\&|iPMS|BEAUMONT|HEALTHLINK|HSE|20260112091500||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|AL||8859/1
EVN|A01|20260112091500|||C1782^Brennan^Fionnuala^^^Dr^^^IMC^PRSNL^^^ORGDR
PID|1||7381204^^^BEAUMONT^MRN~4219837TA^^^PPS^PPS~9000043671^^^IHI^IHI||GALLAGHER^SEÁN^EOGHAN^^^^L||19570423|M|||12 Clontarf Road^^Dublin 3^^D03 K7W2^IRL^H||+353 1 8334217^HOME|+353 87 6541238^MOBILE|en|M|||7381204^^^BEAUMONT^AN|4219837TA||||Dublin||||||N
NK1|1|GALLAGHER^SAOIRSE^^^^|SPO|12 Clontarf Road^^Dublin 3^^D03 K7W2^IRL|(+353)1-8334218||EC
PV1|1|I|SURG1^Bay3^Bed12^BEAUMONT^^BED^Main Building^4|E|||C1782^Brennan^Fionnuala^^^Dr^^^IMC|||SUR|||||||||V100891^^^BEAUMONT^VN||||||||||||||||||||||||||20260112091500
PV2||||||||||||Emergency laparoscopic cholecystectomy
AL1|1|DA|E9333^Penicillin^ICD10||Anaphylaxis
DG1|1||K80.0^Calculus of gallbladder with acute cholecystitis^ICD10||20260112|A
```

---

## 2. ADT^A03 - Discharge (St James's Hospital Dublin)

```
MSH|^~\&|iPMS|STJAMES|HEALTHLINK|HSE|20260215163200||ADT^A03^ADT_A03|MSG00045|P|2.4|||AL|AL||8859/1
EVN|A03|20260215163200|||C2914^Crowley^Aisling^^^Dr^^^IMC
PID|1||5293016^^^STJAMES^MRN~8317246WA^^^PPS^PPS||DOYLE^NIAMH^CAOIMHE^^^^L||19700919|F|||47 Aungier Street^^Dublin 2^^D02 T8R1^IRL^H||+353 1 4753892^HOME||en|S|||5293016^^^STJAMES^AN|8317246WA||||Dublin
PV1|1|I|MED2^Room8^Bed1^STJAMES^^BED^Main^3|R|||C2914^Crowley^Aisling^^^Dr^^^IMC|||MED|||||||||V200913^^^STJAMES^VN||||||||||||||||01^Discharged home^HL70112|||||||||||20260209100000|20260215163200
DG1|1||J18.9^Pneumonia unspecified organism^ICD10||20260209|A
DG1|2||J96.0^Acute respiratory failure^ICD10||20260209|A
PR1|1||96.71^Continuous positive airway pressure ventilation^ICD9CM|CPAP ventilation|20260210
```

---

## 3. ADT^A04 - Outpatient registration (Mater Misericordiae University Hospital)

```
MSH|^~\&|iPMS|MATER|HEALTHLINK|HSE|20260320103045||ADT^A04^ADT_A04|MSG00078|P|2.4|||AL|AL||8859/1
EVN|A04|20260320103045|||C3167^Nolan^Deirdre^^^Dr^^^IMC
PID|1||6139827^^^MATER^MRN~5274618GA^^^PPS^PPS||BYRNE^ORLA^ROISÍN^^^^L||19841105|F|||8 Phibsborough Road^^Dublin 7^^D07 P3N9^IRL^H||+353 1 8301467^HOME|+353 86 2198743^MOBILE|en|M|||6139827^^^MATER^AN|5274618GA||||Dublin||||||N
PV1|1|O|CARD-OPD^Clinic3^^MATER^^AMB^Outpatients^2|R|||C3167^Nolan^Deirdre^^^Dr^^^IMC|||CAR|||||||||V300246^^^MATER^VN||||||||||||||||||||||||||20260320103045
DG1|1||I25.1^Atherosclerotic heart disease^ICD10||20260320|W
```

---

## 4. ADT^A08 - Patient information update (Cork University Hospital)

```
MSH|^~\&|iPMS|CUH|HEALTHLINK|HSE|20260410141530||ADT^A08^ADT_A08|MSG00112|P|2.4|||AL|AL||8859/1
EVN|A08|20260410141530
PID|1||4817362^^^CUH^MRN~7193248HA^^^PPS^PPS~9000058214^^^IHI^IHI||MCCARTHY^CIARÁN^^^^^L|FITZGERALD^SORCHA^^^^|19730308|M|||23 Washington Street^^Cork^^T12 F4W6^IRL^H||+353 21 4397218^HOME|+353 85 7612349^MOBILE|en|M|||4817362^^^CUH^AN|7193248HA||||Cork
PV1|1|I|ORTH^Ward4^Bed7^CUH^^BED^Main^2|E|||C4523^Sullivan^Colm^^^Dr^^^IMC|||ORT|||||||||V400871^^^CUH^VN||||||||||||||||||||||||||20260405082000
```

---

## 5. ADT^A02 - Patient transfer (University Hospital Galway)

```
MSH|^~\&|iPMS|UHG|HEALTHLINK|HSE|20260518084500||ADT^A02^ADT_A02|MSG00156|P|2.4|||AL|AL||8859/1
EVN|A02|20260518084500|||C5634^Healy^Muireann^^^Dr^^^IMC
PID|1||2916483^^^UHG^MRN~6318472JA^^^PPS^PPS||WALSH^DIARMUID^CATHAL^^^^L||19500817|M|||9 Eyre Square^^Galway^^H91 W3K8^IRL^H||+353 91 487213^HOME||ga|M|||2916483^^^UHG^AN|6318472JA||||Galway
PV1|1|I|ICU^Bay1^Bed2^UHG^^BED^Main^1|U|||C5634^Healy^Muireann^^^Dr^^^IMC|||ICU|||||||||V500891^^^UHG^VN||||||||||||||||||||||||||20260518084500
PV2||||||||20260514||20260518||||||||||||||||||||||||AMB^Ambulance^HL70007
```

---

## 6. ADT^A28 - Patient identity feed (Connolly Hospital Blanchardstown)

```
MSH|^~\&|iPMS|CONNOLLY|NATIONAL_MPI|HSE|20260622150230||ADT^A28^ADT_A05|MSG00189|P|2.4|||AL|AL||8859/1
EVN|A28|20260622150230
PID|1||8392714^^^CONNOLLY^MRN~7416293KA^^^PPS^PPS~9000071836^^^IHI^IHI||QUINN^CLODAGH^AISLING^^^^L||19970614|F|||15 Main Street^^Blanchardstown^Dublin 15^D15 T4N7^IRL^H||+353 1 8209316^HOME|+353 87 3148927^MOBILE|en|S|||8392714^^^CONNOLLY^AN|7416293KA||||Dublin||||||N
PV1||N
```

---

## 7. ADT^A31 - Patient update with next-of-kin (Tallaght University Hospital)

```
MSH|^~\&|iPMS|TUH|HEALTHLINK|HSE|20260701112000||ADT^A31^ADT_A05|MSG00210|P|2.4|||AL|AL||8859/1
EVN|A31|20260701112000
PID|1||3614829^^^TUH^MRN~8291346LA^^^PPS^PPS||KAVANAGH^CONOR^^^^^L|DALY^^^^^^|19850709|M|||27 Old Bawn Road^^Tallaght^Dublin 24^D24 V2H7^IRL^H||+353 1 4627183^HOME|+353 86 9213748^MOBILE|en|M|||3614829^^^TUH^AN|8291346LA||||Dublin
NK1|1|KAVANAGH^GRÁINNE^^^^|SPO|27 Old Bawn Road^^Tallaght^Dublin 24^D24 V2H7^IRL|(+353)86-4193827||EC
NK1|2|KAVANAGH^PÁDRAIG^^^^|FTH|11 Templeogue Road^^Dublin 6W^^D06 A8C2^IRL|(+353)1-4928371||NK
PV1||N
```

---

## 8. ADT^A40 - Patient merge (University Hospital Limerick)

```
MSH|^~\&|iPMS|UHL|NATIONAL_MPI|HSE|20251003094500||ADT^A40^ADT_A39|MSG00234|P|2.4|||AL|AL||8859/1
EVN|A40|20251003094500
PID|1||6291834^^^UHL^MRN~9127384MA^^^PPS^PPS||MORAN^TADHG^^^^^L||19621103|M|||6 Henry Street^^Limerick^^V94 E9H3^IRL^H||+353 61 428937^HOME||en|M|||6291834^^^UHL^AN|9127384MA
MRG|6291835^^^UHL^MRN|
```

---

## 9. ORM^O01 - Radiology order (St Vincent's University Hospital)

```
MSH|^~\&|iPMS|SVUH|RIS|SVUH|20260115143000||ORM^O01|MSG00267|P|2.4|||AL|AL||8859/1
PID|1||9214837^^^SVUH^MRN~8193274NA^^^PPS^PPS||BRENNAN^OISÍN^^^^^L||19790818|M|||4 Merrion Road^^Dublin 4^^D04 W2K8^IRL^H||+353 1 2194837^HOME||en|M|||9214837^^^SVUH^AN|8193274NA
PV1|1|I|RESP^Ward6^Bed3^SVUH^^BED^Main^5|E|||C6823^O'Connor^Bríd^^^Dr^^^IMC|||RES|||||||||V600812^^^SVUH^VN||||||||||||||||||||||||||20260113100000
ORC|NW|ORD10501^iPMS||GRP20501^iPMS|||||20260115143000|||C6823^O'Connor^Bríd^^^Dr^^^IMC
OBR|1|ORD10501^iPMS||71020^Chest 2 Views^CPT4|||20260115||||||||C6823^O'Connor^Bríd^^^Dr^^^IMC||||||||||||||||||||||20260115143000
DG1|1||J18.9^Pneumonia unspecified^ICD10||20260113|A
```

---

## 10. ORM^O01 - Laboratory order (Beaumont Hospital)

```
MSH|^~\&|iPMS|BEAUMONT|LIS|BEAUMONT|20260205101500||ORM^O01|MSG00289|P|2.4|||AL|AL||8859/1
PID|1||3847162^^^BEAUMONT^MRN~6219348PA^^^PPS^PPS||DUNNE^AOIFE^^^^^L||19870126|F|||5 Collins Avenue^^Dublin 9^^D09 N3T7^IRL^H||+353 1 8472193^HOME||en|S|||3847162^^^BEAUMONT^AN|6219348PA
PV1|1|O|HAEM-OPD^Clinic1^^BEAUMONT^^AMB^Outpatients^1|R|||C7134^Buckley^Fiachra^^^Dr^^^IMC|||HAE|||||||||V700123^^^BEAUMONT^VN||||||||||||||||||||||||||20260205101500
ORC|NW|ORD20501^iPMS||GRP30501^iPMS|||||20260205101500|||C7134^Buckley^Fiachra^^^Dr^^^IMC
OBR|1|ORD20501^iPMS||58410-2^CBC panel^LN^FBC^Full Blood Count^L|||20260205||||||||C7134^Buckley^Fiachra^^^Dr^^^IMC
OBR|2|ORD20501^iPMS||24331-1^Lipid panel^LN^LIPID^Lipid Profile^L|||20260205||||||||C7134^Buckley^Fiachra^^^Dr^^^IMC
```

---

## 11. ORU^R01 - Discharge summary (Cerner MILL integration, VHI Carrickmines)

```
MSH|^~\&|P3048|MILL|VHI|VHI|20250830115123||ORU^R01|Q11506152T2599882||2.3||||||8859/1
PID|1|31742^^^MRN^MRN|31742^^^MRN^MRN||O'BRIEN^DECLAN^RUAIRÍ^^^^CURRENT|MURPHY^^^^^^|20020714|1|KELLY^^^^^^BIRTH||14 Stillorgan Road^Blackrock^Dublin^""^A94 D3F7^IRL^HOME^Co Dublin^Dublin|Dublin|(+353)1-2837461^HOME^""~^HOME^"^declan.obrien@mailbox.ie~(+353)87-4291638^Mobile^"|(+353)1-6382947^BUSINESS^""|12|S|""|204589^^^Encounter Num^FINNBR|5847291WA|||||""|0|""|""|""||""
NTE|1|CD:469|30/8/2025 11:32:49 AM Comment by: Kearney , Siobhán Cerner \.br\Encounter Comments\.br\--------------------------------------\.br\\.br\
PD1|""|""|^^0|^Kearney^Siobhán^^^^^^^PRSNL|""||""|""
PV1|1|OUTPATIENT|CM Wellness^^^Carrickmines^^AMB^360 Clinic|""|||PHY Ext ID^Whelan^Lorcan^^^^^^External Id^PRSNL^^^EXTID^""~999999^Whelan^Lorcan^^^^^^Irish Medical Council^PRSNL^^^ORGDR^""|999995^Doherty^Maeve^^^^^^Irish Medical Council^PRSNL^^^ORGDR^""||CAM Therapy Class|""|""|""|""|""|""||OUTPATIENT|26714^^^Attendance Num^VISITID|""||""||||||||||||||""|""|""|Carrickmines||ACTIVE|||20250830112812
ORC|RE||e67eefc6-3c4a-44a0-86ed-4546a9610aa7^HNAM_CEREF~2557927^HNAM_EVENTID||||||20250830115122|PHY Ext ID^Kearney^Siobhán^^^^^^^External Id^PRSNL^^^EXTID^""
OBR|1||e67eefc6-3c4a-44a0-86ed-4546a9610aa7^HNAM_CEREF~2557927^HNAM_EVENTID|CD:18150760^Key Discharge Checklist Forms^^^UTC Discharge Summary|||20250830114434|20250830114434||||||||||||||20250830115122||MDOC|AU|||||||PHY Ext ID&Kearney&Siobhán&&&&""&External Id&&EXTID||PHY Ext ID&Kearney&Siobhán&&&&""&External Id&&EXTID
ZDS|SIG|PHY Ext ID^Kearney^Siobhán^^^^^^^External Id^PRSNL^^^EXTID^""|20250830115122|COMP
ZDS|VER|PHY Ext ID^Kearney^Siobhán^^^^^^^External Id^PRSNL^^^EXTID^""|20250830115122|COMP
ZDS|AU|PHY Ext ID^Kearney^Siobhán^^^^^^^External Id^PRSNL^^^EXTID^""|Vhi 360 Carrickmines|COMP
OBX|1|FT|CD:18150760^Key Discharge Checklist Forms|| \.br\GP Practice\.br\ GP Practice information freetexted into the discharge summary\.br\ Patient and Visit Information\.br\ Patient Demographics\.br\ Name:O'BRIEN, DECLAN\.br\ Address:\.br\ 14 Stillorgan Road\.br\ Blackrock\.br\ Co Dublin\.br\ A94 D3F7\.br\ Gender:Male\.br\ Date of Birth:14/07/2002\.br\ Phone:+353 1 2837461\.br\ Emergency Contact:O'BRIEN, MAEVE\.br\ Telephone: \.br\ +353 87 4291638\.br\ NHS: \.br\ 5847291WA\.br\ Other Identifier (MRN): \.br\ 31742\.br\|""||""||""|AU|||20250830115122||PHY Ext ID^Kearney^Siobhán^^^^^^^External Id^PRSNL^^^EXTID^""
```

---

## 12. REF^I12 - GP referral (Cerner MILL integration, VHI Carrickmines)

```
MSH|^~\&|P3048|MILL|VHI|VHI|20250830115123||REF^I12|Q11506152T2599882||2.3
PRD|PP^Primary Care Provider|Kearney^Siobhán|||C
PID|1||31742^^^MRN^MRN||O'BRIEN^DECLAN^RUAIRÍ^^^^CURRENT||20020714|M|||14 Stillorgan Road^Blackrock^^IRL^A94 D3F7||(+353)1-2837461^HOME
PV1|1|O|MED^^^Carrickmines^^C^CM Wellness|||PHY Ext ID^Whelan^Lorcan|999995^Doherty^Maeve||||||||||||||||||||||||||||||||||20250830112812
NTE|1||GP Practice\.br\GP Practice information freetexted into the discharge summary\.br\Patient and Visit Information\.br\Patient Demographics\.br\Name:O'BRIEN, DECLAN\.br\Address:\.br\14 Stillorgan Road\.br\Blackrock\.br\Co Dublin\.br\A94 D3F7\.br\Gender:Male\.br\Date of Birth:14/07/2002
```

---

## 13. ADT^A01 - Emergency admission (University Hospital Waterford)

```
MSH|^~\&|iPMS|UHW|HEALTHLINK|HSE|20251205220130||ADT^A01^ADT_A01|MSG00312|P|2.4|||AL|AL||8859/1
EVN|A01|20251205220130|||C8234^Daly^Eoin^^^Dr^^^IMC
PID|1||7381926^^^UHW^MRN~2918374QA^^^PPS^PPS||RYAN^PÁDRAIG^^^^^L||19440518|M|||3 The Quay^^Waterford^^X91 H4K6^IRL^H||+353 51 392718^HOME||en|W|||7381926^^^UHW^AN|2918374QA||||Waterford||||||N
NK1|1|RYAN^BRÍD^^^^|SPO|3 The Quay^^Waterford^^X91 H4K6^IRL|(+353)51-392719||EC
PV1|1|E|ED^Majors^Bed4^UHW^^BED^ED Building^1|E|||C8234^Daly^Eoin^^^Dr^^^IMC|||EMR|||||||||V800234^^^UHW^VN||||||||||||||||||||||||||20251205220130
AL1|1|DA|Z88.0^Allergy status to penicillin^ICD10||Rash
DG1|1||I21.0^Acute transmural MI of anterior wall^ICD10||20251205|A
```

---

## 14. SIU^S12 - Appointment scheduling (Mater outpatient)

```
MSH|^~\&|iPMS|MATER|CLINICSYS|MATER|20260425090000||SIU^S12|MSG00345|P|2.4|||AL|AL||8859/1
SCH|1001^iPMS|||||CARD-OPD^Cardiology Outpatient^^^MATER|ROUTINE|30|MIN|^^30^20260515093000^20260515100000||C3167^Nolan^Deirdre^^^Dr^^^IMC||||||BOOKED
PID|1||6139827^^^MATER^MRN~5274618GA^^^PPS^PPS||BYRNE^ORLA^ROISÍN^^^^L||19841105|F|||8 Phibsborough Road^^Dublin 7^^D07 P3N9^IRL^H||+353 1 8301467^HOME|+353 86 2198743^MOBILE|en|M
PV1|1|O|CARD-OPD^Clinic3^^MATER^^AMB^Outpatients^2|R|||C3167^Nolan^Deirdre^^^Dr^^^IMC|||CAR
AIP|1||C3167^Nolan^Deirdre^^^Dr^^^IMC|
AIL|1||CARD-OPD^Clinic3^^MATER
```

---

## 15. ADT^A13 - Cancel discharge (Tallaght University Hospital)

```
MSH|^~\&|iPMS|TUH|HEALTHLINK|HSE|20260408143000||ADT^A13^ADT_A13|MSG00378|P|2.4|||AL|AL||8859/1
EVN|A13|20260408143000|||C9178^Fitzgerald^Darragh^^^Dr^^^IMC
PID|1||4918273^^^TUH^MRN~3147289RA^^^PPS^PPS||SULLIVAN^LORCAN^^^^^L||19610625|M|||22 Greenhills Road^^Dublin 12^^D12 K9N4^IRL^H||+353 1 4519273^HOME||en|M|||4918273^^^TUH^AN|3147289RA
PV1|1|I|MED1^Room12^Bed2^TUH^^BED^Main^4|R|||C9178^Fitzgerald^Darragh^^^Dr^^^IMC|||MED|||||||||V900345^^^TUH^VN||||||||||||||||||||||||||20260401100000
```

---

## 16. ADT^A34 - Merge patient identifier (Beaumont Hospital)

```
MSH|^~\&|iPMS|BEAUMONT|NATIONAL_MPI|HSE|20251220111500||ADT^A34^ADT_A30|MSG00401|P|2.4|||AL|AL||8859/1
EVN|A34|20251220111500
PID|1||5291837^^^BEAUMONT^MRN~6382914SA^^^PPS^PPS||NOLAN^SIOBHÁN^^^^^L||19930322|F|||17 Griffith Avenue^^Dublin 9^^D09 F2H8^IRL^H
MRG|5291838^^^BEAUMONT^MRN
```

---

## 17. ORU^R01 - Radiology report with embedded PDF (St James's Hospital)

```
MSH|^~\&|iPMS|STJAMES|GP_SYSTEM|HEALTHLINK|20260120161500||ORU^R01^ORU_R01|MSG00423|P|2.4|||AL|AL||8859/1
PID|1||5293016^^^STJAMES^MRN~8317246WA^^^PPS^PPS||DOYLE^NIAMH^CAOIMHE^^^^L||19700919|F|||47 Aungier Street^^Dublin 2^^D02 T8R1^IRL^H
PV1|1|O|RAD-OPD^^^STJAMES^^AMB|R|||C2914^Crowley^Aisling^^^Dr^^^IMC
ORC|RE|ORD30501^iPMS|RAD40501^RIS||CM||||20260120161500|||C2914^Crowley^Aisling^^^Dr^^^IMC
OBR|1|ORD30501^iPMS|RAD40501^RIS|71020^Chest 2 Views^CPT4|||20260119|||||||||C2914^Crowley^Aisling^^^Dr^^^IMC||||||20260120161500||RAD|F
OBX|1|FT|71020^Chest 2 Views^CPT4||PA and lateral chest radiograph.\.br\\.br\Heart size is normal. Lungs are clear bilaterally.\.br\No pleural effusion or pneumothorax.\.br\\.br\Impression: Normal chest radiograph.||||||F|||20260120
OBX|2|ED|PDF^Radiology Report PDF^L||STJAMES^IM^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSANCjQgMCBSCj4+Cj4+Ci9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCjUgMCBvYmo=||||||F|||20260120
```

---

## 18. ORU^R01 - ECG report with embedded base64 (Cork University Hospital)

```
MSH|^~\&|iPMS|CUH|GP_SYSTEM|HEALTHLINK|20251212093000||ORU^R01^ORU_R01|MSG00456|P|2.4|||AL|AL||8859/1
PID|1||4817362^^^CUH^MRN~7193248HA^^^PPS^PPS||MCCARTHY^CIARÁN^^^^^L||19730308|M|||23 Washington Street^^Cork^^T12 F4W6^IRL^H
PV1|1|O|CARD-OPD^^^CUH^^AMB|R|||C4523^Sullivan^Colm^^^Dr^^^IMC
ORC|RE|ORD40501^iPMS|CARD50501^CARDIOSYS||CM||||20251212093000|||C4523^Sullivan^Colm^^^Dr^^^IMC
OBR|1|ORD40501^iPMS|CARD50501^CARDIOSYS|93000^Electrocardiogram 12-lead^CPT4|||20251211|||||||||C4523^Sullivan^Colm^^^Dr^^^IMC||||||20251212093000||CAR|F
OBX|1|FT|93000^ECG 12-lead^CPT4||Sinus rhythm at 72 bpm.\.br\Normal axis.\.br\No ST segment changes.\.br\No pathological Q waves.\.br\\.br\Impression: Normal ECG.||||||F|||20251211
OBX|2|NM|8867-4^Heart rate^LN||72|/min^beats per minute^UCUM|60-100|N|||F|||20251211
OBX|3|ED|PDF^ECG Report PDF^L||CUH^IM^PDF^Base64^JVBERi0xLjcKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgL01lZGlhQm94IFswIDAgNTk1IDg0Ml0gPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSANCjQgMCBSID4+ID4+IC9Db250ZW50cyA1IDAgUiA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9Db3VyaWVyID4+CmVuZG9iago=||||||F|||20251211
```

---

## 19. ADT^A05 - Pre-admission (University Hospital Kerry)

```
MSH|^~\&|iPMS|UHK|HEALTHLINK|HSE|20251201100000||ADT^A05^ADT_A05|MSG00489|P|2.4|||AL|AL||8859/1
EVN|A05|20251201100000|||C9456^O'Brien^Maeve^^^Dr^^^IMC
PID|1||6482139^^^UHK^MRN~4318276TA^^^PPS^PPS||CROWLEY^DARRAGH^^^^^L||19670912|M|||11 Denny Street^^Tralee^Kerry^V92 T8N3^IRL^H||+353 66 7194328^HOME|+353 87 6312847^MOBILE|en|M|||6482139^^^UHK^AN|4318276TA||||Kerry
PV1|1|P|SURG1^^^UHK^^BED|E|||C9456^O'Brien^Maeve^^^Dr^^^IMC|||SUR|||||||||V110345^^^UHK^VN||||||||||||||||||||||||||20251205080000
DG1|1||K40.9^Unilateral inguinal hernia^ICD10||20251201|W
```

---

## 20. ORU^R01 - Laboratory result (Beaumont Hospital)

```
MSH|^~\&|iPMS|BEAUMONT|GP_SYSTEM|HEALTHLINK|20260310140000||ORU^R01^ORU_R01|MSG00512|P|2.4|||AL|AL||8859/1
PID|1||3847162^^^BEAUMONT^MRN~6219348PA^^^PPS^PPS||DUNNE^AOIFE^^^^^L||19870126|F|||5 Collins Avenue^^Dublin 9^^D09 N3T7^IRL^H||+353 1 8472193^HOME
PV1|1|O|HAEM-OPD^^^BEAUMONT^^AMB|R|||C7134^Buckley^Fiachra^^^Dr^^^IMC
ORC|RE|ORD20501^iPMS|LAB60501^LIS||CM||||20260310140000|||C7134^Buckley^Fiachra^^^Dr^^^IMC
OBR|1|ORD20501^iPMS|LAB60501^LIS|58410-2^CBC panel^LN^FBC^Full Blood Count^L|||20260205|||||||||C7134^Buckley^Fiachra^^^Dr^^^IMC||||||20260310140000||HEM|F
OBX|1|NM|718-7^Hemoglobin^LN||13.2|g/dL^grams per deciliter^UCUM|12.0-16.0|N|||F|||20260309
OBX|2|NM|6690-2^WBC^LN||7.8|10*3/uL^thousands per microliter^UCUM|4.0-11.0|N|||F|||20260309
OBX|3|NM|777-3^Platelets^LN||245|10*3/uL^thousands per microliter^UCUM|150-400|N|||F|||20260309
OBX|4|NM|789-8^RBC^LN||4.5|10*6/uL^millions per microliter^UCUM|4.0-5.5|N|||F|||20260309
OBX|5|NM|787-2^MCV^LN||88.2|fL^femtoliters^UCUM|80-100|N|||F|||20260309
OBX|6|NM|786-4^MCHC^LN||33.5|g/dL^grams per deciliter^UCUM|32.0-36.0|N|||F|||20260309
```

---
