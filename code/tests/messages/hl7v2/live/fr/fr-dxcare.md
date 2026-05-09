# DxCare / ORBIS (Dedalus France) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission (ITI-31, PAM France)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_FR|20240214100721||ADT^A01^ADT_A01|20240214100721|P|2.5||||||UNICODE UTF-8
EVN||20240214100721||||20210906164312
PID|||10557^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~185076234567831^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||ROGER^THIERRY^^^^^L|LEFEVRE^^^^^^M|19890714|F|||23 avenue des Tilleuls^^MARSEILLE^^13006^FRA^H|||||||AN1507^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||O||L|||10003244273^Dupuis^Monique|10003246534^Riviere^Andre|||||||||10003217402^Gautier^Sylvie||VN2659^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 2. ADT^Z99^ADT_A01 - Admission with French extensions (PAM.fr, Softway Medical)

```
MSH|^~\&|HM|Finistere|PAM_FR|PatientManager|20211018171107||ADT^Z99^ADT_A01|203618103876|P|2.5^FRA^2.9||||AL|FRA|8859/1|FR
EVN||20211018171045|||comm^Communication^^^^^^^HMLyo^D^^^EI|20211018170100
PID|1||202110181701^^^HMLyo^PI||BARBIER^PATRICE^^^MR^^L~BARBIER^PATRICE^^^MR^^S||19761015000000|M|||8 RUE LAMARTINE^^RENNES^^35000^100^H~^^RENNES^^35000^^BDL||^PRN^PH^^^^^^06.47.28.91.53^^^0647289153~^ORN^PH^^^^^^02.98.34.56.12^^^0298345612~^NET^Internet^pbarbier@orange.fr|^WPN^PH^^^^^^02.98.71.43.06^^^0298714306||||2021101817019^^^HMLyo^AN|||||35000 RENNES||1|250^Oman||||N||PROV
PD1||||||||||||Y
PV1|1|I|CHIR1A^^^290340000&290340000&N||||LECONTE^LECONTE^Genevieve^^^^^^HMLyo^D^^^EI~136847296^LECONTE^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^ADELI~10003791976^LECONTE^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||||||||I|||2021101817019^^^HMLyo^VN||03|Y||||||||||||||||||||||20211018170100|||||||V
PV2||||||||||||Test
ZBE|203608656011^HMLyo~2021101817011^AGFA|20211018170100||UPDATE|N|A01|Chirurgie 1er etage Secteur A^^^^^290340000&290340000&N^UF^^^CHIR1A|Chirurgie 1er etage Secteur A^^^^^290340000&290340000&N^UF^^^CHIR1A
ZFM|6||4
ROL|203612689980^HMLyo|UP|AT|LECONTE^LECONTE^Genevieve^^^^^^HMLyo^D^^^EI~136847296^LECONTE^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^ADELI~10003791976^LECONTE^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|20211018170100||||||SAINT-CYR^25 Rue DE BREST - RUE VANNEAU^RENNES^^35000^100^O|^NET^Internet^gleconte@softwaymedical.fr
```

---

## 3. ADT^A28^ADT_A05 - Patient identity feed with INS (ITI-30, Gazelle)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_F|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||267059812345671^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MASSON^HERVE^PATRICE^^^^L||19980503|M|||7 place du Commerce^^BORDEAUX^^33000^FRA^H~^^^^^^BDL|||||||AN1496^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 4. ADT^A28^ADT_A05 - Patient feed with multiple identifiers (INS-C, INS-NIR, INS-NIA)

```
MSH|^~\&|PatientManager|PAM_FR|PatientManager|PAM_FR|20240423154852||ADT^A28^ADT_A05|20240423154852|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240423154852
PID|||0093876492823371705143^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-55106^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI~11164^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~275031234274436^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.10&ISO^INS~275031234274436^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS||CHEVALIER^GENEVIEVE^^^^^L|ROCHE^^^^^^L|19750312|F|||Rue de Glasgow^^STRASBOURG^^67000^FRA^H~^^STRASBOURG^^67000^FRA^BDL^^67482|||||G||AN2521^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||PROV
PV1||N
ZFD|||N|N
```

---

## 5. ADT^A31^ADT_A05 - Patient update (ITI-30)

```
MSH|^~\&|MB|MB|PatientManager|PAM_FR|20230602213228||ADT^A31^ADT_A05|5|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230602213228
PID|1||5655ae1f-3d1e-4de6-b177-d57ea581c4f3^^^&&M^PI||IHE-FR PAM^^^^^^D^A~ROCHE^YVES^^^^^L^A||20170814|U|||_UPDATED^^^^^^H|||||||||||||||||||N||PROV|20230602213228
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 6. ADT^Z99^ADT_A01 - Pre-admission (A05) with Gazelle PAM_FR

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210225112019||ADT^Z99^ADT_A01|20210225112019|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210225112019||||20210225111437
PID|||DDS-53872^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||LEFEVRE^SYLVIE^^^^^L|COLIN^^^^^^M|20180217000000|F|||^^^^^FRA|||||||AN1390^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||I|||||||||||||||||VN1762^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210226120000|||||||V
ZBE|MOV3201^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210225111437||UPDATE|N|A05
ZFA||||N||N|N
ZFD|||N
```

---

## 7. ADT^A31^ADT_A05 - Patient update (July 2023)

```
MSH|^~\&|MB|MB|PatientManager|PAM_FR|20230706113531||ADT^A31^ADT_A05|5|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230706113531
PID|1||81f6df3a-c3bf-45a8-b9dc-9dab702e78e7^^^&&M^PI||IHE-FR PAM^^^^^^D^A~LEMOINE^MARTINE^^^^^L^A||19870412|U|||_UPDATED^^^^^^H|||||||||||||||||||N||PROV|20230706113531
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 8. ADT^A04 - Patient registration

```
MSH|^~\&|EPIC|EPICADT|SMS|SMSADT|202211031408|CHARRIS|ADT^A04|1817457|D|2.5|
EVN||202211030800||||202211030800
PID||0597683^^^2^ID 1|562847||BRUN^ANDRE^^^^|BRUN^ANDRE^^^^|19520918|M||B|17 RUE DE LA PAIX^^TOULOUSE^31^31000^FRA||(05)61.45.78.23|||M|NON|400007819~2238197|
NK1||BRUN^CLAUDINE^^^^|SPO||(05)61.45.78.24||EC|||||||||||||||||||||||||||
PV1||O|168 ~219~C~PMA^^^^^^^^^||||277^BONNET^MARTINE^^^^|||||||||| ||2688684|||||||||||||||||||||||||202211031408||||||002376853
```

---

## 9. ADT^A01 - French hospital admission (numlor.fr)

```
MSH|^~\&||SITE|||||ADT^A01|321|P|2.3|||NE
PID|||743219||PONS^MONIQUE||19810607|M|||4 RUE VICTOR HUGO^^^^56100LORIENT||^^^^^^0607534182|||||
PV1|1|O|||||71^BOUCHARD^HERVE||||||||||||12376|||||||||||||||||||||||||20200410160227||||||
OBR|1||12376|cbc^CBC|R||20201410160227|||22^BOUCHARD^HERVE|||Fasting: No|202004101625|
OBX|1|NM|0135-4^TotalProtein||7.3|gm/dl|5.9-8.4||||F
```

---

## 10. ORU^R01 - Biology report CDA transmission (CI-SIS, initial)

```
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^Riviere^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147037433100207@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
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
OBX|13|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsSHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 11. ORU^R01 - Radiology report CDA with masking (CI-SIS, Exemple 1)

```
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147037433100207@patient.mssante.fr
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
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==|||||F|
```

---

## 12. ORU^R01 - Document deletion request (CI-SIS, OBX-11=D)

```
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10234567890^Riviere^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
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
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsSHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 13. ORU^R01 - Document replacement (CI-SIS, OBX-11=C)

```
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^Riviere^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^147037433100207@patient.mssante.fr
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
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsSHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 14. MDM^T02 - Initial radiology report (CI-SIS, MDM format)

```
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^Riviere^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147037433100207@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
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
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsSHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 15. MDM^T10 - Document replacement (CI-SIS, MDM format)

```
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80234567891^Dupuis^Yves^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10234567890^Riviere^Genevieve^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^genevieve.riviere@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^147037433100207@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsSHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 16. ORU^R01 - Radiology order resulted (HL7 Europe Zulip)

```
MSH|^~\&|EPIC|EPIC|||20221216141251|1148|ORU^R01|487|D|2.3||
PID|1||529712^^^EPI||COLIN^MARTINE^M||20050319|F|||45 RUE DES ACACIAS^^STRASBOURG^67^67000^FR^^^|||||||||||||||||||||
PV1|||4300^^^WI HARBOR BLUFF NORTH^^^WI HARBOR BLUFF NORTH^^^^||||||||||||||||10006787555|||||||||||||||||||||||||20221201104507|||||||V
ORC|RE|548498^EPC|3334||Final||^^^20221201104513^20221201104513^R||20221216141251|1148^GAUTIER^HERVE^^^^||||(03)88.56.12.34||
OBR|1|548498^EPC|3334|73000^X-RAY CLAVICLE^EXTEAP||||||||||||859^BONNET^PATRICE^A^^^|(03)88.43.21.65||||||||Final||^^^20221201104513^20221201104513^R|||||3237^BOUCHARD^SYLVIE^^^^|
OBX|1|ST|&GDT|1|X-ray suspected Clavicle fx. The quality of the film was good.|||A|||Final|
OBX|2|ST|&IMP|1|Abnormal, Fracture Present|||A|||Final|
OBX|3|ST|&IMP|1|Left lateral; surgery required|||A|||Final|
```

---

## 17. QBP^Q22 - Patient demographics query (Gazelle)

```
MSH|^~\&|PatientManager|IHE|Gazelle|IHE_FR|20211007154256||QBP^Q22^QBP_Q21|20211007154256|P|2.5||||||UNICODE UTF-8
QPD|IHE PIX Query|Q22_20211007154256|^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI|^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO
RCP|I
```

---

## 18. ACK^A01 - Acknowledgment with error (PAM France)

```
MSH|^~\&|PatientManager|PAM_FR|PatientManager|IHE|20240214100722||ACK^A01^ACK|20240214100722|P|2.5^FRA^2.10||||||UNICODE UTF-8
MSA|AE|20240214100721
ERR||PV1^1^19^1|205|E||||This identifier is already used: VN2659\S\\S\\S\GZL_INTEROP\T\2.16.840.1.113883.2.8.3.7\T\ISO\S\VN
```

---

## 19. ORU^R01 - Embedded TIFF image in OBX (HL7 standard, ED datatype)

```
MSH|^~\&|RADIOLOGY|HOSPITAL|||20131126120000||ORU^R01|MSG00001|P|2.3|
PID|1||PAT002^^^HOSP^MR||ROGER^GENEVIEVE||19770524|F|||31 RUE DES LILAS^^NICE^^06000^FRA|
OBR|1||RAD001|71020^CHEST XRAY^CPT4|R||20131126100000|||||||||||
OBX|1|ED|11490-0^^LN||^IM^TIFF^Base64^SUkqANQAAABXQU5HIFRJRkYgAQC8AAAAVGl0bGU6AEF1dGhvcjoAU3ViamVjdDoAS2V5d29yZHM6AENvbW1lbnRzOgAAAFQAaQB0AGwAZQA6AAAAAABBAHUAdABoAG8AcgA6AAAAAABTAHUAYgBqAGUAYwB0ADoAAAAAAEsAZQB5AHcAbwByAGQAcwA6AAAAAABDAG8AbQBtAGUAbgB0AHMAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAP4ABAABAAAAAAAAAAAB|||||||F
```

---

## 20. ORU^R01 - Embedded PDF in OBX (Australian Standard AS4700.2, ED datatype)

```
MSH|^~\&|LAB|PATHOLOGY|||20150714082250+1000||ORU^R01|MSG98765|P|2.4|
PID|1||876543^^^LAB^MR||MASSON^YVES||19720208|M|||15 BOULEVARD GAMBETTA^^LYON^^69003^FRA|
OBR|1||LAB65432|26604-1^Complete Blood Count^LN|R||20150714080000|||||||||||
OBX|1|ED|PDF^Display format in PDF^AUSPDI||^application^pdf^Base64^JVBERi0xLjQNCiXT9MzhDQoxIDAgb2JqDQo8PCAvVGl0bGUgKFRlc3QgUmVwb3J0KSAvQXV0aG9yIChMYWJvcmF0b3J5KSA+Pg0KZW5kb2JqDQoyIDAgb2JqDQo8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMyAwIFIgPj4NCmVuZG9iag0KMyAwIG9iag0KPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFs0IDAgUl0gL0NvdW50IDEgPj4NCmVuZG9iag0KJSVFT0YNCg==|||||||F|||20150714082250+1000
```

---
