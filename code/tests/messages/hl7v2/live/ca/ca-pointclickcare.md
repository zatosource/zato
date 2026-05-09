# PointClickCare - real HL7v2 ER7 messages

---

## 1. ADT^A01 - admission to long-term care home

```
MSH|^~\&|PCC|SUNSET MANOR LTC|HIS_RCV|LHIN_CENTRAL|20260401100000||ADT^A01^ADT_A01|PCC00001|P|2.5.1
EVN|A01|20260401100000
PID|||1234567890^^^ON_HCN^JHN||Gauthier^Lucienne^Marie^^Mme||19350812|F|||SUNSET MANOR~250 Sunset Dr^^Niagara Falls^ON^L2G 1A4^CA||^^PH^9055551234||F|WID||||||||||||||||||||
NK1|1|Gauthier^Philippe^^Mr|SON|88 Queen St^^St. Catharines^ON^L2R 5G3^CA|^^PH^9055559876~^^CP^9055558765
PV1||I|2EAST^201^A^Sunset Manor LTC||||34567^Simard^Nicole^^^Dr.^^CPSO|||LTC||||||||VN20260401001|||||||||||||||||||||||||||20260401100000
IN1|1||OHIP|Ontario Health Insurance Plan|49 Place d'Armes^^Kingston^ON^K7L 5J2^CA||||||||||||||||||||||||||||||||||||||||1234567890
```

## 2. ADT^A01 - admission to continuing care in Alberta

```
MSH|^~\&|POINTCLICKCARE|SILVER CREEK LODGE|HIS_RCV|AHS_CONNECT|20260402083000||ADT^A01^ADT_A01|PCC00002|P|2.3
EVN|A01|20260402083000
PID|||2345678901^^^AB_PHN^JHN||Ferguson^William^James^^Mr||19410604|M|||SILVER CREEK LODGE~100 Silver Creek Rd^^Red Deer^AB^T4N 5E5^CA||^^PH^4035552345||M|WID||||||||||||||||||||
NK1|1|Ferguson^Sandra^^Ms|DAU|340 Gaetz Ave^^Red Deer^AB^T4N 3Y3^CA|^^PH^4035559876~^^CP^4035558765
PV1||I|MAPLE^102^A^Silver Creek Lodge||||45678^Gupta^Rajesh^^^Dr.^^CPSA|||LTC||||||||VN20260402001|||||||||||||||||||||||||||20260402083000
IN1|1||AHCIP|Alberta Health Care Insurance Plan|10025 Jasper Ave^^Edmonton^AB^T5J 1S6^CA||||||||||||||||||||||||||||||||||||||||2345678901
```

## 3. ADT^A02 - transfer within LTC facility

```
MSH|^~\&|PCC|MAPLE GROVE RESIDENCE|HIS_RCV|LHIN_SOUTH_WEST|20260403140000||ADT^A02^ADT_A02|PCC00003|P|2.5.1
EVN|A02|20260403140000
PID|||3456789012^^^ON_HCN^JHN||Boucher^Therese^Anne^^Mme||19280917|F|||MAPLE GROVE RESIDENCE~75 Maple Grove Rd^^London^ON^N6G 1E7^CA||^^PH^5195553456||F|WID||||||||||||||||||||
PV1||I|BIRCH^301^B^Maple Grove Residence||||56789^Chen^Li^^^Dr.^^CPSO|||LTC||||||||VN20260403001||||||||||||||||||OAK^203^A^Maple Grove Residence|||||20260403140000
```

## 4. ADT^A03 - discharge from LTC (death)

```
MSH|^~\&|PCC|LAKEVIEW TERRACE|HIS_RCV|LHIN_CENTRAL_EAST|20260404060000||ADT^A03^ADT_A03|PCC00004|P|2.5.1
EVN|A03|20260404060000
PID|||4567890123^^^ON_HCN^JHN||Levesque^Henri^Marcel^^Mr||19300215|M|||LAKEVIEW TERRACE~400 Lakeshore Rd E^^Oakville^ON^L6J 1J5^CA||^^PH^9055554567||M|MAR|CAT|||||||||||||||||||20260404053000|Y
PV1||I|PINE^105^A^Lakeview Terrace||||67890^Patel^Sanjay^^^Dr.^^CPSO|||LTC||||||||VN20260404001|||||||||||||||||||||||||||20260404060000
```

## 5. ADT^A06 - transfer from inpatient to outpatient (respite to home)

```
MSH|^~\&|POINTCLICKCARE|HERITAGE GREEN LTC|HIS_RCV|HNHB_LHIN|20260405100000||ADT^A06^ADT_A06|PCC00005|P|2.3
EVN|A06|20260405100000
PID|||5678901234^^^ON_HCN^JHN||Thibault^Yvette^Louise^^Mme||19380721|F|||55 Wilson St^^Hamilton^ON^L8R 1C4^CA||^^PH^9055555678||F|WID||||||||||||||||||||
PV1||O|||||78901^Morin^Claude^^^Dr.^^CPSO|||LTC||||||||VN20260405001|||||||||||||||||||||||||||20260405100000
PV2||||||||20260401100000|20260405100000|||Respite care completed
```

## 6. ADT^A07 - transfer from outpatient to inpatient (admission from respite)

```
MSH|^~\&|PCC|PARKWOOD SUITES|HIS_RCV|LHIN_SOUTH_WEST|20260406080000||ADT^A07^ADT_A07|PCC00006|P|2.5.1
EVN|A07|20260406080000
PID|||6789012345^^^ON_HCN^JHN||Lalonde^Gerald^Robert^^Mr||19360413|M|||PARKWOOD SUITES~180 Commissioners Rd W^^London^ON^N6J 1Y4^CA||^^PH^5195556789||M|MAR||||||||||||||||||||
NK1|1|Lalonde^Diane^^Mme|SPO|180 Commissioners Rd W^^London^ON^N6J 1Y4^CA|^^PH^5195556790~^^CP^5195558901
PV1||I|WILLOW^205^A^Parkwood Suites||||89012^Roy^Francois^^^Dr.^^CPSO|||LTC||||||||VN20260406001|||||||||||||||||||||||||||20260406080000
```

## 7. ADT^A08 - update patient demographics (new contact info)

```
MSH|^~\&|PCC|RIVERDALE PLACE LTC|HIS_RCV|LHIN_CENTRAL|20260407143000||ADT^A08^ADT_A01|PCC00007|P|2.5.1
EVN|A08|20260407143000
PID|||7890123456^^^ON_HCN^JHN||Santos^Maria^Elena^^Ms||19420509|F|||RIVERDALE PLACE~60 Broadview Ave^^Toronto^ON^M4M 2G4^CA||^^PH^4165557890||F|WID||||||||||||||||||||
NK1|1|Santos^Carlos^^Mr|SON|25 Danforth Ave^^Toronto^ON^M4K 1N2^CA|^^PH^4165559012~^^CP^4165558234
NK1|2|Santos^Elena^^Ms|DAU|110 Pape Ave^^Toronto^ON^M4M 2V8^CA|^^PH^4165559345~^^CP^4165557654
PV1||I|3SOUTH^315^A^Riverdale Place LTC||||90123^Lee^Jennifer^^^Dr.^^CPSO|||LTC||||||||VN20260407001|||||||||||||||||||||||||||20260407143000
```

## 8. ADT^A08 - update patient allergy information

```
MSH|^~\&|POINTCLICKCARE|CHARTWELL RESIDENCE|HIS_RCV|LHIN_MISSISSAUGA|20260408110000||ADT^A08^ADT_A01|PCC00008|P|2.3
EVN|A08|20260408110000
PID|||8901234567^^^ON_HCN^JHN||Pelletier^Germaine^Marguerite^^Mme||19310828|F|||CHARTWELL RESIDENCE~450 Dundas St E^^Mississauga^ON^L5A 4A1^CA||^^PH^9055558901||F|WID||||||||||||||||||||
AL1|1|DA|PCN^Penicillin^MED||Anaphylaxis
AL1|2|DA|SUL^Sulfa^MED||Rash
PV1||I|CEDAR^110^A^Chartwell Residence||||01234^Sharma^Vikram^^^Dr.^^CPSO|||LTC||||||||VN20260408001|||||||||||||||||||||||||||20260408110000
```

## 9. ADT^A03 - discharge to hospital (acute care transfer)

```
MSH|^~\&|PCC|VILLAGE OF WENTWORTH HEIGHTS|HIS_RCV|HAMILTON_HEALTH_SCI|20260409023000||ADT^A03^ADT_A03|PCC00009|P|2.5.1
EVN|A03|20260409023000
PID|||9012345678^^^ON_HCN^JHN||Crawford^Dorothy^Mae^^Ms||19320604|F|||VILLAGE OF WENTWORTH HEIGHTS~1020 Upper Gage Ave^^Hamilton^ON^L8V 4R3^CA||^^PH^9055559012||F|WID||||||||||||||||||||
PV1||I|ELM^208^A^Village of Wentworth Heights||||12345^Bhatt^Anand^^^Dr.^^CPSO|||LTC||||||||VN20260409001|||||||||||||||||||||||||||20260409023000
PV2|||||||||||||||||||||||Transfer to Hamilton General Hospital for chest pain evaluation
```

## 10. ORU^R01 - routine lab panel for LTC resident

```
MSH|^~\&|LIFELABS|LIFELABS_ON|PCC|SUNSET MANOR LTC|20260410091500||ORU^R01^ORU_R01|PCC00010|P|2.5.1
PID|||0123456789^^^ON_HCN^JHN||Fortin^Beatrice^Helene^^Mme||19360113|F|||SUNSET MANOR~250 Sunset Dr^^Niagara Falls^ON^L2G 1A4^CA||^^PH^9055550123
OBR|1|ORD20260410001^PCC|SPE20260410001^LIFELABS_ON|CBC^Complete Blood Count^LN|||20260410074500|||||||||0123456789^Fortin^Beatrice H^^^^||||||20260410091500||LAB|F
OBX|1|NM|6690-2^WBC^LN||5.9|x10*9/L|4.0-11.0|N|||F
OBX|2|NM|789-8^RBC^LN||3.95|x10*12/L|3.80-5.80|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||118|g/L|120-160|L|||F
OBX|4|NM|4544-3^Hematocrit^LN||0.35|L/L|0.36-0.46|L|||F
OBX|5|NM|777-3^Platelets^LN||178|x10*9/L|150-400|N|||F
```

## 11. ORU^R01 - INR monitoring for LTC resident on warfarin

```
MSH|^~\&|LIFELABS|LIFELABS_ON|PCC|MAPLE GROVE RESIDENCE|20260411101000||ORU^R01^ORU_R01|PCC00011|P|2.5.1
PID|||1122334455^^^ON_HCN^JHN||Desjardins^Roland^Albert^^Mr||19290320|M|||MAPLE GROVE RESIDENCE~75 Maple Grove Rd^^London^ON^N6G 1E7^CA||^^PH^5195551122
OBR|1|ORD20260411001^PCC|SPE20260411001^LIFELABS_ON|COAG^Coagulation^LN|||20260411080000|||||||||1122334455^Desjardins^Roland A^^^^||||||20260411101000||LAB|F
OBX|1|NM|5902-2^PT^LN||19.8|s|11.0-13.5|H|||F
OBX|2|NM|6301-6^INR^LN||3.2||2.0-3.0|H|||F
```

## 12. ORU^R01 - renal function with critical creatinine

```
MSH|^~\&|GAMMA_DYNACARE|DYNACARE_ON|PCC|LAKEVIEW TERRACE|20260412140000||ORU^R01^ORU_R01|PCC00012|P|2.5.1
PID|||2233445566^^^ON_HCN^JHN||Arsenault^Marguerite^Claire^^Mme||19340725|F|||LAKEVIEW TERRACE~400 Lakeshore Rd E^^Oakville^ON^L6J 1J5^CA||^^PH^9055552233
OBR|1|ORD20260412001^PCC|SPE20260412001^DYNACARE_ON|RENAL^Renal Function Panel^LN|||20260412081000|||||||||2233445566^Arsenault^Marguerite C^^^^||||||20260412140000||LAB|F
OBX|1|NM|2160-0^Creatinine^LN||210|umol/L|50-98|HH|||F
OBX|2|NM|48642-3^eGFR^LN||18|mL/min/1.73m2|>60|LL|||F
OBX|3|NM|3094-0^Urea^LN||22.5|mmol/L|2.1-8.5|HH|||F
OBX|4|NM|2823-3^Potassium^LN||5.4|mmol/L|3.5-5.1|H|||F
```

## 13. ADT^A01 - admission to BC continuing care

```
MSH|^~\&|PCC|SHAUGHNESSY CARE CENTRE|HIS_RCV|PHSA|20260413090000||ADT^A01^ADT_A01|PCC00013|P|2.5.1
EVN|A01|20260413090000
PID|||3344556677^^^BC_PHN^JHN||Wong^Florence^Mei^^Ms||19370918|F|||SHAUGHNESSY CARE CENTRE~4867 Marguerite St^^Vancouver^BC^V6J 4L5^CA||^^PH^6045553344||F|WID||||||||||||||||||||
NK1|1|Wong^David^^Mr|SON|230 Burrard St^^Vancouver^BC^V6C 3L6^CA|^^PH^6045559876~^^CP^6045558765
PV1||I|MAGNOLIA^102^A^Shaughnessy Care Centre||||23456^Leung^Andrew^^^Dr.^^CPSBC|||LTC||||||||VN20260413001|||||||||||||||||||||||||||20260413090000
IN1|1||MSP|BC Medical Services Plan|1515 Blanshard St^^Victoria^BC^V8W 3C8^CA||||||||||||||||||||||||||||||||||||||||3344556677
```

## 14. ORU^R01 - medication review report with embedded PDF

```
MSH|^~\&|PHARMACY|REXALL_LTC|PCC|SUNSET MANOR LTC|20260414153000||ORU^R01^ORU_R01|PCC00014|P|2.5.1
PID|||4455667788^^^ON_HCN^JHN||Tardif^Jeannine^Lise^^Mme||19310502|F|||SUNSET MANOR~250 Sunset Dr^^Niagara Falls^ON^L2G 1A4^CA||^^PH^9055554455
OBR|1|ORD20260414001^PHARMACY|DOC20260414001^REXALL_LTC|MEDREV^Medication Review^LN|||20260414130000|||||||||4455667788^Tardif^Jeannine L^^^^||||||20260414153000||PHARM|F
OBX|1|FT|29553-5^Medication Summary^LN||15 active medications reviewed. Identified 2 potential drug interactions: amlodipine/simvastatin dose concern, metformin/contrast dye precaution. Recommended vitamin D supplementation.||||||F
OBX|2|ED|PDF^Medication Review Report^LN||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq||||||F
```

## 15. ADT^A08 - update level of care designation

```
MSH|^~\&|PCC|HERITAGE GREEN LTC|HIS_RCV|HNHB_LHIN|20260415110000||ADT^A08^ADT_A01|PCC00015|P|2.5.1
EVN|A08|20260415110000
PID|||5566778899^^^ON_HCN^JHN||Gagnon^Lucien^Paul^^Mr||19330107|M|||HERITAGE GREEN~350 Isaac Brock Dr^^Stoney Creek^ON^L8J 2P8^CA||^^PH^9055555566||M|MAR||||||||||||||||||||
PV1||I|SPRUCE^404^A^Heritage Green LTC||||34567^Kim^Soo-Yeon^^^Dr.^^CPSO|||LTC||||||||VN20260415001|||||||||||||||||||||||||||20260415110000
PV2||||||||||||||||||||||||Level of care changed from C to D effective 2026-04-15
```

## 16. ORU^R01 - glucose and electrolytes for diabetic resident

```
MSH|^~\&|LIFELABS|LIFELABS_ON|PCC|RIVERDALE PLACE LTC|20260416093000||ORU^R01^ORU_R01|PCC00016|P|2.5.1
PID|||6677889900^^^ON_HCN^JHN||Cormier^Alphonse^Joseph^^Mr||19350419|M|||RIVERDALE PLACE~60 Broadview Ave^^Toronto^ON^M4M 2G4^CA||^^PH^4165556677
OBR|1|ORD20260416001^PCC|SPE20260416001^LIFELABS_ON|CHEM^Chemistry Panel^LN|||20260416074500|||||||||6677889900^Cormier^Alphonse J^^^^||||||20260416093000||LAB|F
OBX|1|NM|2345-7^Glucose Fasting^LN||12.5|mmol/L|3.3-5.5|HH|||F
OBX|2|NM|2951-2^Sodium^LN||137|mmol/L|136-145|N|||F
OBX|3|NM|2823-3^Potassium^LN||4.6|mmol/L|3.5-5.1|N|||F
OBX|4|NM|2160-0^Creatinine^LN||105|umol/L|62-115|N|||F
```

## 17. ADT^A01 - short-stay convalescent care admission

```
MSH|^~\&|POINTCLICKCARE|BAYCREST CENTRE|HIS_RCV|LHIN_TORONTO_CENTRAL|20260417073000||ADT^A01^ADT_A01|PCC00017|P|2.3
EVN|A01|20260417073000
PID|||7788990011^^^ON_HCN^JHN||Singh^Harjit^Kaur^^Ms||19440622|F|||BAYCREST CENTRE~3560 Bathurst St^^Toronto^ON^M6A 2E1^CA||^^PH^4165557788||F|WID||||||||||||||||||||
NK1|1|Singh^Ranjit^^Mr|SON|45 Finch Ave W^^Toronto^ON^M2N 2H4^CA|^^PH^4165559012~^^CP^4165558234
PV1||I|CONV^302^A^Baycrest Centre||||45678^Shapiro^David^^^Dr.^^CPSO|||LTC||||||||VN20260417001|||||||||||||||||||||||||||20260417073000
PV2||||||||20260417073000|20260515073000|||Convalescent care post hip replacement, 28-day stay
```

## 18. ORU^R01 - wound assessment with embedded photo PNG

```
MSH|^~\&|PCC|PARKWOOD SUITES|WOUND_SYS|WOUND_CARE|20260418140000||ORU^R01^ORU_R01|PCC00018|P|2.5.1
PID|||8899001122^^^ON_HCN^JHN||Belanger^Raymond^Edouard^^Mr||19290814|M|||PARKWOOD SUITES~180 Commissioners Rd W^^London^ON^N6J 1Y4^CA||^^PH^5195558899
OBR|1|ORD20260418001^PCC|WND20260418001^WOUND_CARE|WOUND^Wound Assessment^LN|||20260418100000|||||||||8899001122^Belanger^Raymond E^^^^||||||20260418140000||NURS|F
OBX|1|FT|72170-4^Wound Assessment^LN||Left sacral pressure injury, Stage 3. Dimensions 3.5 x 2.8 x 0.5 cm. Wound bed 80% granulation, 20% slough. Moderate serous drainage. Periwound intact.||||||F
OBX|2|ED|IMG^Wound Photograph^LN||^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==||||||F
```

## 19. ADT^A03 - discharge home with community supports

```
MSH|^~\&|PCC|CHARTWELL RESIDENCE|HIS_RCV|LHIN_MISSISSAUGA|20260419150000||ADT^A03^ADT_A03|PCC00019|P|2.5.1
EVN|A03|20260419150000
PID|||9900112233^^^ON_HCN^JHN||Dupuis^Annette^Bernadette^^Mme||19400305|F|||125 Lakeshore Rd W^^Mississauga^ON^L5H 1E9^CA||^^PH^9055559900||F|WID||||||||||||||||||||
PV1||I|CEDAR^110^A^Chartwell Residence||||01234^Sharma^Vikram^^^Dr.^^CPSO|||LTC||||||||VN20260419001|||||||||||||||||||||||||||20260419150000
PV2||||||||||||||||||||||||Discharged home with CCAC home care supports. Follow-up with family physician within 7 days.
```

## 20. ORU^R01 - chest xray for aspiration screening with embedded JPEG

```
MSH|^~\&|RAD_SYS|HAMILTON_RAD|PCC|VILLAGE OF WENTWORTH HEIGHTS|20260420163000||ORU^R01^ORU_R01|PCC00020|P|2.5.1
PID|||0011223344^^^ON_HCN^JHN||Boudreau^Edith^Marie^^Mme||19310920|F|||VILLAGE OF WENTWORTH HEIGHTS~1020 Upper Gage Ave^^Hamilton^ON^L8V 4R3^CA||^^PH^9055550011
OBR|1|ORD20260420001^PCC|RAD20260420001^HAMILTON_RAD|XCHEST^Portable Chest Xray^LN|||20260420140000|||||||||0011223344^Boudreau^Edith M^^^^||||||20260420163000||RAD|F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Portable AP chest. Patchy opacity in the right lower lobe consistent with aspiration pneumonitis. No pleural effusion. Heart size upper limits of normal. Chronic degenerative changes thoracic spine.||||||F
OBX|2|ED|IMG^Chest Xray Image^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL||||||F
```
