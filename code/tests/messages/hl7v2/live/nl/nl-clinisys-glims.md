# Clinisys GLIMS - real HL7v2 ER7 messages

---

## 1. OML^O21 - lab order outsourcing (aanvraag uitbesteding) - clinical chemistry

```
MSH|^~\&|101|UMCU_LAB|202|ERASMUS_LAB|20260509083000||OML^O21^OML_O21|MSG20260509001|P|2.5|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.31^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
PID|||246813579^^^NLMINBIZA^NNNLD~PAT001^^^UMCU^PI||de Jong^Anneke^W^^^Mevr.||19780315|F|||Lange Nieuwstraat 15^^Utrecht^^3512PN^NLD^H||^^PH^0302531847
PV1||O|POLI KLC^Klinische Chemie^1|||||10045^Visser^Hendrik^^^Dr.^arts
ORC|NW|ORD2026001|||||^^^20260509083000^^R||20260509083000||10045^Visser^Hendrik^^^Dr.^arts
OBR|1|ORD2026001||24325-3^Electrolyte panel - Serum or Plasma^LN|||20260509080000||||A|||||10045^Visser^Hendrik^^^Dr.^arts
SPM|1|||BLDV^Blood venous^HL70487|||||||||||||20260509080000|20260509081500
```

---

## 2. OML^O21 - lab order with clinical context (microbiology outsourcing)

```
MSH|^~\&|305|OLVG_LAB|912|RIVM_IDS|20260509091500||OML^O21^OML_O21|MSG20260509002|P|2.5|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.31^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
PID|||135792468^^^NLMINBIZA^NNNLD~PAT002^^^OLVG^PI||Smit^Pieter^J^^^Dhr.||19650722|M|||Prinsengracht 312^^Amsterdam^^1016HX^NLD^H||^^PH^0206641827
PV1||I|IC^Intensive Care^Bed 3||||20010^Dekker^Elisabeth^^^Dr.^arts
ORC|NW|ORD2026002|||||^^^20260509091500^^R||20260509091500||20010^Dekker^Elisabeth^^^Dr.^arts
OBR|1|ORD2026002||29576-6^Bacterial susceptibility panel^LN|||20260509090000||||A|||||20010^Dekker^Elisabeth^^^Dr.^arts
OBX|1|TX|46239-0^Chief complaint^LN||Urineweginfectie, recidiverend||||||F
OBX|2|TX|8251-1^Service comment^LN||Resistentiebepaling gevraagd na kweek positief E.coli||||||F
SPM|1|||UR^Urine^HL70487|||||||||||||20260509085500|20260509090000
OBR|2|ORD2026002||29576-6^Bacterial susceptibility panel^LN
OBX|1|ST|6652-2^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||>=16|mg/L||null|||F
OBX|2|ST|7029-2^Meropenem [Susceptibility] by Gradient strip^LN||8.0|mg/L||null|||F
OBX|3||18943-1^Meropenem [Susceptibility]^LN|||||R|||F
```

---

## 3. OUL^R22 - lab result outsourcing (resultaat uitbesteding) - hematology

```
MSH|^~\&|202|ERASMUS_LAB|101|UMCU_LAB|20260509103000||OUL^R22^OUL_R22|MSG20260509003|P|2.5|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.32^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
PID|||246813579^^^NLMINBIZA^NNNLD~PAT001^^^UMCU^PI||de Jong^Anneke^W^^^Mevr.||19780315|F|||Lange Nieuwstraat 15^^Utrecht^^3512PN^NLD^H
PV1||O|POLI KLC^Klinische Chemie^1
SPM|1|||BLDV^Blood venous^HL70487|||||||||||||20260509080000|20260509081500
OBR|1|ORD2026001||58410-2^CBC panel - Blood by Automated count^LN|||20260509090000|||||||||||||||20260509103000|||F
ORC|RE|ORD2026001||||||20260509103000
OBX|1|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||8.2|mmol/L^mmol/L^UCUM|7.5-10.0||||F|||20260509100000
OBX|2|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||7.3|10*9/L^10*9/L^UCUM|4.0-10.0||||F|||20260509100000
OBX|3|NM|26515-7^Platelets [#/volume] in Blood by Automated count^LN||245|10*9/L^10*9/L^UCUM|150-400||||F|||20260509100000
OBX|4|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.85|10*12/L^10*12/L^UCUM|3.90-5.50||||F|||20260509100000
```

---

## 4. ORU^R01 - clinical chemistry result (natrium, kalium, creatinine)

```
MSH|^~\&|GLIMS|VUMC_LAB|HIS|VUMC|20260509110000||ORU^R01^ORU_R01|MSG20260509004|P|2.5|||AL|NE|NLD|8859/1
PID|||357924681^^^NLMINBIZA^NNNLD~PAT003^^^VUMC^PI||Bos^Willem^F^^^Dhr.||19520410|M|||Stadionplein 44^^Amsterdam^^1076CM^NLD^H||^^PH^0206448821
PV1||I|4W^Interne Geneeskunde^Bed 12||||30020^van der Laan^Cornelia^^^Dr.^arts
ORC|RE|ORD2026003
OBR|1|ORD2026003||24325-3^Electrolyte panel - Serum or Plasma^LN|||20260509100000|||||||||||||||20260509110000|||F
OBX|1|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||139|mmol/L^mmol/L^UCUM|135-145|N|||F|||20260509104500
OBX|2|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.1|mmol/L^mmol/L^UCUM|3.5-5.0|N|||F|||20260509104500
OBX|3|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||101|mmol/L^mmol/L^UCUM|98-107|N|||F|||20260509104500
OBX|4|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||89|umol/L^umol/L^UCUM|62-106|N|||F|||20260509104500
OBX|5|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||5.8|mmol/L^mmol/L^UCUM|2.5-7.5|N|||F|||20260509104500
```

---

## 5. ORU^R01 - liver function panel result

```
MSH|^~\&|GLIMS|RIJNSTATE_LAB|HIS|RIJNSTATE|20260509113000||ORU^R01^ORU_R01|MSG20260509005|P|2.5|||AL|NE|NLD|8859/1
PID|||864209753^^^NLMINBIZA^NNNLD~PAT004^^^RIJNSTATE^PI||Janssen^Theodora^L^^^Mevr.||19870603|F|||Velperplein 18^^Arnhem^^6811AG^NLD^H||^^PH^0263541289
PV1||O|POLI MDL^Maag-Darm-Leverziekten^1||||40030^Kuiper^Adriaan^^^Dr.^arts
ORC|RE|ORD2026004
OBR|1|ORD2026004||24326-1^Electrolytes 1998 panel - Serum or Plasma^LN|||20260509101500|||||||||||||||20260509113000|||F
OBX|1|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L^U/L^UCUM|0-35|N|||F|||20260509111000
OBX|2|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||32|U/L^U/L^UCUM|0-45|N|||F|||20260509111000
OBX|3|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||78|U/L^U/L^UCUM|40-120|N|||F|||20260509111000
OBX|4|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||12|umol/L^umol/L^UCUM|0-17|N|||F|||20260509111000
OBX|5|NM|2336-6^Gamma glutamyl transferase [Enzymatic activity/volume] in Serum or Plasma^LN||45|U/L^U/L^UCUM|0-55|N|||F|||20260509111000
OBX|6|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||42|g/L^g/L^UCUM|35-52|N|||F|||20260509111000
```

---

## 6. OML^O21 - ZorgDomein lab order with BSN (diagnostische aanvraag)

```
MSH|^~\&|ZorgDomein||GLIMS|ANTONIUS_LAB|20260509090000+0200||OML^O21^OML_O21|ZD20260509001|P|2.5.1|||AL|AL|NLD|8859/1
NTE|1|P|Klinische Chemie|ZD_CLUSTER_NAME^ZorgDomein clusternaam^L
PID|1||579246813^^^NLMINBIZA^NNNLD||Hoekstra^Geertje^M^^^Mevr.||19900512|F|||Plompetorengracht 7^^Utrecht^^3512CA^NLD||^^PH^0302345678||NLD|M
PV1||O|||||50040^Kok^Margaretha^^^Dr.^huisarts||||||||||||V20260509001
PV2||||||||||||||||||||||||||||||||||||Vermoeden diabetes mellitus type 2
IN1|1||3311^VGZ Zorgverzekering|VGZ|||||||||||||||||||||||||||||||||||||||||||NLD
ORC|NW|ZD20260509001|||||^^^20260509090000^^R
OBR|1|ZD20260509001||GLU^Glucose nuchter^L|||20260509085000||||A
OBX|1|TX|CLIN^Klinische vraag^L||Nuchter glucose ter uitsluiting DM2, patient klaagt over polyurie en polydipsie||||||F
```

---

## 7. ORL^O22 - order acknowledgement (bevestiging aanvraag)

```
MSH|^~\&|202|ERASMUS_LAB|101|UMCU_LAB|20260509084500||ORL^O22^ORL_O22|MSG20260509007|P|2.5|||NE|NE|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.33^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
MSA|AA|MSG20260509001
PID|||246813579^^^NLMINBIZA^NNNLD||de Jong^Anneke^W^^^Mevr.||19780315|F
ORC|OK|ORD2026001||||||20260509084500
OBR|1|ORD2026001||24325-3^Electrolyte panel - Serum or Plasma^LN
```

---

## 8. ORU^R01 - microbiology culture result with antibiogram

```
MSH|^~\&|GLIMS|ISALA_LAB|HIS|ISALA|20260509130000||ORU^R01^ORU_R01|MSG20260509008|P|2.5|||AL|NE|NLD|8859/1
PID|||648201357^^^NLMINBIZA^NNNLD~PAT005^^^ISALA^PI||Meijer^Geert^B^^^Dhr.||19710918|M|||Grote Markt 9^^Zwolle^^8011LV^NLD^H
PV1||I|3A^Chirurgie^Bed 8||||60050^van Beek^Johanna^^^Dr.^arts
ORC|RE|ORD2026005
OBR|1|ORD2026005||630-4^Bacteria identified in Urine by Culture^LN|||20260508150000|||||||||||||||20260509130000|||F
OBX|1|CWE|630-4^Bacteria identified in Urine by Culture^LN|1|112283007^Escherichia coli^SCT||||||F|||20260509120000
OBX|2|ST|18907-6^Ampicillin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|>32|mg/L||||R|||F|||20260509123000
OBX|3|ST|18928-2^Gentamicin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|0.5|mg/L||||S|||F|||20260509123000
OBX|4|ST|18932-4^Ciprofloxacin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|0.25|mg/L||||S|||F|||20260509123000
OBX|5|ST|18862-3^Amoxicillin+Clavulanate [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|4|mg/L||||S|||F|||20260509123000
OBX|6|ST|18996-9^Nitrofurantoin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|16|mg/L||||S|||F|||20260509123000
OBX|7|ST|6652-2^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|1|0.03|mg/L||||S|||F|||20260509123000
NTE|1||Kweek >10^5 KVE/mL. Monomicrobieel. Resistentie conform EUCAST.
```

---

## 9. ORU^R01 - coagulation panel result (stollingsonderzoek)

```
MSH|^~\&|GLIMS|ETZ_LAB|HIS|ETZ|20260509140000||ORU^R01^ORU_R01|MSG20260509009|P|2.5|||AL|NE|NLD|8859/1
PID|||753108642^^^NLMINBIZA^NNNLD~PAT006^^^ETZ^PI||van der Heijden^Cornelia^G^^^Mevr.||19450817|F|||Spoorlaan 25^^Tilburg^^5038CB^NLD^H||^^PH^0134627100
PV1||O|POLI HEM^Hematologie^1||||70060^Timmermans^Jacobus^^^Prof.Dr.^arts
ORC|RE|ORD2026006
OBR|1|ORD2026006||LA11803-5^Coagulation panel^LN|||20260509120000|||||||||||||||20260509140000|||F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||13.5|s^s^UCUM|11.0-15.0|N|||F|||20260509133000
OBX|2|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||1.1|{INR}^{INR}^UCUM|0.9-1.2|N|||F|||20260509133000
OBX|3|NM|3173-2^aPTT in Platelet poor plasma by Coagulation assay^LN||31|s^s^UCUM|25-38|N|||F|||20260509133000
OBX|4|NM|3255-7^Fibrinogen [Mass/volume] in Platelet poor plasma by Coagulation assay^LN||3.2|g/L^g/L^UCUM|2.0-4.0|N|||F|||20260509133000
OBX|5|NM|3174-0^D-dimer DDU [Mass/volume] in Platelet poor plasma^LN||0.35|mg/L^mg/L^UCUM|<0.50|N|||F|||20260509133000
```

---

## 10. ORU^R01 - endocrinology panel (schildklierfunctie)

```
MSH|^~\&|GLIMS|UMCG_LAB|HIS|UMCG|20260509143000||ORU^R01^ORU_R01|MSG20260509010|P|2.5|||AL|NE|NLD|8859/1
PID|||912345678^^^NLMINBIZA^NNNLD~PAT007^^^UMCG^PI||Veenstra^Maria^K^^^Mevr.||19620124|F|||Oosterstraat 22^^Groningen^^9711NR^NLD^H||^^PH^0503124567
PV1||O|POLI END^Endocrinologie^1||||80070^Boersma^Adriaan^^^Prof.Dr.^arts
ORC|RE|ORD2026007
OBR|1|ORD2026007||55231-5^Thyroid panel - Serum or Plasma^LN|||20260509130000|||||||||||||||20260509143000|||F
OBX|1|NM|3016-3^Thyrotropin [Units/volume] in Serum or Plasma^LN||2.8|mU/L^mU/L^UCUM|0.4-4.0|N|||F|||20260509141000
OBX|2|NM|3026-2^Thyroxine (T4) free [Mass/volume] in Serum or Plasma^LN||15.2|pmol/L^pmol/L^UCUM|11.0-22.0|N|||F|||20260509141000
OBX|3|NM|3053-6^Triiodothyronine (T3) free [Mass/volume] in Serum or Plasma^LN||4.8|pmol/L^pmol/L^UCUM|3.1-6.8|N|||F|||20260509141000
OBX|4|NM|5385-0^Thyroid peroxidase Ab [Units/volume] in Serum^LN||12|kU/L^kU/L^UCUM|<34|N|||F|||20260509141000
```

---

## 11. OUL^R22 - Lab2Lab result with rapid test (sneltest resultaat)

```
MSH|^~\&|305|OLVG_LAB|912|RIVM_IDS|20260509150000||OUL^R22^OUL_R22|MSG20260509011|P|2.5|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.32^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
PID|||481623957^^^NLMINBIZA^NNNLD~PAT008^^^OLVG^PI||Hendriks^Jan^R^^^Dhr.||19880201|M|||Javastraat 100^^Amsterdam^^1094HG^NLD^H
PV1||E|SEH^Spoedeisende Hulp^1
SPM|1|||NAS^Nasopharyngeal swab^HL70487|||||||||||||20260509143000|20260509143500
OBR|1|ORD2026008||94500-6^SARS-CoV-2 RNA NAA+probe Ql (Resp)^LN|||20260509143500|||||||||||||||20260509150000|||F
ORC|RE|ORD2026008||||||20260509150000
OBX|1|CWE|94500-6^SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection^LN||260415000^Not detected^SCT||||||F|||20260509145500
NTE|1||Sneltest PCR methode, GeneXpert Xpress SARS-CoV-2. Detectielimiet 250 kopieën/mL.
```

---

## 12. ORU^R01 - Lab2PublicHealth notification (meldingsplichtig)

```
MSH|^~\&|GLIMS|UMCU_LAB|OSIRIS|RIVM|20260509160000||ORU^R01^ORU_R01|MSG20260509012|P|2.5|||AL|NE|NLD|8859/1
PID|||294817365^^^NLMINBIZA^NNNLD||Wolters^Hendrik^P^^^Dhr.||19430512|M|||Catharijnesingel 77^^Utrecht^^3511GE^NLD^H
PV1||I|IC^Intensive Care^Bed 5||||90080^Scholten^Adriana^^^Dr.^arts
ORC|RE|ORD2026009
OBR|1|ORD2026009||20897-4^Legionella pneumophila Ag [Presence] in Urine^LN|||20260509140000|||||||||||||||20260509160000|||F
OBX|1|CWE|20897-4^Legionella pneumophila Ag [Presence] in Urine^LN||260373001^Detected^SCT||||||F|||20260509155000
OBX|2|TX|8251-1^Service comment^LN||Meldingsplichtig conform Wet publieke gezondheid groep B2. GGD en RIVM zijn geïnformeerd.||||||F
NTE|1||Bepaling uitgevoerd met BinaxNOW Legionella immunochromatografische assay.
```

---

## 13. ORU^R01 - blood gas analysis result (arterieel bloedgas)

```
MSH|^~\&|GLIMS|MST_LAB|HIS|MST|20260509162000||ORU^R01^ORU_R01|MSG20260509013|P|2.5|||AL|NE|NLD|8859/1
PID|||618273945^^^NLMINBIZA^NNNLD~PAT009^^^MST^PI||Dijkstra^Jacobus^N^^^Dhr.||19580831|M|||Oldenzaalsestraat 55^^Enschede^^7511DV^NLD^H
PV1||I|IC^Intensive Care^Bed 2||||11090^Mulder^Anneke^^^Dr.^arts
ORC|RE|ORD2026010
OBR|1|ORD2026010||24336-0^Gas panel - Arterial blood^LN|||20260509155000|||||||||||||||20260509162000|||F
OBX|1|NM|2744-1^pH of Arterial blood^LN||7.38||7.35-7.45|N|||F|||20260509160000
OBX|2|NM|2019-8^Carbon dioxide [Partial pressure] in Arterial blood^LN||42|mm[Hg]^mm[Hg]^UCUM|35-45|N|||F|||20260509160000
OBX|3|NM|2703-7^Oxygen [Partial pressure] in Arterial blood^LN||88|mm[Hg]^mm[Hg]^UCUM|75-100|N|||F|||20260509160000
OBX|4|NM|1959-6^Bicarbonate [Moles/volume] in Arterial blood^LN||24.5|mmol/L^mmol/L^UCUM|22.0-26.0|N|||F|||20260509160000
OBX|5|NM|2708-6^Oxygen saturation in Arterial blood^LN||96|%^%^UCUM|95-100|N|||F|||20260509160000
OBX|6|NM|2714-4^Base excess in Arterial blood by calculation^LN||0.8|mmol/L^mmol/L^UCUM|-2.0-3.0|N|||F|||20260509160000
OBX|7|NM|59274-1^Lactate [Moles/volume] in Arterial blood^LN||1.2|mmol/L^mmol/L^UCUM|0.5-2.2|N|||F|||20260509160000
```

---

## 14. ORU^R01 - urinalysis result (urineonderzoek)

```
MSH|^~\&|GLIMS|AMPHIA_LAB|HIS|AMPHIA|20260509170000||ORU^R01^ORU_R01|MSG20260509014|P|2.5|||AL|NE|NLD|8859/1
PID|||537294816^^^NLMINBIZA^NNNLD~PAT010^^^AMPHIA^PI||Vermeulen^Elisabeth^C^^^Mevr.||19750929|F|||Ginnekenweg 12^^Breda^^4835NA^NLD^H||^^PH^0765214389
PV1||O|POLI NEF^Nefrologie^1||||12100^Peters^Theodorus^^^Dr.^arts
ORC|RE|ORD2026011
OBR|1|ORD2026011||24356-8^Urinalysis complete panel in Urine^LN|||20260509153000|||||||||||||||20260509170000|||F
OBX|1|NM|2756-5^pH of Urine by Test strip^LN||6.0||5.0-8.0|N|||F|||20260509163000
OBX|2|ST|20454-5^Protein [Presence] in Urine by Test strip^LN||Negatief||Negatief|N|||F|||20260509163000
OBX|3|ST|25428-4^Glucose [Presence] in Urine by Test strip^LN||Negatief||Negatief|N|||F|||20260509163000
OBX|4|NM|30405-5^Leukocytes [#/area] in Urine sediment by Microscopy high power field^LN||3|/[HPF]^/[HPF]^UCUM|0-5|N|||F|||20260509163000
OBX|5|NM|13945-1^Erythrocytes [#/area] in Urine sediment by Microscopy high power field^LN||1|/[HPF]^/[HPF]^UCUM|0-3|N|||F|||20260509163000
OBX|6|ST|5811-5^Specific gravity of Urine by Test strip^LN||1.018||1.005-1.030|N|||F|||20260509163000
```

---

## 15. OML^O21 - order with patient weight/height context (eGFR berekening)

```
MSH|^~\&|103|MAASTRICHT_LAB|202|ERASMUS_LAB|20260509171500||OML^O21^OML_O21|MSG20260509015|P|2.5|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.31^Nictiz^2.16.840.1.113883.2.4.3.11^ISO
PID|||462918375^^^NLMINBIZA^NNNLD~PAT011^^^MUMC^PI||Claessen^Petrus^H^^^Dhr.||19681104|M|||Vrijthof 3^^Maastricht^^6211LE^NLD^H
PV1||I|5B^Nefrologie^Bed 6||||13110^Gielen^Margaretha^^^Dr.^arts
ORC|NW|ORD2026012|||||^^^20260509171500^^R||20260509171500
OBR|1|ORD2026012||2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN|||20260509165000||||A
OBX|1|NM|29463-7^Body weight^LN||82.5|kg^kg^UCUM|||||F
OBX|2|NM|8302-2^Body height^LN||178|cm^cm^UCUM|||||F
OBX|3|TX|46239-0^Chief complaint^LN||Controle nierfunctie, chronische nierinsufficiëntie stadium 3||||||F
SPM|1|||SER^Serum^HL70487|||||||||||||20260509165000|20260509165500
```

---

## 16. ORU^R01 - HbA1c and glucose result (diabetes controle)

```
MSH|^~\&|GLIMS|CATHARINA_LAB|HIS|CATHARINA|20260509174500||ORU^R01^ORU_R01|MSG20260509016|P|2.5|||AL|NE|NLD|8859/1
PID|||183746529^^^NLMINBIZA^NNNLD~PAT012^^^CATHARINA^PI||Willems^Johanna^B^^^Mevr.||19550320|F|||Gestelsestraat 2^^Eindhoven^^5615LC^NLD^H||^^PH^0402389156
PV1||O|POLI INT^Interne Geneeskunde^1||||14120^van Oort^Paulus^^^Dr.^arts
ORC|RE|ORD2026013
OBR|1|ORD2026013||4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20260509160000|||||||||||||||20260509174500|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||52|mmol/mol^mmol/mol^UCUM|<53|N|||F|||20260509172000
OBX|2|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||7.2|mmol/L^mmol/L^UCUM|3.1-6.1|H|||F|||20260509172000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||95|umol/L^umol/L^UCUM|62-106|N|||F|||20260509172000
OBX|4|NM|62238-1^Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI 2021)^LN||68|mL/min/1.73m2^mL/min/1.73m2^UCUM|>60|N|||F|||20260509172000
```

---

## 17. ORU^R01 - toxicology/therapeutic drug monitoring result

```
MSH|^~\&|GLIMS|UMCU_LAB|HIS|UMCU|20260509180000||ORU^R01^ORU_R01|MSG20260509017|P|2.5|||AL|NE|NLD|8859/1
PID|||729461835^^^NLMINBIZA^NNNLD~PAT013^^^UMCU^PI||Brouwer^Adriaan^J^^^Dhr.||19401212|M|||Heidelberglaan 100^^Utrecht^^3584CX^NLD^H
PV1||I|2N^Neurologie^Bed 11||||15130^ter Haar^Margaretha^^^Dr.^arts
ORC|RE|ORD2026014
OBR|1|ORD2026014||4090-7^Valproate [Mass/volume] in Serum or Plasma^LN|||20260509163000|||||||||||||||20260509180000|||F
OBX|1|NM|4090-7^Valproate [Mass/volume] in Serum or Plasma^LN||72|mg/L^mg/L^UCUM|50-100|N|||F|||20260509174500
OBX|2|TX|8251-1^Service comment^LN||Dalconcentratie. Therapeutisch bereik valproïnezuur: 50-100 mg/L. Concentratie passend bij adequate dosering.||||||F
```

---

## 18. ORU^R01 - blood bank/transfusion result (bloedgroeptypering)

```
MSH|^~\&|GLIMS|SANQUIN_LAB|HIS|AMC|20260509183000||ORU^R01^ORU_R01|MSG20260509018|P|2.5|||AL|NE|NLD|8859/1
PID|||351849627^^^NLMINBIZA^NNNLD~PAT014^^^AMC^PI||van Dijk^Grietje^S^^^Mevr.||19830714|F|||Meibergdreef 9^^Amsterdam^^1105AZ^NLD^H
PV1||I|3A^Chirurgie^Bed 4||||16140^Jansen^Frederikus^^^Dr.^arts
ORC|RE|ORD2026015
OBR|1|ORD2026015||882-1^ABO and Rh group [Type] in Blood^LN|||20260509170000|||||||||||||||20260509183000|||F
OBX|1|CWE|883-9^ABO group [Type] in Blood^LN||278149003^Blood group A^SCT||||||F|||20260509180000
OBX|2|CWE|10331-7^Rh [Type] in Blood^LN||165747007^RhD positive^SCT||||||F|||20260509180000
OBX|3|CWE|1250-0^Direct antiglobulin test.IgG specific reagent [Interpretation] in Blood^LN||260385009^Negative^SCT||||||F|||20260509181000
OBX|4|ST|890-4^Ab screen [Presence] in Serum or Plasma^LN||Negatief||||||F|||20260509181500
```

---

## 19. ORU^R01 - lab result with embedded PDF report (base64-encoded cumulative report)

```
MSH|^~\&|GLIMS|RADBOUD_LAB|HIS|RADBOUDUMC|20260509190000||ORU^R01^ORU_R01|MSG20260509019|P|2.5|||AL|NE|NLD|8859/1
PID|||842916375^^^NLMINBIZA^NNNLD~PAT015^^^RADBOUD^PI||Hermsen^Gerardus^T^^^Dhr.||19470305|M|||Geert Grooteplein 10^^Nijmegen^^6525GA^NLD^H
PV1||I|6B^Oncologie^Bed 7||||17150^van den Broek^Suzanne^^^Prof.Dr.^arts
ORC|RE|ORD2026016
OBR|1|ORD2026016||58410-2^CBC panel - Blood by Automated count^LN|||20260509173000|||||||||||||||20260509190000|||F
OBX|1|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||6.1|mmol/L^mmol/L^UCUM|7.5-10.0|L|||F|||20260509183000
OBX|2|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||2.1|10*9/L^10*9/L^UCUM|4.0-10.0|L|||F|||20260509183000
OBX|3|NM|26515-7^Platelets [#/volume] in Blood by Automated count^LN||89|10*9/L^10*9/L^UCUM|150-400|L|||F|||20260509183000
OBX|4|ED|PDF^Display format in PDF^AUSPDI||GLIMS^Application^PDF^Base64^JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMTMgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihSYWRib3VkdW1jIExhYm9yYXRvcml1bSkgVGoKMTAwIDY4MCBUZAooQ3VtdWxhdGlldiBMYWJvdmVyemljaHQpIFRqCjEwMCA2NjAgVGQKKFBhdGllbnQ6IFdpbGxlbXMsIEcuSC4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY2IDAwMDAwIG4gCjAwMDAwMDAxMjUgMDAwMDAgbiAKMDAwMDAwMDMwMiAwMDAwMCBuIAowMDAwMDAwNDY3IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTU2CiUlRU9GCg==||||||F
```

---

## 20. ORU^R01 - pathology result with embedded JPEG image (histologie microscoopfoto)

```
MSH|^~\&|GLIMS|LUMC_PATHOLOGIE|HIS|LUMC|20260509193000||ORU^R01^ORU_R01|MSG20260509020|P|2.5|||AL|NE|NLD|8859/1
PID|||275839164^^^NLMINBIZA^NNNLD~PAT016^^^LUMC^PI||de Groot^Wilhelmina^A^^^Mevr.||19580611|F|||Rapenburg 2^^Leiden^^2311EW^NLD^H
PV1||I|4C^Pathologie^Bed 2||||18160^Vos^Cornelis^^^Prof.Dr.^arts
ORC|RE|ORD2026017
OBR|1|ORD2026017||33717-0^Pathology study^LN|||20260508100000|||||||||||||||20260509193000|||F
OBX|1|FT|22637-3^Pathology report final diagnosis^LN||Colonbiopt: adenocarcinoom, matig gedifferentieerd (G2), invasie in submucosa.\.br\Resectievlakken vrij. Lymfangioinvasie afwezig.\.br\Conclusie: pT1 NX MX coloncarcinoom.||||||F|||20260509190000
OBX|2|ED|IMGHL7^Histopathology image^L||LUMC_PATHOLOGIE^Image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBX/2wBDAQMEBAUEBQkFBQkVDQsNFRUVFRUVFRUV FQUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRX/wAARCAAoACgDASIAAhEBAxEB/8QA HwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR BRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdI SUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXp/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJ Cgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVi ctEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqC g4SFhoeIiYqSk5SVlpeYmZqio6SlpqeoqaqyS7O0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk 5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD7yooooAKKKKACiiigD//Z||||||F|||20260509191500
NTE|1||Microscoopfoto HE-kleuring 40x vergroting, colonbiopt S2026-12345.
```

---
