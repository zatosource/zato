# Therapy - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Rehabilitation admission

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240315091200||ADT^A01|MSG00001|P|2.4
EVN|A01|20240315091200
PID|1||1909873524^^^KENNITALA||Vésteinsson^Hjörtur^^^hr.||19870919|M|||Háaleitisbraut 27^^Reykjavík^^108^IS||+3545821304|||IS||||||||||||N
PV1|1|I|REHAB^201^01||||1234^Þorgrímsdóttir^Iðunn^^^dr.|||PHYS||||1||THERAPY||||||||||||||||||||||||||20240315091200
DG1|1||M54.5^Lágverkur^ICD-10|||A
```

---

## 2. ADT^A03 - Rehabilitation discharge

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240402160000||ADT^A03|MSG00002|P|2.4
EVN|A03|20240402160000
PID|1||0407742681^^^KENNITALA||Brynjólfsdóttir^Védís^^^frú||19740704|F|||Lerkimói 11^^Mosfellsbær^^270^IS||+3545930128|||IS||||||||||||N
PV1|1|I|REHAB^105^02||||5678^Hauksson^Birkir^^^dr.|||OT||||1||THERAPY||||||||||||||||||||||||||20240301080000|20240402160000
DG1|1||S72.0^Lærleggsbrot^ICD-10|||A
```

---

## 3. ADT^A04 - Outpatient therapy registration

```
MSH|^~\&|THERAPY|SIBS|HEKLA|SIBS|20240418083000||ADT^A04|MSG00003|P|2.4
EVN|A04|20240418083000
PID|1||1110912547^^^KENNITALA||Egilsdóttir^Lóa^^^frú||19911011|F|||Holtsbúð 8^^Garðabær^^210^IS||+3545672409|||IS||||||||||||N
PV1|1|O|OUTPT^PT^01||||2345^Marteinsson^Snæbjörn^^^sjúkraþj.|||PT||||1||THERAPY||||||||||||||||||||||||||20240418083000
```

---

## 4. ADT^A08 - Update therapy patient

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240420101500||ADT^A08|MSG00004|P|2.4
EVN|A08|20240420101500
PID|1||1909873524^^^KENNITALA||Vésteinsson^Hjörtur^^^hr.||19870919|M|||Sólheimar 16^^Reykjavík^^104^IS||+3545719042|||IS||||||||||||N
PV1|1|I|REHAB^201^01||||1234^Þorgrímsdóttir^Iðunn^^^dr.|||PHYS||||1||THERAPY||||||||||||||||||||||||||20240315091200
```

---

## 5. ORM^O01 - Physiotherapy referral order

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240422140000||ORM^O01|MSG00005|P|2.4
PID|1||0808812469^^^KENNITALA||Friðjónsson^Kjarri^^^hr.||19810808|M|||Hraunteigur 15^^Reykjavík^^105^IS||+3545348017|||IS||||||||||||N
ORC|NW|ORD0005|||||1^Once^^^^||20240422140000|1234^Þorgrímsdóttir^Iðunn^^^dr.||||||||GRENSASDEILD
OBR|1|ORD0005||PHYSIO^Sjúkraþjálfun^LOCAL|||20240422140000|||||||||1234^Þorgrímsdóttir^Iðunn^^^dr.|||||||||||1^^^20240425^^R
DG1|1||M54.2^Hálsverkur^ICD-10|||A
```

---

## 6. ORM^O01 - Occupational therapy order

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240423093000||ORM^O01|MSG00006|P|2.4
PID|1||1908683472^^^KENNITALA||Pálmadóttir^Sólrún^^^frú||19680819|F|||Sigtún 6^^Akureyri^^603^IS||+3544668304|||IS||||||||||||N
ORC|NW|ORD0006|||||1^Once^^^^||20240423093000|5678^Hauksson^Birkir^^^dr.||||||||REYKJALUNDUR
OBR|1|ORD0006||OT^Iðjuþjálfun^LOCAL|||20240423093000|||||||||5678^Hauksson^Birkir^^^dr.|||||||||||1^^^20240426^^R
DG1|1||I63.9^Heilablóðfall^ICD-10|||A
```

---

## 7. ORM^O01 - Speech therapy order

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240424110000||ORM^O01|MSG00007|P|2.4
PID|1||0703952148^^^KENNITALA||Gunnsteinsson^Bárður^^^hr.||19950307|M|||Klébergsvegur 11^^Reykjavík^^104^IS||+3545820173|||IS||||||||||||N
ORC|NW|ORD0007|||||1^Once^^^^||20240424110000|1234^Þorgrímsdóttir^Iðunn^^^dr.||||||||GRENSASDEILD
OBR|1|ORD0007||ST^Talþjálfun^LOCAL|||20240424110000|||||||||1234^Þorgrímsdóttir^Iðunn^^^dr.|||||||||||1^^^20240429^^R
DG1|1||R13.1^Kyngingarerfiðleikar^ICD-10|||A
```

---

## 8. SIU^S12 - Schedule therapy session

```
MSH|^~\&|THERAPY|SIBS|HEKLA|SIBS|20240425080000||SIU^S12|MSG00008|P|2.4
SCH|1|APT0008||||PHYSIO^Sjúkraþjálfun^LOCAL|ROUTINE|30|MIN|^^30^20240428090000^20240428093000|1234^Þorgrímsdóttir^Iðunn^^^dr.
PID|1||1110912547^^^KENNITALA||Egilsdóttir^Lóa^^^frú||19911011|F|||Holtsbúð 8^^Garðabær^^210^IS||+3545672409|||IS||||||||||||N
AIG|1||2345^Marteinsson^Snæbjörn^^^sjúkraþj.
AIL|1||SIBS^PT_ROOM_3^01
```

---

## 9. SIU^S14 - Modify therapy appointment

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240426143000||SIU^S14|MSG00009|P|2.4
SCH|1|APT0009||||PHYSIO^Sjúkraþjálfun^LOCAL|ROUTINE|45|MIN|^^45^20240429100000^20240429104500|1234^Þorgrímsdóttir^Iðunn^^^dr.
PID|1||1909873524^^^KENNITALA||Vésteinsson^Hjörtur^^^hr.||19870919|M|||Sólheimar 16^^Reykjavík^^104^IS||+3545719042|||IS||||||||||||N
AIG|1||1234^Þorgrímsdóttir^Iðunn^^^dr.
AIL|1||GRENSAS^REHAB_GYM^01
```

---

## 10. SIU^S12 - Schedule group therapy

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240427090000||SIU^S12|MSG00010|P|2.4
SCH|1|APT0010||||GROUP^Hópmeðferð^LOCAL|ROUTINE|60|MIN|^^60^20240430140000^20240430150000|5678^Hauksson^Birkir^^^dr.
PID|1||0407742681^^^KENNITALA||Brynjólfsdóttir^Védís^^^frú||19740704|F|||Lerkimói 11^^Mosfellsbær^^270^IS||+3545930128|||IS||||||||||||N
PID|2||1908683472^^^KENNITALA||Pálmadóttir^Sólrún^^^frú||19680819|F|||Sigtún 6^^Akureyri^^603^IS||+3544668304|||IS||||||||||||N
AIG|1||5678^Hauksson^Birkir^^^dr.
AIL|1||REYKJA^GROUP_HALL^01
```

---

## 11. ORU^R01 - Therapy assessment report

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240429153000||ORU^R01|MSG00011|P|2.4
PID|1||0808812469^^^KENNITALA||Friðjónsson^Kjarri^^^hr.||19810808|M|||Hraunteigur 15^^Reykjavík^^105^IS||+3545348017|||IS||||||||||||N
OBR|1|ORD0011||PTASSESS^Sjúkraþjálfunarmat^LOCAL|||20240429150000|||||||||2345^Marteinsson^Snæbjörn^^^sjúkraþj.
OBX|1|TX|ROM^Hreyfigeta^LOCAL||Axlarhreyfigeta: Fleyging 0-160 gr, Fráfærsla 0-140 gr||||||F
OBX|2|NM|VAS^Verkjamat^LOCAL||6|/10|||||F
OBX|3|TX|FUNC^Starfsgeta^LOCAL||Erfiðleikar við lyfta hluti yfir höfuð, takmarkaður í daglegum athöfnum||||||F
```

---

## 12. ORU^R01 - Functional outcome measurement

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240501110000||ORU^R01|MSG00012|P|2.4
PID|1||0407742681^^^KENNITALA||Brynjólfsdóttir^Védís^^^frú||19740704|F|||Lerkimói 11^^Mosfellsbær^^270^IS||+3545930128|||IS||||||||||||N
OBR|1|ORD0012||FIM^Functional Independence Measure^LOCAL|||20240501100000|||||||||5678^Hauksson^Birkir^^^dr.
OBX|1|NM|FIM_MOTOR^FIM Hreyfiþáttur^LOCAL||78|/91|||||F
OBX|2|NM|FIM_COG^FIM Vitsmunaþáttur^LOCAL||32|/35|||||F
OBX|3|NM|FIM_TOTAL^FIM Heild^LOCAL||110|/126|||||F
OBX|4|TX|FIM_NOTE^Athugasemd^LOCAL||Marktæk framför frá upphafsmati (FIM 72). Sjálfbjörg í flestum ADL verkefnum.||||||F
```

---

## 13. ORU^R01 - Rehabilitation progress with base64 ED OBX (PDF progress report)

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240503140000||ORU^R01|MSG00013|P|2.4
PID|1||1909873524^^^KENNITALA||Vésteinsson^Hjörtur^^^hr.||19870919|M|||Sólheimar 16^^Reykjavík^^104^IS||+3545719042|||IS||||||||||||N
OBR|1|ORD0013||PROGRESS^Framvinduskýrsla^LOCAL|||20240503130000|||||||||1234^Þorgrímsdóttir^Iðunn^^^dr.
OBX|1|ED|PDF^Framvinduskýrsla endurhæfingar||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2Jq||||||F
```

---

## 14. MDM^T02 - Therapy treatment plan

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240505090000||MDM^T02|MSG00014|P|2.4
EVN|T02|20240505090000
PID|1||1908683472^^^KENNITALA||Pálmadóttir^Sólrún^^^frú||19680819|F|||Sigtún 6^^Akureyri^^603^IS||+3544668304|||IS||||||||||||N
TXA|1|HP|TX|20240505090000|5678^Hauksson^Birkir^^^dr.||||||DOC0014||||||AU
OBX|1|TX|PLAN^Meðferðaráætlun^LOCAL||Iðjuþjálfun 3x/viku í 6 vikur. Markmið: Sjálfstæði í ADL, betri fínhreyfingar vinstri handar. Æfingar: Handþjálfun, ADL þjálfun, aðlögun á heimili.||||||F
```

---

## 15. MDM^T02 - Therapy discharge summary

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240508150000||MDM^T02|MSG00015|P|2.4
EVN|T02|20240508150000
PID|1||0407742681^^^KENNITALA||Brynjólfsdóttir^Védís^^^frú||19740704|F|||Lerkimói 11^^Mosfellsbær^^270^IS||+3545930128|||IS||||||||||||N
TXA|1|DS|TX|20240508150000|5678^Hauksson^Birkir^^^dr.||||||DOC0015||||||AU
OBX|1|TX|DSUM^Útskriftarsamantekt^LOCAL||Sjúklingur útskrifaður eftir 5 vikna endurhæfingu vegna lærleggsbrot. FIM skor hækkað úr 72 í 110. Gengur sjálfstætt með göngugrind. Áframhaldandi sjúkraþjálfun á göngudeild ráðlögð 2x/viku.||||||F
```

---

## 16. ADT^A31 - Update patient demographics

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240509120000||ADT^A31|MSG00016|P|2.4
EVN|A31|20240509120000
PID|1||1110912547^^^KENNITALA||Egilsdóttir^Lóa^^^frú||19911011|F|||Suðurmýri 9^^Seltjarnarnes^^170^IS||+3545611274|||IS||||||||||||N
PV1|1|O|OUTPT^PT^01||||2345^Marteinsson^Snæbjörn^^^sjúkraþj.|||PT||||1||THERAPY||||||||||||||||||||||||||20240418083000
```

---

## 17. ORU^R01 - Pain assessment result

```
MSH|^~\&|THERAPY|GRENSASDEILD|SAGA|LANDSPITALI|20240510094500||ORU^R01|MSG00017|P|2.4
PID|1||0808812469^^^KENNITALA||Friðjónsson^Kjarri^^^hr.||19810808|M|||Hraunteigur 15^^Reykjavík^^105^IS||+3545348017|||IS||||||||||||N
OBR|1|ORD0017||PAIN^Verkjamat^LOCAL|||20240510090000|||||||||2345^Marteinsson^Snæbjörn^^^sjúkraþj.
OBX|1|NM|VAS_REST^Verkir í hvíld^LOCAL||3|/10|||||F
OBX|2|NM|VAS_ACT^Verkir við hreyfingu^LOCAL||7|/10|||||F
OBX|3|TX|PAIN_LOC^Staðsetning verkja^LOCAL||Hægri öxl, útgeislun niður í upphandlegg||||||F
OBX|4|TX|PAIN_CHAR^Eðli verkja^LOCAL||Daufir verkir í hvíld, skarpir við hreyfingu yfir 90 gráður||||||F
```

---

## 18. ORU^R01 - Therapy evaluation with base64 ED OBX (PDF evaluation)

```
MSH|^~\&|THERAPY|SIBS|HEKLA|SIBS|20240512110000||ORU^R01|MSG00018|P|2.4
PID|1||1110912547^^^KENNITALA||Egilsdóttir^Lóa^^^frú||19911011|F|||Suðurmýri 9^^Seltjarnarnes^^170^IS||+3545611274|||IS||||||||||||N
OBR|1|ORD0018||EVAL^Meðferðarmat^LOCAL|||20240512100000|||||||||2345^Marteinsson^Snæbjörn^^^sjúkraþj.
OBX|1|ED|PDF^Matsgerð sjúkraþjálfunar||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2Jq||||||F
```

---

## 19. ADT^A02 - Transfer to rehabilitation ward

```
MSH|^~\&|THERAPY|LANDSPITALI|SAGA|LANDSPITALI|20240514080000||ADT^A02|MSG00019|P|2.4
EVN|A02|20240514080000
PID|1||2306882041^^^KENNITALA||Sturluson^Bragi^^^hr.||19880623|M|||Mánagata 19^^Reykjavík^^105^IS||+3545449302|||IS||||||||||||N
PV1|1|I|ORTH^301^02||||3456^Tryggvadóttir^Eyrún^^^dr.|||ORTH||||1||THERAPY||||||||||||||||||||||||||20240510120000
PV2|||||||||||||||||||||||REHAB^201^01
```

---

## 20. ORM^O01 - Hydrotherapy order

```
MSH|^~\&|THERAPY|REYKJALUNDUR|SAGA|LANDSPITALI|20240515100000||ORM^O01|MSG00020|P|2.4
PID|1||0407742681^^^KENNITALA||Brynjólfsdóttir^Védís^^^frú||19740704|F|||Lerkimói 11^^Mosfellsbær^^270^IS||+3545930128|||IS||||||||||||N
ORC|NW|ORD0020|||||2^Twice per week^^^^||20240515100000|5678^Hauksson^Birkir^^^dr.||||||||REYKJALUNDUR
OBR|1|ORD0020||HYDRO^Sundlaugarmeðferð^LOCAL|||20240515100000|||||||||5678^Hauksson^Birkir^^^dr.|||||||||||1^^^20240520^^R
DG1|1||S72.0^Lærleggsbrot^ICD-10|||A
```
