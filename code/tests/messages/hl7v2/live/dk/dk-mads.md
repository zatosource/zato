# MADS (microbiology LIS) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Bloddyrkning-rekvisition (blood culture order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|MADS|SSI|20260401200000||ORM^O01|MADS00001|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2507835855^^^CPR^NNDN||Bertelsen^Tobias^Helmer^^||19830725|M|||Grønnegade 102^^København V^^1620^DK||^^PH^+4558701247
PV1||I|AAUH^MED^302^B4||||12001^Bach^Ulla^^^Dr.|||MED||||||||||AAUH202604010001
ORC|NW|ORD20260401001^COLUMNA_CIS||||||20260401200000|||12001^Bach^Ulla^^^Dr.
OBR|1|ORD20260401001^COLUMNA_CIS||BCUL^Bloddyrkning^LN|||20260401200000||||||Feber 39.2, mistanke om sepsis|12001^Bach^Ulla^^^Dr.
```

---

## 2. ORM^O01 - Urindyrkning-rekvisition (urine culture order)

```
MSH|^~\&|BCC|OUH|MADS|SSI|20260402083000||ORM^O01|MADS00002|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0502908365^^^CPR^NNDN||Frandsen^Oliver^Gunnar^^||19900205|M|||Tolderlundsvej 214^^Esbjerg Ø^^6705^DK||^^PH^+4583363014
PV1||I|OUH^MED^A308^S04||||22002^Christensen^Kristian^^^Dr.|||MED||||||||||OUH202604020001
ORC|NW|ORD20260402001^BCC||||||20260402083000|||22002^Christensen^Kristian^^^Dr.
OBR|1|ORD20260402001^BCC||UCUL^Urindyrkning^LN|||20260402083000||||||Dysuri og pollakisuri|22002^Christensen^Kristian^^^Dr.
```

---

## 3. ORM^O01 - Svælgpodning-rekvisition (throat swab order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|MADS|SSI|20260403091000||ORM^O01|MADS00003|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1207891904^^^CPR^NNDN||Clausen^Rikke^Asta^^||19890712|F|||Munkerisvej 190^^Hillerød^^3400^DK||^^PH^+4561409262
PV1||I|RH^HÆMA^H3041^S01||||33003^Christensen^Charlotte^^^Dr.|||HÆMA||||||||||RH202604030001
ORC|NW|ORD20260403001^EPIC||||||20260403091000|||33003^Christensen^Charlotte^^^Dr.
OBR|1|ORD20260403001^EPIC||TSWAB^Svælgpodning^LN|||20260403091000||||||Neutropeni med feber, immunsupprimeret patient|33003^Christensen^Charlotte^^^Dr.
```

---

## 4. ORU^R01 - Bloddyrkningssvar - positiv (positive blood culture result)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AALBORG_UH|20260402100000||ORU^R01^ORU_R01|MADS00004|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2507835855^^^CPR^NNDN||Bertelsen^Tobias^Helmer^^||19830725|M|||Grønnegade 102^^København V^^1620^DK||^^PH^+4558701247
PV1||I|AAUH^MED^302^B4||||12001^Bach^Ulla^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260401001^COLUMNA_CIS||||||20260402100000
OBR|1|ORD20260401001^COLUMNA_CIS||BCUL^Bloddyrkning^LN|||20260401200000||||||||12001^Bach^Ulla^^^Dr.||||||20260402100000|||P
OBX|1|TX|BCSTATUS^Bloddyrkningsstatus^LN||Foreløbigt resultat: Positive flasker efter 12 timer. Gram-farvning viser gram-negative stave. Endelig identifikation og resistensbestemmelse følger.||||||P
```

---

## 5. ORU^R01 - Bloddyrkningssvar - endelig med resistens (final blood culture with susceptibility)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AALBORG_UH|20260403161500||ORU^R01^ORU_R01|MADS00005|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2507835855^^^CPR^NNDN||Bertelsen^Tobias^Helmer^^||19830725|M|||Grønnegade 102^^København V^^1620^DK||^^PH^+4558701247
PV1||I|AAUH^MED^302^B4||||12001^Bach^Ulla^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260401001^COLUMNA_CIS||||||20260403161500
OBR|1|ORD20260401001^COLUMNA_CIS||BCUL^Bloddyrkning^LN|||20260401200000||||||||12001^Bach^Ulla^^^Dr.||||||20260403161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||ECO^Escherichia coli^LN|||A|||F
OBX|2|ST|SUSCEPT^Følsomhed - Ampicillin^LN||R|||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Amoxicillin/clavulansyre^LN||S|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Cefuroxim^LN||S|||A|||F
OBX|5|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||S|||A|||F
OBX|6|ST|SUSCEPT^Følsomhed - Gentamicin^LN||S|||A|||F
OBX|7|ST|SUSCEPT^Følsomhed - Meropenem^LN||S|||A|||F
OBX|8|ST|SUSCEPT^Følsomhed - Piperacillin/tazobactam^LN||S|||A|||F
```

---

## 6. ORU^R01 - Urindyrkningssvar (urine culture result)

```
MSH|^~\&|MADS|SSI|BCC|OUH|20260403161500||ORU^R01^ORU_R01|MADS00006|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0502908365^^^CPR^NNDN||Frandsen^Oliver^Gunnar^^||19900205|M|||Tolderlundsvej 214^^Esbjerg Ø^^6705^DK||^^PH^+4583363014
PV1||I|OUH^MED^A308^S04||||22002^Christensen^Kristian^^^Dr.|||MED||||||||||OUH202604020001
ORC|RE|ORD20260402001^BCC||||||20260403161500
OBR|1|ORD20260402001^BCC||UCUL^Urindyrkning^LN|||20260402083000||||||||22002^Christensen^Kristian^^^Dr.||||||20260403161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||KPNEU^Klebsiella pneumoniae^LN|||A|||F
OBX|2|NM|COLONY^Kolonital^LN||>100000|CFU/mL||||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Ampicillin^LN||R|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Mecillinam^LN||S|||A|||F
OBX|5|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||S|||A|||F
OBX|6|ST|SUSCEPT^Følsomhed - Nitrofurantoin^LN||I|||A|||F
OBX|7|ST|SUSCEPT^Følsomhed - Trimethoprim^LN||R|||A|||F
```

---

## 7. ORU^R01 - Svælgpodningssvar (throat swab result)

```
MSH|^~\&|MADS|SSI|EPIC|RIGSHOSPITALET|20260404141500||ORU^R01^ORU_R01|MADS00007|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1207891904^^^CPR^NNDN||Clausen^Rikke^Asta^^||19890712|F|||Munkerisvej 190^^Hillerød^^3400^DK||^^PH^+4561409262
PV1||I|RH^HÆMA^H3041^S01||||33003^Christensen^Charlotte^^^Dr.|||HÆMA||||||||||RH202604030001
ORC|RE|ORD20260403001^EPIC||||||20260404141500
OBR|1|ORD20260403001^EPIC||TSWAB^Svælgpodning^LN|||20260403091000||||||||33003^Christensen^Charlotte^^^Dr.||||||20260404141500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||CANDALB^Candida albicans^LN|||A|||F
OBX|2|TX|COMMENT^Kommentar^LN||Candida albicans påvist i svælgpodning. Kan være relateret til immunsuppression. Klinisk vurdering anbefales.||||||F
```

---

## 8. ORM^O01 - Sårpodning-rekvisition (wound swab order)

```
MSH|^~\&|BCC|OUH|MADS|SSI|20260405083000||ORM^O01|MADS00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0707651518^^^CPR^NNDN||Knudsen^Astrid^Gerda^^||19650707|F|||Rådhusgade 168^^Brønshøj^^2700^DK||^^PH^+4579596798
PV1||I|OUH^KIR^C105^S02||||44004^Mikkelsen^Martin^^^Dr.|||KIR||||||||||OUH202604050001
ORC|NW|ORD20260405001^BCC||||||20260405083000|||44004^Mikkelsen^Martin^^^Dr.
OBR|1|ORD20260405001^BCC||WSWAB^Sårpodning^LN|||20260405083000||||||Postoperativ sårinfektion, rødme og sekretion|44004^Mikkelsen^Martin^^^Dr.
```

---

## 9. ORU^R01 - Sårpodningssvar med MRSA (wound swab result with MRSA)

```
MSH|^~\&|MADS|SSI|BCC|OUH|20260407161500||ORU^R01^ORU_R01|MADS00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0707651518^^^CPR^NNDN||Knudsen^Astrid^Gerda^^||19650707|F|||Rådhusgade 168^^Brønshøj^^2700^DK||^^PH^+4579596798
PV1||I|OUH^KIR^C105^S02||||44004^Mikkelsen^Martin^^^Dr.|||KIR||||||||||OUH202604050001
ORC|RE|ORD20260405001^BCC||||||20260407161500
OBR|1|ORD20260405001^BCC||WSWAB^Sårpodning^LN|||20260405083000||||||||44004^Mikkelsen^Martin^^^Dr.||||||20260407161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||SAUR^Staphylococcus aureus (MRSA)^LN|||AA|||F
OBX|2|ST|SUSCEPT^Følsomhed - Oxacillin^LN||R|||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Vancomycin^LN||S|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Linezolid^LN||S|||A|||F
OBX|5|ST|SUSCEPT^Følsomhed - Daptomycin^LN||S|||A|||F
OBX|6|ST|SUSCEPT^Følsomhed - Trimethoprim/sulfamethoxazol^LN||S|||A|||F
OBX|7|ST|SUSCEPT^Følsomhed - Clindamycin^LN||R|||A|||F
OBX|8|TX|COMMENT^Kommentar^LN||MRSA påvist. Anmeldelsespligtig til Statens Serum Institut. Kontaktisolation anbefales.||||||F
```

---

## 10. ORM^O01 - Fæcesdyrkning-rekvisition (stool culture order)

```
MSH|^~\&|COLUMNA_CIS|AARHUS_UH|MADS|SSI|20260408083000||ORM^O01|MADS00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1203887868^^^CPR^NNDN||Petersen^Pia^Elisabeth^^||19880312|F|||Havnevej 117^^Frederikssund^^3600^DK||^^PH^+4576851529
PV1||I|AUH^MED^M205^S03||||55005^Vinther^Laura^^^Dr.|||MED||||||||||AUH202604080001
ORC|NW|ORD20260408001^COLUMNA_CIS||||||20260408083000|||55005^Vinther^Laura^^^Dr.
OBR|1|ORD20260408001^COLUMNA_CIS||FCUL^Fæcesdyrkning^LN|||20260408083000||||||Blodig diarré, 5 dages varighed|55005^Vinther^Laura^^^Dr.
```

---

## 11. ORU^R01 - Fæcesdyrkningssvar (stool culture result)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AARHUS_UH|20260410161500||ORU^R01^ORU_R01|MADS00011|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1203887868^^^CPR^NNDN||Petersen^Pia^Elisabeth^^||19880312|F|||Havnevej 117^^Frederikssund^^3600^DK||^^PH^+4576851529
PV1||I|AUH^MED^M205^S03||||55005^Vinther^Laura^^^Dr.|||MED||||||||||AUH202604080001
ORC|RE|ORD20260408001^COLUMNA_CIS||||||20260410161500
OBR|1|ORD20260408001^COLUMNA_CIS||FCUL^Fæcesdyrkning^LN|||20260408083000||||||||55005^Vinther^Laura^^^Dr.||||||20260410161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||CAMP^Campylobacter jejuni^LN|||A|||F
OBX|2|ST|SUSCEPT^Følsomhed - Erythromycin^LN||S|||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||R|||A|||F
OBX|4|TX|COMMENT^Kommentar^LN||Campylobacter jejuni påvist. Anmeldelsespligtig. Ciprofloxacin-resistent.||||||F
```

---

## 12. ORM^O01 - Clostridium difficile test-rekvisition (C. diff test order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|MADS|SSI|20260411091000||ORM^O01|MADS00012|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1108801759^^^CPR^NNDN||Frandsen^Kristian^Arne^^||19800811|M|||Kastetvej 240^^Taastrup^^2630^DK||^^PH^+4571426265
PV1||I|RH^MED^M4021^S01||||66006^Christiansen^Astrid^^^Dr.|||MED||||||||||RH202604110001
ORC|NW|ORD20260411001^EPIC||||||20260411091000|||66006^Christiansen^Astrid^^^Dr.
OBR|1|ORD20260411001^EPIC||CDIFF^Clostridioides difficile toksintest^LN|||20260411091000||||||Vandig diarré under antibiotikabehandling|66006^Christiansen^Astrid^^^Dr.
```

---

## 13. ORU^R01 - Clostridium difficile svar (C. diff result)

```
MSH|^~\&|MADS|SSI|EPIC|RIGSHOSPITALET|20260412101500||ORU^R01^ORU_R01|MADS00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1108801759^^^CPR^NNDN||Frandsen^Kristian^Arne^^||19800811|M|||Kastetvej 240^^Taastrup^^2630^DK||^^PH^+4571426265
PV1||I|RH^MED^M4021^S01||||66006^Christiansen^Astrid^^^Dr.|||MED||||||||||RH202604110001
ORC|RE|ORD20260411001^EPIC||||||20260412101500
OBR|1|ORD20260411001^EPIC||CDIFF^Clostridioides difficile toksintest^LN|||20260411091000||||||||66006^Christiansen^Astrid^^^Dr.||||||20260412101500|||F
OBX|1|CE|CDTOX^C. difficile toksin A/B^LN||POS^Positiv^LN|||A|||F
OBX|2|CE|CDGDH^C. difficile GDH antigen^LN||POS^Positiv^LN|||A|||F
OBX|3|TX|COMMENT^Kommentar^LN||Toksinproducerende Clostridioides difficile påvist. Behandling med vancomycin peroralt anbefales. Kontaktisolation påkrævet.||||||F
```

---

## 14. ORM^O01 - MRSA-screening-rekvisition (MRSA screening order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|MADS|SSI|20260413083000||ORM^O01|MADS00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103785032^^^CPR^NNDN||Olsen^Karen^Ellen^^||19780301|F|||Klosterstræde 67^^Brønshøj^^2700^DK||^^PH^+4596567646
PV1||I|AAUH^MED^301^A1||||77007^Mikkelsen^Grethe^^^Dr.|||MED||||||||||AAUH202604130001
ORC|NW|ORD20260413001^COLUMNA_CIS||||||20260413083000|||77007^Mikkelsen^Grethe^^^Dr.
OBR|1|ORD20260413001^COLUMNA_CIS||MRSA^MRSA-screening (næse, svælg, perineum)^LN|||20260413083000||||||Indlæggelsesscreening, tidligere udlandsophold|77007^Mikkelsen^Grethe^^^Dr.
```

---

## 15. ORU^R01 - MRSA-screeningssvar (MRSA screening result)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AALBORG_UH|20260415101500||ORU^R01^ORU_R01|MADS00015|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103785032^^^CPR^NNDN||Olsen^Karen^Ellen^^||19780301|F|||Klosterstræde 67^^Brønshøj^^2700^DK||^^PH^+4596567646
PV1||I|AAUH^MED^301^A1||||77007^Mikkelsen^Grethe^^^Dr.|||MED||||||||||AAUH202604130001
ORC|RE|ORD20260413001^COLUMNA_CIS||||||20260415101500
OBR|1|ORD20260413001^COLUMNA_CIS||MRSA^MRSA-screening (næse, svælg, perineum)^LN|||20260413083000||||||||77007^Mikkelsen^Grethe^^^Dr.||||||20260415101500|||F
OBX|1|CE|MRSA_NAESE^MRSA næsepodning^LN||NEG^Negativ^LN|||N|||F
OBX|2|CE|MRSA_SVAELG^MRSA svælgpodning^LN||NEG^Negativ^LN|||N|||F
OBX|3|CE|MRSA_PERI^MRSA perinealpodning^LN||NEG^Negativ^LN|||N|||F
OBX|4|TX|COMMENT^Kommentar^LN||Ingen MRSA påvist ved screening. Isolation kan ophæves.||||||F
```

---

## 16. ORU^R01 - Resistensrapport med PDF (susceptibility report with embedded PDF)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AALBORG_UH|20260403170000||ORU^R01^ORU_R01|MADS00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2507835855^^^CPR^NNDN||Bertelsen^Tobias^Helmer^^||19830725|M|||Grønnegade 102^^København V^^1620^DK||^^PH^+4558701247
PV1||I|AAUH^MED^302^B4||||12001^Bach^Ulla^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260401002^MADS||||||20260403170000
OBR|1|ORD20260401002^MADS||BCUL^Bloddyrkning - komplet resistensrapport^LN|||20260401200000||||||||12001^Bach^Ulla^^^Dr.||||||20260403170000|||F
OBX|1|ED|PDF^Resistensrapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 17. ORM^O01 - PCR-rekvisition - influenza/RSV (PCR order for influenza/RSV)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|MADS|SSI|20260416091000||ORM^O01|MADS00017|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2801902401^^^CPR^NNDN||Holm^Sebastian^Carsten^^||19900128|M|||Tolderlundsvej 58^^Lyngby^^2800^DK||^^CP^+4525346494
PV1||E|RH^AKM^AK101||||88008^Vinther^Vibeke^^^Dr.|||AKM||||||||||RH202604160001
ORC|NW|ORD20260416001^EPIC||||||20260416091000|||88008^Vinther^Vibeke^^^Dr.
OBR|1|ORD20260416001^EPIC||RESPPCR^Respiratorisk PCR-panel^LN|||20260416091000||||||Feber, hoste, myalgi, influenzasæson|88008^Vinther^Vibeke^^^Dr.
```

---

## 18. ORU^R01 - PCR-svar - influenza A positiv (PCR result - influenza A positive)

```
MSH|^~\&|MADS|SSI|EPIC|RIGSHOSPITALET|20260416161500||ORU^R01^ORU_R01|MADS00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2801902401^^^CPR^NNDN||Holm^Sebastian^Carsten^^||19900128|M|||Tolderlundsvej 58^^Lyngby^^2800^DK||^^CP^+4525346494
PV1||E|RH^AKM^AK101||||88008^Vinther^Vibeke^^^Dr.|||AKM||||||||||RH202604160001
ORC|RE|ORD20260416001^EPIC||||||20260416161500
OBR|1|ORD20260416001^EPIC||RESPPCR^Respiratorisk PCR-panel^LN|||20260416091000||||||||88008^Vinther^Vibeke^^^Dr.||||||20260416161500|||F
OBX|1|CE|INFA^Influenza A^LN||POS^Positiv^LN|||A|||F
OBX|2|CE|INFB^Influenza B^LN||NEG^Negativ^LN|||N|||F
OBX|3|CE|RSV^Respiratorisk syncytialvirus^LN||NEG^Negativ^LN|||N|||F
OBX|4|CE|SARS2^SARS-CoV-2^LN||NEG^Negativ^LN|||N|||F
OBX|5|TX|COMMENT^Kommentar^LN||Influenza A påvist. Dråbeisolation anbefales. Overvej oseltamivir ved indikation.||||||F
```

---

## 19. ORU^R01 - Molekylær typningsrapport med PDF (molecular typing report with embedded PDF)

```
MSH|^~\&|MADS|SSI|BCC|OUH|20260418100000||ORU^R01^ORU_R01|MADS00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0707651518^^^CPR^NNDN||Knudsen^Astrid^Gerda^^||19650707|F|||Rådhusgade 168^^Brønshøj^^2700^DK||^^PH^+4579596798
PV1||I|OUH^KIR^C105^S02||||44004^Mikkelsen^Martin^^^Dr.|||KIR||||||||||OUH202604050001
ORC|RE|ORD20260418001^MADS||||||20260418100000
OBR|1|ORD20260418001^MADS||MRSATYP^MRSA molekylær typning^LN|||20260407161500||||||||44004^Mikkelsen^Martin^^^Dr.||||||20260418100000|||F
OBX|1|TX|MRSATYPE^MRSA spa-type^LN||spa-type t032, MLST ST22, SCCmec type IV. UK-EMRSA-15 klon.||||||F
OBX|2|ED|PDF^Typningsrapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 20. ORU^R01 - Bloddyrkning - negativ (negative blood culture result)

```
MSH|^~\&|MADS|SSI|EPIC|RIGSHOSPITALET|20260420161500||ORU^R01^ORU_R01|MADS00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1207891904^^^CPR^NNDN||Clausen^Rikke^Asta^^||19890712|F|||Munkerisvej 190^^Hillerød^^3400^DK||^^PH^+4561409262
PV1||I|RH^HÆMA^H3041^S01||||33003^Christensen^Charlotte^^^Dr.|||HÆMA||||||||||RH202604030001
ORC|RE|ORD20260420001^EPIC||||||20260420161500
OBR|1|ORD20260420001^EPIC||BCUL^Bloddyrkning^LN|||20260418200000||||||||33003^Christensen^Charlotte^^^Dr.||||||20260420161500|||F
OBX|1|TX|BCRESULT^Bloddyrkningsresultat^LN||Ingen vækst efter 5 dages inkubation. Bloddyrkningen er negativ.||||||F
```
