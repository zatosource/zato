# Dutch healthcare EDIFACT - MEDVRI and MEDLAB interchanges

---

## 1. MEDVRI - vrij bericht, volledige interchange met TXT-herhalingen

```
UNB+UNOA:1+41007001+41008002+230405:0912+SNM7431'
UNH+7431+MEDVRI:1'
GGA+Praktijk Rozenburg+Administratie+Praktijk Rozenburg+Kerkstraat:14::Utrecht:3511AB+?+31611223344'
DET+24:02:14+09:41'
PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'
PAD+Lindelaan:27a::Utrecht:3581CD+?+31644556677'
TXT:1+Beste collega'
TXT:2+Graag uw beoordeling van deze patient'
TXT:3+'
TXT:3+Met vriendelijke groet'
GGO+Arts Achternaam+++Dorpsweg:8::Utrecht:'
UNT+11+7431'
UNZ+1+7431'
```

---

## 2. MEDVRI - vrij bericht met release-teken ?' in patientnaam

```
UNB+UNOA:1+41007001+41008002+230405:0912+SNM7431'
UNH+7431+MEDVRI:1'
GGA+Praktijk Rozenburg+Administratie+Praktijk Rozenburg+Kerkstraat:14::Utrecht:3511AB+?+31611223344'
DET+24:02:12+11:05'
PID+1988:06:21+V+Wolf:van ?'t:Bruin:de::JH++BSN999990019'
PAD+Lindelaan:27a::Utrecht:3581CD+?+31644556677'
TXT:1+Beste collega'
TXT:2+hierbij de afgesproken terugkoppeling'
TXT:3'
TXT:4+met vriendelijke groet'
GGO+Arts Naam+++Molenpad:5C::Utrecht:3512EF+0301234567'
UNT+11+7431'
UNZ+1+SNM7431'
```

---

## 3. MEDVRI - vrij bericht met twee tekstregels, ontvanger zonder postcode

```
UNB+UNOA:1+41007001+41008002+230405:0912+7431'
UNH+7431+MEDVRI:1'
GGA+Praktijk Rozenburg+Administratie+Praktijk Rozenburg+Kerkstraat:14::Utrecht:3511AB+?+31611223344'
DET+24:02:14+09:41'
PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'
PAD+Lindelaan:27a::Utrecht:3581CD+?+31644556677'
TXT:1+Beste collega'
TXT:2+Graag uw beoordeling van deze patient'
GGO+Arts Achternaam+++Dorpsweg:8::Utrecht:'
UNT+9+7431'
UNZ+1+7431'
```

---

## 4. MEDLAB - laboratoriumuitslag met BEP-, OPB- en herhalende groepen

```
UNB+UNOA:1+41007001+41008002+230405:0912+7431'
UNH+7431+MEDLAB:1'
ZKH+ZIEKENHUIS OOST+Hoofdweg:22::Zwolle:8011AB+038-1112233'
PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'
PAD+Lindelaan:27a::Utrecht:3581CD+?+31644556677'
ART+S+654321+Huisartsenpraktijk Noord+Statenlaan:90::?Zwolle:8016GH'
AFD+LAB KLINISCHE CHEMIE+038-4445566'
ARA:1+Dr. Visser+038-5556677'
DET:1+24:02:09+09:20'
IDE:1+J+445566+'
BEP:1:1:1+1+MEDICIJNEN'
BEP:1:1:2+0+Carbamazepine+7.4++mg/l++4+10+CARBB SI'
OPB:1:1:2:1+*'
OPB:1:1:2:2+-----OPM-----'
OPB:1:1:2:3+Epilepsie 4-10 mg/l, neuralgie 5-10 mg/l, gecombineerde therapie'
OPB:1:1:2:4+4-8 mg/l, vrije concentratie 1-3 mg/l, Toxisch > 12 mg/l'
OPB:1:1:2:5+controle na dosisaanpassing'
BEP:1:1:3+1+DIVERSEN'
BEP:1:1:4+0+Datum inname+240208++++++DINN10'
BEP:1:1:5+0+Tijd inname+22.15++uur++++TINN10'
BEP:1:1:6+0+Afname tijd+09.20++uur++++TAFN10'
BEP:1:1:7+0+Clozapine+Zie onder++ug/l++++CLOZB'
OPB:1:1:7:1+*'
OPB:1:1:7:2+niet betrouwbaar te bepalen'
UNT+24+55002187364'
UNZ+1+7431'
```
