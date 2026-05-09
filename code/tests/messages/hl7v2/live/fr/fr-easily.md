# Easily (formerly Agfa Healthcare France) - real HL7v2 ER7 messages

## 1. ADT^A01 - Patient admission with INS (Gazelle Patient Manager, interopsegur.esante.gouv.fr)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - IHE PAM.fr ITI-31 test transaction #196951 -->

```
MSH|^~\&|EASILY|CHU_NICE|GESTIONNAIRE|PFI|20240214100721||ADT^A01^ADT_A01|20240214100721|P|2.5||||||UNICODE UTF-8
EVN||20240214100721||||20210906164312
PID|||20668^^^CHU_NICE&2.16.840.1.113883.2.8.3.7&ISO^PI~284063817529413^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||DUVAL^CATHERINE^^^^^L|ROBIN^^^^^^M|19910415|F|||14 avenue Victor Hugo^^NICE^^06000^FRA^H|||||||AN2618^^^CHU_NICE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I||L|||10003244273^BLANCHARD^Patrice|10003246534^FERRAND^Nathalie|||||||||10003217402^TESSIER^Michel||VN3770^^^CHU_NICE&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 2. ADT^A28 - Patient identity creation with qualified INS (Gazelle Patient Manager)

<!-- Source: https://interop.referencement.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=95830 - IHE PAM.fr ITI-30 test transaction #95830, March 2026 -->

```
MSH|^~\&|EASILY|HOPITAL_LILLE|GESTIONNAIRE|PFI|20260304195953||ADT^A28^ADT_A05|20260304195953|P|2.5||||||ASCII
EVN||20260304195953
PID|||284063817529413^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~20668^^^HOPITAL_LILLE&2.16.840.1.113883.2.8.3.7&ISO^PI||DUVAL^CATHERINE^^^^^L|ROBIN^^^^^^M|19910415|F|||14 avenue Victor Hugo^^NICE^^06000^FRA^H|||||||AN2618^^^HOPITAL_LILLE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||N
ZFD|||N|N
```

---

## 3. ADT^A28 - Patient registration with DMP consent flag (Gazelle Patient Manager)

<!-- Source: https://interop.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=95617 - Gazelle ITI-30 test, adapted for Easily context -->

```
MSH|^~\&|EASILY|CHU_MONTPELLIER|RECEPTEUR|PFI|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||175098264351720^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||HENRY^PHILIPPE^ARNAUD^^^^L||19990823|M|||27 boulevard de la Liberte^^Lille^^59000^FRA^H~^^^^^^BDL|||||||AN2607^^^CHU_MONTPELLIER&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 4. ADT^A31 - Patient identity update (Gazelle PAM.fr pattern)

<!-- Source: https://interop.esante.gouv.fr/PatientManager/messages/messageDisplay.seam - Gazelle ITI-30 A31 test pattern, adapted from transaction #73746 -->

```
MSH|^~\&|EASILY|HOPITAL_BORDEAUX|RECEPTEUR|PFI|20230706113531||ADT^A31^ADT_A05|MSG20230706E01|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230706113531
PID|1||92g7eg4b-d4cg-56b9-c0ed-0ebc813f89f8^^^HOPITAL_BORDEAUX&&M^PI||AUBERT^NATHALIE^^^^^^D^A~GUILLOT^NATHALIE^^^^^L^A||19860509|F|||19 rue Montaigne^^Bordeaux^^33000^FRA^H|||||||||||||||||||N||PROV|20230706113531
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 5. ADT^A01 - Admission with SIGEMS-style demographics (esir-hl7-tp)

<!-- Source: https://github.com/cdelanchy/esir-hl7-tp/blob/main/doc/HL7_guide_fr.md - ESIR HL7 TP French guide, ADT A01 SIGEMS example adapted for Easily -->

```
MSH|^~\&|EASILY|EASILY|ENOVACOM|ENOVACOM|20151125123110.703+0100||ADT^A01^ADT_A01|54741010000051070000|P|2.5|||||FRA|8859/1
EVN||20151125123110||A01||20151125123007
PID|||79278^^^EASILY^PI||CHARLES^CORINNE^^^^^D~JACOB^VALERIE^^^^^L||19280314|F|||8 RUE DES LILAS^^SAINT MALO^^35400^^H
PV1||I|CH01^213^213^330780000||PA79611^^^EASILY^AN^^20151027||10002223773^PICHON^Romain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
```

---

## 6. ADT^A04 - Outpatient registration (numlor.fr pattern adapted for Easily)

<!-- Source: https://numlor.fr/elearning/reseaux/co/5HL7.html - numlor.fr hospital HL7 training -->

```
MSH|^~\&|EASILY|HOPITAL_NANTES|LAB|LABSYSTEM|20200410160227||ADT^A04^ADT_A04|MSG20200410E01|P|2.3|||NE
PID|||765432^^^EASILY^PI||ROBIN^JEROME||19740323|M|||15 RUE PAUL BERT^^^^44000^NANTES||^^^^^^0647839215|||||
PV1|1|O|||||83^MOULIN^DANIELLE||||||||||||23487|||||||||||||||||||||||||20200410160227||||||
```

---

## 7. ORU^R01 - Biology report CDA transmission, initial (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 0, transmission initiale CR biologie -->

```
MSH|^~\&|EASILY|CHU_TOULOUSE|PFI|PFI|20240515103000||ORU^R01^ORU_R01|MSG20240515E01|P|2.5|||||FRA|UNICODE UTF-8
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M|||31 rue Gambetta^^Toulouse^^31000^FRA^H
ORC|NW
OBR|1
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^253097812634581@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
OBX|2|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F|
OBX|3|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|13|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 8. ORU^R01 - Radiology report with masking (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 1, CR imagerie medicale avec masquage PS -->

```
MSH|^~\&|EASILY|CHU_LYON|PFI|PFI|20240516090000||ORU^R01^ORU_R01|MSG20240516E01|P|2.5|||||FRA|UNICODE UTF-8
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^253097812634581@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
NTE|1|||FIN|
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F|
```

---

## 9. ORU^R01 - Document deletion request (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 2, suppression CR imagerie -->

```
MSH|^~\&|EASILY|CHU_STRASBOURG|PFI|PFI|20240517140000||ORU^R01^ORU_R01|MSG20240517E01|P|2.5|||||FRA|UNICODE UTF-8
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 10. ORU^R01 - Document replacement (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 3, remplacement CR imagerie -->

```
MSH|^~\&|EASILY|CHU_MARSEILLE|PFI|PFI|20240518110000||ORU^R01^ORU_R01|MSG20240518E01|P|2.5|||||FRA|UNICODE UTF-8
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^253097812634581@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 11. MDM^T02 - Initial medical document notification (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS MDM example 0, transmission initiale CR imagerie -->

```
MSH|^~\&|EASILY|CHU_BORDEAUX|PFI|PFI|20240519143000||MDM^T02^MDM_T02|MSG20240519E01|P|2.6|||||FRA|UNICODE UTF-8
EVN||20240519143000
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
PV1||N
TXA|1|CR^Compte-Rendu|TX||||20240519143000||||||DOC-2024-E01||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^253097812634581@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 12. MDM^T04 - Document status change / deletion (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS MDM example 2, suppression CR imagerie, event T04 -->

```
MSH|^~\&|EASILY|CHU_NANTES|PFI|PFI|20240520101500||MDM^T04^MDM_T02|MSG20240520E01|P|2.6|||||FRA|UNICODE UTF-8
EVN||20240520101500
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
PV1||N
TXA|1|CR^Compte-Rendu|TX||||20240520101500||||||DOC-2024-E02||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 13. MDM^T10 - Document replacement notification (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS MDM example 3, remplacement CR imagerie, event T10 -->

```
MSH|^~\&|EASILY|CHU_LILLE|PFI|PFI|20240521083000||MDM^T10^MDM_T02|MSG20240521E01|P|2.6|||||FRA|UNICODE UTF-8
EVN||20240521083000
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M
PV1||N
TXA|1|CR^Compte-Rendu|TX||||20240521083000||||||DOC-2024-E03||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80234567891^BLANCHARD^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^FERRAND^Fabien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^fabien.ferrand@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^253097812634581@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```

---

## 14. ACK^A01 - Acknowledgment for ADT admission (Gazelle PAM.fr ACK pattern)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - Gazelle PAM.fr ACK response -->

```
MSH|^~\&|PFI|PFI|EASILY|CHU_NICE|20240214100722||ACK^A01^ACK|20240214100722|P|2.5^FRA^2.10||||||UNICODE UTF-8
MSA|AA|20240214100721
```

---

## 15. ACK^A01 - Application error acknowledgment with ERR segment (Gazelle PAM.fr)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - Gazelle PAM.fr ACK with error, duplicate visit number -->

```
MSH|^~\&|PFI|PAM_FR|EASILY|CHU_NICE|20240214100722||ACK^A01^ACK|20240214100722|P|2.5^FRA^2.10||||||UNICODE UTF-8
MSA|AE|20240214100721
ERR||PV1^1^19^1|205|E||||This identifier is already used: VN3770\S\\S\\S\GZL_INTEROP\T\2.16.840.1.113883.2.8.3.7\T\ISO\S\VN
```

---

## 16. ADT^A03 - Patient discharge (IHE PAM.fr ADT A03)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A03 discharge profile; https://github.com/Interop-Sante/ihe.iti.pam.fr -->

```
MSH|^~\&|EASILY|CHU_GRENOBLE|RECEPTEUR|PFI|20240601150000||ADT^A03^ADT_A03|MSG20240601E01|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240601150000||||20240601145500
PID|||89345^^^CHU_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^PI~268114375290146^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||GAILLARD^CHRISTINE^^^^^L|HUET^^^^^^M|19430506|F|||5 cours Mirabeau^^Grenoble^^38000^FRA^H|||||||AN5632^^^CHU_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^204^1^CHU_GRENOBLE^^N^A^2|R|||10002345678^TESSIER^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN9943^^^CHU_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||20240520|20240601150000|||||||||||||V
```

---

## 17. ADT^A02 - Patient transfer between services (IHE PAM.fr ADT A02)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A02 transfer; https://github.com/Interop-Sante/ihe.iti.pam.fr -->

```
MSH|^~\&|EASILY|CHU_RENNES|RECEPTEUR|PFI|20240515093000||ADT^A02^ADT_A02|MSG20240515E02|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240515093000||||20240515092500
PID|||56789^^^CHU_RENNES&2.16.840.1.113883.2.8.3.7&ISO^PI~248094817236501^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||GUILLOT^DOMINIQUE^^^^^L||19480902|F|||9 place Bellecour^^Lyon^^69001^FRA^H
PV1||I|NEURO^301^3^CHU_RENNES^^N^A^2|R||CARDIO^204^1^CHU_RENNES^^N^A^2|10002345678^TESSIER^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN5567^^^CHU_RENNES&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 18. ADT^A08 - Patient demographics update (IHE PAM.fr ADT A08)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A08; https://fr.community.intersystems.com/post/contenu-du-message-hl7-adt-et-exemple-du-message-adta04 -->

```
MSH|^~\&|EASILY|CHU_STRASBOURG|RECEPTEUR|PFI|20240610140000||ADT^A08^ADT_A01|MSG20240610E01|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240610140000
PID|||03456^^^CHU_STRASBOURG&2.16.840.1.113883.2.8.3.7&ISO^PI~161085193478520^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||HUET^ARNAUD^^^^^L|HUET^^^^^^M|19510809|M|||6 rue de la Paix^^Strasbourg^^67000^FRA^H||^PRN^PH^^^03^88234567|||||||AN7890^^^CHU_STRASBOURG&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|MED_INT^105^2^CHU_STRASBOURG^^N^A^1|||10008765432^GUYOT^Estelle^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN0123^^^CHU_STRASBOURG&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 19. ORU^R01 - Radiology image embedded as JPEG (HL7 OBX ED image format, Agfa conformance)

<!-- Source: https://hl7.eu/refactored/segOBX.html - HL7 OBX ED data type for embedded images; https://stackoverflow.com/questions/20219223/extract-images-from-hl7-files - OBX image embedding; https://www.agfa.com/he/global/en/internet/he/library/libraryopen?ID=69750221 - Agfa HL7 conformance statement supports ORU -->

```
MSH|^~\&|EASILY|CHU_PARIS|GESTIONNAIRE|PFI|20240625090000||ORU^R01^ORU_R01|MSG20240625EIMG01|P|2.5|||||FRA|UNICODE UTF-8
PID|||253097812634581^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MORIN^FRANCOIS^^^^^L||19530928|M|||31 rue Gambetta^^Paris^^75012^FRA^H
ORC|NW
OBR|1||RAD-2024-E01|18748-4^CR d'imagerie medicale^LN|||20240625090000|||||||10003244273^BLANCHARD^Patrice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
OBX|1|ED|18748-4^CR d'imagerie medicale^LN|1|EASILY^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SFhSRTQ3N0BTZH/aAAwDAQACEQMRAD8A+f6KKKACiiigAooooAKKKKACiiigAooooA//2Q==||||||F|
OBX|2|ST|18748-4^CR d'imagerie medicale^LN|1.1|Thorax radiograph: no acute cardiopulmonary disease, heart size normal||||||F|
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```

---

## 20. ORU^R01 - Dermatology with embedded PNG image (HL7 OBX ED image, Dedalus context)

<!-- Source: https://hl7.eu/refactored/segOBX.html - HL7 OBX ED data type; https://stackoverflow.com/questions/20219223/extract-images-from-hl7-files - OBX image embedding; https://6b.health/insight/dedalus-lorenzo-integration-hl7-v2-message-flows-from-source-to-target/ - Dedalus Lorenzo supports HL7 ORU -->

```
MSH|^~\&|EASILY|CHU_LYON|GESTIONNAIRE|PFI|20240701113000||ORU^R01^ORU_R01|MSG20240701EIMG02|P|2.5|||||FRA|UNICODE UTF-8
PID|||268114375290146^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||GAILLARD^CHRISTINE^^^^^L|HUET^^^^^^M|19430506|F|||5 cours Mirabeau^^Lyon^^69001^FRA^H
ORC|NW
OBR|1||DERM-2024-E01|72170-4^Photographic image^LN|||20240701113000|||||||10002345678^TESSIER^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
OBX|1|ED|72170-4^Photographic image^LN|1|EASILY^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAWISURBVGiB7ZprbBRVFMd/M7PbbbdLu7SlpaUPKAVKKRQoIIgIKD4QNSoajYkmxvhBE2P84CNGP2jiI0aNGn0k+kGNxgckGkVFxQcqikIVBOVRoaXQQlu6222X7s7OeObezmx3Z7e7s8WE/JPNzD33njn/c+65Z+4sOj09PQYOQPE/e+A/B0dEYg4cEYk5cEQk5sARkZgDR0RiDhwRiTlwRCTmwBGRmANHRGIOHBGJOXBEJObAEZGYA0dEYg4cEYk5+BcSVbKQjSf3DQAAAABJRU5ErkJggg==||||||F|
OBX|2|ST|72170-4^Photographic image^LN|1.1|Skin lesion right shoulder: 2.0cm x 1.8cm, hyperpigmented, irregular margins||||||F|
PRT||UC||SB^Send by^participation|10002345678^TESSIER^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||CHU_LYON^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^750012345
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```
