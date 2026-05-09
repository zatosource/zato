# Columna Flow (Systematic) - real HL7v2 ER7 messages

---

## 1. ADT^A04 - Akut modtagelse - ankomstregistrering (ED arrival registration)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260401070000||ADT^A04^ADT_A01|CF00001|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20260401070000
PID|||1404875050^^^CPR^NNDN||Nørgaard^Clara^Gerda^^||19870414|F|||Valby Langgade 50^^Roskilde^^4000^DK||^^PH^+4569371022~^^CP^+4531532788
PV1||E|AAUH^AKM^101^A1||||11001^Andersen^Julie^^^Dr.|||AKM||||1|||11001^Andersen^Julie^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260401070000
PV2|||^Brystsmerter
```

---

## 2. ADT^A08 - Triagering opdatering (triage status update)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260401071000||ADT^A08^ADT_A01|CF00002|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A08|20260401071000
PID|||1404875050^^^CPR^NNDN||Nørgaard^Clara^Gerda^^||19870414|F|||Valby Langgade 50^^Roskilde^^4000^DK||^^PH^+4569371022~^^CP^+4531532788
PV1||E|AAUH^AKM^101^A1||||11001^Andersen^Julie^^^Dr.|||AKM||||2|||11001^Andersen^Julie^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260401071000
PV2|||^Brystsmerter - triage orange
```

---

## 3. ADT^A02 - Overflytning fra akut til sengeafdeling (transfer from ED to ward)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260401100000||ADT^A02^ADT_A02|CF00003|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A02|20260401100000
PID|||1404875050^^^CPR^NNDN||Nørgaard^Clara^Gerda^^||19870414|F|||Valby Langgade 50^^Roskilde^^4000^DK||^^PH^+4569371022~^^CP^+4531532788
PV1||I|AAUH^KAR^501^B2||||22002^Johansen^Susanne^^^Dr.|||KAR||||7|||22002^Johansen^Susanne^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260401100000
```

---

## 4. SIU^S12 - Operationsbooking (surgery scheduling)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260402080000||SIU^S12|CF00004|P|2.4|||AL|NE||UNICODE UTF-8
SCH|OP20260405001^COLUMNA_FLOW|||||ELECTIVE^^HL70276|CABG^Koronar bypass^^^FLOW|180|MIN|^^180^20260405080000^20260405110000||||||33003^Andersen^Bodil^^^Dr.|^^PH^+4583825540|AAUH^KIR^OP01|33003^Andersen^Bodil^^^Dr.|^^PH^+4583825540|AAUH^KIR^OP01
PID|||1404875050^^^CPR^NNDN||Nørgaard^Clara^Gerda^^||19870414|F|||Valby Langgade 50^^Roskilde^^4000^DK||^^CP^+4531532788
AIS|1||CABG^Koronar bypass operation^LOCAL|20260405080000||180|MIN
AIL|1||AAUH^KIR^OP01
AIP|1||33003^Andersen^Bodil^^^Dr.
```

---

## 5. SIU^S14 - Operationsændring (surgery modification)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260403090000||SIU^S14|CF00005|P|2.4|||AL|NE||UNICODE UTF-8
SCH|OP20260405001^COLUMNA_FLOW|||||ELECTIVE^^HL70276|CABG^Koronar bypass^^^FLOW|180|MIN|^^180^20260407080000^20260407110000||||||33003^Andersen^Bodil^^^Dr.|^^PH^+4583825540|AAUH^KIR^OP01|33003^Andersen^Bodil^^^Dr.|^^PH^+4583825540|AAUH^KIR^OP01
PID|||1404875050^^^CPR^NNDN||Nørgaard^Clara^Gerda^^||19870414|F|||Valby Langgade 50^^Roskilde^^4000^DK||^^CP^+4531532788
AIS|1||CABG^Koronar bypass operation^LOCAL|20260407080000||180|MIN
AIL|1||AAUH^KIR^OP01
AIP|1||33003^Andersen^Bodil^^^Dr.
```

---

## 6. ADT^A01 - Indlæggelse via akut modtagelse (admission through ED)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260404020000||ADT^A01^ADT_A01|CF00006|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20260404020000
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||1|||44004^Johansen^Britt^^^Dr.||AAUH202604040001||||||||||||||||||||||||20260404020000
PV2|||^Fraktur af distale radius
NK1|1|Larsen^Rasmus|GIRLF^Kæreste||^^CP^+4553251115
```

---

## 7. ORM^O01 - Akut laboratorierekvisition (urgent lab order from ED)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|LABKA|KBA|20260404021000||ORM^O01|CF00007|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||||||||AAUH202604040001
ORC|NW|ORD20260404001^COLUMNA_FLOW||||||20260404021000|||44004^Johansen^Britt^^^Dr.
OBR|1|ORD20260404001^COLUMNA_FLOW||CBC^Komplet blodtælling^LN|||20260404021000||||||AKUT - fraktur, præoperativ|44004^Johansen^Britt^^^Dr.
OBR|2|ORD20260404001^COLUMNA_FLOW||KOAG^Koagulationstal^LN|||20260404021000||||||||44004^Johansen^Britt^^^Dr.
```

---

## 8. ORM^O01 - Røntgenrekvisition fra akut (radiology order from ED)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|CARESTREAM_RIS|AAUH_RAD|20260404022000||ORM^O01|CF00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||||||||AAUH202604040001
ORC|NW|ORD20260404002^COLUMNA_FLOW||||||20260404022000|||44004^Johansen^Britt^^^Dr.
OBR|1|ORD20260404002^COLUMNA_FLOW||XWRIST^Røntgen af håndled^LOCAL|||20260404022000||||||Fald på cykel, smerter i ve. håndled|44004^Johansen^Britt^^^Dr.
```

---

## 9. ORU^R01 - Laboratoriesvar til akut (lab result to ED)

```
MSH|^~\&|LABKA|KBA|COLUMNA_FLOW|AALBORG_UH|20260404031500||ORU^R01^ORU_R01|CF00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||||||||AAUH202604040001
ORC|RE|ORD20260404001^COLUMNA_FLOW||||||20260404031500
OBR|1|ORD20260404001^COLUMNA_FLOW||CBC^Komplet blodtælling^LN|||20260404021000||||||||44004^Johansen^Britt^^^Dr.||||||20260404031500|||F
OBX|1|NM|HGB^Hæmoglobin^LN||9.2|mmol/L|8.3-10.5|N|||F
OBX|2|NM|PLT^Trombocytter^LN||265|10*9/L|145-390|N|||F
OBX|3|NM|INR^International Normalised Ratio^LN||1.0||0.8-1.2|N|||F
```

---

## 10. ORU^R01 - Røntgensvar med PDF (radiology result with embedded PDF to ED)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_FLOW|AALBORG_UH|20260404040000||ORU^R01^ORU_R01|CF00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||||||||AAUH202604040001
ORC|RE|ORD20260404002^COLUMNA_FLOW||||||20260404040000
OBR|1|ORD20260404002^COLUMNA_FLOW||XWRIST^Røntgen af håndled^LOCAL|||20260404022000||||||||44004^Johansen^Britt^^^Dr.|||55001^Nielsen^Niels^^^Dr.||20260404040000|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||Røntgen af ve. håndled AP og lateral: Fraktur af distale radius med dorsal angulation og let forkortning. Ingen ulnafraktur. Colles-fraktur. Anbefaler reposition i lokal bedøvelse.||||||F
OBX|2|ED|PDF^Røntgenrapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. ADT^A03 - Udskrivelse fra akut modtagelse (discharge from ED)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260404080000||ADT^A03^ADT_A03|CF00011|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20260404080000
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
PV1||E|AAUH^AKM^101^A3||||44004^Johansen^Britt^^^Dr.|||AKM||||1|||44004^Johansen^Britt^^^Dr.||AAUH202604040001||||||||||||||||||||||||20260404080000
PV2|||^Fraktur af distale radius - behandlet, reposition og gipsskinne
```

---

## 12. ADT^A04 - Ambulant registrering - dagkirurgi (day surgery registration)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260405063000||ADT^A04^ADT_A01|CF00012|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20260405063000
PID|||1209739768^^^CPR^NNDN||Larsen^Kirsten^Karla^^||19730912|F|||Danmarksgade 113^^Hillerød^^3400^DK||^^PH^+4553214566~^^CP^+4525833389
PV1||O|AAUH^KIR^DAG01||||55005^Svendsen^Jonas^^^Dr.|||KIR||||||||||AAUH202604050001||||||||||||||||||||||||20260405063000
PV2|||^Laparoskopisk kolecystektomi
```

---

## 13. SIU^S12 - Ambulant aftale-booking (outpatient appointment scheduling)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|PATIENTPORTAL|SUNDHED_DK|20260406080000||SIU^S12|CF00013|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^COLUMNA_FLOW|||||ROUTINE^^HL70276|KONTROL^Ortopædisk kontrol^^^FLOW|15|MIN|^^15^20260501100000^20260501101500||||||66006^Friis^Jens^^^Dr.|^^PH^+4594742377|AAUH^ORT^AMB01|66006^Friis^Jens^^^Dr.|^^PH^+4594742377|AAUH^ORT^AMB01
PID|||2506957767^^^CPR^NNDN||Olsen^Peter^Holger^^||19950625|M|||Åboulevarden 84^^København N^^2200^DK||^^CP^+4560328811
AIS|1||KONTROL^Kontrolrøntgen - håndled^LOCAL|20260501100000||15|MIN
AIL|1||AAUH^ORT^AMB01
AIP|1||66006^Friis^Jens^^^Dr.
```

---

## 14. MDM^T02 - Operationsnotat (surgical note)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|DOKUMENTDELING|NSP|20260405140000||MDM^T02|CF00014|P|2.4|||AL|NE||UNICODE UTF-8
EVN|T02|20260405140000
PID|||1209739768^^^CPR^NNDN||Larsen^Kirsten^Karla^^||19730912|F|||Danmarksgade 113^^Hillerød^^3400^DK||^^PH^+4553214566
PV1||O|AAUH^KIR^DAG01||||55005^Svendsen^Jonas^^^Dr.|||KIR||||||||||AAUH202604050001
TXA|1|OP^Operationsnotat|TX|20260405140000|55005^Svendsen^Jonas^^^Dr.||20260405140000|||||DOC20260405001||||||AU
OBX|1|TX|NOTE^Operationsnotat^LN||Laparoskopisk kolecystektomi. Ukompliceret procedure. Galdeblæren fjernet intakt. Normal anatomi af ductus cysticus og a. cystica. Operationstid: 45 min. Blodtab: minimalt. Patienten udskrevet til hjemmet i velbefindende.||||||F
```

---

## 15. ORU^R01 - Operationsnotat med PDF (surgical note with embedded PDF)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|DOKUMENTDELING|NSP|20260405143000||ORU^R01^ORU_R01|CF00015|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1209739768^^^CPR^NNDN||Larsen^Kirsten^Karla^^||19730912|F|||Danmarksgade 113^^Hillerød^^3400^DK||^^PH^+4553214566
PV1||O|AAUH^KIR^DAG01||||55005^Svendsen^Jonas^^^Dr.|||KIR||||||||||AAUH202604050001
ORC|RE|DOC20260405001^COLUMNA_FLOW||||||20260405143000
OBR|1|DOC20260405001^COLUMNA_FLOW||OPNOTE^Operationsnotat - komplet^LN|||20260405140000||||||||55005^Svendsen^Jonas^^^Dr.||||||20260405143000|||F
OBX|1|ED|PDF^Operationsnotat^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 16. ADT^A03 - Udskrivelse - dagkirurgi (discharge from day surgery)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260405160000||ADT^A03^ADT_A03|CF00016|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20260405160000
PID|||1209739768^^^CPR^NNDN||Larsen^Kirsten^Karla^^||19730912|F|||Danmarksgade 113^^Hillerød^^3400^DK||^^PH^+4553214566
PV1||O|AAUH^KIR^DAG01||||55005^Svendsen^Jonas^^^Dr.|||KIR||||||||||AAUH202604050001||||||||||||||||||||||||20260405160000
PV2|||^Laparoskopisk kolecystektomi, ukompliceret
```

---

## 17. ADT^A04 - Ambulant registrering - skadestueankomst (ED walk-in arrival)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|COLUMNA_CIS|AALBORG_UH|20260406193000||ADT^A04^ADT_A01|CF00017|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20260406193000
PID|||0711009967^^^CPR^NNDN||Madsen^Oliver^Svend^^||20001107|M|||Frederikssundsvej 226^^Roskilde^^4000^DK||^^CP^+4529314227
PV1||E|AAUH^AKM^SKADE^S01||||77007^Poulsen^Magnus^^^Dr.|||AKM||||5|||77007^Poulsen^Magnus^^^Dr.||AAUH202604060001||||||||||||||||||||||||20260406193000
PV2|||^Forstuvning af ankel
```

---

## 18. ORM^O01 - Rekvisition fra skadestue (order from ED walk-in)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|CARESTREAM_RIS|AAUH_RAD|20260406194000||ORM^O01|CF00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0711009967^^^CPR^NNDN||Madsen^Oliver^Svend^^||20001107|M|||Frederikssundsvej 226^^Roskilde^^4000^DK||^^CP^+4529314227
PV1||E|AAUH^AKM^SKADE^S01||||77007^Poulsen^Magnus^^^Dr.|||AKM||||||||||AAUH202604060001
ORC|NW|ORD20260406001^COLUMNA_FLOW||||||20260406194000|||77007^Poulsen^Magnus^^^Dr.
OBR|1|ORD20260406001^COLUMNA_FLOW||XANKLE^Røntgen af ankel^LOCAL|||20260406194000||||||Inversions-traume, hævelse lateralt|77007^Poulsen^Magnus^^^Dr.
```

---

## 19. ORU^R01 - Røntgensvar til skadestue (radiology result to ED walk-in)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_FLOW|AALBORG_UH|20260406204500||ORU^R01^ORU_R01|CF00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0711009967^^^CPR^NNDN||Madsen^Oliver^Svend^^||20001107|M|||Frederikssundsvej 226^^Roskilde^^4000^DK||^^CP^+4529314227
PV1||E|AAUH^AKM^SKADE^S01||||77007^Poulsen^Magnus^^^Dr.|||AKM||||||||||AAUH202604060001
ORC|RE|ORD20260406001^COLUMNA_FLOW||||||20260406204500
OBR|1|ORD20260406001^COLUMNA_FLOW||XANKLE^Røntgen af ankel^LOCAL|||20260406194000||||||||77007^Poulsen^Magnus^^^Dr.|||55001^Nielsen^Niels^^^Dr.||20260406204500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||Røntgen af ve. ankel AP, lateral og mortise: Ingen fraktur. Let bløddelssvulst lateralt forenelig med ligamentskade. Fibula og tibia intakte. Ankelmortisen kongruent. Konkl: Ingen ossøse læsioner.||||||F
```

---

## 20. ADT^A03 - Udskrivelse fra skadestue (discharge from ED walk-in)

```
MSH|^~\&|COLUMNA_FLOW|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260406213000||ADT^A03^ADT_A03|CF00020|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20260406213000
PID|||0711009967^^^CPR^NNDN||Madsen^Oliver^Svend^^||20001107|M|||Frederikssundsvej 226^^Roskilde^^4000^DK||^^CP^+4529314227
PV1||E|AAUH^AKM^SKADE^S01||||77007^Poulsen^Magnus^^^Dr.|||AKM||||5|||77007^Poulsen^Magnus^^^Dr.||AAUH202604060001||||||||||||||||||||||||20260406213000
PV2|||^Forstuvning af ankel - behandlet, bandage og krykkestokke
```
