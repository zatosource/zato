# Epic EHR - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at Michigan Medicine

```
MSH|^~\&|EPIC|UMICH_MED|MIHIN|MIHIN_HIE|20250312084522||ADT^A01^ADT_A01|MSG00001234|P|2.5.1|||AL|NE
EVN|A01|20250312084500|||THARRISON^Harrison^Todd^E^^MD|
PID|1||MRN10287413^^^UMICH^MR||Kowalski^Terrance^Andre||19810623|M|||1738 Cass Ave^^Detroit^MI^48226||3134427819|||M|||318-52-9471|||N||||||||N
PD1|||Michigan Medicine^^^UMICH||||||||02|N|||||A
NK1|1|Kowalski^Monique^R|SPO^Spouse|922 Liberty St^^Ann Arbor^MI^48103|7342819045||EC
PV1|1|I|4EAST^412^A^UMICH^^^^4EAST||||1938472^Abboud^Nadia^K^^^MD^^NPI|8273615^Whitaker^Dennis^L^^^MD^^NPI|MED||||7|||1938472^Abboud^Nadia^K^^^MD^^NPI|IN||BCBS|||||||||||||||||||UH|||||20250312084500
PV2|||^Acute exacerbation of CHF||||||20250312|||||||||||||N|||||||||||||2
IN1|1|001|BCBS_MI^Blue Cross Blue Shield of Michigan|Blue Cross Blue Shield of Michigan^^PO Box 2000^^Detroit^MI^48226||(800)555-1234|GRP7745102|||||||Kowalski^Terrance^A|SEL|19810623|1738 Cass Ave^^Detroit^MI^48226|||1||||||||||||||ACT83029417||||||M
IN2|1||||||||||||||||||||||||||||||||||||||||||Kowalski^Terrance^A
DG1|1||I50.21^Acute systolic heart failure^ICD10|||A|||||||||1
GT1|1||Kowalski^Terrance^Andre||1738 Cass Ave^^Detroit^MI^48226|3134427819||19810623|M||SEL|318-52-9471
```

---

## 2. ADT^A02 - Patient transfer within Henry Ford Hospital

```
MSH|^~\&|EPIC|HFHS_DET|ADT_RECV|HF_CENTRAL|20250405111230||ADT^A02^ADT_A02|MSG00005678|P|2.5.1|||AL|NE
EVN|A02|20250405111200|||VREESE^Reese^Valerie^D^^RN|
PID|1||MRN20364817^^^HFHS^MR||Banks^Shayla^Renee||19710109|F|||24510 Van Dyke Ave^^Center Line^MI^48015||5864417823|||F|||241-68-3095|||N||||||||N
PV1|1|I|5ICU^502^A^HFHS^^^^5ICU||||4820913^Tanaka^Hiroshi^R^^^MD^^NPI||SURG||||2|||4820913^Tanaka^Hiroshi^R^^^MD^^NPI|IN||AETNA|||||||||||||||||||HF|||||20250403150000
PV2|||^Post-operative monitoring status change||||||20250403|20250407||||||||||||N
```

---

## 3. ADT^A03 - Patient discharge from Spectrum Health

```
MSH|^~\&|EPIC|SPEC_GR|MIHIN|MIHIN_HIE|20250418153045||ADT^A03^ADT_A03|MSG00009101|P|2.5.1|||AL|NE
EVN|A03|20250418153000|||KPHAM^Pham^Kevin^T^^MD|
PID|1||MRN30298176^^^SPECTRUM^MR||Salazar^Eduardo^Miguel||19930504|M|||718 Bridge St NW^^Grand Rapids^MI^49504||6163380271|||M|||527-84-1063|||H||||||||N
PV1|1|I|3MED^308^B^SPECTRUM^^^^3MED||||7612340^Dykstra^Karen^M^^^MD^^NPI||MED||||1|||7612340^Dykstra^Karen^M^^^MD^^NPI|IN||PRIORITY|||||||||||||||||||SH|||||20250415091200||20250418153000
PV2|||^Pneumonia community acquired||||||20250415|20250418||||||||||||N
DG1|1||J18.9^Pneumonia unspecified organism^ICD10|||A|||||||||1
DG1|2||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A|||||||||2
```

---

## 4. ADT^A04 - Patient registration at Beaumont Royal Oak ED

```
MSH|^~\&|EPIC|BEAU_RO|ADT_RECV|BEAU_CENTRAL|20250501082315||ADT^A04^ADT_A04|MSG00011234|P|2.5.1|||AL|NE
EVN|A04|20250501082300|||REGISTRATION^Auto^||
PID|1||MRN40183952^^^BEAUMONT^MR||Zielinski^Walter^Francis||19580917|M|||3294 Crooks Rd^^Royal Oak^MI^48073||2484190237|||M|||614-23-8790|||N||||||||N
NK1|1|Zielinski^Barbara^E|SPO^Spouse|3294 Crooks Rd^^Royal Oak^MI^48073|2484190238||EC
NK1|2|Zielinski^Thomas^R|SON^Son|5801 Livernois Ave^^Troy^MI^48098|2487731540||EC
PV1|1|E|ED^T4^A^BEAUMONT^^^^ED||||2918374^Haddad^Layla^F^^^MD^^NPI||EM||||1|||2918374^Haddad^Layla^F^^^MD^^NPI|ER||MEDICARE|||||||||||||||||||BO|||||20250501082300
IN1|1|001|MCARE^Medicare|Medicare^^PO Box 340^^Detroit^MI^48226||(800)555-4567|||||||||Zielinski^Walter^F|SEL|19580917|3294 Crooks Rd^^Royal Oak^MI^48073|||1||||||||||||||1FQ8-RW2-JK49||||||M
DG1|1||R07.9^Chest pain unspecified^ICD10|||A|||||||||1
```

---

## 5. ADT^A08 - Patient information update at Michigan Medicine

```
MSH|^~\&|EPIC|UMICH_MED|MIHIN|MIHIN_HIE|20250511140022||ADT^A08^ADT_A08|MSG00015678|P|2.5.1|||AL|NE
EVN|A08|20250511140000|||ADMIN^Registration^Staff|
PID|1||MRN10287413^^^UMICH^MR||Kowalski^Terrance^Andre||19810623|M|||407 Packard St^^Ann Arbor^MI^48104||7345519823|||M|||318-52-9471|||N||||||||N
PD1|||Michigan Medicine^^^UMICH||||||||02|N|||||A
NK1|1|Kowalski^Monique^R|SPO^Spouse|407 Packard St^^Ann Arbor^MI^48104|7342819045||EC
PV1|1|O|CLINIC^200^A^UMICH^^^^INTMED||||1938472^Abboud^Nadia^K^^^MD^^NPI||MED||||1|||1938472^Abboud^Nadia^K^^^MD^^NPI|OUT||BCBS|||||||||||||||||||UH|||||20250511140000
IN1|1|001|BCBS_MI^Blue Cross Blue Shield of Michigan|Blue Cross Blue Shield of Michigan^^PO Box 2000^^Detroit^MI^48226||(800)555-1234|GRP7745102|||||||Kowalski^Terrance^A|SEL|19810623|407 Packard St^^Ann Arbor^MI^48104|||1||||||||||||||ACT83029417||||||M
```

---

## 6. ORM^O01 - Radiology order at Henry Ford West Bloomfield

```
MSH|^~\&|EPIC|HFHS_WB|RAD_SYS|HF_RAD|20250322091500||ORM^O01^ORM_O01|MSG00020001|P|2.5.1|||AL|NE
PID|1||MRN50718294^^^HFHS^MR||Booker^Tashara^Imani||19850214|F|||6230 Orchard Lake Rd^^West Bloomfield^MI^48322||2487752014|||F|||742-15-9308|||B||||||||N
PV1|1|O|RADWB^100^A^HFHS^^^^RAD||||3901247^Rashid^Omar^A^^^MD^^NPI||RAD||||1|||3901247^Rashid^Omar^A^^^MD^^NPI|OUT||BCBS|||||||||||||||||||HF|||||20250322091500
ORC|NW|ORD789012^EPIC|||||^^^20250322093000^^R||20250322091500|TECH001^Dombrowski^Karen^^||3901247^Rashid^Omar^A^^^MD^^NPI|RADWB|||20250322091500||HFHS_WB^Henry Ford West Bloomfield||||Henry Ford West Bloomfield^4160 John R St^^Detroit^MI^48201
OBR|1|ORD789012^EPIC||71046^XR CHEST 2 VIEWS^CPT^^^^CHEST XRAY||20250322091500|||||||||3901247^Rashid^Omar^A^^^MD^^NPI||||||||||1^^^20250322093000^^R
DG1|1||R05.9^Cough unspecified^ICD10|||A
```

---

## 7. ORU^R01 - Lab result from Michigan Medicine with embedded PDF report

```
MSH|^~\&|EPIC|UMICH_MED|RESULTS|UMICH_LIS|20250410162030||ORU^R01^ORU_R01|MSG00025001|P|2.5.1|||AL|NE
PID|1||MRN60451928^^^UMICH^MR||Chakrabarti^Meera^Sunita||19750830|F|||1024 S State St^^Ann Arbor^MI^48109||7349217834|||F|||831-47-2609|||A||||||||N
PV1|1|I|6ONCO^604^A^UMICH^^^^6ONCO||||5128370^Ellison^Gregory^W^^^MD^^NPI||ONC||||7|||5128370^Ellison^Gregory^W^^^MD^^NPI|IN||UMHS|||||||||||||||||||UH|||||20250408120000
ORC|RE|ORD456789^EPIC|RES456789^LAB||CM||||20250410162000|||5128370^Ellison^Gregory^W^^^MD^^NPI
OBR|1|ORD456789^EPIC|RES456789^LAB|88305^Surgical Pathology^CPT||20250408140000|20250408140500|||COLLECTOR001^Hensley^Brenda^^|||||5128370^Ellison^Gregory^W^^^MD^^NPI||SP25-12345||20250410160000|||F
OBX|1|ED|PATH_RPT^Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFBhdGhvbG9neSBSZXBvcnQpCi9BdXRob3IgKE1pY2hpZ2FuIE1lZGljaW5lIFBhdGhvbG9neSkKL0NyZWF0b3IgKEVwaWMgQmVha2VyIExJUykKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMyAwIFIKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMTUwIDAwMDAwIG4gCjAwMDAwMDAyMDAgMDAwMDAgbiAKMDAwMDAwMDI1MCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjM1MAolJUVPRgo=||||||F|||20250410162000
OBX|2|ST|22637-3^Pathology Report Narrative^LN||LEFT BREAST BIOPSY: Invasive ductal carcinoma, Grade 2. Tumor size 1.4 cm. Margins negative. ER positive, PR positive, HER2 negative.||||||F|||20250410162000
```

---

## 8. ORM^O01 - Medication order at Spectrum Health Butterworth

```
MSH|^~\&|EPIC|SPEC_BW|PHARMACY|SPEC_PHARM|20250428143000||ORM^O01^ORM_O01|MSG00030001|P|2.5.1|||AL|NE
PID|1||MRN70293018^^^SPECTRUM^MR||VanHouten^Gerald^Raymond||19510312|M|||4782 Lake Michigan Dr NW^^Grand Rapids^MI^49534||6164428190|||M|||813-60-4527|||N||||||||N
PV1|1|I|5CARD^510^A^SPECTRUM^^^^5CARD||||6291048^Kapoor^Vikram^S^^^MD^^NPI||CARD||||7|||6291048^Kapoor^Vikram^S^^^MD^^NPI|IN||PRIORITY|||||||||||||||||||SH|||||20250426080000
ORC|NW|ORD901234^EPIC|||||^^^20250428143000^^R||20250428143000|PHARM01^DeGraaf^Steven^^||6291048^Kapoor^Vikram^S^^^MD^^NPI|5CARD
OBR|1|ORD901234^EPIC||RXA001^Metoprolol Tartrate 25mg PO BID^LOCAL||20250428143000
RXO|6918^Metoprolol Tartrate^NDC|25||mg||TAB^Tablet|PO^Oral||||||||6291048^Kapoor^Vikram^S^^^MD^^NPI
RXR|PO^Oral^HL70162
```

---

## 9. SIU^S12 - Appointment scheduling at Michigan Medicine

```
MSH|^~\&|EPIC|UMICH_MED|SCHED|UMICH_SCHED|20250515093000||SIU^S12^SIU_S12|MSG00035001|P|2.5.1|||AL|NE
SCH|APT100234^EPIC|||||MOD^Moderate complexity visit|30^minutes|^^30^20250520100000^20250520103000|||||BOOKED^Booked|2047183^Park^Helen^J^^^MD^^NPI|UMICH_MED^Michigan Medicine|INTMED^Internal Medicine||APT100234^EPIC
PID|1||MRN80519274^^^UMICH^MR||Grabowski^Ryan^Thomas||19890724|M|||831 Packard St^^Ann Arbor^MI^48104||7346618203|||M|||270-91-3845|||N||||||||N
PV1|1|O|INTMED^301^A^UMICH^^^^INTMED||||2047183^Park^Helen^J^^^MD^^NPI||MED||||1|||2047183^Park^Helen^J^^^MD^^NPI|OUT||BCBS
AIG|1||2047183^Park^Helen^J^^^MD^^NPI|PHYSICIAN
AIL|1||INTMED^301^A^UMICH^^^^INTMED|CLINIC
AIP|1||2047183^Park^Helen^J^^^MD^^NPI|PHYSICIAN||20250520100000|30|MIN
```

---

## 10. ADT^A01 - Admission at Sparrow Hospital Lansing

```
MSH|^~\&|EPIC|SPARROW_LAN|MIHIN|MIHIN_HIE|20250603142200||ADT^A01^ADT_A01|MSG00040001|P|2.5.1|||AL|NE
EVN|A01|20250603142100|||ADMISSIONS^Staff^||
PID|1||MRN90417238^^^SPARROW^MR||Carter^Brianna^Nicole||19960213|F|||2805 W Saginaw St^^Lansing^MI^48917||5172839104|||F|||482-70-1396|||B||||||||N
NK1|1|Carter^Leonard^W|FAT^Father|9140 Cedar St^^Lansing^MI^48910|5174480213||EC
PV1|1|I|3OB^312^A^SPARROW^^^^3OB||||7503812^Gutierrez^Sofia^I^^^MD^^NPI|3891205^Freeman^Tamara^N^^^CNM^^NPI|OBG||||7|||7503812^Gutierrez^Sofia^I^^^MD^^NPI|IN||MCARE|||||||||||||||||||SP|||||20250603142100
PV2|||^Labor and delivery||||||20250603||20250605||||||||||||N
IN1|1|001|MEDICAID_MI^Michigan Medicaid|Michigan Dept of Health and Human Services^^PO Box 30195^^Lansing^MI^48909||(800)555-0100|||||||||Carter^Brianna^N|SEL|19960213|2805 W Saginaw St^^Lansing^MI^48917|||1||||||||||||||MAID604821||||||F
DG1|1||O80^Encounter for full-term uncomplicated delivery^ICD10|||A|||||||||1
```

---

## 11. ORU^R01 - Radiology result with embedded report at Henry Ford

```
MSH|^~\&|EPIC|HFHS_DET|RAD_RESULTS|HF_RAD|20250520174500||ORU^R01^ORU_R01|MSG00045001|P|2.5.1|||AL|NE
PID|1||MRN11730294^^^HFHS^MR||Pryor^Dominic^Lamont||19880503|M|||7425 Gratiot Ave^^Detroit^MI^48213||3135840172|||M|||659-01-8243|||B||||||||N
PV1|1|E|ED^B8^A^HFHS^^^^ED||||8102934^Khoury^Sami^J^^^MD^^NPI||EM||||1|||8102934^Khoury^Sami^J^^^MD^^NPI|ER||BCBS|||||||||||||||||||HF|||||20250520170000
ORC|RE|ORD567890^EPIC|RES567890^RAD||CM||||20250520174500|||8102934^Khoury^Sami^J^^^MD^^NPI
OBR|1|ORD567890^EPIC|RES567890^RAD|70553^MRI BRAIN W AND WO CONTRAST^CPT||20250520171000|20250520171500|||TECH002^Lewandowski^Mark^^|||||6028471^Chang^Linda^Y^^^MD^^NPI||RAD25-78901||20250520174000|||F
OBX|1|ED|RAD_RPT^Radiology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMiAwIG9iago8PAovVGl0bGUgKE1SSSBCcmFpbiBSZXBvcnQpCi9BdXRob3IgKEhlbnJ5IEZvcmQgUmFkaW9sb2d5KQovQ3JlYXRvciAoRXBpYyBSYWRpYW50KQovUHJvZHVjZXIgKEVwaWMgU3lzdGVtcykKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDQgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNSAwIFJdCi9Db3VudCAxCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgNCAwIFIKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL0NvbnRlbnRzIDYgMCBSCj4+CmVuZG9iago2IDAgb2JqCjw8Ci9MZW5ndGggMjAwCj4+CnN0cmVhbQpCVAovRjEgMTIgVGYKNzIgNzIwIFRkCihNUkkgQnJhaW4gV2l0aCBhbmQgV2l0aG91dCBDb250cmFzdCkgVGoKMCAtMjAgVGQKKEZpbmRpbmdzOiBObyBhY3V0ZSBpbnRyYWNyYW5pYWwgYWJub3JtYWxpdHkpIFRqCjAgLTIwIFRkCihJbXByZXNzaW9uOiBOb3JtYWwgTVJJIG9mIHRoZSBicmFpbikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTAgMDAwMDAgbiAKMDAwMDAwMDE1MCAwMDAwMCBuIAowMDAwMDAwMjUwIDAwMDAwIG4gCjAwMDAwMDAzNTAgMDAwMDAgbiAKMDAwMDAwMDQ1MCAwMDAwMCBuIAowMDAwMDAwNTUwIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAzIDAgUgo+PgpzdGFydHhyZWYKODAwCiUlRU9GCg==||||||F|||20250520174500
OBX|2|FT|RAD_NARR^Radiology Narrative^LN||MRI BRAIN WITH AND WITHOUT CONTRAST\.br\\.br\CLINICAL INDICATION: Headaches, rule out intracranial pathology\.br\\.br\FINDINGS: No acute intracranial abnormality. No mass, hemorrhage, or midline shift. Normal gray-white matter differentiation.\.br\\.br\IMPRESSION: Normal MRI of the brain.||||||F|||20250520174500
```

---

## 12. MDM^T02 - Document notification at Michigan Medicine

```
MSH|^~\&|EPIC|UMICH_MED|DOC_MGMT|UMICH_DOC|20250612110000||MDM^T02^MDM_T02|MSG00050001|P|2.5.1|||AL|NE
EVN|T02|20250612110000
PID|1||MRN12840395^^^UMICH^MR||Novak^Raymond^Stanley||19680227|M|||519 W Huron St^^Ann Arbor^MI^48103||7349504182|||M|||407-53-2918|||N||||||||N
PV1|1|O|CARDIO^400^A^UMICH^^^^CARDIO||||3712580^Iyer^Deepa^R^^^MD^^NPI||CARD||||1|||3712580^Iyer^Deepa^R^^^MD^^NPI|OUT||BCBS
TXA|1|HP^History and Physical|TX|20250612110000|3712580^Iyer^Deepa^R^^^MD^^NPI||20250612110000|||||DOC25-34567||||||AU
OBX|1|ST|11488-4^Consultation Note^LN||HISTORY AND PHYSICAL - CARDIOLOGY CONSULT\.br\\.br\CHIEF COMPLAINT: Exertional dyspnea and chest tightness\.br\\.br\HPI: 56 yo male with history of HTN, hyperlipidemia presenting with 3 weeks of progressive exertional dyspnea.\.br\\.br\ASSESSMENT: Suspected coronary artery disease. Will schedule stress echo.||||||F
```

---

## 13. ADT^A04 - ED registration at Munson Medical Center Traverse City

```
MSH|^~\&|EPIC|MUNSON_TC|ADT_RECV|MUNSON_CENTRAL|20250710060045||ADT^A04^ADT_A04|MSG00055001|P|2.5.1|||AL|NE
EVN|A04|20250710060000|||REGISTRATION^Auto^||
PID|1||MRN13502847^^^MUNSON^MR||Johansson^Caleb^Weston||20000918|M|||11420 E Cherry Bend Rd^^Traverse City^MI^49684||2314098571|||M|||539-21-7048|||N||||||||N
PV1|1|E|ED^R2^A^MUNSON^^^^ED||||4921085^Henriksen^Laura^M^^^DO^^NPI||EM||||1|||4921085^Henriksen^Laura^M^^^DO^^NPI|ER||PRIORITY|||||||||||||||||||MN|||||20250710060000
DG1|1||S52.501A^Unspecified fracture of lower end of right radius initial encounter^ICD10|||A|||||||||1
```

---

## 14. ADT^A08 - Insurance update at Beaumont Troy

```
MSH|^~\&|EPIC|BEAU_TROY|ADT_RECV|BEAU_CENTRAL|20250801091500||ADT^A08^ADT_A08|MSG00060001|P|2.5.1|||AL|NE
EVN|A08|20250801091500|||ADMIN^Registration^Staff|
PID|1||MRN14620483^^^BEAUMONT^MR||Majewski^Diane^Christine||19740118|F|||5829 Big Beaver Rd^^Troy^MI^48083||2485039172|||F|||720-48-1539|||N||||||||N
PV1|1|O|CLINIC^102^A^BEAUMONT^^^^ORTHO||||8173024^Vandenberg^Craig^S^^^MD^^NPI||ORTH||||1|||8173024^Vandenberg^Craig^S^^^MD^^NPI|OUT||AETNA|||||||||||||||||||BO|||||20250801091500
IN1|1|001|AETNA^Aetna Health|Aetna^^PO Box 14079^^Lexington^KY^40512||(800)555-7890|GRP3029184|||||||Majewski^Diane^C|SEL|19740118|5829 Big Beaver Rd^^Troy^MI^48083|||1||||||||||||||W609243178||||||F
IN1|2|002|BCBS_MI^Blue Cross Blue Shield of Michigan|Blue Cross Blue Shield of Michigan^^PO Box 2000^^Detroit^MI^48226||(800)555-1234|GRP8014293|||||||Majewski^Richard^P|SEL|19720503|5829 Big Beaver Rd^^Troy^MI^48083|||2||||||||||||||ACT41027893||||||M
```

---

## 15. ORM^O01 - CT order at Spectrum Health Butterworth

```
MSH|^~\&|EPIC|SPEC_BW|RAD_SYS|SPEC_RAD|20250822134500||ORM^O01^ORM_O01|MSG00065001|P|2.5.1|||AL|NE
PID|1||MRN15730481^^^SPECTRUM^MR||DeJong^Warren^Arthur||19600425|M|||2914 Eastern Ave SE^^Grand Rapids^MI^49507||6163047219|||M|||815-32-6074|||N||||||||N
PV1|1|I|4SURG^405^A^SPECTRUM^^^^4SURG||||9204718^Boateng^Kwame^O^^^MD^^NPI||SURG||||7|||9204718^Boateng^Kwame^O^^^MD^^NPI|IN||MEDICARE|||||||||||||||||||SH|||||20250820100000
ORC|NW|ORD123456^EPIC|||||^^^20250822140000^^R||20250822134500|TECH003^Visser^Daniel^^||9204718^Boateng^Kwame^O^^^MD^^NPI|4SURG|||20250822134500||SPEC_BW^Spectrum Health Butterworth||||Spectrum Health Butterworth^100 Michigan St NE^^Grand Rapids^MI^49503
OBR|1|ORD123456^EPIC||74178^CT ABDOMEN AND PELVIS W CONTRAST^CPT^^^^CT ABD PELVIS||20250822134500|||||||||9204718^Boateng^Kwame^O^^^MD^^NPI||||||||||1^^^20250822140000^^R
DG1|1||K80.20^Calculus of gallbladder without cholecystitis^ICD10|||A
```

---

## 16. ORU^R01 - CBC results from Michigan Medicine lab

```
MSH|^~\&|EPIC|UMICH_MED|RESULTS|UMICH_LIS|20250903081500||ORU^R01^ORU_R01|MSG00070001|P|2.5.1|||AL|NE
PID|1||MRN16281047^^^UMICH^MR||Jefferson^Alicia^Renee||19910608|F|||1732 Plymouth Rd^^Ann Arbor^MI^48105||7348201493|||F|||603-78-5214|||B||||||||N
PV1|1|O|LAB^100^A^UMICH^^^^LAB||||4019273^Schaefer^Martin^D^^^MD^^NPI||MED||||1|||4019273^Schaefer^Martin^D^^^MD^^NPI|OUT||BCBS|||||||||||||||||||UH|||||20250903080000
ORC|RE|ORD234567^EPIC|RES234567^LAB||CM||||20250903081500|||4019273^Schaefer^Martin^D^^^MD^^NPI
OBR|1|ORD234567^EPIC|RES234567^LAB|58410-2^CBC with Differential^LN||20250903075000|20250903075500|||PHLEB01^Watkins^Sandra^^|||||4019273^Schaefer^Martin^D^^^MD^^NPI||HEM25-45678||20250903081000|||F
OBX|1|NM|718-7^Hemoglobin^LN||13.2|g/dL|12.0-16.0||||F|||20250903081000
OBX|2|NM|4544-3^Hematocrit^LN||39.1|%|36.0-46.0||||F|||20250903081000
OBX|3|NM|6690-2^WBC^LN||7.8|10*3/uL|4.5-11.0||||F|||20250903081000
OBX|4|NM|777-3^Platelets^LN||245|10*3/uL|150-400||||F|||20250903081000
OBX|5|NM|789-8^RBC^LN||4.52|10*6/uL|4.00-5.50||||F|||20250903081000
OBX|6|NM|787-2^MCV^LN||86.5|fL|80.0-100.0||||F|||20250903081000
OBX|7|NM|785-6^MCH^LN||29.2|pg|27.0-31.0||||F|||20250903081000
OBX|8|NM|786-4^MCHC^LN||33.8|g/dL|32.0-36.0||||F|||20250903081000
OBX|9|NM|788-0^RDW^LN||13.1|%|11.5-14.5||||F|||20250903081000
```

---

## 17. SIU^S12 - Surgery scheduling at Henry Ford Hospital

```
MSH|^~\&|EPIC|HFHS_DET|SCHED|HF_SCHED|20250918100000||SIU^S12^SIU_S12|MSG00075001|P|2.5.1|||AL|NE
SCH|APT200345^EPIC|||||SURG^Surgical procedure|120^minutes|^^120^20251002080000^20251002100000|||||BOOKED^Booked|5017482^Coleman^Reginald^T^^^MD^^NPI|HFHS_DET^Henry Ford Hospital|SURG^Surgery||APT200345^EPIC
PID|1||MRN17294105^^^HFHS^MR||Hamdan^Youssef^Khalil||19790810|M|||4218 Schaefer Hwy^^Dearborn^MI^48126||3137201894|||M|||914-35-6720|||N||||||||N
PV1|1|P|PRESURG^100^A^HFHS^^^^PRESURG||||5017482^Coleman^Reginald^T^^^MD^^NPI||SURG||||1|||5017482^Coleman^Reginald^T^^^MD^^NPI|PRE||BCBS
AIG|1||5017482^Coleman^Reginald^T^^^MD^^NPI|SURGEON
AIL|1||OR^3^A^HFHS^^^^MAIN_OR|OPERATING_ROOM
AIP|1||5017482^Coleman^Reginald^T^^^MD^^NPI|SURGEON||20251002080000|120|MIN
DG1|1||M17.11^Primary osteoarthritis right knee^ICD10|||A
```

---

## 18. ADT^A03 - Discharge from Kalamazoo Bronson Methodist

```
MSH|^~\&|EPIC|BRONSON_KZ|MIHIN|MIHIN_HIE|20251005153000||ADT^A03^ADT_A03|MSG00080001|P|2.5.1|||AL|NE
EVN|A03|20251005153000|||DISCHARGE^Staff^||
PID|1||MRN18503921^^^BRONSON^MR||Pawlak^Evelyn^Rose||19650418|F|||1530 W Michigan Ave^^Kalamazoo^MI^49006||2694817503|||F|||352-79-0148|||N||||||||N
PV1|1|I|2MED^218^B^BRONSON^^^^2MED||||6108237^Tran^Binh^H^^^MD^^NPI||MED||||1|||6108237^Tran^Binh^H^^^MD^^NPI|IN||MCARE|||||||||||||||||||BR|||||20251002091500||20251005153000
PV2|||^COPD exacerbation||||||20251002|20251005||||||||||||N
DG1|1||J44.1^Chronic obstructive pulmonary disease with acute exacerbation^ICD10|||A|||||||||1
DG1|2||J96.01^Acute respiratory failure with hypoxia^ICD10|||A|||||||||2
```

---

## 19. ADT^A01 - Neonatal admission at Beaumont Royal Oak

```
MSH|^~\&|EPIC|BEAU_RO|ADT_RECV|BEAU_CENTRAL|20251112083000||ADT^A01^ADT_A01|MSG00085001|P|2.5.1|||AL|NE
EVN|A01|20251112083000|||ADMISSIONS^Auto^||
PID|1||MRN19481207^^^BEAUMONT^MR||BabyBoy^Okonkwo^^^^||20251112|M|||2740 Coolidge Hwy^^Berkley^MI^48072||2487124039|||M|||000-00-0000|||N||||||||N
NK1|1|Okonkwo^Adaeze^Chidinma|MOT^Mother|2740 Coolidge Hwy^^Berkley^MI^48072|2487124039||EC
NK1|2|Okonkwo^Emeka^Tobenna|FAT^Father|2740 Coolidge Hwy^^Berkley^MI^48072|2487124040||EC
PV1|1|I|NICU^N3^A^BEAUMONT^^^^NICU||||7340218^Brennan^Colleen^A^^^MD^^NPI||PED||||7|||7340218^Brennan^Colleen^A^^^MD^^NPI|IN||BCBS|||||||||||||||||||BO|||||20251112083000
PV2|||^Newborn premature 35 weeks||||||20251112||20251119||||||||||||N
IN1|1|001|BCBS_MI^Blue Cross Blue Shield of Michigan|Blue Cross Blue Shield of Michigan^^PO Box 2000^^Detroit^MI^48226||(800)555-1234|GRP2039184|||||||Okonkwo^Emeka^T|SEL|19880911|2740 Coolidge Hwy^^Berkley^MI^48072|||1||||||||||||||ACT70294183||||||M
DG1|1||P07.38^Preterm newborn gestational age 35 completed weeks^ICD10|||A|||||||||1
```

---

## 20. ORU^R01 - Microbiology culture result at Spectrum Health

```
MSH|^~\&|EPIC|SPEC_GR|RESULTS|SPEC_LIS|20251201141500||ORU^R01^ORU_R01|MSG00090001|P|2.5.1|||AL|NE
PID|1||MRN20841023^^^SPECTRUM^MR||Brouwer^Natalie^Christine||19820317|F|||1580 Wealthy St SE^^Grand Rapids^MI^49506||6169301274|||F|||205-81-4397|||N||||||||N
PV1|1|I|3MED^315^A^SPECTRUM^^^^3MED||||3840271^Fernandez^Marco^L^^^MD^^NPI||MED||||7|||3840271^Fernandez^Marco^L^^^MD^^NPI|IN||PRIORITY|||||||||||||||||||SH|||||20251128100000
ORC|RE|ORD345678^EPIC|RES345678^LAB||CM||||20251201141500|||3840271^Fernandez^Marco^L^^^MD^^NPI
OBR|1|ORD345678^EPIC|RES345678^LAB|87070^Culture Bacterial^CPT||20251128140000|20251128141000|||COLLECTOR002^Hoekstra^Jill^^|||||3840271^Fernandez^Marco^L^^^MD^^NPI||MB25-67890||20251201140000|||F
OBX|1|ST|600-7^Bacteria identified^LN||Escherichia coli||||||F|||20251201140000
OBX|2|ST|18907-6^Specimen source^LN||Urine, clean catch||||||F|||20251201140000
OBX|3|NM|564-5^Colony count^LN||>100000|CFU/mL|||||F|||20251201140000
OBX|4|ST|18769-0^Susceptibility Ampicillin^LN||Resistant||||||F|||20251201140000
OBX|5|ST|18993-6^Susceptibility Ciprofloxacin^LN||Susceptible||||||F|||20251201140000
OBX|6|ST|18961-3^Susceptibility Nitrofurantoin^LN||Susceptible||||||F|||20251201140000
OBX|7|ST|18865-6^Susceptibility Trimethoprim-Sulfamethoxazole^LN||Resistant||||||F|||20251201140000
OBX|8|ST|18878-9^Susceptibility Ceftriaxone^LN||Susceptible||||||F|||20251201140000
```
