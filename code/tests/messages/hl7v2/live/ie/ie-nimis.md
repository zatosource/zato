# NIMIS (National Integrated Medical Imaging System) - real HL7v2 ER7 messages

## 1

```
MSH|^~\&|IPMS|BEAUMONT|NIMIS_RIS|BEAUMONT|20250318091530||ADT^A04^ADT_A01|ADT20250318091530001|P|2.5|||AL|NE
EVN|A04|20250318091500
PID|1||BEA204718^^^BEAUMONT^MR~8406187523AB^^^PPS^PPSN||Gallagher^Ciarán^T^^Mr.||19840618|M|||27 Glasnevin Avenue^^Dublin 9^^D09F3K7^IRL^H||^PRN^CP^^^^^^^(087)9123456||EN|||8406187523AB^^^PPS^PPSN||||IRL
PV1|1|O|RAD^XRAY^1^BEAUMONT||||34512^Daly^Sorcha^^^Dr.^MD^^^IMC||RAD||||1|||34512^Daly^Sorcha^^^Dr.^MD|OUT||GMS|||||||||||||||||||||BEAUMONT|||||20250318091500
```

---

## 2

```
MSH|^~\&|IPMS|STJAMES|NIMIS_RIS|STJAMES|20250410083000||ADT^A01^ADT_A01|ADT20250410083000001|P|2.5|||AL|NE
EVN|A01|20250410082500
PID|1||SJH518294^^^STJAMES^MR~7209065312WA^^^PPS^PPSN||Brennan^Saoirse^L^^Ms.||19720906|F|||48 The Coombe^^Dublin 8^^D08PW21^IRL^H||^PRN^PH^^^^^^^(01)4789234~^PRN^CP^^^^^^^(086)2178345||EN|M|||7209065312WA^^^PPS^PPSN||||IRL
PV1|1|I|ORTHO^WARD6^BED14^STJAMES||||41278^Crowley^Eoghan^^^Dr.^MD^^^IMC||ORT||||7|||41278^Crowley^Eoghan^^^Dr.^MD|IN||GMS|||||||||||||||||||||STJAMES|||||20250410082500
```

---

## 3

```
MSH|^~\&|IPMS|CUH|NIMIS_RIS|CUH|20250505141200||ADT^A08^ADT_A01|ADT20250505141200001|P|2.5|||AL|NE
EVN|A08|20250505141000
PID|1||CUH731045^^^CUH^MR~8512234178FA^^^PPS^PPSN||Walsh^Diarmuid^N^^Mr.||19851223|M|||12 South Mall^^Cork^^T12HN84^IRL^H~3 MacCurtain Street^^Cork^^T23VK62^IRL^H||^PRN^CP^^^^^^^(087)3345521||EN|S|||8512234178FA^^^PPS^PPSN||||IRL
PV1|1|O|RAD^CT^1^CUH||||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC
```

---

## 4

```
MSH|^~\&|IPMS|TALLAGHT|NIMIS_RIS|TALLAGHT|20250612160000||ADT^A03^ADT_A03|ADT20250612160000001|P|2.5|||AL|NE
EVN|A03|20250612155500
PID|1||TUH382956^^^TALLAGHT^MR~9703154289TA^^^PPS^PPSN||Quinn^Aisling^M^^Ms.||19970315|F|||23 Main Road^^Tallaght, Dublin 24^^D24T6W3^IRL^H||^PRN^CP^^^^^^^(087)4456712
PV1|1|I|SURG^WARD3^BED08^TALLAGHT||||76234^Moran^Fiachra^^^Dr.^MD|||SURG||||5|||76234^Moran^Fiachra^^^Dr.^MD|IN||GMS||||||||||||||01^Home|||||||TALLAGHT|||||20250608090000|||20250612155500
```

---

## 5

```
MSH|^~\&|IPMS|UHG|NIMIS_RIS|UHG|20250720103000||ADT^A40^ADT_A39|ADT20250720103000001|P|2.5|||AL|NE
EVN|A40|20250720102500
PID|1||UHG619284^^^UHG^MR~6804258734HA^^^PPS^PPSN||O'Brien^Tadhg^R^^Mr.||19680425|M|||9 Salthill Promenade^^Galway^^H91WD43^IRL^H||^PRN^PH^^^^^^^(091)587234
MRG|UHG619285^^^UHG^MR|
```

---

## 6

```
MSH|^~\&|CPOE|MATER|NIMIS_RIS|MATER|20250415100000||ORM^O01^ORM_O01|ORM20250415100000001|P|2.5|||AL|NE
PID|1||MAT847261^^^MATER^MR~8107194523KA^^^PPS^PPSN||McCarthy^Eoin^G^^Mr.||19810719|M|||18 Phibsborough Road^^Dublin 7^^D07W4R6^IRL^H||^PRN^CP^^^^^^^(086)5589234
PV1|1|I|MED^WARD4A^BED06^MATER||||13478^Sullivan^Orla^^^Prof.^MD^^^IMC||MED||||3
ORC|NW|MATORD20250415001|||SC||||20250415095000|||13478^Sullivan^Orla^^^Prof.^MD^^^IMC
OBR|1|MATORD20250415001||71020^Chest X-ray PA^LOINC|||20250415095000||||||^^Persistent cough, fever||13478^Sullivan^Orla^^^Prof.^MD^^^IMC||RAD20250415001|||||RAD||1^^^20250415100000^^R||||||71020^Chest X-ray PA
ZDS|1.2.840.113619.2.55.3.2250450403.20250415100000.12345^^Application^DICOM
```

---

## 7

```
MSH|^~\&|CPOE|CUH|NIMIS_RIS|CUH|20250520143000||ORM^O01^ORM_O01|ORM20250520143000001|P|2.5|||AL|NE
PID|1||CUH904217^^^CUH^MR~7710083456BA^^^PPS^PPSN||Buckley^Caoimhe^E^^Mrs.||19771008|F|||22 Grand Parade^^Cork^^T12V7N1^IRL^H||^PRN^CP^^^^^^^(087)6712893
PV1|1|E|ED^^^CUH||||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC||MED||||1
ORC|NW|CUHORD20250520001|||SC||||20250520142000|||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC
OBR|1|CUHORD20250520001||72193^CT abdomen and pelvis with contrast^LOINC|||20250520142000||||||^^Acute abdominal pain, elevated WCC||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC||RAD20250520001|||||RAD||1^^^20250520150000^^S||||||72193^CT abdomen pelvis contrast
OBX|1|ST|30525-0^Age^LN||50|yr|||||F
OBX|2|ST|8302-2^Body height^LN||165|cm|||||F
OBX|3|ST|29463-7^Body weight^LN||72|kg|||||F
OBX|4|ST|CREATININE^Creatinine^L||88|umol/L|62-106||||F
NTE|1||Urgent. Hx: 50yo female, acute RIF pain, WCC 18.5, CRP 145. Rule out appendicitis/abscess. No contrast allergy known. eGFR >60.
ZDS|1.2.840.113619.2.55.3.2250450403.20250520143000.67890^^Application^DICOM
```

---

## 8

```
MSH|^~\&|CPOE|UHL|NIMIS_RIS|UHL|20250603110000||ORM^O01^ORM_O01|ORM20250603110000001|P|2.5|||AL|NE
PID|1||UHL473829^^^UHL^MR~9205127891WA^^^PPS^PPSN||Healy^Roisín^D^^Ms.||19920512|F|||31 O'Connell Street^^Limerick^^V94HP28^IRL^H||^PRN^CP^^^^^^^(085)2789134
PV1|1|O|NEURO^OPD^1^UHL||||87456^Nolan^Declan^^^Dr.^MD|||NEUR||||1
ORC|NW|UHLORD20250603001|||SC||||20250603103000|||87456^Nolan^Declan^^^Dr.^MD^^^IMC
OBR|1|UHLORD20250603001||70553^MRI brain without and with contrast^LOINC|||20250603103000||||||^^New onset seizures, headache||87456^Nolan^Declan^^^Dr.^MD^^^IMC||RAD20250603001|||||RAD||1^^^20250610090000^^R
NTE|1||35yo female, first seizure 2 weeks ago, intermittent headaches. No history of trauma. Neurological exam normal except for mild left visual field defect. Please assess for space-occupying lesion.
ZDS|1.2.840.113619.2.55.3.2250450403.20250603110000.11111^^Application^DICOM
```

---

## 9

```
MSH|^~\&|NIMIS_RIS|BEAUMONT|MODALITY|BEAUMONT|20250416083000||ORM^O01^ORM_O01|ORM20250416083000001|P|2.5|||AL|NE
PID|1||BEA204718^^^BEAUMONT^MR~8406187523AB^^^PPS^PPSN||Gallagher^Ciarán^T^^Mr.||19840618|M
PV1|1|I|MED^WARD4A^BED06^BEAUMONT
ORC|SC|MATORD20250415001|NIMISACC20250416001||SC||||20250416082500
OBR|1|MATORD20250415001|NIMISACC20250416001|71020^Chest X-ray PA^LOINC|||20250416083000||||||^^Persistent cough, fever||13478^Sullivan^Orla^^^Prof.^MD^^^IMC||RAD20250416001|||||RAD||1^^^20250416083000^^S||||||71020^Chest X-ray PA
ZDS|1.2.840.113619.2.55.3.2250450403.20250416083000.12345^^Application^DICOM
```

---

## 10

```
MSH|^~\&|CPOE|UHW|NIMIS_RIS|UHW|20250701090000||ORM^O01^ORM_O01|ORM20250701090000001|P|2.5|||AL|NE
PID|1||UHW582347^^^UHW^MR~7001154678DA^^^PPS^PPSN||Doyle^Lorcan^F^^Mr.||19700115|M|||5 The Quay^^Waterford^^X91NP43^IRL^H||^PRN^CP^^^^^^^(087)8234567
PV1|1|O|GP^^^WATERFORD||||98234^Kavanagh^Gráinne^^^Dr.^MD^^^IMC||MED||||1
ORC|NW|UHWORD20250701001|||SC||||20250701085000|||98234^Kavanagh^Gráinne^^^Dr.^MD^^^IMC
OBR|1|UHWORD20250701001||76700^Ultrasound abdomen complete^LOINC|||20250701085000||||||^^Deranged LFTs, epigastric pain||98234^Kavanagh^Gráinne^^^Dr.^MD^^^IMC||RAD20250701001|||||RAD||1^^^20250703100000^^R
NTE|1||56yo male with 2 week history epigastric pain, ALT 120, AST 95, ALP 180. Previous cholecystectomy 2010. Rule out biliary dilatation, hepatic lesion. No alcohol excess reported.
ZDS|1.2.840.113619.2.55.3.2250450403.20250701090000.22222^^Application^DICOM
```

---

## 11

```
MSH|^~\&|NIMIS_RIS|MATER|CPOE|MATER|20250415143000||ORU^R01^ORU_R01|ORU20250415143000001|P|2.5|||AL|NE
PID|1||MAT847261^^^MATER^MR~8107194523KA^^^PPS^PPSN||McCarthy^Eoin^G^^Mr.||19810719|M
PV1|1|I|MED^WARD4A^BED06^MATER||||13478^Sullivan^Orla^^^Prof.^MD^^^IMC
ORC|RE|MATORD20250415001|NIMISACC20250416001||CM
OBR|1|MATORD20250415001|NIMISACC20250416001|71020^Chest X-ray PA^LOINC|||20250416083500||||||||13478^Sullivan^Orla^^^Prof.^MD^^^IMC||RAD20250416001|||||RAD|||F||||||71020^Chest X-ray PA
OBX|1|FT|71020^Chest X-ray PA^LOINC||PA chest radiograph\.br\\.br\Clinical indication: Persistent cough, fever.\.br\\.br\Findings: Heart size and mediastinal contour are normal. Bilateral lower zone airspace opacification, more prominent on the right, consistent with consolidation. Small right-sided pleural effusion. No pneumothorax.\.br\\.br\Impression: Bilateral lower lobe pneumonia, worse on right. Small right pleural effusion. Suggest clinical correlation and follow-up imaging after treatment.\.br\\.br\Reported by: Dr. Bríd O'Connor, Consultant Radiologist, Mater Hospital\.br\||||||F|||20250416140000
```

---

## 12

```
MSH|^~\&|NIMIS_RIS|CUH|CPOE|CUH|20250520180000||ORU^R01^ORU_R01|ORU20250520180000001|P|2.5|||AL|NE
PID|1||CUH904217^^^CUH^MR~7710083456BA^^^PPS^PPSN||Buckley^Caoimhe^E^^Mrs.||19771008|F
PV1|1|E|ED^^^CUH||||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC
ORC|RE|CUHORD20250520001|NIMISACC20250520001||CM
OBR|1|CUHORD20250520001|NIMISACC20250520001|72193^CT abdomen and pelvis with contrast^LOINC|||20250520152000||||||||52893^Fitzgerald^Muireann^^^Dr.^MD^^^IMC||RAD20250520001|||||RAD|||F||||||72193^CT abdomen pelvis contrast
OBX|1|FT|72193^CT abdomen and pelvis with contrast^LOINC||CT abdomen and pelvis with IV contrast\.br\\.br\Clinical indication: Acute abdominal pain, elevated WCC.\.br\\.br\Technique: Helical CT from diaphragm to symphysis pubis, 100mL Omnipaque 350 IV.\.br\\.br\Findings:\.br\Liver: Normal size and attenuation. No focal lesion.\.br\Gallbladder, spleen, pancreas, adrenals: Unremarkable.\.br\Kidneys: Normal bilaterally, no hydronephrosis.\.br\Appendix: Dilated to 12mm with periappendiceal fat stranding and a 5mm appendicolith at the base. Wall enhancement present. No perforation or abscess.\.br\Bowel: No obstruction. No free air.\.br\Free fluid: Trace free fluid in pelvis.\.br\\.br\Impression: Acute appendicitis with appendicolith. No perforation or abscess. Surgical consultation recommended.\.br\\.br\Reported by: Dr. Cathal Ryan, Consultant Radiologist, CUH\.br\||||||F|||20250520174500
NTE|1||URGENT: Acute appendicitis confirmed. Surgical team contacted.
```

---

## 13

```
MSH|^~\&|NIMIS_RIS|UHL|CPOE|UHL|20250611153000||ORU^R01^ORU_R01|ORU20250611153000001|P|2.5|||AL|NE
PID|1||UHL473829^^^UHL^MR~9205127891WA^^^PPS^PPSN||Healy^Roisín^D^^Ms.||19920512|F
PV1|1|O|NEURO^OPD^1^UHL||||87456^Nolan^Declan^^^Dr.^MD
ORC|RE|UHLORD20250603001|NIMISACC20250610001||CM
OBR|1|UHLORD20250603001|NIMISACC20250610001|70553^MRI brain without and with contrast^LOINC|||20250610093000||||||||87456^Nolan^Declan^^^Dr.^MD|||RAD20250610001|||||RAD|||F
OBX|1|FT|70553^MRI brain without and with contrast^LOINC||MRI Brain without and with gadolinium contrast\.br\\.br\Clinical indication: New onset seizures, headache, left visual field defect.\.br\\.br\Technique: Axial T1, T2, FLAIR, DWI, sagittal T1, coronal FLAIR, post-gadolinium axial and coronal T1.\.br\\.br\Findings:\.br\There is a 2.8 x 2.3 cm enhancing extra-axial mass arising from the right sphenoid wing, isointense on T1, hyperintense on T2, with avid homogeneous contrast enhancement. Dural tail sign present. Mild mass effect on the right temporal lobe with 3mm rightward midline shift. No surrounding oedema.\.br\Remainder of brain parenchyma: Normal signal. No additional masses.\.br\Ventricles: Normal size and configuration.\.br\\.br\Impression: Right sphenoid wing meningioma, 2.8cm. Neurosurgical referral recommended.\.br\\.br\Reported by: Dr. Fionnuala Dunne, Consultant Neuroradiologist, UHL\.br\||||||F|||20250611150000
NTE|1||Findings discussed with Dr. Nolan at 15:15 by telephone. Neurosurgical referral initiated.
```

---

## 14

```
MSH|^~\&|CPOE|TALLAGHT|NIMIS_RIS|TALLAGHT|20250515113000||ORM^O01^ORM_O01|ORM20250515113000001|P|2.5|||AL|NE
PID|1||TUH694578^^^TALLAGHT^MR~8411231578RA^^^PPS^PPSN||Kelly^Pádraig^J^^Mr.||19841123|M
PV1|1|I|MED^WARD2^BED11^TALLAGHT||||76234^Moran^Fiachra^^^Dr.^MD
ORC|CA|TUHORD20250514001|NIMISACC20250514001||CA||||20250515112500|||76234^Moran^Fiachra^^^Dr.^MD^^^IMC
OBR|1|TUHORD20250514001|NIMISACC20250514001|74177^CT abdomen with contrast^LOINC
NTE|1||Order cancelled - patient discharged. Investigation no longer clinically required.
```

---

## 15

```
MSH|^~\&|NIMIS_RIS|UHW|CPOE|UHW|20250703160000||ORU^R01^ORU_R01|ORU20250703160000001|P|2.5|||AL|NE
PID|1||UHW582347^^^UHW^MR~7001154678DA^^^PPS^PPSN||Doyle^Lorcan^F^^Mr.||19700115|M
PV1|1|O|GP^^^WATERFORD||||98234^Kavanagh^Gráinne^^^Dr.^MD^^^IMC
ORC|RE|UHWORD20250701001|NIMISACC20250703001||CM
OBR|1|UHWORD20250701001|NIMISACC20250703001|76700^Ultrasound abdomen complete^LOINC|||20250703100000||||||||98234^Kavanagh^Gráinne^^^Dr.^MD^^^IMC||RAD20250703001|||||RAD|||F
OBX|1|FT|76700^Ultrasound abdomen complete^LOINC||Ultrasound abdomen complete\.br\\.br\Clinical indication: Deranged LFTs, epigastric pain. Previous cholecystectomy.\.br\\.br\Findings:\.br\Liver: Mildly increased echogenicity consistent with hepatic steatosis. No focal lesion. Liver span 16cm.\.br\Gallbladder: Post-cholecystectomy status. No collection in gallbladder fossa.\.br\Common bile duct: Normal calibre, 4mm. No intrahepatic duct dilatation.\.br\Pancreas: Partially obscured by bowel gas. Visible portions unremarkable.\.br\Spleen: Normal, 11cm.\.br\Kidneys: Normal bilaterally, no hydronephrosis.\.br\Aorta: Normal calibre.\.br\\.br\Impression: Hepatic steatosis. No biliary dilatation. No focal lesion. Suggest correlation with metabolic profile.\.br\\.br\Reported by: Dr. Deirdre Whelan, Consultant Radiologist, UHW\.br\||||||F|||20250703154500
```

---

## 16

```
MSH|^~\&|NIMIS_RIS|STJAMES|CPOE|STJAMES|20250422170000||ORU^R01^ORU_R01|ORU20250422170000001|P|2.5|||AL|NE
PID|1||SJH923147^^^STJAMES^MR~5809241678FA^^^PPS^PPSN||Sullivan^Maeve^C^^Mrs.||19580924|F
PV1|1|O|GP^^^THOMASST||||41278^Crowley^Eoghan^^^Dr.^MD^^^IMC
ORC|RE|SJHORD20250418001|NIMISACC20250421001||CM
OBR|1|SJHORD20250418001|NIMISACC20250421001|24725^CT chest^LOINC|||20250421100000||||||||41278^Crowley^Eoghan^^^Dr.^MD||RAD20250421001|||||RAD|||C
OBX|1|FT|24725^CT chest^LOINC||ADDENDUM (corrected report)\.br\\.br\Original report: 21/04/2025. This addendum supersedes the original.\.br\\.br\CT Chest with IV contrast\.br\Clinical indication: Follow-up known pulmonary nodule.\.br\\.br\Findings (corrected):\.br\Right upper lobe nodule measures 14mm (previously reported 12mm on review of prior). Compared with CT dated 15/01/2025 (11mm), this represents interval growth of 3mm over 3 months. Spiculated morphology unchanged.\.br\No new pulmonary nodules. No lymphadenopathy. No pleural effusion.\.br\\.br\Impression (corrected): Growing right upper lobe spiculated pulmonary nodule, now 14mm. Highly suspicious for malignancy. PET-CT and MDT discussion recommended.\.br\\.br\Addendum by: Dr. Bríd O'Connor, Consultant Radiologist\.br\Verified by: Prof. Conor Gallagher, Consultant Radiologist\.br\||||||C|||20250422165000
NTE|1||CORRECTED REPORT: Nodule measurement revised from 12mm to 14mm after comparison with prior imaging. Urgency upgraded. MDT referral initiated.
```

---

## 17

```
MSH|^~\&|CPOE|UHG|NIMIS_RIS|UHG|20250805091500||ORM^O01^ORM_O01|ORM20250805091500001|P|2.5|||AL|NE
PID|1||UHG847312^^^UHG^MR~7408235612WA^^^PPS^PPSN||O'Connor^Niamh^S^^Mrs.||19740823|F|||14 Shop Street^^Galway^^H91K3W7^IRL^H||^PRN^CP^^^^^^^(087)1238845
PV1|1|O|BREAST^SCREENING^1^UHG||||97312^Mannion^Siobhán^^^Dr.^MD
ORC|NW|UHGORD20250805001|||SC||||20250805090000|||97312^Mannion^Siobhán^^^Dr.^MD^^^IMC
OBR|1|UHGORD20250805001||77067^Mammography bilateral screening^LOINC|||20250805090000||||||^^Routine breast screening, age 53||97312^Mannion^Siobhán^^^Dr.^MD^^^IMC||RAD20250805001|||||RAD||1^^^20250812093000^^R
NTE|1||Routine BreastCheck screening mammography. No personal history of breast cancer. FHx: Maternal aunt diagnosed age 62. No palpable lumps. Not on HRT.
ZDS|1.2.840.113619.2.55.3.2250450403.20250805091500.33333^^Application^DICOM
```

---

## 18

```
MSH|^~\&|NIMIS_RIS|BEAUMONT|CPOE|BEAUMONT|20250319120000||ORU^R01^ORU_R01|ORU20250319120000001|P|2.5|||AL|NE
PID|1||BEA739412^^^BEAUMONT^MR~5203081567WA^^^PPS^PPSN||Murphy^Colm^R^^Mr.||19520308|M
PV1|1|E|ED^^^BEAUMONT||||34512^Daly^Sorcha^^^Dr.^MD^^^IMC
ORC|RE|BEAORD20250319001|NIMISACC20250319001||CM
OBR|1|BEAORD20250319001|NIMISACC20250319001|30799-1^CT head without contrast^LOINC|||20250319094500||||||||34512^Daly^Sorcha^^^Dr.^MD||RAD20250319001|||||RAD|||F
OBX|1|FT|30799-1^CT head without contrast^LOINC||CT head without contrast\.br\\.br\Clinical indication: 74yo male, sudden onset right-sided weakness and dysphasia, onset 2 hours ago. Query acute stroke.\.br\\.br\Findings:\.br\No acute intracranial haemorrhage. No midline shift.\.br\Subtle hypodensity in the left MCA territory (left insular cortex and left frontal operculum) with loss of grey-white differentiation, ASPECTS score 8.\.br\No established infarct. No mass lesion.\.br\Old lacunar infarct right basal ganglia.\.br\Mild small vessel disease. Mild generalised cerebral atrophy.\.br\\.br\Impression: Early ischaemic changes in left MCA territory, ASPECTS 8. Clinical correlation with stroke pathway. Consider CT angiography and perfusion if within treatment window.\.br\\.br\Reported by: Dr. Ruairí Byrne, Consultant Neuroradiologist, Beaumont Hospital\.br\||||||F|||20250319115000
OBX|2|ED|PDF^CT Head Report^L||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PC9GMSApPj4+Pj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxOTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihDVCBIZWFkIFJlcG9ydCAtIEJlYXVtb250IEhvc3BpdGFsKSBUago1MCA2NTAgVGQKKENsaW5pY2FsIEluZGljYXRpb246IEFjdXRlIFN0cm9rZSkgVGoKNTAgNjMwIFRkCihGaW5kaW5nczogRWFybHkgaXNjaGFlbWljIGNoYW5nZXMgbGVmdCBNQ0EpIFRqCjUwIDYxMCBUZAooQVNQRUNUUyBzY29yZSA4KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNjAgMDAwMDAgbiAKMDAwMDAwMDMyNSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjU2MQolJUVPRgo=||||||F
NTE|1||STROKE ALERT: Report communicated to stroke team at 11:50. CT angiography in progress.
```

---

## 19

```
MSH|^~\&|NIMIS_RIS|UHG|CPOE|UHG|20250813140000||ORU^R01^ORU_R01|ORU20250813140000001|P|2.5|||AL|NE
PID|1||UHG847312^^^UHG^MR~7408235612WA^^^PPS^PPSN||O'Connor^Niamh^S^^Mrs.||19740823|F
PV1|1|O|BREAST^SCREENING^1^UHG||||97312^Mannion^Siobhán^^^Dr.^MD
ORC|RE|UHGORD20250805001|NIMISACC20250812001||CM
OBR|1|UHGORD20250805001|NIMISACC20250812001|77067^Mammography bilateral screening^LOINC|||20250812093000||||||||97312^Mannion^Siobhán^^^Dr.^MD||RAD20250812001|||||RAD|||F
OBX|1|FT|77067^Mammography bilateral screening^LOINC||Bilateral screening mammography\.br\\.br\Clinical indication: Routine BreastCheck screening, age 53.\.br\\.br\Comparison: Screening mammography 14/08/2023.\.br\\.br\Findings:\.br\Breast composition: Heterogeneously dense (ACR C).\.br\Right breast: No suspicious mass, calcification or architectural distortion.\.br\Left breast: New 8mm cluster of pleomorphic microcalcifications in the upper outer quadrant, not present on prior. No associated mass.\.br\\.br\Assessment: BI-RADS 4B - Suspicious.\.br\\.br\Recommendation: Stereotactic biopsy of left breast microcalcifications recommended.\.br\\.br\Reported by: Dr. Aoife Daly, Consultant Breast Radiologist, UHG\.br\||||||F|||20250813133000
OBX|2|ED|PDF^Mammography Report^L||^AP^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PC9GMSApPj4+Pj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyMzAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNYW1tb2dyYXBoeSBSZXBvcnQgLSBVSEcgR2Fsd2F5KSBUago1MCA2NTAgVGQKKEJpbGF0ZXJhbCBTY3JlZW5pbmcgTWFtbW9ncmFwaHkpIFRqCjUwIDYzMCBUZAooQXNzZXNzbWVudDogQkktUkFEUyA0QiAtIFN1c3BpY2lvdXMpIFRqCjUwIDYxMCBUZAooTGVmdCBicmVhc3Q6IFBsZW9tb3JwaGljIG1pY3JvY2FsY2lmaWNhdGlvbnMpIFRqCjUwIDU5MCBUZAooUmVjb21tZW5kYXRpb246IFN0ZXJlb3RhY3RpYyBiaW9wc3kpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE2MCAwMDAwMCBuIAowMDAwMDAwMzI1IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNQovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNjAyCiUlRU9GCg==||||||F
NTE|1||BI-RADS 4B: Stereotactic biopsy recommended. Patient to be contacted by breast care nurse coordinator.
```

---

## 20

```
MSH|^~\&|IPMS|SUH|NIMIS_RIS|SUH|20250901100000||ADT^A28^ADT_A05|ADT20250901100000001|P|2.5|||AL|NE
EVN|A28|20250901095500
PID|1||SUH284713^^^SUH^MR~0507129345TA^^^PPS^PPSN||Clodagh^Siobhán^R^^Ms.||20050712|F|||11 Wine Street^^Sligo^^F91P8K2^IRL^H||^PRN^CP^^^^^^^(086)7234518||EN|S|||0507129345TA^^^PPS^PPSN||||IRL
PV1|1|N
```
