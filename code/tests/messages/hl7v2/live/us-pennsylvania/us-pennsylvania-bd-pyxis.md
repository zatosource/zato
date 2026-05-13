# BD Pyxis MedStation - real HL7v2 ER7 messages

---

## 1. RDS^O13 - Dispense of metoprolol tartrate from Pyxis cabinet

```
MSH|^~\&|PYXIS|UPMC_PRESBY^2.16.840.1.113883.3.1902^ISO|PHARMACY|UPMC_HIS|20260502143022||RDS^O13^RDS_O13|PYX20260502143022001|P|2.5.1|||AL|NE
PID|1||MRN80012345^^^UPMC^MR||Kowalczyk^Irena^Celina^^Mrs.^||19671023|F||2106-3^White^CDCREC|1247 Forbes Ave^^Pittsburgh^PA^15213^US^H||^PRN^PH^^1^412^5559234|||M^Married^HL70002|||234-56-7890|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|5SOUTH^5102^01^UPMC_PRESBY^^^^N|U^Urgent^HL70007|||1234567890^Krasinski^Marek^N^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260430001^^^UPMC^VN|||||||||||||||||||||||||||20260430081500
ORC|RE|ORD90001^PYXIS|RX70001^PHARMACY||CM^Complete^HL70038|||20260502142800|||1234567890^Krasinski^Marek^N^^^MD^^^^NPI
RXD|1|00186-1092-05^metoprolol tartrate 50mg tab^NDC|20260502143000|2||TAB^tablet^HL70292|||||||00186-1092-05||NURSE_RWALSH^Walsh^Rita^E^^^RN
RXR|PO^Oral^HL70162
```

---

## 2. RDS^O13 - Dispense of vancomycin IV from Pyxis cabinet

```
MSH|^~\&|BD_PYXIS|PENN_HUP^2.16.840.1.113883.3.3401^ISO|PHARMACY|PENNMED_HIS|20260503091245||RDS^O13^RDS_O13|PYX20260503091245002|P|2.5.1|||AL|NE
PID|1||MRN80023456^^^PENNMED^MR||Jefferson^Darnell^Xavier^^Mr.^||19780315|M||2054-5^Black or African American^CDCREC|3920 Chestnut St^^Philadelphia^PA^19104^US^H||^PRN^PH^^1^215^5558471|||S^Single^HL70002|||345-67-8901|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|7ICU^7014^01^PENN_HUP^^^^N|E^Emergency^HL70007|||2345678901^Ranganathan^Priya^S^^^MD^^^^NPI||INF^Infectious Disease^HL70069||||||||||VN20260501002^^^PENNMED^VN|||||||||||||||||||||||||||20260501192200
ORC|RE|ORD90002^BD_PYXIS|RX70002^PHARMACY||CM^Complete^HL70038|||20260503091000|||2345678901^Ranganathan^Priya^S^^^MD^^^^NPI
RXD|1|00409-6509-01^vancomycin 1g/200mL IV premix^NDC|20260503091200|1||BAG^IV bag^HL70292|||||1000|MG^milligram^ISO+|||NURSE_TFLYNN^Flynn^Teresa^A^^^RN
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
```

---

## 3. ADT^A01 - Patient admission to surgical unit triggering Pyxis profile load

```
MSH|^~\&|MEDSTATION|GEISINGER_MC^2.16.840.1.113883.3.5501^ISO|ADT_RECV|GEISINGER_HIS|20260504070530||ADT^A01^ADT_A01|PYX20260504070530003|P|2.5.1|||AL|NE
EVN|A01|20260504070000|||ADMITTING^Admitting^Office^^^||20260504070000
PID|1||MRN80034567^^^GEISINGER^MR||Cieslak^Henryk^Tadeusz^^Mr.^||19520618|M||2106-3^White^CDCREC|892 Market St^^Danville^PA^17821^US^H||^PRN^PH^^1^570^5553847|||M^Married^HL70002|||456-78-9012|||N^Not Hispanic or Latino^CDCREC
PD1|||Geisinger Medical Center^^^^NPI|3456789012^Vasquez^Elena^K^^^MD^^^^NPI
NK1|1|Cieslak^Jadwiga^Anna^^Mrs.|SPO^Spouse^HL70063|892 Market St^^Danville^PA^17821^US|^PRN^PH^^1^570^5553848||EC^Emergency Contact^HL70131
PV1|1|I|SURG^3205^02^GEISINGER_MC^^^^N|E^Emergency^HL70007|||3456789012^Vasquez^Elena^K^^^MD^^^^NPI|4567890123^Hwang^Sung^L^^^MD^^^^NPI|GEN^General Surgery^HL70069||||||A^Accident^HL70007|||||VN20260504003^^^GEISINGER^VN|||||||||||||||||||||||||||20260504070000
PV2|||^Acute appendicitis||||||20260504|2
DG1|1||K35.80^Unspecified acute appendicitis without abscess^I10||20260504|A
GT1|1||Cieslak^Henryk^Tadeusz^^Mr.||892 Market St^^Danville^PA^17821^US|^PRN^PH^^1^570^5553847|||||SE^Self^HL70063
IN1|1|GHPLN001|54321^Geisinger Health Plan|GHP^^Danville^PA^17822|||||GRP987654||||||Cieslak^Henryk^Tadeusz|SE^Self^HL70063|19520618|892 Market St^^Danville^PA^17821^US|Y||1||||||||||||||POL556677
```

---

## 4. RDE^O11 - Pharmacy order for hydromorphone PCA pump via Pyxis

```
MSH|^~\&|PYXIS|UPMC_SHDY^2.16.840.1.113883.3.1903^ISO|PHARMACY|UPMC_HIS|20260504153012||RDE^O11^RDE_O11|PYX20260504153012004|P|2.5.1|||AL|NE
PID|1||MRN80045678^^^UPMC^MR||Callahan^Declan^Patrick^^Mr.^||19850911|M||2106-3^White^CDCREC|415 Shady Ave^^Pittsburgh^PA^15206^US^H||^PRN^PH^^1^412^5557612|||S^Single^HL70002|||567-89-0123|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|PACU^2008^01^UPMC_SHDY^^^^N|E^Emergency^HL70007|||5678901234^Pellegrino^Marco^M^^^MD^^^^NPI||ANE^Anesthesiology^HL70069||||||||||VN20260504004^^^UPMC^VN|||||||||||||||||||||||||||20260504120000
ORC|NW|ORD90004^PYXIS||GRP90004^PYXIS|||||20260504152500|||5678901234^Pellegrino^Marco^M^^^MD^^^^NPI|||||UPMC_SHDY^UPMC Shadyside
RXE|1^BID^HL70335|59011-0442-10^hydromorphone HCl 1mg/mL PCA syringe^NDC|0.2|1|MG^milligram^ISO+|ML^milliliter^ISO+||||30||MG^milligram^ISO+
RXR|IV^Intravenous^HL70162
RXC|B^Base^HL70166|59011-0442-10^hydromorphone HCl 1mg/mL^NDC|30|ML^milliliter^ISO+
NTE|1||PCA settings: demand dose 0.2mg, lockout 6 min, 4hr limit 6mg. Basal rate 0mg/hr.
```

---

## 5. RGV^O15 - Pharmacy give of insulin lispro via Pyxis

```
MSH|^~\&|BD_PYXIS|LVHN_CC^2.16.840.1.113883.3.6601^ISO|PHARMACY|LVHN_HIS|20260505081530||RGV^O15^RGV_O15|PYX20260505081530005|P|2.5.1|||AL|NE
PID|1||MRN80056789^^^LVHN^MR||Fuentes^Gabriela^Carmen^^Ms.^||19900704|F||2106-3^White^CDCREC|2145 Cedar Crest Blvd^^Allentown^PA^18103^US^H||^PRN^PH^^1^610^5559381|||S^Single^HL70002|||678-90-1234|||H^Hispanic or Latino^CDCREC
PV1|1|I|MED^4310^01^LVHN_CC^^^^N|U^Urgent^HL70007|||6789012345^Albright^Thomas^R^^^MD^^^^NPI||END^Endocrinology^HL70069||||||||||VN20260503005^^^LVHN^VN|||||||||||||||||||||||||||20260503143000
ORC|RE|ORD90005^BD_PYXIS|RX70005^PHARMACY||CM^Complete^HL70038|||20260505081200|||6789012345^Albright^Thomas^R^^^MD^^^^NPI
RXG|1|0002-7714-17^insulin lispro (Humalog) 100 units/mL^NDC|8|8|UNIT^unit^ISO+||20260505081500|||NURSE_JNGUYEN^Nguyen^Janet^L^^^RN
RXR|SC^Subcutaneous^HL70162|ABD^Abdomen^HL70163
```

---

## 6. ADT^A02 - Patient transfer between units updating Pyxis cabinet assignment

```
MSH|^~\&|MEDSTATION|PENN_PAH^2.16.840.1.113883.3.3402^ISO|ADT_RECV|PENNMED_HIS|20260505141500||ADT^A02^ADT_A01|PYX20260505141500006|P|2.5.1|||AL|NE
EVN|A02|20260505141000|||BEDCONTROL^Bed^Control^^^||20260505141000
PID|1||MRN80067890^^^PENNMED^MR||Okafor^Denise^Renee^^Mrs.^||19630228|F||2054-5^Black or African American^CDCREC|5501 Old York Rd^^Philadelphia^PA^19141^US^H||^PRN^PH^^1^215^5552748|||M^Married^HL70002|||789-01-2345|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MICU^6024^01^PENN_PAH^^^^N|E^Emergency^HL70007|||7890123456^Donovan^Caitlin^C^^^MD^^^^NPI||PUL^Pulmonology^HL70069||||||||||VN20260503006^^^PENNMED^VN|||||||||||||||||||||||||||20260503221500
PV2|||^Acute respiratory failure with COPD exacerbation||||||20260503|5
```

---

## 7. RAS^O17 - Medication administration of enoxaparin recorded by Pyxis

```
MSH|^~\&|PYXIS|UPMC_MERCY^2.16.840.1.113883.3.1904^ISO|PHARMACY|UPMC_HIS|20260505201030||RAS^O17^RAS_O17|PYX20260505201030007|P|2.5.1|||AL|NE
PID|1||MRN80078901^^^UPMC^MR||Moretti^Salvatore^Vincent^^Mr.^||19480506|M||2106-3^White^CDCREC|1837 Boulevard of the Allies^^Pittsburgh^PA^15219^US^H||^PRN^PH^^1^412^5554193|||W^Widowed^HL70002|||890-12-3456|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ORTH^4108^01^UPMC_MERCY^^^^N|E^Emergency^HL70007|||8901234567^Donahue^Siobhan^M^^^MD^^^^NPI||ORT^Orthopedics^HL70069||||||||||VN20260504007^^^UPMC^VN|||||||||||||||||||||||||||20260504111200
ORC|RE|ORD90007^PYXIS|RX70007^PHARMACY||CM^Complete^HL70038|||20260505200800|||8901234567^Donahue^Siobhan^M^^^MD^^^^NPI
RXA|0|1|20260505201000|20260505201000|00075-0621-30^enoxaparin sodium 40mg/0.4mL syringe^NDC|40|MG^milligram^ISO+|SC^Subcutaneous^HL70162||NURSE_VPATEL^Patel^Vidya^N^^^RN||||||||||20260505201000
RXR|SC^Subcutaneous^HL70162|ABD^Abdomen^HL70163
```

---

## 8. DFT^P03 - Charge capture for dispensed controlled substance from Pyxis

```
MSH|^~\&|BD_PYXIS|GEISINGER_MC^2.16.840.1.113883.3.5501^ISO|BILLING|GEISINGER_HIS|20260506083045||DFT^P03^DFT_P03|PYX20260506083045008|P|2.5.1|||AL|NE
EVN|P03|20260506083000
PID|1||MRN80089012^^^GEISINGER^MR||Mazurek^Bozena^Halina^^Mrs.^||19710319|F||2106-3^White^CDCREC|1544 Bloom Rd^^Danville^PA^17821^US^H||^PRN^PH^^1^570^5557291|||M^Married^HL70002|||901-23-4567|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SURG^3212^01^GEISINGER_MC^^^^N|U^Urgent^HL70007|||9012345678^Lichtenstein^Gerhard^W^^^MD^^^^NPI||GEN^General Surgery^HL70069||||||||||VN20260505008^^^GEISINGER^VN|||||||||||||||||||||||||||20260505070000
FT1|1|20260506083000|20260506083000|CG^Charge^HL70017|DR|250.00||1||||||SURG^3212^01^GEISINGER_MC|||||||||00406-0512-01^oxycodone HCl 5mg tab^NDC
FT1|2|20260506083000|20260506083000|CG^Charge^HL70017|DR|18.50||2||||||SURG^3212^01^GEISINGER_MC|||||||||00093-0150-01^acetaminophen 325mg tab^NDC
```

---

## 9. RDS^O13 - Dispense of cefazolin IV piggyback pre-op

```
MSH|^~\&|PYXIS|LVHN_MH^2.16.840.1.113883.3.6602^ISO|PHARMACY|LVHN_HIS|20260506054512||RDS^O13^RDS_O13|PYX20260506054512009|P|2.5.1|||AL|NE
PID|1||MRN80090123^^^LVHN^MR||Stoltzfus^Amos^Levi^^Mr.^||19811225|M||2106-3^White^CDCREC|4780 Hamilton Blvd^^Allentown^PA^18103^US^H||^PRN^PH^^1^610^5553174|||M^Married^HL70002|||012-34-5678|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|PREOP^1002^01^LVHN_MH^^^^N|E^Emergency^HL70007|||0123456789^Goldberg^Nathan^D^^^MD^^^^NPI||GEN^General Surgery^HL70069||||||||||VN20260506009^^^LVHN^VN|||||||||||||||||||||||||||20260506040000
ORC|RE|ORD90009^PYXIS|RX70009^PHARMACY||CM^Complete^HL70038|||20260506054000|||0123456789^Goldberg^Nathan^D^^^MD^^^^NPI
RXD|1|00338-3507-41^cefazolin 2g/100mL IV piggyback^NDC|20260506054500|1||BAG^IV bag^HL70292|||||2000|MG^milligram^ISO+|||NURSE_MHICKS^Hicks^Monica^S^^^RN
RXR|IV^Intravenous^HL70162|RA^Right Arm^HL70163
NTE|1||Pre-operative prophylaxis per surgical protocol. Infuse over 30 minutes prior to incision.
```

---

## 10. ADT^A03 - Patient discharge clearing Pyxis medication profile

```
MSH|^~\&|MEDSTATION|UPMC_PRESBY^2.16.840.1.113883.3.1902^ISO|ADT_RECV|UPMC_HIS|20260507101530||ADT^A03^ADT_A03|PYX20260507101530010|P|2.5.1|||AL|NE
EVN|A03|20260507101000|||DISCH^Discharge^Coord^^^||20260507101000
PID|1||MRN80012345^^^UPMC^MR||Kowalczyk^Irena^Celina^^Mrs.^||19671023|F||2106-3^White^CDCREC|1247 Forbes Ave^^Pittsburgh^PA^15213^US^H||^PRN^PH^^1^412^5559234|||M^Married^HL70002|||234-56-7890|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|5SOUTH^5102^01^UPMC_PRESBY^^^^N|U^Urgent^HL70007|||1234567890^Krasinski^Marek^N^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260430001^^^UPMC^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260430081500|20260507101000
DG1|1||I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^I10||20260430|A
DG1|2||I10^Essential hypertension^I10||20260430|A
```

---

## 11. RDE^O11 - Pharmacy order for heparin drip via Pyxis

```
MSH|^~\&|BD_PYXIS|PENN_HUP^2.16.840.1.113883.3.3401^ISO|PHARMACY|PENNMED_HIS|20260507190530||RDE^O11^RDE_O11|PYX20260507190530011|P|2.5.1|||AL|NE
PID|1||MRN80101234^^^PENNMED^MR||Leibowitz^Nathan^Ephraim^^Mr.^||19590722|M||2106-3^White^CDCREC|245 S Broad St^^Philadelphia^PA^19107^US^H||^PRN^PH^^1^215^5558012|||M^Married^HL70002|||123-45-6789|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|CCU^8016^01^PENN_HUP^^^^N|E^Emergency^HL70007|||1357924680^Chakraborty^Anita^P^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260506011^^^PENNMED^VN|||||||||||||||||||||||||||20260506153000
ORC|NW|ORD90011^BD_PYXIS||GRP90011^BD_PYXIS|||||20260507190000|||1357924680^Chakraborty^Anita^P^^^MD^^^^NPI|||||PENN_HUP^Hospital of the University of Pennsylvania
RXE|1^CONTINUOUS^HL70335|00338-0481-02^heparin sodium 25000 units/500mL D5W^NDC|1000|1000|UNIT^unit^ISO+|HR^hour^ISO+||||25000||UNIT^unit^ISO+
RXR|IV^Intravenous^HL70162
RXC|B^Base^HL70166|00338-0481-02^heparin sodium 25000 units/500mL^NDC|500|ML^milliliter^ISO+
NTE|1||Heparin protocol: target aPTT 60-80 sec. Check aPTT q6h. Adjust per pharmacy nomogram.
```

---

## 12. RGV^O15 - Pharmacy give of fentanyl patch via Pyxis cabinet

```
MSH|^~\&|PYXIS|GEISINGER_MC^2.16.840.1.113883.3.5501^ISO|PHARMACY|GEISINGER_HIS|20260507220045||RGV^O15^RGV_O15|PYX20260507220045012|P|2.5.1|||AL|NE
PID|1||MRN80112345^^^GEISINGER^MR||Kaczmarek^Wanda^Zofia^^Mrs.^||19440913|F||2106-3^White^CDCREC|310 Pine St^^Williamsport^PA^17701^US^H||^PRN^PH^^1^570^5556182|||W^Widowed^HL70002|||234-56-7891|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ONCO^2106^01^GEISINGER_MC^^^^N|R^Routine^HL70007|||2468013579^Strickland^Owen^A^^^MD^^^^NPI||ONC^Oncology^HL70069||||||||||VN20260505012^^^GEISINGER^VN|||||||||||||||||||||||||||20260505091000
ORC|RE|ORD90012^PYXIS|RX70012^PHARMACY||CM^Complete^HL70038|||20260507215800|||2468013579^Strickland^Owen^A^^^MD^^^^NPI
RXG|1|00591-3861-01^fentanyl transdermal patch 25mcg/hr^NDC|1|1|PATCH^patch^ISO+||20260507220000|||NURSE_DCRAWFORD^Crawford^Donna^M^^^RN
RXR|TD^Transdermal^HL70162|UA^Upper Arm^HL70163
```

---

## 13. ADT^A08 - Patient allergy update synced to Pyxis profile

```
MSH|^~\&|MEDSTATION|LVHN_CC^2.16.840.1.113883.3.6601^ISO|ADT_RECV|LVHN_HIS|20260508091200||ADT^A08^ADT_A01|PYX20260508091200013|P|2.5.1|||AL|NE
EVN|A08|20260508090800|||RPHARM^Pharmacist^Review^^^||20260508090800
PID|1||MRN80123456^^^LVHN^MR||Villarreal^Lucia^Marisol^^Ms.^||19880216|F||2106-3^White^CDCREC|1028 Linden St^^Bethlehem^PA^18018^US^H||^PRN^PH^^1^610^5557834|||S^Single^HL70002|||345-67-8912|||H^Hispanic or Latino^CDCREC
PV1|1|I|MED^3207^01^LVHN_CC^^^^N|U^Urgent^HL70007|||3579246801^Yun^Daniel^H^^^MD^^^^NPI||MED^Medicine^HL70069||||||||||VN20260507013^^^LVHN^VN|||||||||||||||||||||||||||20260507160000
AL1|1|DA^Drug Allergy^HL70127|70618^Penicillin^RxNorm|MO^Moderate^HL70128|Rash and urticaria|20200315
AL1|2|DA^Drug Allergy^HL70127|2670^Codeine^RxNorm|SV^Severe^HL70128|Anaphylaxis|20180901
AL1|3|DA^Drug Allergy^HL70127|36437^Sulfonamide^RxNorm|MI^Mild^HL70128|Nausea|20210610
```

---

## 14. RDS^O13 - Dispense of morphine sulfate with witness verification from Pyxis

```
MSH|^~\&|PYXIS|UPMC_MAGEE^2.16.840.1.113883.3.1905^ISO|PHARMACY|UPMC_HIS|20260508143522||RDS^O13^RDS_O13|PYX20260508143522014|P|2.5.1|||AL|NE
PID|1||MRN80134567^^^UPMC^MR||Booker^Tamika^Elise^^Ms.^||19930412|F||2054-5^Black or African American^CDCREC|4215 Fifth Ave^^Pittsburgh^PA^15213^US^H||^PRN^PH^^1^412^5551847|||S^Single^HL70002|||456-78-9013|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|L&D^2204^01^UPMC_MAGEE^^^^N|U^Urgent^HL70007|||4680135792^Santiago^Miguel^L^^^MD^^^^NPI||OBG^Obstetrics and Gynecology^HL70069||||||||||VN20260508014^^^UPMC^VN|||||||||||||||||||||||||||20260508023000
ORC|RE|ORD90014^PYXIS|RX70014^PHARMACY||CM^Complete^HL70038|||20260508143200|||4680135792^Santiago^Miguel^L^^^MD^^^^NPI
RXD|1|00406-8530-01^morphine sulfate 4mg/mL injection^NDC|20260508143500|1||SYR^syringe^HL70292|||||4|MG^milligram^ISO+|||NURSE_LCHANG^Chang^Lisa^J^^^RN
RXR|IV^Intravenous^HL70162
NTE|1||Witness: NURSE_BTURNER (Turner, Brenda R, RN). Controlled substance - Schedule II. Waste: 0mg. Full dose administered.
```

---

## 15. DFT^P03 - Batch charge capture for multiple Pyxis dispenses

```
MSH|^~\&|BD_PYXIS|PENN_PAH^2.16.840.1.113883.3.3402^ISO|BILLING|PENNMED_HIS|20260508180000||DFT^P03^DFT_P03|PYX20260508180000015|P|2.5.1|||AL|NE
EVN|P03|20260508175500
PID|1||MRN80145678^^^PENNMED^MR||Tran^Minh^Duc^^Mr.^||19760803|M||2028-9^Asian^CDCREC|1320 Locust St^^Philadelphia^PA^19107^US^H||^PRN^PH^^1^215^5553917|||M^Married^HL70002|||567-89-0124|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MICU^6018^01^PENN_PAH^^^^N|E^Emergency^HL70007|||5791346802^Abramowitz^Rachel^F^^^MD^^^^NPI||PUL^Pulmonology^HL70069||||||||||VN20260506015^^^PENNMED^VN|||||||||||||||||||||||||||20260506201500
FT1|1|20260508060000|20260508060000|CG^Charge^HL70017|DR|85.00||1||||||MICU^6018^01^PENN_PAH|||||||||00409-6509-01^vancomycin 1g/200mL IV premix^NDC
FT1|2|20260508120000|20260508120000|CG^Charge^HL70017|DR|12.50||2||||||MICU^6018^01^PENN_PAH|||||||||00071-0150-24^furosemide 20mg tab^NDC
FT1|3|20260508140000|20260508140000|CG^Charge^HL70017|DR|42.00||1||||||MICU^6018^01^PENN_PAH|||||||||00338-0049-04^potassium chloride 20mEq/100mL IV^NDC
FT1|4|20260508175500|20260508175500|CG^Charge^HL70017|DR|15.75||1||||||MICU^6018^01^PENN_PAH|||||||||00093-0150-01^acetaminophen 325mg tab^NDC
```

---

## 16. RAS^O17 - Administration of IV push lorazepam from Pyxis

```
MSH|^~\&|MEDSTATION|GEISINGER_MC^2.16.840.1.113883.3.5501^ISO|PHARMACY|GEISINGER_HIS|20260508230145||RAS^O17^RAS_O17|PYX20260508230145016|P|2.5.1|||AL|NE
PID|1||MRN80156789^^^GEISINGER^MR||Wisniewski^Bogdan^Stanislaw^^Mr.^||19570611|M||2106-3^White^CDCREC|756 Mill St^^Danville^PA^17821^US^H||^PRN^PH^^1^570^5558294|||M^Married^HL70002|||678-90-1235|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|NEURO^2408^01^GEISINGER_MC^^^^N|E^Emergency^HL70007|||6802457913^Buckley^Nora^A^^^MD^^^^NPI||NEU^Neurology^HL70069||||||||||VN20260507016^^^GEISINGER^VN|||||||||||||||||||||||||||20260507183000
ORC|RE|ORD90016^MEDSTATION|RX70016^PHARMACY||CM^Complete^HL70038|||20260508225900|||6802457913^Buckley^Nora^A^^^MD^^^^NPI
RXA|0|1|20260508230100|20260508230130|00409-1273-32^lorazepam 2mg/mL injection^NDC|1|MG^milligram^ISO+|IVP^IV Push^HL70162||NURSE_EHOLMES^Holmes^Eric^T^^^RN||||||||||20260508230130
RXR|IVP^IV Push^HL70162|HAND^Hand^HL70163
NTE|1||Witness: NURSE_ASINGH (Singh, Amrita S, RN). Controlled substance - Schedule IV. Administered over 2 minutes per protocol. Waste: 1mg/0.5mL witnessed and documented.
```

---

## 17. RDE^O11 - Pharmacy order for pantoprazole IV drip via Pyxis

```
MSH|^~\&|PYXIS|UPMC_PRESBY^2.16.840.1.113883.3.1902^ISO|PHARMACY|UPMC_HIS|20260509021500||RDE^O11^RDE_O11|PYX20260509021500017|P|2.5.1|||AL|NE
PID|1||MRN80167890^^^UPMC^MR||Le^Thao^Ngoc^^Ms.^||19850929|F||2028-9^Asian^CDCREC|3612 Penn Ave^^Pittsburgh^PA^15201^US^H||^PRN^PH^^1^412^5556483|||M^Married^HL70002|||789-01-2346|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|GI^5206^01^UPMC_PRESBY^^^^N|E^Emergency^HL70007|||7913568024^Fitzpatrick^Colin^J^^^MD^^^^NPI||GAS^Gastroenterology^HL70069||||||||||VN20260508017^^^UPMC^VN|||||||||||||||||||||||||||20260508191500
ORC|NW|ORD90017^PYXIS||GRP90017^PYXIS|||||20260509021000|||7913568024^Fitzpatrick^Colin^J^^^MD^^^^NPI|||||UPMC_PRESBY^UPMC Presbyterian
RXE|1^CONTINUOUS^HL70335|00409-3373-13^pantoprazole sodium 80mg/100mL IV^NDC|8|8|MG^milligram^ISO+|HR^hour^ISO+||||80||MG^milligram^ISO+
RXR|IV^Intravenous^HL70162
NTE|1||GI bleed protocol: pantoprazole 80mg IV bolus then 8mg/hr continuous infusion x 72 hours. Monitor for rebleeding.
```

---

## 18. RDS^O13 - Dispense with OBX encapsulated medication administration record (ED datatype)

```
MSH|^~\&|BD_PYXIS|LVHN_CC^2.16.840.1.113883.3.6601^ISO|PHARMACY|LVHN_HIS|20260509103022||RDS^O13^RDS_O13|PYX20260509103022018|P|2.5.1|||AL|NE
PID|1||MRN80178901^^^LVHN^MR||Gruber^Walter^Raymond^^Mr.^||19460114|M||2106-3^White^CDCREC|519 Wyandotte St^^Bethlehem^PA^18015^US^H||^PRN^PH^^1^610^5552093|||W^Widowed^HL70002|||890-12-3457|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|TELE^4402^01^LVHN_CC^^^^N|U^Urgent^HL70007|||8024679135^Kessler^Philip^M^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260508018^^^LVHN^VN|||||||||||||||||||||||||||20260508071500
ORC|RE|ORD90018^BD_PYXIS|RX70018^PHARMACY||CM^Complete^HL70038|||20260509102800|||8024679135^Kessler^Philip^M^^^MD^^^^NPI
RXD|1|00093-7180-01^warfarin sodium 5mg tab^NDC|20260509103000|1||TAB^tablet^HL70292|||||||00093-7180-01||NURSE_KMORENO^Moreno^Karla^E^^^RN
RXR|PO^Oral^HL70162
OBX|1|ED|PDF^Pyxis Medication Administration Record^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA5OAo+PgpzdHJlYW0KQlQKL0YxIDEwIFRmCjUwIDcyMCBUZAooTWVkaWNhdGlvbiBBZG1pbmlzdHJhdGlvbiBSZWNvcmQpIFRqCjAgLTIwIFRkCihQYXRpZW50OiBCZWNrZXIsIEhhcm9sZCBFLikgVGoKMCAtMjAgVGQKKFdhcmZhcmluIDVtZyBQTyBEYWlseSAtIElOUiAyLjMpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAo=||||||F|||20260509103000
OBX|2|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||2.3|{INR}^INR^UCUM|2.0-3.0|N|||F|||20260509080000
```

---

## 19. RDS^O13 - Dispense with OBX encapsulated Pyxis transaction log (ED datatype)

```
MSH|^~\&|PYXIS|PENN_HUP^2.16.840.1.113883.3.3401^ISO|PHARMACY|PENNMED_HIS|20260509160030||RDS^O13^RDS_O13|PYX20260509160030019|P|2.5.1|||AL|NE
PID|1||MRN80189012^^^PENNMED^MR||Gallagher^Bridget^Fiona^^Mrs.^||19720508|F||2106-3^White^CDCREC|801 Spruce St^^Philadelphia^PA^19107^US^H||^PRN^PH^^1^215^5559461|||M^Married^HL70002|||901-23-4568|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SICU^7032^01^PENN_HUP^^^^N|E^Emergency^HL70007|||9135780246^Okonkwo^Chidi^T^^^MD^^^^NPI||TRA^Trauma Surgery^HL70069||||||||||VN20260507019^^^PENNMED^VN|||||||||||||||||||||||||||20260507043000
ORC|RE|ORD90019^PYXIS|RX70019^PHARMACY||CM^Complete^HL70038|||20260509155800|||9135780246^Okonkwo^Chidi^T^^^MD^^^^NPI
RXD|1|00409-4888-11^propofol 10mg/mL 100mL vial^NDC|20260509160000|1||VIAL^vial^HL70292|||||200|MG^milligram^ISO+|||NURSE_HPARK^Park^Helen^Y^^^RN
RXR|IV^Intravenous^HL70162
OBX|1|ED|LOG^Pyxis Transaction Audit Log^L||^text^plain^Base64^VHJhbnNhY3Rpb24gTG9nIC0gQkQgUHl4aXMgTWVkU3RhdGlvbiBFUwpTdGF0aW9uOiBTSUNVLUNBQi0wMSAoUGVubiBIVVApCkRhdGU6IDIwMjYtMDUtMDkgMTY6MDA6MzAKVXNlcjogTGVlLCBDaHJpc3RpbmUgWSAoUk4pCkFjdGlvbjogRElTUEVOU0UKTWF0ZXJpYWw6IHByb3BvZm9sIDEwbWcvbUwgMTAwbUwgdmlhbApOREM6IDAwNDA5LTQ4ODgtMTEKUXR5OiAxIHZpYWwKV2l0bmVzczogTi9BIChub24tY29udHJvbGxlZCkKT3ZlcnJpZGU6IE5vbmUKQmlvbWV0cmljOiBGaW5nZXJwcmludCB2ZXJpZmllZA==||||||F|||20260509160000
OBX|2|NM|3141-9^Body weight Measured^LN||68.2|kg^kilogram^UCUM|||||F|||20260509040000
NTE|1||Sedation protocol: propofol 5-50 mcg/kg/min titrated to RASS -2. Currently on 20 mcg/kg/min.
```

---

## 20. ADT^A01 - Neonatal admission with Pyxis medication profile initialization

```
MSH|^~\&|BD_PYXIS|UPMC_MAGEE^2.16.840.1.113883.3.1905^ISO|ADT_RECV|UPMC_HIS|20260509040015||ADT^A01^ADT_A01|PYX20260509040015020|P|2.5.1|||AL|NE
EVN|A01|20260509035500|||NICU_ADMIT^NICU^Admitting^^^||20260509035500
PID|1||MRN80190123^^^UPMC^MR||BabyGirl^Delgado^^^^||20260509|F||2106-3^White^CDCREC|2711 Murray Ave^^Pittsburgh^PA^15217^US^H||^PRN^PH^^1^412^5553648|||S^Single^HL70002||||||H^Hispanic or Latino^CDCREC
PD1|||UPMC Magee-Womens Hospital^^^^NPI|0246891357^Pennington^Claudia^M^^^MD^^^^NPI
NK1|1|Delgado^Valentina^Paola^^Mrs.|MTH^Mother^HL70063|2711 Murray Ave^^Pittsburgh^PA^15217^US|^PRN^PH^^1^412^5553648||EC^Emergency Contact^HL70131
NK1|2|Delgado^Andres^Rafael^^Mr.|FTH^Father^HL70063|2711 Murray Ave^^Pittsburgh^PA^15217^US|^PRN^PH^^1^412^5553649||EC^Emergency Contact^HL70131
PV1|1|I|NICU^8004^01^UPMC_MAGEE^^^^N|NB^Newborn^HL70007|||0246891357^Pennington^Claudia^M^^^MD^^^^NPI|1358024679^Kwon^Joon^V^^^MD^^^^NPI|NEO^Neonatology^HL70069||||||B^Baby born in facility^HL70007|||||VN20260509020^^^UPMC^VN|||||||||||||||||||||||||||20260509035500
PV2|||^Premature infant 34 weeks gestation - respiratory distress||||||20260509|14
DG1|1||P07.38^Other preterm infants 34 completed weeks^I10||20260509|A
DG1|2||P22.0^Respiratory distress syndrome of newborn^I10||20260509|A
GT1|1||Delgado^Valentina^Paola^^Mrs.||2711 Murray Ave^^Pittsburgh^PA^15217^US|^PRN^PH^^1^412^5553648|||||MTH^Mother^HL70063
IN1|1|UPMC001|93221^UPMC Health Plan|UPMCHP^^Pittsburgh^PA^15219|||||GRP654321||||||Delgado^Valentina^Paola|19^Child^HL70063|20260509|2711 Murray Ave^^Pittsburgh^PA^15217^US|Y||1||||||||||||||POL998877
```
