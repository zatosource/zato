# ConnectingOntario / ClinicalConnect - real HL7v2 ER7 messages

---

## 1. ADT^A01 - inpatient admission to Ontario hospital

```
MSH|^~\&|OLIS|ONTARIO_HIS|CONNECTING_ON|EHEALTHONTARIO|20260301080000||ADT^A01^ADT_A01|OLIS00001|P|2.5
EVN|A01|20260301080000
PID|||4521789063^^^ON_HCN^JHN||Pelletier^Veronique^Anne^^Mme||19810722|F|||128 Sussex Dr^^Ottawa^ON^K1N 1J5^CA||^^PH^6135552847~^^CP^6135558391||F|CAT||||||||||||||||||||
PV1||I|6WEST^612^A^Ottawa General||||34521^Iyer^Suresh^^^Dr.^^CPSO|78234^Tremblay^Genevieve^^^Dr.^^CPSO|||MED||||||||VN20260301001|||||||||||||||||||||||||||20260301080000
IN1|1||OHIP|Ontario Health Insurance Plan|49 Place d'Armes^^Kingston^ON^K7L 5J2^CA||||||||||||||||||||||||||||||||||||||||4521789063
```

## 2. ADT^A04 - outpatient registration at Ontario clinic

```
MSH|^~\&|OLIS|LHSC|CONNECTING_ON|EHEALTHONTARIO|20260302093000||ADT^A04^ADT_A01|OLIS00002|P|2.5
EVN|A04|20260302093000
PID|||7034825619^^^ON_HCN^JHN||Cloutier^Benjamin^Francois^^Mr||19690511|M|||284 King St E^^Hamilton^ON^L8N 1B6^CA||^^PH^9055552314~^^CP^9055557762||M|PRO||||||||||||||||||||
PV1||O|CLINIC^RM3^1^Victoria Hospital||||45612^Kaur^Manpreet^^^Dr.^^CPSO|||GEN||||||||VN20260302001|||||||||||||||||||||||||||20260302093000
```

## 3. ADT^A08 - patient information update

```
MSH|^~\&|CHRIS|MOHLTC|CONNECTING_ON|EHEALTHONTARIO|20260303140000||ADT^A08^ADT_A01|CHRIS00001|P|2.5
EVN|A08|20260303140000
PID|||8923471056^^^ON_HCN^JHN||Wong^Stephanie^Yi-Chen^^Ms||19920418|F|||162 Bay St^^Toronto^ON^M5J 2T3^CA||^^PH^4165553967~^^CP^4165558821~^^Internet^stephanie.wong@webmail.ca||F|CAT||||||||||||||||||||
PV1||I|7NORTH^712^B^Toronto General||||56712^Adeyemi^Tunde^^^Dr.^^CPSO|78934^Lebrun^Jean-Marc^^^Dr.^^CPSO|||CARD||||||||VN20260303001|||||||||||||||||||||||||||20260303140000
```

## 4. ADT^A31 - update person information in provincial registry

```
MSH|^~\&|OCULYS|LHIN_CENTRAL|CONNECTING_ON|EHEALTHONTARIO|20260304110000||ADT^A31^ADT_A05|OCUL00001|P|2.5
EVN|A31|20260304110000
PID|||1287094563^^^ON_HCN^JHN||Nguyen^Bao^Tran^^Ms||19880229|F|||517 Dundas St^^London^ON^N6B 1W4^CA||^^PH^5195554683~^^CP^5195557291||F|BUD||||||||||||||||||||
PV1||O|EMERG^RM1^1^London Health Sciences||||90234^Krishnan^Deepa^^^Dr.^^CPSO|||EMER||||||||VN20260304001|||||||||||||||||||||||||||20260304110000
```

## 5. ADT^A40 - patient merge in provincial index

```
MSH|^~\&|OLIS|ONTARIO_HIS|CONNECTING_ON|EHEALTHONTARIO|20260305160000||ADT^A40^ADT_A39|OLIS00003|P|2.5
EVN|A40|20260305160000
PID|||3678125409^^^ON_HCN^JHN||Bergeron^Sebastien^Olivier^^Mr||19741203|M|||91 Sparks St^^Ottawa^ON^K1P 5B5^CA||^^PH^6135554729~^^CP^6135557815||M|CAT||||||||||||||||||||
MRG|7821456390^^^ON_HCN^JHN||||||
PV1||I|5WEST^503^A^The Ottawa Hospital||||23145^Choi^Min-Jun^^^Dr.^^CPSO|||SURG||||||||VN20260305001|||||||||||||||||||||||||||20260305160000
```

## 6. QBP^Q22 - patient demographics query by health card number

```
MSH|^~\&|CONNECTING_ON|EHEALTHONTARIO|OLIS|ONTARIO_HIS|20260306090000||QBP^Q22^QBP_Q21|CONN00001|P|2.5
QPD|Q22^FindCandidates^HL7nnnn|Q0001|@PID.3.1^9145206378~@PID.3.4^ON_HCN~@PID.3.5^JHN
RCP|I|10^RD
```

## 7. RSP^K22 - demographics query response with matching patient

```
MSH|^~\&|OLIS|ONTARIO_HIS|CONNECTING_ON|EHEALTHONTARIO|20260306090001||RSP^K22^RSP_K21|OLIS00004|P|2.5
MSA|AA|CONN00001
QAK|Q0001|OK|Q22^FindCandidates^HL7nnnn|1
QPD|Q22^FindCandidates^HL7nnnn|Q0001|@PID.3.1^9145206378~@PID.3.4^ON_HCN~@PID.3.5^JHN
PID|||9145206378^^^ON_HCN^JHN||Fortin^Maxime^Etienne^^Mr||19830209|M|||45 Elgin St^^Ottawa^ON^K1P 5K8^CA||^^PH^6135556124~^^CP^6135559337||M|CAT||||||||||||||||||||
```

## 8. QBP^Q23 - get corresponding identifiers (PIX query)

```
MSH|^~\&|CONNECTING_ON|EHEALTHONTARIO|OLIS|ONTARIO_HIS|20260307100000||QBP^Q23^QBP_Q21|CONN00002|P|2.5
QPD|IHE PIX Query|Q0002|9145206378^^^ON_HCN^JHN|^^^OLIS_MRN~^^^CHRIS_ID
RCP|I
```

## 9. RSP^K23 - PIX query response with cross-referenced identifiers

```
MSH|^~\&|OLIS|ONTARIO_HIS|CONNECTING_ON|EHEALTHONTARIO|20260307100001||RSP^K23^RSP_K23|OLIS00005|P|2.5
MSA|AA|CONN00002
QAK|Q0002|OK|IHE PIX Query
QPD|IHE PIX Query|Q0002|9145206378^^^ON_HCN^JHN|^^^OLIS_MRN~^^^CHRIS_ID
PID|||MRN673829^^^OLIS_MRN^MR~CHR184562^^^CHRIS_ID^PI~9145206378^^^ON_HCN^JHN||Fortin^Maxime^Etienne^^Mr||19830209|M
```

## 10. ADT^A01 - emergency admission with full demographics

```
MSH|^~\&|OCULYS|SUNNYBROOK|CONNECTING_ON|EHEALTHONTARIO|20260308034500||ADT^A01^ADT_A01|OCUL00002|P|2.5
EVN|A01|20260308034500
PID|||5286913074^^^ON_HCN^JHN||Patel^Anjali^Rohini^^Ms||19960615|F|||487 Bloor St W^^Toronto^ON^M5S 1Y1^CA||^^PH^4165557823~^^CP^4165552169||F|CAT||||||||||||||||||||
NK1|1|Patel^Vikram^^Mr|FTH|487 Bloor St W^^Toronto^ON^M5S 1Y1^CA|^^PH^4165557824
PV1||E|EMERG^BAY7^1^Sunnybrook HSC||||34678^Boucher^Mathieu^^^Dr.^^CPSO|||EMER||||||||VN20260308001|||||||||||||||||||||||||||20260308034500
IN1|1||OHIP|Ontario Health Insurance Plan|49 Place d'Armes^^Kingston^ON^K7L 5J2^CA||||||||||||||||||||||||||||||||||||||||5286913074
```

## 11. ADT^A01 - admission with workplace safety insurance

```
MSH|^~\&|OLIS|HAMILTON_GEN|CONNECTING_ON|EHEALTHONTARIO|20260309071500||ADT^A01^ADT_A01|OLIS00006|P|2.5
EVN|A01|20260309071500
PID|||6491738025^^^ON_HCN^JHN||Caron^Olivier^Daniel^^Mr||19840928|M|||275 Main St E^^Hamilton^ON^L8N 1H6^CA||^^PH^9055554912~^^CP^9055557368||M|CAT||||||||||||||||||||
PV1||I|ORTHO^301^A^Hamilton General||||78145^Beaulieu^Stephanie^^^Dr.^^CPSO|||ORTH||||||||VN20260309001|||||||||||||||||||||||||||20260309071500
IN1|1||WSIB|Workplace Safety and Insurance Board|200 Front St W^^Toronto^ON^M5V 3J1^CA||||||||||||||||||||||||||||||||||||||||||
IN1|2||OHIP|Ontario Health Insurance Plan|49 Place d'Armes^^Kingston^ON^K7L 5J2^CA||||||||||||||||||||||||||||||||||||||||6491738025
```

## 12. ORU^R01 - OLIS laboratory result with CBC panel

```
MSH|^~\&|OLIS|GAMMA_DYNACARE|CONNECTING_ON|EHEALTHONTARIO|20260310143000||ORU^R01^ORU_R01|OLIS00007|P|2.5
PID|||2917346058^^^ON_HCN^JHN||Lavoie^Stephanie^Marie^^Mme||19710314|F|||156 Bank St^^Ottawa^ON^K1P 6E5^CA||^^PH^6135558143
OBR|1|ORD20260310001^OLIS|SPE20260310001^GAMMA_DYNACARE|CBC^Complete Blood Count^OLIS_CODE|||20260310081500|||||||||2917346058^Lavoie^Stephanie M^^^^||||||20260310143000||LAB|F
OBX|1|NM|6690-2^WBC^LN||8.2|x10*9/L|4.0-11.0|N|||F
OBX|2|NM|789-8^RBC^LN||4.65|x10*12/L|3.80-5.80|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||138|g/L|120-160|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||0.41|L/L|0.36-0.46|N|||F
OBX|5|NM|777-3^Platelets^LN||256|x10*9/L|150-400|N|||F
```

## 13. ORU^R01 - chemistry panel with abnormal results

```
MSH|^~\&|OLIS|LIFELABS|CONNECTING_ON|EHEALTHONTARIO|20260311101500||ORU^R01^ORU_R01|OLIS00008|P|2.5
PID|||4738261905^^^ON_HCN^JHN||Simard^Robert^Marcel^^Mr||19520809|M|||342 Laurier Ave W^^Ottawa^ON^K1P 1K6^CA||^^PH^6135559267
OBR|1|ORD20260311001^OLIS|SPE20260311001^LIFELABS|BMP^Basic Metabolic Panel^OLIS_CODE|||20260311074500|||||||||4738261905^Simard^Robert M^^^^||||||20260311101500||LAB|F
OBX|1|NM|2345-7^Glucose^LN||9.8|mmol/L|3.3-5.5|HH|||F
OBX|2|NM|2160-0^Creatinine^LN||145|umol/L|62-115|H|||F
OBX|3|NM|3094-0^Urea^LN||12.5|mmol/L|2.1-8.5|H|||F
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F
OBX|5|NM|2823-3^Potassium^LN||4.8|mmol/L|3.5-5.1|N|||F
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L|98-106|N|||F
```

## 14. ORU^R01 - pathology report with embedded PDF

```
MSH|^~\&|OLIS|MOUNT_SINAI_PATH|CONNECTING_ON|EHEALTHONTARIO|20260312153000||ORU^R01^ORU_R01|OLIS00009|P|2.5
PID|||8159427063^^^ON_HCN^JHN||Paquette^Sylvie^Anne^^Mme||19770502|F|||219 College St^^Toronto^ON^M5T 1R3^CA||^^PH^4165554328
OBR|1|ORD20260312001^OLIS|SPE20260312001^MSH_PATH|PATH^Surgical Pathology^OLIS_CODE|||20260312090000|||||||||8159427063^Paquette^Sylvie A^^^^||||||20260312153000||PATH|F
OBX|1|FT|22637-3^Pathology Report^LN||Right breast excisional biopsy: Invasive ductal carcinoma, Grade 2, 1.8 cm. Margins clear. ER positive, PR positive, HER2 negative.||||||F
OBX|2|ED|PDF^Pathology Report PDF^LN||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq||||||F
```

## 15. ORU^R01 - radiology report with embedded JPEG image

```
MSH|^~\&|OLIS|KINGSTON_RAD|CONNECTING_ON|EHEALTHONTARIO|20260313091000||ORU^R01^ORU_R01|OLIS00010|P|2.5
PID|||7264193058^^^ON_HCN^JHN||Ouellet^Antoine^Joseph^^Mr||19580427|M|||316 Princess St^^Kingston^ON^K7L 1B7^CA||^^PH^6135554912
OBR|1|ORD20260313001^OLIS|SPE20260313001^KGH_RAD|XCHEST^Chest Xray^OLIS_CODE|||20260313083000|||||||||7264193058^Ouellet^Antoine J^^^^||||||20260313091000||RAD|F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||PA and lateral views of the chest. Heart size is normal. Lungs are clear. No pleural effusion or pneumothorax identified. Costophrenic angles are sharp bilaterally.||||||F
OBX|2|ED|IMG^Chest Xray Image^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL||||||F
```

## 16. ADT^A01 - admission from northern Ontario facility

```
MSH|^~\&|CHRIS|HSN_SUDBURY|CONNECTING_ON|EHEALTHONTARIO|20260314062000||ADT^A01^ADT_A01|CHRIS00002|P|2.5
EVN|A01|20260314062000
PID|||3815647092^^^ON_HCN^JHN||Gagne^Mathieu^Gilles^^Mr||19610819|M|||87 Elm St W^^Sudbury^ON^P3C 1S5^CA||^^PH^7055552981~^^CP^7055557413||M|CAT||||||||||||||||||||
PV1||I|ICU^101^A^Health Sciences North||||56218^Lapointe^Christine^^^Dr.^^CPSO|||IMED||||||||VN20260314001|||||||||||||||||||||||||||20260314062000
IN1|1||OHIP|Ontario Health Insurance Plan|49 Place d'Armes^^Kingston^ON^K7L 5J2^CA||||||||||||||||||||||||||||||||||||||||3815647092
```

## 17. ADT^A04 - registration at Ottawa children's hospital

```
MSH|^~\&|OLIS|CHEO|CONNECTING_ON|EHEALTHONTARIO|20260315100000||ADT^A04^ADT_A01|OLIS00011|P|2.5
EVN|A04|20260315100000
PID|||5147209638^^^ON_HCN^JHN||Leclerc^Charlotte^Eve^^Ms||20190724|F|||168 Metcalfe St^^Ottawa^ON^K2P 1M9^CA||^^PH^6135559263
NK1|1|Leclerc^Sebastien^^Mr|FTH|168 Metcalfe St^^Ottawa^ON^K2P 1M9^CA|^^PH^6135559264~^^CP^6135552176
NK1|2|Leclerc^Marie-Eve^^Mme|MTH|168 Metcalfe St^^Ottawa^ON^K2P 1M9^CA|^^PH^6135559265~^^CP^6135552177
PV1||O|PEDS^RM5^1^CHEO||||72845^Sharma^Neha^^^Dr.^^CPSO|||PEDS||||||||VN20260315001|||||||||||||||||||||||||||20260315100000
```

## 18. ORU^R01 - microbiology culture result

```
MSH|^~\&|OLIS|ALPHA_LABS|CONNECTING_ON|EHEALTHONTARIO|20260316164500||ORU^R01^ORU_R01|OLIS00012|P|2.5
PID|||9028453617^^^ON_HCN^JHN||Girard^Andre^Pierre^^Mr||19481117|M|||74 Wellington St^^Ottawa^ON^K1A 0B5^CA||^^PH^6135558149
OBR|1|ORD20260316001^OLIS|SPE20260316001^ALPHA_LABS|UCUL^Urine Culture^OLIS_CODE|||20260316081000|||||||||9028453617^Girard^Andre P^^^^||||||20260316164500||MB|F
OBX|1|ST|630-4^Bacteria identified^LN||Escherichia coli||||||F
OBX|2|ST|18900-1^Colony count^LN||>100,000 CFU/mL||||||F
OBX|3|ST|18864-9^Ampicillin^LN||Resistant||||||F
OBX|4|ST|18865-6^Ciprofloxacin^LN||Susceptible||||||F
OBX|5|ST|18866-4^Nitrofurantoin^LN||Susceptible||||||F
OBX|6|ST|18867-2^Trimethoprim-Sulfamethoxazole^LN||Resistant||||||F
```

## 19. ORU^R01 - OLIS lab result with embedded scanned requisition

```
MSH|^~\&|OLIS|DYNACARE|CONNECTING_ON|EHEALTHONTARIO|20260317112000||ORU^R01^ORU_R01|OLIS00013|P|2.5
PID|||4892573160^^^ON_HCN^JHN||Chen^Lillian^Mei-Hua^^Ms||19900318|F|||387 Bay St^^Toronto^ON^M5J 2N4^CA||^^PH^4165553819
OBR|1|ORD20260317001^OLIS|SPE20260317001^DYNACARE|TSH^Thyroid Stimulating Hormone^OLIS_CODE|||20260317080000|||||||||4892573160^Chen^Lillian M^^^^||||||20260317112000||LAB|F
OBX|1|NM|3016-3^TSH^LN||2.45|mIU/L|0.35-5.50|N|||F
OBX|2|NM|3026-2^Free T4^LN||14.2|pmol/L|10.0-25.0|N|||F
OBX|3|ED|REQ^Scanned Requisition^LN||^AP^^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIKPj4KZW5kb2Jq||||||F
```

## 20. ADT^A08 - update with multiple provincial identifiers

```
MSH|^~\&|CONNECTING_ON|EHEALTHONTARIO|OLIS|ONTARIO_HIS|20260318150000||ADT^A08^ADT_A01|CONN00003|P|2.5
EVN|A08|20260318150000
PID|||6273918045^^^ON_HCN^JHN~MRN912348^^^LHSC_MRN^MR~CHR384917^^^CHRIS_ID^PI||Singh^Harjinder^Pal^^Mr||19751024|M|||432 University Ave^^Toronto^ON^M5G 1W3^CA||^^PH^4165556824~^^CP^4165553918~^^Internet^harjinder.singh@webmail.ca||M|CAT||||||||||||||||||||
PV1||I|6SOUTH^610^A^UHN - Toronto General||||34528^Iyer^Kavita^^^Dr.^^CPSO|56739^Roy^Stephanie^^^Dr.^^CPSO|||NEPH||||||||VN20260318001|||||||||||||||||||||||||||20260318150000
```
