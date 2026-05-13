# InterSystems HealthShare Health Connect (CHI) - real HL7v2 ER7 messages

## 1

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318092030+0000||ADT^A01^ADT_A01|HC20250318092030001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20250318092000|||EMP100^Tierney^Bríd^^^Ms.^RN
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M|||14 Sundrive Road^^Dublin 12^^D12 K4N8^IE^H||+35314129876^PRN^PH~+353871234567^PRN^CP||EN|S|||||||IE||||N
NK1|1|Murphy^Aisling^^Ms.||+353871234567^PRN^PH||MTH
NK1|2|Murphy^Tadhg^^Mr.||+353871234568^PRN^PH||FTH
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN^^^^^ED||||PRV100^Hennessy^Roisín^^^Dr.^MD|PRV101^Flanagan^Eoin^^^Dr.^MD|PED||||7|||PRV100^Hennessy^Roisín^^^Dr.^MD|IP||GMS|||||||||||||||||||CHI_CRUMLIN|||||20250318091500
PV2|||^Febrile seizure||||||||||3|||||20250318|20250320
AL1|1|DA|A001^Amoxicillin^LOCAL||Urticaria|20240601
IN1|1|GMS001^GMS Medical Card|HSE_GMS|HSE Primary Care||||||||||20250101|20251231
```

---

## 2

```
MSH|^~\&|EPIC|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250425101530+0100||ADT^A04^ADT_A01|HC20250425101530001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20250425101500|||SYS^System^Epic
PID|1||CHI667788^^^EPIC^MR~1911142367WA^^^PPS^NNNIRL||Kelly^Caoimhe^R^^Miss||20191114|F|||33 Griffith Avenue^^Dublin 9^^D09 T2P7^IE^H||+35318374521^PRN^PH~+353859876543^PRN^CP||EN|S|||||||IE
NK1|1|Kelly^Orla^^Ms.||+353859876543^PRN^PH||MTH
PV1|1|O|CARD^OPD-CARD-3^1^CHI_TEMPLE||||PRV110^Corcoran^Declan^^^Prof.^MD||CARD||||1|||PRV110^Corcoran^Declan^^^Prof.^MD|OUT||GMS|||||||||||||||||||CHI_TEMPLE|||||20250425100000
```

---

## 3

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250502141500+0100||ADT^A03^ADT_A03|HC20250502141500001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A03|20250502141500|||EMP110^Doherty^Gráinne^^^Ms.^RN
PID|1||CHI221144^^^EPIC^MR~2008243156F^^^PPS^NNNIRL||Gallagher^Oisín^D^^Master||20200824|M|||18 Whitehall Road^^Dublin 9^^D09 E5W2^IE^H||+35318567432^PRN^PH||EN|S|||||||IE
NK1|1|Gallagher^Deirdre^^Ms.||+353862345678^PRN^PH||MTH
PV1|1|I|SURG^ST_JOSEPHS^BED-3^CHI_CRUMLIN||||PRV120^Redmond^Fiachra^^^Mr.^MD||PAED_SURG||||3|||PRV120^Redmond^Fiachra^^^Mr.^MD|IP||GMS|||||||||||||||||||CHI_CRUMLIN|||||20250430083000|||20250502141500
DG1|1||K35.8^Acute appendicitis^ICD10||20250430|A
PR1|1||47.01^Laparoscopic appendicectomy^ICD9|||20250430103000
```

---

## 4

```
MSH|^~\&|LABSYS|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318112045+0000||ORU^R01^ORU_R01|HCLAB20250318112045001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN||||PRV100^Hennessy^Roisín^^^Dr.^MD
ORC|RE|EPORD20250318001|CHILAB20250318001||CM||||20250318100000+0000
OBR|1|EPORD20250318001|CHILAB20250318001|58410-2^CBC panel^LN|||20250318093000+0000||||||||PRV100^Hennessy^Roisín^^^Dr.^MD||||||20250318111500+0000|||F
OBX|1|NM|6690-2^WBC^LN||18.5|10*9/L|6.0-17.5|H|||F
OBX|2|NM|718-7^Haemoglobin^LN||112|g/L|105-135|N|||F
OBX|3|NM|777-3^Platelets^LN||310|10*9/L|150-450|N|||F
OBX|4|NM|751-8^Neutrophils^LN||12.4|10*9/L|1.5-8.5|H|||F
OBX|5|NM|731-0^Lymphocytes^LN||4.8|10*9/L|2.0-8.0|N|||F
OBX|6|NM|2160-0^Creatinine^LN||28|umol/L|15-35|N|||F
OBX|7|NM|2951-2^Sodium^LN||138|mmol/L|135-145|N|||F
OBX|8|NM|2823-3^Potassium^LN||4.5|mmol/L|3.5-5.5|N|||F
OBX|9|NM|1988-5^CRP^LN||45.2|mg/L|<5.0|HH|||F
```

---

## 5

```
MSH|^~\&|LABSYS|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250319160030+0000||ORU^R01^ORU_R01|HCLAB20250319160030001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN||||PRV100^Hennessy^Roisín^^^Dr.^MD
ORC|RE|EPORD20250319001|CHILAB20250319001||CM||||20250319140000+0000
OBR|1|EPORD20250319001|CHILAB20250319001|600-7^Blood culture^LN|||20250318095000+0000||||||||PRV100^Hennessy^Roisín^^^Dr.^MD||||||20250319155000+0000|||F
OBX|1|CE|600-7^Blood culture result^LN||260385009^No growth at 48 hours^SCT||||||F
OBX|2|ST|600-7^Specimen type^LN||Peripheral venous blood x2 bottles||||||F
OBX|3|ST|600-7^Incubation^LN||Aerobic and anaerobic 48 hours||||||F
NTE|1||No organisms isolated. If clinically indicated, cultures will be held for 5 days.
```

---

## 6

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318094500+0000||ORM^O01^ORM_O01|HCORD20250318094500001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN||||PRV100^Hennessy^Roisín^^^Dr.^MD
ORC|NW|EPORD20250318002|||SC||||20250318094500+0000|||PRV100^Hennessy^Roisín^^^Dr.^MD
OBR|1|EPORD20250318002||71046^Chest X-ray AP and lateral^CPT4|||20250318094500+0000|||||||||PRV100^Hennessy^Roisín^^^Dr.^MD|||||||||||^STAT
DG1|1||R56.0^Febrile seizure^ICD10
NTE|1||2 year old, febrile seizure, query lower respiratory tract infection. Please assess for consolidation.
```

---

## 7

```
MSH|^~\&|RIS|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318121530+0000||ORU^R01^ORU_R01|HCRAD20250318121530001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN||||PRV100^Hennessy^Roisín^^^Dr.^MD
ORC|RE|EPORD20250318002|CHIRAD20250318001||CM
OBR|1|EPORD20250318002|CHIRAD20250318001|71046^Chest X-ray AP and lateral^CPT4|||20250318100000+0000||||||||PRV130^Moloney^Cathal^^^Dr.^MD||||||20250318120000+0000|||F
OBX|1|FT|71046^Chest X-ray^CPT4||CHEST X-RAY AP AND LATERAL\.br\\.br\Clinical Details: 2 year old male, febrile seizure, query LRTI\.br\\.br\Comparison: No prior imaging available\.br\\.br\Findings:\.br\- Heart size normal\.br\- Right lower lobe airspace opacity consistent with consolidation\.br\- No pleural effusion\.br\- No pneumothorax\.br\- Osseous structures normal\.br\\.br\Impression: Right lower lobe pneumonia.||||||F
```

---

## 8

```
MSH|^~\&|EPIC|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250410140000+0100||SIU^S12^SIU_S12|HCSCH20250410140000001|P|2.5.1|||AL|NE||UNICODE UTF-8
SCH|APT334455^EPIC|APT334455^EPIC|||||ROUTINE^Routine^HL70277|FOLLOWUP^Follow-up^LOCAL|30|MIN|^^30^202505061000^202505061030|||||PRV110^Corcoran^Declan^^^Prof.^MD|^WPN^PH^^^^^+35318784100|CHI_TEMPLE_CARDOPD^CHI_TEMPLE||Booked
PID|1||CHI667788^^^EPIC^MR~1911142367WA^^^PPS^NNNIRL||Kelly^Caoimhe^R^^Miss||20191114|F|||33 Griffith Avenue^^Dublin 9^^D09 T2P7^IE^H
PV1|1|O|CARD^OPD-CARD-3^1^CHI_TEMPLE||||PRV110^Corcoran^Declan^^^Prof.^MD
RGS|1|A
AIS|1|A|CARD_FU^Cardiology Follow-up^LOCAL|||202505061000|0|MIN|30|MIN
AIP|1|A|PRV110^Corcoran^Declan^^^Prof.^MD|ATT^Attending^HL70443
AIL|1|A|CARD^OPD-CARD-3^1^CHI_TEMPLE||202505061000|0|MIN|30|MIN
```

---

## 9

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250415090045+0100||ADT^A08^ADT_A01|HC20250415090045001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20250415090000|||SYS^System^Epic
PID|1||CHI221144^^^EPIC^MR~2008243156F^^^PPS^NNNIRL||Gallagher^Oisín^D^^Master||20200824|M|||18 Whitehall Road^^Dublin 9^^D09 E5W2^IE^H~6 Fortfield Park^^Dublin 6W^^D6W R3K8^IE^M||+35318567432^PRN^PH~+353862345678^PRN^CP||EN|S|||||||IE
NK1|1|Gallagher^Deirdre^^Ms.||+353862345678^PRN^PH||MTH
NK1|2|Gallagher^Lorcan^^Mr.||+353862345679^PRN^PH||FTH
PV1|1|O|SURG^OPD-GEN-1^1^CHI_CRUMLIN||||PRV120^Redmond^Fiachra^^^Mr.^MD
```

---

## 10

```
MSH|^~\&|CARDIOSYS|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250506113000+0100||ORU^R01^ORU_R01|HCCRD20250506113000001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI667788^^^EPIC^MR~1911142367WA^^^PPS^NNNIRL||Kelly^Caoimhe^R^^Miss||20191114|F
PV1|1|O|CARD^OPD-CARD-3^1^CHI_TEMPLE||||PRV110^Corcoran^Declan^^^Prof.^MD
ORC|RE|EPORD20250506001|CHICRD20250506001||CM
OBR|1|EPORD20250506001|CHICRD20250506001|93306^Echocardiogram^CPT4|||20250506100000+0100||||||||PRV110^Corcoran^Declan^^^Prof.^MD||||||20250506112500+0100|||F
OBX|1|FT|93306^Echocardiogram findings^CPT4||TRANSTHORACIC ECHOCARDIOGRAM\.br\\.br\Indication: Follow-up small perimembranous VSD\.br\\.br\Findings:\.br\- Small perimembranous VSD, L-R shunt, Vmax 4.2 m/s\.br\- Estimated gradient 71 mmHg (restrictive)\.br\- Normal LV systolic function, EF 68%\.br\- No RV volume overload\.br\- Trivial tricuspid regurgitation\.br\- No aortic regurgitation\.br\- Normal pulmonary artery pressures\.br\\.br\Conclusion: Stable small restrictive perimembranous VSD\.br\No intervention required. Annual follow-up.||||||F
OBX|2|NM|18043-0^LV Ejection Fraction^LN||68|%|55-75|N|||F
OBX|3|NM|LP264622-2^VSD Vmax^LN||4.2|m/s|||||F
```

---

## 11

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318101500+0000||ORM^O01^ORM_O01|HCRX20250318101500001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_ED^ED-RESUS^1^CHI_CRUMLIN||||PRV100^Hennessy^Roisín^^^Dr.^MD
ORC|NW|EPRX20250318001|||SC||||20250318101500+0000|||PRV100^Hennessy^Roisín^^^Dr.^MD
RXO|J01DD04^Ceftriaxone^ATC|||50|mg/kg|IV|Once daily||G||5|DAY
NTE|1||Weight 12.8kg. Dose 640mg IV OD. Febrile seizure with confirmed RLL pneumonia. Penicillin allergy documented - use cephalosporin.
```

---

## 12

```
MSH|^~\&|LABSYS|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250429161030+0100||ORU^R01^ORU_R01|HCLAB20250429161030001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI221144^^^EPIC^MR~2008243156F^^^PPS^NNNIRL||Gallagher^Oisín^D^^Master||20200824|M
PV1|1|I|SURG^PRE-OP^1^CHI_CRUMLIN||||PRV120^Redmond^Fiachra^^^Mr.^MD
ORC|RE|EPORD20250429001|CHILAB20250429001||CM||||20250429150000+0100
OBR|1|EPORD20250429001|CHILAB20250429001|COAG^Coagulation screen^LOCAL|||20250429143000+0100||||||||PRV120^Redmond^Fiachra^^^Mr.^MD||||||20250429160500+0100|||F
OBX|1|NM|5902-2^PT^LN||12.5|sec|10.5-13.5|N|||F
OBX|2|NM|6301-6^INR^LN||1.0||0.8-1.2|N|||F
OBX|3|NM|3173-2^APTT^LN||28.4|sec|25.0-35.0|N|||F
OBX|4|NM|3255-7^Fibrinogen^LN||3.2|g/L|1.5-4.0|N|||F
```

---

## 13

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250318143000+0000||ADT^A02^ADT_A02|HC20250318143000001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A02|20250318143000|||EMP100^Tierney^Bríd^^^Ms.^RN
PID|1||CHI334455^^^EPIC^MR~2302071892T^^^PPS^NNNIRL||Murphy^Darragh^P^^Master||20230207|M
PV1|1|I|PAED_MED^ST_ANNES^BED-8^CHI_CRUMLIN^^^^^MED||||PRV100^Hennessy^Roisín^^^Dr.^MD||PED||||7|||PRV100^Hennessy^Roisín^^^Dr.^MD|IP||GMS|||||||||||||||||||CHI_CRUMLIN|||||20250318091500
PV2|||^Admitted with febrile seizure and right lower lobe pneumonia
```

---

## 14

```
MSH|^~\&|NEUROPHYSIOL|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250520142000+0100||ORU^R01^ORU_R01|HCEEG20250520142000001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI445599^^^EPIC^MR~2104183478G^^^PPS^NNNIRL||Brennan^Éabha^S^^Miss||20210418|F|||22 Botanic Road^^Dublin 9^^D09 W6R1^IE^H
PV1|1|O|NEURO^EEG-LAB^1^CHI_TEMPLE||||PRV140^Maguire^Sorcha^^^Prof.^MD
ORC|RE|EPORD20250520001|CHIEEG20250520001||CM
OBR|1|EPORD20250520001|CHIEEG20250520001|11524-6^EEG study^LN|||20250520100000+0100||||||||PRV140^Maguire^Sorcha^^^Prof.^MD||||||20250520140000+0100|||F
OBX|1|FT|11524-6^EEG report^LN||EEG REPORT\.br\\.br\Clinical Details: 4-year-old female, two unprovoked generalised tonic-clonic seizures\.br\\.br\Recording: 45-minute routine awake and drowsy EEG\.br\\.br\Background: Symmetrical posterior dominant rhythm at 7Hz, appropriate for age\.br\Intermittent bilateral frontocentral theta activity during drowsiness\.br\\.br\Abnormalities: Brief bursts of generalised 3Hz spike-and-wave discharge,\.br\lasting 1.5-2 seconds, occurring 4 times during hyperventilation\.br\\.br\Impression: Abnormal EEG. Generalised spike-and-wave discharges consistent\.br\with genetic generalised epilepsy. Clinical correlation recommended.||||||F
```

---

## 15

```
MSH|^~\&|EPIC|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250501091500+0100||MDM^T02^MDM_T02|HCDOC20250501091500001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20250501091500
PID|1||CHI221144^^^EPIC^MR~2008243156F^^^PPS^NNNIRL||Gallagher^Oisín^D^^Master||20200824|M
PV1|1|I|SURG^ST_JOSEPHS^BED-3^CHI_CRUMLIN||||PRV120^Redmond^Fiachra^^^Mr.^MD
TXA|1|OP^Operative Note^HL70270|TX||||20250430180000+0100||PRV120^Redmond^Fiachra^^^Mr.^MD||||HCDOC-2025-55667||||||AU
OBX|1|FT|11504-8^Surgical operation note^LN||OPERATIVE NOTE\.br\\.br\Procedure: Laparoscopic appendicectomy\.br\Surgeon: Mr Fiachra Redmond, Consultant Paediatric Surgeon\.br\Anaesthetist: Dr Niamh Whelan\.br\Date: 30/04/2025\.br\\.br\Indication: Acute appendicitis\.br\\.br\Findings: Inflamed non-perforated appendix with surrounding exudate\.br\No free fluid. Caecum and terminal ileum normal\.br\\.br\Procedure: Three-port laparoscopic appendicectomy performed\.br\Mesoappendix divided with diathermy. Appendix divided with endoloop\.br\Specimen retrieved via umbilical port\.br\\.br\Post-op: Stable. IV antibiotics 24hrs then oral step-down.||||||F
```

---

## 16

```
MSH|^~\&|LABSYS|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250612103045+0100||ORU^R01^ORU_R01|HCLAB20250612103045001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI990011^^^EPIC^MR~2206281734H^^^PPS^NNNIRL||Sullivan^Fiadh^N^^Miss||20220628|F|||45 Ennis Road^^Limerick^^V94 T3K2^IE^H
PV1|1|O|IMMUNO^OPD-IMM-1^1^CHI_CRUMLIN||||PRV150^Duggan^Colm^^^Prof.^MD
ORC|RE|EPORD20250612001|CHILAB20250612001||CM||||20250612090000+0100
OBR|1|EPORD20250612001|CHILAB20250612001|RAST^Specific IgE panel^LOCAL|||20250610100000+0100||||||||PRV150^Duggan^Colm^^^Prof.^MD||||||20250612102500+0100|||F
OBX|1|NM|6106-9^Total IgE^LN||245|kU/L|<60|H|||F
OBX|2|NM|6206-7^Peanut IgE^LN||34.5|kUA/L|<0.35|H|||F
OBX|3|NM|6248-9^Cow milk IgE^LN||0.18|kUA/L|<0.35|N|||F
OBX|4|NM|6276-0^Egg white IgE^LN||12.8|kUA/L|<0.35|H|||F
OBX|5|NM|6082-2^Wheat IgE^LN||0.22|kUA/L|<0.35|N|||F
OBX|6|NM|6189-5^Tree nut mix IgE^LN||8.4|kUA/L|<0.35|H|||F
NTE|1||Significant peanut and egg white sensitisation. Tree nut cross-reactivity. Cow milk and wheat negative. Recommend supervised oral food challenge for egg.
```

---

## 17

```
MSH|^~\&|PATHSYS|CHI_CRUMLIN|HEALTHCONNECT|CHI_HUB|20250505161500+0100||ORU^R01^ORU_R01|HCPATH20250505161500001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI221144^^^EPIC^MR~2008243156F^^^PPS^NNNIRL||Gallagher^Oisín^D^^Master||20200824|M
PV1|1|I|SURG^ST_JOSEPHS^BED-3^CHI_CRUMLIN||||PRV120^Redmond^Fiachra^^^Mr.^MD
ORC|RE|EPORD20250505001|CHIPATH20250505001||CM
OBR|1|EPORD20250505001|CHIPATH20250505001|88304^Surgical pathology^CPT4|||20250430120000+0100||||||||PRV120^Redmond^Fiachra^^^Mr.^MD||||||20250505160000+0100|||F
OBX|1|FT|22637-3^Path report^LN||HISTOPATHOLOGY REPORT\.br\\.br\Specimen: Appendix\.br\\.br\Macroscopy: Appendix measuring 55mm in length, 8mm diameter\.br\Serosal surface congested with fibrinous exudate\.br\\.br\Microscopy: Transmural acute inflammation with neutrophilic\.br\infiltration of muscularis propria and serosa\.br\Mucosal ulceration present. No perforation\.br\No faecolith identified\.br\\.br\Diagnosis: Acute suppurative appendicitis without perforation.||||||F
```

---

## 18

```
MSH|^~\&|EPIC|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250506151000+0100||ORU^R01^ORU_R01|HCDOC20250506151000001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||CHI667788^^^EPIC^MR~1911142367WA^^^PPS^NNNIRL||Kelly^Caoimhe^R^^Miss||20191114|F|||33 Griffith Avenue^^Dublin 9^^D09 T2P7^IE^H
PV1|1|O|CARD^OPD-CARD-3^1^CHI_TEMPLE||||PRV110^Corcoran^Declan^^^Prof.^MD
ORC|RE|EPORD20250506002|CHIDOC20250506001||CM
OBR|1|EPORD20250506002|CHIDOC20250506001|29275-5^Growth chart^LN|||20250506103000+0100||||||||PRV110^Corcoran^Declan^^^Prof.^MD||||||20250506150000+0100|||F
OBX|1|NM|8302-2^Body height^LN||108.5|cm|||||F
OBX|2|NM|29463-7^Body weight^LN||17.8|kg|||||F
OBX|3|NM|39156-5^BMI^LN||15.1|kg/m2|||||F
OBX|4|ED|29275-5^Growth chart document^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEdyb3d0aCBDaGFydCBSZXBvcnQgLSBDSEkgVGVtcGxlIFN0cmVldCkKL0NyZWF0b3IgKEVwaWMgSXJlbGFuZCkKL1Byb2R1Y2VyIChIZWFsdGhTaGFyZSBIZWFsdGggQ29ubmVjdCkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDUwNjE1MTAwMCswMScwMCcpCj4+CmVuZG9iagpHUk9XVEggQ0hBUlQgUkVQT1JUCi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KUGF0aWVudDogU2FvaXJzZSBPJ05laWxsCkRPQjogMjUvMDkvMjAxOApBZ2U6IDYgeWVhcnMgNyBtb250aHMKCkhlaWdodDogMTA4LjUgY20gKDI1dGggY2VudGlsZSkKV2VpZ2h0OiAxNy44IGtnICgyNXRoIGNlbnRpbGUpCkJNSTogMTUuMSBrZy9tMiAoNTB0aCBjZW50aWxlKQoKR3Jvd3RoIHZlbG9jaXR5OiBOb3JtYWwgKDUuMiBjbS95ZWFyKQoKQ29tbWVudDogR3Jvd3RoIHRyYWNraW5nIGFwcHJvcHJpYXRlbHkgYWxvbmcgMjV0aCBjZW50aWxlLgpObyBjb25jZXJuIHJlIGdyb3d0aCBpbiBjb250ZXh0IG9mIFZTRC4=||||||F
```

---

## 19

```
MSH|^~\&|EPIC|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250507083000+0100||MDM^T02^MDM_T02|HCDOC20250507083000001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20250507083000
PID|1||CHI667788^^^EPIC^MR~1911142367WA^^^PPS^NNNIRL||Kelly^Caoimhe^R^^Miss||20191114|F|||33 Griffith Avenue^^Dublin 9^^D09 T2P7^IE^H
PV1|1|O|CARD^OPD-CARD-3^1^CHI_TEMPLE||||PRV110^Corcoran^Declan^^^Prof.^MD
TXA|1|CN^Clinic Letter^HL70270|TX||||20250506160000+0100||PRV110^Corcoran^Declan^^^Prof.^MD||||HCDOC-2025-77889||||||AU
OBX|1|ED|11488-4^Consult note^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENhcmRpb2xvZ3kgQ2xpbmljIExldHRlciAtIENISSBUZW1wbGUgU3RyZWV0KQovQ3JlYXRvciAoRXBpYyBJcmVsYW5kKQovUHJvZHVjZXIgKEhlYWx0aFNoYXJlIEhlYWx0aCBDb25uZWN0KQovQ3JlYXRpb25EYXRlIChEOjIwMjUwNTA2MTYwMDAwKzAxJzAwJykKPj4KZW5kb2JqCkNBUkRJT0xPR1kgQ0xJTklDIExFVFRFUgotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCkRyIEZpb25hIE8nTmVpbGwKNyBQaGlic2Jvcm91Z2ggUm9hZApEdWJsaW4gNwoKRGVhciBEciBPJ05laWxsLAoKUmU6IFNhb2lyc2UgTydOZWlsbCwgRE9CIDI1LzA5LzIwMTgKCkkgcmV2aWV3ZWQgU2FvaXJzZSBpbiBjYXJkaW9sb2d5IE9QRCB0b2RheS4KClNoZSByZW1haW5zIHdlbGwgd2l0aCBubyBjYXJkaWFjIHN5bXB0b21zLgpFY2hvIHRvZGF5IHNob3dzIGEgc3RhYmxlIHNtYWxsIHJlc3RyaWN0aXZlIHBlcmltZW1icmFub3VzIFZTRC4KTm8gaW50ZXJ2ZW50aW9uIHJlcXVpcmVkLgoKUGxhbjogQW5udWFsIHJldmlldyBpbiAxMiBtb250aHMuCk5vIGV4ZXJjaXNlIHJlc3RyaWN0aW9ucy4KRW5kb2NhcmRpdGlzIHByb3BoeWxheGlzIG5vdCByZXF1aXJlZC4KCllvdXJzIHNpbmNlcmVseSwKUHJvZiBDb2xpbiBNY01haG9uCkNvbnN1bHRhbnQgUGFlZGlhdHJpYyBDYXJkaW9sb2dpc3QKQ2hpbGRyZW4ncyBIZWFsdGggSXJlbGFuZCwgVGVtcGxlIFN0cmVldA==||||||F
```

---

## 20

```
MSH|^~\&|NBSLAB|CHI_TEMPLE|HEALTHCONNECT|CHI_HUB|20250320142500+0000||ORU^R01^ORU_R01|HCNBS20250320142500001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||NBS20250315-001^^^NBS^MR||Quinn^Baby^^^||20250315|M|||8 Shop Street^^Galway^^H91 K7P9^IE^H
PV1|1|I|NICU^BAY-1^COT-2^CHI_TEMPLE||||PRV160^Doyle^Muireann^^^Prof.^MD
ORC|RE|NBSORD20250315001|NBSLAB20250320001||CM||||20250320130000+0000
OBR|1|NBSORD20250315001|NBSLAB20250320001|54089-8^Newborn dried blood spot screen^LN|||20250317100000+0000||||||||PRV160^Doyle^Muireann^^^Prof.^MD||||||20250320141500+0000|||F
OBX|1|CE|54090-6^PKU screening^LN||260385009^Normal^SCT||||||F
OBX|2|CE|54079-9^Congenital hypothyroidism^LN||260385009^Normal^SCT||||||F
OBX|3|CE|54081-5^CF screening^LN||260385009^Normal^SCT||||||F
OBX|4|CE|57084-6^Galactosaemia^LN||260385009^Normal^SCT||||||F
OBX|5|CE|58232-0^Maple syrup urine disease^LN||260385009^Normal^SCT||||||F
OBX|6|CE|54078-1^Homocystinuria^LN||260385009^Normal^SCT||||||F
OBX|7|CE|MCADD^MCADD screening^LOCAL||260385009^Normal^SCT||||||F
OBX|8|CE|GAI^Glutaric aciduria type 1^LOCAL||260385009^Normal^SCT||||||F
NTE|1||National Newborn Bloodspot Screening Programme. All 8 conditions screened normal. Sample collected day of life 3.
```
