# DIPS Interactor - real HL7v2 ER7 messages

---

## 1. MDM^T02 - Epikrise (discharge summary) with embedded PDF

```
MSH|^~\&|INTERACTOR|AHUS_HF|NHN_EDI|NHN|20260314093012||MDM^T02|MSG00001|P|2.4|||AL|NE||8859/1
EVN|T02|20260314093012
PID|1||13028749832^^^AHUS_HF^PI||HANSEN^KARI^ELISABETH||19870213|F|||Trondheimsveien 44^^Oslo^^0560^NO||+4792345678
PV1|1|I|MED4^412^01^AHUS_HF||||87654^LARSEN^ERIK^ANDREAS^^^DR|||MED||||ADM||12345^BERG^ASTRID^^^DR|IP||||||||||||||||||AHUS_HF|||||20260310080000|20260314090000
TXA|1|EP^Epikrise|TX|20260314093012|87654^LARSEN^ERIK^ANDREAS^^^DR||20260314093012|||||DOC-20260314-00123||||AU|||AV
OBX|1|ED|PDF^Epikrise||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEVwaWtyaXNlIC0gS2FyaSBIYW5zZW4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0NjAKJSVFT0YK||||||F
```

---

## 2. MDM^T01 - Original document notification for operasjonsbeskrivelse

```
MSH|^~\&|INTERACTOR|UNN_HF|DIPS_ARENA|UNN_HF|20260221141530||MDM^T01|MSG00002|P|2.4|||AL|NE||8859/1
EVN|T01|20260221141530
PID|1||05076198234^^^UNN_HF^PI||JOHANSEN^OLE^KRISTIAN||19610705|M|||Hansjordnesgata 12^^Tromsø^^9007^NO||+4777318452
PV1|1|I|KIR2^205^01^UNN_HF||||34567^NILSEN^HANNE^MARIE^^^DR|||KIR||||ADM||23456^OLSEN^PER^^^DR|IP||||||||||||||||||UNN_HF|||||20260219100000|20260221130000
TXA|1|OP^Operasjonsbeskrivelse|TX|20260221141530|34567^NILSEN^HANNE^MARIE^^^DR||20260221141530|||||DOC-20260221-00456||||AU|||AV
OBX|1|TX|OPR^Operasjonsbeskrivelse||Laparoskopisk kolecystektomi utført uten komplikasjoner. Galleblæren ble identifisert og dissekert fri fra leversengen. Ductus cysticus og a. cystica ble klippet og delt. Galleblæren ble fjernet i endobag gjennom umbilikalport. Hemostase sikret. Fascie lukket med Vicryl 0.||||||F
```

---

## 3. ADT^A01 - Innleggelse medisinsk avdeling Haukeland

```
MSH|^~\&|DIPS_INT|HAUK_HF|NHN_EDI|NHN|20260108102045||ADT^A01|MSG00003|P|2.4|||AL|NE||8859/1
EVN|A01|20260108102045
PID|1||14039256789^^^HAUK_HF^PI||MÆLAND^ANNE^SOFIE||19920314|F|||Damsgårdsveien 88^^Bergen^^5058^NO||+4755438217
NK1|1|MÆLAND^BJØRN||Damsgårdsveien 88^^Bergen^^5058^NO|+4755438218||SPOUSE
PV1|1|I|MED1^308^02^HAUK_HF||||56789^ØDEGÅRD^THOMAS^^^DR|||MED||||EM||45678^BREIVIK^SILJE^^^DR|IP||||||||||||||||||HAUK_HF|||||20260108102045
PV2|||PNEUMONI^Pneumoni, uspesifisert^ICD-10-NO
DG1|1||J18.9^Pneumoni, uspesifisert^ICD-10-NO||20260108|A
IN1|1|HEL^Helfo^L|1234|Helfo||||||||||||||||||||||||||||||||||||NO
```

---

## 4. ORU^R01 - Sykepleienotat fra Nordlandssykehuset

```
MSH|^~\&|INTERACTOR|NLSH_HF|DIPS_ARENA|NLSH_HF|20260415160230||ORU^R01|MSG00004|P|2.4|||AL|NE||8859/1
PID|1||20115534567^^^NLSH_HF^PI||PEDERSEN^BERIT^MARIE||19551120|F|||Storgata 22^^Bodø^^8006^NO||+4775283419
PV1|1|I|GER1^112^01^NLSH_HF||||67890^STRAND^VEGARD^^^SYKEPLEIER|||GER||||ADM||78901^HAUGEN^METTE^^^DR|IP||||||||||||||||||NLSH_HF|||||20260412090000
ORC|RE|ORD-20260415-001|FIL-20260415-001||CM
OBR|1|ORD-20260415-001|FIL-20260415-001|SYK^Sykepleienotat^L|||20260415160230
OBX|1|TX|SYKNOTAT^Sykepleienotat||Pasienten er i dag mer våken og orientert. Spiser og drikker selv. Mobilisert til stol ved sengen med hjelp av to pleiere. Smerter VAS 3/10 i ro, 5/10 ved mobilisering. Gitt Paracetamol 1g per os med god effekt. Plan: Fortsette mobilisering, vurdere utskrivelse i morgen.||||||F
```

---

## 5. ADT^A03 - Utskrivelse fra St. Olavs Hospital

```
MSH|^~\&|DIPS_INT|STOLAV_HF|NHN_EDI|NHN|20260522083000||ADT^A03|MSG00005|P|2.4|||AL|NE||8859/1
EVN|A03|20260522083000
PID|1||01068845123^^^STOLAV_HF^PI||SØRENSEN^LARS^PETTER||19880601|M|||Innherredsveien 15^^Trondheim^^7044^NO||+4773529846
PV1|1|I|ORT1^501^01^STOLAV_HF||||89012^GRØNLIE^TONE^KRISTIN^^^DR|||ORT||||ADM||90123^TANGEN^FREDRIK^^^DR|IP||||||||||||||||||STOLAV_HF|||||20260518140000|20260522083000
DG1|1||S72.0^Fractura colli femoris^ICD-10-NO||20260518|A
DG1|2||Z96.6^Tilstedeværelse av ortopedisk leddimplantat^ICD-10-NO||20260520|A
PR1|1||NFB20^Innsetting av totalprotese i hofteledd^NCSP||20260519100000|||||89012^GRØNLIE^TONE^KRISTIN^^^DR
```

---

## 6. MDM^T02 - Poliklinisk notat med klinisk innhold

```
MSH|^~\&|INTERACTOR|OUS_HF|DIPS_ARENA|OUS_HF|20260203113045||MDM^T02|MSG00006|P|2.4|||AL|NE||8859/1
EVN|T02|20260203113045
PID|1||15047823456^^^OUS_HF^PI||BJØRNSTAD^HILDE^MARGRETHE||19780415|F|||Bygdøy allé 55^^Oslo^^0265^NO||+4722619843
PV1|1|O|REV1^POL^01^OUS_HF||||12340^AASHEIM^MORTEN^^^DR|||REV||||REF||11234^DAHL^ELISE^^^DR|OP||||||||||||||||||OUS_HF|||||20260203110000
TXA|1|PN^Poliklinisk notat|TX|20260203113045|12340^AASHEIM^MORTEN^^^DR||20260203113045|||||DOC-20260203-00789||||AU|||AV
OBX|1|TX|POLNOT^Poliklinisk notat||Kontroll revmatologisk poliklinikk. Pasienten har kjent RA siden 2019, behandles med metotreksat 15 mg/uke og folsyre. Klinisk undersøkelse viser ingen hovne ledd, god gripestyrke bilateralt. CRP 4, SR 8. DAS28-CRP 1.9 - lav sykdomsaktivitet. Fortsetter uendret behandling. Ny kontroll om 6 måneder.||||||F
```

---

## 7. ADT^A04 - Poliklinisk registrering Stavanger

```
MSH|^~\&|DIPS_INT|SUS_HF|NHN_EDI|NHN|20260617090100||ADT^A04|MSG00007|P|2.4|||AL|NE||8859/1
EVN|A04|20260617090100
PID|1||28129067890^^^SUS_HF^PI||THORSEN^GUNNAR^OLAV||19901228|M|||Hetlandsgata 33^^Stavanger^^4014^NO||+4751386192
PV1|1|O|ØNH1^POL^01^SUS_HF||||23451^KVAMME^RAGNHILD^^^DR|||ØNH||||REF||34562^JØRGENSEN^KARL^^^DR|OP||||||||||||||||||SUS_HF|||||20260617090100
DG1|1||J32.0^Kronisk sinusitt maxillaris^ICD-10-NO||20260617|A
```

---

## 8. ORM^O01 - Henvisning fra fastlege via Interactor

```
MSH|^~\&|INTERACTOR|AHUS_HF|DIPS_ARENA|AHUS_HF|20260509141200||ORM^O01|MSG00008|P|2.4|||AL|NE||8859/1
PID|1||09058412345^^^AHUS_HF^PI||ANDERSEN^MARIT^ELLEN||19840509|F|||Strømsveien 120^^Lørenskog^^1473^NO||+4741267184
PV1|1|R|HEN^REF^01^AHUS_HF||||45673^LUND^STEINAR^^^DR|||HEN||||REF|||OP||||||||||||||||||AHUS_HF|||||20260509141200
ORC|NW|REF-20260509-001||||||20260509141200|||45673^LUND^STEINAR^^^DR
OBR|1|REF-20260509-001||HENV^Henvisning^L|||20260509141200||||||||45673^LUND^STEINAR^^^DR
OBX|1|TX|HENV^Henvisningstekst||Pasienten henvises til gastromedisinsk poliklinikk for utredning av jernmangelanemi. Hb 9.8 g/dL, ferritin 5 ug/L. Har hatt gradvis vekttap siste 3 mnd ca. 5 kg. Avføringsprøve positiv for okkult blod x3. Ønsker koloskopi.||||||F
```

---

## 9. MDM^T01 - Notification for anestesinotat

```
MSH|^~\&|INTERACTOR|UNN_HF|DIPS_ARENA|UNN_HF|20260330081500||MDM^T01|MSG00009|P|2.4|||AL|NE||8859/1
EVN|T01|20260330081500
PID|1||17036712345^^^UNN_HF^PI||KARLSEN^TROND^IVAR||19670317|M|||Solligata 7^^Tromsø^^9012^NO||+4777845632
PV1|1|I|KIR1^OP3^01^UNN_HF||||56784^VIKSE^BERIT^ANITA^^^DR|||ANE||||ADM||67895^HENRIKSEN^RUNE^^^DR|IP||||||||||||||||||UNN_HF|||||20260330060000
TXA|1|AN^Anestesinotat|TX|20260330081500|56784^VIKSE^BERIT^ANITA^^^DR||20260330081500|||||DOC-20260330-00234||||AU|||AV
OBX|1|TX|ANENOTAT^Anestesinotat||Generell anestesi med endotrakeal intubasjon. Induksjon: Propofol 200 mg, Fentanyl 150 mcg, Rocuronium 50 mg. Vedlikehold: Sevofluran 1.5-2.0 MAC i O2/luft. Hemodynamisk stabil gjennom hele inngrepet. Estimert blodtap 200 ml. Ekstubert våken, SaO2 98% på romluft.||||||F
```

---

## 10. ORU^R01 - Klinisk notat indremedisin Sørlandet

```
MSH|^~\&|INTERACTOR|SSHF|DIPS_ARENA|SSHF|20260128153000||ORU^R01|MSG00010|P|2.4|||AL|NE||8859/1
PID|1||22079534567^^^SSHF^PI||GUNDERSEN^SILJE^IRENE||19950722|F|||Festningsgata 19^^Kristiansand^^4612^NO||+4738197542
PV1|1|I|MED2^210^01^SSHF||||78906^FREDRIKSEN^JAN^OLAV^^^DR|||MED||||EM||89017^EIDE^MARIANNE^^^DR|IP||||||||||||||||||SSHF|||||20260126180000
ORC|RE|ORD-20260128-002|FIL-20260128-002||CM
OBR|1|ORD-20260128-002|FIL-20260128-002|KN^Klinisk notat^L|||20260128153000
OBX|1|TX|KLINNOTAT^Klinisk notat||Dag 3 av innleggelse for diabetisk ketoacidose. pH normalisert til 7.38, bikarbonat 22 mmol/L. Glukose stabil mellom 8-12 mmol/L på insulindrypp. Overført til subkutan insulin: Lantus 24 IE kveld, NovoRapid etter karbohydratvurdering. Ketoner i urin negativ. Plan: Diabetessykepleier for opplæring, ernæringsfysiolog, utskrivelse overmorgen.||||||F
```

---

## 11. ADT^A08 - Oppdatering av pasientinformasjon

```
MSH|^~\&|DIPS_INT|HAUK_HF|NHN_EDI|NHN|20260704121500||ADT^A08|MSG00011|P|2.4|||AL|NE||8859/1
EVN|A08|20260704121500
PID|1||30069078901^^^HAUK_HF^PI||ØDEGAARD^VIBEKE^ANETTE||19900630|F|||Ibsens gate 5^^Bergen^^5052^NO||+4755418367||N||||||30069078901^^^FOLKEREG^NN
PV1|1|I|GYN1^405^01^HAUK_HF||||90128^BAKKE^HELENE^MARIE^^^DR|||GYN||||ADM||01239^SVENDSEN^TERJE^^^DR|IP||||||||||||||||||HAUK_HF|||||20260702080000
```

---

## 12. MDM^T02 - Epikrise psykiatri med innhold

```
MSH|^~\&|INTERACTOR|AHUS_HF|NHN_EDI|NHN|20260819100000||MDM^T02|MSG00012|P|2.4|||AL|NE||8859/1
EVN|T02|20260819100000
PID|1||11118956789^^^AHUS_HF^PI||LIE^JONAS^ALEXANDER||19891111|M|||Akersbakken 72^^Oslo^^0172^NO||+4793461285
PV1|1|I|PSY2^308^01^AHUS_HF||||23452^SKJELBRED^INGRID^^^DR|||PSY||||ADM||34563^AASEN^ROLF^^^DR|IP||||||||||||||||||AHUS_HF|||||20260801120000|20260819093000
TXA|1|EP^Epikrise|TX|20260819100000|23452^SKJELBRED^INGRID^^^DR||20260819100000|||||DOC-20260819-00567||||AU|||AV
OBX|1|TX|EPIKR^Epikrise||Innlagt psykiatrisk avdeling i 18 dager grunnet alvorlig depressiv episode med suicidale tanker. Behandlet med Sertralin 100 mg opptrappet til 150 mg, samt individuell samtaleterapi og miljøterapi. Gradvis bedring av stemningsleie og søvnmønster. Suicidalvurdering ved utskrivelse: ingen aktive planer eller intensjon. Videre oppfølging: DPS Groruddalen innen en uke, fastlege for medikamentoppfølging.||||||F
```

---

## 13. ORM^O01 - Røntgenrekvisisjon fra kliniker

```
MSH|^~\&|INTERACTOR|OUS_HF|RIS|OUS_HF|20260911083000||ORM^O01|MSG00013|P|2.4|||AL|NE||8859/1
PID|1||04025678901^^^OUS_HF^PI||HAUGEN^MARIT^SOLVEIG||19560204|F|||Ekebergveien 48^^Oslo^^1162^NO||+4722364195
PV1|1|O|LUN1^POL^01^OUS_HF||||45674^RØNNING^SVERRE^^^DR|||LUN||||REF|||OP||||||||||||||||||OUS_HF|||||20260911083000
ORC|NW|RAD-20260911-001||||||20260911083000|||45674^RØNNING^SVERRE^^^DR
OBR|1|RAD-20260911-001||RXTHORAX^Røntgen thorax^L|||20260911083000||||||||45674^RØNNING^SVERRE^^^DR
NTE|1||Kontroll etter 6 ukers antibiotikakur for pneumoni. Tidligere røntgen viste venstresidig infiltrat. Ber om vurdering av regress.
```

---

## 14. ADT^A01 - Akuttinnleggelse Universitetssykehuset Nord-Norge

```
MSH|^~\&|DIPS_INT|UNN_HF|NHN_EDI|NHN|20260123221530||ADT^A01|MSG00014|P|2.4|||AL|NE||8859/1
EVN|A01|20260123221530
PID|1||25078534567^^^UNN_HF^PI||NÆSS^HENRIK^JOHAN||19850725|M|||Stakkevollvegen 28^^Tromsø^^9010^NO||+4777392184
NK1|1|NÆSS^TONE||Stakkevollvegen 28^^Tromsø^^9010^NO|+4777392185||SPOUSE
PV1|1|E|AKU1^101^01^UNN_HF||||56785^MOEN^CAMILLA^^^DR|||AKU||||EM|||EP||||||||||||||||||UNN_HF|||||20260123221530
DG1|1||I21.0^Akutt transmuralt hjerteinfarkt i fremre vegg^ICD-10-NO||20260123|A
DG1|2||I25.1^Aterosklerotisk hjertesykdom^ICD-10-NO||20260123|A
```

---

## 15. MDM^T02 - Operasjonsbeskrivelse med embedded PDF

```
MSH|^~\&|INTERACTOR|SUS_HF|NHN_EDI|NHN|20260407144500||MDM^T02|MSG00015|P|2.4|||AL|NE||8859/1
EVN|T02|20260407144500
PID|1||08039145678^^^SUS_HF^PI||VÅGE^TURID^KRISTINE||19910308|F|||Sandvigå 16^^Stavanger^^4007^NO||+4751624378
PV1|1|I|KIR3^OP1^01^SUS_HF||||67896^AASE^MAGNUS^EINAR^^^DR|||KIR||||ADM||78907^DALE^SIRI^^^DR|IP||||||||||||||||||SUS_HF|||||20260407070000
TXA|1|OP^Operasjonsbeskrivelse|TX|20260407144500|67896^AASE^MAGNUS^EINAR^^^DR||20260407144500|||||DOC-20260407-00345||||AU|||AV
OBX|1|ED|PDF^Operasjonsbeskrivelse||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1OAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE9wZXJhc2pvbnNiZXNrcml2ZWxzZSAtIFR1cmlkIFbDpWdlKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNDcwCiUlRU9GCg==||||||F
```

---

## 16. ORU^R01 - Poliklinisk notat kardiologi

```
MSH|^~\&|INTERACTOR|OUS_HF|DIPS_ARENA|OUS_HF|20260610140000||ORU^R01|MSG00016|P|2.4|||AL|NE||8859/1
PID|1||19044523456^^^OUS_HF^PI||BREKKE^ARNE^MAGNUS||19450419|M|||Holmenkollveien 21^^Oslo^^0784^NO||+4722748391
PV1|1|O|KAR1^POL^01^OUS_HF||||89018^VIK^TONE^ELISABETH^^^DR|||KAR||||REF||90129^HOLM^ANDERS^^^DR|OP||||||||||||||||||OUS_HF|||||20260610133000
ORC|RE|ORD-20260610-003|FIL-20260610-003||CM
OBR|1|ORD-20260610-003|FIL-20260610-003|PN^Poliklinisk notat^L|||20260610140000
OBX|1|TX|POLNOT^Poliklinisk notat||Kontroll etter PCI med stentinnleggelse i LAD for 3 måneder siden. Pasienten er symptomfri, ingen brystsmerter eller dyspne. EKG viser sinusrytme, frekvens 62/min, ingen ST-forandringer. Ekko: EF 55%, ingen veggbevegelsesforstyrrelse. Medikamenter: ASA 75 mg, Brilique 90 mg x2 (seponeres om 9 mnd), Atorvastatin 80 mg, Ramipril 5 mg, Metoprolol 50 mg. Ny kontroll om 6 måneder med arbeids-EKG.||||||F
```

---

## 17. ADT^A03 - Utskrivelse nyfødtavdeling

```
MSH|^~\&|DIPS_INT|HAUK_HF|NHN_EDI|NHN|20260228103000||ADT^A03|MSG00017|P|2.4|||AL|NE||8859/1
EVN|A03|20260228103000
PID|1||15022634567^^^HAUK_HF^PI||TØNNESSEN^EMMA^SOFIE||20260215|F|||Sandviksveien 6^^Bergen^^5036^NO||+4755127389
NK1|1|TØNNESSEN^MONA^IRENE||Sandviksveien 6^^Bergen^^5036^NO|+4755127390||MOTHER
PV1|1|I|NEO1^101^01^HAUK_HF||||01230^SØVIK^ODDBJØRN^^^DR|||PED||||ADM||12341^GILJE^GRETE^HELEN^^^DR|IP||||||||||||||||||HAUK_HF|||||20260215120000|20260228103000
DG1|1||P07.3^Andre premature barn^ICD-10-NO||20260215|A
DG1|2||P22.0^Respiratorisk distress-syndrom hos nyfødt^ICD-10-NO||20260215|A
```

---

## 18. MDM^T01 - Notification for henvisning til DPS

```
MSH|^~\&|INTERACTOR|NLSH_HF|DIPS_ARENA|NLSH_HF|20260505091500||MDM^T01|MSG00018|P|2.4|||AL|NE||8859/1
EVN|T01|20260505091500
PID|1||12128267890^^^NLSH_HF^PI||AMUNDSEN^HILDE^KATRINE||19821212|F|||Bankgata 14^^Bodø^^8005^NO||+4775562431
PV1|1|O|PSY1^POL^01^NLSH_HF||||23453^LUNDE^GEIR^ARNE^^^DR|||PSY||||REF|||OP||||||||||||||||||NLSH_HF|||||20260505091500
TXA|1|HV^Henvisning|TX|20260505091500|23453^LUNDE^GEIR^ARNE^^^DR||20260505091500|||||DOC-20260505-00678||||AU|||AV
OBX|1|TX|HENV^Henvisningstekst||Henvises DPS for utredning og behandling av angstlidelse. Pasienten har hatt tiltagende angstplager siste 6 måneder med panikkanfall 2-3 ganger ukentlig, unngåelsesatferd og søvnvansker. GAD-7 score 16 (alvorlig). Har forsøkt Escitalopram 10 mg i 8 uker uten tilstrekkelig effekt. Ber om vurdering for kognitiv terapi og eventuell medikamentjustering.||||||F
```

---

## 19. ADT^A08 - Oppdatering av diagnose under innleggelse

```
MSH|^~\&|DIPS_INT|STOLAV_HF|NHN_EDI|NHN|20260916143000||ADT^A08|MSG00019|P|2.4|||AL|NE||8859/1
EVN|A08|20260916143000
PID|1||03057045678^^^STOLAV_HF^PI||LØNNING^BJØRG^HELENE||19700503|F|||Munkegata 44^^Trondheim^^7011^NO||+4773894231
PV1|1|I|NEV1^302^01^STOLAV_HF||||34564^HAGEN^PETTER^ANDRE^^^DR|||NEV||||EM||45675^SKOGLUND^ELLEN^^^DR|IP||||||||||||||||||STOLAV_HF|||||20260914200000
DG1|1||G45.9^Transitorisk cerebral iskemisk attakk, uspesifisert^ICD-10-NO||20260914|A
DG1|2||I10^Essensiell (primær) hypertensjon^ICD-10-NO||20260914|A
DG1|3||E11.9^Diabetes mellitus type 2 uten komplikasjoner^ICD-10-NO||20260914|A
```

---

## 20. ORU^R01 - Epikrise sendt som klinisk resultat

```
MSH|^~\&|INTERACTOR|SUS_HF|NHN_EDI|NHN|20260801120000||ORU^R01|MSG00020|P|2.4|||AL|NE||8859/1
PID|1||24039378901^^^SUS_HF^PI||ÅLGÅRD^SVEIN^ROALD||19930324|M|||Eiganesveien 8^^Stavanger^^4009^NO||+4751867432
PV1|1|I|MED3^215^01^SUS_HF||||56786^NORDBØ^LINE^MARIE^^^DR|||MED||||ADM||67897^VESTBØ^KNUT^^^DR|IP||||||||||||||||||SUS_HF|||||20260727140000|20260801110000
ORC|RE|ORD-20260801-004|FIL-20260801-004||CM
OBR|1|ORD-20260801-004|FIL-20260801-004|EP^Epikrise^L|||20260801120000
OBX|1|TX|EPIKR^Epikrise||Innlagt grunnet akutt forverring av ulcerøs kolitt. Ved innkomst: blodig diaré 8-10 ganger daglig, CRP 89, Hb 10.2. Behandlet med iv metylprednisolon 40 mg x2 i 5 dager med god respons. Gradvis overgang til peroral Prednisolon 40 mg med nedtrapping over 8 uker. Infliximab induksjonsbehandling startet dag 3, andre dose planlagt om 2 uker poliklinisk. Ved utskrivelse: 2-3 avføringer daglig uten blod, CRP 12. Kontroll gastromedisinsk poliklinikk om 2 uker for infliximab dose 2.||||||F
```
