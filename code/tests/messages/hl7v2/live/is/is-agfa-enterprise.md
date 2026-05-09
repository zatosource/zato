# AGFA Enterprise Imaging - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Imaging order (X-ray)

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250312091500||ORM^O01^ORM_O01|MSG00001|P|2.5|||AL|NE||IS
PID|1||1205874932^^^ISLREG^NI||Gunnarsson^Ólafur^Þorsteinn^^Hr.||19870512|M|||Ásvallagata 11^^Reykjavík^^101^IS||+3545587412|||IS||||1205874932
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012345|||||||||||||||||||||||||20250312091500
ORC|NW|ORD20250312001|||||^^^20250312091500^^R||20250312091500|DRBRYN^Halldórsson^Einar^Magnús^^Dr.||DRBRYN^Halldórsson^Einar^Magnús^^Dr.|Myndgreiningardeild Landspítala
OBR|1|ORD20250312001||XRAY-CHEST^Röntgenmynd af brjóstkassa^ISLPROCRAD|||20250312091500||||||||DRBRYN^Halldórsson^Einar^Magnús^^Dr.||||||||||^^^^^R
```

---

## 2. ORM^O01 - CT imaging order

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|RAFÖRNINN|Landspítali|20250313103000||ORM^O01^ORM_O01|MSG00002|P|2.5|||AL|NE||IS
PID|1||1709916548^^^ISLREG^NI||Kristjánsdóttir^Þórhildur^Ingunn^^Frú||19910917|F|||Baugholt 3^^Kópavogur^^200^IS||+3545524718|||IS||||1709916548
PV1|1|O|CT^CT01^1|||||||RAD|||||||||V00012346|||||||||||||||||||||||||20250313103000
ORC|NW|ORD20250313002|||||^^^20250313103000^^R||20250313103000|DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.||DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.|Myndgreiningardeild Landspítala
OBR|1|ORD20250313002||CT-ABD^Tölvusneiðmynd af kvið^ISLPROCRAD|||20250313103000||||||||DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.||||||||||^^^^^R
```

---

## 3. ORM^O01 - MRI imaging order

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|HEKLA|Landspítali|20250314140000||ORM^O01^ORM_O01|MSG00003|P|2.5|||AL|NE||IS
PID|1||0804953271^^^ISLREG^NI||Stefánsson^Baldur^Helgi^^Hr.||19950804|M|||Kvisthagi 7^^Reykjavík^^105^IS||+3545596231|||IS||||0804953271
PV1|1|O|MRI^MRI01^1|||||||RAD|||||||||V00012347|||||||||||||||||||||||||20250314140000
ORC|NW|ORD20250314003|||||^^^20250314140000^^R||20250314140000|DRJOH^Bjarnason^Kristinn^Arnar^^Dr.||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.|Myndgreiningardeild Landspítala
OBR|1|ORD20250314003||MRI-BRAIN^Segulómun af heila^ISLPROCRAD|||20250314140000||||||||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.||||||||||^^^^^R
```

---

## 4. ORU^R01 - X-ray imaging report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250312141500||ORU^R01^ORU_R01|MSG00004|P|2.5|||AL|NE||IS
PID|1||1205874932^^^ISLREG^NI||Gunnarsson^Ólafur^Þorsteinn^^Hr.||19870512|M|||Ásvallagata 11^^Reykjavík^^101^IS||+3545587412|||IS||||1205874932
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012345|||||||||||||||||||||||||20250312091500
ORC|RE|ORD20250312001||||||20250312141500|DRBRYN^Halldórsson^Einar^Magnús^^Dr.
OBR|1|ORD20250312001||XRAY-CHEST^Röntgenmynd af brjóstkassa^ISLPROCRAD|||20250312091500|||||||20250312141500|DRBRYN^Halldórsson^Einar^Magnús^^Dr.||||||||F
OBX|1|TX|XRAY-CHEST^Röntgenmynd af brjóstkassa||Hjarta og miðmæti eru eðlileg að stærð. Engin vökvasöfnun í fleiðruholi. Lungnavefur hreinn beggja vegna. Ekkert óeðlilegt greinanlegt.||||||F
OBX|2|TX|XRAY-CHEST^Niðurstaða||Eðlileg röntgenmynd af brjóstkassa.||||||F
```

---

## 5. ORU^R01 - CT imaging report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|RAFÖRNINN|Landspítali|20250313163000||ORU^R01^ORU_R01|MSG00005|P|2.5|||AL|NE||IS
PID|1||1709916548^^^ISLREG^NI||Kristjánsdóttir^Þórhildur^Ingunn^^Frú||19910917|F|||Baugholt 3^^Kópavogur^^200^IS||+3545524718|||IS||||1709916548
PV1|1|O|CT^CT01^1|||||||RAD|||||||||V00012346|||||||||||||||||||||||||20250313103000
ORC|RE|ORD20250313002||||||20250313163000|DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.
OBR|1|ORD20250313002||CT-ABD^Tölvusneiðmynd af kvið^ISLPROCRAD|||20250313103000|||||||20250313163000|DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.||||||||F
OBX|1|TX|CT-ABD^Tölvusneiðmynd af kvið||Lifur, milti og nýru af eðlilegri stærð og gerð. Gallblöðru og gallvegir eðlilegir. Briskirtill óbreyttur. Engin eitlastækkun í kviðarholi.||||||F
OBX|2|TX|CT-ABD^Niðurstaða||Eðlileg tölvusneiðmynd af kvið. Engin merki um sjúkdóm.||||||F
```

---

## 6. ORU^R01 - MRI imaging report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|HEKLA|Landspítali|20250314180000||ORU^R01^ORU_R01|MSG00006|P|2.5|||AL|NE||IS
PID|1||0804953271^^^ISLREG^NI||Stefánsson^Baldur^Helgi^^Hr.||19950804|M|||Kvisthagi 7^^Reykjavík^^105^IS||+3545596231|||IS||||0804953271
PV1|1|O|MRI^MRI01^1|||||||RAD|||||||||V00012347|||||||||||||||||||||||||20250314140000
ORC|RE|ORD20250314003||||||20250314180000|DRJOH^Bjarnason^Kristinn^Arnar^^Dr.
OBR|1|ORD20250314003||MRI-BRAIN^Segulómun af heila^ISLPROCRAD|||20250314140000|||||||20250314180000|DRJOH^Bjarnason^Kristinn^Arnar^^Dr.||||||||F
OBX|1|TX|MRI-BRAIN^Segulómun af heila||Heilavefur eðlilegur beggja vegna. Heilahólf af eðlilegri stærð. Ekkert merki um rúmfyllingu eða blæðingu. Hvítt efni heilans er eðlilegt. Heilabarkur óbreyttur.||||||F
OBX|2|TX|MRI-BRAIN^Niðurstaða||Eðlileg segulómun af heila. Ekkert sjúklegt greinanlegt.||||||F
```

---

## 7. ORU^R01 - Echocardiography report

```
MSH|^~\&|AGFA_EI|Hjartamyndgreining Landspítala|SAGA|Landspítali|20250315111500||ORU^R01^ORU_R01|MSG00007|P|2.5|||AL|NE||IS
PID|1||2403681094^^^ISLREG^NI||Ásgeirsdóttir^Helga^Kristín^^Frú||19680324|F|||Lönguhlíð 52^^Reykjavík^^101^IS||+3545539147|||IS||||2403681094
PV1|1|O|CARD^CARD01^1|||||||CARD|||||||||V00012348|||||||||||||||||||||||||20250315100000
ORC|RE|ORD20250315004||||||20250315111500|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.
OBR|1|ORD20250315004||ECHO^Hjartaómun^ISLPROCCARD|||20250315100000|||||||20250315111500|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.||||||||F
OBX|1|TX|ECHO^Hjartaómun||Vinstri slegli af eðlilegri stærð og samdráttargetu. Útfallsbrot (EF) metið 62%. Hjartalokur án verulegrar leka eða þrengingar. Hægri slegli og gáttir eðlileg.||||||F
OBX|2|NM|ECHO-EF^Útfallsbrot||62|%|55-75||||F
OBX|3|TX|ECHO^Niðurstaða||Eðlileg hjartaómun. Engin merki um hjartabilun eða lokusjúkdóm.||||||F
```

---

## 8. ORU^R01 - Mammography screening report

```
MSH|^~\&|AGFA_EI|Brjóstamyndgreining|SAGA|Landspítali|20250316093000||ORU^R01^ORU_R01|MSG00008|P|2.5|||AL|NE||IS
PID|1||0611772583^^^ISLREG^NI||Haraldsdóttir^Sigríður^Ásta^^Frú||19770611|F|||Grundarstígur 18^^Hafnarfjörður^^220^IS||+3545648902|||IS||||0611772583
PV1|1|O|MAM^MAM01^1|||||||RAD|||||||||V00012349|||||||||||||||||||||||||20250316090000
ORC|RE|ORD20250316005||||||20250316093000|DRVAL^Guðmundsdóttir^Jóhanna^Lilja^^Dr.
OBR|1|ORD20250316005||MAMMO^Brjóstamyndgreining^ISLPROCRAD|||20250316090000|||||||20250316093000|DRVAL^Guðmundsdóttir^Jóhanna^Lilja^^Dr.||||||||F
OBX|1|TX|MAMMO^Brjóstamyndgreining||Brjóstavefur beggja vegna skoðaður. Kirtlavefur er af meðalþéttleika (BI-RADS þéttleika flokkur B). Engar grunsamlegar kölkanir eða fyrirferðir sjáanlegar.||||||F
OBX|2|TX|MAMMO^Niðurstaða||BI-RADS 1: Eðlileg brjóstamyndgreining. Mælt með endurkomu eftir tvö ár.||||||F
```

---

## 9. SIU^S12 - Schedule imaging

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250317080000||SIU^S12^SIU_S12|MSG00009|P|2.5|||AL|NE||IS
SCH|SCH20250317001|||||XRAY-SPINE^Röntgenmynd af hrygg^ISLPROCRAD|||||15|MIN|^^^20250320091500^20250320093000||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.|+3545551146|Myndgreiningardeild Landspítala|Hringbraut^^Reykjavík^^101^IS||BOOKED
PID|1||2201893748^^^ISLREG^NI||Þorvaldsson^Sindri^Leifur^^Hr.||19890122|M|||Hlíðarbraut 6^^Garðabær^^210^IS||+3545571943|||IS||||2201893748
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012350
RGS|1
AIS|1||XRAY-SPINE^Röntgenmynd af hrygg^ISLPROCRAD|20250320091500|0|MIN|15|MIN
AIG|1||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.
AIL|1||Myndgreiningardeild Landspítala^^RAD^RAD01
```

---

## 10. SIU^S14 - Reschedule imaging

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250318100000||SIU^S14^SIU_S14|MSG00010|P|2.5|||AL|NE||IS
SCH|SCH20250317001|||||XRAY-SPINE^Röntgenmynd af hrygg^ISLPROCRAD|||||15|MIN|^^^20250322101500^20250322103000||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.|+3545551146|Myndgreiningardeild Landspítala|Hringbraut^^Reykjavík^^101^IS||BOOKED
PID|1||2201893748^^^ISLREG^NI||Þorvaldsson^Sindri^Leifur^^Hr.||19890122|M|||Hlíðarbraut 6^^Garðabær^^210^IS||+3545571943|||IS||||2201893748
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012350
RGS|1
AIS|1||XRAY-SPINE^Röntgenmynd af hrygg^ISLPROCRAD|20250322101500|0|MIN|15|MIN
AIG|1||DRJOH^Bjarnason^Kristinn^Arnar^^Dr.
AIL|1||Myndgreiningardeild Landspítala^^RAD^RAD01
```

---

## 11. ADT^A04 - Imaging patient registration

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250319070000||ADT^A04^ADT_A01|MSG00011|P|2.5|||AL|NE||IS
EVN|A04|20250319070000
PID|1||1503962817^^^ISLREG^NI||Magnúsdóttir^Rakel^Þórunn^^Frú||19960315|F|||Dalvegur 19^^Mosfellsbær^^270^IS||+3545560418|||IS||||1503962817
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012351|||||||||||||||||||||||||20250319070000
```

---

## 12. ADT^A08 - Update imaging patient

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250319120000||ADT^A08^ADT_A01|MSG00012|P|2.5|||AL|NE||IS
EVN|A08|20250319120000
PID|1||1503962817^^^ISLREG^NI||Magnúsdóttir^Rakel^Þórunn^^Frú||19960315|F|||Birkihlíð 8^^Mosfellsbær^^270^IS||+3545560418|+3545560291||IS||||1503962817
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012351|||||||||||||||||||||||||20250319070000
```

---

## 13. ORU^R01 - Nuclear medicine report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|RAFÖRNINN|Landspítali|20250320163000||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE||IS
PID|1||0407802693^^^ISLREG^NI||Jónsdóttir^Vigdís^Hrefna^^Frú||19800407|F|||Ránargata 23^^Akureyri^^600^IS||+3544625189|||IS||||0407802693
PV1|1|O|NM^NM01^1|||||||RAD|||||||||V00012352|||||||||||||||||||||||||20250320090000
ORC|RE|ORD20250320006||||||20250320163000|DRARNI^Sigurðsson^Guðmundur^Fannar^^Dr.
OBR|1|ORD20250320006||NM-BONE^Beinaskann^ISLPROCRAD|||20250320090000|||||||20250320163000|DRARNI^Sigurðsson^Guðmundur^Fannar^^Dr.||||||||F
OBX|1|TX|NM-BONE^Beinaskann||Geislavirk efnagjöf með Tc-99m MDP. Dreifing geislavirknisefnis í beinagrind er samhverf og eðlileg. Engin svæði aukinnar eða minni upptöku sem benda til meinvarps eða brots.||||||F
OBX|2|TX|NM-BONE^Niðurstaða||Eðlilegt beinaskann. Engin merki um meinvörp í beinum.||||||F
```

---

## 14. MDM^T02 - Imaging consultation report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250321100000||MDM^T02^MDM_T02|MSG00014|P|2.5|||AL|NE||IS
EVN|T02|20250321100000
PID|1||1205874932^^^ISLREG^NI||Gunnarsson^Ólafur^Þorsteinn^^Hr.||19870512|M|||Ásvallagata 11^^Reykjavík^^101^IS||+3545587412|||IS||||1205874932
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012345
TXA|1|RAD-CONSULT^Myndgreiningarráðgjöf|TX|20250321100000|DRBRYN^Halldórsson^Einar^Magnús^^Dr.||20250321100000||DRBRYN^Halldórsson^Einar^Magnús^^Dr.||||DOC20250321001||||AU
OBX|1|TX|RAD-CONSULT^Myndgreiningarráðgjöf||Ráðgjöf vegna áður greinds hnúts í lungnavef á röntgenmynd. Mælt með tölvusneiðmynd af brjóstkassa til nánari greiningar. Skoða á aftur eftir 3 mánuði ef tölvusneiðmynd er eðlileg.||||||F
```

---

## 15. ORU^R01 - Cardiac catheterization report

```
MSH|^~\&|AGFA_EI|Hjartamyndgreining Landspítala|SAGA|Landspítali|20250322153000||ORU^R01^ORU_R01|MSG00015|P|2.5|||AL|NE||IS
PID|1||1806701347^^^ISLREG^NI||Haraldsson^Magnús^Guðjón^^Hr.||19700618|M|||Miðtún 29^^Hafnarfjörður^^220^IS||+3545653804|||IS||||1806701347
PV1|1|I|CARD^CATH01^1|||||||CARD|||||||||V00012353|||||||||||||||||||||||||20250322080000
ORC|RE|ORD20250322007||||||20250322153000|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.
OBR|1|ORD20250322007||CATH^Hjartaþræðing^ISLPROCCARD|||20250322100000|||||||20250322153000|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.||||||||F
OBX|1|TX|CATH^Hjartaþræðing||Hjartaþræðing framkvæmd. Vinstri kransæð (LAD) með 70% þrengingu í nálægðarhluta. Hægri kransæð opin. Útfallsbrot vinstri slegils metið 55%. Lokþrýstingur eðlilegur.||||||F
OBX|2|NM|CATH-EF^Útfallsbrot||55|%|55-75||||F
OBX|3|TX|CATH^Niðurstaða||Marktæk þrenging í LAD kransæð. Mælt með PCI meðferð eða kransæðahjáveituaðgerð. Ræða við hjartaskurðlækni.||||||F
```

---

## 16. ORM^O01 - Ultrasound order

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|HEKLA|Landspítali|20250323083000||ORM^O01^ORM_O01|MSG00016|P|2.5|||AL|NE||IS
PID|1||2108882504^^^ISLREG^NI||Pétursdóttir^Hólmfríður^Elín^^Frú||19880821|F|||Brekkuás 12^^Reykjanesbær^^230^IS||+3545427891|||IS||||2108882504
PV1|1|O|US^US01^1|||||||RAD|||||||||V00012354|||||||||||||||||||||||||20250323083000
ORC|NW|ORD20250323008|||||^^^20250323083000^^R||20250323083000|DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.||DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.|Myndgreiningardeild Landspítala
OBR|1|ORD20250323008||US-ABD^Ómun af kvið^ISLPROCRAD|||20250323083000||||||||DRSIG^Þórarinsdóttir^Ása^Guðrún^^Dr.||||||||||^^^^^R
```

---

## 17. ORU^R01 - Enterprise imaging with base64 ED OBX (PDF report)

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250324120000||ORU^R01^ORU_R01|MSG00017|P|2.5|||AL|NE||IS
PID|1||0804953271^^^ISLREG^NI||Stefánsson^Baldur^Helgi^^Hr.||19950804|M|||Kvisthagi 7^^Reykjavík^^105^IS||+3545596231|||IS||||0804953271
PV1|1|O|MRI^MRI01^1|||||||RAD|||||||||V00012347|||||||||||||||||||||||||20250314140000
ORC|RE|ORD20250314003||||||20250324120000|DRJOH^Bjarnason^Kristinn^Arnar^^Dr.
OBR|1|ORD20250314003||MRI-BRAIN^Segulómun af heila^ISLPROCRAD|||20250314140000|||||||20250324120000|DRJOH^Bjarnason^Kristinn^Arnar^^Dr.||||||||F
OBX|1|TX|MRI-BRAIN^Segulómun af heila||Segulómun af heila framkvæmd. Heilavefur eðlilegur. Engin rúmfylling eða blæðing. Sjá meðfylgjandi PDF skýrslu.||||||F
OBX|2|ED|PDF^Imaging Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE1SSS1CcmFpbiBSZXBvcnQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1MSAwMDAwMCBuIAowMDAwMDAwMjMwIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNQovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMzI0CiUlRU9GCg==||||||F
```

---

## 18. ORU^R01 - Cardiac imaging with base64 ED OBX (PDF)

```
MSH|^~\&|AGFA_EI|Hjartamyndgreining Landspítala|SAGA|Landspítali|20250325140000||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE||IS
PID|1||2403681094^^^ISLREG^NI||Ásgeirsdóttir^Helga^Kristín^^Frú||19680324|F|||Lönguhlíð 52^^Reykjavík^^101^IS||+3545539147|||IS||||2403681094
PV1|1|O|CARD^CARD01^1|||||||CARD|||||||||V00012348|||||||||||||||||||||||||20250315100000
ORC|RE|ORD20250315004||||||20250325140000|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.
OBR|1|ORD20250315004||ECHO^Hjartaómun^ISLPROCCARD|||20250315100000|||||||20250325140000|DRSTEIN^Jónsson^Ragnar^Ingvar^^Dr.||||||||F
OBX|1|TX|ECHO^Hjartaómun||Hjartaómun framkvæmd. Útfallsbrot 62%. Lokur eðlilegar. Sjá meðfylgjandi PDF skýrslu.||||||F
OBX|2|ED|PDF^Cardiac Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1MAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEVjaG9jYXJkaW9ncmFwaHkgUmVwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNTEgMDAwMDAgbiAKMDAwMDAwMDIzMCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjMzMAolJUVPRgo=||||||F
```

---

## 19. ADT^A31 - Update patient demographics

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|RAFÖRNINN|Landspítali|20250326090000||ADT^A31^ADT_A05|MSG00019|P|2.5|||AL|NE||IS
EVN|A31|20250326090000
PID|1||0407802693^^^ISLREG^NI||Jónsdóttir^Vigdís^Hrefna^^Frú||19800407|F|||Vallargata 5^^Akureyri^^600^IS||+3544625189|+3544625301||IS||||0407802693
PV1|1|O|RAD^RAD01^1|||||||RAD|||||||||V00012352
NK1|1|Jónsson^Guðlaugur^^^Hr.|SPO|Vallargata 5^^Akureyri^^600^IS|+3544625402
```

---

## 20. ORU^R01 - Bone density DEXA report

```
MSH|^~\&|AGFA_EI|Myndgreiningardeild Landspítala|SAGA|Landspítali|20250327143000||ORU^R01^ORU_R01|MSG00020|P|2.5|||AL|NE||IS
PID|1||0611772583^^^ISLREG^NI||Haraldsdóttir^Sigríður^Ásta^^Frú||19770611|F|||Grundarstígur 18^^Hafnarfjörður^^220^IS||+3545648902|||IS||||0611772583
PV1|1|O|DEXA^DEXA01^1|||||||RAD|||||||||V00012355|||||||||||||||||||||||||20250327130000
ORC|RE|ORD20250327009||||||20250327143000|DRVAL^Guðmundsdóttir^Jóhanna^Lilja^^Dr.
OBR|1|ORD20250327009||DEXA^Beinþéttnimæling^ISLPROCRAD|||20250327130000|||||||20250327143000|DRVAL^Guðmundsdóttir^Jóhanna^Lilja^^Dr.||||||||F
OBX|1|TX|DEXA^Beinþéttnimæling||Beinþéttnimæling framkvæmd á lendhrygg (L1-L4) og lærleggshálsi. Lendhryggur: T-skor -1.8, Z-skor -1.2. Lærleggshálsur: T-skor -1.5, Z-skor -0.9. Niðurstöður benda til beinþynningar (osteopenia).||||||F
OBX|2|NM|DEXA-TSCORE-SPINE^T-skor lendhryggur||-1.8||||||F
OBX|3|NM|DEXA-TSCORE-HIP^T-skor lærleggshálsur||-1.5||||||F
OBX|4|TX|DEXA^Niðurstaða||Beinþynning (osteopenia) í lendhrygg og lærleggshálsi. Mælt með kalkviðbót, D-vítamíni og endurteknum mælingum eftir 2 ár.||||||F
```
