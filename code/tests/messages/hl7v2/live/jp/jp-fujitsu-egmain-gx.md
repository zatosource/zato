# Fujitsu HOPE EGMAIN-GX - real HL7v2 ER7 messages

---

## 1. ADT^A01 - inpatient admission (入院登録)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260301090000||ADT^A01^ADT_A01|EGMX20260301090000001|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A01|20260301090000
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M|||新潟県新潟市中央区旭町通1-754^^中央区^新潟県^951-8520^JPN^H||^PRN^PH^^81^25^2236161||JPN|M|||||||||||||||||||N
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR|||MED||||A|||V001234|||||||||||||||||||||||||||20260301090000
IN1|1||12345678|国民健康保険|新潟県新潟市中央区学校町通1-602-1||||||||||||||||||||||||||||||||||||||||6
```

---

## 2. ADT^A02 - patient transfer (転棟)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260305140000||ADT^A02^ADT_A02|EGMX20260305140000002|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A02|20260305140000
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M|||新潟県新潟市中央区旭町通1-754^^中央区^新潟県^951-8520^JPN^H||^PRN^PH^^81^25^2236161||JPN|M
PV1||I|5E^502^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR|||MED||3N^301^1^新潟大学病院^^^^N|||||||V001234|||||||||||||||||||||||||||20260305140000
```

---

## 3. ADT^A03 - discharge (退院)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260310100000||ADT^A03^ADT_A03|EGMX20260310100000003|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A03|20260310100000
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M|||新潟県新潟市中央区旭町通1-754^^中央区^新潟県^951-8520^JPN^H||^PRN^PH^^81^25^2236161||JPN|M
PV1||I|5E^502^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR|||MED||||||||V001234|||||||||||||||||||||||||||20260310100000
```

---

## 4. ORM^O01 - pharmacy order (処方オーダ)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|薬剤部|新潟大学病院|20260302080000||ORM^O01^ORM_O01|EGMX20260302080000004|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
ORC|NW|ORD20260302001^EGMAIN-GX||||||||||D001234^本田^一郎^^^^^L^^^DR
RXO|612340101^アムロジピン錠5mg^HOT9|||5||mg||||||||||||||||||D001234^本田^一郎^^^^^L^^^DR
```

---

## 5. OML^O33 - laboratory order (検体検査オーダ)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|検査部|新潟大学病院|20260302083000||OML^O33^OML_O33|EGMX20260302083000005|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
SPM|1|||BLD^血液^HL70487|||||||||||20260302083000
ORC|NW|LAB20260302001^EGMAIN-GX||||||||||D001234^本田^一郎^^^^^L^^^DR
OBR|1|LAB20260302001^EGMAIN-GX||3A010000002327101^HbA1c(NGSP)^JC10|R||20260302083000
```

---

## 6. ORU^R01 - laboratory result (検査結果)

```
MSH|^~\&|検査部|新潟大学病院|EGMAIN-GX|新潟大学病院|20260302150000||ORU^R01^ORU_R01|LAB20260302150000006|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
ORC|RE|LAB20260302001^EGMAIN-GX||||||||||D001234^本田^一郎^^^^^L^^^DR
OBR|1|LAB20260302001^EGMAIN-GX||3A010000002327101^HbA1c(NGSP)^JC10|R||20260302083000|||||||20260302083000||D001234^本田^一郎^^^^^L^^^DR||||||||20260302150000|||F
OBX|1|NM|3A010000002327101^HbA1c(NGSP)^JC10||6.5|%|4.6-6.2|H|||F|||20260302150000
OBX|2|NM|2A040000001930101^空腹時血糖^JC10||126|mg/dL|70-109|H|||F|||20260302150000
OBX|3|NM|2A050000001930101^クレアチニン^JC10||0.82|mg/dL|0.65-1.07|N|||F|||20260302150000
```

---

## 7. ORU^R01 - radiology report with embedded PDF (放射線レポート)

```
MSH|^~\&|放射線部|新潟大学病院|EGMAIN-GX|新潟大学病院|20260303100000||ORU^R01^ORU_R01|RAD20260303100000007|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
ORC|RE|RAD20260303001^EGMAIN-GX
OBR|1|RAD20260303001^EGMAIN-GX||71020^胸部X線2方向^RADLEX|R||20260303090000|||||||20260303090000||D001234^本田^一郎^^^^^L^^^DR||||||||20260303100000|||F
OBX|1|TX|71020^胸部X線2方向^RADLEX|1|心胸比正常範囲内。肺野に明らかな異常陰影認めず。||||||F|||20260303100000
OBX|2|ED|PDF^レポートPDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIwNgolJUVPRgo=||||||F|||20260303100000
```

---

## 8. ADT^A08 - patient information update (患者情報更新)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260306090000||ADT^A08^ADT_A01|EGMX20260306090000008|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A08|20260306090000
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M|||新潟県新潟市中央区旭町通1-754^^中央区^新潟県^951-8520^JPN^H~新潟県新潟市中央区東大通1-7-12^^中央区^新潟県^950-0087^JPN^O||^PRN^PH^^81^25^2236161~^WPN^PH^^81^25^2451234||JPN|M|||||||||||||||||||N
PV1||I|5E^502^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR|||MED||||||||V001234|||||||||||||||||||||||||||20260305140000
IN1|1||12345678|国民健康保険|新潟県新潟市中央区学校町通1-602-1||||||||||||||||||||||||||||||||||||||||6
```

---

## 9. ORM^O01 - radiology order (放射線オーダ)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|放射線部|新潟大学病院|20260303083000||ORM^O01^ORM_O01|EGMX20260303083000009|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
ORC|NW|RAD20260303001^EGMAIN-GX||||||||||D001234^本田^一郎^^^^^L^^^DR
OBR|1|RAD20260303001^EGMAIN-GX||71020^胸部X線2方向^RADLEX|R||20260303083000|||||||20260303083000||D001234^本田^一郎^^^^^L^^^DR
```

---

## 10. ORM^O01 - injection order (注射オーダ)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|薬剤部|新潟大学病院|20260302100000||ORM^O01^ORM_O01|EGMX20260302100000010|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|3N^301^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
ORC|NW|INJ20260302001^EGMAIN-GX||||||||||D001234^本田^一郎^^^^^L^^^DR
RXO|620007301^生理食塩液500mL^HOT9|||500||mL||IV^静脈内^HL70162|||||||||||||||D001234^本田^一郎^^^^^L^^^DR
```

---

## 11. ADT^A04 - outpatient registration (外来受付)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260307080000||ADT^A04^ADT_A01|EGMX20260307080000011|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A04|20260307080000
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F|||新潟県長岡市殿町2-2-6^^長岡市^新潟県^940-0061^JPN^H||^PRN^PH^^81^258^321111||JPN|M
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR|||MED||||A|||V005678|||||||||||||||||||||||||||20260307080000
IN1|1||87654321|社会保険|新潟県新潟市中央区八千代1-3-1||||||||||||||||||||||||||||||||||||||||8
```

---

## 12. ORU^R01 - pathology report with embedded image (病理レポート)

```
MSH|^~\&|病理部|新潟大学病院|EGMAIN-GX|新潟大学病院|20260308160000||ORU^R01^ORU_R01|PATH20260308160000012|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
ORC|RE|PATH20260308001^EGMAIN-GX
OBR|1|PATH20260308001^EGMAIN-GX||88305^病理組織診断^CPT|R||20260307090000|||||||20260307090000||D002345^岡崎^次郎^^^^^L^^^DR||||||||20260308160000|||F
OBX|1|TX|88305^病理組織診断^CPT|1|胃生検：慢性胃炎、腸上皮化生を認める。悪性所見なし。||||||F|||20260308160000
OBX|2|ED|IMG^病理画像^L|1|^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAIAAgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAACf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKYH/9k=||||||F|||20260308160000
```

---

## 13. ADT^A28 - new patient registration (新規患者登録)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|MPI|地域連携|20260301070000||ADT^A28^ADT_A05|EGMX20260301070000013|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|A28|20260301070000
PID|||PAT009012^^^新潟大学病院^PI||後藤^健一^^^^^L||19900715|M|||新潟県上越市本城町8-1^^上越市^新潟県^943-0838^JPN^H||^PRN^PH^^81^25^5252222||JPN|S
```

---

## 14. OMP^O09 - prescription order with multiple medications (複数処方)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|薬剤部|新潟大学病院|20260307090000||OMP^O09^OMP_O09|EGMX20260307090000014|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
ORC|NW|RX20260307001^EGMAIN-GX||||||||||D002345^岡崎^次郎^^^^^L^^^DR
RXO|612170101^メトホルミン塩酸塩錠250mg^HOT9|||250||mg
TQ1|||1^^D&日&JAHIS0001~1^^D&日&JAHIS0001~1^^D&日&JAHIS0001|||||20260307|||30^日^JAHIS0002
ORC|NW|RX20260307002^EGMAIN-GX||||||||||D002345^岡崎^次郎^^^^^L^^^DR
RXO|613990201^アトルバスタチン錠10mg^HOT9|||10||mg
TQ1|||1^^D&日&JAHIS0001|||||20260307|||30^日^JAHIS0002
```

---

## 15. MFN^M02 - physician master update (医師マスタ更新)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260401000000||MFN^M02^MFN_M02|EGMX20260401000000015|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
MFI|PRA^^HL70175||UPD|||NE
MFE|MAD|D003456|20260401000000|D003456^内田^美咲^^^^^L^^^DR^新潟大学病院^CDA
STF|D003456|D003456^^新潟大学病院|内田^美咲^^^^^L||F||||||^WPN^PH^^81^25^2236161
PRA|D003456||I|循環器内科||||||||||||||||||20260401
```

---

## 16. SIU^S12 - appointment scheduled (予約登録)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|外来予約|新潟大学病院|20260306150000||SIU^S12^SIU_S12|EGMX20260306150000016|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
SCH|APT20260310001^EGMAIN-GX|APT20260310001^EGMAIN-GX|||||外来受診^外来予約^L|||||^^30^20260310090000^20260310093000
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
AIG|1||D002345^岡崎^次郎^^^^^L^^^DR
AIL|1||内科外来^1^1^新潟大学病院
```

---

## 17. DFT^P03 - charge posting (診療報酬請求)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|医事会計|新潟大学病院|20260310170000||DFT^P03^DFT_P03|EGMX20260310170000017|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|P03|20260310170000
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
FT1|1|ORD20260310001|20260310|20260310|CG|120^初診料^診療行為コード||1|2880|||||||||||||||D002345^岡崎^次郎^^^^^L^^^DR
FT1|2|ORD20260310002|20260310|20260310|CG|160119910^外来管理加算^診療行為コード||1|520|||||||||||||||D002345^岡崎^次郎^^^^^L^^^DR
```

---

## 18. RDE^O11 - pharmacy dispense event (調剤実施)

```
MSH|^~\&|薬剤部|新潟大学病院|EGMAIN-GX|新潟大学病院|20260307110000||RDE^O11^RDE_O11|PH20260307110000018|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
ORC|RE|RX20260307001^EGMAIN-GX|DSP20260307001^薬剤部|||||||||D002345^岡崎^次郎^^^^^L^^^DR
RXE|^^^20260307^^^日|612170101^メトホルミン塩酸塩錠250mg^HOT9|250||mg|錠|||||||30|||||||||||PH001^大塚^優子^^^^^L^^^RPH
RXD|1|612170101^メトホルミン塩酸塩錠250mg^HOT9|20260307110000|90|錠||||||||||||||PH001^大塚^優子^^^^^L^^^RPH
```

---

## 19. ORU^R01 - endoscopy report (内視鏡レポート)

```
MSH|^~\&|内視鏡部|新潟大学病院|EGMAIN-GX|新潟大学病院|20260312140000||ORU^R01^ORU_R01|ENDO20260312140000019|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
PID|||PAT005678^^^新潟大学病院^PI||遠藤^香織^^^^^L||19780923|F
PV1||O|内科外来^1^1^新潟大学病院^^^^N||||D002345^岡崎^次郎^^^^^L^^^DR
ORC|RE|ENDO20260312001^EGMAIN-GX
OBR|1|ENDO20260312001^EGMAIN-GX||43239^上部消化管内視鏡^CPT|R||20260312100000|||||||20260312100000||D002345^岡崎^次郎^^^^^L^^^DR||||||||20260312140000|||F
OBX|1|TX|43239^上部消化管内視鏡^CPT|1|食道：異常なし。胃：体部に軽度発赤あり。十二指腸：異常なし。||||||F|||20260312140000
OBX|2|TX|43239^上部消化管内視鏡^CPT|2|診断：慢性表層性胃炎（軽度）||||||F|||20260312140000
```

---

## 20. MDM^T02 - clinical document notification with attached CDA (診療文書通知)

```
MSH|^~\&|EGMAIN-GX|新潟大学医歯学総合病院|SS-MIX2|地域連携|20260315120000||MDM^T02^MDM_T02|EGMX20260315120000020|P|2.5||||||~ISO IR87||ISO 2022-1994|JPN
EVN|T02|20260315120000
PID|||PAT001234^^^新潟大学病院^PI||吉田^俊明^^^^^L||19650412|M
PV1||I|5E^502^1^新潟大学病院^^^^N||||D001234^本田^一郎^^^^^L^^^DR
TXA|1|DS^退院時サマリ^HL70270|TX|20260315120000|D001234^本田^一郎^^^^^L^^^DR||20260315120000||||||DOC20260315001||||||AU
OBX|1|ED|DS^退院時サマリ^HL70270|1|^text^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+6YCA6Zmi5pmC44K144Oe44OqPC90aXRsZT4KICA8ZWZmZWN0aXZlVGltZSB2YWx1ZT0iMjAyNjAzMTUiLz4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAgICAgPHRpdGxlPuWFpeemouaZguiouuaWrTwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7nmbrnmb3ooYDnlIMsIOiEguW8j+ezluWwv+eXhTwvdGV4dD4KICAgICAgICA8L3NlY3Rpb24+CiAgICAgIDwvY29tcG9uZW50PgogICAgPC9zdHJ1Y3R1cmVkQm9keT4KICA8L2NvbXBvbmVudD4KPC9DbGluaWNhbERvY3VtZW50Pgo=||||||F|||20260315120000
```
