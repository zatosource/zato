# Dedalus DXCare (Belgium) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - inpatient admission with insurance

```
MSH|^~\&|DXCARE|CHU_ST_PIERRE|HIS_BE|CHU_ST_PIERRE|20260509070000||ADT^A01^ADT_A01|MSG10001|P|2.5
EVN|A01|20260509070000
PID|1||PAT23012^^^CHSP^PI|86021534217^^^^NN|Dubois^Marc-Antoine^R^^M.||19860215|M|||Rue du Midi 145^^Bruxelles^^1000^BE||^^PH^02-646-4222~^^CP^0476-234567~^^Internet^madubois@skynet.be
NK1|1|Dubois^Elise^L|SPO|Rue du Midi 145^^Bruxelles^^1000^BE|0476-765432
PV1||I|CARDIO^Kamer 405^Bed 2^Cardiologie||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.|||MED||||||||OPNAME89142|||||||||||||||||||||||CARDIO^Kamer 405^Bed 2^Cardiologie||20260509070000
IN1|1|0|MUT003|NEUTRALE ZIEKENFONDS|Rue des Colonies 11^^Bruxelles^^1000^BE||||||||||||||||||||||||||||||||||||||||||||56
```

---

## 2. ADT^A04 - outpatient registration

```
MSH|^~\&|DXCARE|AZ_MONICA|HIS_BE|AZ_MONICA|20260509083000||ADT^A04|MSG10002|P|2.4
EVN|A04|20260509083000
PID|1||PAT24212^^^AZM^PI|92041267834^^^^NN|Goossens^Lien^M^^Mevr.||19920412|F|||Turnhoutsebaan 88^^Borgerhout^^2140^BE||^^PH^03-431-2345
NK1|1|Goossens^Hendrik^W|FTH|||||20260509
PV1||O|CONS^Consult-3^1^Gastro-enterologie||||20333444023^Wouters^Katrien^^^Dr.|||MED
AL1|1||^ASPIRINE||BRONCHOSPASME
DG1|1|ICD10|K21.0^Gastro-oesofageale reflux met oesofagitis^ICD10||20260509
```

---

## 3. ADT^A02 - patient transfer between wards

```
MSH|^~\&|DXCARE|CHU_ST_PIERRE|HIS_BE|CHU_ST_PIERRE|20260510090000||ADT^A02^ADT_A02|MSG10003|P|2.5
EVN|A02|20260510090000
PID|1||PAT23012^^^CHSP^PI|86021534217^^^^NN|Dubois^Marc-Antoine^R^^M.||19860215|M|||Rue du Midi 145^^Bruxelles^^1000^BE
PV1||I|ICU^Kamer 102^Bed 1^Intensieve Zorgen||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.|||MED||CARDIO^Kamer 405^Bed 2^Cardiologie||||||||OPNAME89142|||||||||||||||||||||||ICU^Kamer 102^Bed 1^Intensieve Zorgen||20260510090000
```

---

## 4. ADT^A03 - discharge

```
MSH|^~\&|DXCARE|CHU_ST_PIERRE|HIS_BE|CHU_ST_PIERRE|20260515143000||ADT^A03^ADT_A03|MSG10004|P|2.5
EVN|A03|20260515143000
PID|1||PAT23012^^^CHSP^PI|86021534217^^^^NN|Dubois^Marc-Antoine^R^^M.||19860215|M|||Rue du Midi 145^^Bruxelles^^1000^BE||^^PH^02-646-4222~^^CP^0476-234567
PV1||I|CARDIO^Kamer 405^Bed 2^Cardiologie||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.|||MED||||||||OPNAME89142|||||||||||||||||||||||CARDIO^Kamer 405^Bed 2^Cardiologie||20260515143000
```

---

## 5. ADT^A08 - patient demographics update

```
MSH|^~\&|DXCARE|AZ_MONICA|HIS_BE|AZ_MONICA|20260509100000||ADT^A08^ADT_A01|MSG10005|P|2.4
EVN|A08|20260509100000
PID|1||PAT24212^^^AZM^PI|92041267834^^^^NN|Goossens-De Smedt^Lien^M^^Mevr.||19920412|F|||Plantin en Moretuslei 66^^Berchem^^2600^BE||^^PH^03-431-2345~^^CP^0487-223344~^^Internet^lien.goossens@gmail.com
PV1||O|CONS^Consult-3^1^Gastro-enterologie||||20333444023^Wouters^Katrien^^^Dr.|||MED
```

---

## 6. ORM^O01 - laboratory order for blood chemistry panel

```
MSH|^~\&|DXCARE|CHU_LIEGE|LABO_BE|CHU_LIEGE|20260509081500||ORM^O01|MSG10006|P|2.5
PID|1||PAT25312^^^CHUL^PI||Marchand^Olivier^V^^M.||19790928|M|||Boulevard d'Avroy 33^^Liege^^4000^BE||^^PH^04-477-8901
PV1||I|MED-INT^Kamer 512^Bed 1^Interne Geneeskunde||||20444555034^Simon^Christophe^^^Dr.|||MED
ORC|NW|ORD10001^DXCARE|FIL20001^LABO_BE||SC||^^^20260509081500^^R||20260509081500|20444555034^Simon^Christophe^^^Dr.
OBR|1|ORD10001^DXCARE|FIL20001^LABO_BE|80053^BLOEDCHEMIE PANEL^CPT4|R|20260509080000|||||||20444555034^Simon^Christophe^^^Dr.||||||LAB|SC
```

---

## 7. ORU^R01 - laboratory result with numeric observations

```
MSH|^~\&|LABO_BE|CHU_LIEGE|DXCARE|CHU_LIEGE|20260509141500||ORU^R01|MSG10007|P|2.5
PID|1||PAT25312^^^CHUL^PI||Marchand^Olivier^V^^M.||19790928|M|||Boulevard d'Avroy 33^^Liege^^4000^BE
PV1||I|MED-INT^Kamer 512^Bed 1^Interne Geneeskunde||||20444555034^Simon^Christophe^^^Dr.|||MED
ORC|RE|ORD10001^DXCARE|FIL20001^LABO_BE||CM
OBR|1|ORD10001^DXCARE|FIL20001^LABO_BE|80053^BLOEDCHEMIE PANEL^CPT4||||||||||||20666777056^Michel^Francois^^^Dr.||||||F
OBX|1|NM|2160-0^CREATININE^LN||88|umol/L|62-106|N|||F
OBX|2|NM|3094-0^UREUM^LN||5.2|mmol/L|2.5-7.1|N|||F
OBX|3|NM|2345-7^GLUCOSE^LN||12.8|mmol/L|3.9-5.8|HH|||F
OBX|4|NM|2823-3^KALIUM^LN||4.1|mmol/L|3.5-5.1|N|||F
OBX|5|NM|2951-2^NATRIUM^LN||139|mmol/L|136-145|N|||F
```

---

## 8. ORU^R01 - CDA-R2 biology report with base64 document

```
MSH|^~\&|DXCARE|CLINIQUE_STE_ANNE|DMP_BE|EHEALTH_BE|20260509150000||ORU^R01^ORU_R01|MSG10008|P|2.5
PID|1||PAT26412^^^CSA^PI||Janssens^Nathalie^E^^Mevr.||19971022|F|||Rue Neuve 55^^Bruxelles^^1000^BE
PV1||I|CHIR^Kamer 301^Bed 1^Chirurgie||||20666777056^Mertens^Willem^^^Dr.|||CHIR
ORC|RE|ORD11101^DXCARE|FIL21101^LABO_BE||CM
OBR|1|ORD11101^DXCARE|FIL21101^LABO_BE|11502-2^CR d'examens biologiques^LN||||||||||||20666777056^Mertens^Willem^^^Dr.||||||F
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+Q29tcHRlIHJlbmR1IGQnZXhhbWVucyBiaW9sb2dpcXVlczwvdGl0bGU+PGNvbXBvbmVudD48c2VjdGlvbj48dGV4dD5IZW1vZ2xvYmluZSAxNDUgZy9MLCBDUlAgMTIgbWcvTDwvdGV4dD48L3NlY3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg==||||||F
PRT||UC||SB^Send by^participation|20666777056^Mertens^Willem^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgZGUgYmlvbG9naWUgZGUgTW1lIERlY2xlcmNxLg==||||||F
```

---

## 9. MDM^T02 - initial medical document transmission with base64 CDA

```
MSH|^~\&|DXCARE|CHR_NAMUR|DMP_BE|EHEALTH_BE|20260509160000||MDM^T02^MDM_T02|MSG10009|P|2.6
EVN|T02|20260509160000
PID|1||PAT27512^^^CHRN^PI||Gilles^Thierry^J^^M.||19701124|M|||Rue de Fer 28^^Namur^^5000^BE
PV1||O|MED-INT^Consult-1^1^Medecine Interne||||20777888067^Lejeune^Marie-Claire^^^Dr.|||MED
TXA|1|CR^Compte Rendu^L|TX|20260509155000|20777888067^Lejeune^Marie-Claire^^^Dr.||20260509160000|ED|DOC-20260509-001|||20777888067^Lejeune^Marie-Claire^^^Dr.||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+Q29tcHRlIHJlbmR1IGQnaW1hZ2VyaWUgbWVkaWNhbGU8L3RpdGxlPjxjb21wb25lbnQ+PHNlY3Rpb24+PHRleHQ+UmFkaW9ncmFwaGllIHRob3JhY2lxdWUgbm9ybWFsZTwvdGV4dD48L3NlY3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg==||||||F
PRT||UC||SB^Send by^participation|20777888067^Lejeune^Marie-Claire^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
PRT||UC||RCT^Results Copies To^participation|20888999078^Laurent^Bernard^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgZCdpbWFnZXJpZSBkZSBNLkJvZGFydC4=||||||F
```

---

## 10. MDM^T04 - document deletion notification

```
MSH|^~\&|DXCARE|CHR_NAMUR|DMP_BE|EHEALTH_BE|20260510080000||MDM^T04^MDM_T02|MSG10010|P|2.6
EVN|T04|20260510080000
PID|1||PAT27512^^^CHRN^PI||Gilles^Thierry^J^^M.||19701124|M|||Rue de Fer 28^^Namur^^5000^BE
PV1||O|MED-INT^Consult-1^1^Medecine Interne||||20777888067^Lejeune^Marie-Claire^^^Dr.|||MED
TXA|1|CR^Compte Rendu^L|TX|20260510075000|20777888067^Lejeune^Marie-Claire^^^Dr.||20260510080000|ED|DOC-20260509-001|||20777888067^Lejeune^Marie-Claire^^^Dr.||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+RG9jdW1lbnQgc3VwcHJpbWU8L3RpdGxlPjwvQ2xpbmljYWxEb2N1bWVudD4=||||||D
PRT||UC||SB^send by^participation|20777888067^Lejeune^Marie-Claire^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 11. MDM^T10 - document replacement with base64 CDA (OBX-11=C)

```
MSH|^~\&|DXCARE|CHR_NAMUR|DMP_BE|EHEALTH_BE|20260510100000||MDM^T10^MDM_T02|MSG10011|P|2.6
EVN|T10|20260510100000
PID|1||PAT27512^^^CHRN^PI||Gilles^Thierry^J^^M.||19701124|M|||Rue de Fer 28^^Namur^^5000^BE
PV1||O|MED-INT^Consult-1^1^Medecine Interne||||20777888067^Lejeune^Marie-Claire^^^Dr.|||MED
TXA|1|CR^Compte Rendu^L|TX|20260510095000|20777888067^Lejeune^Marie-Claire^^^Dr.||20260510100000|ED|DOC-20260509-001|||20777888067^Lejeune^Marie-Claire^^^Dr.||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48cmVsYXRlZERvY3VtZW50IHR5cGVDb2RlPSJSUExDIj48cGFyZW50RG9jdW1lbnQ+PGlkIHJvb3Q9IjEuMi4yNTAuMS4yMTMuMS4xLjEiLz48L3BhcmVudERvY3VtZW50PjwvcmVsYXRlZERvY3VtZW50Pjxjb21wb25lbnQ+PHNlY3Rpb24+PHRleHQ+VmVyc2lvbiBjb3JyaWdlZTwvdGV4dD48L3NlY3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg==||||||C
PRT||UC||SB^Send by^participation|20777888067^Lejeune^Marie-Claire^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
PRT||UC||RCT^Results Copies To^participation|20888999078^Laurent^Bernard^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgY29ycmlnZSBkZSBNLkJvZGFydC4=||||||F
```

---

## 12. ORM^O01 - medication order

```
MSH|^~\&|DXCARE|CHU_ST_PIERRE|PHARMA_BE|CHU_ST_PIERRE|20260509091000||ORM^O01|MSG10012|P|2.5
PID|1||PAT23012^^^CHSP^PI|86021534217^^^^NN|Dubois^Marc-Antoine^R^^M.||19860215|M|||Rue du Midi 145^^Bruxelles^^1000^BE
PV1||I|CARDIO^Kamer 405^Bed 2^Cardiologie||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.|||MED
ORC|NW|ORD12201^DXCARE|FIL23101^PHARMA_BE||SC||^^^20260509091000^^R||20260509091000|20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.
OBR|1|ORD12201^DXCARE|FIL23101^PHARMA_BE|METOP^METOPROLOL 50MG^LOCAL|R|20260509090000|||||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.
RXO|METOP50^METOPROLOL TARTRATE 50MG^LOCAL||50|MG|TAB^TABLET^HL70292||||||1|2x per dag
```

---

## 13. SIU^S12 - new appointment scheduled

```
MSH|^~\&|DXCARE|AZ_MONICA|AGENDA_BE|AZ_MONICA|20260509103000||SIU^S12|MSG10013|P|2.5
SCH|APT55001^DXCARE|APT55001^AGENDA_BE|||||ROUTINE^Routine afspraak^HL70276|30^MIN|^^MIN|^Gastroscopie controle||||20333444023^Wouters^Katrien^^^Dr.|||20333444023^Wouters^Katrien^^^Dr.||BOOKED|
PID|1||PAT24212^^^AZM^PI|92041267834^^^^NN|Goossens^Lien^M^^Mevr.||19920412|F|||Plantin en Moretuslei 66^^Berchem^^2600^BE
PV1||O|ENDO^Zaal-1^1^Endoscopie||||20333444023^Wouters^Katrien^^^Dr.|||MED
RGS|1
AIS|1||GASTRO^Gastroscopie^LOCAL|20260520100000|||30^MIN
AIL|1||ENDO^Zaal-1^1^Endoscopie
AIP|1||20333444023^Wouters^Katrien^^^Dr.
```

---

## 14. SIU^S15 - appointment cancellation

```
MSH|^~\&|DXCARE|AZ_MONICA|AGENDA_BE|AZ_MONICA|20260512083000||SIU^S15|MSG10014|P|2.5
SCH|APT55001^DXCARE|APT55001^AGENDA_BE|||||ROUTINE^Routine afspraak^HL70276|30^MIN|^^MIN|^Gastroscopie controle||||20333444023^Wouters^Katrien^^^Dr.|||20333444023^Wouters^Katrien^^^Dr.||CANCELLED|
PID|1||PAT24212^^^AZM^PI|92041267834^^^^NN|Goossens^Lien^M^^Mevr.||19920412|F|||Plantin en Moretuslei 66^^Berchem^^2600^BE
PV1||O|ENDO^Zaal-1^1^Endoscopie||||20333444023^Wouters^Katrien^^^Dr.|||MED
```

---

## 15. ORU^R01 - microbiology result with antibiogram

```
MSH|^~\&|LABO_BE|CHU_LIEGE|DXCARE|CHU_LIEGE|20260509170000||ORU^R01|MSG10015|P|2.5
PID|1||PAT25312^^^CHUL^PI||Marchand^Olivier^V^^M.||19790928|M|||Boulevard d'Avroy 33^^Liege^^4000^BE
PV1||I|MED-INT^Kamer 512^Bed 1^Interne Geneeskunde||||20444555034^Simon^Christophe^^^Dr.|||MED
ORC|RE|ORD13301^DXCARE|FIL24201^LABO_BE||CM
OBR|1|ORD13301^DXCARE|FIL24201^LABO_BE|87040^URINEKWEEK^CPT4||||||||||||20999000089^Renard^Sylvie^^^Dr.||||||F
OBX|1|ST|11475-1^MICRO-ORGANISME^LN||Escherichia coli|||A|||F
OBX|2|NM|30004-6^KIEMGETAL^LN||100000|CFU/mL|||||F
OBX|3|ST|18907-6^AMOXICILLINE^LN||R|||R|||F
OBX|4|ST|18908-4^AMOXICILLINE-CLAVULAANZUUR^LN||S|||N|||F
OBX|5|ST|18928-2^CIPROFLOXACINE^LN||S|||N|||F
OBX|6|ST|18932-4^COTRIMOXAZOL^LN||R|||R|||F
OBX|7|ST|18964-7^NITROFURANTOINE^LN||S|||N|||F
```

---

## 16. ORU^R01 - pathology result with narrative text

```
MSH|^~\&|PATHOLOGIE|CHU_ST_PIERRE|DXCARE|CHU_ST_PIERRE|20260512140000||ORU^R01|MSG10016|P|2.5
PID|1||PAT28612^^^CHSP^PI||Moreau^Caroline^T^^Mevr.||19830517|F|||Chaussee de Charleroi 99^^Saint-Gilles^^1060^BE
PV1||I|CHIR^Kamer 210^Bed 1^Chirurgie||||21000111090^Claes^Dirk^^^Prof.^Dr.|||CHIR
ORC|RE|ORD14401^DXCARE|FIL25301^PATHOLOGIE||CM
OBR|1|ORD14401^DXCARE|FIL25301^PATHOLOGIE|88305^PATHOLOGISCH ONDERZOEK WEEFSEL^CPT4||||||||||||21111222001^Lambert^Helene^^^Dr.||||||F
OBX|1|FT|22637-3^PATHOLOGIE VERSLAG^LN|1|Macroscopie: Excisiebiopt rechter borst, 2.1 x 1.8 x 1.5 cm.\.br\Microscopie: Invasief ductaal carcinoom, graad 2 (Bloom-Richardson score 6/9). Tumorgrootte 14mm. Snijranden vrij (minimale marge 3mm). Geen lymfovasculaire invasie.\.br\Conclusie: pT1c invasief ductaal carcinoom graad 2, snijranden vrij.|||A|||F
OBX|2|CE|85319-2^HORMOONRECEPTOR ER^LN||POS^Positief 90%^LOCAL|||N|||F
OBX|3|CE|85337-4^HORMOONRECEPTOR PR^LN||POS^Positief 70%^LOCAL|||N|||F
OBX|4|CE|85318-4^HER2 STATUS^LN||NEG^Negatief (IHC 1+)^LOCAL|||N|||F
OBX|5|NM|85336-6^KI67 INDEX^LN||15|%|||||F
```

---

## 17. ORM^O01 - radiology order from EPR to RIS

```
MSH|^~\&|DXCARE|UZ_BRUSSEL|RISONWEB|UZ_BRUSSEL|20260509104500||ORM^O01|MSG10017|P|2.5.1
PID|1||PAT29712^^^UZB^PI||Coppens^Thomas^D^^Dhr.||19850719|M|||Boulevard de Smet de Nayer 44^^Laeken^^1020^BE||^^PH^02-588-5222
PV1||O|ORTHO^Consult-2^1^Orthopedie||||21222333012^Peeters^Stefan^^^Dr.|||MED
ORC|NW|ORD15501^DXCARE|FIL26401^RISONWEB||SC||^^^20260509104500^^R||20260509104500|21222333012^Peeters^Stefan^^^Dr.
OBR|1|ORD15501^DXCARE|FIL26401^RISONWEB|73630^RX VOET 3 OPNAMES^CPT4|R|20260509103000|||||||21222333012^Peeters^Stefan^^^Dr.|||Chronische pijn voorvoet, uitsluiten stressfractuur||CR|SC
DG1|1|ICD10|M79.67^Pijn voet^ICD10||20260509
```

---

## 18. ADT^A28 - add person information (master patient index)

```
MSH|^~\&|DXCARE|AZ_DELTA|MPI_BE|AZ_DELTA|20260509070000||ADT^A28^ADT_A05|MSG10018|P|2.5
EVN|A28|20260509070000
PID|1||PAT30812^^^AZD^PI|97122078345^^^^NN|Bogaert^Emma^H^^Mevr.||19971220|F|||Brugsesteenweg 77^^Roeselare^^8800^BE||^^PH^051-456789~^^CP^0498-223344~^^Internet^emma.bogaert@outlook.be
PD1|||AZ DELTA^^AZD
```

---

## 19. ADT^A31 - update person information in master patient index

```
MSH|^~\&|DXCARE|AZ_DELTA|MPI_BE|AZ_DELTA|20260509113000||ADT^A31^ADT_A05|MSG10019|P|2.5
EVN|A31|20260509113000
PID|1||PAT30812^^^AZD^PI|97122078345^^^^NN|Bogaert-Peeters^Emma^H^^Mevr.||19971220|F|||Mandellaan 14^^Roeselare^^8800^BE||^^PH^051-456789~^^CP^0498-223344~^^Internet^emma.bogaert@outlook.be
PD1|||AZ DELTA^^AZD
```

---

## 20. ORU^R01 - discharge letter with base64 CDA and mail routing

```
MSH|^~\&|DXCARE|CHU_ST_PIERRE|DMP_BE|EHEALTH_BE|20260515160000||ORU^R01^ORU_R01|MSG10020|P|2.5
PID|1||PAT23012^^^CHSP^PI|86021534217^^^^NN|Dubois^Marc-Antoine^R^^M.||19860215|M|||Rue du Midi 145^^Bruxelles^^1000^BE
PV1||I|CARDIO^Kamer 405^Bed 2^Cardiologie||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.|||MED
ORC|RE|ORD16601^DXCARE|FIL27501^DMP_BE||CM
OBR|1|ORD16601^DXCARE|FIL27501^DMP_BE|34133-9^Lettre de sortie^LN||||||||||||20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.||||||F
OBX|1|ED|34133-9^Lettre de sortie^LN||^TEXT^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+TGV0dHJlIGRlIHNvcnRpZSAtIENhcmRpb2xvZ2llPC90aXRsZT48Y29tcG9uZW50PjxzZWN0aW9uPjx0ZXh0PlBhdGllbnQgc29ydGkgYXByZXMgYW5naW9wbGFzdGllIGNvcm9uYWlyZS4gVHJhaXRlbWVudDogQXNwaXJpbmUgMTAwbWcsIENsb3BpZG9ncmVsIDc1bWcsIEF0b3J2YXN0YXRpbmUgNDBtZy48L3RleHQ+PC9zZWN0aW9uPjwvY29tcG9uZW50PjwvQ2xpbmljYWxEb2N1bWVudD4=||||||C
PRT||UC||SB^Send by^participation|20555666045^Van Damme^Frederik^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI|||CHU Saint-Pierre^^^^^NIHDI-ST&2.16.840.1.113883.3.6777.5.2&ISO^FINEG^^^71000436
PRT||UC||RCT^Results Copies To^participation|20888999078^Laurent^Bernard^^^^^^NIHDI&2.16.840.1.113883.3.6777.5.2&ISO^D^^^NIHDI
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
