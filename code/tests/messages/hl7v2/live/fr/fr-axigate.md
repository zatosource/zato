# Axigate (Axigate Link) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission (MCO inpatient)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|SIH_Receptor|CH-LYON|20251130103019||ADT^A01^ADT_A01|20251130103019|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251130103019||||20251130103019
PID|||278043512378956^^^ASIP-SANTE-INS-C&1.2.250.1.213.1.4.6&ISO^NH~DDS-66086^^^DDS&1.3.6.1.4.1.12559.11.36.3&ISO^PI||LEFEBVRE^ANTOINE^^^^^L|GARNIER^^^^^^M|19840808|M|||15 Rue de la Paix^^Lyon^^69003^FRA^H|||||||AN3544^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||I|||||||||||||||||VN4369^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20251130103000|||||||V
ZBE|MOV7434^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20251130103019||INSERT|N
ZFA||||N||N|N
ZFD|||N|N
```

---

## 2. ADT^A04 - Emergency registration

```
MSH|^~\&|HOSPILINK|AXIGATE_URG|SIH_Receptor|CH-LYON|20250427122641||ADT^A04^ADT_A01|20250427122641|P|2.5||||||UNICODE UTF-8
EVN||20250427122641||||20250427122641
PID|||DDS-64995^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||RODRIGUEZ^LUCAS^^^^^L|SANCHEZ^^^^^^M|20130109214522|M|||^^^^^ESP|||||||AN2507^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||R||L|||10200834567^Blanchard^Christophe|10101765432^Renaud^Camille|||||||||10102498765^Picard^Augustin||VN2882^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
ZBE|MOV4320^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20250427122641||INSERT|N
```

---

## 3. ADT^A28 - Add patient demographic (ITI-30)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|SIH_Receptor|PAM_F|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||201035467892345^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MERCIER^PHILIPPE^ALAIN^^^^L||20030617|M|||8 rue des Lilas^^Strasbourg^^67000^FRA^H~^^^^^^BDL|||||||AN2607^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 4. ADT^A04 - Outpatient registration with INS

```
MSH|^~\&|HOSPILINK|AXIGATE_CONSULT|SIH_Receptor|CH-LYON|20250519120506||ADT^A04^ADT_A01|20250519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20250519120506||||20250519120506
PID|||DDS-65102^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||BLANC^JULIEN^^^^^L|LAMBERT^^^^^^M|19970530075500|M|||^^^^^FRA|||||||AN2612^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN3583^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20250520120000|||||||V
ZBE|MOV5632^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20250519120506||INSERT|N
ZFD|||N|N
```

---

## 5. ADT^A28 - Demographics with multiple identifiers

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|SIH_Receptor|PAM_FR|20240423154852||ADT^A28^ADT_A05|20240423154852|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240423154852
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~2880912345678^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS~IPP-02145^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||MOREAU^CAROLINE^LUCIE^^^^L|VINCENT^^^^^^M|19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H|||||||AN5613^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 6. ADT^A02 - Transfer between units (SMR)

```
MSH|^~\&|HOSPILINK|AXIGATE_SMR|SIH_Receptor|CH-LYON|20251201091500||ADT^A02^ADT_A02|20251201091500|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251201091500||||20251201091500
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-02145^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||MOREAU^CAROLINE^LUCIE^^^^L|VINCENT^^^^^^M|19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H|||||||AN5613^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|REEDUCATION^RE201^2^^^AXIGATE||||10400321987^Lemaire^Veronique||||||||||||||VN6723^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20251128080000|||||||V
PV2||||||||20251220
ZBE|MOV9012^AXIGATE^2.16.840.1.113883.2.8.3.7^ISO|20251201091500||UPDATE|N
ZFD|||N|N
```

---

## 7. ADT^A03 - Discharge

```
MSH|^~\&|HOSPILINK|AXIGATE_SMR|SIH_Receptor|CH-LYON|20251220160000||ADT^A03^ADT_A03|20251220160000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251220160000||||20251220160000
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-02145^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||MOREAU^CAROLINE^LUCIE^^^^L|VINCENT^^^^^^M|19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H|||||||AN5613^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|REEDUCATION^RE201^2^^^AXIGATE||||10400321987^Lemaire^Veronique||||||||||||||VN6723^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20251128080000|20251220160000|||||V
ZBE|MOV9013^AXIGATE^2.16.840.1.113883.2.8.3.7^ISO|20251220160000||UPDATE|N
ZFD|||N|N
```

---

## 8. ADT^A08 - Update patient demographics

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|SIH_Receptor|CH-LYON|20251203140000||ADT^A08^ADT_A01|20251203140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251203140000||||20251203140000
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-02145^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||MOREAU^CAROLINE^LUCIE^^^^L|VINCENT^^^^^^M|19880912|F|||47 Rue Victor Hugo^^Nantes^^44000^FRA^H||0240567834|||||||AN5613^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|REEDUCATION^RE201^2^^^AXIGATE||||10400321987^Lemaire^Veronique||||||||||||||VN6723^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20251128080000|||||||V
ZBE|MOV9014^AXIGATE^2.16.840.1.113883.2.8.3.7^ISO|20251203140000||UPDATE|N
ZFD|||N|N
```

---

## 9. ADT^A05 - Pre-admission (HAD - Home hospitalization)

```
MSH|^~\&|DOMILINK|AXIGATE_HAD|SIH_Receptor|CH-LYON|20251210090000||ADT^A05^ADT_A05|20251210090000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251210090000||||20251210090000
PID|||271113412389756^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-02189^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||FOURNIER^NATHALIE^ELISE^^^^L|ROUX^^^^^^M|19711115|F|||12 Chemin des Platanes^^Montpellier^^34000^FRA^H||0467891234|||||||AN5789^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||I|HAD^DOMICILE^1^^^AXIGATE||||10500876543^Guillot^Thierry||||||||||||||VN6901^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||||||||||V
ZBE|MOV9112^AXIGATE^2.16.840.1.113883.2.8.3.7^ISO|20251210090000||INSERT|N
ZFD|||N|N
```

---

## 10. ADT^A11 - Cancel admission

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|SIH_Receptor|CH-LYON|20251204083000||ADT^A11^ADT_A09|20251204083000|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20251204083000||||20251204083000
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS~IPP-02145^^^AXIGATE&1.2.250.1.213.1.1.2.1&ISO^PI||MOREAU^CAROLINE^LUCIE^^^^L|VINCENT^^^^^^M|19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H|||||||AN5613^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I|||||||||||||||||VN6723^^^AXIGATE&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20251128080000|||||||V
ZBE|MOV9015^AXIGATE^2.16.840.1.113883.2.8.3.7^ISO|20251204083000||CANCEL|N
ZFD|||N|N
```

---

## 11. ORU^R01 - Biology report for DMP (CDA-R2 level 3)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251215103000||ORU^R01^ORU_R01|MSG20251215103000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|BIOLOGIE^BIO101^1^^^AXIGATE
ORC|NW||ORD-AXI-20251215|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-20251215|11502-2^CR d'examens biologiques^LN
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10134567823^Clement^Xavier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^288091234567823@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
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

## 12. ORU^R01 - Radiology report with masking

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251216140000||ORU^R01^ORU_R01|MSG20251216140000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-20251216|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-20251216|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||F
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^288091234567823@patient.mssante.fr
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

## 13. ORU^R01 - Document deletion

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251217080000||ORU^R01^ORU_R01|MSG20251217080000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-20251217|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-20251217|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx||||||D
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10134567823^Clement^Xavier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
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

## 14. ORU^R01 - Document replacement

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251218093000||ORU^R01^ORU_R01|MSG20251218093000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-20251218|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-20251218|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10134567823^Clement^Xavier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^288091234567823@patient.mssante.fr
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

## 15. MDM^T02 - Initial medical document transmission

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251219110000||MDM^T02^MDM_T02|MSG20251219110000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20251219110000
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-20251219
OBR|1||ORD-AXI-20251219|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20251219110000|||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.5678^AXIGATE|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10134567823^Clement^Xavier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
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

## 16. MDM^T04 - Document status change notification (deletion)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251220143000||MDM^T04^MDM_T02|MSG20251220143000|P|2.6^FRA^2.1||||||UNICODE UTF-8
EVN||20251220143000
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-20251220D
OBR|1||ORD-AXI-20251220D|18748-4^CR d'imagerie medicale^LN
TXA|1|18748-4^CR d'imagerie medicale^LN|TEXT||20251220143000|||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||1.2.250.1.213.1.1.9.5678^AXIGATE|||||||LA
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D
PRT||UC||SB^send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|10134567823^Clement^Xavier^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^xavier.clement@test-ci-sis.mssante.fr
OBX|2|CWE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CWE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CWE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CWE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|6|CWE|ACK_LECTURE_MSS^Accuse de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 17. ACK - Positive acknowledgment

```
MSH|^~\&|SIH_Receptor|CH-LYON|HOSPILINK|AXIGATE_MCO|20251130093020||ACK^A01^ACK|20251130093020|P|2.5^FRA^2.10
MSA|AA|20251130103019
```

---

## 18. ACK - Negative acknowledgment (error)

```
MSH|^~\&|SIH_Receptor|CH-LYON|HOSPILINK|AXIGATE_MCO|20251204090000||ACK^A01^ACK|20251204090000|P|2.5^FRA^2.10
MSA|AE|20251204083000
ERR|||207^Application internal error^HL70357||||Patient identifier not found in local registry
```

---

## 19. ORU^R01 - Embedded JPEG radiology image (ED/Base64)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251222143000||ORU^R01^ORU_R01|MSG20251222143000|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-IMG-20251222|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-IMG-20251222|18748-4^CR d'imagerie medicale^LN
OBX|1|ED|18748-4^CR d'imagerie medicale^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAAcP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgA/9k=||||||F
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```

---

## 20. ORU^R01 - Embedded PDF scanned consent document (ED/Base64)

```
MSH|^~\&|HOSPILINK|AXIGATE_MCO|PFI_GESTIONNAIRE|CH-LYON|20251223161500||ORU^R01^ORU_R01|MSG20251223161500|P|2.5^FRA^2.10||||||UNICODE UTF-8
PID|||288091234567823^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||MOREAU^CAROLINE^^^^^L||19880912|F|||22 Boulevard Gambetta^^Nantes^^44000^FRA^H
PV1||I|IMAGERIE^IMG201^1^^^AXIGATE
ORC|NW||ORD-AXI-SCAN-20251223|||||||80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS
OBR|1||ORD-AXI-SCAN-20251223|11488-4^Document numerise^LN
OBX|1|ED|11488-4^Document numerise^LN||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjMgMDAwMDAgbiAKMDAwMDAwMDEyMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIxNQolJUVPRgo=||||||F
PRT||UC||SB^Send by^participation|80134567891^Marchand^Henri^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
OBX|2|CE|MASQUE_PS^Masque aux professionnels de Sante^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Sante, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
OBX|5|CE|ACK_RECEPTION^Accuse de reception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F
```
