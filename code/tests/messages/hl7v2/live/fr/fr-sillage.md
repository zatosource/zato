# Clinicom / Sillage (SIB) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission (inpatient)

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20231130103019||ADT^A01^ADT_A01|20231130103019|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231130103019||||20231130103019
PID|||1183028366817078421184^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-72814^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||DELACROIX^Pascal^^^^^L|JOUBERT^^^^^^M|19830417|M|||12 Rue des Arenes^^Nantes^^44000^FRA^H|||||||AN3891^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I|||||||||||||||||VN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV6323^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231130103019||INSERT|N
ZFA||||N||N|N
ZFD|||N|N
```

---

## 2. ADT^A04 - Emergency registration

```
MSH|^~\&|SILLAGE|SIB_URG|SIH_Receptor|GHT-ARTOIS|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-61847^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||BERGER^Vincent^^^^^L|ARNAULT^^^^^^M|19921214075500|M|||^^^^^FRA|||||||AN2063^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN3195^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV4521^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N
ZFD|||N|N
```

---

## 3. ADT^A28 - Add patient demographics (ITI-30)

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||201089745632180^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||COLLET^SERGE^XAVIER^^^^L||19890422|M|||8 Avenue des Lilas^^Bordeaux^^33000^FRA^H~^^^^^^BDL|||||||AN2148^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 4. ADT^A04 - Registration with attending physician

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20210427122641||ADT^A04^ADT_A01|20210427122641|P|2.5||||||UNICODE UTF-8
EVN||20210427122641||||20210427122641
PID|||DDS-61503^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||DUFOUR^Gilles^^^^^L|LANGLOIS^^^^^^M|20080316214522|M|||^^^^^ESP|||||||AN1852^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||R||L|||10200537642^RENAUD^Sandrine|10003491087^PERROT^Nathalie|||||||||10004228319^JACQUET^Damien||VN2384^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
ZBE|MOV3209^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210427122641||INSERT|N
```

---

## 5. ADT^A28 - Demographics with INS qualified identity

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20240423154852||ADT^A28^ADT_A05|20240423154852|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240423154852
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~2640715987234^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS~IPP-52789^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||CHARLES^DANIELLE^PIERRETTE^^^^L|BARRE^^^^^^M|19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H||0561238947|||||||AN6271^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 6. ADT^A02 - Transfer between wards

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20231201091500||ADT^A02^ADT_A02|20231201091500|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231201091500||||20231201091500
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-52789^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||CHARLES^DANIELLE^PIERRETTE^^^^L|BARRE^^^^^^M|19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H||0561238947|||||||AN6271^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|PNEUMO^P301^2^^^SIB||||10700891234^LEMAITRE^Dominique||||||||||||||VN8345^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231128100000|||||||V
PV2||||||||20231215
ZBE|MOV9101^SIB^2.16.840.1.113883.2.8.3.7^ISO|20231201091500||UPDATE|N
ZFD|||N|N
```

---

## 7. ADT^A03 - Discharge

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20231215160000||ADT^A03^ADT_A03|20231215160000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231215160000||||20231215160000
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-52789^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||CHARLES^DANIELLE^PIERRETTE^^^^L|BARRE^^^^^^M|19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H||0561238947|||||||AN6271^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|PNEUMO^P301^2^^^SIB||||10700891234^LEMAITRE^Dominique||||||||||||||VN8345^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231128100000|20231215160000|||||V
ZBE|MOV9102^SIB^2.16.840.1.113883.2.8.3.7^ISO|20231215160000||UPDATE|N
ZFD|||N|N
```

---

## 8. ADT^A08 - Update patient information

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20231202140000||ADT^A08^ADT_A01|20231202140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231202140000||||20231202140000
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-52789^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||CHARLES^DANIELLE^PIERRETTE^^^^L|BARRE^^^^^^M|19640715|F|||22 Boulevard Carnot^^Toulouse^^31000^FRA^H||0561238947|||||||AN6271^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|PNEUMO^P301^2^^^SIB||||10700891234^LEMAITRE^Dominique||||||||||||||VN8345^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231128100000|||||||V
ZBE|MOV9103^SIB^2.16.840.1.113883.2.8.3.7^ISO|20231202140000||UPDATE|N
ZFD|||N|N
```

---

## 9. ADT^A05 - Pre-admission (psychiatry)

```
MSH|^~\&|SILLAGE|SIB_PSY|SIH_Receptor|GHT-ARTOIS|20231208110000||ADT^A05^ADT_A05|20231208110000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231208110000||||20231208110000
PID|||185041276543210^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-53601^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||POIRIER^HUGUETTE^MARGUERITE^^^^L|LANGLOIS^^^^^^M|19850412|F|||9 Allee des Chenes^^Lens^^62300^FRA^H||0321894567|||||||AN5847^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||I|PSY^PSY401^1^^^SIB||||10800912345^COULON^Mathieu||||||||||||||VN7623^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||||||||||V
ZBE|MOV9201^SIB^2.16.840.1.113883.2.8.3.7^ISO|20231208110000||INSERT|N
ZFD|||N|N
```

---

## 10. ADT^A12 - Cancel transfer

```
MSH|^~\&|SILLAGE|SIB_MCO|SIH_Receptor|GHT-ARTOIS|20231202080000||ADT^A12^ADT_A12|20231202080000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231202080000||||20231202080000
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-52789^^^SIB&1.2.250.1.213.1.1.3.1&ISO^PI||CHARLES^DANIELLE^PIERRETTE^^^^L|BARRE^^^^^^M|19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H||0561238947|||||||AN6271^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^C201^1^^^SIB||||10700891234^LEMAITRE^Dominique||||||||||||||VN8345^^^SIB&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231128100000|||||||V
ZBE|MOV9104^SIB^2.16.840.1.113883.2.8.3.7^ISO|20231202080000||CANCEL|N
ZFD|||N|N
```

---

## 11. ORU^R01 - Biology report for DMP/MSSante

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231215103000||ORU^R01^ORU_R01|MSG20231215103000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|BIOLOGIE^BIO301^1^^^SIB
ORC|NW||ORD-SIB-20231215|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-20231215|11502-2^CR d'examens biologiques^LN
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^COULON^Hugo^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^264071598723461@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
OBX|2|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
OBX|3|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|8|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|13|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 12. ORU^R01 - Radiology report with PS masking, patient MSSante only

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231216140000||ORU^R01^ORU_R01|MSG20231216140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-20231216|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-20231216|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^264071598723461@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F
```

---

## 13. ORU^R01 - Document replacement

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231218093000||ORU^R01^ORU_R01|MSG20231218093000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-20231218|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-20231218|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^COULON^Hugo^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^264071598723461@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 14. ORU^R01 - Document deletion

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231217080000||ORU^R01^ORU_R01|MSG20231217080000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-20231217|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-20231217|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10234567890^COULON^Hugo^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 15. MDM^T02 - Medical document initial transmission

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231219110000||MDM^T02^MDM_T02|MSG20231219110000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20231219110000
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-20231219
OBR|1||ORD-SIB-20231219|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20231219110000|||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.9012^SIB|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^COULON^Hugo^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^264071598723461@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 16. MDM^T10 - Document replacement via MDM

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231220090000||MDM^T10^MDM_T02|MSG20231220090000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20231220090000
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-20231220
OBR|1||ORD-SIB-20231220|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20231220090000|||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.9012^SIB|1.2.250.1.213.1.1.9.9011^SIB|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^COULON^Hugo^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^hugo.coulon@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^264071598723461@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 17. ACK - Positive acknowledgment

```
MSH|^~\&|SIH_Receptor|GHT-ARTOIS|SILLAGE|SIB_MCO|20231130093020||ACK^A01^ACK|20231130093020|P|2.5^FRA^2.10
MSA|AA|20231130103019
```

---

## 18. ACK - Negative acknowledgment with ERR segment

```
MSH|^~\&|SIH_Receptor|GHT-ARTOIS|SILLAGE|SIB_MCO|20231208120000||ACK^A05^ACK|20231208120000|P|2.5^FRA^2.10
MSA|AE|20231208110000
ERR|||207^Application internal error^HL70357||||Duplicate movement identifier detected
```

---

## 19. ORU^R01 - Embedded JPEG radiology image (ED/Base64)

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231222143000||ORU^R01^ORU_R01|MSG20231222143000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-IMG-20231222|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-IMG-20231222|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAAcP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgA/9k=||||||F
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 20. ORU^R01 - Embedded PDF scanned document (ED/Base64)

```
MSH|^~\&|SILLAGE|SIB_MCO|PFI_GESTIONNAIRE|GHT-ARTOIS|20231223161500||ORU^R01^ORU_R01|MSG20231223161500|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||264071598723461^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CHARLES^DANIELLE^^^^^L||19640715|F|||14 Rue de la Paix^^Toulouse^^31000^FRA^H
PV1||I|IMAGERIE^IMG301^1^^^SIB
ORC|NW||ORD-SIB-SCAN-20231223|||||||80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-SIB-SCAN-20231223|11488-4^Document numerise^LN
OBX|1|ED|11488-4^Document numerise^LN||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjMgMDAwMDAgbiAKMDAwMDAwMDEyMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIxNQolJUVPRgo=||||||F
PRT||UC||SB^Send by^participation|80234567891^GILBERT^Lucie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
