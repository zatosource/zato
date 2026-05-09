# M-CrossWay (Maincare / La Poste Sante) - real HL7v2 ER7 messages

## 1. ADT^A01 - patient admission (IHE France PAM, SIGEMS/Enovacom)

```
MSH|^~\&|SIGEMS|SIGEMS|ENOVACOM|ENOVACOM|20151125123110.703+0100||ADT^A01^ADT_A01|54741010000051070000|P|2.5|||||FRA|8859/1
EVN||20151125123110||A01||20151125123007
PID|||73294^^^SIGEMS^PI||ANDRE^Colette^^^^^D~FERREIRA^Colette^^^^^L||19280714|F|||8 RUE DES LILAS^^STRASBOURG^^67000^^H~^^^^^^SA~^^^^^^O~^^RENNES^^^^BR||^PRN^PH^^^^^^^^^0388471256~^PRN^CP^^^^^^^^^0672143589~^NET^Internet^NON|||M||1638472^^^SIGEMS^AN|||||RENNES|||1||||N||VIDE
PD1||||||||||||N
ROL||UC|ODRP|10293847561^DUMONT^Raymond^^^^^^ASIP-SANTE-PS&1.2.250.2.72.4.1.1&ISO^L^^^LLAMA~RAYM01^DUMONT^Luc^^^^^^SIGEMS^L^^^EI|||||||24 RUE PASTEUR^^STRASBOURG^^67000^^O
NK1|1|MME LEGRAND^Lucette|OTH^AUTRE||^PRN^CP^^^^^^^^^0634781295||C^Personne à contacter|20151125
PV1||I|CH01^213^213^330780000||PA73501^^^SIGEMS^AN^^20151027||20003445871^MERCIER^Alain^^^^^^ASIP-SANTE-PS&1.1.300.1.71.4.2.1&ISO^L^^^RPPS~441263000^MERCIER^Alain^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^L^^^ADELI~GUER01^MERCIER^Alain^^^^^^SIGEMS^L^^^EI|||181||||80|||||1638472^^^SIGEMS^AN^^20151125||03|Y||||||||||||||80||||||||20151125170000|||||||A
PV2|||||||SM|20151125170000|20151129180000|||||||||||||N
ZBE|1638472^SIGEMS|20151125170000||INSERT|N||Chirurgie 1^^^^^SIGEMS^UF^^^CHI1||HMS
ZFV|330780537^20151125000000|||||27 RUE DU FAUBOURG^^BORDEAUX^^33000^FRA^DST|||80
```

---

## 2. ADT^A02 - patient transfer (IHE France PAM, Hopital Manager)

```
MSH|^~\&|HMLIT|HMLIT|TELECOMSANTEPLI|TELECOMSANTEPLI|20140415154239||ADT^A02^ADT_A02|13444281|P|2.5|||||FRA|8859/1|FR||
EVN||20151126083028||||20151126083028|
PID|1||73294^^^SIGEMS^PI||LEMAIRE^Yvonne^^^MME^^L||19050827|F|||12 PLACE DE LA REPUBLIQUE^^TOULOUSE^^31000^100^H||06.53.72.18.94^PRN^PH^^^^^^^^^0653721894|||||467219385^^^HMLIT^AN|284053712046893||||||1|||||N|||||||||
PV1|1|I|MATER^174^174^220000301|||MATER^170^170^220000301|TVAL7^JOLIVET^Nathalie^^^^^^HMLIT^^^^EI~33120040000^JOLIVET^Nathalie^^^^^^HMLIT^^^^ADELI|||165|||||||||427118385^^^HMLIT||03|Y||||||||||||||||||||||20140502040000|||||||A|
ZBE|15936482^HMLIT|20151126083028||INSERT|N||MATER^^^^^HMLIT^UF^^^MATER|MATER^^^^^HMLIT^UF^^^MATER|
ZFM|8||||
ROL|15936357^HMLIT|UP|AT|TVAL7^JOLIVET^Nathalie^^^^^^HMLIT^^^^EI~33120000000^JOLIVET^Nathalie^^^^^^HMLIT^^^^ADELI|20151126083028|
```

---

## 3. ADT^A04 - patient registration (ANS Gazelle, PAM_FR ITI-31)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210519120506||ADT^A04^ADT_A01|20210519120506|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210519120506||||20210519120506
PID|||DDS-61748^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||PHILIPPE^Jacques^^^^^L|NOEL^^^^^^M|19930217084300|M|||^^^^^FRA|||||||AN1714^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||E|||||||||||||||||VN3597^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210520120000|||||||V
ZBE|MOV4371^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210519120506||INSERT|N||Urgences^^^^^^UF^^^8782|Psychiatrie adulte^^^^^^UF^^^6277|S^Changement de responsabilité de soins uniquement
ZFA||||N||N|N
ZFP|4|12
ZFV|140024886^20210511120000|||||||||8
ZFM|7||5
ZFD|||N
```

---

## 4. ADT^A05 - pre-admission (ANS Gazelle, PAM_FR ITI-31 with INS)

```
MSH|^~\&|PatientManager|PAM_FR|Cortex-Care|Cortex-Care|20231107113004||ADT^A05^ADT_A05|20231107113004|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20231107113004||||20231107113004
PID|||14293^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~208037261004817^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.10&ISO^INS~208037261004817^^^ASIP-SANTE-INS-NIA&1.2.250.1.213.1.4.9&ISO^INS||NOEL^Renee^^^^^L|DENIS^^^^^^L|20080923|F|||Allee des Marronniers^^Nantes^^44000^FRA^H~^^Grenoble^^38000^FRA^BDL^BDL^38185|||||||AN2891^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|VALI
PV1||I||U|VN4372^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||36001982540^LECOMTE^Denis^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1 I&ISO^D^^^ADELI|||||||||||VN4372^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
PV2||||||||20231107113000
ZBE|MOV6315^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20231107113004||INSERT|N||Pédiatrie^^^^^^UF^^^4044|Ophtalmomogie^^^^^^UF^^^6275|HMS^Changement conjoint des trois responsabilités.
ZFA|INEXISTANT|||N||N|N
ZFP|1|23
ZFM|8
ZFD|||N|N
```

---

## 5. ADT^A28 - patient identity feed with INS (ANS Gazelle, ITI-30)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_F|20240220183827||ADT^A28^ADT_A05|20240220183827|P|2.5^FRA^2.10||||||UNICODE UTF-8
EVN||20240220183827
PID|||195046283710462^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||GILBERT^Louis^Louis Maurice^^^^L||19990403|M|||5 Boulevard Victor Hugo^^Lyon^^69006^FRA^H~^^^^^^BDL|||||||AN1823^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN||||||||||||||VALI
PV1||N
ZFD|||N|N
```

---

## 6. ADT^A01 - encounter with INS (ANS Gazelle, PAM_FR ITI-31)

```
MSH|^~\&|PatientManager|IHE|PatientManager|PAM_FR|20240214100721||ADT^A01^ADT_A01|20240214100721|P|2.5||||||UNICODE UTF-8
EVN||20240214100721||||20210906164312
PID|||13684^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^PI~294058173502641^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||DENIS^Huguette^^^^^L|PEREIRA^^^^^^M|19911108|F|||14 rue de la Paix^^MARSEILLE^^13002^FRA^H|||||||AN1934^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N|PROV
PV1||O||L|||20004587231^MAILLARD^Marc|20004589612^BRESSON^Eloise|||||||||20004563178^DUMONT^Didier||VN3847^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN||||||||||||||||||||||||||||||||V
```

---

## 7. ADT^Z99 - custom event (ANS Gazelle, PAM_FR v2.9)

```
MSH|^~\&|Gazelle|PAM_FR|PatientManager|PAM_FR|20210225112019||ADT^Z99^ADT_A01|20210225112019|P|2.5^FRA^2.9||||||UNICODE UTF-8
EVN||20210225112019||||20210225111437
PID|||DDS-60943^^^DDS&1.3.6.1.4.1.12559.11.36.9&ISO^PI||PEREIRA^Lucette^^^^^L|LUCAS^^^^^^M|20170812000000|F|||^^^^^FRA|||||||AN1502^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^AN|||||||||||||N
PV1||I|||||||||||||||||VN2148^^^GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO^VN|||||||||||||||||||||||||20210226120000|||||||V
ZBE|MOV3201^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO|20210225111437||UPDATE|N|A05
ZFA||||N||N|N
ZFD|||N
```

---

## 8. ACK^A04 - acknowledgment (ANS Gazelle, PAM_FR)

```
MSH|^~\&|PatientManager|PAM_FR|Gazelle|PAM_FR|20210519120507||ACK^A04^ACK|20210519120507|P|2.5^FRA^2.9||||||UNICODE UTF-8
MSA|AA|20210519120506
```

---

## 9. ORU^R01 - MSH example (ANS CI-SIS, Transmission CDA-R2 en HL7v2 v2.1.2)

```
MSH|^~\&|SIL|CHU_X|PFI|CHU_X|202310030830||ORU^R01^ORU_R01|12345|P|2.5|||||FRA|8859/15|||2.1^CISIS_CDA_HL7_V2
```

---

## 10. ORU^R01 - biology report initial transmission (ANS CI-SIS, Volet Trans-CDA-R2)

```
MSH|^~\&|SIL|CHU_X|PFI|CHU_X|202310030830||ORU^R01^ORU_R01|12345|P|2.5|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||9 rue Descartes^^NICE^^06000^FRA^H|||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||11502-2^CR d'examens biologiques^LN
OBX|1|ED|11502-2^CR d'examens biologiques^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
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

## 11. ORU^R01 - radiology report with masking (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 1)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310040900||ORU^R01^ORU_R01|12346|P|2.5|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||O|||||||||||||||||VN8544^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|12|ED|CORPSMAIL_PATIENT^Corps du mail pour le patient^MetaDMPMSS||^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg==||||||F|
```

---

## 12. ORU^R01 - document deletion request (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 2)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310050830||ORU^R01^ORU_R01|12347|P|2.5|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
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

## 13. ORU^R01 - document replacement (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 3)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310060930||ORU^R01^ORU_R01|12348|P|2.5|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
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

## 14. MDM^T02 - radiology report initial transmission (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 0 MDM)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310030830||MDM^T02^MDM_T02|12349|P|2.6|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
EVN||202310030830
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
TXA||18748-4^CR d'imagerie médicale^LN|TX||||||||DOC-UUID-12345-67890|||||AU
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||F|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
PRT||UC||RCT^results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||Radiologie^^^^^120456789^UF^^^3435|||||||^^X.400^radiologie@hopitalA.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
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

## 15. MDM^T04 - document deletion (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 2 MDM)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310071000||MDM^T04^MDM_T02|12350|P|2.6|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
EVN||202310071000
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
TXA||18748-4^CR d'imagerie médicale^LN|TX||||||||DOC-UUID-12345-67890|||||AU
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||D|
PRT||UC||SB^send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
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

## 16. MDM^T10 - document replacement (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 3 MDM)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310081400||MDM^T10^MDM_T02|12351|P|2.6|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
EVN||202310081400
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||I|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
TXA||18748-4^CR d'imagerie médicale^LN|TX||||||||DOC-UUID-12345-NEW||DOC-UUID-12345-67890|||AU
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^text^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
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

## 17. ORU^R01 - visibility modification with REPLY (ANS CI-SIS, Volet Trans-CDA-R2 Exemple 4)

```
MSH|^~\&|RIS|CHU_X|PFI|CHU_X|202310091100||ORU^R01^ORU_R01|12352|P|2.5|||||FRA|UNICODE UTF-8|||2.1^CISIS_CDA_HL7_V2
PID|||987654321^^^CHU_X&1.2.250.1.213.1.4.2&ISO^PI~176091248703519^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||LEGRAND^Daniel^^^^^L||19770603|M|||||||||||DA78432^^^CHU_X&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||O|||||||||||||||||VN8543^^^CHU_X&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||18748-4^CR d'imagerie médicale^LN
OBX|1|ED|18748-4^CR d'imagerie médicale^LN||^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ||||||C|
PRT||UC||SB^Send by^participation|80256743189^MERCIER^Daniel^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS|||Organisation-X^^^^^ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO^FINEG^^^300017985
PRT||UC||RCT^Results Copies To^participation|10256743183^JOLIVET^Maurice^^^^^^ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO^D^^^RPPS||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
PRT||UC||RCT^Results Copies To^participation||||||12|||||^^X.400^appliExemple@hopitalB.mssante.fr
PRT||UC||RCT^Results Copies To^participation|||||||||||^^X.400^147093418000253@patient.mssante.fr
PRT||UC||REPLY^Reply to^participation|||||||||||^^X.400^maurice.jolivet@test-ci-sis.mssante.fr
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|INVISIBLE_PATIENT^Document Non Visible par le patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|4|CE|INVISIBLE_REP_LEGAUX^Non visible par les représentants Légaux du patient^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|5|CE|CONNEXION_SECRETE^Connexion Secrete^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|6|CE|MODIF_CONF_CODE^Modification Confidentiality Code^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|7|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|8|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|9|CE|DESTMSSANTEPAT^Destinataire Patient^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|10|CE|ACK_RECEPTION^Accusé de réception^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|11|CE|ACK_LECTURE_MSS^Accusé de lecture^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
```

---

## 18. ORU^R01 - retinal screening with embedded JPEG image (IRIS/RetinalScreenings ORU, ED format used in France PFI integrations)

```
MSH|^~\&|IRIS|IRIS|PFI|CHU_LILLE|20231215143022||ORU^R01|231215143022|P|2.4|||AL|NE
PID||PAT54321^^^^MRN|PAT54321||LUCAS^Michel||19720809|M||||||||||7643|183076249301856
PV1|1|O|OPHTALMO^^^^||||34567^BRESSON^Christine^^^^^^RPPS^^^^RPPS|||OPH
ORC|RE||ORD-2023-7812|||^^^20231215143000||20231215143022|||34567^BRESSON^Christine^^^^^^RPPS^^^^RPPS
OBR|1||ORD-2023-7812|92250-7^Fundus Photography^LN|||20231215142500|||||||||34567^BRESSON^Christine||||||20231215143000|||F
OBX|1|CWE|57832-8^Diabetic Retinal Screening Severity^LN||LA24921-5^No apparent retinopathy^LN||||||F
OBX|2|CWE|57831-0^Macular Edema^LN||LA9634-2^Absent^LN||||||F
OBX|3|NM|57830-2^Image Quality^LN||85|%|||||F
OBX|4|ED|57829-4^Fundus Image Right Eye^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFRABAQAAAAAAAAAAAAAAAAAAABb/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AkqOjX//Z||||||F
OBX|5|ED|57828-6^Fundus Image Left Eye^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFRABAQAAAAAAAAAAAAAAAAAAABb/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AjaOjL//Z||||||F
OBX|6|ED|PDF^Rapport PDF^LOCAL||^Application^PDF^Base64^JVBERi0xLjMNCiXi48/TDQoNCjEgMCBvYmoNCjw8DQovVHlwZSAvQ2F0YWxvZw0KL091dGxpbmVzIDIgMCBSDQovUGFnZXMgMyAwIFINCj4+DQplbmRvYmoNCg0KMiAwIG9iag0KPDwNCi9UeXBlIC9PdXRsaW5lcw0KL0NvdW50IDANCj4+DQplbmRvYmoNCg==||||||F
```

---

## 19. ORU^R01 - scanned document with embedded TIFF image (HL7 Australia/IHE format, used in French scanning workflows)

```
MSH|^~\&|SCANNER|CHU_MONTPELLIER|PFI|CHU_MONTPELLIER|20231020091500||ORU^R01^ORU_R01|MSG20231020091500|P|2.5|||||FRA|UNICODE UTF-8
PID|||876543^^^CHU_MONTPELLIER&1.2.250.1.213.1.4.2&ISO^PI~291048537012394^^^ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO^INS||FERREIRA^Huguette^^^^^L||19880521|F|||||||||||DA91347^^^CHU_MONTPELLIER&1.2.250.1.213.1.4.2&ISO^AN|||||||||||||VALI
PV1||O|||||||||||||||||VN6718^^^CHU_MONTPELLIER&1.2.250.1.213.1.4.2&ISO^VN||||||||||||||||||||||||||||||||V
ORC|NW
OBR|1|||11490-0^Document numérisé^LN|||20231020091500
OBX|1|ED|11490-0^Document numérisé^LN||^IM^TIFF^Base64^SUkqANQAAABXQU5HIFRJRkYgAQC8AAAAVGl0bGU6AEF1dGhvcjoAU3ViamVjdDoAS2V5d29yZHM6AENvbW1lbnRzOgAAAFQAaQB0AGwAZQA6AAAAAABBAHUAdABoAG8AcgA6AAAAAABTAHUAYgBqAGUAYwB0ADoAAAAAAEsAZQB5AHcAbwByAGQAcwA6AAAAAABDAG8AbQBtAGUAbgB0AHMAOgAAAAAAAAAAAA==||||||F
OBX|2|CE|MASQUE_PS^Masqué aux professionnels de Santé^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
OBX|3|CE|DESTDMP^Destinataire DMP^MetaDMPMSS||Y^^expandedYes-NoIndicator||||||F|
OBX|4|CE|DESTMSSANTEPS^Destinataire (Professionnel de Santé, organisation ou BAL applicative)^MetaDMPMSS||N^^expandedYes-NoIndicator||||||F|
```

---

## 20. ACK^A05 - acknowledgment with version FRA 2.10 (ANS Gazelle, Cortex-Care)

```
MSH|^~\&|Cortex-Care|Cortex-Care|PatientManager|PAM_FR|20231107103005||ACK^A05^ACK|20231107103005|P|2.5^FRA^2.10
MSA|AA|20231107113004
```
