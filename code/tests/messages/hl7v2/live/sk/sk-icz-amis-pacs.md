# ICZ AMIS PACS - real HL7v2 ER7 messages

## 1. ORM^O01 - Radiology order for chest X-ray

```
MSH|^~\&|HIS|UNB|AMISPACS|RAD_UNB|20260509080000||ORM^O01|HIS20260509001|P|2.3|||AL|NE|SVK|8859/2
PID|||8901154782^^^UNB^PI||Brhel^Zdenko^Dušan^^^L||19890115|M|||Dlhá 7^^Bratislava^^81101^SVK^H
PV1|1|I|INT^201^1|||101234^Šranko^Albín^^^MUDr.
ORC|NW|ORD2026050001^HIS|||||^^^20260509080000^^R||20260509080000|101234^Šranko^Albín^^^MUDr.
OBR|1|ORD2026050001^HIS||71020^RTG hrudníka PA a bočný^CPT|||20260509075000||||WALK|||||101234^Šranko^Albín^^^MUDr.||ACC2026050001||20260509090000|||F
```

---

## 2. ORM^O01 - CT abdomen order (urgent)

```
MSH|^~\&|HIS|UNLP_KE|AMISPACS|RAD_UNLP_KE|20260509083000||ORM^O01|HIS20260509002|P|2.3|||AL|NE|SVK|8859/2
PID|||7560140032^^^UNLP_KE^PI||Koštrnová^Lýdia^Renáta^^^L||19750614|F|||Hlavná 92^^Košice^^04001^SVK^H
PV1|1|E|URG^001^1|||301234^Chrenko^Bruno^^^MUDr.
ORC|NW|ORD2026050002^HIS|||||^^^20260509083000^^S||20260509083000|301234^Chrenko^Bruno^^^MUDr.
OBR|1|ORD2026050002^HIS||74177^CT abdomenu s kontrastom^CPT|||20260509082000||||WHEELCHAIR|||||301234^Chrenko^Bruno^^^MUDr.||ACC2026050002||20260509093000|||S
```

---

## 3. ORU^R01 - Radiology report for chest X-ray

```
MSH|^~\&|AMISPACS|RAD_UNB|HIS|UNB|20260509100000||ORU^R01|PACS20260509001|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
PID|||8901154782^^^UNB^PI||Brhel^Zdenko^Dušan^^^L||19890115|M|||Dlhá 7^^Bratislava^^81101^SVK^H
PV1|1|I|INT^201^1|||101234^Šranko^Albín^^^MUDr.
ORC|RE|ORD2026050001^HIS|RES2026050001^AMISPACS
OBR|1|ORD2026050001^HIS|RES2026050001^AMISPACS|71020^RTG hrudníka PA a bočný^CPT|||20260509075000|||||||||101234^Šranko^Albín^^^MUDr.|||||ACC2026050001|20260509100000|||F
OBX|1|FT|59776-5^Nález^LN||Pľúcne polia primerane prevzdušnené. Bronchovaskulárna kresba primeraná. Srdce a mediastínum bez patologického nálezu. Bránica hladká, kostofrenické uhly voľné. Skeletálne štruktúry bez čerstvých traumatických zmien.||||||F|||20260509095000
OBX|2|FT|59777-3^Záver^LN||RTG hrudníka bez patologického nálezu.||||||F|||20260509095000
```

---

## 4. ORU^R01 - CT abdomen report with embedded PDF (base64)

```
MSH|^~\&|AMISPACS|RAD_UNLP_KE|HIS|UNLP_KE|20260509110000||ORU^R01|PACS20260509002|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
PID|||7560140032^^^UNLP_KE^PI||Koštrnová^Lýdia^Renáta^^^L||19750614|F|||Hlavná 92^^Košice^^04001^SVK^H
PV1|1|E|URG^001^1|||301234^Chrenko^Bruno^^^MUDr.
ORC|RE|ORD2026050002^HIS|RES2026050002^AMISPACS
OBR|1|ORD2026050002^HIS|RES2026050002^AMISPACS|74177^CT abdomenu s kontrastom^CPT|||20260509082000|||||||||301234^Chrenko^Bruno^^^MUDr.|||||ACC2026050002|20260509110000|||F
OBX|1|FT|59776-5^Nález^LN||Pečeň normálnej veľkosti, homogénna. Žlčník bez konkrementov. Pankreas bez ložiskových zmien. Slezina nezvačšená. Obličky bilaterálne bez dilatácie dutého systému. Appendix bez známok zápalu. Voľná tekutina v Douglasovom priestore cca 50 ml.||||||F|||20260509105000
OBX|2|FT|59777-3^Záver^LN||Malé množstvo voľnej tekutiny v malej panve, inak CT abdomenu bez akútnej patológie.||||||F|||20260509105000
OBX|3|ED|11502-2^Rádiologická správa^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5hIHNwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK||||||F
```

---

## 5. ORM^O01 - MRI brain order

```
MSH|^~\&|HIS|FNSP_ZA|AMISPACS|RAD_FNSP_ZA|20260509113000||ORM^O01|HIS20260509003|P|2.3|||AL|NE|SVK|8859/2
PID|||9260180055^^^FNSP_ZA^PI||Šípošová^Jarmila^Tatiana^^^L||19920618|F|||Hviezdoslavova 22^^Žilina^^01001^SVK^H
PV1|1|I|NEU^102^1|||204567^Mrvečka^Dalibor^^^MUDr.
ORC|NW|ORD2026050003^HIS|||||^^^20260509113000^^R||20260509113000|204567^Mrvečka^Dalibor^^^MUDr.
OBR|1|ORD2026050003^HIS||70553^MRI mozgu s kontrastom^CPT|||20260509112000||||STRETCHER|||||204567^Mrvečka^Dalibor^^^MUDr.||ACC2026050003||20260510100000|||F
```

---

## 6. ADT^A01 - Patient admission notification to PACS

```
MSH|^~\&|HIS|FNSP_BB|AMISPACS|RAD_FNSP_BB|20260509120000||ADT^A01^ADT_A01|HIS20260509004|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|A01|20260509120000
PID|||8453070028^^^FNSP_BB^PI||Radičová^Elena^Veronika^^^L||19840307|F|||Námestie slobody 10^^Banská Bystrica^^97401^SVK^H||^PRN^PH^^421^48^4141234|||||||||||||SVK
PV1|1|I|ORT^101^2^^^N^A|R|||701234^Lipták^Ernest^^^MUDr.^^^FNSP_BB^L|||ORT||||||||2026050006^^^FNSP_BB^VN|||||||||||||||||||||||||20260509120000
IN1|1|27-001^^^VšZP|VšZP^Všeobecná zdravotná poisťovňa||Mamateyova 17^^Bratislava^^85104^SVK
```

---

## 7. ORM^O01 - X-ray of the knee

```
MSH|^~\&|HIS|FNSP_BB|AMISPACS|RAD_FNSP_BB|20260509123000||ORM^O01|HIS20260509005|P|2.3|||AL|NE|SVK|8859/2
PID|||8453070028^^^FNSP_BB^PI||Radičová^Elena^Veronika^^^L||19840307|F|||Námestie slobody 10^^Banská Bystrica^^97401^SVK^H
PV1|1|I|ORT^101^2|||701234^Lipták^Ernest^^^MUDr.
ORC|NW|ORD2026050005^HIS|||||^^^20260509123000^^R||20260509123000|701234^Lipták^Ernest^^^MUDr.
OBR|1|ORD2026050005^HIS||73562^RTG kolena^CPT|||20260509122000||||WALK|||||701234^Lipták^Ernest^^^MUDr.||ACC2026050005||20260509133000|||F
```

---

## 8. ORU^R01 - MRI brain report

```
MSH|^~\&|AMISPACS|RAD_FNSP_ZA|HIS|FNSP_ZA|20260509140000||ORU^R01|PACS20260509003|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
PID|||9260180055^^^FNSP_ZA^PI||Šípošová^Jarmila^Tatiana^^^L||19920618|F|||Hviezdoslavova 22^^Žilina^^01001^SVK^H
PV1|1|I|NEU^102^1|||204567^Mrvečka^Dalibor^^^MUDr.
ORC|RE|ORD2026050003^HIS|RES2026050003^AMISPACS
OBR|1|ORD2026050003^HIS|RES2026050003^AMISPACS|70553^MRI mozgu s kontrastom^CPT|||20260509112000|||||||||204567^Mrvečka^Dalibor^^^MUDr.|||||ACC2026050003|20260509140000|||F
OBX|1|FT|59776-5^Nález^LN||Mozgový parenchým bez ložiskových zmien. Komorový systém symetrický, primeranej šírky. Stredočiarové štruktúry nedeviované. Bazálne cisterny voľné. Cerebellum a mozgový kmeň bez patológie. Parameterické sínusy vzdušné. Po podaní kontrastu bez patologického sýtenia.||||||F|||20260509135000
OBX|2|FT|59777-3^Záver^LN||MRI mozgu bez štrukturálnej patológie.||||||F|||20260509135000
```

---

## 9. ADT^A08 - Patient update propagated to PACS

```
MSH|^~\&|HIS|UNB|AMISPACS|RAD_UNB|20260509143000||ADT^A08^ADT_A01|HIS20260509006|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|A08|20260509143000
PID|||8901154782^^^UNB^PI||Brhel^Zdenko^Dušan^^^L||19890115|M|||Dlhá 7^^Bratislava^^81101^SVK^H||^PRN^PH^^421^2^54411234~^PRN^CP^^421^902^345678|||||||||||||SVK
PV1|1|I|INT^201^1|||101234^Šranko^Albín^^^MUDr.^^^UNB^L|||INT||||||||2026050001^^^UNB^VN|||||||||||||||||||||||||20260509080000
```

---

## 10. SIU^S12 - Scheduled mammography examination

```
MSH|^~\&|HIS|FN_NR|AMISPACS|RAD_FN_NR|20260509150000||SIU^S12|HIS20260509007|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
SCH|APT2026050001|APT2026050001|||||ROUTINE|MMG^Mamografia^L|20|min|^^^20260515090000^^20260515092000|702345^Kvasničková^Natália^^^MUDr.
PID|||8560230041^^^FN_NR^PI||Uhrínová^Agnesa^Monika^^^L||19850623|F|||Štefánikova 88^^Nitra^^94901^SVK^H||^PRN^PH^^421^37^6521234
PV1|1|O|MMG_AMB^A01^1
RGS|1
AIS|1|A|MMG^Mamografia^L|20260515090000|20|min
AIG|1|A|702345^Kvasničková^Natália^^^MUDr.|114
AIL|1|A|MMG_AMB^A01^1^^^FN_NR
```

---

## 11. ORU^R01 - Knee X-ray report

```
MSH|^~\&|AMISPACS|RAD_FNSP_BB|HIS|FNSP_BB|20260509153000||ORU^R01|PACS20260509004|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
PID|||8453070028^^^FNSP_BB^PI||Radičová^Elena^Veronika^^^L||19840307|F|||Námestie slobody 10^^Banská Bystrica^^97401^SVK^H
PV1|1|I|ORT^101^2|||701234^Lipták^Ernest^^^MUDr.
ORC|RE|ORD2026050005^HIS|RES2026050005^AMISPACS
OBR|1|ORD2026050005^HIS|RES2026050005^AMISPACS|73562^RTG kolena^CPT|||20260509122000|||||||||701234^Lipták^Ernest^^^MUDr.|||||ACC2026050005|20260509153000|||F
OBX|1|FT|59776-5^Nález^LN||Kĺbová štrbina zúžená mediálne. Osteofyty na okrajoch mediálneho kondylu femuru a tibie. Subchondrálna skleróza mediálneho kompartmentu. Mäkké tkanivá bez opuchu. Patella v správnej polohe.||||||F|||20260509150000
OBX|2|FT|59777-3^Záver^LN||Gonartróza II. stupňa podľa Kellgren-Lawrence, mediálny kompartment.||||||F|||20260509150000
```

---

## 12. ADT^A03 - Discharge notification to PACS

```
MSH|^~\&|HIS|FNSP_ZA|AMISPACS|RAD_FNSP_ZA|20260509160000||ADT^A03^ADT_A03|HIS20260509008|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|A03|20260509160000
PID|||9260180055^^^FNSP_ZA^PI||Šípošová^Jarmila^Tatiana^^^L||19920618|F|||Hviezdoslavova 22^^Žilina^^01001^SVK^H
PV1|1|I|NEU^102^1^^^N^A|R|||204567^Mrvečka^Dalibor^^^MUDr.^^^FNSP_ZA^L|||NEU||||||||2026040112^^^FNSP_ZA^VN|||||||||||||||||011||||||||20260425080000|20260509160000
```

---

## 13. ORM^O01 - Ultrasound of the abdomen

```
MSH|^~\&|HIS|FN_NR|AMISPACS|RAD_FN_NR|20260509163000||ORM^O01|HIS20260509009|P|2.3|||AL|NE|SVK|8859/2
PID|||9558250044^^^FN_NR^PI||Kvapilová^Božena^Alžbeta^^^L||19950825|F|||Záhradná 156^^Nitra^^94911^SVK^H
PV1|1|I|GYN^401^2|||207890^Záborec^Fridrich^^^MUDr.
ORC|NW|ORD2026050009^HIS|||||^^^20260509163000^^R||20260509163000|207890^Záborec^Fridrich^^^MUDr.
OBR|1|ORD2026050009^HIS||76700^USG abdomenu^CPT|||20260509162000||||WALK|||||207890^Záborec^Fridrich^^^MUDr.||ACC2026050009||20260510080000|||F
```

---

## 14. ADT^A40 - Merge patient in PACS

```
MSH|^~\&|HIS|UNB|AMISPACS|RAD_UNB|20260509170000||ADT^A40^ADT_A39|HIS20260509010|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|A40|20260509170000
PID|||8901154782^^^UNB^PI||Brhel^Zdenko^Dušan^^^L||19890115|M|||Dlhá 7^^Bratislava^^81101^SVK^H
MRG|8901154799^^^UNB^PI
```

---

## 15. ORU^R01 - USG abdomen report

```
MSH|^~\&|AMISPACS|RAD_FN_NR|HIS|FN_NR|20260509173000||ORU^R01|PACS20260509005|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
PID|||9558250044^^^FN_NR^PI||Kvapilová^Božena^Alžbeta^^^L||19950825|F|||Záhradná 156^^Nitra^^94911^SVK^H
PV1|1|I|GYN^401^2|||207890^Záborec^Fridrich^^^MUDr.
ORC|RE|ORD2026050009^HIS|RES2026050009^AMISPACS
OBR|1|ORD2026050009^HIS|RES2026050009^AMISPACS|76700^USG abdomenu^CPT|||20260509162000|||||||||207890^Záborec^Fridrich^^^MUDr.|||||ACC2026050009|20260509173000|||F
OBX|1|FT|59776-5^Nález^LN||Pečeň normálnej veľkosti a echogenity. Žlčník bez konkrementov. Žlčové cesty nedilatované. Pankreas prehľadný, bez ložiskových zmien. Obličky symetrické, bez hydronefrózy. Slezina normálnej veľkosti. Maternica anteverzia, myóm na prednej stene 18 mm.||||||F|||20260509172000
OBX|2|FT|59777-3^Záver^LN||Intramurálny myóm maternice 18 mm, inak USG abdomenu v norme.||||||F|||20260509172000
```

---

## 16. MDM^T02 - Radiology report with embedded DICOM-SR PDF (base64)

```
MSH|^~\&|AMISPACS|RAD_FNSP_BB|HIS|FNSP_BB|20260509180000||MDM^T02|PACS20260509006|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|T02|20260509180000
PID|||8453070028^^^FNSP_BB^PI||Radičová^Elena^Veronika^^^L||19840307|F|||Námestie slobody 10^^Banská Bystrica^^97401^SVK^H
PV1|1|I|ORT^101^2|||701234^Lipták^Ernest^^^MUDr.
TXA|1|RA^Rádiologická správa^L|TX|20260509175000|703456^Čiháková^Oľga^^^MUDr.|20260509180000||||||DOC2026050016|||||AU
OBX|1|ED|18748-4^Rádiologická správa^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5hIHNwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK||||||F
```

---

## 17. ACK - Positive acknowledgment for radiology order

```
MSH|^~\&|AMISPACS|RAD_UNB|HIS|UNB|20260509080001||ACK^O01^ACK|PACS20260509ACK001|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
MSA|AA|HIS20260509001
```

---

## 18. ADT^A02 - Patient transfer notification to PACS

```
MSH|^~\&|HIS|UNB|AMISPACS|RAD_UNB|20260509183000||ADT^A02^ADT_A02|HIS20260509011|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
EVN|A02|20260509183000
PID|||8901154782^^^UNB^PI||Brhel^Zdenko^Dušan^^^L||19890115|M|||Dlhá 7^^Bratislava^^81101^SVK^H
PV1|1|I|KAR^310^1^^^N^D|R||INT^201^1^^^N^D|101234^Šranko^Albín^^^MUDr.^^^UNB^L|||KAR||||||||2026050001^^^UNB^VN|||||||||||||||||||||||||20260509080000
```

---

## 19. ORM^O01 - Order for cardiac echocardiography

```
MSH|^~\&|HIS|UNB|AMISPACS|RAD_UNB|20260509190000||ORM^O01|HIS20260509012|P|2.3|||AL|NE|SVK|8859/2
PID|||7855060019^^^UNB^PI||Kočiš^Karol^Tibor^^^L||19780506|M|||Vajanského 46^^Bratislava^^82108^SVK^H
PV1|1|I|KAR^305^2|||103789^Pašteka^Gregor^^^MUDr.
ORC|NW|ORD2026050012^HIS|||||^^^20260509190000^^R||20260509190000|103789^Pašteka^Gregor^^^MUDr.
OBR|1|ORD2026050012^HIS||93306^Echokardiografia^CPT|||20260509185000||||WALK|||||103789^Pašteka^Gregor^^^MUDr.||ACC2026050012||20260512080000|||F
```

---

## 20. ACK - Negative acknowledgment for duplicate order

```
MSH|^~\&|AMISPACS|RAD_UNLP_KE|HIS|UNLP_KE|20260509193000||ACK^O01^ACK|PACS20260509ACK002|P|2.5|||AL|NE|SVK|UNICODE UTF-8|SVK^Slovak^HL70296
MSA|AE|HIS20260509002|Duplicitná objednávka - vyšetrenie už existuje
ERR|||205^Duplicitný identifikátor objednávky^HL70357
```
