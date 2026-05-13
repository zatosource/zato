# Enovacom Integration Engine - real HL7v2 ER7 messages

---

## 1. ADT^A01 - admission du patient (inpatient admission)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260301080000||ADT^A01^ADT_A01|ENOV00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301080000
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR~7560666777888^^^&2.16.756.5.31&ISO^SS||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819~^^CP^0794670523
PV1||I|MEDINTERNE^Chambre 201^Lit A^Médecine interne||||MED500^Dubois^Denise^^^Dr.^méd.||||||||||||CAS50001|||||||||||||||||||||||||||20260301080000
IN1|1|LAMal|GROUPE_MUTUEL001|Groupe Mutuel|Rue du Nord 5^^Martigny^^1920^CH||||||||||||||||||||||||||||||||||||||||||||756.4444.5555.66
```

---

## 2. ADT^A03 - sortie du patient (discharge)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260310140000||ADT^A03^ADT_A03|ENOV00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260310140000
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819
PV1||I|MEDINTERNE^Chambre 201^Lit A^Médecine interne||||MED500^Dubois^Denise^^^Dr.^méd.||||||||||||CAS50001|||||||||||||||||||||||||||20260310140000
```

---

## 3. ADT^A04 - inscription ambulatoire (outpatient registration)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260315100000||ADT^A04^ADT_A01|ENOV00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||PAT900002^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Boyer^Nathalie^Claude^^Mme||19780330|F|||Boulevard Helvetique 196^^Renens^^1020^CH||^^CP^0796771784
PV1||O|CONSULT^Salle 5^^Consultation||||MED501^Guerin^Brigitte^^^Dr.^méd.||||||||||||CAS50002|||||||||||||||||||||||||||20260315100000
```

---

## 4. ADT^A08 - mise à jour patient (patient update)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260318110000||ADT^A08^ADT_A01|ENOV00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819~^^CP^0794670523~^^Internet^claude.gautier@gmail.com
PV1||N
```

---

## 5. ORM^O01 - ordre de laboratoire (laboratory order)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260320083000||ORM^O01^ORM_O01|ENOV00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900003^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Garnier^Vincent^Paul^^M.||19550620|M|||Rue Neuve 149^^Morges^^1110^CH||^^CP^0788284820
PV1||I|CHIRURGIE^Chambre 305^Lit A^Chirurgie||||MED502^Petit^Sylvie^^^Dr.^méd.||||||||||||CAS50003
ORC|NW|ORD900^^^HIS_SRC|||||^^^20260320090000^^R||20260320083000|MED502^Petit^Sylvie^^^Dr.^méd.
OBR|1|ORD900^^^HIS_SRC||CBC^Formule sanguine complète^LN|||20260320083000||||A|||||MED502^Petit^Sylvie^^^Dr.^méd.
```

---

## 6. ORU^R01 - résultats de laboratoire (laboratory results)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260320150000||ORU^R01^ORU_R01|ENOV00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900003^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Garnier^Vincent^Paul^^M.||19550620|M|||Rue Neuve 149^^Morges^^1110^CH||^^CP^0788284820
PV1||I|CHIRURGIE^Chambre 305^Lit A^Chirurgie||||MED502^Petit^Sylvie^^^Dr.^méd.||||||||||||CAS50003
OBR|1|ORD900^^^HIS_SRC|RES900^^^LABSYS|CBC^Formule sanguine complète^LN|||20260320083000|||||||||MED502^Petit^Sylvie^^^Dr.^méd.||||||20260320150000|||F
OBX|1|NM|718-7^Hémoglobine^LN||128|g/L|135-175|L|||F
OBX|2|NM|6690-2^Leucocytes^LN||9.5|10*9/L|4.0-10.0|N|||F
OBX|3|NM|789-8^Thrombocytes^LN||195|10*9/L|150-400|N|||F
OBX|4|NM|17861-6^CRP^LN||32|mg/L|0-5|HH|||F
```

---

## 7. ORU^R01 - rapport avec PDF intégré (result with embedded PDF)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260321110000||ORU^R01^ORU_R01|ENOV00007|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819
PV1||I|MEDINTERNE^Chambre 201^Lit A^Médecine interne||||MED500^Dubois^Denise^^^Dr.^méd.||||||||||||CAS50001
OBR|1|ORD901^^^HIS_SRC|RES901^^^LABSYS|11502-2^Rapport de laboratoire^LN|||20260321090000|||||||||MED500^Dubois^Denise^^^Dr.^méd.||||||20260321110000|||F
OBX|1|ED|11502-2^Rapport de laboratoire^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFJhcHBvcnQgZGUgbGFib3JhdG9pcmUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzUwCiUlRU9GCg==||||||F
```

---

## 8. MDM^T02 - lettre de sortie avec document (discharge letter with embedded PDF)

```
MSH|^~\&|ENOVACOM|INTEGRATION|ARCHIV|HOPITAL_SION|20260322140000||MDM^T02^MDM_T02|ENOV00008|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||PAT900002^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Boyer^Nathalie^Claude^^Mme||19780330|F|||Boulevard Helvetique 196^^Renens^^1020^CH||^^CP^0796771784
PV1||O|CONSULT^Salle 5^^Consultation||||MED501^Guerin^Brigitte^^^Dr.^méd.||||||||||||CAS50002
TXA|1|DS|AP|20260322140000|MED501^Guerin^Brigitte^^^Dr.^méd.||||||||DOC500001||||||AU
OBX|1|ED|11490-0^Lettre de sortie^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExldHRyZSBkZSBzb3J0aWUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzM4CiUlRU9GCg==||||||F
```

---

## 9. ORM^O01 - ordre de radiologie (radiology order)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260402110000||ORM^O01^ORM_O01|ENOV00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900003^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Garnier^Vincent^Paul^^M.||19550620|M|||Rue Neuve 149^^Morges^^1110^CH||^^CP^0788284820
PV1||I|CHIRURGIE^Chambre 305^Lit A^Chirurgie||||MED502^Petit^Sylvie^^^Dr.^méd.||||||||||||CAS50003
ORC|NW|ORD902^^^HIS_SRC|||||^^^20260402120000^^S||20260402110000|MED502^Petit^Sylvie^^^Dr.^méd.
OBR|1|ORD902^^^HIS_SRC||71020^Thorax 2 incidences^CPT|||20260402110000||||A|||||MED502^Petit^Sylvie^^^Dr.^méd.|||XRAY
```

---

## 10. ADT^A40 - fusion de patients (patient merge)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260405080000||ADT^A40^ADT_A39|ENOV00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260405080000
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819
MRG|PAT999888^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR
```

---

## 11. SIU^S12 - rendez-vous planifié (appointment scheduling)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260406090000||SIU^S12^SIU_S12|ENOV00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|RDV500^^^HIS_SRC|||||ROUTINE^Routine^HL70276|CONSULT^Consultation^HL70277|30|MIN|^^30^20260420100000^20260420103000|MED501^Guerin^Brigitte^^^Dr.^méd.
PID|||PAT900002^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Boyer^Nathalie^Claude^^Mme||19780330|F|||Boulevard Helvetique 196^^Renens^^1020^CH||^^CP^0796771784
PV1||O|CONSULT^Salle 5^^Consultation||||MED501^Guerin^Brigitte^^^Dr.^méd.
RGS|1
AIS|1|A|CONSULT^Consultation|||20260420100000|30|MIN
```

---

## 12. ADT^A02 - transfert de patient (patient transfer)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260407090000||ADT^A02^ADT_A02|ENOV00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260407090000
PID|||PAT900003^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Garnier^Vincent^Paul^^M.||19550620|M|||Rue Neuve 149^^Morges^^1110^CH||^^CP^0788284820
PV1||I|READAPT^Chambre 101^Lit A^Réadaptation||||MED503^Morin^Henri^^^Dr.^méd.||||||||||||CAS50003||||||||||||||||||||||CHIRURGIE^Chambre 305^Lit A^Chirurgie||20260407090000
```

---

## 13. ORU^R01 - résultats de chimie clinique (clinical chemistry results)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260408150000||ORU^R01^ORU_R01|ENOV00013|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819
PV1||I|MEDINTERNE^Chambre 201^Lit A^Médecine interne||||MED500^Dubois^Denise^^^Dr.^méd.||||||||||||CAS50001
OBR|1|ORD903^^^HIS_SRC|RES903^^^LABSYS|2160-0^Profil rénal^LN|||20260408090000|||||||||MED500^Dubois^Denise^^^Dr.^méd.||||||20260408150000|||F
OBX|1|NM|2160-0^Créatinine^LN||95|umol/L|62-106|N|||F
OBX|2|NM|3094-0^Urée^LN||6.2|mmol/L|2.8-7.2|N|||F
OBX|3|NM|2823-3^Potassium^LN||4.1|mmol/L|3.5-5.1|N|||F
OBX|4|NM|2951-2^Sodium^LN||138|mmol/L|136-145|N|||F
```

---

## 14. ADT^A31 - mise à jour personne (update person)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260409120000||ADT^A31^ADT_A05|ENOV00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260409120000
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR~7560666777888^^^&2.16.756.5.31&ISO^SS||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819~^^CP^0794670523~^^Internet^claude.gautier@gmail.com
PV1||N
```

---

## 15. ADT^A11 - annulation d'admission (cancel admit)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260410070000||ADT^A11^ADT_A09|ENOV00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260410070000
PID|||PAT900004^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Legrand^Yves^Sophie^^M.||19820915|M|||Chemin des Vignes 140^^Yverdon-les-Bains^^1400^CH||^^CP^0778752399
PV1||I|CHIRURGIE^Chambre 201^Lit A^Chirurgie||||MED502^Petit^Sylvie^^^Dr.^méd.||||||||||||CAS50004|||||||||||||||||||||||||||20260410070000
```

---

## 16. ORU^R01 - résultats de microbiologie (microbiology results)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260411160000||ORU^R01^ORU_R01|ENOV00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900003^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Garnier^Vincent^Paul^^M.||19550620|M|||Rue Neuve 149^^Morges^^1110^CH||^^CP^0788284820
PV1||I|READAPT^Chambre 101^Lit A^Réadaptation||||MED503^Morin^Henri^^^Dr.^méd.||||||||||||CAS50003
OBR|1|ORD904^^^HIS_SRC|RES904^^^LABSYS|87040^Hémoculture^LN|||20260411060000|||||||||MED503^Morin^Henri^^^Dr.^méd.||||||20260411160000|||F
OBX|1|ST|600-7^Micro-organisme identifié^LN||Pas de croissance après 5 jours||||||F
```

---

## 17. ADT^A28 - nouvelle personne (add person)

```
MSH|^~\&|HIS_SRC|HOPITAL_SION|ENOVACOM|INTEGRATION|20260412080000||ADT^A28^ADT_A05|ENOV00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260412080000
PID|||PAT900005^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR~7567890123456^^^&2.16.756.5.31&ISO^SS||Duval^Laure^Sophie^^Mme||19901205|F|||Avenue du Leman 106^^Renens^^1020^CH||^^CP^0784535774~^^Internet^laure.duval@gmail.com
PV1||N
```

---

## 18. ORU^R01 - résultat de pathologie (pathology result)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260413110000||ORU^R01^ORU_R01|ENOV00018|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900002^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Boyer^Nathalie^Claude^^Mme||19780330|F|||Boulevard Helvetique 196^^Renens^^1020^CH||^^CP^0796771784
PV1||O|CONSULT^Salle 5^^Consultation||||MED501^Guerin^Brigitte^^^Dr.^méd.||||||||||||CAS50002
OBR|1|ORD905^^^HIS_SRC|RES905^^^PATHO|88305^Examen histopathologique^CPT|||20260412140000|||||||||MED501^Guerin^Brigitte^^^Dr.^méd.||||||20260413110000|||F
OBX|1|FT|22637-3^Rapport de pathologie^LN||Macroscopie: Polype colique, 1.2 x 0.8 cm\.br\Microscopie: Adénome tubuleux à dysplasie de bas grade\.br\Résection complète\.br\Conclusion: Adénome tubuleux bénin, résection complète||||||F
```

---

## 19. ORU^R01 - coagulation (coagulation result)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_DST|HOPITAL_SION|20260414150000||ORU^R01^ORU_R01|ENOV00019|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT900001^^^HOPITAL_SION&2.16.756.5.30.1.190.1&ISO^MR||Gautier^Claude^Yvonne^^M.||19650812|M|||Place Saint-Francois 168^^Bulle^^1630^CH||^^PH^0262460819
PV1||I|MEDINTERNE^Chambre 201^Lit A^Médecine interne||||MED500^Dubois^Denise^^^Dr.^méd.||||||||||||CAS50001
OBR|1|ORD906^^^HIS_SRC|RES906^^^LABSYS|COAG^Bilan de coagulation^LN|||20260414090000|||||||||MED500^Dubois^Denise^^^Dr.^méd.||||||20260414150000|||F
OBX|1|NM|5902-2^Temps de prothrombine (Quick)^LN||88|%|70-120|N|||F
OBX|2|NM|6301-6^INR^LN||1.0||0.8-1.2|N|||F
OBX|3|NM|3173-2^aPTT^LN||30|s|25-37|N|||F
```

---

## 20. ACK - accusé de réception (acknowledgment)

```
MSH|^~\&|ENOVACOM|INTEGRATION|HIS_SRC|HOPITAL_SION|20260415080100||ACK^A01^ACK|ACK50001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|ENOV00001|Message traité avec succès
```
