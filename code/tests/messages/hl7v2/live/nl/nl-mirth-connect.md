# Mirth Connect (NextGen) - real HL7v2 ER7 messages

## 1. ADT^A01 - patient admission (HL7.org v2.8 sample)

```
MSH|^~\&|ADT1|ERASMUS MC|GHH LAB, INC.|ERASMUS MC|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||
EVN|A01|200708181123||
PID|1||PATID1234^5^M11^ADT1^MR^ERASMUS MC~287456912^^^NLMINBIZA^NNNLD||van Dijk^Adriaan^J^III||19610615|M||C|Westersingel 42^^Rotterdam^ZH^3015BA|GL|+31 10-4567890|+31 10-4567891||S||PATID12345001^2^M10^ADT1^AN^A|287456912|12345678^ZH|
NK1|1|van Dijk^Cornelia^M|SPO^SPOUSE||||NK^NEXT OF KIN
PV1|1|I|2000^2012^01||||004777^Brouwer^Theodora^A|||SUR||||ADM|A0|
```

---

## 2. ADT^A01 - patient admission (SIMHOSP/NHS v2.3 sample)

```
MSH|^~\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII
EVN|A01|20200508130643|||C006^Wolters^Femke^^^Dr^^^DRNBR^PRSNL^^^ORGDR|
PID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||de Vries^Saskia^M^^^Miss^^CURRENT||19890118000000|F|||Prinsengracht 263^^Amsterdam^^1016GV^NLD^HOME||020-5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||||
PD1|||FAMILY PRACTICE^^12345|
PV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b|||C006^Wolters^Femke^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||
```

---

## 3. ADT^A01 - patient admission (Mirth Connect / AWS example)

```
MSH|^~\&|SOURCEEHR|WA|MIRTHDST|WA|201611111111||ADT^A01|MSGID10001|P|2.3|
EVN|A01|201611111111||
PID|1|100001^^^1^MRN1|900001||Jansen^Willem^^^^||19601111|M||WH|Kerkstraat 15^^Utrecht^UT^3512AB^NLD||(030)555-2309|||M|NON|384921756|
NK1|1|Jansen^Johanna^|WIFE||(030)555-5555||||NK^NEXT OF KIN
PV1|1|O|1001^2002^01||||123456^Meijer^Hendrik^T^^DR|||||||ADM|A0|
```

---

## 4. ADT^A04 - patient registration (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|MIE|wc_hl7d|recv_facil|20210701123459||ADT^A04^ADT_A01|DSD1625157299701062|P|2.5|||||||||||||
EVN||20210701123459||
PID|1|1059319|1059319^^^MR&1.2.840.114398.1.90.1&ISO^MR^1.2.840.114398.1.90.1&MR&ISO~523718649^^^^SS||Dekker^Anneke^^||19640423000000|F|||Singel 105^^Amsterdam^NH^1012AB^NL||+31 20-5557091^PRN^PH~+31 6-12345678^PRN^CP|||W|||523718649||||||||||||||||||||
PV1|1||^^^MIE||||15104^Visser^Geert^^^^dr.|89^Timmerman^Jacobus|123^Bakker^Pieter^^^^dr.|||||||||||||||||||||||||||||||||||||||||||
GT1|1||DEKKER^ANNEKE||SINGEL 105^^AMSTERDAM^NH^1012AB|+31 20-5557091||19640423000000|F||||||||||||||||||||||||||||||||||||||||||||||
IN1|1|5273||ZILVEREN KRUIS|Postbus 444^^Leiden^ZH^2300AK|||100000291006|||||||ZILVEREN KRUIS|Dekker^Anneke|Self|19640423000000|Singel 105^^Amsterdam^NH^1012AB|||||||||||||||||10122060000|||||||F||||||
```

---

## 5. ADT^A08 - update patient information (Enterprise Health / Mirth)

```
MSH|^~\&|WEBCHART|OLVG|RECEIVING_APPLICATION|RECEIVING_FACILITY|20210701123459||ADT^A08^ADT_A01|DSD1625157299704299|P|2.5|||||||||||||
EVN||20210701123459||
PID|1|1025209|1025209^^^MR&1.2.840.114398.1.90.1&ISO^MR^1.2.840.114398.1.90.1&MR&ISO~841672935^^^^SS||Mulder^Bram^Jan||19461001000000|M||White|Hofweg 12^^Den Haag^ZH^2511AA^NL||+31 70-5553241^PRN^PH^b.mulder@email.nl~+31 6-98765432^PRN^CP||Dutch|M|||841672935|||Not Hispanic or Latino|||||||||||||||||
PV1|1||^^^OLVG||||6^van der Linden^Elisabeth^H.^^^dr.|269^Hoekstra^Daan^D.|231^Kuipers^Floor|||||||||||||||||||||||||||||||||||||||||||
GT1|1||MULDER^BRAM^JAN||HOFWEG 12^^DEN HAAG^ZH^2511AA|+31 70-5553241||19461001000000|M||||||||||||||||||||||||||||||||||||||||||||||
IN1|1|4751|14079|VGZ|Postbus 202^^Arnhem^GE^6800AE||||||||||VGZ|Mulder^Bram^Jan|Self|19461001000000|Hofweg 12^^Den Haag^ZH^2511AA|||||||||||||||||W255837512|||||||M||||||
```

---

## 6. ORU^R01 - Dutch lab results with BSN (HL7 Nederland)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~328917456^^^NLMINBIZA^NNNLD||Bakker&&Bakker&&^Margaretha^^^^^L||19500101|F|||
OBR|1|123|20050701015070^Labosys||||200507010907||||||""|||3004^van den Ende||||200507010907||201708220955||S|F||^^^^^R
OBX|1|ST|266^Bezinking^L^BSE||2|mm/uur|0 - 15|""|||F
OBX|2|ST|325^Leucocyten^L^LEU||6.7|/nl|4.0 - 10.0|""|||F
```

---

## 7. ORU^R01 - ZorgDomein cardiologie referral with embedded PDF (Dutch)

```
MSH|^_\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van den Berg&van den&Berg^P^J^^^^L||20000101|M|||Leidsestraat 88  bis&Leidsestraat&88^bis^Eindhoven^^5611AA^NL^H||040-2839174
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&de Groot^A.B.C.||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9FeHRHU3RhdGUKL1NBIHRydWUKL1NNIDAuMDIKL2NhIDEuMAovQ0EgMS4wCi9BSVMgZmFsc2UKL1NNYXNrIC9Ob25lPj4KZW5kb2JqCjQgMCBvYmoKWy9QYXR0ZXJuIC9EZXZpY2VSR0JdCmVuZG9iago4IDAgb2JqClswIC9YWVogMzUuMDM5OTk5OSAgCjc3My4zNTk5OTkgIDBdCmVuZG9iago5IDAgb2Jq||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 8. ORU^R01 - discrete lab results, hormones and hepatitis panel (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|omg|wc_hl7d|recv_facil|20210709080455||ORU^R01^ORU_R01|DSD1625832295118172|P|2.5|||||||||||||
PID|1|5007|5007^^^MR&1.2.840.114398.1.5110.1&ISO^MR^MR&1.2.840.114398.1.5110.1&ISO||Smit^Thijs^^||19830101|M|||Herengracht 200^^Amsterdam^NH^1016BS||||||||||||||||||||||||||||
ORC|CN||211820124^hexlab-lab|||||||||6^van der Linden^Elisabeth^H.^^^dr.|^^^^BIO^^^^^Biotech Labs||20210701120200||||||||||||||||
OBR|1||GROUP320^100|^H O R M O N E S||20210701120200|20210701120200||||||Patient: Smit, Thijs\X0A\Ordering Physician: van der Linden, Elisabeth\X0A\\X0A\-----------------------------------------------------------------------------------\X0A\211820124|20210701180500||||||||20210709080400|||F|||||||||||||||||||1||||||
OBX|1||3676^TESTOSTERONE, TOTAL|0|531.17|ng/dL|220 - 715||||F|20210701180500|0|20210701120200|00004140^^MS4R||||||||||
OBR|2||GROUP400^100|^INFECTIOUS DISEASE||20210701120200|20210701120200||||||Patient: Smit, Thijs\X0A\Ordering Physician: van der Linden, Elisabeth|20210701180500||||||||20210709080400|||F|||||||||||||||||||2||||||
OBX|2||9472^*ACUTE HEPATITIS PANEL*|0|||||||I|20210701180500|0|20210701120200|HDR80074^^MS4R||||||||||
OBX|3||1139^HEP A IgM|0|NON-REACTIVE||NON-REACTI||||F|20210701180500|0|20210701120200|00001048^^MS4R||||||||||
OBX|4||579^HEP B SURF AG|0|NON-REACTIVE||NON-REACTI||||F|20210701180500|0|20210701120200|00002042^^MS4R||||||||||
OBX|5||699^HEP B CORE IGM|0|NON-REACTIVE||NON-REACTI||||F|20210701180500|0|20210701120200|00001049^^MS4R||||||||||
OBX|6||581^ANTI-HCV|0|NON-REACTIVE||NON-REACTI||||F|20210701180500|0|20210701120200|00002044^^MS4R||||||||||
NTE|1||This test was performed using the Siemens Advia Centaur immunoassay\X0A\method. Values obtained from different assay methods cannot be used\X0A\interchangeably.|TC
```

---

## 9. ORU^R01 - SARS-CoV-2 PCR result with notes (Enterprise Health / Mirth)

```
MSH|^~\&|MIE|SHC|MIE|SU|20210621214932||ORU^R01^ORU_R01|DSD1624337372374298|P|2.5.1|||||||||||||
PID|1|5007|5007^^^MR&1.2.840.114398.1.5110.1&ISO^MR^MR&1.2.840.114398.1.5110.1&ISO||Smit^Thijs^^||19830101|M|||Herengracht 200^^Amsterdam^NH^1016BS||||||||||||||||||||||||||||
PV1|||||||40^Kuipers^Daan^I.^dr.|||||||||||||||||||||||||||||||||||||||||||||
ORC|RE|7913|21S-160VI0363||CM||||||||||||||||||||||||||
OBR|1|7913|21S-160VI0363|LABSARSCOV2^NOVEL CORONAVIRUS 2019 (SARS-COV-2), RT PCR||20210609114100|20210609114100|||||||||40^Kuipers^Daan^I.^dr.||||0|||||F|||||||40^20210614112732||||20210609231214||||||||||||||
NTE|1||Patient: Smit, Thijs|
NTE|2||MR #: 5007|
NTE|3||Ordering Physician: Kuipers, Daan Isaac|
OBX|1|ST|1230303009^SPECIMEN TYPE (SARS-COV-2)^MIE^7918^SPECIMEN TYPE (SARS-COV-2)^WEBCHART||Resp, Upper||||||F|||20210609114100|1020^Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA|1020|||||||||
OBX|2|ST|1230303010^SPECIMEN SOURCE (SARS-COV-2)^MIE^7919^SPECIMEN SOURCE (SARS-COV-2)^WEBCHART||Mid Turbinate Nasal Swab||||||F|||20210609114100|1020^Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA|1020|||||||||
OBX|3|ST|1230303011^SARS-COV-2 RNA^MIE^7920^SARS-COV-2 RNA^WEBCHART||Not Detected||Not Detected||||F|||20210609114100|1020^Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA|1020|||||||||
NTE|1||Methodology: Nucleic Acid Amplification Test (NAAT): RT-PCR or TMA;(Hologic Panther System)|
```

---

## 10. ORM^O01 - lab order, porphobilinogen urine (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|DEV|wc_hl7d|recv_facil|20210413152312||ORM^O01^ORM_O01|DSD1618345392293653|P|2.5|||||||||||||
PID|1|10018|10018^^^MR&1.2.840.114398.1.6629.1&ISO^MR||Wolters^Floor^^^^^L||20210413000000||||Dorpsstraat 22^^Deventer^OV^7411HP^NL^^^OV||^PRN^PH|^WPN^PH|||||||||||||||||||||||||
PV1|1||^^^FREELM|||||||||||||||||||||||||||||||||||||||||||||||^^^^^1.2.840.114398.1.6629||
IN1|1||||||||||||||||||||||||||||||||||||||||||||||C||
ORC|NW|22|||Pending||^^^^^0||20210413152252|89^Medical Informatics Engineering^MIE||8^Hoekstra^Bram^B^^^dr.|^^^^OFFICE^^^^^Huisartsenpraktijk Hoekstra, Bram B. Hoekstra, dr.||||OFFICE||||Huisartsenpraktijk Hoekstra, Bram B. Hoekstra, dr.|Stationsstraat 10^Suite 2^Deventer^OV^7411HK^NL|0570-612345|Stationsstraat 10^Suite 2^Deventer^OV^7411HK|||||||
OBR|1|22||E693^PORPHOBILINOGEN (PBG) URINE - AEL|0|20210413152252|20210413161900|||||||||8^Hoekstra^Bram^B^^^dr.||||||||||||||||||||||||||||||||||
DG1|1|ICD|R05^COUGH^I10|COUGH||||||||||||
OBX|1|NM|C6806^HOURS COLLECTED||0.25||||||||||||||||||||
OBX|2|NM|C6804^TOTAL VOLUME||4||||||||||||||||||||
```

---

## 11. ORM^O01 - COVID test order (Enterprise Health / Mirth)

```
MSH|^~\&|EH|EH|COVID LAB|COVID LAB|20210311091929||ORM^O01^ORM_O01|DSD1615472369786270|P|2.5|||||||||||||
PID|1|101394|101394^^^MR&1.2.840.114398.1.6391.5&ISO^MR||de Jong^Geert^^^^^L||19820101000000|M|||Marktplein 7^^Groningen^GR^9711CV^NL||+31 50-1234567^PRN^PH^g.dejong@email.nl|+31 50-1234568^WPN^PH|||||||||||||||||||||||||
NTE|1|I|COMMENTS|
IN1|1||||||||||||||||||||||||||||||||||||||||||||||C||
ORC|NW|75055|||Pending||^^^^^0||20210311061912|12137^Visser^Maria||1972697324^Bakker^Lotte^^^^^N^NPI|^^^^GRONINGEN^^^^^Groningen||||GRONINGEN||||Groningen|Herestraat 50^^Groningen^GR^9713GZ^NL||Postbus 997377^^Groningen^GR|||||||
OBR|1|75055||94500-6^SARS coronavirus|0|20210311061912|20210311061900||||||||^^^covid_anterior_nares_swab|1972697324^Bakker^Lotte^^^^^N^NPI|||||||||||||||COMMENTS|||||||||||||||||||
OBX|1|ST|^BODY SITE||COVID_ANTERIOR_NARES_SWAB||||||||||||||||||||
```

---

## 12. ORM^O01 - radiology order, ankle x-ray (interfaceware.com / EPIC-style)

```
MSH|^~\&|MESA_OP|CATHARINA|iFW|ABC_RADIOLOGY|||ORM^O01|101104|P|2.3||||||||
PID|1||20891312^^^^EPI||Brouwer^Pieter^H^^dhr.^||19661201|M||AfrAm|Vestdijk 50^^Eindhoven^NB^5611AZ^NL^^^NB|NB|+31 40-2345678|+31 40-2345679||S|| 11480003|471829365||||^^^NB^^
PV1|||^^^CATHARINA ZIEKENHUIS^^^^^||| |1173^Timmerman^Jacobus^A^^^||||||||||||610613||||||||||||||||||||||||||||||||V
ORC|NW|987654^EPIC|76543^EPC||Final||^^^20140418170014^^^^||20140418173314|1148^de Wit^Saskia^^^^||1173^Timmerman^Jacobus^A^^^|1133^^^222^^^^^|(040)222-1122||
OBR|1|363463^EPC|1858^EPC|73610^X-RAY ANKLE 3+ VW^^^X-RAY ANKLE ||||||||||||1173^Timmerman^Jacobus^A^^^|(040)258-8866||||||||Final||^^^20140418170014^^^^|||||6064^Hendriks^Adriaan^^^^||1148010^1A^EAST^X-RAY^^^|^|
DG1||I10|S82^ANKLE FRACTURE^I10|ANKLE FRACTURE||
```

---

## 13. SIU^S12 - new appointment (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|handle|wc_hl7d|recv_facil|20210423091057||SIU^S12^SIU_S12|DSD1619205057152978|P|2.5|||||||||||||
SCH|2588939|2677255|||||ppd 2nd step|NURS^Nurse Encounter|15|MIN|^^^202104270815^202104270830||||||||||||||BOOKED
PID|1|123456|123456^^^MR&1.2.840.114398.1.5881.2&ISO^MR^1.2.840.114398.1.5881.2&MR&ISO~963258^^^ECW&1.2.840.114398.1.5881.3&ISO^MR^1.2.840.114398.1.5881.3&ECW&ISO~517263849^^^^SS|123456^^^MR&1.2.840.114398.1.5881.1&ISO|Vermeer^Femke^L||19830711000000|F||Asian|Oudegracht 30^^Utrecht^UT^3511AR^NL||+31 30-5550101^PRN^PH^f.vermeer@email.nl~+31 6-55500202^PRN^CP|+31 30-5550303^WPN^PH|EN|M|||517263849|||Not Hispanic or Latino|||||||||||||||||NK1|1||||||||||||||||||||||||||||||||||||||
PV1|1||^^^handle|||||||||||||||||||||||||||||||||||||||||||||||||
RGS|1||
AIL|1||^30^^^^^^^Amphia Ziekenhuis|||||||||
AIP|1||12029^van Leeuwen^Theodora^V^^^dr.|RESOURCE|||||||SUBSTITUTE|
```

---

## 14. SIU^S15 - cancelled appointment (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|maui|wc_hl7d|recv_facil|20210428235041||SIU^S15^SIU_S12|DSD1619689841639741|P|2.5|||||||||||||
SCH|2588939|2677255||||NOSHOW^NO SHOW|ppd 2nd step|NURS^Nurse Encounter|15|MIN|^^^202104270815^202104270830|||||||||29^Cronjobs|||||CANCELED
PID|1|123456|123456^^^MR&1.2.840.114398.1.5881.2&ISO^MR^1.2.840.114398.1.5881.2&MR&ISO~963258^^^ECW&1.2.840.114398.1.5881.3&ISO^MR^1.2.840.114398.1.5881.3&ECW&ISO~517263849^^^^SS|123456^^^MR&1.2.840.114398.1.5881.1&ISO|Vermeer^Femke^L||19830711000000|F||Asian|Oudegracht 30^^Utrecht^UT^3511AR^NL||+31 30-5550101^PRN^PH^f.vermeer@email.nl~+31 6-55500202^PRN^CP|+31 30-5550303^WPN^PH|EN|M|||517263849|||Not Hispanic or Latino|||||||||||||||||NK1|1||||||||||||||||||||||||||||||||||||||
NK1|1||||||||||||||||||||||||||||||||||||||
PV1|1||^^^maui|||||||||||||||||||||||||||||||||||||||||||||||||
RGS|1||
AIL|1||^30^^^^^^^Amphia Ziekenhuis|||||||||
AIP|1||12029^van Leeuwen^Theodora^V^^^dr.|RESOURCE|||||||SUBSTITUTE|
```

---

## 15. MDM^T02 - radiology report, thoracic spine (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend||wc_hl7d|recv_facil|20210716121708||MDM^T02^MDM_T02|DSD1626452228213830|P|2.5|||||||||
PID|1|55555|55555^^^FWR&1.2.840.114398.1.13.1&ISO^MR^1.2.840.114398.1.13.1&FWR&ISO~55555^^^TSMI&1.2.840.114398.1.77.1&ISO^MR^1.2.840.114398.1.77.1&TSMI&ISO~88888^^^CAMHBOC&1.2.840.114398.1.4.1&ISO^MR^1.2.840.114398.1.4.1&CAMHBOC&ISO~649271835^^^^SS||Janssen^Lotte^K||19961110000000|F||W|Nassaulaan 5^Apt 705^Breda^NB^4811TC^NL||+31 76-5554073^PRN^PH|||S|||649271835||||||||||||||||||||
PV1|1|OUTPATIENT|CAM^^^^^^^^Amphia Ziekenhuis^fwr|||||||XR|||||||11094^Bos^Hendrik^^^^dr.||10391981|||||||||||||||0|||||||1|||20160502121300||||||341623620160502^^^^^CPSI||
TXA|1|PS|FT|20160502121300||20160502142755|20160502142755|20160502142755|11094^Bos^Hendrik^^^^dr.|||918711^Powerscribe|||||LA|||||11094^Bos^Hendrik^^^^^^^^1^^^^20160502124809|9290^BREDA^RADIOLOGY
OBX|1|ST|14|PS|Amphia Ziekenhuis\X0A\Molengracht 21\X0A\Breda, NB 4818CK\X0A\ORDERING PROVIDER: de Vries, Willem, dr.\X0A\\X0A\PATIENT NAME: Lotte Janssen\X0A\MR: 85459\X0A\DOB: Nov 10, 1996\X0A\\X0A\EXAMINATION: CR THORACIC SPINE 3 VIEW.\X0A\DATE OF EXAM: May 02, 2016 12:13:00 PM.\X0A\INDICATION: back pain, nki, hx arthritis\X0A\Comparison: Chest x-ray 12/3/2014, 4/27/2015, nuclear medicine bone\X0A\scan 4/26/2016.\X0A\NUMBER OF IMAGES: 4\X0A\\X0A\DISCUSSION: There is diffuse bony demineralization, which limits\X0A\evaluation for nondisplaced fractures. Within this limitation,\X0A\vertebral body heights are grossly preserved, as well as can be seen.\X0A\There is multilevel disc space narrowing and associated endplate\X0A\degenerative changes in the thoracic and visualized upper lumbar\X0A\spine. There is mild dextro scoliotic curvature of the upper and mid\X0A\thoracic spine. Small focus of radiotracer activity in the mid\X0A\thoracic spine left of midline could represent chronic changes\X0A\associated with the mild dextroscoliotic curvature. Left ureteral\X0A\stent is incidentally noted.\X0A\\X0A\IMPRESSION: Diffuse bony demineralization, which limits evaluation for\X0A\nondisplaced fractures. No significant compression fracture\X0A\identified. Multilevel degenerative changes. See discussion above.\X0A\\X0A\\X0A\Professional Interpretation by BREDA RADIOLOGY\X0A\Electronically signed by: Bos, dr., Hendrik\X0A\||||||||||||||||||||
NTE|1||CR THORACIC SPINE 3 VIEW|RE
```

---

## 16. MDM^T02 - document with embedded base64 PDF (Enterprise Health / Mirth)

```
MSH|^~\&|EH_MDM|BCC|POST_MEDIA|recv_facil|20220613153036||MDM^T02^MDM_T02|DSD1655148636292112|P|2.3|||||||||||||
PID|1|10019|10019^^^MIE&1.2.840.114398.1.6885.2&ISO^MR^1.2.840.114398.1.6885.2&MIE&ISO~291485736^^^^SS||de Groot^Willem^S.||19541130000000|M||White|Plein 1953 nr 1^^Tilburg^NB^5038EK^NL||+31 13-4440099^PRN^PH^w.degroot@email.nl~+31 6-30700001^PRN^CP||Dutch|M|||291485736|||Not Hispanic or Latino|||||||||||||||||
PV1|1|HISTEXAM|OFFICE^^^^^^^^Rijnstate^BCC||||8^Dekker^Cornelia||9^Jansen^Pieter^M.^^^dr.||||||||8^Dekker^Cornelia|||||||||||||||||0|||||||1|||20100225000000||||||11^^^^^1.2.840.114398.1.6885||
TXA|1|REGFORM|AP|20100312000000||20100323202954|20100323202954|20100324101735|8^Dekker^Cornelia||2^Engineering^Medical^Informatics|298^1.2.840.114398.1.6885|||||DO||||||
OBX|1|ED|17|REGFORM|^^^Base64^JVBERi0xLjEgDSXi48/TDQoxIDAgb2JqDTw8IA0vVHlwZSAvQ2F0YWxvZyANL1BhZ2VzIDMgMCBSIA0+Pg1lbmRvYmoNMiAwIG9iag08PCANL0NyZWF0aW9uRGF0ZSAoRDoyMDIyMDYxMzE1MzAzOSkNL01vZERhdGUgKEQ6MjAyMjA2MTMxNTMwMzkpDS9Qcm9kdWNlciAoTUlFIGltZ2ZpbHRlciB2MS43LjApDS9DcmVhdG9yIChNSUUgaW1nZmlsdGVyIHYxLjcuMCkNPj4gDWVuZG9iag0zIDAgb2JqDTw8IA0vVHlwZSAvUGFnZXMgDS9LaWRzIFsgNCAwIFIgXSANL0NvdW50IDEgDT4+IA1lbmRvYmoNNCAwIG9iag08PA0vVHlwZSAvUGFnZSANL1BhcmVudCAzIDAgUiANL01lZGlhQm94IFswLjAwMDAgMC4wMDAwIDYxMi4wMDAwIDc5Mi4wMDAwXSANL0NvbnRlbnRzIDUgMCBSIA0vUmVzb3VyY2VzIDw8IA0vWE9iamVjdCA8PA0vSW0xIDcgMCBSID4+DS9Qcm9jU2V0IFsgL0ltYWdlQiBdDT4+DT4+DWVuZG9iag01IDAgb2JqDTw8IA0vTGVuZ3RoIDYgMCBSIA0gPj4Nc3RyZWFtDQpxICA2MTIuMDAwMCAwLjAwMDAgMC4wMDAwIDc5Mi4wMDAwIDAuMDAwMCAwLjAwMDAgY20gL0ltMSBEbyBRDQ1lbmRzdHJlYW0NZW5kb2JqDTYgMCBvYmoNNjINZW5kb2JqDTcgMCBvYmoNPDwgDS9MZW5ndGggOCAwIFIgDS9UeXBlIC9YT2JqZWN0IA0vU3VidHlwZSAvSW1hZ2UgDS9OYW1lIC9JbTENL1dpZHRoIDE3MDANL0hlaWdodCAyMjAwDS9CaXRzUGVyQ29tcG9uZW50IDgNL0NvbG9yU3BhY2UgL0RldmljZUdyYXkgDS9GaWx0ZXIgL0ZsYXRlRGVjb2RlICA+Pg1zdHJlYW0NCnic7d1viBznfQfwp7ix5UryGZdLiHBVk0NIlS1hvziwgtCVYPtAC5ZKsQKH3TioYCQ3GCdxfKDWsrFgjVq7pfUthggsRxxxRYItuqJqRDjMkkvRCwVfctgEieMsITeHhaToj2WpYfvMzO7d7mlPJ6eWZlp/Pi9u5pln5pnf7ov9MnPPztbrAAAAAAAAAAAAAAAAAAAAAAA||||||F
```

---

## 17. MDM^T02 - hospital document notification (HL7 Confluence)

```
MSH|^~\&|HIE|ISALA|||20230814022400||MDM^T02^MDM_T02|10819306|P|2.5.1
EVN||20230814022400
PID|||000322330^^^ISALA&1.1.1.1&GUID^MR||Visser^Jan^Hendrik^Jr.^^^D||19941201|M|||Kamperweg 92^^Zwolle^OV^8011AB^NL^P^^OV||(038)144-1441^P^H^^^038^1443441|||||1055989633^^^^HAR
PV1||I|F1N^F151^F151-01^FTH^^^^^HILLS 1 North Oncolog||||1123456771^Bakker^Maria^K^^^^^NPI^^^^NPI||||||||||||1234567891|||||||||||||||||||||||||20230729081300
ORC|RE|ORD777999^SndFac^1.2.3.4.5^ISO|432344432^FillerFac^8.7.6.5.4^ISO|GORD874299^SndFac^1.2.3.4.5^ISO|CM||||20230814011500+0000|||5742200012^Verhoeven^Adriaan^^^^^^&372526&L^L^^^NPI|||||Isala^L||||||||||||I|
TQ1|1|1
OBR|1||432344432^FillerFac^8.7.6.5.4^ISO|11502-2^^LN^^Laboratory Report|||20130408141909.0+0000|20130411154157.0+0000||||||||5742200012^Verhoeven^Adriaan^^^^^^&372526&L^L^^^NPI|||||||||F|
TXA|1|PN|TX|20230820174913|1780850958^Timmerman^Margaretha^^^^^^^^^^TIMMERMAN, MARGARETHA|20230820174913||20230820191149|5742200012^Verhoeven^Adriaan^^^^^^&372526&L^L^^^NPI|1123456771^Bakker^Maria^K^^^^^NPI^^^^NPI||3738931392^ISALA&1.1.1.1&GUID||||PN_Verhoeven_20230820174913.RTF|AU|R|AV||||^TIMMERMAN, MARGARETHA|PHYSICIAN
OBX|1|TX|85202^Transcription Authentication Interface Message Text|1|Transcription Authentication Interface Message Text||||||F
OBX|2|FT|1055860039^Critical Values - Text||Critical Values Entered On: 08/22/2023 2:11 EDT \.br\ Performed On: 08/22/2023 2:11 EDT by WOLTERS, JOHANNA C||||||F|||20230822021111||
OBX|3|ST|&GDT^Critical Values-String||Table formatting from the original result was not included.||||||F
OBX|4|ED|1111.2^PHQ-9 Depression Screen PDF^L^44249-1^PHQ-9 quick depression assessment panel [Reported.PHQ]^LN||CareCoordination^AP^PDF^Base64^||||||F
```

---

## 18. DFT^P03 - financial transaction, office visit (Enterprise Health / Mirth)

```
MSH|^~\&|WCDataSend|SENDING_FACILITY|wc_hl7d|recv_facil|20210723040307||DFT^P03^DFT_P03|DSD1627027387370313|P|2.5|||||||||||||
EVN||20210723040307||
PID|1||222222^^^MR&1.2.840.114398.1.6421.1&ISO^MR^1.2.840.114398.1.6421.1&MR&ISO~736514289^^^^SS||Vermeer^Anneke^^||19860214000000|F|||Rijnkade 10^^Arnhem^GE^6811HA^NL||+31 26-5551416^PRN^PH|||||506214^^^MNGWCTR1D|736514289||||||||||||||||||||
FT1|1|506214||20210719154000||CG|HAIR5PAN|Hair Test 5 Panel||1|79.000000|79.000000||||^^^^MNGWCTR1D^^^^WorkHealth Arnhem||VISIT||220^Verpleegkundige^WH Arnhem|||506214|47600^Dekker^Femke^^^Mevr.^LPN|HAIR5PAN||||
PR1|1|CPT|HAIR5PAN|Hair Test 5 Panel|20210719154000|||||||220^Verpleegkundige^WH Arnhem||||
FT1|2|506214||20210719154000||CG|NON9|NONDOT 9 Panel (30GQ)||1|46.000000|46.000000||||^^^^MNGWCTR1D^^^^WorkHealth Arnhem||VISIT||220^Verpleegkundige^WH Arnhem|||506214|47600^Dekker^Femke^^^Mevr.^LPN|NON9||||
PR1|2|CPT|NON9|NONDOT 9 Panel (30GQ)|20210719154000|||||||220^Verpleegkundige^WH Arnhem||||
```

---

## 19. VXU^V04 - immunization record, Tdap (Enterprise Health / Mirth)

```
MSH|^~\&|WebChart|SIISCLIENT23068|Impact|SIIS|20210723110514-0400||VXU^V04^VXU_V04|WCCHIRPA740231627052714|P|2.5.1|||AL|AL|||||Z22^CDCPHINVS|SIISCLIENT23068^^^^^NIST-AA-IZ-1&2.16.840.1.113883.3.72.5.40.9&ISO^XX^^^ohioHealth
PID|1||88888^^^MR^MR~836291475^^^MAA^SS||Bosman^Daan^^^^^L||19890513000000|U||2106-3^White^HL70005|Hoofdstraat 45^^Tilburg^NB^5038AE^NL^L^^NB||^PRN^PH^^^013^5555394|||||||||2186-5^Not Hispanic or Latino^HL70189
ORC|RE||74023^ohiohealth^1.2.840.114398.1.6426^ISO|||||||81^Mulder^Saskia^^^^^^ohiohealth&1.2.840.114398.1.6426&ISO^L^^^PRN^^^^^^^^RN||1669786117^Wolters^Elisabeth^^^^^^NPI^L^^^NPI^^^^^^^^CNP
RXA|0|999|20210723110400|20210723110400|115^Tdap^CVX|0.5|mL^MilliLiter [SI Volume Units]^UCUM||00^New immunization record^NIP001|81^Mulder^Saskia^^^^^^ohiohealth&1.2.840.114398.1.6426&ISO^L^^^PRN^^^^^^^^RN|||||U6964AA|52020223000000|PMC^Sanofi Pasteur^MVX|||CP|A|20210723110508
RXR|IM^Intramuscular^HL70162|RD^Right Deltoid^HL70163
OBX|1|ST|VFC-STATUS^VFC STATUS^STC|1|V00||||||F|||20210723|||VXC40^Eligibility captured at the immunization level^CDCPHINVS
```

---

## 20. ORU^R01 - retinal screening, diabetic retinopathy critical (IRIS / Mirth)

```
MSH|^\~\&|IRIS|IRIS|Vendor|Vendor|20191223193115||ORU^R01|191223193115|P|2.3
PID||MRNtest123|MRNtest123||de Vries^Cornelia^^||19391126|F||||||||||593172846|
PV1|1|O|WRSIM||||NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI|NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI|||||||||NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI||593172846|||||||||||||||||||||||||20191223012424|20191223012424
ORC|RE|12378912|799932^IRIS||F||||20191223193115|||NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI
OBR|1|12378912|799932^IRIS|^FUNDUS PHOTOGRAPHY^EAP^^FUNDAL PHOTO|||20191223012424|||||||20191223012424||NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI||||||20191223012555|||F|||||||1234567890^Meijer^Geert^^^dr.^dr.^^^^^^NPI
OBX|1|ST|SEVERITY^^IRIS|1|CRITICAL|||AA|||F
OBX|2|ST|LEFTDIABRETIN^^IRIS|2|Severe|||AA|||F
OBX|3|ST|LEFTMACEDEMA^^IRIS|3|Severe|||AA|||F
OBX|4|ST|LEFTOTHERRETIN^^IRIS|4|Suspected Vein Occlusion|||A|||F
OBX|5|ST|LEFTQUALAPP^^IRIS|5|Gradable Image||||||F
OBX|6|ST|RIGHTDIABRETIN^^IRIS|6|Moderate|||A|||F
OBX|7|ST|RIGHTMACEDEMA^^IRIS|7|Moderate|||A|||F
OBX|8|ST|RIGHTOTHERRETIN^^IRIS|8|Suspected Dry AMD|||A|||F
OBX|9|ST|RIGHTQUALAPP^^IRIS|9|Gradable Image||||||F
OBX|10|FT|Result^^IRIS|001|Retinal Study Result for Cornelia de Vries||||||F
OBX|11|FT|Result^^IRIS|002|||||||F
OBX|12|FT|Result^^IRIS|003|Cornelia de Vries, a 80 y/o, F (DOB: 11-26-1939, MRN: MRNtest123)||||||F
OBX|13|FT|Result^^IRIS|004|presented to Rijnstate Oogheelkunde on 12-23-2019 for a retinal imaging study of the left and right eyes.||||||F
OBX|14|FT|Result^^IRIS|005|||||||F
OBX|15|FT|Result^^IRIS|006|Based on the findings of the study, the following is recommended for Cornelia de Vries||||||F
OBX|16|FT|Result^^IRIS|007|Next Available Appointment: Refer patient to a retina specialist, next available appointment.||||||F
OBX|17|FT|Result^^IRIS|008|||||||F
OBX|18|FT|Result^^IRIS|009|Interpreting Provider's Comments: No comments provided||||||F
OBX|19|FT|Result^^IRIS|010|Diagnoses Present: E11.3311 - Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye||||||F
OBX|20|FT|Result^^IRIS|011|E11.3412 - Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye||||||F
OBX|21|FT|Result^^IRIS|012|||||||F
OBX|22|FT|Result^^IRIS|013|Right eye findings: Diabetic Retinopathy: Moderate||||||F
OBX|23|FT|Result^^IRIS|014|Macular Edema: Moderate||||||F
OBX|24|FT|Result^^IRIS|015|Other: Suspected Dry AMD||||||F
OBX|25|FT|Result^^IRIS|016|||||||F
OBX|26|FT|Result^^IRIS|017|Left eye findings: Diabetic Retinopathy: Severe||||||F
OBX|27|FT|Result^^IRIS|018|Macular Edema: Severe||||||F
OBX|28|FT|Result^^IRIS|019|Other: Suspected Vein Occlusion||||||F
OBX|29|FT|Result^^IRIS|020|||||||F
OBX|30|FT|Result^^IRIS|021|||||||F
OBX|31|FT|Result^^IRIS|022|This result was electronically signed by Meijer, Geert, on 12-23-2019 07:25:55 UTC time.||||||F
OBX|32|FT|Result^^IRIS|023|||||||F
OBX|33|FT|Result^^IRIS|024|NOTE: Any pathology noted on this diabetic retinal evaluation should be confirmed by an appropriate ophthalmic examination.||||||F
OBX|34|RP|LINK^^PDFLINK|34|https://api.retinalscreenings.com/api/PatientOrders/GetSingleResultForDisplayInEmr?patientOrderId=799932\T\asPdf=True\T\isPreliminary=False\T\auth=6DCAFF6AC2A555F00F9E470D221B6A077C3497A668B1EEBBB4983C8D98672F8FBA00707190026B817325C2A088725B5A0E5D7AB659AC0790C1C1D22B2C50F897\T\asAddendum=False||||||F
```
