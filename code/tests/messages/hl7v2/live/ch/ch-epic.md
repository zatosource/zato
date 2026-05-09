# Epic - real HL7v2 ER7 messages

---

## 1. ADT^A01 - admission d'un patient (inpatient admission)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|LABO|CHUV_LAUSANNE|20260301070000||ADT^A01^ADT_A01|EPIC00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301070000
PID|||MRN100001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR~7560111222333^^^&2.16.756.5.31&ISO^SS||Simon^Anne^Claude^^Mme||19750415|F|||Boulevard Helvetique 68^^Vernier^^1214^CH||^^PH^0223298752~^^CP^0771375557
PV1||I|MEDINTERNE^Chambre 301^Lit A^Médecine interne||||MED001^Richard^Madeleine^^^Dr.^méd.|MED002^Perrin^Yvonne^^^Dr.^méd.||||||||||||CAS00123|||||||||||||||||||||||||||20260301070000
IN1|1|LAMal|ASSURA001|Assura SA|Avenue Charles-Ferdinand Ramuz 70^^Pully^^1009^CH||||||||||||||||||||||||||||||||||||||||||||756.5678.9012.34
```

---

## 2. ADT^A02 - transfert de patient (patient transfer)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|LABO|CHUV_LAUSANNE|20260303090000||ADT^A02^ADT_A02|EPIC00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260303090000
PID|||MRN100001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Simon^Anne^Claude^^Mme||19750415|F|||Boulevard Helvetique 68^^Vernier^^1214^CH||^^PH^0223298752~^^CP^0771375557
PV1||I|CHIRURGIE^Chambre 405^Lit B^Chirurgie||||MED003^Andre^Thierry^^^Prof.^Dr.^méd.||||||||||||CAS00123||||||||||||||||||||||MEDINTERNE^Chambre 301^Lit A^Médecine interne||20260303090000
```

---

## 3. ADT^A03 - sortie du patient (discharge)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|LABO|CHUV_LAUSANNE|20260312150000||ADT^A03^ADT_A03|EPIC00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260312150000
PID|||MRN100001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Simon^Anne^Claude^^Mme||19750415|F|||Boulevard Helvetique 68^^Vernier^^1214^CH||^^PH^0223298752~^^CP^0771375557
PV1||I|CHIRURGIE^Chambre 405^Lit B^Chirurgie||||MED003^Andre^Thierry^^^Prof.^Dr.^méd.||||||||||||CAS00123|||||||||||||||||||||||||||20260312150000
```

---

## 4. ADT^A04 - inscription ambulatoire (outpatient registration)

```
MSH|^~\&|EPIC|HUG_GENEVE|POLICLINIQUE|HUG_GENEVE|20260315100000||ADT^A04^ADT_A01|EPIC00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||MRN200001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Durand^Raymond^Maurice^^M.||19681228|M|||Quai du Mont-Blanc 18^^Renens^^1020^CH||^^PH^0218770834~^^CP^0783039770
PV1||O|CONSULT^Salle 12^^Consultation||||MED004^Morin^Renee^^^Dr.^méd.||||||||||||CAS00456|||||||||||||||||||||||||||20260315100000
```

---

## 5. ADT^A08 - mise à jour patient (patient update)

```
MSH|^~\&|EPIC|HUG_GENEVE|MPI|HUG_GENEVE|20260318110000||ADT^A08^ADT_A01|EPIC00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||MRN200001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Durand^Raymond^Maurice^^M.||19681228|M|||Quai du Mont-Blanc 18^^Renens^^1020^CH||^^PH^0218770834~^^CP^0783039770~^^Internet^raymond.durand@netplus.ch
PV1||O|CONSULT^Salle 12^^Consultation||||MED004^Morin^Renee^^^Dr.^méd.||||||||||||CAS00456|||||||||||||||||||||||||||20260318110000
IN1|1|LAMal|VISANA001|Visana AG|Weltpoststrasse 19^^Bern^^3015^CH||||||||||||||||||||||||||||||||||||||||||||756.8765.4321.09
```

---

## 6. ORM^O01 - ordre de laboratoire (laboratory order)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|LABOSYS|CHUV_LAUSANNE|20260320083000||ORM^O01^ORM_O01|EPIC00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN300001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Moreau^Luc^Madeleine^^M.||19550310|M|||Avenue de France 153^^Nyon^^1260^CH||^^CP^0793789273
PV1||I|MEDINTERNE^Chambre 210^Lit A^Médecine interne||||MED005^Garnier^Denise^^^Dr.^méd.||||||||||||CAS00789
ORC|NW|ORD001^^^EPIC|||||^^^20260320090000^^R||20260320083000|MED005^Garnier^Denise^^^Dr.^méd.
OBR|1|ORD001^^^EPIC||24323-8^Bilan hépatique complet^LN|||20260320083000||||A|||||MED005^Garnier^Denise^^^Dr.^méd.
```

---

## 7. ORU^R01 - résultats de laboratoire (laboratory results)

```
MSH|^~\&|LABOSYS|CHUV_LAUSANNE|EPIC|CHUV_LAUSANNE|20260320160000||ORU^R01^ORU_R01|LAB00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN300001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Moreau^Luc^Madeleine^^M.||19550310|M|||Avenue de France 153^^Nyon^^1260^CH||^^CP^0793789273
PV1||I|MEDINTERNE^Chambre 210^Lit A^Médecine interne||||MED005^Garnier^Denise^^^Dr.^méd.||||||||||||CAS00789
OBR|1|ORD001^^^EPIC|RES001^^^LABOSYS|24323-8^Bilan hépatique complet^LN|||20260320083000|||||||||MED005^Garnier^Denise^^^Dr.^méd.||||||20260320160000|||F
OBX|1|NM|1742-6^ALAT (GPT)^LN||35|U/L|7-56|N|||F
OBX|2|NM|1920-8^ASAT (GOT)^LN||28|U/L|10-40|N|||F
OBX|3|NM|6768-6^Phosphatase alcaline^LN||72|U/L|44-147|N|||F
OBX|4|NM|1975-2^Bilirubine totale^LN||12|umol/L|3-22|N|||F
OBX|5|NM|1751-7^Albumine^LN||42|g/L|34-54|N|||F
```

---

## 8. ORU^R01 - rapport de laboratoire PDF (lab report with embedded PDF)

```
MSH|^~\&|LABOSYS|CHUV_LAUSANNE|EPIC|CHUV_LAUSANNE|20260321110000||ORU^R01^ORU_R01|LAB00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN400001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Gautier^Brigitte^Therese^^Mme||19821203|F|||Rue de la Servette 53^^Bulle^^1630^CH||^^CP^0761606448
PV1||O|CONSULT^Salle 4^^Hématologie||||MED006^Henry^Roger^^^Dr.^méd.||||||||||||CAS01234
OBR|1|ORD002^^^EPIC|RES002^^^LABOSYS|58410-2^Formule sanguine complète^LN|||20260321090000|||||||||MED006^Henry^Roger^^^Dr.^méd.||||||20260321110000|||F
OBX|1|ED|58410-2^Formule sanguine complète^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEZvcm11bGUgc2FuZ3VpbmUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ0CiUlRU9GCg==||||||F
```

---

## 9. MDM^T02 - lettre de sortie (discharge letter with embedded document)

```
MSH|^~\&|EPIC|HUG_GENEVE|ARCHIVDOC|HUG_GENEVE|20260322140000||MDM^T02^MDM_T02|EPIC00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||MRN200001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Durand^Raymond^Maurice^^M.||19681228|M|||Quai du Mont-Blanc 18^^Renens^^1020^CH||^^CP^0783039770
PV1||I|CHIRURGIE^Chambre 302^Lit A^Chirurgie||||MED007^Roussel^Philippe^^^Dr.^méd.||||||||||||CAS01456
TXA|1|DS|AP|20260322140000|MED007^Roussel^Philippe^^^Dr.^méd.||||||||DOC789012||||||AU
OBX|1|ED|11490-0^Lettre de sortie^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExldHRyZSBkZSBzb3J0aWUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ2CiUlRU9GCg==||||||F
```

---

## 10. SIU^S12 - rendez-vous planifié (appointment scheduling)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|AGENDA|CHUV_LAUSANNE|20260401090000||SIU^S12^SIU_S12|EPIC00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|RDV001^^^EPIC|||||ROUTINE^Routine^HL70276|CONSULT^Consultation^HL70277|30|MIN|^^30^20260415100000^20260415103000|MED005^Garnier^Denise^^^Dr.^méd.
PID|||MRN300001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Moreau^Luc^Madeleine^^M.||19550310|M|||Avenue de France 153^^Nyon^^1260^CH||^^CP^0793789273
PV1||O|CONSULT^Salle 8^^Consultation||||MED005^Garnier^Denise^^^Dr.^méd.
RGS|1
AIS|1|A|CONSULT^Consultation|||20260415100000|30|MIN
AIL|1|A|CONSULT^Salle 8^^Consultation
AIP|1|A|MED005^Garnier^Denise^^^Dr.^méd.
```

---

## 11. ORM^O01 - ordre de radiologie (radiology order)

```
MSH|^~\&|EPIC|HUG_GENEVE|RIS|HUG_GENEVE|20260402110000||ORM^O01^ORM_O01|EPIC00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN500001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Roux^Yves^Jean^^M.||19721014|M|||Rue de la Gare 75^^Martigny^^1920^CH||^^CP^0792154580
PV1||E|URG^Box 3^^Urgences||||MED008^Robert^Suzanne^^^Dr.^méd.||||||||||||CAS02345
ORC|NW|ORD100^^^EPIC|||||^^^20260402120000^^S||20260402110000|MED008^Robert^Suzanne^^^Dr.^méd.
OBR|1|ORD100^^^EPIC||36643-5^CT Thorax avec contraste^LN|||20260402110000||||A|||||MED008^Robert^Suzanne^^^Dr.^méd.|||CT||||||||||TRAUMA
```

---

## 12. ORU^R01 - résultats de microbiologie (microbiology results)

```
MSH|^~\&|MICROBIO|HUG_GENEVE|EPIC|HUG_GENEVE|20260403160000||ORU^R01^ORU_R01|MIC00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN500001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Roux^Yves^Jean^^M.||19721014|M|||Rue de la Gare 75^^Martigny^^1920^CH||^^CP^0792154580
PV1||E|URG^Box 3^^Urgences||||MED008^Robert^Suzanne^^^Dr.^méd.||||||||||||CAS02345
OBR|1|ORD101^^^EPIC|RES101^^^MICROBIO|87040^Hémoculture^LN|||20260403060000|||||||||MED008^Robert^Suzanne^^^Dr.^méd.||||||20260403160000|||F
OBX|1|ST|600-7^Micro-organisme identifié^LN||Escherichia coli||||||F
OBX|2|ST|18906-8^Ampicilline^LN||R||||||F
OBX|3|ST|18928-2^Gentamicine^LN||S||||||F
OBX|4|ST|18955-5^Ciprofloxacine^LN||S||||||F
```

---

## 13. ADT^A31 - mise à jour personne (update person information)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|MPI|CHUV_LAUSANNE|20260405120000||ADT^A31^ADT_A05|EPIC00013|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260405120000
PID|||MRN100001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR~7560111222333^^^&2.16.756.5.31&ISO^SS||Simon^Anne^Claude^^Mme||19750415|F|||Boulevard Helvetique 68^^Vernier^^1214^CH||^^PH^0223298752~^^CP^0771375557~^^Internet^anne.simon@sunrise.ch
PV1||N
```

---

## 14. ADT^A40 - fusion de patients (patient merge)

```
MSH|^~\&|EPIC|HUG_GENEVE|MPI|HUG_GENEVE|20260406080000||ADT^A40^ADT_A39|EPIC00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260406080000
PID|||MRN200001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Durand^Raymond^Maurice^^M.||19681228|M|||Quai du Mont-Blanc 18^^Renens^^1020^CH||^^CP^0783039770
MRG|MRN299999^^^HUG&2.16.756.5.30.1.146.1&ISO^MR
```

---

## 15. ORU^R01 - résultat de chimie clinique (clinical chemistry result)

```
MSH|^~\&|CHIMIE|CHUV_LAUSANNE|EPIC|CHUV_LAUSANNE|20260407150000||ORU^R01^ORU_R01|CHIM00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN600001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Morel^Francois^Renee^^M.||19490520|M|||Avenue de la Gare 198^^Carouge^^1227^CH||^^PH^0227558410
PV1||I|CARDIO^Chambre 501^Lit A^Cardiologie||||MED009^Duval^Henri^^^Prof.^Dr.^méd.||||||||||||CAS03456
OBR|1|ORD200^^^EPIC|RES200^^^CHIMIE|2160-0^Créatinine sérique^LN|||20260407090000|||||||||MED009^Duval^Henri^^^Prof.^Dr.^méd.||||||20260407150000|||F
OBX|1|NM|2160-0^Créatinine^LN||112|umol/L|62-106|H|||F
OBX|2|NM|3094-0^Urée^LN||8.5|mmol/L|2.8-7.2|H|||F
OBX|3|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F
OBX|4|NM|2951-2^Sodium^LN||139|mmol/L|136-145|N|||F
```

---

## 16. ADT^A11 - annulation d'admission (cancel admit)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|LABO|CHUV_LAUSANNE|20260408070000||ADT^A11^ADT_A09|EPIC00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260408070000
PID|||MRN700001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Dubois^Alain^Andre^^M.||19880612|M|||Rue du Marche 173^^Morges^^1110^CH||^^CP^0767993202
PV1||I|CHIRURGIE^Chambre 201^Lit A^Chirurgie||||MED003^Andre^Thierry^^^Prof.^Dr.^méd.||||||||||||CAS04567|||||||||||||||||||||||||||20260408070000
```

---

## 17. ORU^R01 - résultats d'hématologie (hematology results)

```
MSH|^~\&|HEMATO|HUG_GENEVE|EPIC|HUG_GENEVE|20260409140000||ORU^R01^ORU_R01|HEM00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN800001^^^HUG&2.16.756.5.30.1.146.1&ISO^MR||Legrand^Pauline^Jean^^Mme||19630817|F|||Avenue de Cour 38^^Morges^^1110^CH||^^PH^0211190117
PV1||I|HEMATO^Chambre 605^Lit A^Hématologie||||MED010^Mercier^Agnes^^^Prof.^Dr.^méd.||||||||||||CAS05678
OBR|1|ORD300^^^EPIC|RES300^^^HEMATO|57021-8^Formule leucocytaire^LN|||20260409080000|||||||||MED010^Mercier^Agnes^^^Prof.^Dr.^méd.||||||20260409140000|||F
OBX|1|NM|718-7^Hémoglobine^LN||98|g/L|120-160|L|||F
OBX|2|NM|6690-2^Leucocytes^LN||12.5|10*9/L|4.0-10.0|H|||F
OBX|3|NM|789-8^Thrombocytes^LN||180|10*9/L|150-400|N|||F
OBX|4|NM|4544-3^Hématocrite^LN||0.31|L/L|0.36-0.46|L|||F
```

---

## 18. ADT^A28 - nouvelle personne (add person information)

```
MSH|^~\&|EPIC|CHUV_LAUSANNE|MPI|CHUV_LAUSANNE|20260410080000||ADT^A28^ADT_A05|EPIC00018|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260410080000
PID|||MRN900001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR~7569012345678^^^&2.16.756.5.31&ISO^SS||Masson^Gerard^Pierre^^M.||19950718|M|||Rue Neuve 141^^Sion^^1950^CH||^^CP^0779983319~^^Internet^gerard.masson@gmail.com
PV1||N
```

---

## 19. ORU^R01 - résultat de pathologie (pathology result)

```
MSH|^~\&|PATHO|CHUV_LAUSANNE|EPIC|CHUV_LAUSANNE|20260411110000||ORU^R01^ORU_R01|PATH00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||MRN300001^^^CHUV&2.16.756.5.30.1.145.1&ISO^MR||Moreau^Luc^Madeleine^^M.||19550310|M|||Avenue de France 153^^Nyon^^1260^CH||^^CP^0793789273
PV1||I|CHIRURGIE^Chambre 308^Lit A^Chirurgie||||MED003^Andre^Thierry^^^Prof.^Dr.^méd.||||||||||||CAS06789
OBR|1|ORD400^^^EPIC|RES400^^^PATHO|88305^Examen histopathologique^CPT|||20260410140000|||||||||MED003^Andre^Thierry^^^Prof.^Dr.^méd.||||||20260411110000|||F
OBX|1|FT|22637-3^Rapport de pathologie^LN||Macroscopie: Pièce de résection colique, 18 cm\.br\Microscopie: Adénocarcinome colique modérément différencié\.br\Invasion pariétale: Sous-séreuse (pT3)\.br\Ganglions: 2/18 positifs (pN1a)\.br\Marges de résection libres\.br\Classification: pT3 pN1a M0, stade IIIB||||||F
```

---

## 20. ACK - accusé de réception (acknowledgment)

```
MSH|^~\&|LABO|CHUV_LAUSANNE|EPIC|CHUV_LAUSANNE|20260412080100||ACK^A01^ACK|ACK00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|EPIC00001|Message traité avec succès
```
