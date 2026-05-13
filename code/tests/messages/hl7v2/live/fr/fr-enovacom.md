# Enovacom Integration Engine (Orange) - real HL7v2 ER7 messages

## 1. ADT^A01 - patient admission (SIGEMS to Enovacom)

```
MSH|^~\&|SIGEMS|SIGEMS|ENOVACOM|ENOVACOM|20151125123110.703+0100||ADT^A01^ADT_A01|54741010000051070000|P|2.5|||||FRA|8859/1
EVN||20151125123110||A01||20151125123007
PID|||72438^^^SIGEMS^PI||BERTRAND^MARCEL^^^^^D~KOWALCZYK^MARCELIN^^^^^L||19280519|F|||7 IMPASSE DES CHARDONNERETS^^PLOUDANIEL^^29260^^H~^^^^^^SA~^^^^^^O~^^PLOUGASTEL^^^^BR||^PRN^PH^^^^^^^^^0298451177~^PRN^CP^^^^^^^^^0672983401~^NET^Internet^NON|||M||1637842^^^SIGEMS^AN|||||PLOUGASTEL|||1||||N||VIDE
PV1||I|CH01^213^213^330780000||PA72100^^^SIGEMS^AN^^20151027||10001287543^VOISIN^LOIC^^^^^^ASIP-SANTE-PS&1.1.300.1.71.4.2.1&ISO^L^^^RPPS~331298000^VOISIN^LOIC^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^ADELI~VOIS00^VOISIN^LOIC^^^^^^SIGEMS^L^^^EI|||181||||80|||||1637842^^^SIGEMS^AN^^20151125||03|Y||||||||||||||80||||||||20151125170000|||||||A
```

---

## 2. ADT^A01 - PAM.fr admission with INS-C (Gazelle platform, Cortex-Care)

```
MSH|^~\&|PatientManager|PAM_FR|Cortex-Care|Cortex-Care|20231130103019||ADT^A01^ADT_A01|20231130103019|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231130103019||||20231130103019
PID|||269081243578012^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-61842^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||PICARD^Sebastien^^^^^L|ADAM^^^^^^M|19790214|M|||12 Rue du Faubourg Saint-Antoine^^Paris^^75013^FRA^H|||||||AN3617^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I|||||||||||||||||VN4892^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV6323^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231130103019||INSERT|N
ZFA||||N||N|N
ZFD|||N|N
```

---

## 3. ADT^Z99 - PAM.fr update movement (Gazelle platform)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210225112019||ADT^Z99^ADT_A01|20210225112019|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210225112019||||20210225111437
PID|||DDS-60245^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||RENARD^Odette^^^^^L|GUILLON^^^^^^M|20190711000000|F|||^^^^^FRA|||||||AN2074^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||I|||||||||||||||||VN2483^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210226120000|||||||V
ZBE|MOV3201^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210225111437||UPDATE|N|A05
ZFA||||N||N|N
ZFD|||N
```

---

## 4. ADT^A04 - PAM.fr emergency registration with ZBE/ZFA/ZFP/ZFV/ZFM segments (Gazelle platform)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-60718^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||MENARD^Lucien^^^^^L|TANGUY^^^^^^M|19930817065200|M|||^^^^^FRA|||||||AN2189^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN3145^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV4371^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N||Urgences^^^^^^UF^^^8782|Psychiatrie adulte^^^^^^UF^^^6277|S^Changement de responsabilite de soins uniquement
ZFA||||N||N|N
ZFP|4|12
ZFV|140024886^20210511120000|||||||||8
ZFM|7||5
ZFD|||N
```

---

## 5. ACK^A01 - acknowledgement for PAM.fr admission (Gazelle platform)

```
MSH|^~\&|Cortex-Care|Cortex-Care|PatientManager|PAM_FR|20231130093020||ACK^A01^ACK|20231130093020|P|2.5^FRA^2.10
MSA|AA|20231130103019
```

---

## 6. ADT^A01 - simple admission (numlor.fr French hospital network training)

```
MSH|^~\&||SITE|||||ADT^A01|321|P|2.3|||NE
PID|||819476||ADAM^DIDIER||19761108|M|||15 RUE JEAN JAURES^^^^56100LORIENT||^^^^^^0697823514|||||
PV1|1|O|||||83^ROUX^BEATRICE||||||||||||14592|||||||||||||||||||||||||20200410160227||||||
OBR|1||14592|cbc^CBC|R||20201410160227|||34^ROUX^BEATRICE|||Fasting: No|202004101625|
OBX|1|NM|0135-4^TotalProtein||7.3|gm/dl|5.9-8.4||||F
OBX|2|NM|0033-1^Albumin||3.9|gm/dl|3.2-5.2||||F
```

---

## 7. ORU^R01 - biology report CDA transmission, initial (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|CHU_BORDEAUX|GESTIONNAIRE|PFI_CHU|20240315091200||ORU^R01^ORU_R01|MSG00001|P|2.5||||||UNICODE UTF-8
PID|||280019354821967^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-001^^^CHU_BORDEAUX&1.2.250.1.213.1.4.2&ISO^PI||BRUNET^Mireille^^^^^L||19530907|M|||45 Rue Sainte-Catherine^^Bordeaux^^33000^FRA^H
PV1||I|MED-A^101^1^CHU_BORDEAUX||||23456789012^PELLETIER^Aurelie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||BIO-2024-001^CHU_BORDEAUX|11502-2^CR d'examens biologiques^LN|||20240315091200
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 8. ORU^R01 - radiology report with masking (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|HOPITAL_A|GESTIONNAIRE|PFI_HOP|20240320143000||ORU^R01^ORU_R01|MSG00002|P|2.5||||||UNICODE UTF-8
PID|||297054C913287^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-042^^^HOPITAL_A&1.2.250.1.213.1.4.2&ISO^PI||GUILLON^Agnes^^^^^L||19680422|F|||8 Place Bellecour^^Lyon^^69002^FRA^H
PV1||I|RAD-B^202^1^HOPITAL_A||||87654321098^LAROCHE^Lucien^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||RAD-2024-042^HOPITAL_A|18748-4^CR d'imagerie medicale^LN|||20240320143000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246098745000312@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F
```

---

## 9. ORU^R01 - document deletion request (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|HOPITAL_A|GESTIONNAIRE|PFI_HOP|20240325100000||ORU^R01^ORU_R01|MSG00003|P|2.5||||||UNICODE UTF-8
PID|||297054C913287^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||GUILLON^Agnes^^^^^L||19680422|F
ORC|NW
OBR|1||RAD-2024-042^HOPITAL_A|18748-4^CR d'imagerie medicale^LN|||20240325100000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
OBX|2|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 10. ORU^R01 - document replacement (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|HOPITAL_A|GESTIONNAIRE|PFI_HOP|20240401082000||ORU^R01^ORU_R01|MSG00004|P|2.5||||||UNICODE UTF-8
PID|||297054C913287^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||GUILLON^Agnes^^^^^L||19680422|F
ORC|NW
OBR|1||RAD-2024-043^HOPITAL_A|18748-4^CR d'imagerie medicale^LN|||20240401082000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246098745000312@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 11. MDM^T02 - medical document initial transmission (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|CHU_NANTES|GESTIONNAIRE|PFI_CHU|20240410141500||MDM^T02^MDM_T02|MSG00005|P|2.6||||||UNICODE UTF-8
EVN||20240410141500
PID|||296087612345098^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-100^^^CHU_NANTES&1.2.250.1.213.1.4.2&ISO^PI||CAMUS^Romain^^^^^L||19580321|M|||14 Rue Crebillon^^Nantes^^44000^FRA^H
PV1||I|CARD^301^2^CHU_NANTES||||22334455667^PASQUIER^Sandrine^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240410141500|||||DOC-2024-100^CHU_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 12. MDM^T10 - document replacement (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|CHU_NANTES|GESTIONNAIRE|PFI_CHU|20240415093000||MDM^T10^MDM_T02|MSG00006|P|2.6||||||UNICODE UTF-8
EVN||20240415093000
PID|||296087612345098^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||CAMUS^Romain^^^^^L||19580321|M
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240415093000|||||DOC-2024-101^CHU_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246098745000312@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 13. MDM^T04 - document deletion notification (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|CHU_NANTES|GESTIONNAIRE|PFI_CHU|20240420110000||MDM^T04^MDM_T02|MSG00007|P|2.6||||||UNICODE UTF-8
EVN||20240420110000
PID|||296087612345098^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||CAMUS^Romain^^^^^L||19580321|M
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240420110000|||||DOC-2024-100^CHU_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D
PRT||UC||SB^send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 14. ORU^R01 - visibility modification with MODIF_CONF_CODE (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|CREATEUR|HOPITAL_B|GESTIONNAIRE|PFI_HOP|20240505160000||ORU^R01^ORU_R01|MSG00008|P|2.5||||||UNICODE UTF-8
PID|||280019354821967^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||BRUNET^Mireille^^^^^L||19530907|M
ORC|NW
OBR|1||IMG-2024-088^HOPITAL_B|18748-4^CR d'imagerie medicale^LN|||20240505160000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|104567890123^DELORME^Didier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^246098745000312@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^didier.delorme@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 15. ADT^A04 - outpatient registration (fr.community.intersystems.com French HL7 guide)

```
MSH|^~\&|EPIC|EPICADT|SMS|SMSADT|202211031408|CHARRIS|ADT^A04|1817457|D|2.5
EVN||202211030800||||202211030800
PID||0597312^^^2^ID 1|518934||FABRE^ROMAIN^^^^|TANGUY^ROMAIN^^^^|19510617|M||B|23 RUE DES OLIVIERS^^MONTPELLIER^34^34000^FRA||(467)312-8947|||M|NON|400007891~2234517|
NK1||FABRE^DANIELLE^^^^|SPO||(467)312-8947||EC|||||||||||||||||||||||||||
PV1||O|168 ~219~C~PMA^^^^^^^^^||||312^PELLETIER^CLAIRE^^^^|||||||||| ||3791245|||||||||||||||||||||||||202211031408||||||002498176
```

---

## 16. SIU^S12 - appointment scheduling (IHE SIU profile, French context)

```
MSH|^~\&|ENOVACOM|CH_MARSEILLE|AGENDA|PLANNING_BLOC|20240610091500||SIU^S12^SIU_S12|SIU00001|P|2.5|||||FRA|8859/1
SCH|APT-20240610-001^ENOVACOM|APT-20240610-001^AGENDA||||RDV^Rendez-vous^HL70276|ROUTINE^Routine^HL70277|30^MIN|||||^BRUNET^Mireille|^PRN^PH^^^^^^^^^0491276834|^^BLOC_A^^13008^FRA|105678901234^PELLETIER^Aurelie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
PID|||PAT-2024-610^^^CH_MARSEILLE^PI||TANGUY^Sebastien^^^^^L||19830729|M|||38 Boulevard de la Canebiere^^Marseille^^13008^FRA^H
PV1||O
RGS|1
AIS|1||CHIR-ORTHO^Chirurgie orthopedique^LOCAL|||20240610091500|30^MIN
AIP|1||105678901234^PELLETIER^Aurelie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
AIL|1||BLOC_A^SALLE_3^CH_MARSEILLE
```

---

## 17. ORM^O01 - laboratory order (French hospital context via Enovacom EAI)

```
MSH|^~\&|DPI_HOPITAL|CH_TOULOUSE|LAB_SIL|LABO_BIOCHIMIE|20240715080000||ORM^O01^ORM_O01|ORM20240715001|P|2.5|||||FRA|8859/1
PID|||PAT-84623^^^CH_TOULOUSE^PI||PICARD^Yvette^^^^^L||19691103|F|||22 Rue de Metz^^Toulouse^^31000^FRA^H
PV1||I|MED-C^405^1^CH_TOULOUSE||||33445566778^ROUX^Mathieu^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW|ORD-2024-789^DPI_HOPITAL||GRP-001^DPI_HOPITAL|||||20240715080000|||33445566778^ROUX^Mathieu^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
OBR|1|ORD-2024-789^DPI_HOPITAL||58410-2^NFS^LN|||20240715080000|||||||||33445566778^ROUX^Mathieu^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
DG1|1||R50.9^Fievre sans precision^I10
NTE|1||Patient febrile depuis 48h, recherche infection
```

---

## 18. ORU^R01 - lab results with numeric observations (numlor.fr + French lab context)

```
MSH|^~\&|SIL_BIOCHIMIE|LABO_CH|DPI_HOPITAL|CH_LORIENT|20240801143000||ORU^R01^ORU_R01|ORU20240801001|P|2.5|||||FRA|8859/1
PID|||819476^^^CH_LORIENT^PI||ADAM^DIDIER^^^^^L||19761108|M|||15 RUE JEAN JAURES^^LORIENT^^56100^FRA^H||^PRN^CP^^^^^^^^^0697823514
PV1||O|||||83^ROUX^BEATRICE^^^^^^CH_LORIENT^L
ORC|RE
OBR|1||BIO-14592^LABO_CH|24323-8^Bilan hepatique complet^LN|R||20240801140000|||83^ROUX^BEATRICE
OBX|1|NM|0135-4^Total Protein^LN||7.3|g/dL|5.9-8.4||||F
OBX|2|NM|0033-1^Albumin^LN||3.9|g/dL|3.2-5.2||||F
OBX|3|NM|1742-6^ALAT^LN||28|U/L|7-56||||F
OBX|4|NM|1920-8^ASAT^LN||22|U/L|10-40||||F
OBX|5|NM|1975-2^Bilirubine totale^LN||0.8|mg/dL|0.1-1.2||||F
OBX|6|NM|6768-6^Phosphatases alcalines^LN||65|U/L|44-147||||F
```

---

## 19. ORU^R01 - radiology report with embedded JPEG image (ANS CI-SIS context, base64 encapsulated image)

```
MSH|^~\&|PACS_RADIO|CH_BORDEAUX|GESTIONNAIRE|PFI_CHU|20240901102000||ORU^R01^ORU_R01|ORU-IMG-001|P|2.5||||||UNICODE UTF-8
PID|||280019354821967^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-201^^^CH_BORDEAUX^PI||BRUNET^Mireille^^^^^L||19530907|M|||45 Rue Sainte-Catherine^^Bordeaux^^33000^FRA^H
PV1||I|RAD-A^101^1^CH_BORDEAUX||||23456789012^PELLETIER^Aurelie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||RAD-2024-201^CH_BORDEAUX|18748-4^CR d'imagerie medicale^LN|||20240901102000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
OBX|2|ED|IMG-DICOM^Image radiologique JPEG^LOCAL||^image^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBU/9j/4QCcRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAYgAAABsBBQABAAAAagAAABwBAwABAAAAAQAAADsBAgADAAAAAAAAAGmHBAABAAAAbgAAAAAAAAAIAAgACAAKAAAAZAAAAA==||||||F
PRT||UC||SB^Send by^participation|803456789012^LAROCHE^Philippe^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 20. ORU^R01 - pathology report with embedded PNG image (ANS CI-SIS context, base64 encapsulated image)

```
MSH|^~\&|SGL_ANAPATH|CHU_LYON|GESTIONNAIRE|PFI_CHU|20240920150000||ORU^R01^ORU_R01|ORU-IMG-002|P|2.5||||||UNICODE UTF-8
PID|||297054C913287^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-305^^^CHU_LYON^PI||GUILLON^Agnes^^^^^L||19680422|F|||8 Place Bellecour^^Lyon^^69002^FRA^H
PV1||I|ANAPATH^201^1^CHU_LYON||||66778899001^PASQUIER^Guillaume^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||ANAPATH-2024-305^CHU_LYON|60567-5^CR d'anatomie et de cytologie pathologiques^LN|||20240920150000
OBX|1|ED|60567-5^CR d'anatomie et de cytologie pathologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
OBX|2|ED|IMG-HISTO^Image histologie coupe HE^LOCAL||^image^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==||||||F
OBX|3|ED|IMG-MACRO^Photo macroscopique piece operatoire^LOCAL||^image^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB/9j/4QAiRXhpZgAASUkqAAgAAAABADIBAgAUAAAAGgAAAAAAAAA=||||||F
PRT||UC||SB^Send by^participation|66778899001^PASQUIER^Guillaume^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||CHU_LYON^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^690783154
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
