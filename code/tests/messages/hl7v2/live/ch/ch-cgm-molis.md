# CGM MOLIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Laborauftrag Hämatologie (hematology order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260301083000||ORM^O01^ORM_O01|MOLIS00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700001^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Brunner^Karl^Otto^^Herr||19650415|M|||Birkenstrasse 155^^Solothurn^^4500^CH||^^CP^0784511915
PV1||I|MED^Zimmer 301^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30001
ORC|NW|ORD700^^^KISIM|||||^^^20260301090000^^R||20260301083000|ARZ300^Meyer^Petra^^^Dr.^med.
OBR|1|ORD700^^^KISIM||CBC^Blutbild komplett^LN|||20260301083000||||A|||||ARZ300^Meyer^Petra^^^Dr.^med.
```

---

## 2. ORU^R01 - Hämatologie-Befund (hematology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260301150000||ORU^R01^ORU_R01|MOLIS00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700001^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Brunner^Karl^Otto^^Herr||19650415|M|||Birkenstrasse 155^^Solothurn^^4500^CH||^^CP^0784511915
PV1||I|MED^Zimmer 301^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30001
OBR|1|ORD700^^^KISIM|RES700^^^MOLIS|CBC^Blutbild komplett^LN|||20260301083000|||||||||ARZ300^Meyer^Petra^^^Dr.^med.||||||20260301150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||142|g/L|135-175|N|||F
OBX|2|NM|6690-2^Leukozyten^LN||8.1|10*9/L|4.0-10.0|N|||F
OBX|3|NM|789-8^Thrombozyten^LN||235|10*9/L|150-400|N|||F
OBX|4|NM|787-2^Erythrozyten^LN||4.8|10*12/L|4.3-5.8|N|||F
OBX|5|NM|4544-3^Hämatokrit^LN||0.42|L/L|0.40-0.52|N|||F
```

---

## 3. ORM^O01 - Laborauftrag Klinische Chemie (clinical chemistry order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260305083000||ORM^O01^ORM_O01|MOLIS00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700002^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Meier^Susanne^Helene^^Frau||19780212|F|||Schulstrasse 179^^Chur^^7000^CH||^^PH^0817866222
PV1||I|NEURO^Zimmer 502^Bett B^Neurologie||||ARZ301^Glaus^Silvia^^^Dr.^med.||||||||||||FALL30002
ORC|NW|ORD701^^^KISIM|||||^^^20260305090000^^R||20260305083000|ARZ301^Glaus^Silvia^^^Dr.^med.
OBR|1|ORD701^^^KISIM||24323-8^Bilan hépatique complet^LN|||20260305083000||||A|||||ARZ301^Glaus^Silvia^^^Dr.^med.
OBR|2|ORD701^^^KISIM||2160-0^Nierenprofil^LN|||20260305083000||||A|||||ARZ301^Glaus^Silvia^^^Dr.^med.
```

---

## 4. ORU^R01 - Klinische Chemie-Befund (clinical chemistry result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260305160000||ORU^R01^ORU_R01|MOLIS00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700002^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Meier^Susanne^Helene^^Frau||19780212|F|||Schulstrasse 179^^Chur^^7000^CH||^^PH^0817866222
PV1||I|NEURO^Zimmer 502^Bett B^Neurologie||||ARZ301^Glaus^Silvia^^^Dr.^med.||||||||||||FALL30002
OBR|1|ORD701^^^KISIM|RES701^^^MOLIS|24323-8^Bilan hépatique complet^LN|||20260305083000|||||||||ARZ301^Glaus^Silvia^^^Dr.^med.||||||20260305160000|||F
OBX|1|NM|1742-6^ALAT (GPT)^LN||32|U/L|7-56|N|||F
OBX|2|NM|1920-8^ASAT (GOT)^LN||25|U/L|10-40|N|||F
OBX|3|NM|2160-0^Kreatinin^LN||88|umol/L|62-106|N|||F
OBX|4|NM|3094-0^Harnstoff^LN||5.8|mmol/L|2.8-7.2|N|||F
OBX|5|NM|2823-3^Kalium^LN||4.0|mmol/L|3.5-5.1|N|||F
OBX|6|NM|2951-2^Natrium^LN||140|mmol/L|136-145|N|||F
```

---

## 5. ORM^O01 - Laborauftrag Gerinnung (coagulation order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260310083000||ORM^O01^ORM_O01|MOLIS00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700003^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Kaufmann^Jakob^Walter^^Herr||19500820|M|||Tessinerplatz 54^^Bern^^3001^CH||^^PH^0314246798
PV1||I|KARD^Zimmer 601^Bett A^Kardiologie||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.||||||||||||FALL30003
ORC|NW|ORD702^^^KISIM|||||^^^20260310090000^^R||20260310083000|ARZ302^Schmid^Helene^^^Prof.^Dr.^med.
OBR|1|ORD702^^^KISIM||COAG^Gerinnungsprofil^LN|||20260310083000||||A|||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.
```

---

## 6. ORU^R01 - Gerinnungs-Befund (coagulation result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260310150000||ORU^R01^ORU_R01|MOLIS00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700003^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Kaufmann^Jakob^Walter^^Herr||19500820|M|||Tessinerplatz 54^^Bern^^3001^CH||^^PH^0314246798
PV1||I|KARD^Zimmer 601^Bett A^Kardiologie||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.||||||||||||FALL30003
OBR|1|ORD702^^^KISIM|RES702^^^MOLIS|COAG^Gerinnungsprofil^LN|||20260310083000|||||||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.||||||20260310150000|||F
OBX|1|NM|5902-2^Prothrombinzeit (Quick)^LN||85|%|70-120|N|||F
OBX|2|NM|6301-6^INR^LN||1.1||0.8-1.2|N|||F
OBX|3|NM|3173-2^aPTT^LN||32|s|25-37|N|||F
OBX|4|NM|3255-7^Fibrinogen^LN||3.2|g/L|2.0-4.0|N|||F
```

---

## 7. ORM^O01 - Laborauftrag Mikrobiologie (microbiology order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260315083000||ORM^O01^ORM_O01|MOLIS00007|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700004^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Vogel^Barbara^Margrit^^Frau||19680318|F|||Buchenstrasse 144^^Frauenfeld^^8500^CH||^^CP^0787229713
PV1||I|MED^Zimmer 305^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30004
ORC|NW|ORD703^^^KISIM|||||^^^20260315090000^^R||20260315083000|ARZ300^Meyer^Petra^^^Dr.^med.
OBR|1|ORD703^^^KISIM||87040^Blutkultur^LN|||20260315060000||||A|||||ARZ300^Meyer^Petra^^^Dr.^med.
```

---

## 8. ORU^R01 - Mikrobiologie-Befund (microbiology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260317160000||ORU^R01^ORU_R01|MOLIS00008|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700004^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Vogel^Barbara^Margrit^^Frau||19680318|F|||Buchenstrasse 144^^Frauenfeld^^8500^CH||^^CP^0787229713
PV1||I|MED^Zimmer 305^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30004
OBR|1|ORD703^^^KISIM|RES703^^^MOLIS|87040^Blutkultur^LN|||20260315060000|||||||||ARZ300^Meyer^Petra^^^Dr.^med.||||||20260317160000|||F
OBX|1|ST|600-7^Bakterien identifiziert^LN||Streptococcus pneumoniae||||||F
OBX|2|ST|18862-3^Amoxicillin^LN||S||||||F
OBX|3|ST|18906-8^Penicillin G^LN||S||||||F
OBX|4|ST|18928-2^Gentamicin^LN||S||||||F
OBX|5|ST|18878-9^Erythromycin^LN||R||||||F
```

---

## 9. ORU^R01 - Laborbericht mit PDF (lab report with embedded PDF)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260320110000||ORU^R01^ORU_R01|MOLIS00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700001^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Brunner^Karl^Otto^^Herr||19650415|M|||Birkenstrasse 155^^Solothurn^^4500^CH||^^CP^0784511915
PV1||I|MED^Zimmer 301^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30001
OBR|1|ORD704^^^KISIM|RES704^^^MOLIS|11502-2^Gesamtlaborbericht^LN|||20260320080000|||||||||ARZ300^Meyer^Petra^^^Dr.^med.||||||20260320110000|||F
OBX|1|ED|11502-2^Gesamtlaborbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEdlc2FtdGxhYm9yYmVyaWNodCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNTAKJSVFT0YK||||||F
```

---

## 10. ORU^R01 - Kumulativbefund mit eingebettetem Bild (cumulative report with image)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260322100000||ORU^R01^ORU_R01|MOLIS00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700004^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Vogel^Barbara^Margrit^^Frau||19680318|F|||Buchenstrasse 144^^Frauenfeld^^8500^CH||^^CP^0787229713
PV1||I|MED^Zimmer 305^Bett A^Innere Medizin||||ARZ300^Meyer^Petra^^^Dr.^med.||||||||||||FALL30004
OBR|1|ORD705^^^KISIM|RES705^^^MOLIS|49765-1^Blutausstrich^LN|||20260322060000|||||||||ARZ300^Meyer^Petra^^^Dr.^med.||||||20260322100000|||F
OBX|1|FT|49765-1^Blutausstrich Befund^LN||Blutausstrich: Normochrome, normozytäre Erythrozyten\.br\Leukozyten morphologisch unauffällig\.br\Thrombozyten in normaler Anzahl||||||F
OBX|2|ED|49765-1^Blutausstrich Bild^LN|IMG|^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM
DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQU
FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAACAAIDASIAAhEBAxEB/8QAHwAA
AQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcI||||||F
```

---

## 11. ORM^O01 - Laborauftrag Serologie (serology order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260325083000||ORM^O01^ORM_O01|MOLIS00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700005^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Burgener^Martin^Helene^^Herr||19750615|M|||Seefeldstrasse 11^^Solothurn^^4500^CH||^^CP^0791881781
PV1||I|INFEKT^Zimmer 401^Bett A^Infektiologie||||ARZ303^Stauffer^Therese^^^Dr.^med.||||||||||||FALL30005
ORC|NW|ORD706^^^KISIM|||||^^^20260325090000^^R||20260325083000|ARZ303^Stauffer^Therese^^^Dr.^med.
OBR|1|ORD706^^^KISIM||SERO^Hepatitis-Serologie^LN|||20260325083000||||A|||||ARZ303^Stauffer^Therese^^^Dr.^med.
```

---

## 12. ORU^R01 - Serologie-Befund (serology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260325160000||ORU^R01^ORU_R01|MOLIS00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700005^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Burgener^Martin^Helene^^Herr||19750615|M|||Seefeldstrasse 11^^Solothurn^^4500^CH||^^CP^0791881781
PV1||I|INFEKT^Zimmer 401^Bett A^Infektiologie||||ARZ303^Stauffer^Therese^^^Dr.^med.||||||||||||FALL30005
OBR|1|ORD706^^^KISIM|RES706^^^MOLIS|SERO^Hepatitis-Serologie^LN|||20260325083000|||||||||ARZ303^Stauffer^Therese^^^Dr.^med.||||||20260325160000|||F
OBX|1|ST|5196-1^HBsAg^LN||Negativ||Negativ||||F
OBX|2|ST|16935-9^Anti-HBs^LN||Positiv (>100 mIU/mL)||Positiv||||F
OBX|3|ST|5199-5^Anti-HCV^LN||Negativ||Negativ||||F
OBX|4|ST|7905-3^Anti-HAV IgG^LN||Positiv||||||F
```

---

## 13. ORM^O01 - Laborauftrag Toxikologie (toxicology order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260401083000||ORM^O01^ORM_O01|MOLIS00013|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700006^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Schneider^Monika^Sophie^^Frau||19900110|F|||Tannenstrasse 135^^Aarau^^5000^CH||^^CP^0777458603
PV1||E|NOTFALL^Box 5^^Notfallstation||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.||||||||||||FALL30006
ORC|NW|ORD707^^^KISIM|||||^^^20260401090000^^S||20260401083000|ARZ304^Hofmann^Elisabeth^^^Dr.^med.
OBR|1|ORD707^^^KISIM||TOX^Drogenscreening Urin^LN|||20260401083000||||A|||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.
```

---

## 14. ORU^R01 - Toxikologie-Befund (toxicology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260401120000||ORU^R01^ORU_R01|MOLIS00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700006^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Schneider^Monika^Sophie^^Frau||19900110|F|||Tannenstrasse 135^^Aarau^^5000^CH||^^CP^0777458603
PV1||E|NOTFALL^Box 5^^Notfallstation||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.||||||||||||FALL30006
OBR|1|ORD707^^^KISIM|RES707^^^MOLIS|TOX^Drogenscreening Urin^LN|||20260401083000|||||||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.||||||20260401120000|||F
OBX|1|ST|3397-7^Benzodiazepine Urin^LN||Negativ||Negativ||||F
OBX|2|ST|3426-4^Opiate Urin^LN||Negativ||Negativ||||F
OBX|3|ST|19658-4^Cannabinoide Urin^LN||Negativ||Negativ||||F
OBX|4|ST|3349-8^Kokain-Metabolit Urin^LN||Negativ||Negativ||||F
OBX|5|ST|3373-8^Amphetamine Urin^LN||Negativ||Negativ||||F
```

---

## 15. ORU^R01 - Blutgasanalyse (blood gas analysis result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260403100000||ORU^R01^ORU_R01|MOLIS00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700006^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Schneider^Monika^Sophie^^Frau||19900110|F|||Tannenstrasse 135^^Aarau^^5000^CH||^^CP^0777458603
PV1||E|NOTFALL^Box 5^^Notfallstation||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.||||||||||||FALL30006
OBR|1|ORD708^^^KISIM|RES708^^^MOLIS|BGA^Blutgasanalyse^LN|||20260403095000|||||||||ARZ304^Hofmann^Elisabeth^^^Dr.^med.||||||20260403100000|||F
OBX|1|NM|2744-1^pH arteriell^LN||7.38||7.35-7.45|N|||F
OBX|2|NM|2019-8^pCO2 arteriell^LN||5.1|kPa|4.7-6.0|N|||F
OBX|3|NM|2703-7^pO2 arteriell^LN||12.5|kPa|10.0-13.3|N|||F
OBX|4|NM|1960-4^Bicarbonat^LN||24|mmol/L|22-26|N|||F
OBX|5|NM|1925-7^Base Excess^LN||-0.5|mmol/L|-2.0-2.0|N|||F
```

---

## 16. ORM^O01 - Laborauftrag Endokrinologie (endocrinology order)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260405083000||ORM^O01^ORM_O01|MOLIS00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700007^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Gerber^Doris^Hans^^Frau||19560930|F|||Gerechtigkeitsgasse 95^^Zug^^6300^CH||^^PH^0417860837
PV1||O|AMB^Sprechzimmer 3^^Endokrinologie||||ARZ305^Widmer^Ruth^^^Dr.^med.||||||||||||FALL30007
ORC|NW|ORD709^^^KISIM|||||^^^20260405090000^^R||20260405083000|ARZ305^Widmer^Ruth^^^Dr.^med.
OBR|1|ORD709^^^KISIM||ENDO^Schilddrüsenprofil^LN|||20260405083000||||A|||||ARZ305^Widmer^Ruth^^^Dr.^med.
```

---

## 17. ORU^R01 - Endokrinologie-Befund (endocrinology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260405160000||ORU^R01^ORU_R01|MOLIS00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700007^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Gerber^Doris^Hans^^Frau||19560930|F|||Gerechtigkeitsgasse 95^^Zug^^6300^CH||^^PH^0417860837
PV1||O|AMB^Sprechzimmer 3^^Endokrinologie||||ARZ305^Widmer^Ruth^^^Dr.^med.||||||||||||FALL30007
OBR|1|ORD709^^^KISIM|RES709^^^MOLIS|ENDO^Schilddrüsenprofil^LN|||20260405083000|||||||||ARZ305^Widmer^Ruth^^^Dr.^med.||||||20260405160000|||F
OBX|1|NM|3016-3^TSH^LN||8.5|mIU/L|0.27-4.2|HH|||F
OBX|2|NM|3024-7^fT4^LN||9.8|pmol/L|12.0-22.0|L|||F
OBX|3|NM|3053-6^fT3^LN||3.1|pmol/L|3.1-6.8|N|||F
```

---

## 18. ORU^R01 - Urinanalyse (urinalysis result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260407100000||ORU^R01^ORU_R01|MOLIS00018|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700003^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Kaufmann^Jakob^Walter^^Herr||19500820|M|||Tessinerplatz 54^^Bern^^3001^CH||^^PH^0314246798
PV1||I|KARD^Zimmer 601^Bett A^Kardiologie||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.||||||||||||FALL30003
OBR|1|ORD710^^^KISIM|RES710^^^MOLIS|24357-6^Urinstatus^LN|||20260407060000|||||||||ARZ302^Schmid^Helene^^^Prof.^Dr.^med.||||||20260407100000|||F
OBX|1|ST|5811-5^Urin pH^LN||6.0||5.0-8.0|N|||F
OBX|2|ST|2965-2^Urin spezifisches Gewicht^LN||1.018||1.005-1.030|N|||F
OBX|3|ST|5804-0^Urin Protein^LN||Negativ||Negativ||||F
OBX|4|ST|5794-3^Urin Glukose^LN||Negativ||Negativ||||F
OBX|5|ST|5799-2^Urin Leukozyten^LN||Negativ||Negativ||||F
```

---

## 19. ORU^R01 - Immunologie-Befund (immunology result)

```
MSH|^~\&|MOLIS|USB_BASEL|KISIM|USB_BASEL|20260409150000||ORU^R01^ORU_R01|MOLIS00019|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT700002^^^USB&2.16.756.5.30.1.170.1&ISO^MR||Meier^Susanne^Helene^^Frau||19780212|F|||Schulstrasse 179^^Chur^^7000^CH||^^PH^0817866222
PV1||I|NEURO^Zimmer 502^Bett B^Neurologie||||ARZ301^Glaus^Silvia^^^Dr.^med.||||||||||||FALL30002
OBR|1|ORD711^^^KISIM|RES711^^^MOLIS|IMMU^Immunologie Panel^LN|||20260409083000|||||||||ARZ301^Glaus^Silvia^^^Dr.^med.||||||20260409150000|||F
OBX|1|NM|2465-3^IgG^LN||12.5|g/L|7.0-16.0|N|||F
OBX|2|NM|2472-9^IgA^LN||2.8|g/L|0.7-4.0|N|||F
OBX|3|NM|2458-8^IgM^LN||1.1|g/L|0.4-2.3|N|||F
OBX|4|NM|17861-6^CRP^LN||3.2|mg/L|0-5|N|||F
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|KISIM|USB_BASEL|MOLIS|USB_BASEL|20260410080100||ACK^O01^ACK|ACK30001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|MOLIS00002|Ergebnis erfolgreich empfangen
```
