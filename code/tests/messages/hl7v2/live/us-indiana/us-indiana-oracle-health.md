# Oracle Health (Cerner Millennium) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Franciscan Health Indianapolis

```
MSH|^~\&|CERMILL|FRAN_INDY|ADT_RECV|IHIE|20250310063000||ADT^A01^ADT_A01|CERN00001234|P|2.3|||AL|NE
EVN|A01|20250310063000|||MREDMOND^Redmond^Mark^E^^^MD
PID|1||FMRN40087612^^^FRAN^MR||Calloway^Jerome^Davion||19720815|M|||2345 South Emerson Ave^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5551122|^WPN^PH^^1^317^5553344|ENG|M|CAT|SSN418-52-7163^^^SS|||||||||||N
NK1|1|Calloway^Tamika^Denise|SPO|2345 South Emerson Ave^^Indianapolis^IN^46203^US|^PRN^PH^^1^317^5551122
PV1|1|I|3EAST^312^A^FRAN_INDY^^^^3EAST||||MREDMOND^Redmond^Mark^E^^^MD|LCONRAD^Conrad^Laura^M^^^MD||MED|||7|||MREDMOND^Redmond^Mark^E^^^MD|IP||||||||||||||||||FRAN_INDY|||||20250310063000
PV2|||^Acute exacerbation of COPD
IN1|1|ANTHEM1^Anthem BCBS|ANT093|Anthem Blue Cross Blue Shield||||||||20240101|20251231|||PPO|Calloway^Jerome^Davion|Self|19720815|2345 South Emerson Ave^^Indianapolis^IN^46203^US
DG1|1||J44.1^Chronic obstructive pulmonary disease with acute exacerbation^ICD10|||A
```

---

## 2. ORU^R01 - Basic metabolic panel from Franciscan Health

```
MSH|^~\&|CERMILL|FRAN_LAB|LAB_RECV|FRAN|20250311092000||ORU^R01^ORU_R01|CERN00004567|P|2.3|||AL|NE
PID|1||FMRN40087612^^^FRAN^MR||Calloway^Jerome^Davion||19720815|M|||2345 South Emerson Ave^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5551122
PV1|1|I|3EAST^312^A^FRAN_INDY||||MREDMOND^Redmond^Mark^E^^^MD
ORC|RE|CORD100234|CRES100234||CM||||20250311091500|||MREDMOND^Redmond^Mark^E^^^MD
OBR|1|CORD100234|CRES100234|24320-4^Basic Metabolic Panel^LN|||20250311080000||||||||MREDMOND^Redmond^Mark^E^^^MD||||||20250311092000|||F
OBX|1|NM|2345-7^Glucose^LN||112|mg/dL|70-99|H|||F|||20250311092000
OBX|2|NM|3094-0^BUN^LN||22|mg/dL|7-20|H|||F|||20250311092000
OBX|3|NM|2160-0^Creatinine^LN||1.4|mg/dL|0.7-1.3|H|||F|||20250311092000
OBX|4|NM|2951-2^Sodium^LN||138|mmol/L|136-145|N|||F|||20250311092000
OBX|5|NM|2823-3^Potassium^LN||4.8|mmol/L|3.5-5.1|N|||F|||20250311092000
OBX|6|NM|2075-0^Chloride^LN||101|mmol/L|98-106|N|||F|||20250311092000
OBX|7|NM|2028-9^CO2^LN||22|mmol/L|21-32|N|||F|||20250311092000
OBX|8|NM|17861-6^Calcium^LN||9.1|mg/dL|8.5-10.5|N|||F|||20250311092000
```

---

## 3. ORM^O01 - Chest X-ray order at Deaconess Health Evansville

```
MSH|^~\&|CERMILL|DEAC_EVN|RAD_SYS|DEAC|20250312143500||ORM^O01^ORM_O01|CERN00007890|P|2.3|||AL|NE
PID|1||DMRN50076821^^^DEAC^MR||Bridwell^Tonya^Renee||19650427|F|||890 Lincoln Ave^^Evansville^IN^47714^US||^PRN^PH^^1^812^5552233||ENG|M|BAP|SSN531-27-8946^^^SS
PV1|1|E|ED^TRIAGE^^DEAC_EVN||||RPENDLETON^Pendleton^Roger^C^^^MD|||EM|||1|||RPENDLETON^Pendleton^Roger^C^^^MD|ER
ORC|NW|CORD200345||GRP200345|SC||||20250312143000|||RPENDLETON^Pendleton^Roger^C^^^MD|ED^TRIAGE^^DEAC_EVN
OBR|1|CORD200345||71046^Chest X-Ray 2 Views^CPT|||20250312144500||||||||RPENDLETON^Pendleton^Roger^C^^^MD||||||||||1^^^20250312144500^^S
DG1|1||R06.02^Shortness of breath^ICD10|||A
```

---

## 4. DFT^P03 - Charge posting for outpatient visit at Franciscan Health

```
MSH|^~\&|CERMILL|FRAN_MOOR|FIN_SYS|FRAN|20250313161000||DFT^P03^DFT_P03|CERN00011234|P|2.4|||AL|NE
EVN|P03|20250313161000
PID|1||FMRN40193847^^^FRAN^MR||Troutman^Derek^Alan||19800321|M|||456 State Road 67^^Mooresville^IN^46158^US||^PRN^PH^^1^317^5554455||ENG|M|NON|SSN642-38-1759^^^SS
PV1|1|O|ORTHO^201^^FRAN_MOOR||||SCRAWFORD^Crawford^Scott^J^^^MD|||ORT|||1|||SCRAWFORD^Crawford^Scott^J^^^MD|OP
FT1|1||20250313|20250313|CG|99213^Office Visit Level 3^CPT||||1||||||ORTHO^201^^FRAN_MOOR|SCRAWFORD^Crawford^Scott^J^^^MD
FT1|2||20250313|20250313|CG|73560^X-Ray Knee 3 Views^CPT||||1||||||RAD^101^^FRAN_MOOR|SCRAWFORD^Crawford^Scott^J^^^MD
DG1|1||M17.11^Primary osteoarthritis, right knee^ICD10|||A
IN1|1|ANTHEM1^Anthem BCBS|ANT093|Anthem Blue Cross Blue Shield||||||||20240101|20251231|||PPO|Troutman^Derek^Alan|Self|19800321|456 State Road 67^^Mooresville^IN^46158^US
```

---

## 5. SIU^S12 - Appointment scheduled at Deaconess Gateway Hospital

```
MSH|^~\&|CERMILL|DEAC_GW|SCHED_SYS|DEAC|20250314100000||SIU^S12^SIU_S12|CERN00014567|P|2.4|||AL|NE
SCH|CAPT890123|CAPT890123|||OFFICE^Office Visit|ROUTINE^Routine||20|MIN|^^20^20250321090000^20250321092000|||||AREDDY^Reddy^Ashok^N^^^MD|^WPN^PH^^1^812^5556677|GASTRO^204^^DEAC_GW|||||BOOKED
PID|1||DMRN50034981^^^DEAC^MR||Wagoner^Phyllis^June||19490612|F|||123 Oak Hill Rd^^Newburgh^IN^47630^US||^PRN^PH^^1^812^5558899||ENG|W|MET|SSN753-49-2618^^^SS
PV1|1|O|GASTRO^204^^DEAC_GW||||AREDDY^Reddy^Ashok^N^^^MD|||GI|||1|||AREDDY^Reddy^Ashok^N^^^MD|OP
RGS|1||GASTRO^204^^DEAC_GW
AIS|1||GI_CONSULT^Gastroenterology Consultation|20250321090000|||20|MIN
AIP|1||AREDDY^Reddy^Ashok^N^^^MD|ATTENDING
```

---

## 6. ADT^A03 - Patient discharge from Deaconess Midtown Evansville

```
MSH|^~\&|CERMILL|DEAC_MID|ADT_RECV|IHIE|20250315140000||ADT^A03^ADT_A03|CERN00017890|P|2.3|||AL|NE
EVN|A03|20250315140000|||RPENDLETON^Pendleton^Roger^C^^^MD
PID|1||DMRN50052913^^^DEAC^MR||Wilkerson^Earl^Preston||19530910|M|||567 Riverside Dr^^Evansville^IN^47713^US||^PRN^PH^^1^812^5551144||ENG|M|PRO|SSN864-51-3097^^^SS
PV1|1|I|2SOUTH^210^A^DEAC_MID||||RPENDLETON^Pendleton^Roger^C^^^MD|NKELLY^Kelly^Natalie^A^^^MD||MED|||7|||RPENDLETON^Pendleton^Roger^C^^^MD|IP||||||||||||||||||DEAC_MID|||||20250311080000|||20250315140000
PV2|||^Congestive heart failure, acute on chronic
DG1|1||I50.21^Acute systolic (congestive) heart failure^ICD10|||A
DG1|2||I50.22^Chronic systolic (congestive) heart failure^ICD10|||A
```

---

## 7. ORU^R01 - Urinalysis results from Franciscan Health Crown Point

```
MSH|^~\&|CERMILL|FRAN_CP|LAB_RECV|FRAN|20250316083000||ORU^R01^ORU_R01|CERN00021234|P|2.3|||AL|NE
PID|1||FMRN40261574^^^FRAN^MR||Salinas^Gabriela^Lucia||19910704|F|||789 Broadway^^Crown Point^IN^46307^US||^PRN^PH^^1^219^5553322||SPA|S|CAT|SSN907-63-4281^^^SS
PV1|1|O|UCLINIC^105^^FRAN_CP||||DTANAKA^Tanaka^Douglas^L^^^MD|||FM|||1|||DTANAKA^Tanaka^Douglas^L^^^MD|OP
ORC|RE|CORD300456|CRES300456||CM||||20250316082500|||DTANAKA^Tanaka^Douglas^L^^^MD
OBR|1|CORD300456|CRES300456|24356-8^Urinalysis Complete^LN|||20250316073000||||||||DTANAKA^Tanaka^Douglas^L^^^MD||||||20250316083000|||F
OBX|1|ST|5778-6^Color^LN||Yellow||Yellow|N|||F|||20250316083000
OBX|2|ST|5767-9^Appearance^LN||Clear||Clear|N|||F|||20250316083000
OBX|3|NM|2965-2^Specific Gravity^LN||1.018||1.005-1.030|N|||F|||20250316083000
OBX|4|NM|2756-5^pH^LN||6.0||5.0-8.0|N|||F|||20250316083000
OBX|5|ST|5792-7^Glucose UA^LN||Negative||Negative|N|||F|||20250316083000
OBX|6|ST|20454-5^Protein UA^LN||Trace||Negative|A|||F|||20250316083000
OBX|7|ST|5794-3^Hemoglobin UA^LN||Negative||Negative|N|||F|||20250316083000
OBX|8|ST|5799-2^Leukocyte Esterase^LN||Negative||Negative|N|||F|||20250316083000
```

---

## 8. ORU^R01 - Echocardiogram report with embedded PDF from Deaconess

```
MSH|^~\&|CERMILL|DEAC_EVN|CARDIO_RECV|DEAC|20250317113000||ORU^R01^ORU_R01|CERN00024567|P|2.4|||AL|NE
PID|1||DMRN50052913^^^DEAC^MR||Wilkerson^Earl^Preston||19530910|M|||567 Riverside Dr^^Evansville^IN^47713^US||^PRN^PH^^1^812^5551144
PV1|1|O|CARDIO^301^^DEAC_EVN||||MFERGUSON^Ferguson^Mitchell^D^^^MD|||CAR|||1|||MFERGUSON^Ferguson^Mitchell^D^^^MD|OP
ORC|RE|CORD400567|CRES400567||CM||||20250317112500|||MFERGUSON^Ferguson^Mitchell^D^^^MD
OBR|1|CORD400567|CRES400567|93306^Echocardiogram Complete^CPT|||20250317100000||||||||MFERGUSON^Ferguson^Mitchell^D^^^MD||||||20250317113000|||F
OBX|1|TX|93306^Echocardiogram Complete^CPT||FINDINGS: LV ejection fraction estimated at 35-40%. Moderate global hypokinesis. Mild mitral regurgitation. No pericardial effusion. IMPRESSION: Moderate LV systolic dysfunction.||||||F
OBX|2|ED|PDF^Echocardiogram Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 9. ADT^A08 - Patient update at Franciscan Health Michigan City

```
MSH|^~\&|CERMILL|FRAN_MC|ADT_RECV|IHIE|20250318091500||ADT^A08^ADT_A08|CERN00027890|P|2.3|||AL|NE
EVN|A08|20250318091500|||REG_CLERK
PID|1||FMRN40395026^^^FRAN^MR||Grabowski^Walter^Anton||19680222|M|||345 Franklin St^^Michigan City^IN^46360^US||^PRN^PH^^1^219^5557788|^WPN^PH^^1^219^5559900|POL|M|CAT|SSN078-74-5319^^^SS
PD1|||FRANCISCAN MC PRIMARY^^40334|JSRINIVASAN^Srinivasan^Jay^K^^^MD
PV1|1|O|PCP^102^^FRAN_MC||||JSRINIVASAN^Srinivasan^Jay^K^^^MD|||FM|||1|||JSRINIVASAN^Srinivasan^Jay^K^^^MD|OP
NK1|1|Grabowski^Irene^Cecilia|SPO|345 Franklin St^^Michigan City^IN^46360^US|^PRN^PH^^1^219^5557788
IN1|1|UHC789^United Healthcare|UHC047|United Healthcare||||||||20250101|20251231|||HMO|Grabowski^Walter^Anton|Self|19680222|345 Franklin St^^Michigan City^IN^46360^US
```

---

## 10. ORM^O01 - Colonoscopy order at Deaconess Gateway

```
MSH|^~\&|CERMILL|DEAC_GW|PROC_SYS|DEAC|20250319103000||ORM^O01^ORM_O01|CERN00031234|P|2.3|||AL|NE
PID|1||DMRN50034981^^^DEAC^MR||Wagoner^Phyllis^June||19490612|F|||123 Oak Hill Rd^^Newburgh^IN^47630^US||^PRN^PH^^1^812^5558899||ENG|W|MET|SSN753-49-2618^^^SS
PV1|1|O|GASTRO^204^^DEAC_GW||||AREDDY^Reddy^Ashok^N^^^MD|||GI|||1|||AREDDY^Reddy^Ashok^N^^^MD|OP
ORC|NW|CORD500678||GRP500678|SC||||20250319102500|||AREDDY^Reddy^Ashok^N^^^MD|GASTRO^204^^DEAC_GW
OBR|1|CORD500678||45378^Colonoscopy Diagnostic^CPT|||20250326073000||||||||AREDDY^Reddy^Ashok^N^^^MD||||||||||1^^^20250326073000^^R
DG1|1||Z12.11^Encounter for screening for malignant neoplasm of colon^ICD10|||A
```

---

## 11. ORU^R01 - Lipid panel from Franciscan Health Indianapolis

```
MSH|^~\&|CERMILL|FRAN_INDY|LAB_RECV|FRAN|20250320141500||ORU^R01^ORU_R01|CERN00034567|P|2.3|||AL|NE
PID|1||FMRN40482710^^^FRAN^MR||Hubbard^Terrence^Wayne||19770918|M|||1234 Harding St^^Indianapolis^IN^46221^US||^PRN^PH^^1^317^5556611||ENG|M|NON|SSN129-83-6042^^^SS
PV1|1|O|PCP^201^^FRAN_INDY||||KGUPTA^Gupta^Kavita^P^^^MD|||FM|||1|||KGUPTA^Gupta^Kavita^P^^^MD|OP
ORC|RE|CORD600789|CRES600789||CM||||20250320141000|||KGUPTA^Gupta^Kavita^P^^^MD
OBR|1|CORD600789|CRES600789|24331-1^Lipid Panel^LN|||20250320080000||||||||KGUPTA^Gupta^Kavita^P^^^MD||||||20250320141500|||F
OBX|1|NM|2093-3^Total Cholesterol^LN||232|mg/dL|<200|H|||F|||20250320141500
OBX|2|NM|2571-8^Triglycerides^LN||178|mg/dL|<150|H|||F|||20250320141500
OBX|3|NM|2085-9^HDL Cholesterol^LN||38|mg/dL|>40|L|||F|||20250320141500
OBX|4|NM|13457-7^LDL Cholesterol Calc^LN||158|mg/dL|<100|H|||F|||20250320141500
OBX|5|NM|13458-5^VLDL Cholesterol Calc^LN||36|mg/dL|5-40|N|||F|||20250320141500
```

---

## 12. ADT^A04 - ER registration at Franciscan Health Hammond

```
MSH|^~\&|CERMILL|FRAN_HAM|ADT_RECV|IHIE|20250321192000||ADT^A04^ADT_A04|CERN00037890|P|2.3|||AL|NE
EVN|A04|20250321192000|||TRIAGE_RN
PID|1||FMRN40518263^^^FRAN^MR||Beasley^Darnell^Tyrone||19850411|M|||890 Calumet Ave^^Hammond^IN^46324^US||^PRN^PH^^1^219^5554411||ENG|S|BAP|SSN238-94-5172^^^SS
PV1|1|E|ED^TRIAGE^^FRAN_HAM||||HOWENS^Owens^Howard^P^^^MD|||EM|||1|||HOWENS^Owens^Howard^P^^^MD|ER
NK1|1|Beasley^Gloria^Marie|MTH|890 Calumet Ave^^Hammond^IN^46324^US|^PRN^PH^^1^219^5554412
IN1|1|MDCD01^Indiana Medicaid|MDCD047|Indiana Medicaid||||||||20250101|20251231|||MEDICAID|Beasley^Darnell^Tyrone|Self|19850411|890 Calumet Ave^^Hammond^IN^46324^US
DG1|1||R10.9^Unspecified abdominal pain^ICD10|||A
```

---

## 13. SIU^S12 - Surgery scheduled at Franciscan Health Indianapolis

```
MSH|^~\&|CERMILL|FRAN_INDY|SCHED_SYS|FRAN|20250322085000||SIU^S12^SIU_S12|CERN00041234|P|2.4|||AL|NE
SCH|CAPT901234|CAPT901234|||SURGERY^Surgical Procedure|ELECTIVE^Elective||120|MIN|^^120^20250405070000^20250405090000|||||JBREWER^Brewer^Jonathan^W^^^MD|^WPN^PH^^1^317^5552200|SURG^OR3^^FRAN_INDY|||||BOOKED
PID|1||FMRN40193847^^^FRAN^MR||Troutman^Derek^Alan||19800321|M|||456 State Road 67^^Mooresville^IN^46158^US||^PRN^PH^^1^317^5554455
PV1|1|O|SURG^OR3^^FRAN_INDY||||JBREWER^Brewer^Jonathan^W^^^MD|||ORT|||1|||JBREWER^Brewer^Jonathan^W^^^MD|OP
RGS|1||SURG^OR3^^FRAN_INDY
AIS|1||TKR_RT^Total Knee Replacement Right|20250405070000|||120|MIN
AIP|1||JBREWER^Brewer^Jonathan^W^^^MD|PRIMARY_SURGEON
```

---

## 14. ORU^R01 - Colonoscopy report with embedded PDF from Deaconess

```
MSH|^~\&|CERMILL|DEAC_GW|GI_RECV|DEAC|20250326152000||ORU^R01^ORU_R01|CERN00044567|P|2.4|||AL|NE
PID|1||DMRN50034981^^^DEAC^MR||Wagoner^Phyllis^June||19490612|F|||123 Oak Hill Rd^^Newburgh^IN^47630^US||^PRN^PH^^1^812^5558899
PV1|1|O|ENDO^101^^DEAC_GW||||AREDDY^Reddy^Ashok^N^^^MD|||GI
ORC|RE|CORD500678|CRES500678||CM||||20250326151500|||AREDDY^Reddy^Ashok^N^^^MD
OBR|1|CORD500678|CRES500678|45378^Colonoscopy Diagnostic^CPT|||20250326073000||||||||AREDDY^Reddy^Ashok^N^^^MD||||||20250326152000|||F
OBX|1|TX|45378^Colonoscopy Diagnostic^CPT||FINDINGS: Cecum reached. Two 5mm tubular adenomas in sigmoid colon removed by snare polypectomy. No other lesions. Prep quality good. RECOMMENDATION: Repeat colonoscopy in 3 years.||||||F
OBX|2|ED|PDF^Colonoscopy Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 15. ADT^A01 - Admission to Franciscan Health Crown Point

```
MSH|^~\&|CERMILL|FRAN_CP|ADT_RECV|IHIE|20250327071500||ADT^A01^ADT_A01|CERN00047890|P|2.3|||AL|NE
EVN|A01|20250327071500|||DTANAKA^Tanaka^Douglas^L^^^MD
PID|1||FMRN40673194^^^FRAN^MR||Szymanski^Loretta^Mae||19430505|F|||456 Lake Shore Dr^^Crown Point^IN^46307^US||^PRN^PH^^1^219^5551133||POL|W|CAT|SSN341-07-8253^^^SS|||||||||||N
NK1|1|Szymanski^Gerald^Thomas|SON|789 Maple Ave^^Crown Point^IN^46307^US|^PRN^PH^^1^219^5551134
PV1|1|I|2NORTH^205^A^FRAN_CP^^^^2NORTH||||DTANAKA^Tanaka^Douglas^L^^^MD|BHARMON^Harmon^Beth^R^^^MD||MED|||7|||DTANAKA^Tanaka^Douglas^L^^^MD|IP||||||||||||||||||FRAN_CP|||||20250327071500
PV2|||^Urinary tract infection
IN1|1|MCARE01^Medicare|MCR058|Medicare Part A||||||||20230101|99991231|||MEDICARE|Szymanski^Loretta^Mae|Self|19430505|456 Lake Shore Dr^^Crown Point^IN^46307^US
DG1|1||N39.0^Urinary tract infection, site not specified^ICD10|||A
```

---

## 16. DFT^P03 - Inpatient charges at Deaconess Midtown

```
MSH|^~\&|CERMILL|DEAC_MID|FIN_SYS|DEAC|20250328160000||DFT^P03^DFT_P03|CERN00051234|P|2.4|||AL|NE
EVN|P03|20250328160000
PID|1||DMRN50052913^^^DEAC^MR||Wilkerson^Earl^Preston||19530910|M|||567 Riverside Dr^^Evansville^IN^47713^US||^PRN^PH^^1^812^5551144
PV1|1|I|2SOUTH^210^A^DEAC_MID||||RPENDLETON^Pendleton^Roger^C^^^MD|||MED|||7|||RPENDLETON^Pendleton^Roger^C^^^MD|IP
FT1|1||20250312|20250315|CG|99223^Initial Hospital Care Level 3^CPT||||1||||||2SOUTH^210^^DEAC_MID|RPENDLETON^Pendleton^Roger^C^^^MD
FT1|2||20250313|20250313|CG|93306^Echocardiogram Complete^CPT||||1||||||CARDIO^301^^DEAC_EVN|MFERGUSON^Ferguson^Mitchell^D^^^MD
FT1|3||20250311|20250315|CG|99232^Subsequent Hospital Care Level 2^CPT||||3||||||2SOUTH^210^^DEAC_MID|RPENDLETON^Pendleton^Roger^C^^^MD
DG1|1||I50.21^Acute systolic (congestive) heart failure^ICD10|||A
IN1|1|MCARE01^Medicare|MCR058|Medicare Part A||||||||20200101|99991231|||MEDICARE|Wilkerson^Earl^Preston|Self|19530910|567 Riverside Dr^^Evansville^IN^47713^US
```

---

## 17. ORU^R01 - Thyroid function tests from Franciscan Health

```
MSH|^~\&|CERMILL|FRAN_INDY|LAB_RECV|FRAN|20250329094500||ORU^R01^ORU_R01|CERN00054567|P|2.3|||AL|NE
PID|1||FMRN40749308^^^FRAN^MR||Desai^Priya^Nandini||19780630|F|||2345 Georgetown Rd^^Indianapolis^IN^46234^US||^PRN^PH^^1^317^5558877||HIN|M|HIN|SSN452-16-7934^^^SS
PV1|1|O|ENDO^102^^FRAN_INDY||||CWILKINS^Wilkins^Craig^B^^^MD|||END|||1|||CWILKINS^Wilkins^Craig^B^^^MD|OP
ORC|RE|CORD700890|CRES700890||CM||||20250329094000|||CWILKINS^Wilkins^Craig^B^^^MD
OBR|1|CORD700890|CRES700890|24348-5^Thyroid Panel^LN|||20250329080000||||||||CWILKINS^Wilkins^Craig^B^^^MD||||||20250329094500|||F
OBX|1|NM|3016-3^TSH^LN||8.2|mIU/L|0.27-4.20|H|||F|||20250329094500
OBX|2|NM|3026-2^Free T4^LN||0.7|ng/dL|0.9-1.7|L|||F|||20250329094500
OBX|3|NM|3053-6^Free T3^LN||2.1|pg/mL|2.0-4.4|N|||F|||20250329094500
```

---

## 18. ADT^A02 - Patient transfer within Deaconess Health

```
MSH|^~\&|CERMILL|DEAC_EVN|ADT_RECV|IHIE|20250330083000||ADT^A02^ADT_A02|CERN00057890|P|2.3|||AL|NE
EVN|A02|20250330083000|||CHARGE_RN
PID|1||DMRN50061347^^^DEAC^MR||Hendricks^Vernon^Lloyd||19470318|M|||234 First Ave^^Evansville^IN^47710^US||^PRN^PH^^1^812^5553366||ENG|M|MET|SSN573-21-8460^^^SS
PV1|1|I|ICU^101^A^DEAC_EVN^^^^ICU||||TNARANG^Narang^Tarun^A^^^MD|RPENDLETON^Pendleton^Roger^C^^^MD||MED|||7|||TNARANG^Narang^Tarun^A^^^MD|IP||||||||||||||||||DEAC_EVN|||||20250327190000
PV2|||^Acute myocardial infarction
```

---

## 19. ORU^R01 - Blood culture from Franciscan Health Hammond

```
MSH|^~\&|CERMILL|FRAN_HAM|LAB_RECV|FRAN|20250331102000||ORU^R01^ORU_R01|CERN00061234|P|2.3|||AL|NE
PID|1||FMRN40518263^^^FRAN^MR||Beasley^Darnell^Tyrone||19850411|M|||890 Calumet Ave^^Hammond^IN^46324^US||^PRN^PH^^1^219^5554411
PV1|1|I|3WEST^315^A^FRAN_HAM||||HOWENS^Owens^Howard^P^^^MD|||MED|||7|||HOWENS^Owens^Howard^P^^^MD|IP
ORC|RE|CORD800901|CRES800901||CM||||20250331101500|||HOWENS^Owens^Howard^P^^^MD
OBR|1|CORD800901|CRES800901|600-7^Blood Culture^LN|||20250321200000||||||||HOWENS^Owens^Howard^P^^^MD||||||20250331102000|||F
OBX|1|ST|600-7^Blood Culture^LN||POSITIVE||Negative|A|||F|||20250323060000
OBX|2|ST|634-6^Organism Identified^LN||Staphylococcus aureus||||||F|||20250324120000
OBX|3|ST|18907-6^Methicillin Resistance^LN||MRSA detected||||||A|||F|||20250325080000
OBX|4|ST|18900-1^Vancomycin Susceptibility^LN||Susceptible (MIC 1.0 mcg/mL)||||||F|||20250325080000
OBX|5|ST|18993-6^Daptomycin Susceptibility^LN||Susceptible (MIC 0.5 mcg/mL)||||||F|||20250325080000
```

---

## 20. ORU^R01 - CT Abdomen report with embedded PDF from Franciscan Health

```
MSH|^~\&|CERMILL|FRAN_INDY|RAD_RECV|FRAN|20250401091000||ORU^R01^ORU_R01|CERN00064567|P|2.4|||AL|NE
PID|1||FMRN40482710^^^FRAN^MR||Hubbard^Terrence^Wayne||19770918|M|||1234 Harding St^^Indianapolis^IN^46221^US||^PRN^PH^^1^317^5556611
PV1|1|E|ED^TRIAGE^^FRAN_INDY||||PNAIR^Nair^Pallavi^N^^^MD|||EM|||1|||PNAIR^Nair^Pallavi^N^^^MD|ER
ORC|RE|CORD900012|CRES900012||CM||||20250401090500|||PNAIR^Nair^Pallavi^N^^^MD
OBR|1|CORD900012|CRES900012|74178^CT Abdomen Pelvis with Contrast^CPT|||20250401074500||||||||PNAIR^Nair^Pallavi^N^^^MD||||||20250401091000|||F
OBX|1|TX|74178^CT Abdomen Pelvis with Contrast^CPT||IMPRESSION: 1. Acute appendicitis with periappendiceal fat stranding. No abscess. 2. No free air. Recommend surgical consultation.||||||F
OBX|2|ED|PDF^CT Abdomen Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```
