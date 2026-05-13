# HopitalWEB / Osiris (Evolucare Technologies) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission (inpatient)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231130103019||ADT^A01^ADT_A01|20231130103019|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231130103019||||20231130103019
PID|||1830412247813295462187^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-67148^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||THOMAS^Antoine^^^^^L|MOREAU^^^^^^M|19830412|M|||14 Rue de Kerinou^^Quimper^^29000^FRA^H|||||||AN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I|||||||||||||||||VN5541^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV8596^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231130103019||INSERT|N
ZFA||||N||N|N
ZFD|||N|N
```

---

## 2. ADT^A04 - Patient registration (outpatient/emergency)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_URG|SIH_Receptor|CH-EXAMPLE|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-66274^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||ROBERT^Henri^^^^^L|FOURNIER^^^^^^M|19970214083200|M|||^^^^^FRA|||||||AN3784^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN4755^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV6794^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N
ZFD|||N|N
```

---

## 3. ADT^A04 - Emergency registration with location

```
MSH|^~\&|HopitalWEB|EVOLUCARE_URG|SIH_Receptor|CH-EXAMPLE|20210427122641||ADT^A04^ADT_A01|20210427122641|P|2.5||||||UNICODE UTF-8
EVN||20210427122641||||20210427122641
PID|||DDS-66157^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||RICHARD^Georges^^^^^L|GIRARD^^^^^^M|20080317152800|M|||^^^^^ESP|||||||AN3679^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||R||L|||10300527843^CLEMENT^Marc|10201764387^NICOLAS^Sophie|||||||||10302298614^MATHIEU^Laurent||VN4054^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
ZBE|MOV5482^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210427122641||INSERT|N
```

---

## 4. ADT^A28 - Add patient demographic information (ITI-30)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|PAM_F|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||269082317854296^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||PETIT^Madeleine^Simone^^^^L||19990823|M|||3 Rue Victor Hugo^^Lyon^^69003^FRA^H~^^^^^^BDL|||||||AN3779^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 5. ADT^A28 - Add patient with multiple INS identifiers (ITI-30)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|PAM_FR|20240423154852||ADT^A28^ADT_A05|20240423154852|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240423154852
PID|||272054413726183^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~2720544137261^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS~IPP-91625^^^EVOLUCARE&1.2.250.1.213.1.1.1.1&ISO^PI||DURAND^Simone^Andree^^^^L|BONNET^^^^^^M|19720509|F|||8 Place du Commerce^^Nantes^^44000^FRA^H|||||||AN5174^^^EVOLUCARE&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 6. ADT^A02 - Patient transfer between units

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231201091500||ADT^A02^ADT_A02|20231201091500|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231201091500||||20231201091500
PID|||1830412247813295462187^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-67148^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||THOMAS^Antoine^^^^^L|MOREAU^^^^^^M|19830412|M|||14 Rue de Kerinou^^Quimper^^29000^FRA^H|||||||AN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^C312^1^^^EVOLUCARE||||10300527843^CLEMENT^Marc||||||||||||||VN5541^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
PV2||||||||20231205
ZBE|MOV8597^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231201091500||UPDATE|N
ZFD|||N|N
```

---

## 7. ADT^A03 - Patient discharge

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231205160000||ADT^A03^ADT_A03|20231205160000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231205160000||||20231205160000
PID|||1830412247813295462187^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-67148^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||THOMAS^Antoine^^^^^L|MOREAU^^^^^^M|19830412|M|||14 Rue de Kerinou^^Quimper^^29000^FRA^H|||||||AN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^C312^1^^^EVOLUCARE||||10300527843^CLEMENT^Marc||||||||||||||VN5541^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|20231205160000|||||V
ZBE|MOV8598^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231205160000||UPDATE|N
ZFD|||N|N
```

---

## 8. ADT^A08 - Update patient information

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231202140000||ADT^A08^ADT_A01|20231202140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231202140000||||20231202140000
PID|||1830412247813295462187^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-67148^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||THOMAS^Antoine^^^^^L|MOREAU^^^^^^M|19830412|M|||7 Rue de Siam^^Quimper^^29000^FRA^H||0298451237|||||||AN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^C312^1^^^EVOLUCARE||||10300527843^CLEMENT^Marc||||||||||||||VN5541^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV8599^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231202140000||UPDATE|N
ZFD|||N|N
```

---

## 9. ORU^R01 - Transmission of biology report (CDA-R2) for DMP/MSSante

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231215103000||ORU^R01^ORU_R01|MSG20231215103000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|BIOLOGIE^B201^1^^^EVOLUCARE
ORC|NW||ORD-2023121551|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023121551|11502-2^CR d'examens biologiques^LN
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
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

## 10. ORU^R01 - Radiology report (CDA-R2) with PS masking

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231216140000||ORU^R01^ORU_R01|MSG20231216140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023121651|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023121651|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^267071844923157@patient.mssante.fr
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

## 11. ORU^R01 - Document deletion request

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231217080000||ORU^R01^ORU_R01|MSG20231217080000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023121751|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023121751|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
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

## 12. ORU^R01 - Document replacement (new version)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231218093000||ORU^R01^ORU_R01|MSG20231218093000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023121851|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023121851|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^267071844923157@patient.mssante.fr
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

## 13. MDM^T02 - Medical document management initial transmission

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231219110000||MDM^T02^MDM_T02|MSG20231219110000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20231219110000
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023121951
OBR|1||ORD-2023121951|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20231219110000|||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.5678^EVOLUCARE|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^267071844923157@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
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

## 14. MDM^T10 - Document replacement via MDM

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231220090000||MDM^T10^MDM_T02|MSG20231220090000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20231220090000
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023122051
OBR|1||ORD-2023122051|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20231220090000|||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.5678^EVOLUCARE|1.2.250.1.213.1.1.9.5677^EVOLUCARE|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^267071844923157@patient.mssante.fr
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

## 15. ACK - Acknowledgment response to ADT

```
MSH|^~\&|SIH_Receptor|CH-EXAMPLE|HopitalWEB|EVOLUCARE_MCO|20231130093020||ACK^A01^ACK|20231130093020|P|2.5^FRA^2.10
MSA|AA|20231130103019
```

---

## 16. ADT^A05 - Pre-admission

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231128150000||ADT^A05^ADT_A05|20231128150000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231128150000||||20231128150000
PID|||284092135847261^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-55329^^^EVOLUCARE&1.2.250.1.213.1.1.1.1&ISO^PI||FOURNIER^Germaine^Jacqueline^^^^L|PETIT^^^^^^M|19840921|F|||5 Rue de la Monnaie^^Rennes^^35000^FRA^H||0299547812|||||||AN5295^^^EVOLUCARE&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||I|CARDIO^C201^1^^^EVOLUCARE||||10400617852^MULLER^Francois|||||||||||||||||||||||||||||||||||||||20231203|||||||V
ZBE|MOV9274^EVOLUCARE^2.16.840.1.113883.2.8.3.7^ISO|20231128150000||INSERT|N
ZFD|||N|N
```

---

## 17. ADT^A13 - Cancel discharge

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|SIH_Receptor|CH-EXAMPLE|20231206080000||ADT^A13^ADT_A01|20231206080000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231206080000||||20231206080000
PID|||1830412247813295462187^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-67148^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||THOMAS^Antoine^^^^^L|MOREAU^^^^^^M|19830412|M|||14 Rue de Kerinou^^Quimper^^29000^FRA^H|||||||AN4716^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|CARDIO^C312^1^^^EVOLUCARE||||10300527843^CLEMENT^Marc||||||||||||||VN5541^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20231130103000|||||||V
ZBE|MOV8600^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231206080000||CANCEL|N
ZFD|||N|N
```

---

## 18. ORU^R01 - Document with visibility modification (MODIF_CONF_CODE)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231221100000||ORU^R01^ORU_R01|MSG20231221100000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023122151|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023122151|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10345678927^LOUIS^Jean^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^267071844923157@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^jean.louis@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les representants Legaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|10|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|11|CE|ACK_LECTURE^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 19. ORU^R01 - Radiology image embedded as JPEG (ED/Base64)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231222143000||ORU^R01^ORU_R01|MSG20231222143000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023122251|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023122251|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAAcP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgA/9k=||||||F
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 20. ORU^R01 - Scanned document as PDF embedded (ED/Base64)

```
MSH|^~\&|HopitalWEB|EVOLUCARE_MCO|PFI_GESTIONNAIRE|CH-EXAMPLE|20231223161500||ORU^R01^ORU_R01|MSG20231223161500|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||267071844923157^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEROY^Roger^^^^^L||19670718|M|||15 Cours de l'Intendance^^Bordeaux^^33000^FRA^H
PV1||I|RADIO^R101^1^^^EVOLUCARE
ORC|NW||ORD-2023122351|||||||80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-2023122351|11502-2^CR d'examens biologiques^LN
OBX|1|ED|PDF^Document numerise^LOCAL||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjMgMDAwMDAgbiAKMDAwMDAwMDEyMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIxNQolJUVPRgo=||||||F
PRT||UC||SB^Send by^participation|80345678914^VINCENT^Pierre^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
