# DIPS Arena

---

## 1. ADT^A01 - innleggelse (inpatient admission)

```
MSH|^~\&|DIPS|OUS_ULLEVAAL|NHN_EDI|HELSE_SOROST|20260312081500||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE||8859/1
EVN|A01|20260312081500
PID|||12036812345^^^OUS^PI||Gulbrandsen^Tore^Birger^^||19680312|M|||Waldemar Thranes gate 14^^Oslo^^0171||^^PH^22745891
NK1|1|Gulbrandsen^Randi||^^PH^93184267||N
PV1||I|MED3^Rom 412^Seng 1^Medisinsk avdeling||||LEG200^Fjellstad^Astrid^^^Dr.||MED||||7|||LEG200^Fjellstad^Astrid^^^Dr.|||||||||||||||||||V||||||20260312081500
IN1|1|HEL01^^HELFO|HELFO|||||||||||||||||||||||||||||||1
```

---

## 2. ADT^A04 - poliklinisk registrering (outpatient registration)

```
MSH|^~\&|DIPSARENA|HAUKELAND_HUS|NHN_EDI|HELSE_VEST|20260314093000||ADT^A04^ADT_A01|MSG00002|P|2.4|||AL|NE||8859/1
EVN|A04|20260314093000
PID|||14025623456^^^HUS^PI||Tveit^Ingrid^Solveig^^||19780214|F|||Møhlenpris allé 22^^Bergen^^5006||^^PH^55329841
PV1||O|ØYE1^Poliklinikk 3^^Øyeavdelingen||||LEG301^Kværnø^Per^^^Dr.||ØYE||||1|||LEG301^Kværnø^Per^^^Dr.|||||||||||||||||||V||||||20260314093000
PV2|||ØYE^Kontroll etter kataraktoperasjon
```

---

## 3. ADT^A03 - utskrivning (discharge)

```
MSH|^~\&|DIPS|STOLAVS|NHN_EDI|HELSE_MIDT|20260316140000||ADT^A03^ADT_A03|MSG00003|P|2.4|||AL|NE||8859/1
EVN|A03|20260316140000
PID|||16117812345^^^STOLAV^PI||Vangen^Bjørn^Arne^^||19651116|M|||Bispegata 8^^Trondheim^^7012||^^PH^73503214
PV1||I|KIR2^Rom 205^Seng 2^Kirurgisk avdeling||||LEG105^Haugland^Knut^^^Dr.||KIR||||7|||LEG105^Haugland^Knut^^^Dr.|||||||||||||||||||V||||||20260310093000|||20260316140000
DG1|1|ICD10|K40.9^Lyskebrokk, uspesifisert^ICD10||20260310
```

---

## 4. ADT^A02 - overføring (transfer)

```
MSH|^~\&|DIPSARENA|AHUS|NHN_EDI|HELSE_SOROST|20260318110000||ADT^A02^ADT_A02|MSG00004|P|2.4|||AL|NE||8859/1
EVN|A02|20260318110000
PID|||18066923456^^^AHUS^PI||Ødegård^Hilde^Margrete^^||19690618|F|||Sinsenveien 5^^Oslo^^0572||^^PH^67451287
PV1||I|ORT1^Rom 308^Seng 1^Ortopedisk avdeling||||LEG410^Bøhler^Sigrid^^^Dr.||ORT||||7|||LEG410^Bøhler^Sigrid^^^Dr.|||||||||||||||||||V||||||20260315080000
PV2|||ORT^Overført fra akuttmottak til ortopedisk avdeling
```

---

## 5. ORM^O01 - laboratoriebestilling (lab order)

```
MSH|^~\&|DIPS|OUS_RIKSHOSP|LABSYSTEM|OUS_LAB|20260319084500||ORM^O01|MSG00005|P|2.4|||AL|NE||8859/1
PID|||19087612345^^^OUS^PI||Fossberg^Erik^Torbjørn^^||19870319|M|||Maridalsveien 31^^Oslo^^0461||^^PH^22769845
PV1||I|MED1^Rom 110^Seng 2^Medisinsk avdeling||||LEG520^Grøndahl^Lars^^^Dr.
ORC|NW|ORD5001^DIPS||||||20260319084500|||LEG520^Grøndahl^Lars^^^Dr.
OBR|1|ORD5001^DIPS||CBC^Hemoglobin, leukocytter, trombocytter^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.
OBR|2|ORD5001^DIPS||CRP^C-reaktivt protein^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.
OBR|3|ORD5001^DIPS||KREA^Kreatinin^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.
```

---

## 6. ORU^R01 - laboratoriesvar (lab result with OBX)

```
MSH|^~\&|LABSYSTEM|OUS_LAB|DIPS|OUS_RIKSHOSP|20260319112000||ORU^R01|MSG00006|P|2.4|||AL|NE||8859/1
PID|||19087612345^^^OUS^PI||Fossberg^Erik^Torbjørn^^||19870319|M|||Maridalsveien 31^^Oslo^^0461||^^PH^22769845
PV1||I|MED1^Rom 110^Seng 2^Medisinsk avdeling||||LEG520^Grøndahl^Lars^^^Dr.
ORC|RE|ORD5001^DIPS||||||20260319112000|||LEG520^Grøndahl^Lars^^^Dr.
OBR|1|ORD5001^DIPS||CBC^Hemoglobin, leukocytter, trombocytter^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.|||20260319112000
OBX|1|NM|HGB^Hemoglobin^NLK||14.2|g/dL|13.0-17.0|N|||F
OBX|2|NM|WBC^Leukocytter^NLK||7.8|10*9/L|4.0-11.0|N|||F
OBX|3|NM|PLT^Trombocytter^NLK||245|10*9/L|150-400|N|||F
OBR|2|ORD5001^DIPS||CRP^C-reaktivt protein^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.|||20260319112000
OBX|4|NM|CRP^C-reaktivt protein^NLK||12|mg/L|0-5|H|||F
OBR|3|ORD5001^DIPS||KREA^Kreatinin^NLK|||20260319084000||||||||LEG520^Grøndahl^Lars^^^Dr.|||20260319112000
OBX|5|NM|KREA^Kreatinin^NLK||88|umol/L|60-105|N|||F
```

---

## 7. ADT^A08 - oppdatering av pasientinformasjon (update patient info)

```
MSH|^~\&|DIPS|SUS|NHN_EDI|HELSE_VEST|20260320090000||ADT^A08^ADT_A01|MSG00007|P|2.4|||AL|NE||8859/1
EVN|A08|20260320090000
PID|||20038812345^^^SUS^PI||Brattli^Kari^Wenche^^||19880320|F|||Pedersgata 17^^Stavanger^^4013||^^PH^51568432~^^CP^48723451
PV1||O|MED2^Poliklinikk 1^^Medisinsk poliklinikk||||LEG620^Hovde^Morten^^^Dr.
```

---

## 8. SIU^S12 - timeavtale opprettet (schedule notification)

```
MSH|^~\&|DIPSARENA|UNN_TROMSO|NHN_EDI|HELSE_NORD|20260321100000||SIU^S12|MSG00008|P|2.4|||AL|NE||8859/1
SCH|APT8001^DIPS|||||RUTINEMESSIG^Rutinekontroll||30|MIN|^^30^20260402090000^20260402093000|||||LEG730^Aslaksen^Turid^^^Dr.||||BOOKED
PID|||21046723456^^^UNN^PI||Ellingsen^Stein^Ragnar^^||19670421|M|||Grønnegata 44^^Tromsø^^9008||^^PH^77654832
PV1||O|NEV1^Poliklinikk^^Nevrologisk avdeling||||LEG730^Aslaksen^Turid^^^Dr.
RGS|1|A
AIS|1|A|NEVKONS^Nevrologisk konsultasjon||20260402090000|30|MIN
AIL|1|A|NEV1^Konsultasjonsrom 3^^Nevrologisk avdeling
AIP|1|A|LEG730^Aslaksen^Turid^^^Dr.
```

---

## 9. MDM^T02 - epikrisevarsel med innhold (document notification with content)

```
MSH|^~\&|DIPS|OUS_ULLEVAAL|NHN_EDI|FASTLEGE_OSLO|20260322160000||MDM^T02|MSG00009|P|2.4|||AL|NE||8859/1
EVN|T02|20260322160000
PID|||22118834567^^^OUS^PI||Rønningen^Tone^Kristin^^||19881122|F|||Schweigaards gate 9^^Oslo^^0191||^^PH^22839145
PV1||I|MED3^Rom 412^Seng 1^Medisinsk avdeling||||LEG200^Fjellstad^Astrid^^^Dr.
TXA|1|EP^Epikrise|TX|20260322160000|LEG200^Fjellstad^Astrid^^^Dr.||20260322160000||||||DOC90001|||AU
OBX|1|ED|PDF^Epikrise^LOINC||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 10. ORM^O01 - røntgenbestilling (radiology order)

```
MSH|^~\&|DIPSARENA|HAUKELAND_HUS|PACS_RIS|HUS_RAD|20260323071500||ORM^O01|MSG00010|P|2.4|||AL|NE||8859/1
PID|||23059945678^^^HUS^PI||Knudsen^Geir^Anders^^||19990523|M|||Fjøsangerveien 58^^Bergen^^5054||^^PH^55619073
PV1||E|AKU1^Akuttmottak^^Akuttavdelingen||||LEG840^Skjærvik^Eva^^^Dr.
ORC|NW|ORD10001^DIPS||||||20260323071500|||LEG840^Skjærvik^Eva^^^Dr.
OBR|1|ORD10001^DIPS||XRTHORAX^Røntgen thorax^NLK|||20260323071000|||||Mistanke om pneumothorax etter fall|||LEG840^Skjærvik^Eva^^^Dr.||||||||||1
```

---

## 11. ORU^R01 - radiologisvar (radiology result with OBX)

```
MSH|^~\&|PACS_RIS|HUS_RAD|DIPSARENA|HAUKELAND_HUS|20260323093000||ORU^R01|MSG00011|P|2.4|||AL|NE||8859/1
PID|||23059945678^^^HUS^PI||Knudsen^Geir^Anders^^||19990523|M|||Fjøsangerveien 58^^Bergen^^5054||^^PH^55619073
PV1||E|AKU1^Akuttmottak^^Akuttavdelingen||||LEG840^Skjærvik^Eva^^^Dr.
ORC|RE|ORD10001^DIPS||||||20260323093000|||RAD910^Nøstdal^Helene^^^Dr.
OBR|1|ORD10001^DIPS||XRTHORAX^Røntgen thorax^NLK|||20260323071000||||||||LEG840^Skjærvik^Eva^^^Dr.|||20260323093000||||||F
OBX|1|TX|XRTHORAX^Røntgen thorax, vurdering^NLK||Frontal røntgen thorax utført. Ingen tegn til pneumothorax. Lungefelt uten infiltrater. Hjertestørrelse normal. Mediastinum uten patologiske funn. Konklusjon: Normalt røntgen thorax.||||||F
```

---

## 12. ADT^A31 - oppdatering av personopplysninger (update person information)

```
MSH|^~\&|DIPS|SORLANDET_SYK|NHN_EDI|FOLKEREG|20260324080000||ADT^A31^ADT_A05|MSG00012|P|2.4|||AL|NE||8859/1
EVN|A31|20260324080000
PID|||24037856789^^^SSK^PI||Thorkildsen^Ragnhild^Marie^^||19780324|F|||Vesterveien 12^^Kristiansand^^4613||^^PH^38192345~^^CP^41783214||N|||24037856789
```

---

## 13. ADT^A40 - sammenslåing av pasienter (merge patient)

```
MSH|^~\&|DIPSARENA|VESTRE_VIKEN|NHN_EDI|HELSE_SOROST|20260325113000||ADT^A40^ADT_A39|MSG00013|P|2.4|||AL|NE||8859/1
EVN|A40|20260325113000
PID|||25069067890^^^VVHF^PI||Lystad^Terje^Gunnar^^||19900625|M|||Treschows gate 12^^Drammen^^3044||^^PH^32456178
MRG|25069067899^^^VVHF^PI||||||Lystad^Terje^G^^
```

---

## 14. SIU^S14 - endring av timeavtale (schedule modification)

```
MSH|^~\&|DIPS|SYK_OSTFOLD|NHN_EDI|HELSE_SOROST|20260326140000||SIU^S14|MSG00014|P|2.4|||AL|NE||8859/1
SCH|APT14001^DIPS|||||RUTINEMESSIG^Kontroll||45|MIN|^^45^20260410100000^20260410104500|||||LEG150^Røssland^Rune^^^Dr.||||BOOKED
PID|||26028178901^^^SØ^PI||Melby^Wenche^Solveig^^||19810226|F|||Glommengata 33^^Fredrikstad^^1606||^^PH^69782134
PV1||O|GAS1^Poliklinikk^^Gastroenterologisk avdeling||||LEG150^Røssland^Rune^^^Dr.
RGS|1|A
AIS|1|A|GASKOL^Gastroskopikontroll||20260410100000|45|MIN
AIL|1|A|GAS1^Skoprom 2^^Gastroenterologisk avdeling
AIP|1|A|LEG150^Røssland^Rune^^^Dr.
```

---

## 15. ORU^R01 - mikrobiologisvar (microbiology result with OBX)

```
MSH|^~\&|MIKROLAB|STOLAVS_LAB|DIPS|STOLAVS|20260327151500||ORU^R01|MSG00015|P|2.4|||AL|NE||8859/1
PID|||27047089012^^^STOLAV^PI||Skogstad^Hans^Fredrik^^||19700427|M|||Klæbuveien 7^^Trondheim^^7031||^^PH^73482167
PV1||I|INF1^Rom 103^Seng 1^Infeksjonsavdelingen||||LEG440^Myrvang^Kirsten^^^Dr.
ORC|RE|ORD15001^DIPS||||||20260327151500|||LEG440^Myrvang^Kirsten^^^Dr.
OBR|1|ORD15001^DIPS||BLODK^Blodkultur^NLK|||20260325100000||||||||LEG440^Myrvang^Kirsten^^^Dr.|||20260327151500||||||F
OBX|1|TX|BLODK^Blodkultur, resultat^NLK||Vekst av Staphylococcus aureus i aerob flaske etter 18 timer. Meticillinfølsom (MSSA).||||||F
OBX|2|TX|BLODK^Blodkultur, resistens^NLK||Oksacillin: S, Vankomycin: S, Gentamicin: S, Klindamycin: S, Trimetoprim-sulfametoksazol: S||||||F
OBX|3|TX|BLODK^Blodkultur, kommentar^NLK||Anbefaler iv kloksacillin. Kontakt infeksjonsmedisiner for videre behandling.||||||F
```

---

## 16. ADT^A01 - innleggelse barn (pediatric admission)

```
MSH|^~\&|DIPSARENA|OUS_RIKSHOSP|NHN_EDI|HELSE_SOROST|20260328063000||ADT^A01^ADT_A01|MSG00016|P|2.4|||AL|NE||8859/1
EVN|A01|20260328063000
PID|||28121912345^^^OUS^PI||Åsland^Emilie^Sofie^^||20191228|F|||Sognsveien 40^^Oslo^^0855||^^PH^22571983
NK1|1|Åsland^Anders^Thomas||Sognsveien 40^^Oslo^^0855^^PH^22571983~^^CP^98432167||F
NK1|2|Åsland^Silje^Marie||Sognsveien 40^^Oslo^^0855^^PH^22571983~^^CP^91653284||M
PV1||I|BRN1^Rom 201^Seng 1^Barneavdelingen||||LEG550^Thorbjørnsen^Marte^^^Dr.||BRN||||7|||LEG550^Thorbjørnsen^Marte^^^Dr.|||||||||||||||||||V||||||20260328063000
DG1|1|ICD10|J18.9^Pneumoni, uspesifisert^ICD10||20260328
```

---

## 17. ORM^O01 - blodprøvebestilling fra poliklinikk (outpatient lab order)

```
MSH|^~\&|DIPS|UNN_TROMSO|LABSYSTEM|UNN_LAB|20260329083000||ORM^O01|MSG00017|P|2.4|||AL|NE||8859/1
PID|||29068201234^^^UNN^PI||Nygård^Sverre^Halvard^^||19820629|M|||Sjøgata 12^^Tromsø^^9008||^^PH^77194532
PV1||O|END1^Poliklinikk^^Endokrinologisk poliklinikk||||LEG660^Vassbotn^Grete^^^Dr.
ORC|NW|ORD17001^DIPS||||||20260329083000|||LEG660^Vassbotn^Grete^^^Dr.
OBR|1|ORD17001^DIPS||TSH^Thyreoideastimulerende hormon^NLK|||20260329082500||||||||LEG660^Vassbotn^Grete^^^Dr.
OBR|2|ORD17001^DIPS||FT4^Fritt tyroksin^NLK|||20260329082500||||||||LEG660^Vassbotn^Grete^^^Dr.
OBR|3|ORD17001^DIPS||HBA1C^Glykosylert hemoglobin^NLK|||20260329082500||||||||LEG660^Vassbotn^Grete^^^Dr.
OBR|4|ORD17001^DIPS||GLUK^Glukose, fastende^NLK|||20260329082500||||||||LEG660^Vassbotn^Grete^^^Dr.
```

---

## 18. MDM^T02 - operasjonsnotat med vedlegg (operative note with PDF attachment)

```
MSH|^~\&|DIPSARENA|AHUS|NHN_EDI|FASTLEGE_AKERSHUS|20260330120000||MDM^T02|MSG00018|P|2.4|||AL|NE||8859/1
EVN|T02|20260330120000
PID|||30047523456^^^AHUS^PI||Stenseth^Kari^Elisabeth^^||19750430|F|||Trondheimsveien 28^^Oslo^^0560||^^PH^67328914
PV1||I|KIR1^Rom 305^Seng 2^Kirurgisk avdeling||||LEG770^Falkenborg^Anders^^^Dr.
TXA|1|OP^Operasjonsnotat|TX|20260330120000|LEG770^Falkenborg^Anders^^^Dr.||20260330120000||||||DOC18001|||AU
OBX|1|ED|PDF^Operasjonsnotat^LOINC||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmDQowMDAwMDAwMDA5IDAwMDAwIG4NCjAwMDAwMDAwNTggMDAwMDAgbg0KMDAwMDAwMDE1MSAwMDAwMCBuDQp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjIwMgolJUVPRgo=||||||F
```

---

## 19. ADT^A03 - utskrivning med diagnoser (discharge with diagnoses)

```
MSH|^~\&|DIPS|SUS|NHN_EDI|HELSE_VEST|20260331150000||ADT^A03^ADT_A03|MSG00019|P|2.4|||AL|NE||8859/1
EVN|A03|20260331150000
PID|||31128634567^^^SUS^PI||Tveiten^Magnus^Petter^^||19860131|M|||Hillevågsveien 3^^Stavanger^^4016||^^PH^51294831
PV1||I|KAR1^Rom 501^Seng 1^Kardiologisk avdeling||||LEG880^Mjølhus^Henrik^^^Dr.||KAR||||7|||LEG880^Mjølhus^Henrik^^^Dr.|||||||||||||||||||V||||||20260326090000|||20260331150000
DG1|1|ICD10|I21.0^Akutt transmuralt hjerteinfarkt i fremre vegg^ICD10||20260326|A
DG1|2|ICD10|I25.1^Aterosklerotisk hjertesykdom^ICD10||20260326|S
DG1|3|ICD10|E11.9^Diabetes mellitus type 2 uten komplikasjoner^ICD10||20260326|S
PR1|1|NCSP|FNG02^Perkutan koronar intervensjon (PCI)^NCSP|20260326110000|||LEG880^Mjølhus^Henrik^^^Dr.
```

---

## 20. ORU^R01 - patologisvar med vedlegg (pathology result with PDF)

```
MSH|^~\&|PATOLOGI|OUS_RADIUM|DIPSARENA|OUS_ULLEVAAL|20260401091500||ORU^R01|MSG00020|P|2.4|||AL|NE||8859/1
PID|||01057745678^^^OUS^PI||Åmot^Liv^Turid^^||19770501|F|||Frognerveien 15^^Oslo^^0263||^^PH^22573896
PV1||O|ONK1^Poliklinikk^^Onkologisk avdeling||||LEG990^Løkken^Morten^^^Dr.
ORC|RE|ORD20001^DIPS||||||20260401091500|||PAT100^Grøttum^Sissel^^^Dr.
OBR|1|ORD20001^DIPS||BIOPSI^Biopsi, histopatologisk undersøkelse^NLK|||20260328140000||||||||LEG990^Løkken^Morten^^^Dr.|||20260401091500||||||F
OBX|1|TX|BIOPSI^Histopatologisk vurdering^NLK||Mottatt: Stansebiopsi fra venstre bryst. Makroskopi: To stansebiopsier, samlet lengde 12 mm. Mikroskopi: Invasivt duktalt karsinom, grad 2. ER-positiv, PR-positiv, HER2-negativ, Ki-67 15%.||||||F
OBX|2|ED|PDF^Patologisvar^LOINC||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMDIKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihQYXRvbG9naXN2YXIgLSBIaXN0b3BhdG9sb2dpc2sgdnVyZGVyaW5nKSBUagpFVAplbmRzdHJlYW0KZW5kb2Jq||||||F
```
