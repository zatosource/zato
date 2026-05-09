# BCC (CGI) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Indlæggelse (inpatient admission)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260401080000||ADT^A01^ADT_A01|BCC00001|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20260401080000
PID|||0712837798^^^CPR^NNDN||Christiansen^Signe^Henriette^^||19831207|F|||Hjallesevej 229^^Aarhus N^^8200^DK||^^PH^+4555342150~^^CP^+4542803385
PV1||I|OUH^MED^A301^S01||||11001^Christiansen^Laura^^^Dr.|||MED||||7|||11001^Christiansen^Laura^^^Dr.||OUH202604010001||||||||||||||||||||||||20260401080000
PV2|||^Kronisk obstruktiv lungesygdom, exacerbation
NK1|1|Christiansen^Henrik|SPO^Ægtefælle||^^CP^+4542991436
```

---

## 2. ADT^A02 - Overflytning (patient transfer)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260402110000||ADT^A02^ADT_A02|BCC00002|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A02|20260402110000
PID|||0712837798^^^CPR^NNDN||Christiansen^Signe^Henriette^^||19831207|F|||Hjallesevej 229^^Aarhus N^^8200^DK||^^PH^+4555342150~^^CP^+4542803385
PV1||I|OUH^LUN^B202^S03||||22002^Berg^Jonas^^^Dr.|||LUN||||7|||22002^Berg^Jonas^^^Dr.||OUH202604010001||||||||||||||||||||||||20260402110000
```

---

## 3. ADT^A03 - Udskrivelse (discharge)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260406140000||ADT^A03^ADT_A03|BCC00003|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20260406140000
PID|||0712837798^^^CPR^NNDN||Christiansen^Signe^Henriette^^||19831207|F|||Hjallesevej 229^^Aarhus N^^8200^DK||^^PH^+4555342150~^^CP^+4542803385
PV1||I|OUH^LUN^B202^S03||||22002^Berg^Jonas^^^Dr.|||LUN||||7|||22002^Berg^Jonas^^^Dr.||OUH202604010001||||||||||||||||||||||||20260406140000
PV2|||^Kronisk obstruktiv lungesygdom, exacerbation
```

---

## 4. ADT^A04 - Ambulant registrering (outpatient registration)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260407090000||ADT^A04^ADT_A01|BCC00004|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20260407090000
PID|||1809722039^^^CPR^NNDN||Johansen^Lars^Viggo^^||19720918|M|||Viborgvej 24^^Esbjerg^^6700^DK||^^PH^+4591969695~^^CP^+4550142881
PV1||O|OUH^ORT^AMB01||||33003^Andersen^Simon^^^Dr.|||ORT||||||||||OUH202604070001||||||||||||||||||||||||20260407090000
PV2|||^Kontrol - knæalloplastik
```

---

## 5. ADT^A08 - Opdatering af patientdata (update patient information)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260408091500||ADT^A08^ADT_A01|BCC00005|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A08|20260408091500
PID|||1809722039^^^CPR^NNDN||Johansen^Lars^Viggo^^||19720918|M|||Paludan-Müllers Vej 234^^Brønshøj^^2700^DK||^^PH^+4560352174~^^CP^+4550142881
PV1||O|OUH^ORT^AMB01||||33003^Andersen^Simon^^^Dr.|||ORT||||||||||OUH202604070001||||||||||||||||||||||||20260408091500
```

---

## 6. ADT^A31 - Opdatering af stamdata (update person information)

```
MSH|^~\&|BCC|OUH|CPR_REGISTERET|SST|20260409080000||ADT^A31^ADT_A05|BCC00006|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A31|20260409080000
PID|||1410656774^^^CPR^NNDN||Bang^Inger^Oda^^||19651014|F|||Amagerbrogade 85^^Slagelse^^4200^DK||^^PH^+4547881821~^^CP^+4593927737
PD1||||44004^Clausen^Lærke^^^Dr.
```

---

## 7. ADT^A40 - Sammenlægning af patientidentiteter (merge patient)

```
MSH|^~\&|BCC|OUH|MPI|SST|20260410060000||ADT^A40^ADT_A39|BCC00007|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A40|20260410060000
PID|||2503787801^^^CPR^NNDN||Sørensen^Erik^Arne^^||19780325|M|||Maglekildevej 164^^Aarhus N^^8200^DK||^^PH^+4541126549
MRG|9113382477^^^CPR^NNDN||OUH202601050001
```

---

## 8. ORM^O01 - Laboratorierekvisition (laboratory order)

```
MSH|^~\&|BCC|OUH|LABKA|KBA|20260411083000||ORM^O01|BCC00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1602909889^^^CPR^NNDN||Vinther^Jens^Steen^^||19900216|M|||Randersvej 44^^Aalborg^^9000^DK||^^PH^+4594401117
PV1||I|OUH^MED^A308^S04||||55005^Nørgaard^Anders^^^Dr.|||MED||||||||||OUH202604110001
ORC|NW|ORD20260411001^BCC||||||20260411083000|||55005^Nørgaard^Anders^^^Dr.
OBR|1|ORD20260411001^BCC||LFT^Leverfunktionsprøver^LN|||20260411083000||||||||55005^Nørgaard^Anders^^^Dr.
OBR|2|ORD20260411001^BCC||AMYL^Amylase^LN|||20260411083000||||||||55005^Nørgaard^Anders^^^Dr.
```

---

## 9. ORU^R01 - Laboratoriesvar (laboratory result)

```
MSH|^~\&|LABKA|KBA|BCC|OUH|20260411143000||ORU^R01^ORU_R01|BCC00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1602909889^^^CPR^NNDN||Vinther^Jens^Steen^^||19900216|M|||Randersvej 44^^Aalborg^^9000^DK||^^PH^+4594401117
PV1||I|OUH^MED^A308^S04||||55005^Nørgaard^Anders^^^Dr.|||MED||||||||||OUH202604110001
ORC|RE|ORD20260411001^BCC||||||20260411143000
OBR|1|ORD20260411001^BCC||LFT^Leverfunktionsprøver^LN|||20260411083000||||||||55005^Nørgaard^Anders^^^Dr.||||||20260411143000|||F
OBX|1|NM|ALAT^Alanin-aminotransferase^LN||185|U/L|10-45|HH|||F
OBX|2|NM|ASAT^Aspartat-aminotransferase^LN||142|U/L|15-35|HH|||F
OBX|3|NM|ALP^Basisk fosfatase^LN||210|U/L|35-105|H|||F
OBX|4|NM|BILIRUB^Bilirubin, total^LN||45|umol/L|5-25|H|||F
OBX|5|NM|GGT^Gamma-glutamyltransferase^LN||320|U/L|10-80|HH|||F
OBX|6|NM|ALBUM^Albumin^LN||31|g/L|35-50|L|||F
```

---

## 10. ORU^R01 - Laboratoriesvar med PDF (lab result with embedded PDF report)

```
MSH|^~\&|LABKA|KBA|BCC|OUH|20260412101500||ORU^R01^ORU_R01|BCC00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1602909889^^^CPR^NNDN||Vinther^Jens^Steen^^||19900216|M|||Randersvej 44^^Aalborg^^9000^DK||^^PH^+4594401117
PV1||I|OUH^MED^A308^S04||||55005^Nørgaard^Anders^^^Dr.|||MED||||||||||OUH202604110001
ORC|RE|ORD20260412001^LABKA||||||20260412101500
OBR|1|ORD20260412001^LABKA||MISC^Samlet laboratorieudskrift^LN|||20260412083000||||||||55005^Nørgaard^Anders^^^Dr.||||||20260412101500|||F
OBX|1|ED|PDF^Laboratorieudskrift^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. SIU^S12 - Aftale-booking (appointment scheduling notification)

```
MSH|^~\&|BCC|OUH|PATIENTPORTAL|SUNDHED_DK|20260413080000||SIU^S12|BCC00011|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APT20260505001^BCC|||||ROUTINE^^HL70276|AMB_KONTROL^Ambulant kontrol^^^BCC|20|MIN|^^20^20260505090000^20260505092000||||||33003^Andersen^Simon^^^Dr.|^^PH^+4542809446|OUH^ORT^AMB01|33003^Andersen^Simon^^^Dr.|^^PH^+4542809446|OUH^ORT^AMB01
PID|||1809722039^^^CPR^NNDN||Johansen^Lars^Viggo^^||19720918|M|||Paludan-Müllers Vej 234^^Brønshøj^^2700^DK||^^CP^+4550142881
AIS|1||KONTROL^Ambulant kontrol - ortopædi^LOCAL|20260505090000||20|MIN
AIL|1||OUH^ORT^AMB01
AIP|1||33003^Andersen^Simon^^^Dr.
```

---

## 12. SIU^S14 - Aftaleændring (appointment modification)

```
MSH|^~\&|BCC|OUH|PATIENTPORTAL|SUNDHED_DK|20260414090000||SIU^S14|BCC00012|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APT20260505001^BCC|||||ROUTINE^^HL70276|AMB_KONTROL^Ambulant kontrol^^^BCC|20|MIN|^^20^20260512090000^20260512092000||||||33003^Andersen^Simon^^^Dr.|^^PH^+4542809446|OUH^ORT^AMB01|33003^Andersen^Simon^^^Dr.|^^PH^+4542809446|OUH^ORT^AMB01
PID|||1809722039^^^CPR^NNDN||Johansen^Lars^Viggo^^||19720918|M|||Paludan-Müllers Vej 234^^Brønshøj^^2700^DK||^^CP^+4550142881
AIS|1||KONTROL^Ambulant kontrol - ortopædi^LOCAL|20260512090000||20|MIN
AIL|1||OUH^ORT^AMB01
AIP|1||33003^Andersen^Simon^^^Dr.
```

---

## 13. ORM^O01 - Røntgenrekvisition (radiology order)

```
MSH|^~\&|BCC|OUH|CARESTREAM_RIS|OUH_RAD|20260415091000||ORM^O01|BCC00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0712837798^^^CPR^NNDN||Christiansen^Signe^Henriette^^||19831207|F|||Hjallesevej 229^^Aarhus N^^8200^DK||^^PH^+4555342150
PV1||I|OUH^LUN^B202^S03||||22002^Berg^Jonas^^^Dr.|||LUN||||||||||OUH202604010001
ORC|NW|ORD20260415001^BCC||||||20260415091000|||22002^Berg^Jonas^^^Dr.
OBR|1|ORD20260415001^BCC||XTHORAX^Røntgen af thorax^LOCAL|||20260415091000||||||KOL exacerbation - kontrol|22002^Berg^Jonas^^^Dr.
```

---

## 14. ORU^R01 - Mikrobiologisvar (microbiology result)

```
MSH|^~\&|MADS|SSI|BCC|OUH|20260416161500||ORU^R01^ORU_R01|BCC00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1602909889^^^CPR^NNDN||Vinther^Jens^Steen^^||19900216|M|||Randersvej 44^^Aalborg^^9000^DK||^^PH^+4594401117
PV1||I|OUH^MED^A308^S04||||55005^Nørgaard^Anders^^^Dr.|||MED||||||||||OUH202604110001
ORC|RE|ORD20260416001^MADS||||||20260416161500
OBR|1|ORD20260416001^MADS||UCUL^Urindyrkning^LN|||20260415100000||||||||55005^Nørgaard^Anders^^^Dr.||||||20260416161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||KPNEU^Klebsiella pneumoniae^LN|||A|||F
OBX|2|ST|SUSCEPT^Følsomhed - Ampicillin^LN||R|||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Cefuroxim^LN||S|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||S|||A|||F
OBX|5|ST|SUSCEPT^Følsomhed - Meropenem^LN||S|||A|||F
```

---

## 15. MDM^T02 - Klinisk notat (clinical document notification)

```
MSH|^~\&|BCC|OUH|DOKUMENTDELING|NSP|20260417120000||MDM^T02|BCC00015|P|2.4|||AL|NE||UNICODE UTF-8
EVN|T02|20260417120000
PID|||1602909889^^^CPR^NNDN||Vinther^Jens^Steen^^||19900216|M|||Randersvej 44^^Aalborg^^9000^DK||^^PH^+4594401117
PV1||I|OUH^MED^A308^S04||||55005^Nørgaard^Anders^^^Dr.|||MED||||||||||OUH202604110001
TXA|1|CN^Klinisk notat|TX|20260417120000|55005^Nørgaard^Anders^^^Dr.||20260417120000|||||DOC20260417001||||||AU
OBX|1|TX|NOTE^Klinisk notat^LN||Hepatitisudredning: Forhøjede levertal, se laboratoriesvar. Startet udredning for viral hepatitis. Serologiprøver afsendt. Patienten er abstinent fra alkohol. Planlagt UL-scanning af leveren i morgen.||||||F
```

---

## 16. ORU^R01 - Patologisvar med PDF-rapport (pathology result with embedded PDF)

```
MSH|^~\&|PATOLOGI|OUH_PAT|BCC|OUH|20260418100000||ORU^R01^ORU_R01|BCC00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1410656774^^^CPR^NNDN||Bang^Inger^Oda^^||19651014|F|||Amagerbrogade 85^^Slagelse^^4200^DK||^^PH^+4547881821
PV1||I|OUH^KIR^C105^S02||||66006^Clausen^Magnus^^^Dr.|||KIR||||||||||OUH202604180001
ORC|RE|ORD20260418001^PATOLOGI||||||20260418100000
OBR|1|ORD20260418001^PATOLOGI||PATHBX^Biopsi - mamma^LN|||20260416090000||||||||66006^Clausen^Magnus^^^Dr.||||||20260418100000|||F
OBX|1|TX|PATDIAG^Patologisk diagnose^LN||Invasivt duktalt karcinom, grad II. Østrogenreceptorpositiv, HER2-negativ. Frie resektionsrande.||||||F
OBX|2|ED|PDF^Patologirapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 17. ADT^A01 - Akut indlæggelse (emergency admission)

```
MSH|^~\&|BCC|OUH|LANDSPATIENTREGISTERET|SST|20260419230000||ADT^A01^ADT_A01|BCC00017|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20260419230000
PID|||2211971075^^^CPR^NNDN||Dahl^Peter^Bo^^||19971122|M|||Amagerbrogade 194^^Aarhus C^^8000^DK||^^CP^+4522484459
PV1||E|OUH^AKM^A101||||77007^Larsen^Jonas^^^Dr.|||AKM||||1|||77007^Larsen^Jonas^^^Dr.||OUH202604190001||||||||||||||||||||||||20260419230000
PV2|||^Akut myokardieinfarkt
NK1|1|Madsen^Jakob|GIRLF^Kæreste||^^CP^+4591446281
```

---

## 18. ORM^O01 - Akut blodprøverekvisition (urgent blood test order)

```
MSH|^~\&|BCC|OUH|LABKA|KBA|20260419231000||ORM^O01|BCC00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2211971075^^^CPR^NNDN||Dahl^Peter^Bo^^||19971122|M|||Amagerbrogade 194^^Aarhus C^^8000^DK||^^CP^+4522484459
PV1||E|OUH^AKM^A101||||77007^Larsen^Jonas^^^Dr.|||AKM||||||||||OUH202604190001
ORC|NW|ORD20260419001^BCC||||||20260419231000|||77007^Larsen^Jonas^^^Dr.
OBR|1|ORD20260419001^BCC||TROP^Troponin T og I^LN|||20260419231000||||||||77007^Larsen^Jonas^^^Dr.
OBR|2|ORD20260419001^BCC||CKMB^CK-MB^LN|||20260419231000||||||||77007^Larsen^Jonas^^^Dr.
OBR|3|ORD20260419001^BCC||KOAG^Koagulationstal^LN|||20260419231000||||||||77007^Larsen^Jonas^^^Dr.
```

---

## 19. ORU^R01 - Hjertesvar - troponin (cardiac marker result)

```
MSH|^~\&|LABKA|KBA|BCC|OUH|20260420004500||ORU^R01^ORU_R01|BCC00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2211971075^^^CPR^NNDN||Dahl^Peter^Bo^^||19971122|M|||Amagerbrogade 194^^Aarhus C^^8000^DK||^^CP^+4522484459
PV1||E|OUH^AKM^A101||||77007^Larsen^Jonas^^^Dr.|||AKM||||||||||OUH202604190001
ORC|RE|ORD20260419001^BCC||||||20260420004500
OBR|1|ORD20260419001^BCC||TROP^Troponin T og I^LN|||20260419231000||||||||77007^Larsen^Jonas^^^Dr.||||||20260420004500|||F
OBX|1|NM|TNTHS^Troponin T, højsensitiv^LN||892|ng/L|<14|HH|||F
OBX|2|NM|TNIH^Troponin I, højsensitiv^LN||4500|ng/L|<26|HH|||F
OBX|3|NM|CKMB^CK-MB masse^LN||85|ug/L|<5|HH|||F
```

---

## 20. ORU^R01 - Nyrefunktionssvar (renal function result)

```
MSH|^~\&|LABKA|KBA|BCC|OUH|20260421091000||ORU^R01^ORU_R01|BCC00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1410656774^^^CPR^NNDN||Bang^Inger^Oda^^||19651014|F|||Amagerbrogade 85^^Slagelse^^4200^DK||^^PH^+4547881821
PV1||O|OUH^NEF^AMB01||||88008^Berg^Bent^^^Dr.|||NEF||||||||||OUH202604210001
ORC|RE|ORD20260421001^LABKA||||||20260421091000
OBR|1|ORD20260421001^LABKA||RENAL^Nyrefunktion^LN|||20260421083000||||||||88008^Berg^Bent^^^Dr.||||||20260421091000|||F
OBX|1|NM|CREA^Kreatinin^LN||142|umol/L|45-105|H|||F
OBX|2|NM|EGFR^Estimeret GFR^LN||38|mL/min/1.73m2|>60|L|||F
OBX|3|NM|UREA^Karbamid^LN||12.8|mmol/L|2.6-6.4|H|||F
OBX|4|NM|K^Kalium^LN||5.3|mmol/L|3.5-5.0|H|||F
OBX|5|NM|PHOS^Fosfat^LN||1.9|mmol/L|0.8-1.5|H|||F
```
