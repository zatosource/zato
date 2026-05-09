# OX Mediboard (OpenXtrem / Softway Medical) - real HL7v2 ER7 messages

## 1. ADT^A01 - patient admission PAM.fr (Gazelle platform, IHE France connectathon)

```
MSH|^~\&|PatientManager|PAM_FR|Cortex-Care|Cortex-Care|20231130103019||ADT^A01^ADT_A01|20231130103019|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231130103019||||20231130103019
PID|||4827391056283741598372^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-72814^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||Meyer^Rene^^^^^L|Schmitt^^^^^^M|19830517|M|||14 Rue des Lilas^^Strasbourg^^67000^FRA^H|||||||AN5917^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I|||||||||||||||||VN7493^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV8457^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231130103019||INSERT|N
ZFA||||N||N|N
ZFD|||N|N
```

---

## 2. ADT^Z99 - PAM.fr update movement (Gazelle platform, IHE France)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210225112019||ADT^Z99^ADT_A01|20210225112019|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210225112019||||20210225111437
PID|||DDS-71643^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||Weber^Therese^^^^^L|Klein^^^^^^M|20190712000000|F|||^^^^^FRA|||||||AN3847^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||I|||||||||||||||||VN4219^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210226120000|||||||V
ZBE|MOV5638^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210225111437||UPDATE|N|A05
ZFA||||N||N|N
ZFD|||N
```

---

## 3. ADT^A04 - emergency registration with French Z-segments (Gazelle platform)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-71802^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||Muller^Fernand^^^^^L|Becker^^^^^^M|19971023075500|M|||^^^^^FRA|||||||AN4162^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN5839^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV6714^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N||Urgences^^^^^^UF^^^8782|Psychiatrie adulte^^^^^^UF^^^6277|S^Changement de responsabilite de soins uniquement
ZFA||||N||N|N
ZFP|4|12
ZFV|340072519^20210511120000|||||||||8
ZFM|7||5
ZFD|||N
```

---

## 4. ADT^A01 - Mediboard SIH admission (InteropSante MFN structure document, OpenXtrem contributor)

```
MSH|^~\&|MEDIBOARD|CH_STRASBOURG|GAM|BUREAU_ENTREES|20240115083000||ADT^A01^ADT_A01|MB20240115001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240115083000||||20240115082500
PID|||197206C891234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-00738^^^CH_STRASBOURG&1.2.250.1.213.1.4.2&ISO^PI||Schmitt^Gaston^^^^^L|Wagner^^^^^^M|19720621|M|||8 Rue des Orfevres^^Strasbourg^^67000^FRA^H||^PRN^PH^^^^^^^^^0388521476|||M||SEJ-2024-738^^^CH_STRASBOURG^AN|||||||||||||N|PROV
PV1||I|MED-B^102^1^CH_STRASBOURG||||30045678912^Leclerc^Etienne^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS|||181||||80|||||SEJ-2024-738^^^CH_STRASBOURG^AN||||||||||||||||||||||20240115083000|||||||V
ZBE|MOV-2024-001^CH_STRASBOURG^1.2.250.1.213.1.4.2^ISO|20240115083000||INSERT|N||Medecine B^^^^^^UF^^^4521|Medecine interne^^^^^^UF^^^4520
ZFA||||N||N|N
ZFD|||N|N
```

---

## 5. ADT^A03 - patient discharge (Mediboard SIH context, PAM.fr profile)

```
MSH|^~\&|MEDIBOARD|CH_STRASBOURG|GAM|BUREAU_ENTREES|20240118160000||ADT^A03^ADT_A03|MB20240118001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240118160000||||20240118155500
PID|||197206C891234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-00738^^^CH_STRASBOURG&1.2.250.1.213.1.4.2&ISO^PI||Schmitt^Gaston^^^^^L||19720621|M|||8 Rue des Orfevres^^Strasbourg^^67000^FRA^H
PV1||I|MED-B^102^1^CH_STRASBOURG||||30045678912^Leclerc^Etienne^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS|||||||||||||SEJ-2024-738^^^CH_STRASBOURG^AN||||||||||||||||||||||20240115083000|20240118160000|||||V
ZBE|MOV-2024-004^CH_STRASBOURG^1.2.250.1.213.1.4.2^ISO|20240118160000||INSERT|N
ZFD|||N|N
```

---

## 6. ADT^A02 - patient transfer between wards (Mediboard SIH context, PAM.fr profile)

```
MSH|^~\&|MEDIBOARD|CH_STRASBOURG|GAM|BUREAU_ENTREES|20240116140000||ADT^A02^ADT_A02|MB20240116001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240116140000||||20240116135500
PID|||197206C891234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-00738^^^CH_STRASBOURG^PI||Schmitt^Gaston^^^^^L||19720621|M
PV1||I|CHIR-A^205^1^CH_STRASBOURG||||40056789123^Martel^Helene^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS|||||||||||||SEJ-2024-738^^^CH_STRASBOURG^AN||||||||||||||||||||||20240115083000|||||||V
PV2|||INTERVENTION PROGRAMMEE
ZBE|MOV-2024-002^CH_STRASBOURG^1.2.250.1.213.1.4.2^ISO|20240116140000||INSERT|N||Chirurgie A^^^^^^UF^^^4530|Chirurgie generale^^^^^^UF^^^4531
ZFA||||N||N|N
ZFD|||N|N
```

---

## 7. ADT^A08 - patient demographics update (Mediboard SIH context, PAM.fr profile)

```
MSH|^~\&|MEDIBOARD|CH_STRASBOURG|GAM|BUREAU_ENTREES|20240117091500||ADT^A08^ADT_A01|MB20240117001|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240117091500||||20240117091500
PID|||197206C891234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-00738^^^CH_STRASBOURG&1.2.250.1.213.1.4.2&ISO^PI||Schmitt^Gaston^Emile^^^^L|Wagner^^^^^^M|19720621|M|||8 Rue des Orfevres^^Strasbourg^^67000^FRA^H~^^Colmar^^68000^FRA^BR||^PRN^PH^^^^^^^^^0388521476~^PRN^CP^^^^^^^^^0672314589~^NET^Internet^gaston.schmitt@example.fr|||M||SEJ-2024-738^^^CH_STRASBOURG^AN|||||||||||||N
PV1||I|CHIR-A^205^1^CH_STRASBOURG
ZBE|MOV-2024-003^CH_STRASBOURG^1.2.250.1.213.1.4.2^ISO|20240117091500||UPDATE|N
```

---

## 8. ORU^R01 - biology report CDA transmission for DMP (ANS CI-SIS via Mediboard PFI)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|GESTIONNAIRE|PFI_NANTES|20240301090000||ORU^R01^ORU_R01|ORU-MB-001|P|2.5||||||UNICODE UTF-8
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-2047^^^CH_NANTES&1.2.250.1.213.1.4.2&ISO^PI||Fischer^Arlette^^^^^L||19621103|M|||7 Rue de la Fosse^^Nantes^^44000^FRA^H
PV1||I|BIOCHIMIE^301^2^CH_NANTES||||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||BIO-2024-2047^CH_NANTES|11502-2^CR d'examens biologiques^LN|||20240301090000
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^285093456781234@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|2|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
OBX|3|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 9. ORU^R01 - radiology report with masking and patient MSSante (ANS CI-SIS via Mediboard)

```
MSH|^~\&|MEDIBOARD|HOPITAL_A|GESTIONNAIRE|PFI_HOP|20240320143000||ORU^R01^ORU_R01|ORU-MB-002|P|2.5||||||UNICODE UTF-8
PID|||196128D567891^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-063^^^HOPITAL_A&1.2.250.1.213.1.4.2&ISO^PI||Zimmermann^Odette^^^^^L||19610428|F|||3 Allee du Parc^^Lyon^^69003^FRA^H
PV1||I|RAD-B^202^1^HOPITAL_A||||76543219087^Parent^Viviane^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||RAD-2024-063^HOPITAL_A|18748-4^CR d'imagerie medicale^LN|||20240320143000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
PRT||UC||SB^Send by^participation|76543219087^Parent^Viviane^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^285093456781234@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
NTE|1|||FIN
OBX|8|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F
```

---

## 10. MDM^T02 - initial medical document transmission (ANS CI-SIS via Mediboard PFI)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|GESTIONNAIRE|PFI_NANTES|20240410141500||MDM^T02^MDM_T02|MDM-MB-001|P|2.6||||||UNICODE UTF-8
EVN||20240410141500
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-2047^^^CH_NANTES&1.2.250.1.213.1.4.2&ISO^PI||Fischer^Arlette^^^^^L||19621103|M|||7 Rue de la Fosse^^Nantes^^44000^FRA^H
PV1||I|CARD^301^2^CH_NANTES||||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240410141500|||||DOC-2024-100^CH_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^285093456781234@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 11. MDM^T10 - document replacement via Mediboard (ANS CI-SIS volet Trans_Doc_CDA_HL7v2)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|GESTIONNAIRE|PFI_NANTES|20240415093000||MDM^T10^MDM_T02|MDM-MB-002|P|2.6||||||UNICODE UTF-8
EVN||20240415093000
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||Fischer^Arlette^^^^^L||19621103|M
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240415093000|||||DOC-2024-101^CH_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^285093456781234@patient.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CWE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 12. MDM^T04 - document deletion notification (ANS CI-SIS via Mediboard)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|GESTIONNAIRE|PFI_NANTES|20240420110000||MDM^T04^MDM_T02|MDM-MB-003|P|2.6||||||UNICODE UTF-8
EVN||20240420110000
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||Fischer^Arlette^^^^^L||19621103|M
TXA|1|18748-4^CR d'imagerie medicale^LN|TX|||20240420110000|||||DOC-2024-100^CH_NANTES||||||AU
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D
PRT||UC||SB^send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^text^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 13. ACK^A04 - acknowledgement for emergency registration (Gazelle platform)

```
MSH|^~\&|PatientManager|PAM_FR|Gazelle|PAM_FR|20210519120507||ACK^A04^ACK|20210519120507|P|2.5^FRA^2.9||||||UNICODE UTF-8
MSA|AA|20210519120506
```

---

## 14. SIU^S12 - appointment scheduling from Mediboard (IHE SIU profile, French hospital context)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|AGENDA_BLOC|BLOC_OPERATOIRE|20240610091500||SIU^S12^SIU_S12|SIU-MB-001|P|2.5^FRA^2.10||||||UNICODE UTF-8
SCH|RDV-2024-001^MEDIBOARD|RDV-2024-001^AGENDA_BLOC||||RDV^Rendez-vous^HL70276|ROUTINE^Routine^HL70277|60^MIN|||||^Fischer^Arlette|^PRN^PH^^^^^^^^^0240693718|^^BLOC_OP^^44000^FRA|22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-2047^^^CH_NANTES^PI||Fischer^Arlette^^^^^L||19621103|M|||7 Rue de la Fosse^^Nantes^^44000^FRA^H
PV1||O
RGS|1
AIS|1||CHIR-CARD^Chirurgie cardiaque^LOCAL|||20240610091500|60^MIN
AIP|1||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
AIL|1||BLOC_OP^SALLE_2^CH_NANTES
```

---

## 15. ORM^O01 - laboratory order from Mediboard (French hospital lab integration)

```
MSH|^~\&|MEDIBOARD|CH_NANTES|SIL_LABO|BIOCHIMIE|20240715080000||ORM^O01^ORM_O01|ORM-MB-001|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-2047^^^CH_NANTES^PI||Fischer^Arlette^^^^^L||19621103|M|||7 Rue de la Fosse^^Nantes^^44000^FRA^H
PV1||I|CARD^301^2^CH_NANTES||||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW|ORD-2024-001^MEDIBOARD||GRP-001^MEDIBOARD|||||20240715080000|||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
OBR|1|ORD-2024-001^MEDIBOARD||58410-2^NFS^LN|||20240715080000|||||||||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
DG1|1||I25.1^Cardiopathie atherosclereuse^I10
NTE|1||Bilan pre-operatoire chirurgie cardiaque
```

---

## 16. ORU^R01 - lab results numeric observations (French biology lab via Mediboard)

```
MSH|^~\&|SIL_BIOCHIMIE|LABO_CH|MEDIBOARD|CH_NANTES|20240801143000||ORU^R01^ORU_R01|ORU-LAB-001|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-2047^^^CH_NANTES^PI||Fischer^Arlette^^^^^L||19621103|M
PV1||I|CARD^301^2^CH_NANTES||||22233445566^Cordier^Nathalie^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|RE
OBR|1||BIO-2024-301^LABO_CH|58410-2^NFS^LN|R||20240801140000|||22233445566^Cordier^Nathalie
OBX|1|NM|6690-2^Leucocytes^LN||8.2|10*3/uL|4.5-11.0||||F
OBX|2|NM|789-8^Erythrocytes^LN||4.8|10*6/uL|4.7-6.1||||F
OBX|3|NM|718-7^Hemoglobine^LN||14.5|g/dL|13.5-17.5||||F
OBX|4|NM|4544-3^Hematocrite^LN||42.1|%|38.3-48.6||||F
OBX|5|NM|777-3^Plaquettes^LN||245|10*3/uL|150-400||||F
OBX|6|NM|770-8^Polynucleaires neutrophiles^LN||5.1|10*3/uL|1.8-7.7||||F
```

---

## 17. ORU^R01 - document transmission with MODIF_CONF_CODE visibility change (ANS CI-SIS via Mediboard)

```
MSH|^~\&|MEDIBOARD|HOPITAL_B|GESTIONNAIRE|PFI_HOP|20240505160000||ORU^R01^ORU_R01|ORU-MB-003|P|2.5||||||UNICODE UTF-8
PID|||269058234567891^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||Hartmann^Marcelle^^^^^L||19580726|M
ORC|NW
OBR|1||IMG-2024-088^HOPITAL_B|18748-4^CR d'imagerie medicale^LN|||20240505160000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^285093456781234@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 18. ORU^R01 - document deletion request (ANS CI-SIS via Mediboard)

```
MSH|^~\&|MEDIBOARD|HOPITAL_A|GESTIONNAIRE|PFI_HOP|20240325100000||ORU^R01^ORU_R01|ORU-MB-004|P|2.5||||||UNICODE UTF-8
PID|||196128D567891^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH||Zimmermann^Odette^^^^^L||19610428|F
ORC|NW
OBR|1||RAD-2024-063^HOPITAL_A|18748-4^CR d'imagerie medicale^LN|||20240325100000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D
PRT||UC||SB^Send by^participation|60148723965^Boulay^Sylvain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|ED|CORPSMAIL_PS^Corps du mail pour un PS^MetaDMPMSS||^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA==||||||F
```

---

## 19. ORU^R01 - radiology report with embedded JPEG image (ANS CI-SIS context, base64 encapsulated image via Mediboard PACS)

```
MSH|^~\&|MEDIBOARD|CHU_LYON|GESTIONNAIRE|PFI_CHU|20240901102000||ORU^R01^ORU_R01|ORU-MB-IMG-001|P|2.5||||||UNICODE UTF-8
PID|||196128D567891^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-471^^^CHU_LYON^PI||Zimmermann^Odette^^^^^L||19610428|F|||3 Allee du Parc^^Lyon^^69003^FRA^H
PV1||I|RAD-A^101^1^CHU_LYON||||44778899001^Parent^Olivier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||RAD-2024-471^CHU_LYON|18748-4^CR d'imagerie medicale^LN|||20240901102000
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
OBX|2|ED|IMG-RADIO^Image radiographie thoracique JPEG^LOCAL||^image^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBU/9j/4QCcRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAYgAAABsBBQABAAAAagAAABwBAwABAAAAAQAAADsBAgADAAAAAAAAAGmHBAABAAAAbgAAAAAAAAAIAAgACAAKAAAAZAAAAA==||||||F
PRT||UC||SB^Send by^participation|44778899001^Parent^Olivier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||CHU_LYON^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^690783154
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 20. ORU^R01 - anatomopathology report with embedded PNG histology image (ANS CI-SIS context, base64 encapsulated image via Mediboard)

```
MSH|^~\&|MEDIBOARD|CHU_LYON|GESTIONNAIRE|PFI_CHU|20240920150000||ORU^R01^ORU_R01|ORU-MB-IMG-002|P|2.5||||||UNICODE UTF-8
PID|||285093456781234^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~PAT-518^^^CHU_LYON^PI||Fischer^Arlette^^^^^L||19621103|M|||7 Rue de la Fosse^^Nantes^^44000^FRA^H
PV1||I|ANAPATH^201^1^CHU_LYON||||44778899001^Parent^Olivier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^RPPS
ORC|NW
OBR|1||ANAPATH-2024-518^CHU_LYON|60567-5^CR d'anatomie et de cytologie pathologiques^LN|||20240920150000
OBX|1|ED|60567-5^CR d'anatomie et de cytologie pathologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
OBX|2|ED|IMG-HISTO^Image histologie coupe HE^LOCAL||^image^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==||||||F
OBX|3|ED|IMG-MACRO^Photo macroscopique piece operatoire^LOCAL||^image^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB/9j/4QAiRXhpZgAASUkqAAgAAAABADIBAgAUAAAAGgAAAAAAAAA=||||||F
PRT||UC||SB^Send by^participation|44778899001^Parent^Olivier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||CHU_LYON^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^690783154
PRT||UC||RCT^Results Copies To^participation|70193847562^Vasseur^Louis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^louis.vasseur@test-ci-sis.mssante.fr
OBX|4|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|DESTMSSANTEPS^Destinataire PS^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
