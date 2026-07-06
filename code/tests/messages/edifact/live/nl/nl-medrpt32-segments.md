# MEDRPT 3.2 (MRPN32-LRP) - segment vectors

Per-segment examples of the Dutch laboratory report message MEDRPT:D:93A:UN:MRPN32,
plus the envelope lines that accompany it. Each example below is a single segment
as it appears on the wire.

---

## 1. UNB - interchange header

```
UNB+UNOA:1+019283746+019283746+
```

---

## 2. UNH - message header

```
UNH+31415926+MEDRPT:D:93A:UN:MRPN32'
```

---

## 3. BGM - begin of message

```
BGM+LRP:MF:ITN+8642097+9+NA'
```

---

## 4. DTM - date/time varianten

```
DTM+137:'
DTM+329:20011122:102'
DTM+SCO:'
DTM+ISO:'
```

---

## 5. NAD - naam en adres varianten

```
NAD+SLA+06172839:CLB:VEK++LB :NOORD:::09876543'
NAD+PO+09876543:CGP:VEK++Vermeer:H:van+Dorpsstraat+7:b+Dorp+5678CD'
NAD+CCR'
NAD+CCR+09876543:CGP:VEK++Vermeer:H:van+Dorpsstraat+7:b+Dorp+5678CD'
```

---

## 6. PNA - patient

```
PNA+PAT+::999990019:PCL:LZB+++NAN:Bakker+NVV:M*de++NEA:Smit+NEV:van'
```

---

## 7. ADR - adres

```
ADR++7:Dorpsstraat:7 b+Dorp+5678CD+NL'
```

---

## 8. COM - communicatie

```
COM+0698765432:TE'
COM+0623344556:TE'
COM+0611998877:TE'
```

---

## 9. CTA - contact

```
CTA+AFD+:Hematologie'
```

---

## 10. RFF - referenties

```
RFF+LZB:999990019'
RFF+SRI:654321'
RFF+ROI:654321'
```

---

## 11. STS - status

```
STS++G'
```

---

## 12. FCA - verzekering

```
FCA+PU+5678:ZZ:VEK:09876543'
```

---

## 13. PDI - geslacht

```
PDI+1'
PDI+2'
```

---

## 14. SPC - monster

```
SPC+TSP'
```

---

## 15. INV - bepaling

```
INV+1+GLUC:AMB:NHG:Glucose nuchter'
INV+1+KREA:AMB:NHG:Kreatinine'
```

---

## 16. RSL - uitslag varianten

```
RSL+NV+5+0.0 12.0+mmol/l'
RSL+NV+14+0.0 12.0+mmol/l+HI'
RSL+NV+3+4,5 12,0+mmol/l+LO'
```

---

## 17. RND - normaalwaarden

```
RND+RU+0.0+12.0'
RND+RU+4,5+12,0'
```

---

## 18. FTX - vrije tekst met regelsplitsing

```
FTX+UIT+++Dit commentaar is met opzet extra lang gemaakt zodat de inhoud over:meerdere regels verdeeld moet worden.'
```
