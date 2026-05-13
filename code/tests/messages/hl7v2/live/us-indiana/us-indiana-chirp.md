# CHIRP (Indiana immunization registry) - real HL7v2 ER7 messages

---

## 1. VXU^V04 - Infant 2-month vaccination series reported to CHIRP

```
MSH|^~\&|PEDS_EMR|IUH_PEDS|CHIRP|ISDH|20250310101500||VXU^V04^VXU_V04|CHIRP00001234|P|2.5.1|||AL|NE
PID|1||IUH_MRN80001234^^^IUH^MR||Brennan^Chloe^Isabelle||20250108|F|||812 Meridian Park Dr^^Indianapolis^IN^46260^US||^PRN^PH^^1^317^5551234||ENG||NON|SSN234-71-9023^^^SS
PD1|||IU HEALTH PEDIATRICS NORTH^^80001|PEDMD^Gupta^Anita^K^^^MD
NK1|1|Brennan^Heather^Lynn|MTH|812 Meridian Park Dr^^Indianapolis^IN^46260^US|^PRN^PH^^1^317^5551234
NK1|2|Brennan^Michael^Joseph|FTH|812 Meridian Park Dr^^Indianapolis^IN^46260^US|^PRN^PH^^1^317^5551235
ORC|RE|CHIRP_SUB001||||||||||PEDMD^Gupta^Anita^K^^^MD
RXA|0|1|20250310100000|20250310100000|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|RT^^Right Thigh||||||C3456A||GSK^GlaxoSmithKline|||||A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
ORC|RE|CHIRP_SUB002||||||||||PEDMD^Gupta^Anita^K^^^MD
RXA|0|1|20250310100500|20250310100500|133^PCV13^CVX|0.5|mL|IM|LT^^Left Thigh||||||D7890B||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
ORC|RE|CHIRP_SUB003||||||||||PEDMD^Gupta^Anita^K^^^MD
RXA|0|1|20250310101000|20250310101000|116^Rotavirus Pentavalent^CVX|2.0|mL|PO|||||||E1234C||MSD^Merck Sharp & Dohme|||||A
RXR|PO^Oral^HL70162
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC1^Medicaid^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||120^DTaP-Hep B-IPV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
```

---

## 2. VXU^V04 - 4-month well-child immunizations reported to CHIRP

```
MSH|^~\&|PEDS_EMR|CHN_PEDS|CHIRP|ISDH|20250312140000||VXU^V04^VXU_V04|CHIRP00004567|P|2.5.1|||AL|NE
PID|1||CHN_MRN90002345^^^CHN^MR||Vasquez^Diego^Rafael||20241112|M|||1547 East 82nd St^^Indianapolis^IN^46240^US||^PRN^PH^^1^317^5552345||SPA||CAT|SSN318-62-4509^^^SS
PD1|||COMMUNITY HEALTH PEDIATRICS^^90002|PEDMD^Thornton^Rachel^L^^^MD
NK1|1|Vasquez^Carmen^Sofia|MTH|1547 East 82nd St^^Indianapolis^IN^46240^US|^PRN^PH^^1^317^5552345
ORC|RE|CHIRP_SUB004||||||||||PEDMD^Thornton^Rachel^L^^^MD
RXA|0|1|20250312135000|20250312135000|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|RT^^Right Thigh||||||C4567B||GSK^GlaxoSmithKline|||||A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
ORC|RE|CHIRP_SUB005||||||||||PEDMD^Thornton^Rachel^L^^^MD
RXA|0|1|20250312135500|20250312135500|133^PCV13^CVX|0.5|mL|IM|LT^^Left Thigh||||||D8901C||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
ORC|RE|CHIRP_SUB006||||||||||PEDMD^Thornton^Rachel^L^^^MD
RXA|0|1|20250312135800|20250312135800|116^Rotavirus Pentavalent^CVX|2.0|mL|PO|||||||E2345D||MSD^Merck Sharp & Dohme|||||A
RXR|PO^Oral^HL70162
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||120^DTaP-Hep B-IPV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
```

---

## 3. VXU^V04 - Kindergarten entry immunizations at Parkview Pediatrics

```
MSH|^~\&|PEDS_EMR|PKV_PEDS|CHIRP|ISDH|20250314093000||VXU^V04^VXU_V04|CHIRP00007890|P|2.5.1|||AL|NE
PID|1||PKV_MRN70003456^^^PKV^MR||Albright^Lily^Catherine||20200601|F|||918 Stellhorn Rd^^Fort Wayne^IN^46815^US||^PRN^PH^^1^260^5553456||ENG||LUT|SSN427-53-8160^^^SS
PD1|||PARKVIEW PEDIATRICS^^70003|PEDMD^Farley^Denise^S^^^MD
NK1|1|Albright^Megan^Rose|MTH|918 Stellhorn Rd^^Fort Wayne^IN^46815^US|^PRN^PH^^1^260^5553456
ORC|RE|CHIRP_SUB007||||||||||PEDMD^Farley^Denise^S^^^MD
RXA|0|1|20250314092000|20250314092000|94^MMRV^CVX|0.5|mL|SC|LA^^Left Arm||||||M9012E||MSD^Merck Sharp & Dohme|||||A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
ORC|RE|CHIRP_SUB008||||||||||PEDMD^Farley^Denise^S^^^MD
RXA|0|1|20250314092500|20250314092500|20^DTaP^CVX|0.5|mL|IM|RA^^Right Arm||||||F3456G||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
ORC|RE|CHIRP_SUB009||||||||||PEDMD^Farley^Denise^S^^^MD
RXA|0|1|20250314092800|20250314092800|89^Polio IPV^CVX|0.5|mL|IM|LA^^Left Arm||||||G4567H||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||94^MMRV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200812||||||F
```

---

## 4. QBP^Q11 - Immunization history query for school enrollment

```
MSH|^~\&|SCHOOL_SYS|MSDW_SCHOOLS|CHIRP|ISDH|20250315081500||QBP^Q11^QBP_Q11|CHIRP00011234|P|2.5.1|||AL|NE
QPD|Z44^Request Immunization History^CDCPHINVS|SQRY001234||Albright^Lily^Catherine||20200601|F|||918 Stellhorn Rd^^Fort Wayne^IN^46815
RCP|I|99^RD
```

---

## 5. RSP^K11 - Immunization history response for school enrollment

```
MSH|^~\&|CHIRP|ISDH|SCHOOL_SYS|MSDW_SCHOOLS|20250315081510||RSP^K11^RSP_K11|CHIRP00011235|P|2.5.1|||AL|NE
MSA|AA|CHIRP00011234
QAK|SQRY001234|OK|Z44^Request Immunization History^CDCPHINVS
QPD|Z44^Request Immunization History^CDCPHINVS|SQRY001234||Albright^Lily^Catherine||20200601|F
PID|1||CHIRP_ID003456^^^CHIRP^SR||Albright^Lily^Catherine||20200601|F|||918 Stellhorn Rd^^Fort Wayne^IN^46815^US
ORC|RE|CHIRP_HIST001||||||||||
RXA|0|1|20200801|20200801|08^Hep B Adolescent or Pediatric^CVX|0.5|mL|IM|||||||H1234A||MSD^Merck Sharp & Dohme
RXA|0|1|20201112|20201112|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|||||||C1234A||GSK^GlaxoSmithKline
RXA|0|1|20210112|20210112|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|||||||C2345B||GSK^GlaxoSmithKline
RXA|0|1|20210412|20210412|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|||||||C3456C||GSK^GlaxoSmithKline
RXA|0|1|20210712|20210712|03^MMR^CVX|0.5|mL|SC|||||||M1234A||MSD^Merck Sharp & Dohme
RXA|0|1|20210712|20210712|21^Varicella^CVX|0.5|mL|SC|||||||V1234A||MSD^Merck Sharp & Dohme
RXA|0|1|20250314|20250314|94^MMRV^CVX|0.5|mL|SC|||||||M9012E||MSD^Merck Sharp & Dohme
RXA|0|1|20250314|20250314|20^DTaP^CVX|0.5|mL|IM|||||||F3456G||SNF^Sanofi Pasteur
RXA|0|1|20250314|20250314|89^Polio IPV^CVX|0.5|mL|IM|||||||G4567H||SNF^Sanofi Pasteur
```

---

## 6. VXU^V04 - Adolescent HPV and Tdap immunizations

```
MSH|^~\&|PEDS_EMR|FRAN_PEDS|CHIRP|ISDH|20250316153000||VXU^V04^VXU_V04|CHIRP00014567|P|2.5.1|||AL|NE
PID|1||FRAN_MRN40004567^^^FRAN^MR||Nguyen^Sophia^Mai||20130722|F|||823 US Highway 30^^Crown Point^IN^46307^US||^PRN^PH^^1^219^5554567||CHI||BUD|SSN541-82-3079^^^SS
PD1|||FRANCISCAN PEDIATRICS CP^^40004|PEDMD^Harmon^Beth^T^^^MD
NK1|1|Nguyen^Lan^Thi|MTH|823 US Highway 30^^Crown Point^IN^46307^US|^PRN^PH^^1^219^5554567
ORC|RE|CHIRP_SUB010||||||||||PEDMD^Harmon^Beth^T^^^MD
RXA|0|1|20250316152000|20250316152000|165^HPV9^CVX|0.5|mL|IM|LA^^Left Arm||||||J5678K||MSD^Merck Sharp & Dohme|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
ORC|RE|CHIRP_SUB011||||||||||PEDMD^Harmon^Beth^T^^^MD
RXA|0|1|20250316152500|20250316152500|115^Tdap^CVX|0.5|mL|IM|RA^^Right Arm||||||K6789L||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
ORC|RE|CHIRP_SUB012||||||||||PEDMD^Harmon^Beth^T^^^MD
RXA|0|1|20250316153000|20250316153000|164^Meningococcal MenACWY^CVX|0.5|mL|IM|LA^^Left Arm||||||L7890M||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||165^HPV9^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20191206||||||F
```

---

## 7. VXU^V04 - Flu shot administered at pharmacy reported to CHIRP

```
MSH|^~\&|PHARM_SYS|WALGREENS|CHIRP|ISDH|20250318110000||VXU^V04^VXU_V04|CHIRP00017890|P|2.5.1|||AL|NE
PID|1||WAL_MRN50005678^^^WLGRN^MR||Dalton^Kenneth^Wayne||19520310|M|||2340 Grape Rd^^Mishawaka^IN^46545^US||^PRN^PH^^1^574^5555678||ENG|M|PRO|SSN617-43-8902^^^SS
PD1|||WALGREENS PHARMACY 4567^^50005|PHARMD^Kapoor^Ravi^K^^^PharmD
ORC|RE|CHIRP_SUB013||||||||||PHARMD^Kapoor^Ravi^K^^^PharmD
RXA|0|1|20250318105500|20250318105500|197^Influenza HD Quadrivalent^CVX|0.7|mL|IM|LA^^Left Arm||||||N8901O||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||197^Influenza HD Quadrivalent^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20240815||||||F
OBX|4|CE|69764-9^Document Type^LN||253088698300028411171010^FLUZONE HIGH-DOSE QUADRIVALENT^NDC||||||F
```

---

## 8. VXU^V04 - Shingles vaccine administered at Deaconess Health

```
MSH|^~\&|CLINIC_EMR|DEAC_PC|CHIRP|ISDH|20250319091000||VXU^V04^VXU_V04|CHIRP00021234|P|2.5.1|||AL|NE
PID|1||DEAC_MRN60006789^^^DEAC^MR||Whitfield^Barbara^Jean||19480725|F|||1205 Green River Rd^^Evansville^IN^47715^US||^PRN^PH^^1^812^5556789||ENG|W|MET|SSN723-45-1968^^^SS
PD1|||DEACONESS PRIMARY CARE^^60006|PRIMMD^Owens^Gregory^W^^^MD
ORC|RE|CHIRP_SUB014||||||||||PRIMMD^Owens^Gregory^W^^^MD
RXA|0|1|20250319090500|20250319090500|187^Recombinant Zoster^CVX|0.5|mL|IM|RA^^Right Arm||||||P9012Q||GSK^GlaxoSmithKline|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V04^Medicare^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||187^Recombinant Zoster^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20211015||||||F
OBX|4|NM|30973-2^Dose Number^LN||1||||||F
```

---

## 9. QBP^Q11 - Provider query for patient immunization forecast

```
MSH|^~\&|CLINIC_EMR|CHN_PEDS|CHIRP|ISDH|20250320083000||QBP^Q11^QBP_Q11|CHIRP00024567|P|2.5.1|||AL|NE
QPD|Z44^Request Immunization History^CDCPHINVS|PQRY002345|CHN_MRN90002345^^^CHN^MR|Vasquez^Diego^Rafael||20241112|M|||1547 East 82nd St^^Indianapolis^IN^46240
RCP|I|99^RD
```

---

## 10. RSP^K11 - Immunization forecast response with recommendations

```
MSH|^~\&|CHIRP|ISDH|CLINIC_EMR|CHN_PEDS|20250320083010||RSP^K11^RSP_K11|CHIRP00024568|P|2.5.1|||AL|NE
MSA|AA|CHIRP00024567
QAK|PQRY002345|OK|Z44^Request Immunization History^CDCPHINVS
QPD|Z44^Request Immunization History^CDCPHINVS|PQRY002345|CHN_MRN90002345^^^CHN^MR|Vasquez^Diego^Rafael||20241112|M
PID|1||CHIRP_ID004567^^^CHIRP^SR||Vasquez^Diego^Rafael||20241112|M|||1547 East 82nd St^^Indianapolis^IN^46240^US
ORC|RE|CHIRP_HIST002||||||||||
RXA|0|1|20250112|20250112|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|||||||C4567B||GSK^GlaxoSmithKline
RXA|0|1|20250112|20250112|133^PCV13^CVX|0.5|mL|IM|||||||D8901C||PFR^Pfizer
RXA|0|1|20250112|20250112|116^Rotavirus Pentavalent^CVX|2.0|mL|PO|||||||E2345D||MSD^Merck Sharp & Dohme
RXA|0|1|20250312|20250312|120^DTaP-Hep B-IPV (Pediarix)^CVX|0.5|mL|IM|||||||C4567B||GSK^GlaxoSmithKline
RXA|0|1|20250312|20250312|133^PCV13^CVX|0.5|mL|IM|||||||D8901C||PFR^Pfizer
RXA|0|1|20250312|20250312|116^Rotavirus Pentavalent^CVX|2.0|mL|PO|||||||E2345D||MSD^Merck Sharp & Dohme
OBX|1|CE|30979-9^Vaccines Due Next^LN||120^DTaP-Hep B-IPV^CVX||||||F
OBX|2|TS|30980-7^Date Vaccine Due^LN||20250512||||||F
OBX|3|CE|30979-9^Vaccines Due Next^LN||133^PCV13^CVX||||||F
OBX|4|TS|30980-7^Date Vaccine Due^LN||20250512||||||F
```

---

## 11. VXU^V04 - Hepatitis B birth dose reported from IU Health

```
MSH|^~\&|NURSERY_EMR|IUH_METH|CHIRP|ISDH|20250321200000||VXU^V04^VXU_V04|CHIRP00027890|P|2.5.1|||AL|NE
PID|1||IUH_NB002345^^^IUH^MR||Caldwell^Baby Boy||20250321|M|||2318 North Capitol Ave^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^5557890||ENG||NON|SSN000-00-0000^^^SS
PD1|||IU HEALTH METHODIST NURSERY^^NB002|NEOMD^Reeves^Jillian^S^^^MD
NK1|1|Caldwell^Amber^Nicole|MTH|2318 North Capitol Ave^^Indianapolis^IN^46204^US|^PRN^PH^^1^317^5557890
ORC|RE|CHIRP_SUB015||||||||||NEOMD^Reeves^Jillian^S^^^MD
RXA|0|1|20250321195500|20250321195500|08^Hep B Adolescent or Pediatric^CVX|0.5|mL|IM|RT^^Right Thigh||||||Q0123R||MSD^Merck Sharp & Dohme|||||A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC1^Medicaid^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||08^Hep B Adolescent or Pediatric^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
OBX|4|NM|30973-2^Dose Number^LN||1||||||F
OBX|5|NM|8339-4^Birth Weight^LN||3420|g|||||F
```

---

## 12. VXU^V04 - Travel immunizations at IU Health Travel Clinic

```
MSH|^~\&|TRAVEL_EMR|IUH_TRAVEL|CHIRP|ISDH|20250322143000||VXU^V04^VXU_V04|CHIRP00031234|P|2.5.1|||AL|NE
PID|1||IUH_MRN80007890^^^IUH^MR||Bhatt^Priya^Lakshmi||19880315|F|||1935 Broad Ripple Ave^^Indianapolis^IN^46220^US||^PRN^PH^^1^317^5557891||HIN|S|HIN|SSN814-29-6753^^^SS
PD1|||IU HEALTH TRAVEL CLINIC^^80007|TRAVMD^Emerson^Charles^R^^^MD
ORC|RE|CHIRP_SUB016||||||||||TRAVMD^Emerson^Charles^R^^^MD
RXA|0|1|20250322142000|20250322142000|25^Typhoid Vi Polysaccharide^CVX|0.5|mL|IM|RA^^Right Arm||||||R2345S||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
ORC|RE|CHIRP_SUB017||||||||||TRAVMD^Emerson^Charles^R^^^MD
RXA|0|1|20250322142500|20250322142500|37^Yellow Fever^CVX|0.5|mL|SC|LA^^Left Arm||||||S3456T||SNF^Sanofi Pasteur|||||A
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
ORC|RE|CHIRP_SUB018||||||||||TRAVMD^Emerson^Charles^R^^^MD
RXA|0|1|20250322143000|20250322143000|52^Hep A Adult^CVX|1.0|mL|IM|RA^^Right Arm||||||T4567U||GSK^GlaxoSmithKline|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||25^Typhoid Vi Polysaccharide^CVX||||||F
```

---

## 13. VXU^V04 - COVID primary series for child at Eskenazi Health

```
MSH|^~\&|PED_EMR|ESK_PEDS|CHIRP|ISDH|20250323101500||VXU^V04^VXU_V04|CHIRP00034567|P|2.5.1|||AL|NE
PID|1||ESK_MRN70008901^^^ESK^MR||Jefferson^Amara^Denise||20200430|F|||2190 East 38th St^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^5558901||ENG||BAP|SSN000-00-0000^^^SS
PD1|||ESKENAZI PEDIATRICS^^70008|PEDMD^Barnes^Keith^M^^^MD
NK1|1|Jefferson^Tamika^Elaine|MTH|2190 East 38th St^^Indianapolis^IN^46205^US|^PRN^PH^^1^317^5558901
ORC|RE|CHIRP_SUB019||||||||||PEDMD^Barnes^Keith^M^^^MD
RXA|0|1|20250323101000|20250323101000|300^COVID-19 Vaccine mRNA BV^CVX|0.25|mL|IM|LA^^Left Arm||||||U5678V||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||300^COVID-19 Vaccine mRNA BV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20240812||||||F
OBX|4|NM|30973-2^Dose Number^LN||1||||||F
```

---

## 14. VXU^V04 - Pneumococcal vaccine for elderly patient at Franciscan

```
MSH|^~\&|CLINIC_EMR|FRAN_PC|CHIRP|ISDH|20250324141000||VXU^V04^VXU_V04|CHIRP00037890|P|2.5.1|||AL|NE
PID|1||FRAN_MRN40009012^^^FRAN^MR||Kowalski^Helen^Mae||19420614|F|||1820 Indianapolis Blvd^^East Chicago^IN^46312^US||^PRN^PH^^1^219^5559012||ENG|W|BAP|SSN305-78-4192^^^SS
PD1|||FRANCISCAN PRIMARY CARE EC^^40009|PRIMMD^Delgado^Roberto^A^^^MD
ORC|RE|CHIRP_SUB020||||||||||PRIMMD^Delgado^Roberto^A^^^MD
RXA|0|1|20250324140500|20250324140500|152^PCV20^CVX|0.5|mL|IM|LA^^Left Arm||||||V6789W||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V04^Medicare^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||152^PCV20^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20220601||||||F
OBX|4|NM|30973-2^Dose Number^LN||1||||||F
```

---

## 15. VXU^V04 - Back-to-school Tdap booster at Community Health

```
MSH|^~\&|PEDS_EMR|CHN_NORTH|CHIRP|ISDH|20250325100000||VXU^V04^VXU_V04|CHIRP00041234|P|2.5.1|||AL|NE
PID|1||CHN_MRN90010123^^^CHN^MR||Rao^Arjun^Vikram||20140215|M|||4319 East 96th St^^Indianapolis^IN^46240^US||^PRN^PH^^1^317^5550123||HIN||HIN|SSN000-00-0000^^^SS
PD1|||COMMUNITY HEALTH NORTH PEDS^^90010|PEDMD^Morton^Craig^L^^^MD
NK1|1|Rao^Sunita^Devi|MTH|4319 East 96th St^^Indianapolis^IN^46240^US|^PRN^PH^^1^317^5550123
ORC|RE|CHIRP_SUB021||||||||||PEDMD^Morton^Craig^L^^^MD
RXA|0|1|20250325095500|20250325095500|115^Tdap^CVX|0.5|mL|IM|RA^^Right Arm||||||W7890X||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||115^Tdap^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
```

---

## 16. VXU^V04 - Immunization with VFC-supplied vaccine at health department

```
MSH|^~\&|HD_EMR|MCPHD|CHIRP|ISDH|20250326093000||VXU^V04^VXU_V04|CHIRP00044567|P|2.5.1|||AL|NE
PID|1||MCPHD_MRN80011234^^^MCPHD^MR||Cervantes^Diego^Manuel||20190408|M|||1945 South Meridian St^^Indianapolis^IN^46225^US||^PRN^PH^^1^317^5551234||SPA||CAT|SSN000-00-0000^^^SS
PD1|||MARION COUNTY PUBLIC HEALTH^^80011|PHMD^Pearson^Cynthia^L^^^MD
NK1|1|Cervantes^Maria^Guadalupe|MTH|1945 South Meridian St^^Indianapolis^IN^46225^US|^PRN^PH^^1^317^5551234
ORC|RE|CHIRP_SUB022||||||||||PHMD^Pearson^Cynthia^L^^^MD
RXA|0|1|20250326092000|20250326092000|83^Hep A Pediatric^CVX|0.5|mL|IM|RT^^Right Thigh||||||X8901Y||GSK^GlaxoSmithKline|||||A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC3^VFC eligible^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||83^Hep A Pediatric^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200101||||||F
OBX|4|CE|VFC-STATUS^VFC Eligibility^L||V03^Uninsured^CDCPHINVS||||||F
```

---

## 17. VXU^V04 - Historical immunization record entry with VIS PDF

```
MSH|^~\&|CLINIC_EMR|PKV_FM|CHIRP|ISDH|20250327110000||VXU^V04^VXU_V04|CHIRP00047890|P|2.5.1|||AL|NE
PID|1||PKV_MRN70012345^^^PKV^MR||Stratton^Noah^Alexander||20180620|M|||2415 Covington Rd^^Fort Wayne^IN^46804^US||^PRN^PH^^1^260^5552345||ENG||LUT|SSN000-00-0000^^^SS
PD1|||PARKVIEW FAMILY MEDICINE^^70012|FAMMED^Lyons^Jessica^M^^^MD
NK1|1|Stratton^Courtney^Dawn|MTH|2415 Covington Rd^^Fort Wayne^IN^46804^US|^PRN^PH^^1^260^5552345
ORC|RE|CHIRP_SUB023||||||||||FAMMED^Lyons^Jessica^M^^^MD
RXA|0|1|20250327105000|20250327105000|141^Influenza Seasonal^CVX|0.5|mL|IM|LA^^Left Arm||||||Y9012Z||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||141^Influenza Seasonal^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20240815||||||F
OBX|4|ED|VIS^Vaccine Information Statement PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 18. VXU^V04 - College entry meningococcal B vaccine

```
MSH|^~\&|STUDENT_EMR|IU_HEALTH|CHIRP|ISDH|20250328091500||VXU^V04^VXU_V04|CHIRP00051234|P|2.5.1|||AL|NE
PID|1||IU_MRN90013456^^^IU_SHS^MR||Hoffman^Tyler^James||20060812|M|||3417 East 3rd St^^Bloomington^IN^47401^US||^PRN^PH^^1^812^5553456||ENG|S|NON|SSN479-31-6028^^^SS
PD1|||IU STUDENT HEALTH SERVICE^^90013|STUMD^Blackwell^Katherine^P^^^MD
NK1|1|Hoffman^Robert^Daniel|FTH|9214 Township Line Rd^^Indianapolis^IN^46220^US|^PRN^PH^^1^317^5553457
ORC|RE|CHIRP_SUB024||||||||||STUMD^Blackwell^Katherine^P^^^MD
RXA|0|1|20250328091000|20250328091000|163^Meningococcal B FHbp^CVX|0.5|mL|IM|RA^^Right Arm||||||Z0123A||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||163^Meningococcal B FHbp^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20191024||||||F
OBX|4|NM|30973-2^Dose Number^LN||1||||||F
```

---

## 19. VXU^V04 - Mass vaccination event with immunization certificate PDF

```
MSH|^~\&|EVENT_EMR|MCPHD|CHIRP|ISDH|20250329140000||VXU^V04^VXU_V04|CHIRP00054567|P|2.5.1|||AL|NE
PID|1||EVENT_MRN90014567^^^MCPHD^MR||Garner^Marcus^DeShawn||19750304|M|||1812 West Michigan St^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^5554567||ENG|S|BAP|SSN621-38-7504^^^SS
PD1|||MARION COUNTY HEALTH EVENT^^90014|PHMD^Pearson^Cynthia^L^^^MD
ORC|RE|CHIRP_SUB025||||||||||PHMD^Pearson^Cynthia^L^^^MD
RXA|0|1|20250329135500|20250329135500|300^COVID-19 Vaccine mRNA BV^CVX|0.5|mL|IM|LA^^Left Arm||||||AA1234B||PFR^Pfizer|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V05^Section 317^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||300^COVID-19 Vaccine mRNA BV^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20240812||||||F
OBX|4|ED|IMM_CERT^Immunization Certificate PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 20. QBP^Q11 - Pharmacy query for patient immunization status before flu shot

```
MSH|^~\&|PHARM_SYS|CVS_INDY|CHIRP|ISDH|20250330153000||QBP^Q11^QBP_Q11|CHIRP00057890|P|2.5.1|||AL|NE
QPD|Z44^Request Immunization History^CDCPHINVS|RXQRY003456|CVS_MRN90015678^^^CVS^MR|Dalton^Kenneth^Wayne||19520310|M|||2340 Grape Rd^^Mishawaka^IN^46545
RCP|I|99^RD
```
