# Epic (Netherlands) - real HL7v2 ER7 messages

## 1. ADT^A01 - Admit/visit notification (ICU admission)

```
MSH|^~\&|EPIC|UMCU|LAB_SYS|PATHOLOGY|202603011430||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||AL|NE
EVN|A01|202603011430|||ADMIN^Bakker^Johanna^^^RN
PID|1||MRN12345^^^UMCU^MR||van den Berg^Hendrik^Willem||19800115|M||2106-3^White^HL70005|Oudegracht 88^^Utrecht^UT^3511AB^NL||^PRN^PH^^^^^030-2345678||NLD^Dutch^HL70296|S^Single^HL70002||ACCT98765^^^UMCU^AN
PV1|1|I|ICU^0101^01^UMCU^^^^NURS|E^Emergency^HL70007|||ATT1234^de Groot^Anna^^^MD|REF5678^Visser^Karel^^^MD||MED^Medical^HL70069||||7|||ATT1234^de Groot^Anna^^^MD|IP^Inpatient^HL70004||||||||||||||||||UMCU||A|||202603011415
NK1|1|van den Berg^Cornelia^M|SPO^Spouse^HL70063|Oudegracht 88^^Utrecht^UT^3511AB|^PRN^PH^^^^^030-2345679
IN1|1|ZK001^Zilveren Kruis|ZK|Postbus 444^^Leiden^^2300AK|^WPN^PH^^^^^071-5553333||GRP54321|||||||20230101|20261231||SELF^Self^HL70063|van den Berg^Hendrik^Willem|SELF|19800115
AL1|1|DA^Drug Allergy^HL70127|PCN^Penicillin^HL70127|SV^Severe^HL70128|Anaphylaxis
```

---

## 2. ORU^R01 - Lab result (Comprehensive Metabolic Panel)

```
MSH|^~\&|LAB_SYS|UMCU|EPIC|UMCU|202603011630||ORU^R01^ORU_R01|LAB00042|P|2.5.1|||AL|NE
PID|1||MRN12345^^^UMCU^MR||van den Berg^Hendrik^Willem||19800115|M
PV1|1|I|ICU^0101^01^UMCU
ORC|RE|ORD5678^EPIC|FIL9012^LAB_SYS||CM
OBR|1|ORD5678^EPIC|FIL9012^LAB_SYS|24323-8^CMP^LN|||202603011445|||||||ATT1234^de Groot^Anna^^^MD||||||202603011615||LAB|F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.6-1.2|N|||F
OBX|3|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F
OBX|4|NM|2951-2^Sodium^LN||140|mEq/L|136-145|N|||F
OBX|5|NM|2823-3^Potassium^LN||4.2|mEq/L|3.5-5.0|N|||F
OBX|6|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F
OBX|7|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F
```

---

## 3. ORM^O01 - Lab order (STAT CBC)

```
MSH|^~\&|EPIC|UMCU|LAB_SYS|PATHOLOGY|202603011400||ORM^O01^ORM_O01|ORD00123|P|2.5.1|||AL|NE
PID|1||MRN12345^^^UMCU^MR||van den Berg^Hendrik^Willem||19800115|M
PV1|1|I|ICU^0101^01^UMCU||||ATT1234^de Groot^Anna^^^MD
ORC|NW|ORD5678^EPIC||GRP001^EPIC|||||202603011400|||ATT1234^de Groot^Anna^^^MD
OBR|1|ORD5678^EPIC||58410-2^CBC with Diff^LN|||202603011400|||||||||ATT1234^de Groot^Anna^^^MD|||||||||||^STAT
DG1|1||R50.9^Fever, unspecified^I10
NTE|1||Patient febrile x 24hrs, rule out infection.
```

---

## 4. SIU^S12 - New appointment booking

```
MSH|^~\&|SCHED_SYS|UMCU|EPIC|UMCU|202603051000||SIU^S12^SIU_S12|SCH00456|P|2.5.1|||AL|NE
SCH|APT78901^SCHED_SYS|APT78901^EPIC|||||ROUTINE^Routine^HL70277|OFFICE^Office Visit^LOCAL|30|MIN|^^30^202603101400^202603101430|||||ATT1234^de Groot^Anna^^^MD|^WPN^PH^^^^^030-2221234|POLI ALG^UMCU|ATT1234^de Groot^Anna^^^MD||Booked
PID|1||MRN12345^^^UMCU^MR||van den Berg^Hendrik^Willem||19800115|M|||Oudegracht 88^^Utrecht^UT^3511AB||^PRN^PH^^^^^030-2345678
PV1|1|O|POLI ALG^EXAM3^01^UMCU||||ATT1234^de Groot^Anna^^^MD
RGS|1|A
AIS|1|A|OFFICE_VISIT^Office Visit^LOCAL|||202603101400|0|MIN|30|MIN
AIP|1|A|ATT1234^de Groot^Anna^^^MD|ATT^Attending^HL70443
AIL|1|A|POLI ALG^EXAM3^01^UMCU||202603101400|0|MIN|30|MIN
```

---

## 5. MDM^T02 - Original document notification (operative note)

```
MSH|^~\&|TRANS_SYS|ERASMUS MC|EPIC|ERASMUS MC|202603021000||MDM^T02^MDM_T02|DOC00321|P|2.5.1|||AL|NE
EVN|T02|202603021000
PID|1||MRN12345^^^ERASMUS MC^MR||Brouwer^Jacobus^Adriaan||19800115|M
PV1|1|I|SURG^OR3^01^ERASMUS MC||||SUR5678^Meijer^Theodora^^^MD
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||202603011600|||||SUR5678^Meijer^Theodora^^^MD||||DOC54321||AU^Authenticated^HL70271||202603021000
OBX|1|TX|OP_NOTE^Operative Note^LOCAL||Procedure: Laparoscopic cholecystectomy\.br\Patient tolerated procedure well\.br\No complications\.br\EBL: 50mL\.br\Specimens sent to pathology.||||||F
```

---

## 6. ZorgDomein ORU^R01 - Referral letter with embedded PDF (Netherlands)

```
MSH|^_\&|ZorgDomein||||20160324163509+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van Dijk&van&Dijk^Pieter^Jan^^^^L||20000101|M|||Keizersgracht 42&Keizersgracht&42^^Amsterdam^^1016CS^NL^H||020-5551234_^NET^Internet^p.vandijk@kpnmail.nl
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Willemsen^E.F.G.||01004567^&&van Houten^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Houten^Z.Z.^^^^^^VEKTIS
OBX|1|NM|VB^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iagoz||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 7. ZorgDomein ORU^R01 - Diagnostic request with embedded PDF (Netherlands)

```
MSH|^_\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Jansen&Jansen&Jansen^Maria^Floor^^^^L||20000101|M|||Laan van Meerdervoort 15&Laan van Meerdervoort&15^^Den Haag^^2517AK^NL^H||070-3456789
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Bakker^D.E.F.||01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iagoz||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 8. HL7 Nederland ORU^R01 - Lab result (BSE/Bezinking)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~999999011^^^NLMINBIZA^NNNLD||Jansen^Pieter^A^^^^L||19650312|M|||Kerkstraat 42^^Amsterdam^^1012AB^NL^H||020-5551234
OBR|1|123|20050701015070^Labosys||||||||||||||||||LAB|F
OBX|1|ST|266^Bezinking^L^BSE||2|mm/uur|0 - 15|""|||F
```

---

## 9. IHE PAM ITI-31 ADT^A01 - Patient admission (French hospital, IHE Gazelle test)

```
MSH|^~\&|?|Saint-Louis|?|Saint-Louis|20050530082015||ADT^A01^ADT_A01|000001|T|2.5|||||FRA|8859/15|EN
EVN||20050530082000|||1001^Renard^Janine|20050530082000
PID|1||12345^^^Saint-Louis^PI||Lefèvre^Robert^^^^^L|||M||||||||||987654^^^Saint-Louis^AN
ROL||AD|FHCP|7777^Moreau^Philippe
PV1|1|I||||||2001^Dupont^Charles
ZBE|mvt1|20050530082000||INSERT|N
```

---

## 10. OML^O21 - Laboratory order (NIST example, Hepatitis panel)

```
MSH|^~\&#|NIST EHR|NIST EHR Facility|NIST Test Lab APP|NIST Lab Facility|20130211184101-0500||OML^O21^OML_O21|NIST-LOI_5.0_1.1-NG|T|2.5.1|||AL|AL|||||
PID|1||PATID5421^^^NIST MPI^MR||de Graaf^Saskia^Margaretha^^^^L||19820304|F||2106-3^White^HL70005|Singel 105^^Amsterdam^NH^1012VG^^H||^PRN^PH^^^020^6234567|||||||||N^Not Hispanic or Latino^HL70189
NK1|1|de Graaf^Daan^Willem^^^^L|SPO^Spouse^HL70063|Singel 105^^Amsterdam^NH^1012VG^^H|||||||||
ORC|NW|ORD448811^NIST EHR|||||||20120628070100|||5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI
OBR|1|ORD448811^NIST EHR||1000^Hepatitis A B C Panel^99USL|||20120628070100|||||||||5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI
DG1|1||F11.129^Opioid abuse with intoxication,unspecified^I10C|||W|||||||||1
```

---

## 11. ADT^A31 - Update patient information (NHS Homerton Hospital)

```
MSH|^~\&|P0241|HOMERTON|HOMERTON_TIE|HOMERTON|20150209170901||ADT^A31|Q111111119T4083493511111111||2.3
EVN|A31|20150209170901|||101111^Dekker^Geert^^^^^^PERSONNEL PRIMARY IDENTIFIER^Personnel^^^Personnel Primary Identifier^""
PID|1|999999^^^Homerton Case Note Number^MRN^""|999998^^^Homerton Case Note Number^CNN~111111^^^Person ID^Person ID||van Vliet^Anneke^^^Mrs^^Current~~^van Vliet^^^^^Alternate||19781030000000|Female|^van Vliet^^^^^Alternate~van Vliet^Johanna^^^Mrs^^Preferred~Brouwer^Anneke^^^Mrs^^Previous|""|Flat 1^15 Churchillaan^^Amsterdam^1078AA^""^home^^""~MAJOR HOUSE^CHURCH ROAD^^""^^""^Previous^AMSTERDAM^""||^Home^Tel~06-12345678^Mobile Number^Tel|^Business|Dutch|""|Not Known|999999^^^Homerton FIN^Encounter No.^""|9999999999|||European|||0|""|""|""||No||Trace in Progress
PD1|""|""||G88888888^Huisarts^Elisabeth^^020711111111^F84040^HUISARTSENPRAKTIJK CENTRUM^100 SINGEL^&AMSTERDAM&1012AB^^^^^Q06|""||""|""
NK1|1|van Vliet^Willem^^^^^Current|""|Flat 1^15 Churchillaan^^""^1078AA^""^^^""|06-98765432||Next of Kin|||||||||||||""
PV1|1|Inpatient|HUH AE OMU^OMU B^Bed 03^HOMERTON UNIVER^^Bed(s)^Homerton UH|Emergency-A\T\E/Dental||HUH AE Adults^""^""^HOMERTON UNIVER^^^Homerton UH|1122334^Yilmaz^Ahmed^^^^^^PERSONNEL PRIMARY IDENTIFIER^Personnel^^^Personnel Primary Identifier^""||3333444^Patel^Raj^^^^^^PERSONNEL PRIMARY IDENTIFIER^Personnel^^^Personnel Primary Identifier^""||Accident and Emergency|""|""|New Problem/First Attendance|NHS Provider-General (inc.A\T\E-this Hosp)|""|""||Inpatient|5000000^0^""^^Attendance No.|""||""||||||||||||||Admitted as Inpatient|""|""|HOMERTON UNIVER||Active|||20150208113419
PV2||NHS|^4 UNWELL|Transfer from ED|||""|||0|||""||||||||""|""|^^1
```

---

## 12. Nictiz Lab2Lab OML^O21 - Microbiology susceptibility (Netherlands)

```
MSH|^~\&|LABOSYS|UMCG_LAB|UMCG_MIC|UMCG|20180501120000||OML^O21^OML_O21|MSG20180501001|P|2.5|||AL|AL||NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.4.5^NL
PID|||987654321^^^^PI~999900011^^^NLMINBIZA^NNNLD||de Vries^Maria^J^^^^L||19750822|F|||Damrak 100^^Amsterdam^^1012LP^NL^H
ORC|NW|ORD99001^UMCG_LAB|||||||20180501110000|||1234567^Arts^Jan^^^^^^BIG
OBR|1|ORD99001^UMCG_LAB||29576-6^Bacterial susceptibility panel^LN|||20180501100000|||||||||1234567^Arts^Jan^^^^^^BIG
OBX|1|ST|6652-2^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||>=16|mg/L||null|||F
OBX|2|ST|7029-2^Meropenem [Susceptibility] by Gradient strip^LN||8,0|mg/L||null|||F
OBX|3||18943-1^Meropenem [Susceptibility]^LN|||||R|||F
SPM|1|||BLD^Blood^HL70487
```

---

## 13. ADT^A01 - HL7.org standard example (Good Health Hospital)

```
MSH|^~\&|ADT1|AMPHIA|GHH LAB, INC.|AMPHIA|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||
EVN|A01|200708181123||
PID|1||PATID1234^^^ADT1^MR^AMPHIA~283746591^^^NLMINBIZA^NNNLD||Mulder^Geert^Jan^III||19610615|M||2106-3^WHITE^HL70005|Marktplein 7^^Breda^^4811AB^NL||^PRN^PH^CP^^^076^5142233|^WPN^PH^CP^^^076^5142234|NLD^Dutch^HL70296|M^Married^HL70002|CHR^Christian^HL70006|ACCT001
PV1|1|I|WARD1^ROOM02^BED01^AMPHIA|U^Urgent^HL70007||WARD1^ROOM01^BED01|ATTEND001^van der Linden^Pieter^J^III^DR|REFER001^Bos^Elisabeth^A^JR^DR||SUR^Surgery^HL70069||||ADM^ADMIT^HL70023
```

---

## 14. MDM^T02 - Retinal screening with base64 image attachment

```
MSH|^\~\&|IRIS|IRIS|VENDOR|VENDOR|20170410145907||MDM^T02|170410145907|T|2.4
PID|1||12345^^^IRIS^MR||Bakker^Anneke||19650101|F|||Breestraat 30^^Leiden^^2311CJ||^PRN^PH^^^^^071-5234567
PV1|1|O|CLINIC^RM1^BED1||||PROV001^Smit^Daan^^^MD
TXA|1|OP^Examination Report^HL70270|TX||20170410||||||PROV001^Smit^Daan^^^MD||||RPT001||AU||20170410145907
OBX|1|ED|RETINAL_IMG^Retinal Image Right Eye^LOCAL||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgcI/8QAJhAAAQMDAwQCAwAAAAAAAAAAAQIDBAAFEQYSIQcxQVETImFx/8QAFQEBAQAAAAAAAAAAAAAAAAAABQb/xAAeEQABAwQDAAAAAAAAAAAAAAABAAIDBAUSITFRYf/aAAwDAQACEQMRAD8Aq==||||||F
OBX|2|NM|IOP_OD^Intraocular Pressure Right Eye^LOCAL||14|mmHg|10-21|N|||F
OBX|3|NM|IOP_OS^Intraocular Pressure Left Eye^LOCAL||15|mmHg|10-21|N|||F
OBX|4|TX|FINDINGS^Clinical Findings^LOCAL||No diabetic retinopathy detected. Cup-to-disc ratio within normal limits bilaterally.||||||F
```

---

## 15. ORU^R01 - Dutch lab result with BSN identifier

```
MSH|^~\&|LABSYS|AMC_LAB|EPIC|AMC|20200915143000+0200||ORU^R01^ORU_R01|LAB20200915001|P|2.4|||AL|AL||NLD|8859/1
PID|||7654321^^^^PI~999911234^^^NLMINBIZA^NNNLD||Bakker^Jan^P^^^^L||19580622|M|||Prinsengracht 263^^Amsterdam^^1016GV^NL^H||020-6249876
PV1|1|O|POLI INT^01^01^AMC
ORC|RE|ORD2020001^EPIC|FILL2020001^LABSYS||CM
OBR|1|ORD2020001^EPIC|FILL2020001^LABSYS|24326-1^Electrolytes 1998 panel - Serum or Plasma^LN|||20200915100000+0200|||||||||12345678^Jansen^Karel^^^^^^BIG
OBX|1|NM|2951-2^Natrium^LN||138|mmol/L|136-145|N|||F
OBX|2|NM|2823-3^Kalium^LN||4.5|mmol/L|3.5-5.0|N|||F
OBX|3|NM|2075-0^Chloride^LN||101|mmol/L|98-107|N|||F
OBX|4|NM|1963-8^Bicarbonaat^LN||24|mmol/L|22-29|N|||F
```

---

## 16. ADT^A04 - Outpatient registration (European profile)

```
MSH|^~\&|EPIC|RADBOUDUMC|PAS|RADBOUDUMC|20210315090000+0100||ADT^A04^ADT_A04|REG20210315001|P|2.5|||AL|NE||NLD|8859/1
EVN|A04|20210315090000+0100
PID|1||8765432^^^^PI~999922345^^^NLMINBIZA^NNNLD||van den Berg^Sophie^M^^^^L||19900714|F|||Grote Markt 1^^Nijmegen^^6511KB^NL^H||024-3611234||NLD^Dutch^HL70296|S^Single^HL70002
PV1|1|O|POLI DERM^201^A^RADBOUDUMC|R^Routine^HL70007|||54321678^de Groot^Anna^^^^^^BIG|||DER^Dermatologie^HL70069||||1|||54321678^de Groot^Anna^^^^^^BIG|OP^Outpatient^HL70004||||||||||||||||||RADBOUDUMC||A|||20210315090000+0100
IN1|1|VGZ001^VGZ|VGZ|Postbus 1000^^Arnhem^^6800BA^NL||||GRP789|||||||20210101|20211231
```

---

## 17. ORM^O01 - Radiology order (typical Epic outgoing)

```
MSH|^~\&|EPIC|UMCG|RIS|UMCG_RAD|20220118141500+0100||ORM^O01^ORM_O01|RAD20220118001|P|2.5.1|||AL|NE||NLD|8859/1
PID|1||3456789^^^^PI~999933456^^^NLMINBIZA^NNNLD||Mulder^Frederik^H^^^^L||19720930|M|||Vijzelstraat 77^^Amsterdam^^1017HG^NL^H||020-5557890
PV1|1|O|POLI RAD^102^A^UMCG||||98765432^Visser^Maria^^^^^^BIG
ORC|NW|ORDRAD001^EPIC||||||20220118141500+0100|||98765432^Visser^Maria^^^^^^BIG
OBR|1|ORDRAD001^EPIC||71020^Chest 2 views^CPT4|||20220118141500+0100|||||||||98765432^Visser^Maria^^^^^^BIG|||||||||^ROUTINE
DG1|1||R05.9^Hoest, niet gespecificeerd^I10
NTE|1||Persisterende hoest > 3 weken, uitsluiten pneumonie.
```

---

## 18. ORU^R01 - Pathology report with text

```
MSH|^~\&|PATH_SYS|CATHARINA|EPIC|CATHARINA|202204051430||ORU^R01^ORU_R01|PATH20220405001|P|2.5.1|||AL|NE
PID|1||MRN98765^^^CATHARINA^MR||de Jong^Margaretha^Elisabeth||19550812|F
PV1|1|I|SURG^401^A^CATHARINA||||SUR001^Dekker^Michiel^^^MD
ORC|RE|ORDPATH001^EPIC|FILLPATH001^PATH_SYS||CM
OBR|1|ORDPATH001^EPIC|FILLPATH001^PATH_SYS|88305^Surgical Pathology^CPT4|||202204051000|||||||SUR001^Dekker^Michiel^^^MD||||||202204051415||PATH|F
OBX|1|FT|22637-3^Pathology report final diagnosis^LN||FINAL DIAGNOSIS:\.br\\.br\Gallbladder, cholecystectomy:\.br\- Chronic cholecystitis with cholelithiasis\.br\- No evidence of dysplasia or malignancy\.br\\.br\GROSS DESCRIPTION:\.br\Received in formalin is a gallbladder measuring 8.5 x 3.2 x 2.8 cm\.br\containing multiple faceted yellow-green gallstones ranging from 0.3-1.2 cm.||||||F
```

---

## 19. SIU^S15 - Appointment cancellation

```
MSH|^~\&|EPIC|AMC|SCHED|AMC|20230501143000+0200||SIU^S15^SIU_S15|CANC20230501001|P|2.5.1|||AL|NE||NLD|8859/1
SCH|APT55001^EPIC|APT55001^SCHED|||||ROUTINE^Routine^HL70277|CONSULT^Consultation^LOCAL|20|MIN|^^20^202305081000^202305081020|||||67890123^Smit^Dirk^^^MD|^WPN^PH^^^^^020-5559876|POLI KNO^AMC||Cancelled
PID|1||4567890^^^^PI~999944567^^^NLMINBIZA^NNNLD||de Jong^Willem^R^^^^L||19830225|M|||Herengracht 500^^Amsterdam^^1017CB^NL^H
PV1|1|O|POLI KNO^305^B^AMC||||67890123^Smit^Dirk^^^MD
RGS|1|A
AIS|1|A|CONSULT_KNO^ENT Consultation^LOCAL|||202305081000|0|MIN|20|MIN
```

---

## 20. ADT^A08 - Update patient information (Dutch demographics)

```
MSH|^~\&|EPIC|AMSTERDAM_UMC|MPI|AMSTERDAM_UMC|20240112100000+0100||ADT^A08^ADT_A08|UPD20240112001|P|2.5|||AL|NE||NLD|8859/1
EVN|A08|20240112100000+0100
PID|1||1234567890^^^^PI~999955678^^^NLMINBIZA^NNNLD||Vermeer^Elisabeth^A^^^^L||19680419|F|||Vondelpark 12^^Amsterdam^^1071AA^NL^H~Postbus 999^^Amsterdam^^1000AZ^NL^M||020-5551111^PRN^PH~06-12345678^PRN^CP||NLD^Dutch^HL70296|M^Married^HL70002||ACCT240001^^^AMSTERDAM_UMC^AN
PD1||||87654321^Huisarts^Petra^^^^^^BIG^L^^^BIG
PV1|1|O|POLI INT^501^A^AMSTERDAM_UMC|R|||11223344^Dekker^Michiel^^^^^^BIG|||INT^Interne Geneeskunde^HL70069||||1|||11223344^Dekker^Michiel^^^^^^BIG|OP^Outpatient^HL70004
NK1|1|Vermeer^Pieter^J|SPO^Spouse^HL70063|Vondelpark 12^^Amsterdam^^1071AA^NL|06-98765432^PRN^CP
IN1|1|CZ001^CZ|CZ|Postbus 900^^Tilburg^^5000AX^NL||||GRP456|||||||20240101|20241231||SELF^Zelf^HL70063|Vermeer^Elisabeth^A|SELF|19680419
```
