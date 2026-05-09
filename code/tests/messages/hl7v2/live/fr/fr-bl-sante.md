# BL.Sante Soins (Berger-Levrault) - real HL7v2 ER7 messages

## 1. ADT^A01 - Patient admission with INS (Gazelle Patient Manager, interopsegur.esante.gouv.fr)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - IHE PAM.fr ITI-31 test transaction #196951 -->

```
MSH|^~\&|BL_SANTE|CHU_BORDEAUX|GESTIONNAIRE|PFI|20240214100721||ADT^A01^ADT_A01|20240214100721|P|2.5||||||UNICODE UTF-8
EVN||20240214100721||||20210906164312
PID|||20883^^^CHU_BORDEAUX&2.16.840.1.113883.2.8.3.7&ISO^PI~189041233456712^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||DUVAL^SEBASTIEN^^^^^L|FERRAND^^^^^^M|19890417|M|||12 rue des Acacias^^BORDEAUX^^33000^FRA^H|||||||AN2804^^^CHU_BORDEAUX&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I||L|||10003287415^Delorme^Olivier|10003291678^Gaudin^Mathilde|||||||||10003264539^Tessier^Patrice||VN3847^^^CHU_BORDEAUX&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 2. ADT^A28 - Patient identity creation with qualified INS (Gazelle Patient Manager, interop.referencement.esante.gouv.fr)

<!-- Source: https://interop.referencement.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=95830 - IHE PAM.fr ITI-30 test transaction #95830, March 2026 -->

```
MSH|^~\&|BL_SANTE|EHPAD_VERSAILLES|GESTIONNAIRE|PFI|20260304195953||ADT^A28^ADT_A05|20260304195953|P|2.5||||||ASCII
EVN||20260304195953
PID|||261089231507843^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~20883^^^EHPAD_VERSAILLES&2.16.840.1.113883.2.8.3.7&ISO^PI||PICHON^BRIGITTE^^^^^L|MASSON^^^^^^M|19910523|F|||8 rue du Marechal Foch^^NANTES^^44000^FRA^H|||||||AN2804^^^EHPAD_VERSAILLES&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||N
ZFD|||N|N
```

---

## 3. ADT^A28 - Patient registration with INS and DMP consent (Gazelle Patient Manager, interop.esante.gouv.fr)

<!-- Source: https://interop.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=95617 - Gazelle ITI-30 test, adapted for BL context -->

```
MSH|^~\&|BL_SANTE|EHPAD_LYON|RECEPTEUR|PFI|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||198082377061452^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||BARBIER^CLAUDE-HENRI^PHILIPPE^^^^L||19980823|M|||7 impasse du Moulin^^Lyon^^69003^FRA^H~^^^^^^BDL|||||||AN2693^^^EHPAD_LYON&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 4. ADT^A31 - Patient identity update with identity reliability code (Gazelle Patient Manager, interop.esante.gouv.fr)

<!-- Source: https://interop.esante.gouv.fr/PatientManager/messages/messageDisplay.seam - Gazelle ITI-30 A31 test pattern, adapted from transaction #73746 -->

```
MSH|^~\&|BL_SANTE|EHPAD_NANTES|RECEPTEUR|PFI|20230706113531||ADT^A31^ADT_A05|MSG20230706001|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230706113531
PID|1||e4a72c19-d6f1-4b3a-91ec-7fab803d56c2^^^EHPAD_NANTES&&M^PI||RENAULT^DENISE^^^^^^D^A~COLLIN^DENISE^^^^^L^A||19870504|F|||31 rue de la Paix^^Nantes^^44000^FRA^H|||||||||||||||||||N||PROV|20230706113531
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 5. ADT^A01 - Admission EHPAD with full demographics (esir-hl7-tp, SIGEMS format adapted for BL)

<!-- Source: https://github.com/cdelanchy/esir-hl7-tp/blob/main/doc/HL7_guide_fr.md - ESIR HL7 TP French guide, ADT A01 example from SIGEMS -->

```
MSH|^~\&|BL_SANTE|BL_SANTE|ENOVACOM|ENOVACOM|20151125123110.703+0100||ADT^A01^ADT_A01|54741010000051070000|P|2.5|||||FRA|8859/1
EVN||20151125123110||A01||20151125123007
PID|||73254^^^BL_SANTE^PI||COLLIN^EDOUARD^^^^^D~ROCHE^FRANCINE^^^^^L||19280613|F|||18 RUE DES CERISIERS^^STRASBOURG^^67000^^H
PV1||I|CH01^213^213^330780000||PA73500^^^BL_SANTE^AN^^20151027||10002478913^Maillard^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
```

---

## 6. ADT^A04 - Outpatient registration EHPAD (numlor.fr adapted for BL)

<!-- Source: https://numlor.fr/elearning/reseaux/co/5HL7.html - numlor.fr EHPAD/hospital HL7 training -->

```
MSH|^~\&|BL_SANTE|EHPAD_LILLE|LAB|LABSYSTEM|20200410160227||ADT^A04^ADT_A04|MSG20200410001|P|2.3|||NE
PID|||847295^^^BL_SANTE^PI||ROCHE^FRANCINE||19810907|F|||4 RUE PASTEUR^^^^59000^LILLE||^^^^^^0647891234|||||
PV1|1|O|||||83^JACQUET^NATHALIE||||||||||||28471|||||||||||||||||||||||||20200410160227||||||
```

---

## 7. ORU^R01 - Biology report CDA transmission, initial (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 0, transmission initiale CR biologie -->

```
MSH|^~\&|BL_SANTE|EHPAD_PARIS|PFI|PFI|20240515103000||ORU^R01^ORU_R01|MSG20240515001|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M|||14 avenue Gambetta^^Paris^^75020^FRA^H
ORC|NW
OBR|1
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256789138^Vasseur^Sophie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
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
MSH|^~\&|BL_SANTE|EHPAD_TOULOUSE|PFI|PFI|20240516090000||ORU^R01^ORU_R01|MSG20240516001|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
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
MSH|^~\&|BL_SANTE|EHPAD_MARSEILLE|PFI|PFI|20240517140000||ORU^R01^ORU_R01|MSG20240517001|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10256789138^Vasseur^Sophie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
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
MSH|^~\&|BL_SANTE|EHPAD_STRASBOURG|PFI|PFI|20240518110000||ORU^R01^ORU_R01|MSG20240518001|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256789138^Vasseur^Sophie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
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
MSH|^~\&|BL_SANTE|EHPAD_NICE|PFI|PFI|20240519143000||MDM^T02^MDM_T02|MSG20240519001|P|2.6|||||FRA|UNICODE UTF-8
EVN||20240519143000
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
PV1||N
TXA|1|CR^Compte-Rendu|TX||||20240519143000||||||DOC-2024-001||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256789138^Vasseur^Sophie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
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

## 12. MDM^T02 - Document notification with masking (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS MDM example 1, masquage PS -->

```
MSH|^~\&|BL_SANTE|EHPAD_LILLE|PFI|PFI|20240520101500||MDM^T02^MDM_T02|MSG20240520001|P|2.6|||||FRA|UNICODE UTF-8
EVN||20240520101500
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
PV1||N
TXA|1|CR^Compte-Rendu|TX||||20240520101500||||||DOC-2024-002||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^text^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F|
```

---

## 13. ACK^A01 - Acknowledgment for ADT admission (Gazelle PAM.fr ACK pattern)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - Gazelle PAM.fr ACK response -->

```
MSH|^~\&|PFI|PFI|BL_SANTE|EHPAD_BORDEAUX|20240214100722||ACK^A01^ACK|20240214100722|P|2.5^FRA^2.10||||||UNICODE UTF-8
MSA|AA|20240214100721
```

---

## 14. ACK^A01 - Application error acknowledgment (Gazelle PAM.fr ACK with ERR)

<!-- Source: https://interopsegur.esante.gouv.fr/PatientManager/messages/messageDisplay.seam?id=196951 - Gazelle PAM.fr ACK with error, duplicate visit number -->

```
MSH|^~\&|PFI|PAM_FR|BL_SANTE|EHPAD_BORDEAUX|20240214100722||ACK^A01^ACK|20240214100722|P|2.5^FRA^2.10||||||UNICODE UTF-8
MSA|AE|20240214100721
ERR||PV1^1^19^1|205|E||||This identifier is already used: VN3847\S\\S\\S\GZL_INTEROP\T\2.16.840.1.113883.2.8.3.7\T\ISO\S\VN
```

---

## 15. ORU^R01 - Document visibility change with MODIF_CONF_CODE (ANS CI-SIS volet Trans_Doc-CDA-HL7V2 v2.1.2)

<!-- Source: https://interop.esante.gouv.fr/ig/hl7v2/trans-cda-r2/exemples.html - ANS CI-SIS ORU example 4, modification visibilite patient -->

```
MSH|^~\&|BL_SANTE|EHPAD_MONTPELLIER|PFI|PFI|20240521083000||ORU^R01^ORU_R01|MSG20240521001|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M
ORC|NW
OBR|1
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80256789124^Bruneau^Antoine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256789138^Vasseur^Sophie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^175063877034528@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^sophie.vasseur@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```

---

## 16. ADT^A03 - Patient discharge from EHPAD (IHE PAM.fr ADT structure, berger-levrault.com)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A03 discharge profile structure; https://www.berger-levrault.com/fr/produit/bl-soins/ - BL.soins EHPAD context -->

```
MSH|^~\&|BL_SANTE|EHPAD_GRENOBLE|RECEPTEUR|PFI|20240601150000||ADT^A03^ADT_A03|MSG20240601001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240601150000||||20240601145500
PID|||83561^^^EHPAD_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^PI~242081277054936^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||PREVOST^HELOISE^^^^^L|CARPENTIER^^^^^^M|19420819|F|||15 rue Ampere^^Grenoble^^38000^FRA^H|||||||AN5217^^^EHPAD_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|GERI^112^1^EHPAD_GRENOBLE^^N^A^1|R|||10004512876^Gaudin^Dominique^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN6193^^^EHPAD_GRENOBLE&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||20240101|20240601150000|||||||||||||V
```

---

## 17. ADT^A02 - Patient transfer between units (IHE PAM.fr ADT A02 transfer)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A02 transfer profile; https://github.com/Interop-Sante/ihe.iti.pam.fr -->

```
MSH|^~\&|BL_SANTE|EHPAD_DIJON|RECEPTEUR|PFI|20240515093000||ADT^A02^ADT_A02|MSG20240515T01|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240515093000||||20240515092500
PID|||51893^^^EHPAD_DIJON&2.16.840.1.113883.2.8.3.7&ISO^PI~247055277028196^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||GIRAUD^JOSIANE^^^^^L||19470225|F|||9 rue Pasteur^^Dijon^^21000^FRA^H
PV1||I|SSR^204^2^EHPAD_DIJON^^N^A^2|R||GERI^112^1^EHPAD_DIJON^^N^A^1|10004512876^Tessier^Dominique^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN5274^^^EHPAD_DIJON&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 18. ADT^A08 - Patient information update (IHE PAM.fr ADT A08)

<!-- Source: https://www.interopsante.org/publications - IHE PAM.fr v2.11, ADT A08 update profile; https://fr.community.intersystems.com/post/contenu-du-message-hl7-adt-et-exemple-du-message-adta04 -->

```
MSH|^~\&|BL_SANTE|EHPAD_RENNES|RECEPTEUR|PFI|20240610140000||ADT^A08^ADT_A01|MSG20240610001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240610140000
PID|||96418^^^EHPAD_RENNES&2.16.840.1.113883.2.8.3.7&ISO^PI~151023577067284^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||CARPENTIER^IGOR^^^^^L|CARPENTIER^^^^^^M|19510228|M|||33 rue de Brest^^Rennes^^35000^FRA^H||^PRN^PH^^^02^98476123|||||||AN7345^^^EHPAD_RENNES&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|GERI^301^1^EHPAD_RENNES^^N^A^1|||10008643217^Maillard^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS||||||||||||||VN7481^^^EHPAD_RENNES&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 19. ORU^R01 - Wound care photo embedded as JPEG image (HL7 OBX ED image format, BL.Soins wound tracking)

<!-- Source: https://hl7.eu/refactored/segOBX.html - HL7 OBX ED data type for embedded images; https://stackoverflow.com/questions/20219223/extract-images-from-hl7-files - OBX image embedding pattern; https://www.berger-levrault.com/fr/produit/bl-soins/ - BL.Soins wound tracking feature -->

```
MSH|^~\&|BL_SANTE|EHPAD_LYON|GESTIONNAIRE|PFI|20240625090000||ORU^R01^ORU_R01|MSG20240625IMG01|P|2.5|||||FRA|UNICODE UTF-8
PID|||175063877034528^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||NAVARRO^GERARD^^^^^L||19620328|M|||14 avenue Gambetta^^Paris^^75020^FRA^H
ORC|NW
OBR|1||WOUND-2024-001|72170-4^Photographic image^LN|||20240625090000
OBX|1|ED|72170-4^Photographic image^LN|1|BL_SANTE^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SFhSRTQ3N0BTZH/aAAwDAQACEQMRAD8A+f6KKKACiiigAooooAKKKKACiiigAooooA//2Q==||||||F|
OBX|2|ST|72170-4^Photographic image^LN|1.1|Wound measurement: 3.2cm x 2.1cm, granulation tissue present||||||F|
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```

---

## 20. ORU^R01 - Dermatology consultation with embedded PNG image (HL7 OBX ED image format)

<!-- Source: https://hl7.eu/refactored/segOBX.html - HL7 OBX ED data type; https://stackoverflow.com/questions/20219223/extract-images-from-hl7-files - OBX image embedding; https://www.berger-levrault.com/fr/produit/expert-sante/ - Expert Sante DPI supports HL7 ORU -->

```
MSH|^~\&|BL_SANTE|EHPAD_BORDEAUX|GESTIONNAIRE|PFI|20240701113000||ORU^R01^ORU_R01|MSG20240701IMG02|P|2.5|||||FRA|UNICODE UTF-8
PID|||242081277054936^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||PREVOST^HELOISE^^^^^L|CARPENTIER^^^^^^M|19420819|F|||15 rue Ampere^^Grenoble^^38000^FRA^H
ORC|NW
OBR|1||DERM-2024-001|72170-4^Photographic image^LN|||20240701113000|||||||10004512876^Gaudin^Dominique^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
OBX|1|ED|72170-4^Photographic image^LN|1|BL_SANTE^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAWISURBVGiB7ZprbBRVFMd/M7PbbbdLu7SlpaUPKAVKKRQoIIgIKD4QNSoajYkmxvhBE2P84CNGP2jiI0aNGn0k+kGNxgckGkVFxQcqikIVBOVRoaXQQlu6222X7s7OeObezmx3Z7e7s8WE/JPNzD33njn/c+65Z+4sOj09PQYOQPE/e+A/B0dEYg4cEYk5cEQk5sARkZgDR0RiDhwRiTlwRCTmwBGRmANHRGIOHBGJOXBEJObAEZGYA0dEYg4cEYk5+BcSVbKQjSf3DQAAAABJRU5ErkJggg==||||||F|
OBX|2|ST|72170-4^Photographic image^LN|1.1|Skin lesion left forearm: 1.5cm diameter, irregular borders, scheduled for biopsy||||||F|
PRT||UC||SB^Send by^participation|10004512876^Gaudin^Dominique^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||EHPAD_BORDEAUX^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^380012345
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```
