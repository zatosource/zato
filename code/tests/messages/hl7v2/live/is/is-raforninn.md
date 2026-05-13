# Raförninn RIS/PACS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Chest X-ray order

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250314091200||ORM^O01|MSG00001|P|2.4
PID|1||1408903127^^^ÞJÓÐSKRÁ^KT||Bárðarson^Hróar^^^hr.||19900814|M|||Hraunteigur 6^^Reykjavík^^105^IS||+3545671203|||S
PV1|1|O|RAD^RÖNTGEN^01||||^Vilbergsdóttir^Þórdís^^^dr.|||RAD||||||||V00012345|||||||||||||||||||||||||20250314091200
ORC|NW|ORD20250314-001|FIL20250314-001||SC|||1^^^20250314091200^^R||20250314091200|^Vilbergsdóttir^Þórdís^^^dr.||^Vilbergsdóttir^Þórdís^^^dr.|RÖNTGENDEILD LANDSPÍTALA
OBR|1|ORD20250314-001|FIL20250314-001|RRCH^Röntgen af brjóstkassa^RAFÖRNINN|||20250314091200||||||||^Vilbergsdóttir^Þórdís^^^dr.||||||20250314091200|||1^^^20250314091200^^R||^Grun um lungnabólgu
```

---

## 2. ORM^O01 - CT abdomen order

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250315103000||ORM^O01|MSG00002|P|2.4
PID|1||0709864321^^^ÞJÓÐSKRÁ^KT||Tómasdóttir^Sigurlaug^^^frú||19860907|F|||Furugrund 22^^Akureyri^^603^IS||+3544669012|||G
PV1|1|O|RAD^SNEIÐMYND^02||||^Skúlason^Davíð^^^dr.|||RAD||||||||V00023456|||||||||||||||||||||||||20250315103000
ORC|NW|ORD20250315-002|FIL20250315-002||SC|||1^^^20250315103000^^R||20250315103000|^Skúlason^Davíð^^^dr.||^Skúlason^Davíð^^^dr.|RÖNTGENDEILD LANDSPÍTALA
OBR|1|ORD20250315-002|FIL20250315-002|CTAB^Tölvusneiðmynd af kvið^RAFÖRNINN|||20250315103000||||||||^Skúlason^Davíð^^^dr.||||||20250315103000|||1^^^20250315103000^^R||^Kviðverkur og þyngdartap
```

---

## 3. ORM^O01 - MRI brain order

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250316140500||ORM^O01|MSG00003|P|2.4
PID|1||1102942768^^^ÞJÓÐSKRÁ^KT||Heiðarsson^Sölvi^^^hr.||19940211|M|||Norðurmýri 12^^Reykjavík^^105^IS||+3545540821|||S
PV1|1|O|RAD^SEGULÓMUN^03||||^Vésteinsdóttir^Auður^^^dr.|||RAD||||||||V00034567|||||||||||||||||||||||||20250316140500
ORC|NW|ORD20250316-003|FIL20250316-003||SC|||1^^^20250316140500^^R||20250316140500|^Vésteinsdóttir^Auður^^^dr.||^Vésteinsdóttir^Auður^^^dr.|RÖNTGENDEILD LANDSPÍTALA
OBR|1|ORD20250316-003|FIL20250316-003|MRBR^Segulómun af heila^RAFÖRNINN|||20250316140500||||||||^Vésteinsdóttir^Auður^^^dr.||||||20250316140500|||1^^^20250316140500^^R||^Endurteknir höfuðverkir og sjóntruflanir
```

---

## 4. ORM^O01 - Ultrasound order

```
MSH|^~\&|RAFÖRNINN|MYNDGREININGARDEILD FSA|AGFA|FSA AKUREYRI|20250317083000||ORM^O01|MSG00004|P|2.4
PID|1||0309892347^^^ÞJÓÐSKRÁ^KT||Brandsdóttir^Hugborg^^^frú||19890903|F|||Skipagata 14^^Akureyri^^600^IS||+3544627193|||G
PV1|1|O|RAD^ÓMUN^01||||^Tryggvason^Bergþór^^^dr.|||RAD||||||||V00045678|||||||||||||||||||||||||20250317083000
ORC|NW|ORD20250317-004|FIL20250317-004||SC|||1^^^20250317083000^^R||20250317083000|^Tryggvason^Bergþór^^^dr.||^Tryggvason^Bergþór^^^dr.|MYNDGREININGARDEILD FSA
OBR|1|ORD20250317-004|FIL20250317-004|USAB^Ómun af kvið^RAFÖRNINN|||20250317083000||||||||^Tryggvason^Bergþór^^^dr.||||||20250317083000|||1^^^20250317083000^^R||^Gallsteinar grunaðir
```

---

## 5. ORU^R01 - Chest X-ray report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250314143000||ORU^R01|MSG00005|P|2.4
PID|1||1408903127^^^ÞJÓÐSKRÁ^KT||Bárðarson^Hróar^^^hr.||19900814|M|||Hraunteigur 6^^Reykjavík^^105^IS||+3545671203|||S
PV1|1|O|RAD^RÖNTGEN^01||||^Vilbergsdóttir^Þórdís^^^dr.|||RAD||||||||V00012345|||||||||||||||||||||||||20250314091200
ORC|RE|ORD20250314-001|FIL20250314-001||CM|||1^^^20250314091200^^R||20250314143000|^Marteinsson^Heimir^^^dr.
OBR|1|ORD20250314-001|FIL20250314-001|RRCH^Röntgen af brjóstkassa^RAFÖRNINN|||20250314091200|||||||||^Vilbergsdóttir^Þórdís^^^dr.||||||20250314143000|||F
OBX|1|FT|REPORT^Niðurstaða||Hjarta og miðmæti eðlileg að stærð. Engin vökvasöfnun í fleiðruholi. Lungnavefur án greinanlega sjúklegra breytinga. Beingerð eðlileg.||||||F
OBX|2|FT|CONCLUSION^Álitun||Eðlilegt röntgenmynd af brjóstkassa. Engin merki um lungnabólgu.||||||F
```

---

## 6. ORU^R01 - CT abdomen report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250315160000||ORU^R01|MSG00006|P|2.4
PID|1||0709864321^^^ÞJÓÐSKRÁ^KT||Tómasdóttir^Sigurlaug^^^frú||19860907|F|||Furugrund 22^^Akureyri^^603^IS||+3544669012|||G
PV1|1|O|RAD^SNEIÐMYND^02||||^Skúlason^Davíð^^^dr.|||RAD||||||||V00023456|||||||||||||||||||||||||20250315103000
ORC|RE|ORD20250315-002|FIL20250315-002||CM|||1^^^20250315103000^^R||20250315160000|^Þorgrímsdóttir^Hekla^^^dr.
OBR|1|ORD20250315-002|FIL20250315-002|CTAB^Tölvusneiðmynd af kvið^RAFÖRNINN|||20250315103000|||||||||^Skúlason^Davíð^^^dr.||||||20250315160000|||F
OBX|1|FT|REPORT^Niðurstaða||Lifur, milti og nýru eðlileg að stærð og útliti. Gallblöðru og gallgöng eðlileg. Bris eðlilegt. Engin eitlastækkun. Engin vökvasöfnun í kviðarholi. Ristill og smáþarmar án athugasemda.||||||F
OBX|2|FT|CONCLUSION^Álitun||Eðlileg tölvusneiðmynd af kvið. Engar skýringar á einkennum sjúklings fundust.||||||F
```

---

## 7. ORU^R01 - MRI brain report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250316173000||ORU^R01|MSG00007|P|2.4
PID|1||1102942768^^^ÞJÓÐSKRÁ^KT||Heiðarsson^Sölvi^^^hr.||19940211|M|||Norðurmýri 12^^Reykjavík^^105^IS||+3545540821|||S
PV1|1|O|RAD^SEGULÓMUN^03||||^Vésteinsdóttir^Auður^^^dr.|||RAD||||||||V00034567|||||||||||||||||||||||||20250316140500
ORC|RE|ORD20250316-003|FIL20250316-003||CM|||1^^^20250316140500^^R||20250316173000|^Stefánsson^Hjalti^^^dr.
OBR|1|ORD20250316-003|FIL20250316-003|MRBR^Segulómun af heila^RAFÖRNINN|||20250316140500|||||||||^Vésteinsdóttir^Auður^^^dr.||||||20250316173000|||F
OBX|1|FT|REPORT^Niðurstaða||Heilavefur eðlilegur. Engin rýmisaukin meðferð. Heilahólf eðlileg að stærð. Hvítt efni án merkja um afmýlingu. Engin óeðlileg aukning á skuggaefni. Heilabörkur og heiladinglar eðlileg.||||||F
OBX|2|FT|CONCLUSION^Álitun||Eðlileg segulómun af heila. Engar skýringar á höfuðverk eða sjóntruflunum.||||||F
```

---

## 8. ORU^R01 - Ultrasound report

```
MSH|^~\&|RAFÖRNINN|MYNDGREININGARDEILD FSA|AGFA|FSA AKUREYRI|20250317112000||ORU^R01|MSG00008|P|2.4
PID|1||0309892347^^^ÞJÓÐSKRÁ^KT||Brandsdóttir^Hugborg^^^frú||19890903|F|||Skipagata 14^^Akureyri^^600^IS||+3544627193|||G
PV1|1|O|RAD^ÓMUN^01||||^Tryggvason^Bergþór^^^dr.|||RAD||||||||V00045678|||||||||||||||||||||||||20250317083000
ORC|RE|ORD20250317-004|FIL20250317-004||CM|||1^^^20250317083000^^R||20250317112000|^Tryggvason^Bergþór^^^dr.
OBR|1|ORD20250317-004|FIL20250317-004|USAB^Ómun af kvið^RAFÖRNINN|||20250317083000|||||||||^Tryggvason^Bergþór^^^dr.||||||20250317112000|||F
OBX|1|FT|REPORT^Niðurstaða||Gallblaðra inniheldur marga litla gallsteina, sá stærsti um 8mm. Engin merki um bólgu í gallblöðru. Gallgöng ekki útvíkkuð, sameiginlegur gallgangur mælist 4mm. Lifur, milti og nýru eðlileg.||||||F
OBX|2|FT|CONCLUSION^Álitun||Gallsteinar í gallblöðru án merkja um bráða gallblöðrubólgu.||||||F
```

---

## 9. SIU^S12 - Schedule CT appointment

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250318090000||SIU^S12|MSG00009|P|2.4
SCH|SCH20250318-001|APT20250318-001|||||ROUTINE^Venjuleg tímapöntun|CTCH^Tölvusneiðmynd af brjóstkassa^RAFÖRNINN|30|MIN|^^30^20250320093000^20250320100000||^Daníelsdóttir^Lóa^^^dr.|+3545430711|RÖNTGENDEILD LANDSPÍTALA|Hringbraut 101^^Reykjavík^^101^IS|||BOOKED
PID|1||1907871542^^^ÞJÓÐSKRÁ^KT||Pálmason^Erlendur^^^hr.||19870719|M|||Lyngheiði 21^^Kópavogur^^200^IS||+3545891367|||S
PV1|1|O|RAD^SNEIÐMYND^02||||^Daníelsdóttir^Lóa^^^dr.|||RAD||||||||V00056789
RGS|1|A
AIS|1|A|CTCH^Tölvusneiðmynd af brjóstkassa^RAFÖRNINN|20250320093000|0|MIN|30|MIN
AIG|1|A|^Daníelsdóttir^Lóa^^^dr.|RÖNTGENLÆKNIR
AIL|1|A|RAD^SNEIÐMYND^02^RÖNTGENDEILD LANDSPÍTALA
```

---

## 10. SIU^S14 - Modify MRI appointment

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250319101500||SIU^S14|MSG00010|P|2.4
SCH|SCH20250319-001|APT20250319-001|||||ROUTINE^Venjuleg tímapöntun|MRKN^Segulómun af hné^RAFÖRNINN|45|MIN|^^45^20250325140000^20250325144500||^Stefánsson^Hjalti^^^dr.|+3545430712|RÖNTGENDEILD LANDSPÍTALA|Hringbraut 101^^Reykjavík^^101^IS|||BOOKED
PID|1||0510962078^^^ÞJÓÐSKRÁ^KT||Vésteinsdóttir^Bryndís^^^frú||19961005|F|||Aratún 9^^Garðabær^^210^IS||+3545710924|||G
PV1|1|O|RAD^SEGULÓMUN^03||||^Stefánsson^Hjalti^^^dr.|||RAD||||||||V00067890
RGS|1|A
AIS|1|A|MRKN^Segulómun af hné^RAFÖRNINN|20250325140000|0|MIN|45|MIN
AIG|1|A|^Stefánsson^Hjalti^^^dr.|RÖNTGENLÆKNIR
AIL|1|A|RAD^SEGULÓMUN^03^RÖNTGENDEILD LANDSPÍTALA
```

---

## 11. ADT^A04 - Radiology patient registration

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250320080000||ADT^A04|MSG00011|P|2.4
EVN|A04|20250320080000
PID|1||2811944216^^^ÞJÓÐSKRÁ^KT||Þorláksson^Bjarki^^^hr.||19941128|M|||Hjarðarhagi 23^^Reykjavík^^107^IS||+3545387012|||S||PAT20250320-001
PV1|1|O|RAD^RÖNTGEN^01||||^Þorgrímsdóttir^Hekla^^^dr.|||RAD||||||||V00078901|||||||||||||||||||||||||20250320080000
NK1|1|Þorláksdóttir^Sigríður^^^frú|SPO^Maki|Hjarðarhagi 23^^Reykjavík^^107^IS|+3545387013
IN1|1|SÍ^Sjúkratryggingar Íslands|SÍ001|Sjúkratryggingar Íslands|Vínlandsleið 16^^Reykjavík^^105^IS|+3545154400|||||||||||Þorláksson^Bjarki|SELF|19941128
```

---

## 12. ADT^A08 - Update radiology patient

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250320084500||ADT^A08|MSG00012|P|2.4
EVN|A08|20250320084500
PID|1||2811944216^^^ÞJÓÐSKRÁ^KT||Þorláksson^Bjarki^^^hr.||19941128|M|||Hverafold 11^^Reykjavík^^112^IS||+3545387089|||S||PAT20250320-001
PV1|1|O|RAD^RÖNTGEN^01||||^Þorgrímsdóttir^Hekla^^^dr.|||RAD||||||||V00078901|||||||||||||||||||||||||20250320080000
```

---

## 13. ORU^R01 - Mammography report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250321153000||ORU^R01|MSG00013|P|2.4
PID|1||1006733091^^^ÞJÓÐSKRÁ^KT||Egilsdóttir^Þórný^^^frú||19730610|F|||Sunnubraut 16^^Reykjanesbær^^230^IS||+3544203814|||W
PV1|1|O|RAD^BRJÓSTAMYNDUN^04||||^Halldórsdóttir^Yrsa^^^dr.|||RAD||||||||V00089012|||||||||||||||||||||||||20250321140000
ORC|RE|ORD20250321-005|FIL20250321-005||CM|||1^^^20250321140000^^R||20250321153000|^Halldórsdóttir^Yrsa^^^dr.
OBR|1|ORD20250321-005|FIL20250321-005|MAMM^Brjóstamyndun^RAFÖRNINN|||20250321140000|||||||||^Halldórsdóttir^Yrsa^^^dr.||||||20250321153000|||F
OBX|1|FT|REPORT^Niðurstaða||Tvíhliða brjóstamyndun framkvæmd. Brjóstavefur er þéttur (ACR flokkur C). Engin æxlisgrunsamleg fyrirferð sést. Engar örkalkanir greinast. Eitlar í holhöndum eðlilegir.||||||F
OBX|2|FT|BIRADS^BI-RADS flokkun||BI-RADS 1 - Eðlilegt. Endurkomurannsókn eftir 2 ár.||||||F
OBX|3|FT|CONCLUSION^Álitun||Eðlileg brjóstamyndun. BI-RADS 1.||||||F
```

---

## 14. ORU^R01 - Fluoroscopy report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250322110000||ORU^R01|MSG00014|P|2.4
PID|1||2008812435^^^ÞJÓÐSKRÁ^KT||Hauksson^Frosti^^^hr.||19810820|M|||Brúnavegur 14^^Reykjavík^^104^IS||+3545628701|||M
PV1|1|O|RAD^GEGNSKIN^05||||^Þrastardóttir^Iðunn^^^dr.|||RAD||||||||V00090123|||||||||||||||||||||||||20250322090000
ORC|RE|ORD20250322-006|FIL20250322-006||CM|||1^^^20250322090000^^R||20250322110000|^Þrastardóttir^Iðunn^^^dr.
OBR|1|ORD20250322-006|FIL20250322-006|FLKV^Gegnskin af kvið - barýuminnhelling^RAFÖRNINN|||20250322090000|||||||||^Þrastardóttir^Iðunn^^^dr.||||||20250322110000|||F
OBX|1|FT|REPORT^Niðurstaða||Barýuminnhelling framkvæmd. Vélinda eðlilegur, engin þrenging eða slímhúðarbreytingar. Magi fyllst eðlilega, engin sárasjúkdómur. Skeifugörn eðlileg. Þarmahreyfingar eðlilegar.||||||F
OBX|2|FT|CONCLUSION^Álitun||Eðlilegt gegnskin af efri meltingarvegi. Engar sjúklegar breytingar.||||||F
```

---

## 15. ORM^O01 - PET-CT order

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250323080000||ORM^O01|MSG00015|P|2.4
PID|1||1604762839^^^ÞJÓÐSKRÁ^KT||Brynjólfsdóttir^Una^^^frú||19760416|F|||Holtsbúð 3^^Garðabær^^210^IS||+3545829314|||M
PV1|1|I|RAD^KJARNALÆKNISFRÆÐI^06||||^Snorrason^Heiðar^^^dr.|||RAD||||||||V00101234|||||||||||||||||||||||||20250323080000
ORC|NW|ORD20250323-007|FIL20250323-007||SC|||1^^^20250323080000^^R||20250323080000|^Snorrason^Heiðar^^^dr.||^Snorrason^Heiðar^^^dr.|RÖNTGENDEILD LANDSPÍTALA
OBR|1|ORD20250323-007|FIL20250323-007|PETCT^PET-CT heilkroppsrannsókn^RAFÖRNINN|||20250323080000||||||||^Snorrason^Heiðar^^^dr.||||||20250323080000|||1^^^20250323080000^^R||^Stigun á lungnaæxli, grunur um meinvörp
```

---

## 16. ORU^R01 - PET-CT report

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250323163000||ORU^R01|MSG00016|P|2.4
PID|1||1604762839^^^ÞJÓÐSKRÁ^KT||Brynjólfsdóttir^Una^^^frú||19760416|F|||Holtsbúð 3^^Garðabær^^210^IS||+3545829314|||M
PV1|1|I|RAD^KJARNALÆKNISFRÆÐI^06||||^Snorrason^Heiðar^^^dr.|||RAD||||||||V00101234|||||||||||||||||||||||||20250323080000
ORC|RE|ORD20250323-007|FIL20250323-007||CM|||1^^^20250323080000^^R||20250323163000|^Sigfúsdóttir^Bríet^^^dr.
OBR|1|ORD20250323-007|FIL20250323-007|PETCT^PET-CT heilkroppsrannsókn^RAFÖRNINN|||20250323080000|||||||||^Snorrason^Heiðar^^^dr.||||||20250323163000|||F
OBX|1|FT|REPORT^Niðurstaða||FDG PET-CT heilkroppsrannsókn. Fyrirferð í hægra efra lungnakviku, 3.2 x 2.8 cm, með auknu FDG-upptöku (SUVmax 8.4). Eitlastækkun í miðmæti hægra megin, stærsti eitill 1.5 cm, SUVmax 4.2. Engin merki um fjarmeinvörp í lifur, nýrnahettu, beinum eða heila.||||||F
OBX|2|FT|CONCLUSION^Álitun||Fyrirferð í hægra lunga með mikilli FDG-upptöku, samrýmist frumæxli. Eitlastækkun í miðmæti bendir til svæðisbundinna meinvarpa (N2). Stig: T2a N2 M0.||||||F
```

---

## 17. ORU^R01 - Radiology report with base64 ED OBX (PDF report)

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250324120000||ORU^R01|MSG00017|P|2.4
PID|1||2406931064^^^ÞJÓÐSKRÁ^KT||Klemensson^Vagn^^^hr.||19930624|M|||Stigahlíð 14^^Reykjavík^^105^IS||+3545204918|||S
PV1|1|O|RAD^RÖNTGEN^01||||^Vilbergsdóttir^Þórdís^^^dr.|||RAD||||||||V00112345|||||||||||||||||||||||||20250324090000
ORC|RE|ORD20250324-008|FIL20250324-008||CM|||1^^^20250324090000^^R||20250324120000|^Marteinsson^Heimir^^^dr.
OBR|1|ORD20250324-008|FIL20250324-008|CTTH^Tölvusneiðmynd af brjóstholi^RAFÖRNINN|||20250324090000|||||||||^Vilbergsdóttir^Þórdís^^^dr.||||||20250324120000|||F
OBX|1|FT|REPORT^Niðurstaða||Lungnavefur eðlilegur. Engin fyrirferð eða íferð. Hjarta og stór æðar eðlileg. Vélindi og berkjur eðlileg. Beingerð eðlileg.||||||F
OBX|2|FT|CONCLUSION^Álitun||Eðlileg tölvusneiðmynd af brjóstholi.||||||F
OBX|3|ED|PDF^Radiology Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFJhZm9ybmlubiAtIFJhZGlvbG9neSBSZXBvcnQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1MCAwMDAwMCBuIAowMDAwMDAwMjI5IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNQovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMzIzCiUlRU9GCg==||||||F
```

---

## 18. ORU^R01 - CT angiography with base64 ED OBX (PDF)

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|HEKLA|LANDSPÍTALI|20250325143000||ORU^R01|MSG00018|P|2.4
PID|1||2410861783^^^ÞJÓÐSKRÁ^KT||Friðjónsdóttir^Halla^^^frú||19861024|F|||Suðurmýri 9^^Seltjarnarnes^^170^IS||+3545610382|||M
PV1|1|I|RAD^SNEIÐMYND^02||||^Skúlason^Davíð^^^dr.|||RAD||||||||V00123456|||||||||||||||||||||||||20250325100000
ORC|RE|ORD20250325-009|FIL20250325-009||CM|||1^^^20250325100000^^R||20250325143000|^Þorgrímsdóttir^Hekla^^^dr.
OBR|1|ORD20250325-009|FIL20250325-009|CTANG^CT-æðamyndataka^RAFÖRNINN|||20250325100000|||||||||^Skúlason^Davíð^^^dr.||||||20250325143000|||F
OBX|1|FT|REPORT^Niðurstaða||CT-æðamyndataka af ósæð og útlægum slagæðum. Ósæð eðlileg, enginn ósæðargúlpur. Nýrnaæðar tvíhliða opnar. Mjaðmaæðar og lærleggsslagæðar opnar. Engin merki um stíflu eða þrengingu. Kalkanir í hnjáliðsæðum beggja vegna, engin marktæk þrenging.||||||F
OBX|2|FT|CONCLUSION^Álitun||Engin marktæk æðaþrenging. Vægar kalkanir í hnjáliðsæðum.||||||F
OBX|3|ED|PDF^Radiology Report||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1OAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFJhZm9ybmlubiAtIENUIEFlZGFteW5kYXRha2EgUmVwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNTAgMDAwMDAgbiAKMDAwMDAwMDIyOSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjMzNwolJUVPRgo=||||||F
```

---

## 19. MDM^T02 - Radiology addendum

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250326091500||MDM^T02|MSG00019|P|2.4
EVN|T02|20250326091500
PID|1||1408903127^^^ÞJÓÐSKRÁ^KT||Bárðarson^Hróar^^^hr.||19900814|M|||Hraunteigur 6^^Reykjavík^^105^IS||+3545671203|||S
PV1|1|O|RAD^RÖNTGEN^01||||^Vilbergsdóttir^Þórdís^^^dr.|||RAD||||||||V00012345
TXA|1|RAD^Röntgenskýrsla|TX|20250326091500|^Marteinsson^Heimir^^^dr.||20250326091500|20250326091500||^Marteinsson^Heimir^^^dr.||DOC20250326-001||||AU|||AD^Viðauki
OBX|1|FT|ADDENDUM^Viðauki||Viðauki við röntgenmynd af brjóstkassa frá 14.03.2025 (ORD20250314-001). Eftir frekari skoðun á myndum sést lítil 5mm hnúta í hægra neðra lungnakviku sem ekki var lýst í upphaflegu niðurstöðu. Mælt með eftirfylgni með tölvusneiðmynd eftir 3 mánuði.||||||F
```

---

## 20. ORM^O01 - Interventional radiology order

```
MSH|^~\&|RAFÖRNINN|RÖNTGENDEILD LANDSPÍTALA|SAGA|LANDSPÍTALI|20250327071500||ORM^O01|MSG00020|P|2.4
PID|1||1207813526^^^ÞJÓÐSKRÁ^KT||Magnason^Þorgeir^^^hr.||19810712|M|||Vesturbraut 8^^Hafnarfjörður^^220^IS||+3545643018|||M
PV1|1|I|RAD^INNGRIPSMYNDGREINING^07||||^Stefánsson^Hjalti^^^dr.|||RAD||||||||V00134567|||||||||||||||||||||||||20250327071500
ORC|NW|ORD20250327-010|FIL20250327-010||SC|||1^^^20250327071500^^R||20250327071500|^Stefánsson^Hjalti^^^dr.||^Stefánsson^Hjalti^^^dr.|RÖNTGENDEILD LANDSPÍTALA
OBR|1|ORD20250327-010|FIL20250327-010|IRAB^Inngripsmyndgreining - æðavíkkun á nýrnaslagæð^RAFÖRNINN|||20250327071500||||||||^Stefánsson^Hjalti^^^dr.||||||20250327071500|||1^^^20250327071500^^R||^Nýrnaslagæðarþrenging, illstjórnlegur háþrýstingur
```
