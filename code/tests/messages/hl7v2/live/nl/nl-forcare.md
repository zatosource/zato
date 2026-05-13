# Forcare (Philips) - real HL7v2 ER7 messages

## 1. ORU R01 - diagnostic research request with embedded PDF (ZorgDomein)

```
MSH|^_\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van Dijk&van&Dijk^Pieter^Jan^^^^L||20000101|M|||Keizersgracht 42&Keizersgracht&42^^Amsterdam^^1016CS^NL^H||020-5551234
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Willemsen^E.F.G.||01004567^&&van Houten^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Houten^Z.Z.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgAxKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iag==||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 2. ORU R01 - referral with Word document attachment (ZorgDomein)

```
MSH|^_\&|ZorgDomein||||20160324163507+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Jansen&Jansen&Jansen^Maria^Floor^^^^L||20000101|M|||Laan van Meerdervoort 15&Laan van Meerdervoort&15^^Den Haag^^2517AK^NL^H||070-3456789
PV1|1|O
ORC|XO|ZD200046119|||||||20160324163432+0100|^&&het Bakker^D.E.F.||01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CARCOA001^zorgproductcode^ZORGDOMEIN|||20160324163432+0100||||||Mijn toelichting op de bijlagen.|||01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS|||||||||F|||||||||||||||||||||^Overzicht van de bijlagen:\.br\De volgende bijlage(n) behorend bij de verwijzing met ZD200046119 is/zijn verzonden\.br\- HL7.doc\.br\- ZD\R\logo\R\kleur\R\RGB.png\.br\
OBX|1|ED|BLOB^Bijlage^ZORGDOMEIN|1|^application^msword^Base64^0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP7/CQAGAAAAAAAAAAAAAAABAAAALgAAAAAAAAAAEAAAMAAAAAEAAAD+////AAAAAC0AAAD///////8=||||||F
NTE|1|P|HL7.doc|RE
OBX|2|ED|BLOB^Bijlage^ZORGDOMEIN|2|^image^png^Base64^iVBORw0KGgoAAAANSUhEUgAABJ0AAAOxCAYAAABfedaEAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAA||||||F
NTE|2|P|ZD\R\logo\R\kleur\R\RGB.png|RE
```

---

## 3. SRM S01 - appointment request (ZorgDomein)

```
MSH|^~\&|ZorgDomein||applicatie|faciliteit|20160324163440||SRM^S01^SRM_S01|g20ce6a9f8ca4f551275|P|2.4|||||NLD|8859/1
ARQ|ZD200046139|||||CARHAR^Cardiologie / Hartfalen^99zda|CARREG001^consult cardioloog^99zda|REG^regulier^99zda|||20160329^20160428|R|||01004567^van Houten^Z.Z.^^^^^^VEKTIS|015-2222222^^PH~012-2222222^^FX|Molenweg 12&Molenweg&12^^Groningen^^9711GP^NL|^^^Huisartsenpraktijk Eikenlaan&01059999^^^^^locatie Utrecht|""^het Willemsen^E.F.G.|015-2222222^^PH~012-2222222^^FX|^^^Huisartsenpraktijk Eikenlaan&01059999^^^^^locatie Utrecht
PID|1||^^^NLMINBIZA^NNNLD~ZD200046139^^^ZorgDomein^VN||de Boer&de&Boer^Willem^Hendrik^^^^L||20000101|U|||Herengracht 200&Herengracht&200^^Amsterdam^^1016BS^NL^M||020-5557890^PRN^PH~06-55554444^ORN^CP||||||||||||||||||Y|NNNLD
RGS|1|U
AIS|1|U|^consult cardioloog||0|m|||No||^Patiënt spreekt uitsluitend Frans.
AIG|1|U|CAR^Cardiologie^99zda|""|||||0|m|||No
AIL|1|U|^^^01059998&Isala, locatie Zwolle|""|||0|m|||No
AIP|1|U|^Meijer^Theodora|""|||0|m|||No
```

---

## 4. ORU R01 - Dutch lab results with BSN (HL7 Nederland)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~999999011^^^NLMINBIZA^NNNLD||van der Meer&&van der Meer^Cornelia^^^^^L~van der Meer&&van der Meer^Cornelia^^^^^B||19500101|F|||Dorpsstraat 8&Dorpsstraat&8^^Zwolle^^8011AB^^M~Dorpsstraat 8&Dorpsstraat&8^^Zwolle^^8011AB^^L||038-4567890^PRN^PH~^^^c.vandermeer@kpnmail.nl|||M|||||||Zwolle|Y|2||||""|N|N|||||||
OBX|1|ST|882-1^ABO+Rh group||O pos||||||F
PV1|1|I|0RGC2||||
OBR|1|123|20050701015070^Labosys||||200507010907||||||""|||3004^Brouwer||||200507010907||201708220955||S|F||^^^^^R
OBX|1|ST|266^Bezinking^L^BSE||2|mm/uur|0 - 15|""|||F
OBX|2|ST|325^Leucocyten^L^LEU||6.7|/nl|4.0 - 10.0|""|||F
OBX|3|ST|323^Hemoglobine^L^HB||10.2|mmol/l|8.5 - 11.0|""|||F
OBX|4|ST|324^Hematocriet^L^HT||0.48|l/l|0.41 - 0.51|""|||F
OBX|5|ST|326^Ery's^L^ERY||5.2|/pl|4.4 - 5.8|""|||F
OBX|6|ST|328^MCV^L^MCV1||92|fl|80 - 100|""|||F
OBX|7|ST|329^MCH^L^MCH||1.97|fmol|1.60 - 2.10|""|||F
OBX|8|ST|330^MCHC^L^MCHC||21.3|mmol/l|19.0 - 23.0|""|||F
OBX|9|ST|648^Ureum^L^UR||3.9|mmol/l|2.5 - 7.5|""|||F
OBX|10|ST|630^Kreatinine^L^KR||99|umol/l|70 - 110|""|||F
OBX|11|ST|638^Natrium^L^NA||139|mmol/l|135 - 145|""|||F
OBX|12|ST|628^Kalium^L^K||3.9|mmol/l|3.5 - 5.0|""|||F
OBX|13|ST|2325^Alk.fosf.^L^AF||52|U/l|0 - 120|""|||F
OBX|14|ST|2326^Gamma GT^L^GGT||29|U/l| - 50|""|||F
OBX|15|ST|2327^ASAT^L^ASAT||19|U/l|0 - 40|""|||F
OBX|16|ST|2328^ALAT^L^ALAT||20|U/l|0 - 45|""|||F
OBX|17|ST|614^Glucose^L^GLUS||10.3|mmol/l|4.0 - 7.8|H|||F
OBX|18|ST|34^TSH^L^TSH||0.78|mU/l|0.4 - 4.0|""|||F
```

---

## 5. ADT A01 - patient admission (HL7.org v2.8)

```
MSH|^~\&|ADT1|AMPHIA|GHH LAB, INC.|AMPHIA|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||
EVN|A01|200708181123||
PID|1||PATID1234^^^ADT1^MR^AMPHIA^^198807010900^199912312359~283746591^^^NLMINBIZA^NNNLD||Mulder&Mulder^Geert^Jan^III^DR^^L^^^199907010900&199912312359^^199907010900^199912312359^PhD^AL|van Loon|19610615|M^MALE^HL70001||2106-3^WHITE^HL70005|Marktplein 7^Bus 2^Breda^NB^4811AB^NL^M^^Breda&Breda&HL70289^^^199907010900&199912312359^199907010900^199912312359^^^^^C/O H. MULDER|Breda|(076) 514-2233^PRN^CP^^31^076^5142233^^^^^^198807010900^199912312359~^NET^Internet^g.mulder@kpnmail.nl|(076)514-2234^WPN^PH^^31^076^5142234^X2301^^^^^198807010900^199912312359|cs^Czech^HL70296|M^MARRIED^HL70002|AGN^Agnostic^HL70006||444333333|987654^NB^20010715||H^Hispanic or Latino^HL70189|Prague|Y|2|CZ^Czech^HL70171|||19880818|Y|||19880818|||||||(076) 514-2235^PRN^PH^^31^076^5142235^^^^^^198807010900^199912312359
PD1|||Huisartsenpraktijk Centrum^L^^^^NPIAA^XX^^^123457|998874^van Dongen^Johanna^Maria^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|N^NOT A STUDENT^HL70231||Y^YES PATIENT HAS WILL^HL70315|||||||AGNOSTIC HALL
NK1|1|Mulder^Anneke^W|SPO^SPOUSE^HL70063|Marktplein 7^Bus 2^Breda^NB^4811AB^NL^M^^Breda&Breda&HL70289^^^199907010900&199912312359^199907010900^199912312359|(076) 514-2235^PRN^PH^^31^076^5142235^^^^^^198807010900^199912312359||NK^NEXT OF KIN^HL70131|19770704|19980901|||||M^MARRIED^HL70002|F^FEMALE^HL70001|19680913
PV1|1|I^INPATIENT^HL70004|12NORTH^1211^A^AMPHIA^^^1956 ADDITION^12|U^URGENT^HL0007|pa5543^^AMPHIA||004777^Bos^Adriaan^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|004778^Veldman^Saskia^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|004799^Huisman^Floor^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|SUR^SURGICAL SERVICE^HL70069|||R^READMISSION^HL70093|ADM^^HL70023||VIP^VIP^HL70099|004744^Koster^Theodora^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD||P1231^^^AMPHIA^VN|||||||||||||||||DEC^DECEASED^HL70112||VEG^VEGETARIAN^HL701114||||||198808161216|198808181126|||||9942^^^GHS^VN||004744^Kuijpers^Hendrik^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD
PV2|||||||||||2|ADMIT TO CARDIAC UNIT|||||||||||||1^EMERGENCY^HL70217|||||||||||||A^AMBULANCE^HL70430
AL1|1|DA^DRUG ALLERGY^HL70127|387458008^ASPIRIN(SUBSTANCE)^SCT|MO^MODERATE^HL70128|HIVES|199807011755
AL1|2|DA^DRUG ALLERGY^HL70127|373529000^MORPHINE(SUBSTANCE)^SCT|MO^MODERATE^HL70128|DELERIUM|199806111225
DG1|1||85898001^CARDIOMYOPATHY^SCT||19970212|||||||||||998874^van Dongen^Johanna^Maria^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|||19970213|423432^GHS|U
PR1|1||41976001^Cardiac catheterization^SCT||198808180701|||99234^Evers^Elisabeth^Cornelia^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|||998874^de Wit^Jacobus^^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD|998874^Scholten^Pieter^^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD||||85898001^CARDIOMYOPATHY^SCT|||123231^AMPHIA
```

---

## 6. ORU R01 - hepatitis panel lab results (NIST test lab)

```
MSH|^~\&|NIST Test Lab APP|NIST Lab Facility||NIST EHR Facility|20150926140551||ORU^R01^ORU_R01|NIST-LOI_5.0_1.1-NG|T|2.5.1|||AL|AL|||||
PID|1||PATID5421^^^NIST MPI^MR||de Graaf^Saskia^Margaretha^^^^L||19820304|F||2106-3^White^HL70005|Singel 105^^Amsterdam^NH^1012VG^^H||^PRN^PH^^^020^6234567|||||||||N^Not Hispanic or Latino^HL70189
ORC|NW|ORD448811^NIST EHR|R-511^NIST Lab Filler||||||20120628070100|||5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI
OBR|1|ORD448811^NIST EHR|R-511^NIST Lab Filler|1000^Hepatitis A B C Panel^99USL|||20120628070100|||||||||5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI
OBX|1|CWE|22314-9^Hepatitis A virus IgM Ab [Presence] in Serum^LN^HAVM^Hepatitis A IgM antibodies (IgM anti-HAV)^L^2.52||260385009^Negative (qualifier value)^SCT^NEG^NEGATIVE^L^201509USEd^^Negative (qualifier value)||Negative|N|||F|||20150925|||||201509261400
OBX|2|CWE|20575-7^Hepatitis A virus Ab [Presence] in Serum^LN^HAVAB^Hepatitis A antibodies (anti-HAV)^L^2.52||260385009^Negative (qualifier value)^SCT^NEG^NEGATIVE^L^201509USEd^^Negative (qualifier value)||Negative|N|||F|||20150925|||||201509261400
OBX|3|NM|22316-4^Hepatitis B virus core Ab [Units/volume] in Serum^LN^HBcAbQ^Hepatitis B core antibodies (anti-HBVc) Quant^L^2.52||0.70|[IU]/mL^international unit per milliliter^UCUM^IU/ml^^L^1.9|<0.50 IU/mL|H|||F|||20150925|||||201509261400
```

---

## 7. ORU R01 - ICU patient monitoring vitals (HL7.org)

```
MSH|^~\&|HL7|CG3_SICU|CE_CENTRAL|GH_CSF|20251014154101||ORU^R01|20251014154101-639|P|2.3||||||UNICODE UTF-8
PID|||100002^^^A^MR||Hendriks^^|^^|||||^^^^^^^||||||||||||||||
PV1||E|G52008|||||||||||||||||||||||||||||||||||||||
OBR|1||||||20251014154101||||||||||||||||||||^^^^||||||||||
OBX|1|ST|HR||73|/min|||||R
OBX|2|ST|PVC||15|#/min|||||R
OBX|3|ST|STI||-0.5|mm|||||R
OBX|4|ST|STII||0.0|mm|||||R
OBX|5|ST|STIII||0.5|mm|||||R
OBX|6|ST|STV1||0.0|mm|||||R
OBX|7|ST|STAVR||0.2|mm|||||R
OBX|8|ST|STAVL||-0.5|mm|||||R
OBX|9|ST|STAVF||0.2|mm|||||R
OBX|10|ST|RR||15|breaths/min|||||R
OBX|11|ST|CO2EX||32|mm(hg)|||||R
OBX|12|ST|CO2IN||0|mm(hg)|||||R
OBX|13|ST|CO2RR||14|breaths/min|||||R
OBX|14|ST|SPO2R||73|/min|||||R
OBX|15|ST|SPO2P||99|%|||||R
```

---

## 8. ORU R01 - Dutch lab blood count and chemistry (HL7 Nederland variation)

```
MSH|^~\&|GLIMS|UMCG|||20180315091200||ORU^R01|MSG20180315001|P|2.4||
PID|||7654321^^^^PI~123456782^^^NLMINBIZA^NNNLD||de Vries&&de Vries^Jan^^^^^L||19650423|M|||Keizersgracht 42&Keizersgracht&42^^Amsterdam^^1015CS^^L||020-5551234^PRN^PH|||||||||||||||||||N|N|||||||
PV1|1|O|POLI||||
OBR|1|REQ-98765|LAB-2018-4433^GLIMS|CBC^Volledig bloedbeeld^L|||20180315080000||||||||||||||20180315091200||LAB|F||^^^^^R
OBX|1|NM|718-7^Hemoglobine^LN^HB||8.9|mmol/l|7.5 - 10.0|""|||F
OBX|2|NM|6690-2^Leucocyten^LN^WBC||7.2|10*9/l|4.0 - 10.0|""|||F
OBX|3|NM|789-8^Erytrocyten^LN^RBC||4.8|10*12/l|4.0 - 5.5|""|||F
OBX|4|NM|787-2^MCV^LN^MCV||88|fl|80 - 100|""|||F
OBX|5|NM|4544-3^Hematocriet^LN^HCT||0.43|l/l|0.35 - 0.47|""|||F
OBX|6|NM|777-3^Trombocyten^LN^PLT||245|10*9/l|150 - 400|""|||F
```

---

## 9. ORM O01 - radiology order (Dutch hospital context)

```
MSH|^~\&|ZIS|VUMC|RIS|VUMC|20190614102300||ORM^O01|ORM2019061401|P|2.4|||||NLD|8859/1
PID|1||PAT-445566^^^^MR~987654321^^^NLMINBIZA^NNNLD||Bakker&&Bakker^Pieter^^^^^L||19780312|M|||Prinsengracht 100&Prinsengracht&100^^Amsterdam^^1015EA^NL^L||020-6234567^PRN^PH
PV1|1|O|RAD^001^^VUMC||||123456^Jansen^M.D.^^^^^^VEKTIS
ORC|NW|ORD-2019-8877|||||||20190614102300|||123456^Jansen^M.D.^^^^^^VEKTIS
OBR|1|ORD-2019-8877||71020^CT Thorax^CPT|||20190614|||||||Verdenking longembolie|||123456^Jansen^M.D.^^^^^^VEKTIS
DG1|1||I26.9^Longembolie^ICD10||20190614
```

---

## 10. ADT A04 - patient registration outpatient (Dutch hospital)

```
MSH|^~\&|EPD|ERASMUSMC|LIS|ERASMUSMC|20200901083015||ADT^A04|ADT20200901001|P|2.4|||||NLD|8859/1
EVN|A04|20200901083015
PID|1||12345678^^^^MR~111222333^^^NLMINBIZA^NNNLD||van der Berg&&van der Berg^Maria^C.^^^^L||19850715|F|||Laan van Meerdervoort 50&Laan van Meerdervoort&50^^Den Haag^^2517AK^NL^L||070-3456789^PRN^PH~06-12345678^ORN^CP
PV1|1|O|POLI^INT^^ERASMUSMC||||567890^de Groot^A.B.^^^^^^VEKTIS|||INT^Interne geneeskunde^L|||||||567890^de Groot^A.B.^^^^^^VEKTIS||V-2020-12345^^^ERASMUSMC^VN
```

---

## 11. ADT A08 - patient information update (Dutch hospital)

```
MSH|^~\&|ZIS|AMC|EPD|AMC|20210115140030||ADT^A08|ADT20210115002|P|2.4|||||NLD|8859/1
EVN|A08|20210115140030
PID|1||99887766^^^^MR~222333444^^^NLMINBIZA^NNNLD||Smit&&Smit^Willem^J.^^^^L||19720903|M|||Herengracht 200&Herengracht&200^^Amsterdam^^1016BS^NL^L||020-7654321^PRN^PH~06-87654321^ORN^CP~^^^w.smit@kpnmail.nl
PV1|1|I|5WEST^501^A^AMC||||234567^Peters^K.L.^^^^^^VEKTIS|||CHI^Chirurgie^L|||||||234567^Peters^K.L.^^^^^^VEKTIS||B-2021-001^^^AMC^VN
```

---

## 12. ADT A03 - patient discharge (Dutch hospital)

```
MSH|^~\&|ZIS|LUMC|EPD|LUMC|20210520160000||ADT^A03|ADT20210520003|P|2.4|||||NLD|8859/1
EVN|A03|20210520160000
PID|1||44556677^^^^MR~333444555^^^NLMINBIZA^NNNLD||Dijkstra&&Dijkstra^Anna^M.^^^^L||19900228|F|||Breestraat 75&Breestraat&75^^Leiden^^2311CH^NL^L||071-5123456^PRN^PH
PV1|1|I|3NORTH^302^B^LUMC||||345678^van Dijk^R.S.^^^^^^VEKTIS|||CAR^Cardiologie^L|||||||345678^van Dijk^R.S.^^^^^^VEKTIS||B-2021-055^^^LUMC^VN|||||||||||||||||||||||||20210515100000|20210520160000
DG1|1||I50.0^Hartfalen^ICD10||20210515
```

---

## 13. OML O21 - lab order with specimen (Nictiz Lab2Lab style)

```
MSH|^~\&|LIS-A|LAB-ALPHA|LIS-B|LAB-BETA|20180415093000||OML^O21^OML_O21|OML201804150001|P|2.5|||||NLD|UNICODE UTF-8
PID|1||LABPAT-001^^^^MR~555666777^^^NLMINBIZA^NNNLD||Mulder&&Mulder^Kees^^^^^L||19551010|M|||Dorpsstraat 12&Dorpsstraat&12^^Groningen^^9711AA^NL^L||050-3123456^PRN^PH
PV1|1|O|POLI||||
ORC|NW|REQ-LAB-2018-100|||||||20180415093000|||456789^Huisarts^W.^^^^^^VEKTIS
OBR|1|REQ-LAB-2018-100||24357-6^Urinalysis macro (dipstick) panel^LN|||20180415|||||||||||||||||||F
SPM|1|SPM-001^^LAB-ALPHA||UR^Urine^HL70487||||||||||||||20180415080000|20180415090000
```

---

## 14. ORU R01 - microbiology susceptibility result (Nictiz Lab2Lab style)

```
MSH|^~\&|LIS-B|LAB-BETA|LIS-A|LAB-ALPHA|20180420141500||ORU^R01^ORU_R01|ORU201804200001|P|2.5|||||NLD|UNICODE UTF-8
PID|1||LABPAT-002^^^^MR~666777888^^^NLMINBIZA^NNNLD||Visser&&Visser^Henk^^^^^L||19680301|M
PV1|1|I|ICU||||
ORC|RE|REQ-LAB-2018-200|RES-LAB-2018-200||CM||||20180420141500
OBR|1|REQ-LAB-2018-200|RES-LAB-2018-200|632-0^Bacteria Culture^LN|||20180418||||||||||||||20180420141500||MB|F
OBX|1|CWE|600-7^Bacteria identified^LN||112283007^Escherichia coli^SCT||||||F
OBX|2|ST|6652-2^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||>=16|mg/L||R|||F
OBX|3|ST|7029-2^Meropenem [Susceptibility] by Gradient strip^LN||8.0|mg/L||I|||F
OBX|4|CWE|18943-1^Meropenem [Susceptibility]^LN||R^Resistant^HL70078||||||F
```

---

## 15. ORU R01 - pathology report with embedded PDF (IHE XD-LAB style)

```
MSH|^~\&|PATH_SYS|RADBOUDUMC|EPD|RADBOUDUMC|20220310150000||ORU^R01^ORU_R01|ORU-PA-2022-001|P|2.5.1|||||NLD|UNICODE UTF-8
PID|1||PA-12345^^^^MR~888999000^^^NLMINBIZA^NNNLD||Jansen&&Jansen^Sophie^^^^^L||19750620|F|||Plein 1944 nr 5&Plein 1944&5^^Nijmegen^^6511AA^NL^L||024-3612345^PRN^PH
PV1|1|O|PATH||||
ORC|RE|PA-ORD-2022-100|PA-RES-2022-100||CM
OBR|1|PA-ORD-2022-100|PA-RES-2022-100|11529-5^Surgical pathology study^LN|||20220308
OBX|1|FT|22638-1^Pathology report^LN||Macroscopie: Huidbiopt linker onderarm, 0.4 cm\.br\Microscopie: Basaalcelcarcinoom, nodulair type\.br\Snijvlakken vrij\.br\Conclusie: BCC nodulair type, radicaal verwijderd.||||||F
OBX|2|ED|PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCg==||||||F
```

---

## 16. ORM O01 - lab order CBC (general HL7v2)

```
MSH|^~\&|EMR|RIJNSTATE|LAB|RIJNSTATE|20230915120000||ORM^O01|ORM-2023-001|P|2.3
PID|1||MR-12345^^^RIJNSTATE^MR||de Wit^Floor^Johanna||19800101|F|||Velperweg 26^^Arnhem^^6824BJ||026-4456789
PV1|1|O|SEH^^^RIJNSTATE||||1234^Kuijpers^Hendrik^A|||SEH||||||||1234^Kuijpers^Hendrik^A|SEH|V1234^^^RIJNSTATE^VN
ORC|NW|ORD-5001|||||^^^20230915120000^^S||20230915120000|||1234^Kuijpers^Hendrik^A
OBR|1|ORD-5001||58410-2^CBC panel^LN|||20230915120000||||||||1234^Kuijpers^Hendrik^A
DG1|1||R50.9^Fever, unspecified^ICD10
NTE|1||STAT - Patient febrile, suspect infection
```

---

## 17. ORU R01 - CBC results (general HL7v2)

```
MSH|^~\&|LAB|RIJNSTATE|EMR|RIJNSTATE|20230915140000||ORU^R01|ORU-2023-001|P|2.3
PID|1||MR-12345^^^RIJNSTATE^MR||de Wit^Floor^Johanna||19800101|F|||Velperweg 26^^Arnhem^^6824BJ||026-4456789
PV1|1|O|SEH^^^RIJNSTATE||||1234^Kuijpers^Hendrik^A
ORC|RE|ORD-5001|LAB-R-5001||CM
OBR|1|ORD-5001|LAB-R-5001|58410-2^CBC panel^LN|||20230915120000|||||||||1234^Kuijpers^Hendrik^A|||||||20230915140000||LAB|F
OBX|1|NM|6690-2^Leukocytes^LN||12.5|10*3/uL|4.5-11.0|H|||F
OBX|2|NM|789-8^Erythrocytes^LN||4.2|10*6/uL|3.8-5.2|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||13.5|g/dL|12.0-16.0|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||40.2|%|36.0-46.0|N|||F
OBX|5|NM|787-2^MCV^LN||88.5|fL|80.0-100.0|N|||F
OBX|6|NM|777-3^Platelets^LN||225|10*3/uL|150-400|N|||F
```

---

## 18. ADT A01 - Dutch inpatient admission

```
MSH|^~\&|ZIS|UMCU|EPD|UMCU|20220101083000||ADT^A01|ADT20220101001|P|2.4|||||NLD|8859/1
EVN|A01|20220101083000
PID|1||55667788^^^^MR~444555666^^^NLMINBIZA^NNNLD||de Boer&&de Boer^Frederik^H.^^^^L||19450812|M|||Oudegracht 150&Oudegracht&150^^Utrecht^^3511AX^NL^L||030-2345678^PRN^PH
NK1|1|de Boer^Elisabeth|SPO^Echtgenote^HL70063|Oudegracht 150&Oudegracht&150^^Utrecht^^3511AX^NL^L|030-2345678^PRN^PH
PV1|1|I|6EAST^601^A^UMCU|E^Spoed^HL0007|||789012^Willemsen^P.Q.^^^^^^VEKTIS|||LON^Longziekten^L|||||||789012^Willemsen^P.Q.^^^^^^VEKTIS||B-2022-001^^^UMCU^VN||||||||||||||||||||||||20220101083000
AL1|1|DA^Geneesmiddellenallergie^HL70127|N02BE01^Paracetamol^ATC|MI^Mild^HL70128|Huiduitslag
DG1|1||J18.9^Pneumonie, niet gespecificeerd^ICD10||20220101
```

---

## 19. ORU R01 - comprehensive metabolic panel (general HL7v2)

```
MSH|^~\&|LAB|ISALA|EMR|ISALA|20230920100000||ORU^R01|ORU-2023-CMP-001|P|2.5.1
PID|1||MR-67890^^^ISALA^MR||Bos^Jacobus^Adriaan||19650315|M|||Grote Voort 33^^Zwolle^^8011GE||038-4234567
PV1|1|O|POLI^^^ISALA||||5678^van der Heijden^Saskia^B
ORC|RE|ORD-6001|LAB-R-6001||CM
OBR|1|ORD-6001|LAB-R-6001|24323-8^Comprehensive metabolic panel^LN|||20230920080000|||||||||5678^van der Heijden^Saskia^B|||||||20230920100000||LAB|F
OBX|1|NM|2345-7^Glucose^LN||95|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F
OBX|3|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F
OBX|6|NM|17861-6^Calcium^LN||9.5|mg/dL|8.5-10.5|N|||F
OBX|7|NM|1742-6^ALT^LN||32|U/L|7-56|N|||F
```

---

## 20. ADT A02 - patient transfer between wards (Dutch hospital)

```
MSH|^~\&|ZIS|OLVG|EPD|OLVG|20211203111500||ADT^A02|ADT20211203004|P|2.4|||||NLD|8859/1
EVN|A02|20211203111500
PID|1||33445566^^^^MR~777888999^^^NLMINBIZA^NNNLD||Hendriks&&Hendriks^Cornelia^A.^^^^L||19581124|F|||Westerstraat 88&Westerstraat&88^^Amsterdam^^1015MN^NL^L||020-6789012^PRN^PH
PV1|1|I|ICU^101^A^OLVG|U^Urgent|||890123^Brouwer^T.M.^^^^^^VEKTIS|||CAR^Cardiologie^L|||||||890123^Brouwer^T.M.^^^^^^VEKTIS||B-2021-234^^^OLVG^VN||||||||||||||||||||||||20211201090000|||||3WEST^305^B^OLVG
```
