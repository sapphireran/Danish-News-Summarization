# Blåhøj Sogn

A closed inland parish between two real Jutland towns that are never
named in the briefs. Nothing here is scraped from Nordjylland-News or
the private 10k dump.

## Places

| Name | Role |
| --- | --- |
| Græsbjerg | Village and weather station |
| Havremarken | Cooperative fields |
| Sønderholt Skole | School |
| Blåhøj Kirke | Church |
| Kærholm Mejeri | Dairy and grain dryer |
| Rævedal Skov | Wood and turbine neighbour |
| Stenholt Hallen | Sports hall, 24 × 44 m |
| Pilebro | Bridge and chokepoint |
| Nørreled | Bus stop, line 82 |
| Mosebækken | Stream that floods and freezes |

## People

Inge Skovgaard, Morten Bæk, Hanne Friis, Ejvind Holm, Pia Kjeldsen,
Ole Nygaard.

## Sixteen briefs and the scar each one plants

| id | topic | planted |
| --- | --- | --- |
| bh-01 | June rain | `47,2 mm` → `47 mm` |
| bh-02 | Barley | `2,4 ha` → `24 ha`; `3.200 kr.` → `dollar` |
| bh-03 | First school day | `kl. 8.15` → `kl. 20.15` |
| bh-04 | Advent | advent → fasten |
| bh-05 | Cycle path | `4,8 km` → `48 km`; `1,2 mio.` → `12 mio.` |
| bh-06 | January frost | `−8,3 °C` loses the minus |
| bh-07 | Turbine | `2,1 MW` → `21 MW` |
| bh-08 | Library hours | `13.00–17.00` → `13.00–19.00` |
| bh-09 | Potatoes | `38 t/ha` → `38 kg/ha` |
| bh-10 | Bus | linje 82 → 28 |
| bh-11 | Well | `2,4 mg/l` → `24 mg/l` |
| bh-12 | Hall | `24 × 44 m` → `24 × 4,4 m` |
| bh-13 | Milk | `3,8%` → `38%` |
| bh-14 | Fire drill | `12 min.` → `21 min.` |
| bh-15 | Harvest market | `09.00–14.00` → `09.00–16.00` |
| bh-16 | Gusts | `14,7 m/s` → `147 m/s` |

## Split

The 2023 hand-in never committed the train/val/test cut. The lab uses
a boring 10/3/3 in article order: `bh-01…bh-10` train, `bh-11…bh-13`
validation, `bh-14…bh-16` test. That is a fixture, not a claim about
2023.

## Live ledger on this fiction set

`python3 -m maalestok ledger` (not a 2023 eval):

| hop | mean survival |
| --- | --- |
| pivot (hand EN) | 0.92 |
| English T5-style summary | 0.16 |
| silver DA | 0.19 |
| oracle DA | 0.52 |
| lead-2 DA | 0.50 |

Worst silver: `bh-02` (comma shift *and* currency swap, everything else dropped).
Oracle beats silver on every brief. Those numbers describe Blåhøj only.
