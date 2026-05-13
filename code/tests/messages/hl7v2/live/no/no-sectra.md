# Sectra RIS/PACS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CT thorax order from Oslo universitetssykehus

```
MSH|^~\&|SECTRA_RIS|OSLO_UNIV_SH|DIPS_ARENA|OSLO_UNIV_SH|20260312084512||ORM^O01^ORM_O01|MSG00001|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||12038549723^^^OSLO_UNIV_SH^PI||Nordberg^Ingrid^Marie||19850312|F|||Kirkeveien 42^^Oslo^^0364^NOR||+4722334455||NOR|U||VN00001|||||||N
PV1|1|O|RAD^CT01^01||||1234567^Haugen^Lars^Erik^^^dr.|||RAD||||1||REF|9876543^Olsen^Marte^^^^^dr.||VN00001|||||||||||||||||||||20260312
ORC|NW|ORD20260312001|FIL20260312001||SC|||1^^^20260312^^^^S||20260312084500|1234567^Haugen^Lars^Erik^^^dr.||9876543^Olsen^Marte^^^^^dr.|RAD^CT01^01
OBR|1|ORD20260312001|FIL20260312001|AA0AK^CT thorax med kontrast^NCRP||20260312084500|||||||||9876543^Olsen^Marte^^^^^dr.|||||||RAD||||^CT|||20260312^^^^S|||||||||||20260312
DG1|1|ICD10|J18.9^Pneumoni, uspesifisert^ICD10||20260312|A
```

---

## 2. ORM^O01 - MR caput order from Haukeland universitetssjukehus

```
MSH|^~\&|SECTRA_RIS|HAUKELAND_US|DIPS_ARENA|HAUKELAND_US|20260315101023||ORM^O01^ORM_O01|MSG00002|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||15067832145^^^HAUKELAND_US^PI||Bjørnstad^Anders^Kristian||19780615|M|||Nygårdsgaten 17^^Bergen^^5015^NOR||+4755223344||NOR|U||VN00002|||||||N
PV1|1|O|RAD^MR01^01||||2345678^Svendsen^Kari^Anne^^^dr.|||RAD||||1||REF|8765432^Eriksen^Per^^^^^dr.||VN00002|||||||||||||||||||||20260315
ORC|NW|ORD20260315001|FIL20260315001||SC|||1^^^20260315^^^^S||20260315101000|2345678^Svendsen^Kari^Anne^^^dr.||8765432^Eriksen^Per^^^^^dr.|RAD^MR01^01
OBR|1|ORD20260315001|FIL20260315001|AB1AA^MR caput uten kontrast^NCRP||20260315101000|||||||||8765432^Eriksen^Per^^^^^dr.|||||||RAD||||^MR|||20260315^^^^S|||||||||||20260315
DG1|1|ICD10|G43.9^Migrene, uspesifisert^ICD10||20260315|A
```

---

## 3. ORU^R01 - CT thorax result with findings

```
MSH|^~\&|SECTRA_RIS|OSLO_UNIV_SH|DIPS_ARENA|OSLO_UNIV_SH|20260312143022||ORU^R01^ORU_R01|MSG00003|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||12038549723^^^OSLO_UNIV_SH^PI||Nordberg^Ingrid^Marie||19850312|F|||Kirkeveien 42^^Oslo^^0364^NOR||+4722334455||NOR|U||VN00001|||||||N
PV1|1|O|RAD^CT01^01||||1234567^Haugen^Lars^Erik^^^dr.|||RAD||||1||REF|9876543^Olsen^Marte^^^^^dr.||VN00001|||||||||||||||||||||20260312
ORC|RE|ORD20260312001|FIL20260312001||CM||||||1234567^Haugen^Lars^Erik^^^dr.||9876543^Olsen^Marte^^^^^dr.|RAD^CT01^01
OBR|1|ORD20260312001|FIL20260312001|AA0AK^CT thorax med kontrast^NCRP||20260312084500|20260312090000||||||||9876543^Olsen^Marte^^^^^dr.||||||20260312143000|RAD||||^CT||1^^^20260312^^^^S|||||1234567^Haugen^Lars^Erik^^^dr.|||20260312143000
OBX|1|TX|^Klinisk informasjon||Hoste og feber i to uker. Mistanke om pneumoni.||||||F
OBX|2|TX|^Beskrivelse||Undersøkelse: CT thorax med intravenøs kontrast.\.br\\.br\Funn: Det ses et konsoliderende infiltrat i høyre underlapp forenlig med pneumoni. Ingen pleuraeffusjon. Ingen tegn til lungeemboli. Mediastinale strukturer er normale. Ingen patologisk forstørrede lymfeknuter.||||||F
OBX|3|TX|^Konklusjon||Høyresidig underlappsinfiltrat forenlig med pneumoni. Ingen tegn til komplikasjoner.||||||F
```

---

## 4. ADT^A04 - Outpatient registration for røntgen thorax at Stavanger

```
MSH|^~\&|DIPS_ARENA|STAVANGER_US|SECTRA_RIS|STAVANGER_US|20260318073015||ADT^A04^ADT_A01|MSG00004|P|2.5|||AL|NE||UNICODE UTF-8|||NO
EVN|A04|20260318073015|||ADMIN01^Pettersen^Hilde
PID|1||08099145632^^^STAVANGER_US^PI||Ødegård^Tone^Kristin||19910908|F|||Løkkeveien 33^^Stavanger^^4008^NOR||+4751667788||NOR|U||VN00004|||||||N
PV1|1|O|RAD^RTGN01^01||||3456789^Johannessen^Stein^^^^^dr.|||RAD||||1||REF|7654321^Andersen^Silje^^^^^dr.||VN00004|||||||||||||||||||||20260318
```

---

## 5. SIU^S12 - Scheduling CT abdomen at St. Olavs hospital

```
MSH|^~\&|SECTRA_RIS|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20260319091200||SIU^S12^SIU_S12|MSG00005|P|2.5|||AL|NE||UNICODE UTF-8|||NO
SCH|APT20260322001|APT20260322001|||AA0AH^CT abdomen med kontrast^NCRP|Planlagt|Normal|30|min|^^30^20260322100000^20260322103000||4567890^Lund^Berit^^^^^dr.||4567890^Lund^Berit^^^^^dr.|BOOKED|||4567890^Lund^Berit^^^^^dr.|
PID|1||22115678901^^^ST_OLAVS^PI||Aasen^Trond^Harald||19561122|M|||Munkegata 5^^Trondheim^^7013^NOR||+4773889900||NOR|U||VN00005|||||||N
AIS|1|A|AA0AH^CT abdomen med kontrast^NCRP|20260322100000||30|min
AIL|1|A|RAD^CT02^01^ST_OLAVS||||20260322100000||30|min
AIP|1|A|4567890^Lund^Berit^^^^^dr.|||||20260322100000||30|min
```

---

## 6. ORM^O01 - Ultralyd abdomen order from Akershus universitetssykehus

```
MSH|^~\&|SECTRA_RIS|AHUS|DIPS_ARENA|AHUS|20260320114530||ORM^O01^ORM_O01|MSG00006|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||01028834567^^^AHUS^PI||Grønlund^Eva^Solveig||19880201|F|||Storgata 12^^Lillestrøm^^2000^NOR||+4763112233||NOR|U||VN00006|||||||N
PV1|1|O|RAD^UL01^01||||5678901^Dahl^Henrik^Olav^^^dr.|||RAD||||1||REF|6543210^Berg^Kristine^^^^^dr.||VN00006|||||||||||||||||||||20260320
ORC|NW|ORD20260320001|FIL20260320001||SC|||1^^^20260321^^^^S||20260320114500|5678901^Dahl^Henrik^Olav^^^dr.||6543210^Berg^Kristine^^^^^dr.|RAD^UL01^01
OBR|1|ORD20260320001|FIL20260320001|AC1AE^Ultralyd abdomen^NCRP||20260320114500|||||||||6543210^Berg^Kristine^^^^^dr.|||||||RAD||||^US|||20260321^^^^S|||||||||||20260320
DG1|1|ICD10|R10.4^Andre og uspesifiserte magesmerter^ICD10||20260320|A
```

---

## 7. ORU^R01 - MR caput result with detailed findings from Haukeland

```
MSH|^~\&|SECTRA_RIS|HAUKELAND_US|DIPS_ARENA|HAUKELAND_US|20260316162045||ORU^R01^ORU_R01|MSG00007|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||15067832145^^^HAUKELAND_US^PI||Bjørnstad^Anders^Kristian||19780615|M|||Nygårdsgaten 17^^Bergen^^5015^NOR||+4755223344||NOR|U||VN00002|||||||N
PV1|1|O|RAD^MR01^01||||2345678^Svendsen^Kari^Anne^^^dr.|||RAD||||1||REF|8765432^Eriksen^Per^^^^^dr.||VN00002|||||||||||||||||||||20260316
ORC|RE|ORD20260315001|FIL20260315001||CM||||||2345678^Svendsen^Kari^Anne^^^dr.||8765432^Eriksen^Per^^^^^dr.|RAD^MR01^01
OBR|1|ORD20260315001|FIL20260315001|AB1AA^MR caput uten kontrast^NCRP||20260315101000|20260316150000||||||||8765432^Eriksen^Per^^^^^dr.||||||20260316162000|RAD||||^MR||1^^^20260315^^^^S|||||2345678^Svendsen^Kari^Anne^^^dr.|||20260316162000
OBX|1|TX|^Klinisk informasjon||Tilbakevendende hodepine med aura. Utelukke intrakraniell patologi.||||||F
OBX|2|TX|^Teknikk||MR caput uten kontrast. Sekvenser: T1, T2, FLAIR, DWI, SWI. Aksiale, koronale og sagittale plan.||||||F
OBX|3|TX|^Beskrivelse||Hjerneparenkymet viser normal signalintensitet. Ingen fokale lesjoner. Ventrikelsystemet er normalkalibret og symmetrisk. Midtlinjestrukturene er ikke forskjøvet. Ingen tegn til romoppfyllende prosess. Sella turcica og hypofysen er normale. Cerebellopontine vinkler uten patologi. Normale strømningsforhold i de store intrakranielle karene.||||||F
OBX|4|TX|^Konklusjon||Normalt MR-funn av hjernen. Ingen strukturell årsak til pasientens hodepine påvist.||||||F
```

---

## 8. ADT^A01 - Inpatient admission for akutt CT caput at UNN Tromsø

```
MSH|^~\&|DIPS_ARENA|UNN_TROMSO|SECTRA_RIS|UNN_TROMSO|20260321220145||ADT^A01^ADT_A01|MSG00008|P|2.5|||AL|NE||UNICODE UTF-8|||NO
EVN|A01|20260321220145|||ADMIN02^Nilsen^Ragnhild
PID|1||30047123456^^^UNN_TROMSO^PI||Henriksen^Eirik^Magnus||19710430|M|||Sjøgata 8^^Tromsø^^9008^NOR||+4777556677||NOR|U||VN00008|||||||N
NK1|1|Henriksen^Astrid^^|SPO|Sjøgata 8^^Tromsø^^9008^NOR|+4777556688
PV1|1|E|AKU^AKU01^01||||6789012^Solheim^Trygve^^^^^dr.|||AKU||||7||REF|5432109^Hansen^Lise^^^^^dr.||VN00008|||||||||||||||||||||20260321
```

---

## 9. ORM^O01 - Røntgen thorax order from Stavanger universitetssjukehus

```
MSH|^~\&|SECTRA_RIS|STAVANGER_US|DIPS_ARENA|STAVANGER_US|20260318074500||ORM^O01^ORM_O01|MSG00009|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||08099145632^^^STAVANGER_US^PI||Ødegård^Tone^Kristin||19910908|F|||Løkkeveien 33^^Stavanger^^4008^NOR||+4751667788||NOR|U||VN00004|||||||N
PV1|1|O|RAD^RTGN01^01||||3456789^Johannessen^Stein^^^^^dr.|||RAD||||1||REF|7654321^Andersen^Silje^^^^^dr.||VN00004|||||||||||||||||||||20260318
ORC|NW|ORD20260318001|FIL20260318001||SC|||1^^^20260318^^^^S||20260318074500|3456789^Johannessen^Stein^^^^^dr.||7654321^Andersen^Silje^^^^^dr.|RAD^RTGN01^01
OBR|1|ORD20260318001|FIL20260318001|AA0AA^Røntgen thorax^NCRP||20260318074500|||||||||7654321^Andersen^Silje^^^^^dr.|||||||RAD||||^CR|||20260318^^^^S|||||||||||20260318
DG1|1|ICD10|R05^Hoste^ICD10||20260318|A
```

---

## 10. ORU^R01 - Radiology result with ED datatype (base64 PDF report) from Oslo

```
MSH|^~\&|SECTRA_PACS|OSLO_UNIV_SH|NHN_EDI|NHN|20260313091500||ORU^R01^ORU_R01|MSG00010|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||12038549723^^^OSLO_UNIV_SH^PI||Nordberg^Ingrid^Marie||19850312|F|||Kirkeveien 42^^Oslo^^0364^NOR||+4722334455||NOR|U||VN00001|||||||N
PV1|1|O|RAD^CT01^01||||1234567^Haugen^Lars^Erik^^^dr.|||RAD||||1||REF|9876543^Olsen^Marte^^^^^dr.||VN00001|||||||||||||||||||||20260312
ORC|RE|ORD20260312001|FIL20260312001||CM||||||1234567^Haugen^Lars^Erik^^^dr.||9876543^Olsen^Marte^^^^^dr.|RAD^CT01^01
OBR|1|ORD20260312001|FIL20260312001|AA0AK^CT thorax med kontrast^NCRP||20260312084500|20260312090000||||||||9876543^Olsen^Marte^^^^^dr.||||||20260313091500|RAD||||^CT||1^^^20260312^^^^S|||||1234567^Haugen^Lars^Erik^^^dr.|||20260313091500
OBX|1|TX|^Konklusjon||Høyresidig underlappsinfiltrat forenlig med pneumoni.||||||F
OBX|2|ED|PDF^Radiologisk beskrivelse||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFJhZGlvbG9naXNrIGJlc2tyaXZlbHNlKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDE3MiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjI2NgolJUVPRgo=||||||F
```

---

## 11. SIU^S14 - Rescheduling MR kne appointment at Akershus

```
MSH|^~\&|SECTRA_RIS|AHUS|DIPS_ARENA|AHUS|20260322083000||SIU^S14^SIU_S12|MSG00011|P|2.5|||AL|NE||UNICODE UTF-8|||NO
SCH|APT20260325001|APT20260325001|||AB2CA^MR kne^NCRP|Endret|Normal|45|min|^^45^20260328093000^20260328101500||5678901^Dahl^Henrik^Olav^^^dr.||5678901^Dahl^Henrik^Olav^^^dr.|BOOKED|||5678901^Dahl^Henrik^Olav^^^dr.|
PID|1||14029945678^^^AHUS^PI||Solberg^Martin^Andreas||19990214|M|||Åsveien 7^^Jessheim^^2050^NOR||+4763445566||NOR|U||VN00011|||||||N
AIS|1|A|AB2CA^MR kne^NCRP|20260328093000||45|min
AIL|1|A|RAD^MR02^01^AHUS||||20260328093000||45|min
AIP|1|A|5678901^Dahl^Henrik^Olav^^^dr.|||||20260328093000||45|min
```

---

## 12. ORM^O01 - CT caput akutt order from UNN

```
MSH|^~\&|SECTRA_RIS|UNN_TROMSO|DIPS_ARENA|UNN_TROMSO|20260321221000||ORM^O01^ORM_O01|MSG00012|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||30047123456^^^UNN_TROMSO^PI||Henriksen^Eirik^Magnus||19710430|M|||Sjøgata 8^^Tromsø^^9008^NOR||+4777556677||NOR|U||VN00008|||||||N
PV1|1|E|AKU^AKU01^01||||6789012^Solheim^Trygve^^^^^dr.|||AKU||||7||REF|5432109^Hansen^Lise^^^^^dr.||VN00008|||||||||||||||||||||20260321
ORC|NW|ORD20260321001|FIL20260321001||SC|||1^^^20260321^^^^R||20260321221000|6789012^Solheim^Trygve^^^^^dr.||5432109^Hansen^Lise^^^^^dr.|AKU^AKU01^01
OBR|1|ORD20260321001|FIL20260321001|AA0AB^CT caput uten kontrast^NCRP||20260321221000|||||AKUTT||||5432109^Hansen^Lise^^^^^dr.|||||||RAD||||^CT|||20260321^^^^R|||||||||||20260321
DG1|1|ICD10|S06.9^Intrakraniell skade, uspesifisert^ICD10||20260321|A
```

---

## 13. ORU^R01 - Røntgen thorax result from Stavanger

```
MSH|^~\&|SECTRA_RIS|STAVANGER_US|DIPS_ARENA|STAVANGER_US|20260318112030||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||08099145632^^^STAVANGER_US^PI||Ødegård^Tone^Kristin||19910908|F|||Løkkeveien 33^^Stavanger^^4008^NOR||+4751667788||NOR|U||VN00004|||||||N
PV1|1|O|RAD^RTGN01^01||||3456789^Johannessen^Stein^^^^^dr.|||RAD||||1||REF|7654321^Andersen^Silje^^^^^dr.||VN00004|||||||||||||||||||||20260318
ORC|RE|ORD20260318001|FIL20260318001||CM||||||3456789^Johannessen^Stein^^^^^dr.||7654321^Andersen^Silje^^^^^dr.|RAD^RTGN01^01
OBR|1|ORD20260318001|FIL20260318001|AA0AA^Røntgen thorax^NCRP||20260318074500|20260318080000||||||||7654321^Andersen^Silje^^^^^dr.||||||20260318112000|RAD||||^CR||1^^^20260318^^^^S|||||3456789^Johannessen^Stein^^^^^dr.|||20260318112000
OBX|1|TX|^Klinisk informasjon||Hoste i tre uker, røyker. Utelukke lungepatologi.||||||F
OBX|2|TX|^Beskrivelse||Røntgen thorax front og side. Lungefelter uten fokale infiltrater. Hjerteskyggen er normalstørrelse. Normale hili. Ingen pleuraeffusjon. Costofreniske vinkler er frie. Bløtdeler og skjelett uten anmerkning.||||||F
OBX|3|TX|^Konklusjon||Normalt røntgen thorax. Ingen tegn til pneumoni eller malignitet.||||||F
```

---

## 14. ADT^A08 - Patient information update at St. Olavs

```
MSH|^~\&|DIPS_ARENA|ST_OLAVS|SECTRA_RIS|ST_OLAVS|20260323140500||ADT^A08^ADT_A01|MSG00014|P|2.5|||AL|NE||UNICODE UTF-8|||NO
EVN|A08|20260323140500|||ADMIN03^Tangen^Marit
PID|1||22115678901^^^ST_OLAVS^PI||Aasen^Trond^Harald||19561122|M|||Elgeseter gate 22^^Trondheim^^7030^NOR||+4773112233||NOR|U||VN00005|||||||N
PV1|1|O|RAD^CT02^01||||4567890^Lund^Berit^^^^^dr.|||RAD||||1||REF|||VN00005|||||||||||||||||||||20260323
```

---

## 15. ORM^O01 - MR columna lumbalis order from Oslo universitetssykehus

```
MSH|^~\&|SECTRA_RIS|OSLO_UNIV_SH|DIPS_ARENA|OSLO_UNIV_SH|20260324081200||ORM^O01^ORM_O01|MSG00015|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||05115534289^^^OSLO_UNIV_SH^PI||Strøm^Helene^Cathrine||19551105|F|||Bogstadveien 19^^Oslo^^0355^NOR||+4722998877||NOR|U||VN00015|||||||N
PV1|1|O|RAD^MR02^01||||7890123^Thorsen^Geir^^^^^dr.|||RAD||||1||REF|2109876^Kolstad^Ane^^^^^dr.||VN00015|||||||||||||||||||||20260324
ORC|NW|ORD20260324001|FIL20260324001||SC|||1^^^20260326^^^^S||20260324081200|7890123^Thorsen^Geir^^^^^dr.||2109876^Kolstad^Ane^^^^^dr.|RAD^MR02^01
OBR|1|ORD20260324001|FIL20260324001|AB1FA^MR columna lumbalis^NCRP||20260324081200|||||||||2109876^Kolstad^Ane^^^^^dr.|||||||RAD||||^MR|||20260326^^^^S|||||||||||20260324
DG1|1|ICD10|M54.5^Korsryggsmerter^ICD10||20260324|A
```

---

## 16. ORU^R01 - CT abdomen result with findings from St. Olavs

```
MSH|^~\&|SECTRA_RIS|ST_OLAVS|DIPS_ARENA|ST_OLAVS|20260322161500||ORU^R01^ORU_R01|MSG00016|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||22115678901^^^ST_OLAVS^PI||Aasen^Trond^Harald||19561122|M|||Elgeseter gate 22^^Trondheim^^7030^NOR||+4773112233||NOR|U||VN00005|||||||N
PV1|1|O|RAD^CT02^01||||4567890^Lund^Berit^^^^^dr.|||RAD||||1||REF|8901234^Hovland^Espen^^^^^dr.||VN00005|||||||||||||||||||||20260322
ORC|RE|ORD20260322001|FIL20260322001||CM||||||4567890^Lund^Berit^^^^^dr.||8901234^Hovland^Espen^^^^^dr.|RAD^CT02^01
OBR|1|ORD20260322001|FIL20260322001|AA0AH^CT abdomen med kontrast^NCRP||20260322100000|20260322103000||||||||8901234^Hovland^Espen^^^^^dr.||||||20260322161500|RAD||||^CT||1^^^20260322^^^^S|||||4567890^Lund^Berit^^^^^dr.|||20260322161500
OBX|1|TX|^Klinisk informasjon||Magesmerter og vekttap. Utelukke malignitet.||||||F
OBX|2|TX|^Teknikk||CT abdomen og bekken med peroral og intravenøs kontrast. Portovenøs fase.||||||F
OBX|3|TX|^Beskrivelse||Lever: Normalt parenkymmønster uten fokale lesjoner. Galleveier ikke dilatert. Pankreas: Normal størrelse og form. Milten er normalstørrelse. Nyrer: Bilateral normal størrelse med homogen kontrastoppladning. Enkel 8 mm cyste i høyre nyre, uvesentlig. Aorta og store kar uten aneurisme. Ingen patologisk lymfadenopati. Tarm: Ingen veggfortykkelse eller obstruksjon. Fri luft ses ikke.||||||F
OBX|4|TX|^Konklusjon||Normalt CT abdomen og bekken. Enkel uskyldig nyrecyste høyre side. Ingen tegn til malignitet.||||||F
```

---

## 17. SIU^S12 - Scheduling mammografi at Haukeland

```
MSH|^~\&|SECTRA_RIS|HAUKELAND_US|DIPS_ARENA|HAUKELAND_US|20260325090000||SIU^S12^SIU_S12|MSG00017|P|2.5|||AL|NE||UNICODE UTF-8|||NO
SCH|APT20260401001|APT20260401001|||AD1AA^Mammografi^NCRP|Planlagt|Normal|20|min|^^20^20260401110000^20260401112000||9012345^Vikane^Randi^^^^^dr.||9012345^Vikane^Randi^^^^^dr.|BOOKED|||9012345^Vikane^Randi^^^^^dr.|
PID|1||17067245890^^^HAUKELAND_US^PI||Søvik^Gro^Anette||19720617|F|||Fjøsangerveien 44^^Bergen^^5054^NOR||+4755667788||NOR|U||VN00017|||||||N
AIS|1|A|AD1AA^Mammografi^NCRP|20260401110000||20|min
AIL|1|A|RAD^MAMMO01^01^HAUKELAND_US||||20260401110000||20|min
AIP|1|A|9012345^Vikane^Randi^^^^^dr.|||||20260401110000||20|min
```

---

## 18. ORU^R01 - CT caput akutt result with ED datatype (base64 PDF) from UNN

```
MSH|^~\&|SECTRA_PACS|UNN_TROMSO|NHN_EDI|NHN|20260322010030||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||30047123456^^^UNN_TROMSO^PI||Henriksen^Eirik^Magnus||19710430|M|||Sjøgata 8^^Tromsø^^9008^NOR||+4777556677||NOR|U||VN00008|||||||N
PV1|1|E|AKU^AKU01^01||||6789012^Solheim^Trygve^^^^^dr.|||AKU||||7||REF|5432109^Hansen^Lise^^^^^dr.||VN00008|||||||||||||||||||||20260322
ORC|RE|ORD20260321001|FIL20260321001||CM||||||6789012^Solheim^Trygve^^^^^dr.||5432109^Hansen^Lise^^^^^dr.|AKU^AKU01^01
OBR|1|ORD20260321001|FIL20260321001|AA0AB^CT caput uten kontrast^NCRP||20260321221000|20260321223000||||AKUTT||||5432109^Hansen^Lise^^^^^dr.||||||20260322010000|RAD||||^CT||1^^^20260321^^^^R|||||6789012^Solheim^Trygve^^^^^dr.|||20260322010000
OBX|1|TX|^Klinisk informasjon||Fall fra trapp. Bevisstløs ved ankomst. GCS 12. Utelukke intrakraniell blødning.||||||F
OBX|2|TX|^Beskrivelse||CT caput uten kontrast. Det ses ingen tegn til intrakraniell blødning, epiduralt eller subduralt hematom. Ingen midtlinjeforskyvning. Ventrikelsystemet er symmetrisk og normalkalibret. Basale cisterner er åpne. Benvev i calvaria uten frakturlinjer. Paranasale bihuler er klare.||||||F
OBX|3|TX|^Konklusjon||Ingen tegn til akutt intrakraniell patologi. Ingen fraktur.||||||F
OBX|4|ED|PDF^Radiologisk beskrivelse||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA4Mgo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKENUIGNhcHV0IC0gSW5nZW4gaW50cmFrcmFuaWVsbCBwYXRvbG9naSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMTcyIDAwMDAwIG4gCjAwMDAwMDAzMDQgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgozNzcKJSVFT0YK||||||F
```

---

## 19. ORM^O01 - CT angiografi lungearterie order from Haukeland

```
MSH|^~\&|SECTRA_RIS|HAUKELAND_US|DIPS_ARENA|HAUKELAND_US|20260326183045||ORM^O01^ORM_O01|MSG00019|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||25098756321^^^HAUKELAND_US^PI||Våge^Siri^Elisabeth||19870925|F|||Damsgårdsveien 112^^Bergen^^5058^NOR||+4755334455||NOR|U||VN00019|||||||N
PV1|1|E|AKU^AKU01^01||||2345678^Svendsen^Kari^Anne^^^dr.|||AKU||||7||REF|3210987^Mæland^Jonas^^^^^dr.||VN00019|||||||||||||||||||||20260326
ORC|NW|ORD20260326001|FIL20260326001||SC|||1^^^20260326^^^^R||20260326183045|2345678^Svendsen^Kari^Anne^^^dr.||3210987^Mæland^Jonas^^^^^dr.|AKU^AKU01^01
OBR|1|ORD20260326001|FIL20260326001|AA0AL^CT angiografi lungearterie^NCRP||20260326183045|||||AKUTT||||3210987^Mæland^Jonas^^^^^dr.|||||||RAD||||^CT|||20260326^^^^R|||||||||||20260326
DG1|1|ICD10|I26.9^Lungeemboli uten opplysning om akutt cor pulmonale^ICD10||20260326|A
```

---

## 20. ORU^R01 - Ultralyd abdomen result from Akershus universitetssykehus

```
MSH|^~\&|SECTRA_RIS|AHUS|DIPS_ARENA|AHUS|20260321152000||ORU^R01^ORU_R01|MSG00020|P|2.5|||AL|NE||UNICODE UTF-8|||NO
PID|1||01028834567^^^AHUS^PI||Grønlund^Eva^Solveig||19880201|F|||Storgata 12^^Lillestrøm^^2000^NOR||+4763112233||NOR|U||VN00006|||||||N
PV1|1|O|RAD^UL01^01||||5678901^Dahl^Henrik^Olav^^^dr.|||RAD||||1||REF|6543210^Berg^Kristine^^^^^dr.||VN00006|||||||||||||||||||||20260321
ORC|RE|ORD20260320001|FIL20260320001||CM||||||5678901^Dahl^Henrik^Olav^^^dr.||6543210^Berg^Kristine^^^^^dr.|RAD^UL01^01
OBR|1|ORD20260320001|FIL20260320001|AC1AE^Ultralyd abdomen^NCRP||20260320114500|20260321140000||||||||6543210^Berg^Kristine^^^^^dr.||||||20260321152000|RAD||||^US||1^^^20260320^^^^S|||||5678901^Dahl^Henrik^Olav^^^dr.|||20260321152000
OBX|1|TX|^Klinisk informasjon||Uklare magesmerter, intermitterende. Utelukke gallesteinssykdom.||||||F
OBX|2|TX|^Teknikk||Ultralyd av lever, galleblære, galleveier, pankreas, nyrer og milt.||||||F
OBX|3|TX|^Beskrivelse||Lever: Normal størrelse og ekkogenisitet. Ingen fokale lesjoner. Galleblære: Normal veggtykkelse. Det ses to ekkogene strukturer på henholdsvis 6 mm og 9 mm med akustisk skygge forenlig med gallesteiner. Galleveier: Ductus hepatocholedochus måler 4 mm, normalt. Pankreas: Delvis innsyn, normal der vurdert. Høyre nyre: 11,2 cm, normal parenkymmønster. Venstre nyre: 11,5 cm, normal. Milten: Normalstørrelse.||||||F
OBX|4|TX|^Konklusjon||To gallesteiner uten tegn til akutt kolecystitt. For øvrig normale funn.||||||F
```
