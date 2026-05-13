# Cambio CIS - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Indlæggelse (inpatient admission)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260401073000||ADT^A01^ADT_A01|CAM00001|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A01|20260401073000
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283~^^CP^+4531765470
PV1||I|RSK^MED^M301^S02||||11001^Vestergaard^Kirsten^^^Dr.|||MED||||7|||11001^Vestergaard^Kirsten^^^Dr.||RSK202604010001||||||||||||||||||||||||20260401073000
PV2|||^Akut pancreatit
NK1|1|Skov^Karsten|SPO^Ægtefælle||^^CP^+4528937731
```

---

## 2. ADT^A02 - Overflytning (patient transfer)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260402103000||ADT^A02^ADT_A02|CAM00002|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A02|20260402103000
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283~^^CP^+4531765470
PV1||I|RSK^KIR^K201^S04||||22002^Lund^Mads^^^Dr.|||KIR||||7|||22002^Lund^Mads^^^Dr.||RSK202604010001||||||||||||||||||||||||20260402103000
```

---

## 3. ADT^A03 - Udskrivelse (discharge)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260407140000||ADT^A03^ADT_A03|CAM00003|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A03|20260407140000
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283~^^CP^+4531765470
PV1||I|RSK^KIR^K201^S04||||22002^Lund^Mads^^^Dr.|||KIR||||7|||22002^Lund^Mads^^^Dr.||RSK202604010001||||||||||||||||||||||||20260407140000
PV2|||^Akut pancreatit
```

---

## 4. ADT^A04 - Ambulant registrering (outpatient registration)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260408090000||ADT^A04^ADT_A01|CAM00004|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A04|20260408090000
PID|||0306752095^^^CPR^NNDN||Petersen^Jens^Asger^^||19750603|M|||Søndergade 129^^Glostrup^^2600^DK||^^PH^+4646878889~^^CP^+4524348467
PV1||O|RSK^URO^AMB01||||33003^Mikkelsen^Brian^^^Dr.|||URO||||||||||RSK202604080001||||||||||||||||||||||||20260408090000
PV2|||^Kontrol - blærecancer
```

---

## 5. ADT^A08 - Opdatering af patientdata (update patient information)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260409091500||ADT^A08^ADT_A01|CAM00005|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A08|20260409091500
PID|||0306752095^^^CPR^NNDN||Petersen^Jens^Asger^^||19750603|M|||Hunderupvej 79^^Hvidovre^^2650^DK||^^PH^+4646919293~^^CP^+4524348467
PV1||O|RSK^URO^AMB01||||33003^Mikkelsen^Brian^^^Dr.|||URO||||||||||RSK202604080001||||||||||||||||||||||||20260409091500
```

---

## 6. ADT^A31 - Opdatering af stamdata (update person information)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|CPR_REGISTERET|SST|20260410080000||ADT^A31^ADT_A05|CAM00006|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A31|20260410080000
PID|||2607924670^^^CPR^NNDN||Olsen^Charlotte^Henriette^^||19920726|F|||Kongensgade 175^^Odense V^^5210^DK||^^PH^+4646949596~^^CP^+4591349110
PD1||||44004^Mikkelsen^Lærke^^^Dr.
```

---

## 7. ADT^A40 - Sammenlægning af patientidentiteter (merge patient)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|MPI|SST|20260411060000||ADT^A40^ADT_A39|CAM00007|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A40|20260411060000
PID|||1209861149^^^CPR^NNDN||Bruun^Kristian^Asger^^||19860912|M|||Klostergade 48^^Rødovre^^2610^DK||^^PH^+4646010203
MRG|7673779964^^^CPR^NNDN||RSK202601100001
```

---

## 8. ORM^O01 - Laboratorierekvisition (laboratory order)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LABKA|KBA|20260412083000||ORM^O01|CAM00008|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^MED^M301^S02||||11001^Vestergaard^Kirsten^^^Dr.|||MED||||||||||RSK202604010001
ORC|NW|ORD20260412001^CAMBIO_CIS||||||20260412083000|||11001^Vestergaard^Kirsten^^^Dr.
OBR|1|ORD20260412001^CAMBIO_CIS||AMYL^P-Amylase^LN|||20260412083000||||||||11001^Vestergaard^Kirsten^^^Dr.
OBR|2|ORD20260412001^CAMBIO_CIS||LFT^Leverfunktionsprøver^LN|||20260412083000||||||||11001^Vestergaard^Kirsten^^^Dr.
OBR|3|ORD20260412001^CAMBIO_CIS||CRP^C-reaktivt protein^LN|||20260412083000||||||||11001^Vestergaard^Kirsten^^^Dr.
```

---

## 9. ORU^R01 - Laboratoriesvar (laboratory result)

```
MSH|^~\&|LABKA|KBA|CAMBIO_CIS|ROSKILDE_SYG|20260412143000||ORU^R01^ORU_R01|CAM00009|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^MED^M301^S02||||11001^Vestergaard^Kirsten^^^Dr.|||MED||||||||||RSK202604010001
ORC|RE|ORD20260412001^CAMBIO_CIS||||||20260412143000
OBR|1|ORD20260412001^CAMBIO_CIS||AMYL^P-Amylase^LN|||20260412083000||||||||11001^Vestergaard^Kirsten^^^Dr.||||||20260412143000|||F
OBX|1|NM|AMYL^P-Amylase^LN||780|U/L|28-100|HH|||F
OBX|2|NM|LIPASE^P-Lipase^LN||1250|U/L|13-60|HH|||F
OBX|3|NM|CRP^C-reaktivt protein^LN||145|mg/L|<10|HH|||F
```

---

## 10. ORU^R01 - Laboratoriesvar med PDF (lab result with embedded PDF report)

```
MSH|^~\&|LABKA|KBA|CAMBIO_CIS|ROSKILDE_SYG|20260413101500||ORU^R01^ORU_R01|CAM00010|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^KIR^K201^S04||||22002^Lund^Mads^^^Dr.|||KIR||||||||||RSK202604010001
ORC|RE|ORD20260413001^LABKA||||||20260413101500
OBR|1|ORD20260413001^LABKA||MISC^Samlet blodprøveudskrift^LN|||20260413083000||||||||22002^Lund^Mads^^^Dr.||||||20260413101500|||F
OBX|1|ED|PDF^Laboratorieudskrift^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. SIU^S12 - Aftale-booking (appointment scheduling notification)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|PATIENTPORTAL|SUNDHED_DK|20260414080000||SIU^S12|CAM00011|P|2.5|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^CAMBIO_CIS|||||ROUTINE^^HL70276|AMB_KONTROL^Ambulant kontrol^^^CAMBIO|30|MIN|^^30^20260501093000^20260501100000||||||33003^Mikkelsen^Brian^^^Dr.|^^PH^+4646878889|RSK^URO^AMB01|33003^Mikkelsen^Brian^^^Dr.|^^PH^+4646878889|RSK^URO^AMB01
PID|||0306752095^^^CPR^NNDN||Petersen^Jens^Asger^^||19750603|M|||Hunderupvej 79^^Hvidovre^^2650^DK||^^CP^+4524348467
AIS|1||KONTROL^Cystoskopi kontrol^LOCAL|20260501093000||30|MIN
AIL|1||RSK^URO^AMB01
AIP|1||33003^Mikkelsen^Brian^^^Dr.
```

---

## 12. SIU^S14 - Aftaleændring (appointment modification)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|PATIENTPORTAL|SUNDHED_DK|20260415090000||SIU^S14|CAM00012|P|2.5|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^CAMBIO_CIS|||||ROUTINE^^HL70276|AMB_KONTROL^Ambulant kontrol^^^CAMBIO|30|MIN|^^30^20260508093000^20260508100000||||||33003^Mikkelsen^Brian^^^Dr.|^^PH^+4646878889|RSK^URO^AMB01|33003^Mikkelsen^Brian^^^Dr.|^^PH^+4646878889|RSK^URO^AMB01
PID|||0306752095^^^CPR^NNDN||Petersen^Jens^Asger^^||19750603|M|||Hunderupvej 79^^Hvidovre^^2650^DK||^^CP^+4524348467
AIS|1||KONTROL^Cystoskopi kontrol^LOCAL|20260508093000||30|MIN
AIL|1||RSK^URO^AMB01
AIP|1||33003^Mikkelsen^Brian^^^Dr.
```

---

## 13. ORM^O01 - Røntgenrekvisition (radiology order)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|CARESTREAM_RIS|RSK_RAD|20260416091000||ORM^O01|CAM00013|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^MED^M301^S02||||11001^Vestergaard^Kirsten^^^Dr.|||MED||||||||||RSK202604010001
ORC|NW|ORD20260416001^CAMBIO_CIS||||||20260416091000|||11001^Vestergaard^Kirsten^^^Dr.
OBR|1|ORD20260416001^CAMBIO_CIS||CTABD^CT af abdomen med kontrast^LOCAL|||20260416091000||||||Akut pancreatit, vurdering af nekrose|11001^Vestergaard^Kirsten^^^Dr.
```

---

## 14. ORU^R01 - Mikrobiologisvar (microbiology result)

```
MSH|^~\&|MADS|SSI|CAMBIO_CIS|ROSKILDE_SYG|20260417161500||ORU^R01^ORU_R01|CAM00014|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^KIR^K201^S04||||22002^Lund^Mads^^^Dr.|||KIR||||||||||RSK202604010001
ORC|RE|ORD20260417001^MADS||||||20260417161500
OBR|1|ORD20260417001^MADS||BCUL^Bloddyrkning^LN|||20260416200000||||||||22002^Lund^Mads^^^Dr.||||||20260417161500|||F
OBX|1|TX|BCRESULT^Bloddyrkningsresultat^LN||Ingen vækst efter 5 dages inkubation.||||||F
```

---

## 15. MDM^T02 - Klinisk notat (clinical document notification)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|DOKUMENTDELING|NSP|20260418120000||MDM^T02|CAM00015|P|2.5|||AL|NE||UNICODE UTF-8
EVN|T02|20260418120000
PID|||0306752095^^^CPR^NNDN||Petersen^Jens^Asger^^||19750603|M|||Hunderupvej 79^^Hvidovre^^2650^DK||^^CP^+4524348467
PV1||O|RSK^URO^AMB01||||33003^Mikkelsen^Brian^^^Dr.|||URO||||||||||RSK202604080001
TXA|1|CN^Klinisk notat|TX|20260418120000|33003^Mikkelsen^Brian^^^Dr.||20260418120000|||||DOC20260418001||||||AU
OBX|1|TX|NOTE^Klinisk notat^LN||Cystoskopi kontrol: Ingen tegn på recidiv. Blæreslimhinden normal. Næste kontrol om 6 måneder. Patienten informeret.||||||F
```

---

## 16. ORU^R01 - CT-beskrivelse med PDF (CT report with embedded PDF)

```
MSH|^~\&|CARESTREAM_RIS|RSK_RAD|CAMBIO_CIS|ROSKILDE_SYG|20260416160000||ORU^R01^ORU_R01|CAM00016|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1108863030^^^CPR^NNDN||Skov^Lærke^Yrsa^^||19860811|F|||Vestergade 4^^Slagelse^^4200^DK||^^PH^+4646818283
PV1||I|RSK^MED^M301^S02||||11001^Vestergaard^Kirsten^^^Dr.|||MED||||||||||RSK202604010001
ORC|RE|ORD20260416001^CAMBIO_CIS||||||20260416160000
OBR|1|ORD20260416001^CAMBIO_CIS||CTABD^CT af abdomen med kontrast^LOCAL|||20260416091000||||||||11001^Vestergaard^Kirsten^^^Dr.|||55001^Vinther^Flemming^^^Dr.||20260416160000|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||CT abdomen med iv kontrast: Pancreas er diffust hævet med peripancreatisk fedtinfiltration. Ingen organiseret nekrose. Ingen pseudocyster. Galdegange normale. Ingen fri luft. Konkl: Akut pancreatit, Balthazar grad C.||||||F
OBX|2|ED|PDF^CT abdomen rapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 17. ADT^A01 - Akut indlæggelse (emergency admission)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|LANDSPATIENTREGISTERET|SST|20260419020000||ADT^A01^ADT_A01|CAM00017|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A01|20260419020000
PID|||0509828331^^^CPR^NNDN||Frandsen^Bent^Børge^^||19820905|M|||Randersvej 38^^Holstebro^^7500^DK||^^CP^+4531236071
PV1||E|RSK^AKM^AK101||||66006^Sørensen^Bent^^^Dr.|||AKM||||1|||66006^Sørensen^Bent^^^Dr.||RSK202604190001||||||||||||||||||||||||20260419020000
PV2|||^Apopleksi, mistanke om
NK1|1|Frandsen^Ole|SPO^Ægtefælle||^^CP^+4591268187
```

---

## 18. ORM^O01 - Akut CT-rekvisition (urgent CT order)

```
MSH|^~\&|CAMBIO_CIS|ROSKILDE_SYG|CARESTREAM_RIS|RSK_RAD|20260419022000||ORM^O01|CAM00018|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0509828331^^^CPR^NNDN||Frandsen^Bent^Børge^^||19820905|M|||Randersvej 38^^Holstebro^^7500^DK||^^CP^+4531236071
PV1||E|RSK^AKM^AK101||||66006^Sørensen^Bent^^^Dr.|||AKM||||||||||RSK202604190001
ORC|NW|ORD20260419001^CAMBIO_CIS||||||20260419022000|||66006^Sørensen^Bent^^^Dr.
OBR|1|ORD20260419001^CAMBIO_CIS||CTCEREB^CT cerebrum uden kontrast^LOCAL|||20260419022000||||||AKUT - apopleksi, trombolyse-vurdering|66006^Sørensen^Bent^^^Dr.
```

---

## 19. ORU^R01 - Blodprøvesvar - kritisk værdi (critical lab result)

```
MSH|^~\&|LABKA|KBA|CAMBIO_CIS|ROSKILDE_SYG|20260420151500||ORU^R01^ORU_R01|CAM00019|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2607924670^^^CPR^NNDN||Olsen^Charlotte^Henriette^^||19920726|F|||Kongensgade 175^^Odense V^^5210^DK||^^PH^+4646949596
PV1||I|RSK^MED^M302^S01||||77007^Schmidt^Emma^^^Dr.|||MED||||||||||RSK202604200001
ORC|RE|ORD20260420001^CAMBIO_CIS||||||20260420151500
OBR|1|ORD20260420001^CAMBIO_CIS||K^Kalium^LN|||20260420140000||||||||77007^Schmidt^Emma^^^Dr.||||||20260420151500|||F
OBX|1|NM|K^Kalium^LN||2.5|mmol/L|3.5-5.0|LL|||F
OBX|2|NM|NA^Natrium^LN||125|mmol/L|137-145|LL|||F
OBX|3|NM|MG^Magnesium^LN||0.52|mmol/L|0.70-1.05|L|||F
```

---

## 20. ORU^R01 - D-dimer og troponin (D-dimer and troponin result)

```
MSH|^~\&|LABKA|KBA|CAMBIO_CIS|ROSKILDE_SYG|20260421091000||ORU^R01^ORU_R01|CAM00020|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1209861149^^^CPR^NNDN||Bruun^Kristian^Asger^^||19860912|M|||Klostergade 48^^Rødovre^^2610^DK||^^PH^+4646010203
PV1||E|RSK^AKM^AK101||||66006^Sørensen^Bent^^^Dr.|||AKM||||||||||RSK202604210001
ORC|RE|ORD20260421001^CAMBIO_CIS||||||20260421091000
OBR|1|ORD20260421001^CAMBIO_CIS||CARDIAC^Akut hjertepakke^LN|||20260421083000||||||||66006^Sørensen^Bent^^^Dr.||||||20260421091000|||F
OBX|1|NM|TNTHS^Troponin T, højsensitiv^LN||8|ng/L|<14|N|||F
OBX|2|NM|DDIMER^D-dimer^LN||0.35|mg/L FEU|<0.5|N|||F
OBX|3|NM|CRP^C-reaktivt protein^LN||3|mg/L|<10|N|||F
```
