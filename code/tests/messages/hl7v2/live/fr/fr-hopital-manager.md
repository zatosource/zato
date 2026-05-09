# Hopital Manager (Softway Medical) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission (SIGEMS/ENOVACOM, French hospital)

```
MSH|^~\&|SIGEMS|SIGEMS|ENOVACOM|ENOVACOM|20151125123110.703+0100||ADT^A01^ADT_A01|54741010000051070000|P|2.5|||||FRA|8859/1
EVN||20151125123110||A01||20151125123007
PID|||72439^^^SIGEMS^PI||SIMON^JOSETTE^^^^^D~LEFEBVRE^JOSETTE^^^^^L||19280814|F|||7 RUE DES ACACIAS^^RENNES^^35000^^H~^^^^^^SA~^^^^^^O~^^PLOEMEUR^^^^BR||^PRN^PH^^^^^^^^^0299471823~^PRN^CP^^^^^^^^^0647891234~^NET^Internet^NON|||M||1638471^^^SIGEMS^AN|||||PLOEMEUR|||1||||N||VIDE
PD1||||||||||||N
ROL||UC|ODRP|10293847561^HARDY^RENE^^^^^^ASIP-SANTE-PS&1.2.250.2.72.4.1.1&ISO^L^^^LLAMA~RENE01^RENE^LUC^^^^^^SIGEMS^L^^^EI|||||||28 RUE GAMBETTA^^RENNES^^35000^^O
NK1|1|MME CARPENTIER^LOUISETTE|OTH^AUTRE||^PRN^CP^^^^^^^^^0612349876||C^Personne à contacter|20151125
PV1||I|CH01^213^213^330780000||PA72101^^^SIGEMS^AN^^20151027||20003345781^BOULANGER^ANTOINE^^^^^^ASIP-SANTE-PS&1.1.300.1.71.4.2.1&ISO^L^^^RPPS~441253000^PREVOST^PAUL^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^ADELI~TISS01^PREVOST^PAUL^^^^^^SIGEMS^L^^^EI|||181||||80|||||1638471^^^SIGEMS^AN^^20151125||03|Y||||||||||||||80||||||||20151125170000|||||||A
PV2|||||||SM|20151125170000|201
```

---

## 2. ADT^A04 - Registration (IHE France PAM, Gazelle)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-61724^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||LAURENT^Olivier^^^^^L|GARCIA^^^^^^M|19920317084200|M|||^^^^^FRA|||||||AN1823^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN3891^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV4371^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N||Urgences^^^^^^UF^^^8782|Psychiatrie adulte^^^^^^UF^^^6277|S^Changement de responsabilité de soins uniquement
ZFA||||N||N|N
ZFP|4|12
ZFV|140024886^20210511120000|||||||||8
ZFM|7||5
ZFD|||N
```

---

## 3. ADT^A04 - Registration (IHE PAM International, Gazelle)

```
MSH|^~\&|PAMSimulator|IHE|Gazelle|IHE_Intl|20210427122641||ADT^A04^ADT_A01|20210427122641|P|2.5||||||UNICODE UTF-8
EVN||20210427122641||||20210427122641
PID|||DDS-61907^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||GARCIA^Thierry^^^^^L|MARTINEZ^^^^^^M|20080623181033|M|||^^^^^ESP|||||||AN1547^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||R||L|||20100556832^NAVARRO^Francois|20003997412^GUERIN^Nathalie|||||||||20004228651^BENOIT^Olivier||VN2294^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
ZBE|MOV3209^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210427122641||INSERT|N
```

---

## 4. ADT^A31 - Patient update (IHE France ITI-30, Gazelle)

```
MSH|^~\&|MB|MB|PatientManager|PAM_FR|20230602213228||ADT^A31^ADT_A05|5|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230602213228
PID|1||a7c42e3f-9b1d-4f87-a632-e81d5a7f29c4^^^&&M^PI||IHE-FR PAM^^^^^^D^A~BMRQWVKZXJP^QKLNDZHFTYW^^^^^L^A||20170811|U|||_UPDATED^^^^^^H|||||||||||||||||||N||PROV|20230602213228
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 5. ADT^A31 - Patient update (IHE France ITI-30, Gazelle)

```
MSH|^~\&|MB|MB|PatientManager|PAM_FR|20230706113531||ADT^A31^ADT_A05|5|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20230706113531
PID|1||d4f8a21b-7e6c-49d3-8c15-b3a6e0f47d92^^^&&M^PI||IHE-FR PAM^^^^^^D^A~XHWFKQTRNVC^PJYMBLGZDKS^^^^^L^A||19880504|U|||_UPDATED^^^^^^H|||||||||||||||||||N||PROV|20230706113531
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 6. ADT^A31 - Patient update with INS-NIR (IHE France ITI-30, Gazelle)

```
MSH|^~\&|MB|MB|PatientManager|PAM_FR|20221117041746||ADT^A31^ADT_A05|2|D|2.5^FRA^2.10||||||UNICODE UTF-8|FR
EVN||20221117041746
PID|1||b8e6d41a-c253-4a0f-9e17-f642c8b31d0e^^^275046812045913&&M^PI||IHE-FR PAM^^^^M.^^D^A~Vqlfxwkmbnr^TYHZGJCWPEM^^^M.^^L^A||19680422|U|||_UPDATED^^^^^^H|||||||||||||||||||N||PROV|20221117041746
PD1||U||||||||||N
PV1|1|N
ZFD|||N|N|SM
```

---

## 7. ADT^A28 - Patient creation with INS-NIR (IHE France ITI-30, Gazelle)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_F|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||268057391042815^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||DAVID^RAYMOND^CHRISTIAN^^^^L||19990423|M|||8 rue de la Paix^^Lyon^^69005^FRA^H~^^^^^^BDL|||||||AN1672^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 8. ADT^A05 - Pre-admission with INS and full French segments (IHE France ITI-31, Gazelle)

```
MSH|^~\&|PatientManager|PAM_FR|Cortex-Care|Cortex-Care|20231107113004||ADT^A05^ADT_A05|20231107113004|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231107113004||||20231107113004
PID|||14392^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~207219661104826^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.10&ISO^INS~207219661104826^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS||FLEURY^Madeleine^MADELEINE^^^^L|SANCHEZ^^^^^^L|20051228|F|||Rue de la Victoire^^Strasbourg^^67000^FRA^H~^^Versailles^^78000^FRA^BDL^BDL^78200|||||||AN2814^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I||U|VN4178^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||35001274630^PREVOST^Alain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1 I&ISO^D^^^ADELI|||||||||||VN4178^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
PV2||||||||20231107113000
ZBE|MOV6315^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231107113004||INSERT|N||Pédiatrie^^^^^^UF^^^4044|Ophtalmomogie^^^^^^UF^^^6275|HMS^Changement conjoint des trois responsabilités.
ZFA|INEXISTANT|||N||N|N
ZFP|1|23
ZFM|8
ZFD|||N|N
```

---

## 9. ADT^A01 - Admission with INS (IHE France/SEGUR, Gazelle)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_FR|20240214100721||ADT^A01^ADT_A01|20240214100721|P|2.5||||||UNICODE UTF-8
EVN||20240214100721||||20210906164312
PID|||13284^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~293158921704632^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MARTINEZ^Paulette^^^^^L|NGUYEN^^^^^^M|19910715|F|||14 rue des Lilas^^NANTES^^44000^FRA^H|||||||AN1839^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||O||L|||20004367291^HARDY^Denis|20004482156^BOULANGER^Margaux|||||||||20003849127^NAVARRO^Yves||VN3472^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 10. ADT^Z99 - French extension admission (IHE France PAM, Gazelle)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210225112019||ADT^Z99^ADT_A01|20210225112019|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210225112019||||20210225111437
PID|||DDS-62045^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||SANCHEZ^Jeannine^^^^^L|NGUYEN^^^^^^M|20180912000000|F|||^^^^^FRA|||||||AN1617^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||I|||||||||||||||||VN2183^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210226120000|||||||V
ZBE|MOV3201^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210225111437||UPDATE|N|A05
ZFA||||N||N|N
ZFD|||N
```

---

## 11. ORU^R01 - Biology report CDA transmission (ANS CI-SIS, OBX extracts)

```
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246037433000291@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
OBX|2|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F|
OBX|3|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|CE|ACK_LECTURE^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|13|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 12. ORU^R01 - Radiology imaging report CDA with masking (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246037433000291@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
NTE|1|||FIN|
OBX|10|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F|
```

---

## 13. ORU^R01 - Radiology imaging report deletion (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 14. ORU^R01 - Radiology imaging report replacement (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246037433000291@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 15. MDM^T02 - Initial medical imaging report CDA (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246037433000291@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 16. MDM^T04 - Document deletion notification (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 17. MDM^T10 - Document replacement (ANS CI-SIS)

```
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|90148273651^GUERIN^Bernard^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|20198437265^BENOIT^Thierry^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^thierry.benoit@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^246037433000291@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CWE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CWE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CWE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CWE|DESTDMP^Destinataire DMP||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CWE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CWE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F|
```

---

## 18. ACK^A04 - Acknowledgment (IHE France PAM, Gazelle)

```
MSH|^~\&|PatientManager|PAM_FR|Gazelle|PAM_FR|20210519120507||ACK^A04^ACK|20210519120507|P|2.5^FRA^2.9||||||UNICODE UTF-8
MSA|AA|20210519120506
```

---

## 19. ORU^R01 - Ultrasound report with two embedded JPEG images (SonoSite SWS)

```
MSH|^~\&|SWSIMAGESRVR|SONOSITE_ENG|MIRTH|SONOSITE_ENG|20100719133858.504||ORU^R01^ORU_R01|1279571938021|P|2.6||||||UNICODE UTF-8
PID|1||SWS-B7429D1A||NGUYEN^JEANNINE^BERNARD||19720318|F
OBR|1|788824-217^georges|00298453^SWS_FILLERUP|077777-TCD^077777-TCD^DEFAULT_RSCSN|||20090923155556|||||||||^HARDY|||||||||F|||||||&BOULANGER&Christophe&&&&D.O.
OBX|1|TX|Title^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Report Title: Cardiac||||||F
OBX|2|TX|PatientName^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Patient Name: NGUYEN, JEANNINE BERNARD,||||||F
OBX|3|TX|PatientID^1.2.840.114340.3.8251016058117.2.20090923.155556.44||ID: SWS-B7429D1A||||||F
OBX|4|TX|PatientDOB^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Date of Birth: 18 Mar, 1972||||||F
OBX|5|TX|PatientIndications^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Indications: These are indications entered in the patient form||||||F
OBX|6|TX|PatientGender^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Gender: female||||||F
OBX|7|TX|Accession^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Accession: 00298453||||||F
OBX|8|TX|ReferringDr^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Referring Dr.: HARDY||||||F
OBX|9|TX|ReadingDr^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Reading Dr.: BOULANGER||||||F
OBX|10|TX|WorksheetIndications^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Indications: Patient presents with shortness of breath, trauma, hypotension, hypoxia. Free text indications entered in cardiac worksheet form||||||F
OBX|11|TX|ProcedureDetails^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Procedure Details: A subcostal view of the heart was obtained and demonstrated no evidence of pericardial effusion. A parasternal view of the heart was obtained and demonstrated no evidence of pericardial effusion. An apical 4-chamber view of the heart was obtained and demonstrated no evidence of pericardial effusion.||||||F
OBX|12|TX|Conclusions^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Conclusions: This exam was: positive for cardiac activity, negative for tamponade physiology, negative for a pericardial effusion in the subcostal view, negative for a pericardial effusion in the parasternal view, negative for a pericardial effusion in the apical 4-chamber view.||||||F
OBX|13|TX|Comments^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Comments: Comments entered in Additional Notes in the Cardiac Worksheet During the exam, the following anatomical areas were not visualized due to example reason: example area.||||||F
OBX|14|TX|Signature^1.2.840.114340.3.8251016058117.2.20090923.155556.44||Electronic Signature: This report was electronically signed by Boulanger, Christophe, D.O. at 2010-Jul-19, 01:37 PM. Findings and interpretation were completed by Prevost, Nicolas, MD at 2010-Jul-19, 01:36 PM.||||||F
OBX|15|ED|AttachedImage^1.2.840.114340.3.8251016058117.3.20090923.160940.349.4||fred^image^image/jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AKwA//9k=||||||F
OBX|16|ED|AttachedImage^1.2.840.114340.3.8251016058117.3.20090923.161000.350.4||fred^image^image/jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AKwA//9k=||||||F
```

---

## 20. ORU^R01 - Ultrasound report with embedded TIFF image (HL7 OBX ED standard example)

```
OBX|1|ED|11490-0^^LN||^IM^TIFF^Base64^SUkqANQAAABXQU5HIFRJRkYgAQC8AAAAVGl0bGU6AEF1dGhvcjoAU3ViamVjdDoAS2V5d29yZHM6AENvbW1lbnRzOgAAAFQAaQB0AGwAZQA6AAAAAABBAHUAdABoAG8AcgA6AAAAAABTAHUAYgBqAGUAYwB0ADoAAAAAAEsAZQB5AHcAbwByAGQAcwA6AAAAAABDAG8AbQBtAGUAbgB0AHMAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAP4ABAABAAAAAAAAAAAB||||||F
```

---
