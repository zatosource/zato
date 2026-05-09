# Dedalus RISonWEB (Belgium) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - radiology order for CT sinus (IHE SWF)

```
MSH|^~\&|RISONWEB|UZ_BRUSSEL|PACS_BE|UZ_BRUSSEL|20260509083000||ORM^O01|MSG00001|P|2.5.1
PID|1||PAT55932^^^UZB^PI||Van Damme^Pieter^L^^Dhr.||19780312|M|||Vlaamsesteenweg 42^^Brussel^^1000^BE||^^PH^02-512-7834
PV1||O|RAD^CT-1^1^Radiologie||||21345678012^Van Acker^Kristof^^^Dr.|||RAD
ORC|NW|ORD88432^RISONWEB|FIL99321^PACS_BE||SC||^^^20260509083000^^R||20260509083000|21345678012^Van Acker^Kristof^^^Dr.
OBR|1|ORD88432^RISONWEB|FIL99321^PACS_BE|70486^CT SINUS ZONDER CONTRAST^CPT4|R|20260509080000|||||||21345678012^Van Acker^Kristof^^^Dr.||||||CT|SC
ZDS|1.2.840.113619.2.55.3.604688119.968.2345678901.223^RISONWEB^APPLICATION^DICOM
```

---

## 2. ORM^O01 - radiology order for chest X-ray AP and lateral

```
MSH|^~\&|RISONWEB|AZ_SINT_JAN|PACS_BE|AZ_SINT_JAN|20260509091500||ORM^O01|MSG00002|P|2.3
PID|1||PAT66213^^^AZSJ^PI||De Smedt^Inge^A^^Mevr.||19710721|F|||Tiensestraat 87^^Leuven^^3000^BE||^^PH^016-224589
PV1||I|PULMO^Kamer 302^Bed 1^Longziekten||||21456789023^De Backer^Filip^^^Dr.|||MED
ORC|NW|ORD77201^RISONWEB|FIL88102^PACS_BE||SC||^^^20260509091500^^R||20260509091500|21456789023^De Backer^Filip^^^Dr.
OBR|1|ORD77201^RISONWEB|FIL88102^PACS_BE|71020^RX THORAX AP EN LATERAAL^CPT4|R|20260509090000|||||||21456789023^De Backer^Filip^^^Dr.||||||CR|SC
ZDS|1.2.840.113619.2.55.3.604688119.968.3456789012.334^RISONWEB^APPLICATION^DICOM
```

---

## 3. ORU^R01 - radiology result for chest X-ray with report text

```
MSH|^~\&|RISONWEB|AZ_SINT_JAN|HIS_BE|AZ_SINT_JAN|20260509141200||ORU^R01|MSG00003|P|2.3
PID|1||PAT66213^^^AZSJ^PI||De Smedt^Inge^A^^Mevr.||19710721|F|||Tiensestraat 87^^Leuven^^3000^BE
PV1||I|PULMO^Kamer 302^Bed 1^Longziekten||||21456789023^De Backer^Filip^^^Dr.|||MED
ORC|RE|ORD77201^RISONWEB|FIL88102^PACS_BE||CM||^^^20260509091500^^R||20260509141200|21456789023^De Backer^Filip^^^Dr.
OBR|1|ORD77201^RISONWEB|FIL88102^PACS_BE|71020^RX THORAX AP EN LATERAAL^CPT4||||||||||||21567890034^Timmermans^Hilde^^^Dr.||||||F
OBX|1|ST|&GDT|1|Thoraxfoto AP en lateraal. Geen focale consolidaties. Normale hartschaduw. Geen pleuravocht.|||N|||F
OBX|2|ST|&IMP|1|Normaal thoraxonderzoek, geen bijzonderheden.|||N|||F
```

---

## 4. ORU^R01 - radiology result with base64 PDF report (CDA-R2)

```
MSH|^~\&|RISONWEB|CHU_LIEGE|DMP_BE|EHEALTH_BE|20260509150000||ORU^R01^ORU_R01|MSG00004|P|2.5
PID|1||PAT77312^^^CHUL^PI||Mertens^Wim^F^^Dhr.||19840114|M|||Quai de Rome 33^^Liege^^4000^BE
PV1||O|RAD^IRM-2^1^Radiologie||||21678901045^Lejeune^Antoine^^^Dr.|||RAD
ORC|RE|ORD99301^RISONWEB|FIL00201^PACS_BE||CM
OBR|1|ORD99301^RISONWEB|FIL00201^PACS_BE|18748-4^CR d'imagerie medicale^LN||||||||||||21678901045^Lejeune^Antoine^^^Dr.||||||F
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj48dGl0bGU+Q29tcHRlIHJlbmR1IGQnaW1hZ2VyaWUgbWVkaWNhbGU8L3RpdGxlPjwvQ2xpbmljYWxEb2N1bWVudD4=||||||F
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
```

---

## 5. ORU^R01 - CT abdomen result with findings and impression

```
MSH|^~\&|RISONWEB|UZ_GENT|HIS_BE|UZ_GENT|20260509160000||ORU^R01|MSG00005|P|2.5.1
PID|1||PAT88413^^^UZG^PI||Michiels^Eline^J^^Mevr.||19920605|F|||Vrijdagmarkt 14^^Gent^^9000^BE||^^PH^09-267-4521
PV1||O|RAD^CT-2^1^Radiologie||||21789012056^Desmet^Bart^^^Dr.|||RAD
ORC|RE|ORD11401^RISONWEB|FIL22301^PACS_BE||CM
OBR|1|ORD11401^RISONWEB|FIL22301^PACS_BE|74150^CT ABDOMEN ZONDER CONTRAST^CPT4||||||||||||21789012056^Desmet^Bart^^^Dr.||||||F
OBX|1|TX|859776-5^Procedure Findings^LN|1|Lever, milt en nieren normaal van grootte en aspect. Geen vrij vocht. Geen lymfadenopathie.|||N^Normaal^HL70078|||F
OBX|2|TX|859776-5^Procedure Findings^LN|2|Kleine cyste rechternier (12mm), klinisch niet significant.|||N^Normaal^HL70078|||F
OBX|3|ST|&IMP|1|Normaal CT abdomen. Kleine eenvoudige niercyste rechts, geen verdere opvolging nodig.|||N|||F
```

---

## 6. ADT^A04 - patient registration for radiology outpatient visit

```
MSH|^~\&|RISONWEB|AZ_DELTA|HIS_BE|AZ_DELTA|20260509100000||ADT^A04|MSG00006|P|2.4
EVN|A04|20260509100000
PID|1||PAT99512^^^AZD^PI|92040523178^^^^NN|Baert^Koen^M^^Dhr.||19920405|M|||Meensesteenweg 7^^Roeselare^^8800^BE||^^PH^051-263748
NK1|1|Baert^Griet^V|MTH|||||20260509
PV1||O|RAD^RX-1^1^Radiologie||||21890123067^Martens^Eva^^^Dr.|||RAD
AL1|1||^JODIUMHOUDEND CONTRASTMIDDEL||URTICARIA~NAUSEA
```

---

## 7. ADT^A01 - inpatient admission to radiology ward

```
MSH|^~\&|RISONWEB|UZ_ANTWERPEN|HIS_BE|UZ_ANTWERPEN|20260509073000||ADT^A01^ADT_A01|MSG00007|P|2.5
EVN|A01|20260509073000
PID|1||PAT00612^^^UZA^PI|86071234589^^^^NN|Lenaerts^Annelies^T^^Mevr.||19860712|F|||Mechelsesteenweg 55^^Antwerpen^^2000^BE||^^PH^03-231-8945~^^CP^0476-589321
PV1||I|RAD^Kamer 201^Bed 1^Interventionele Radiologie||||21901234078^Peeters^Luc^^^Dr.^med.|||RAD||||||||OPNAME20260509|||||||||||||||||||||||RAD^Kamer 201^Bed 1^Interventionele Radiologie||20260509073000
IN1|1|0|MUT002|SOCIALISTISCHE MUTUALITEIT|Lambermontlaan 100^^Brussel^^1030^BE||||||||||||||||||||||||||||||||||||||||||||56
```

---

## 8. ORM^O01 - MRI brain order with clinical indication

```
MSH|^~\&|RISONWEB|AZ_KLINA|PACS_BE|AZ_KLINA|20260509113000||ORM^O01|MSG00008|P|2.5.1
PID|1||PAT21712^^^AZKL^PI||Wouters^Bram^E^^Dhr.||19800923|M|||Bredabaan 33^^Brasschaat^^2930^BE||^^PH^03-652-1847
PV1||O|NEURO^Consult-2^1^Neurologie||||22012345089^Jacobs^Karen^^^Dr.|||MED
ORC|NW|ORD22501^RISONWEB|FIL33401^PACS_BE||SC||^^^20260509113000^^R||20260509113000|22012345089^Jacobs^Karen^^^Dr.
OBR|1|ORD22501^RISONWEB|FIL33401^PACS_BE|70553^MRI HERSENEN MET CONTRAST^CPT4|R|20260509110000|||||||22012345089^Jacobs^Karen^^^Dr.|||Hoofdpijn, vermoeden MS||MR|SC||||||22012345089^Jacobs^Karen^^^Dr.
DG1|1|ICD10|G35^Multiple sclerose^ICD10||20260509
```

---

## 9. ORU^R01 - MRI brain result with structured findings

```
MSH|^~\&|RISONWEB|AZ_KLINA|HIS_BE|AZ_KLINA|20260509163000||ORU^R01|MSG00009|P|2.5.1
PID|1||PAT21712^^^AZKL^PI||Wouters^Bram^E^^Dhr.||19800923|M|||Bredabaan 33^^Brasschaat^^2930^BE
PV1||O|NEURO^Consult-2^1^Neurologie||||22012345089^Jacobs^Karen^^^Dr.|||MED
ORC|RE|ORD22501^RISONWEB|FIL33401^PACS_BE||CM
OBR|1|ORD22501^RISONWEB|FIL33401^PACS_BE|70553^MRI HERSENEN MET CONTRAST^CPT4||||||||||||22123456090^Vandenberghe^Elke^^^Dr.||||||F
OBX|1|TX|859776-5^Procedure Findings^LN|1|Meerdere periventriculaire en juxtacorticale T2-hyperintense witte stof laesies, wisselend van grootte (3-12mm). Enkele infratentoriele laesies in de pons.|||A^Abnormaal^HL70078|||F
OBX|2|TX|859776-5^Procedure Findings^LN|2|Na contrasttoediening aankleuring van twee periventriculaire laesies, suggestief voor actieve demyelinisatie.|||A^Abnormaal^HL70078|||F
OBX|3|ST|&IMP|1|Beeld verenigbaar met multipele sclerose volgens McDonald-criteria. Actieve en niet-actieve laesies aanwezig.|||A|||F
```

---

## 10. ORU^R01 - radiology report with base64-encoded CDA-R2 document and mail body

```
MSH|^~\&|RISONWEB|CHR_NAMUR|DMP_BE|EHEALTH_BE|20260509170000||ORU^R01^ORU_R01|MSG00010|P|2.5
PID|1||PAT32812^^^CHRN^PI||Renard^Isabelle^C^^Mevr.||19890310|F|||Rue de Fer 15^^Namur^^5000^BE
PV1||O|RAD^ECHO-1^1^Radiologie||||22234567001^Dupont^Francois^^^Dr.|||RAD
ORC|RE|ORD33601^RISONWEB|FIL44501^PACS_BE||CM
OBR|1|ORD33601^RISONWEB|FIL44501^PACS_BE|18748-4^CR d'imagerie medicale^LN||||||||||||22234567001^Dupont^Francois^^^Dr.||||||F
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+RWNob2dyYXBoaWUgYWJkb21pbmFsZTwvdGl0bGU+PGNvbXBvbmVudD48c2VjdGlvbj48dGV4dD5Gb2llIG5vcm1hbCwgcGFzIGRlIGxpdGhpYXNlIGJpbGlhaXJlPC90ZXh0Pjwvc2VjdGlvbj48L2NvbXBvbmVudD48L0NsaW5pY2FsRG9jdW1lbnQ+||||||F
PRT||UC||SB^Send by^participation|22234567001^Dupont^Francois^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNbWUgRHVtb250LCB2b3VzIHRyb3V2ZXJleiBjaS1qb2ludCB2b3RyZSBjb21wdGUgcmVuZHUgZCdlY2hvZ3JhcGhpZS4=||||||F
```

---

## 11. ORM^O01 - ultrasound abdomen order with reason for study

```
MSH|^~\&|RISONWEB|AZ_GROENINGE|PACS_BE|AZ_GROENINGE|20260509080000||ORM^O01|MSG00011|P|2.3
PID|1||PAT43912^^^AZG^PI||Maes^Ruben^D^^Dhr.||19640418|M|||Doorniksesteenweg 112^^Kortrijk^^8500^BE||^^PH^056-218734
PV1||O|RAD^ECHO-2^1^Radiologie||||22345678012^Pauwels^Inge^^^Dr.|||RAD
ORC|NW|ORD44701^RISONWEB|FIL55601^PACS_BE||SC
OBR|1|ORD44701^RISONWEB|FIL55601^PACS_BE|76700^ECHOGRAFIE ABDOMEN VOLLEDIG^CPT4|R|20260509075000|||||||22345678012^Pauwels^Inge^^^Dr.|||Abdominale pijn rechts boven, vermoeden cholelithiasis||US|SC
DG1|1|ICD10|K80.2^Cholelithiasis^ICD10||20260509
```

---

## 12. ORU^R01 - ultrasound result with multiple OBX findings

```
MSH|^~\&|RISONWEB|AZ_GROENINGE|HIS_BE|AZ_GROENINGE|20260509143000||ORU^R01|MSG00012|P|2.3
PID|1||PAT43912^^^AZG^PI||Maes^Ruben^D^^Dhr.||19640418|M|||Doorniksesteenweg 112^^Kortrijk^^8500^BE
PV1||O|RAD^ECHO-2^1^Radiologie||||22345678012^Pauwels^Inge^^^Dr.|||RAD
ORC|RE|ORD44701^RISONWEB|FIL55601^PACS_BE||CM
OBR|1|ORD44701^RISONWEB|FIL55601^PACS_BE|76700^ECHOGRAFIE ABDOMEN VOLLEDIG^CPT4||||||||||||22456789023^Simon^Benoit^^^Dr.||||||F
OBX|1|ST|&GDT|1|Lever normaal van grootte en echostructuur. Galblaas bevat meerdere echorijke structuren met slagschaduw, diameter grootste steen 14mm.|||A|||F
OBX|2|ST|&GDT|2|Galwegen niet verwijd. Pancreas normaal. Milt en nieren zonder bijzonderheden.|||N|||F
OBX|3|ST|&IMP|1|Cholelithiasis met meerdere galstenen. Geen cholecystitis. Verder normaal echografisch abdomenonderzoek.|||A|||F
```

---

## 13. ORM^O01 - cancel radiology order

```
MSH|^~\&|RISONWEB|UZ_BRUSSEL|PACS_BE|UZ_BRUSSEL|20260509111500||ORM^O01|MSG00013|P|2.5.1
PID|1||PAT55932^^^UZB^PI||Van Damme^Pieter^L^^Dhr.||19780312|M|||Vlaamsesteenweg 42^^Brussel^^1000^BE
PV1||O|RAD^CT-1^1^Radiologie||||21345678012^Van Acker^Kristof^^^Dr.|||RAD
ORC|CA|ORD88432^RISONWEB|FIL99321^PACS_BE||CA||^^^20260509111500||20260509111500|21345678012^Van Acker^Kristof^^^Dr.
OBR|1|ORD88432^RISONWEB|FIL99321^PACS_BE|70486^CT SINUS ZONDER CONTRAST^CPT4|R|20260509080000|||||||21345678012^Van Acker^Kristof^^^Dr.||||||CT|CA
```

---

## 14. ADT^A08 - update patient demographics in RIS

```
MSH|^~\&|RISONWEB|AZ_DELTA|HIS_BE|AZ_DELTA|20260509123000||ADT^A08^ADT_A01|MSG00014|P|2.4
EVN|A08|20260509123000
PID|1||PAT99512^^^AZD^PI|92040523178^^^^NN|Baert-Verbeke^Koen^M^^Dhr.||19920405|M|||Marktplein 7^^Roeselare^^8800^BE||^^PH^051-263748~^^CP^0479-341256~^^Internet^koen.baert@telenet.be
PV1||O|RAD^RX-1^1^Radiologie||||21890123067^Martens^Eva^^^Dr.|||RAD
```

---

## 15. ORM^O01 - mammography screening order

```
MSH|^~\&|RISONWEB|AZ_MARIA|PACS_BE|AZ_MARIA|20260509090000||ORM^O01|MSG00015|P|2.5.1
PID|1||PAT54012^^^AZM^PI||Coppens^Vera^H^^Mevr.||19730815|F|||Thonissenlaan 8^^Hasselt^^3500^BE||^^PH^011-423567
PV1||O|RAD^MAMMO-1^1^Radiologie||||22567890034^Claes^Katrien^^^Dr.|||RAD
ORC|NW|ORD55801^RISONWEB|FIL66701^PACS_BE||SC||^^^20260509090000^^R||20260509090000|22567890034^Claes^Katrien^^^Dr.
OBR|1|ORD55801^RISONWEB|FIL66701^PACS_BE|77067^MAMMOGRAFIE BILATERAAL SCREENING^CPT4|R|20260509085000|||||||22567890034^Claes^Katrien^^^Dr.|||Borstkankerscreening, leeftijd >50||MG|SC
```

---

## 16. ORU^R01 - mammography result with BI-RADS classification

```
MSH|^~\&|RISONWEB|AZ_MARIA|HIS_BE|AZ_MARIA|20260509153000||ORU^R01|MSG00016|P|2.5.1
PID|1||PAT54012^^^AZM^PI||Coppens^Vera^H^^Mevr.||19730815|F|||Thonissenlaan 8^^Hasselt^^3500^BE
PV1||O|RAD^MAMMO-1^1^Radiologie||||22567890034^Claes^Katrien^^^Dr.|||RAD
ORC|RE|ORD55801^RISONWEB|FIL66701^PACS_BE||CM
OBR|1|ORD55801^RISONWEB|FIL66701^PACS_BE|77067^MAMMOGRAFIE BILATERAAL SCREENING^CPT4||||||||||||22678901045^Hendrickx^Sara^^^Dr.||||||F
OBX|1|TX|859776-5^Procedure Findings^LN|1|Bilaterale mammografie. Dicht klierweefsel (ACR-densiteit C). Geen verdachte microcalcificaties. Geen architectuurverstoring. Geen focale asymmetrie.|||N^Normaal^HL70078|||F
OBX|2|CE|36625-2^BI-RADS Assessment^LN||BI-RADS 1^Negatief^ACR|||N|||F
OBX|3|ST|&IMP|1|BI-RADS 1 - Negatief bilateraal mammografisch onderzoek. Volgende screening over 2 jaar aanbevolen.|||N|||F
```

---

## 17. ADT^A03 - discharge from interventional radiology

```
MSH|^~\&|RISONWEB|UZ_ANTWERPEN|HIS_BE|UZ_ANTWERPEN|20260509160000||ADT^A03^ADT_A03|MSG00017|P|2.5
EVN|A03|20260509160000
PID|1||PAT00612^^^UZA^PI|86071234589^^^^NN|Lenaerts^Annelies^T^^Mevr.||19860712|F|||Mechelsesteenweg 55^^Antwerpen^^2000^BE||^^PH^03-231-8945~^^CP^0476-589321
PV1||I|RAD^Kamer 201^Bed 1^Interventionele Radiologie||||21901234078^Peeters^Luc^^^Dr.^med.|||RAD||||||||OPNAME20260509|||||||||||||||||||||||RAD^Kamer 201^Bed 1^Interventionele Radiologie||20260509160000
```

---

## 18. ORM^O01 - PET/CT order with clinical context

```
MSH|^~\&|RISONWEB|UZ_GENT|PACS_BE|UZ_GENT|20260509140000||ORM^O01|MSG00018|P|2.5.1
PID|1||PAT65112^^^UZG^PI||Janssens^Dirk^R^^Dhr.||19670302|M|||Blaarmeersen 18^^Gent^^9000^BE||^^PH^09-335-7812
PV1||O|NUCL^PET-1^1^Nucleaire Geneeskunde||||22789012056^Goossens^Marc^^^Prof.^Dr.|||MED
ORC|NW|ORD66901^RISONWEB|FIL77801^PACS_BE||SC||^^^20260509140000^^R||20260509140000|22789012056^Goossens^Marc^^^Prof.^Dr.
OBR|1|ORD66901^RISONWEB|FIL77801^PACS_BE|78816^PET-CT FDG WHOLE BODY^CPT4|R|20260509130000|||||||22789012056^Goossens^Marc^^^Prof.^Dr.|||Stadiering longcarcinoom, histologisch bewezen NSCLC||PT|SC
DG1|1|ICD10|C34.1^Maligne neoplasma bovenkwab long^ICD10||20260505
```

---

## 19. ORU^R01 - base64 CDA-R2 document replacement (OBX-11=C)

```
MSH|^~\&|RISONWEB|CHU_LIEGE|DMP_BE|EHEALTH_BE|20260509180000||ORU^R01^ORU_R01|MSG00019|P|2.5
PID|1||PAT77312^^^CHUL^PI||Mertens^Wim^F^^Dhr.||19840114|M|||Quai de Rome 33^^Liege^^4000^BE
PV1||O|RAD^IRM-2^1^Radiologie||||21678901045^Lejeune^Antoine^^^Dr.|||RAD
ORC|RE|ORD99301^RISONWEB|FIL00201^PACS_BE||CM
OBR|1|ORD99301^RISONWEB|FIL00201^PACS_BE|18748-4^CR d'imagerie medicale^LN||||||||||||21678901045^Lejeune^Antoine^^^Dr.||||||F
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48cmVsYXRlZERvY3VtZW50IHR5cGVDb2RlPSJSUExDIj48cGFyZW50RG9jdW1lbnQ+PGlkIHJvb3Q9IjEuMi4yNTAuMS4yMTMuMS4xLjEiLz48L3BhcmVudERvY3VtZW50PjwvcmVsYXRlZERvY3VtZW50PjwvQ2xpbmljYWxEb2N1bWVudD4=||||||C
PRT||UC||SB^Send by^participation|21678901045^Lejeune^Antoine^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgY29ycmlnZSBkJ0lSTS4=||||||F
```

---

## 20. ORM^O01 - status update (in-progress) for scheduled procedure

```
MSH|^~\&|RISONWEB|UZ_GENT|PACS_BE|UZ_GENT|20260509141500||ORM^O01|MSG00020|P|2.5.1
PID|1||PAT65112^^^UZG^PI||Janssens^Dirk^R^^Dhr.||19670302|M|||Blaarmeersen 18^^Gent^^9000^BE
PV1||O|NUCL^PET-1^1^Nucleaire Geneeskunde||||22789012056^Goossens^Marc^^^Prof.^Dr.|||MED
ORC|SC|ORD66901^RISONWEB|FIL77801^PACS_BE||IP||^^^20260509141500^^R||20260509141500|22789012056^Goossens^Marc^^^Prof.^Dr.
OBR|1|ORD66901^RISONWEB|FIL77801^PACS_BE|78816^PET-CT FDG WHOLE BODY^CPT4||||||||||||22789012056^Goossens^Marc^^^Prof.^Dr.||||||IP
```
