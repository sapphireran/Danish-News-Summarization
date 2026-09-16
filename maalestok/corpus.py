"""Sixteen original Blåhøj Almanak briefs.

These are not newspaper copy and not model output. Each brief plants at least
one measure scar that the 2023 hops are known to invite: comma shift, dropped
sign, 12-hour clock, currency swap, unit swap, feast swap, scale shift.
"""

from __future__ import annotations

from .article import Article, PlantedError

ARTICLES: tuple[Article, ...] = (
    Article(
        id="bh-01",
        title="Juni-regn over Græsbjerg",
        topic="vejr",
        body_da=(
            "I juni målte vejrstationen ved Græsbjerg 47,2 mm nedbør. "
            "Hele 18,6 mm faldt den 12. juni mellem kl. 06.00 og kl. 09.30, "
            "da et smalt regnbælte stod stille over Havremarken. "
            "Morten Bæk sagde, at vårbyggen godt kunne tåle vandet, men at "
            "furerne ved Mosebækken løb over Pilebro. "
            "Kommunens klimatabel noterer, at juni i fjor kun gav 29 mm. "
            "Provst Ejvind Holm aflyste aftensangen kl. 19.00, fordi kirkestien "
            "stod under vand. Almanakken minder om, at 47,2 mm på én måned "
            "stadig er under rekorden fra 2015 på 81,4 mm."
        ),
        pivot_en=(
            "In June the weather station at Graesbjerg measured 47.2 mm of rain. "
            "A full 18.6 mm fell on 12 June between 06:00 and 09:30, when a "
            "narrow rain band stalled over Havremarken. Morten Baek said the "
            "spring barley could take the water, but the furrows by Mosebaekken "
            "ran over Pilebro. The municipal climate table notes that June last "
            "year only gave 29 mm. Provst Ejvind Holm cancelled evensong at "
            "19:00 because the church path stood under water. The almanac "
            "recalls that 47.2 mm in one month is still below the 2015 record "
            "of 81.4 mm."
        ),
        summary_en=(
            "Graesbjerg recorded 47 mm of rain in June, including a morning "
            "burst on 12 June; evensong at 19:00 was cancelled."
        ),
        silver_da=(
            "Græsbjerg registrerede 47 mm regn i juni, heraf et morgenbyge "
            "den 12. juni; aftensangen kl. 19.00 blev aflyst."
        ),
        oracle_da=(
            "Græsbjerg målte 47,2 mm regn i juni, heraf 18,6 mm den 12. juni "
            "mellem kl. 06.00 og kl. 09.30; aftensangen kl. 19.00 blev aflyst, "
            "og rekorden fra 2015 på 81,4 mm står stadig."
        ),
        planted=(
            PlantedError(
                "precision_loss",
                "47,2 mm",
                "47 mm",
                "summary",
                "T5 rounded the June total before the back-translation.",
            ),
        ),
        lead2_da=(
            "I juni målte vejrstationen ved Græsbjerg 47,2 mm nedbør. "
            "Hele 18,6 mm faldt den 12. juni mellem kl. 06.00 og kl. 09.30, "
            "da et smalt regnbælte stod stille over Havremarken."
        ),
    ),
    Article(
        id="bh-02",
        title="Vårbyg på Havremarken",
        topic="høst",
        body_da=(
            "Morten Bæk høstede 2,4 ha vårbyg på Havremarken i uge 32. "
            "Kornet blev kørt til Kærholm Mejeri, som i år også tørrer korn "
            "for tre naboer. Afregningen landede på 3.200 kr. pr. ton, "
            "lidt under det, Inge Skovgaard havde sat som sogneregnskabets "
            "tommelfingerregel. Bæk minder om, at stykket kun er 2,4 ha, "
            "så en enkelt våd plet ved Mosebækken kan slå udbyttet skævt. "
            "Han venter 6,8 t/ha, hvis august holder sig tør efter kl. 14.00."
        ),
        pivot_en=(
            "Morten Baek harvested 2.4 ha of spring barley at Havremarken in "
            "week 32. The grain went to Kaerholm Dairy, which this year also "
            "dries grain for three neighbours. Settlement landed at 3,200 kr. "
            "per tonne, a little under the rule of thumb Inge Skovgaard had "
            "set for the parish accounts. Baek reminds us that the plot is "
            "only 2.4 ha, so one wet patch by Mosebaekken can skew the yield. "
            "He expects 6.8 t/ha if August stays dry after 14:00."
        ),
        summary_en=(
            "Baek harvested 24 ha of spring barley; settlement was 3,200 "
            "dollars per tonne."
        ),
        silver_da=(
            "Bæk høstede 24 ha vårbyg; afregningen var 3.200 dollar pr. ton."
        ),
        oracle_da=(
            "Bæk høstede 2,4 ha vårbyg på Havremarken; afregningen var "
            "3.200 kr. pr. ton, og han venter 6,8 t/ha."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "2,4 ha",
                "24 ha",
                "summary",
                "English 2.4 lost the decimal and came back as 24.",
            ),
            PlantedError(
                "currency_swap",
                "3.200 kr.",
                "3.200 dollar",
                "summary",
                "kr. was read as a generic currency and emitted as dollars.",
            ),
        ),
        lead2_da=(
            "Morten Bæk høstede 2,4 ha vårbyg på Havremarken i uge 32. "
            "Kornet blev kørt til Kærholm Mejeri, som i år også tørrer korn "
            "for tre naboer."
        ),
    ),
    Article(
        id="bh-03",
        title="Første skoledag på Sønderholt",
        topic="skole",
        body_da=(
            "Sønderholt Skole åbner 1. klasse med 28 elever onsdag. "
            "Lektor Hanne Friis ringer ind kl. 8.15, og forældrene bliver "
            "bedt om at være ude af gangen inden kl. 8.40. "
            "Skolen minder om, at Skt. Hans-ugen stadig tæller som "
            "undervisning, t.eks. når 1. klasse går til Mosebækken. "
            "Inge Skovgaard kommer med æbler kl. 10.00. "
            "Der er 28 elever på listen, heraf fire fra Græsbjerg."
        ),
        pivot_en=(
            "Sonderholt School opens year 1 with 28 pupils on Wednesday. "
            "Hanne Friis rings the bell at 8:15, and parents should be off "
            "the corridor before 8:40. The school notes that St. Hans week "
            "still counts as teaching, e.g. when year 1 walks to Mosebaekken. "
            "Inge Skovgaard brings apples at 10:00. There are 28 pupils on "
            "the list, including four from Graesbjerg."
        ),
        summary_en=(
            "Year 1 starts with 28 pupils; the bell rings at 20:15."
        ),
        silver_da=(
            "1. klasse starter med 28 elever; der ringes ind kl. 20.15."
        ),
        oracle_da=(
            "1. klasse åbner med 28 elever; Hanne Friis ringer ind kl. 8.15, "
            "og Inge Skovgaard kommer kl. 10.00."
        ),
        planted=(
            PlantedError(
                "clock_12h",
                "kl. 8.15",
                "kl. 20.15",
                "summary",
                "8:15 AM was emitted as a 24-hour evening time.",
            ),
        ),
        lead2_da=(
            "Sønderholt Skole åbner 1. klasse med 28 elever onsdag. "
            "Lektor Hanne Friis ringer ind kl. 8.15, og forældrene bliver "
            "bedt om at være ude af gangen inden kl. 8.40."
        ),
    ),
    Article(
        id="bh-04",
        title="Advent i Blåhøj Kirke",
        topic="kirke",
        body_da=(
            "3. søndag i advent holdes højmesse i Blåhøj Kirke kl. 10.00. "
            "Provst Ejvind Holm prædiker over teksten, og børnekoret øver "
            "fra kl. 9.15. Kirkekaffen bagefter koster 12 kr. "
            "Almanakken understreger, at det er 3. søndag i advent og ikke "
            "fasten, selv om salmevalget kan minde om hinanden. "
            "Der stilles 40 stole ekstra ved Pilebro-indgangen."
        ),
        pivot_en=(
            "On the third Sunday of Advent, high mass is held in Blaahoj "
            "Church at 10:00. Provst Ejvind Holm preaches, and the children's "
            "choir rehearses from 09:15. Church coffee afterwards costs 12 kr. "
            "The almanac stresses that this is the third Sunday of Advent and "
            "not Lent, even if the hymn list can sound alike. Forty extra "
            "chairs are set by the Pilebro door."
        ),
        summary_en=(
            "High mass on the third Sunday of Lent is at 10:00; coffee is 12 kr."
        ),
        silver_da=(
            "Højmesse 3. søndag i fasten er kl. 10.00; kaffen koster 12 kr."
        ),
        oracle_da=(
            "Højmesse 3. søndag i advent er kl. 10.00; kaffen koster 12 kr., "
            "og koret øver fra kl. 9.15."
        ),
        planted=(
            PlantedError(
                "feast_swap",
                "3. søndag i advent",
                "3. søndag i fasten",
                "summary",
                "Advent and Lent are easy to swap once the pivot says 'third Sunday'.",
            ),
        ),
        lead2_da=(
            "3. søndag i advent holdes højmesse i Blåhøj Kirke kl. 10.00. "
            "Provst Ejvind Holm prædiker over teksten, og børnekoret øver "
            "fra kl. 9.15."
        ),
    ),
    Article(
        id="bh-05",
        title="Cykelsti til Nørreled",
        topic="anlæg",
        body_da=(
            "Den nye cykelsti fra Græsbjerg til Nørreled er 4,8 km lang. "
            "Sognerådet har sat 1,2 mio. kr. af, heraf 0,3 mio. kr. til "
            "belysning ved Pilebro. Inge Skovgaard siger, at 4,8 km lyder "
            "kort på et kort, men at bakken ved Rævedal Skov tager tiden. "
            "Arbejdet begynder den 22. september kl. 06.30, hvis Mosebækken "
            "ikke står over sine brinker."
        ),
        pivot_en=(
            "The new cycle path from Graesbjerg to Norreled is 4.8 km long. "
            "The parish council has set aside 1.2 million kr., of which 0.3 "
            "million kr. is for lighting at Pilebro. Inge Skovgaard says 4.8 "
            "km looks short on a map, but the hill by Raevedal Wood takes "
            "time. Work starts on 22 September at 06:30 if Mosebaekken stays "
            "inside its banks."
        ),
        summary_en=(
            "The 48 km cycle path is budgeted at 12 million kr. and starts "
            "on 22 September."
        ),
        silver_da=(
            "Den 48 km lange cykelsti er budgetteret til 12 mio. kr. og "
            "begynder den 22. september."
        ),
        oracle_da=(
            "Cykelstien er 4,8 km og budgetteret til 1,2 mio. kr.; arbejdet "
            "begynder den 22. september kl. 06.30."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "4,8 km",
                "48 km",
                "summary",
                "4.8 km lost the decimal in the English summary.",
            ),
            PlantedError(
                "scale_shift",
                "1,2 mio. kr.",
                "12 mio. kr.",
                "summary",
                "1.2 million was rewritten as 12 million.",
            ),
        ),
        lead2_da=(
            "Den nye cykelsti fra Græsbjerg til Nørreled er 4,8 km lang. "
            "Sognerådet har sat 1,2 mio. kr. af, heraf 0,3 mio. kr. til "
            "belysning ved Pilebro."
        ),
    ),
    Article(
        id="bh-06",
        title="Nattefrost i januar",
        topic="vejr",
        body_da=(
            "Nattemperaturen i Græsbjerg faldt til −8,3 °C den 14. januar "
            "kl. 03.40. Vandrørene ved Sønderholt Skole holdt, men hanerne "
            "på Havremarken frøs. Morten Bæk målte −8,3 °C på sin egen "
            "stang ved laden, t.eks. da han slukkede lyset kl. 03.55. "
            "Almanakken sammenligner med −11,0 °C i 2018. "
            "Inge Skovgaard bad folk tømme slangerne inden kl. 18.00."
        ),
        pivot_en=(
            "The night temperature in Graesbjerg fell to -8.3 C on 14 January "
            "at 03:40. The pipes at Sonderholt School held, but the taps at "
            "Havremarken froze. Morten Baek measured -8.3 C on his own post "
            "by the barn, e.g. when he switched the light off at 03:55. "
            "The almanac compares this with -11.0 C in 2018. Inge Skovgaard "
            "asked people to empty the hoses before 18:00."
        ),
        summary_en=(
            "Graesbjerg fell to 8.3 C on 14 January; hoses should be emptied "
            "before 18:00."
        ),
        silver_da=(
            "Græsbjerg faldt til 8,3 °C den 14. januar; slangerne skulle "
            "tømmes inden kl. 18.00."
        ),
        oracle_da=(
            "Græsbjerg faldt til −8,3 °C den 14. januar kl. 03.40; slangerne "
            "skulle tømmes inden kl. 18.00, og 2018-målet var −11,0 °C."
        ),
        planted=(
            PlantedError(
                "sign_drop",
                "−8,3 °C",
                "8,3 °C",
                "summary",
                "The leading minus did not survive the English T5 rewrite.",
            ),
        ),
        lead2_da=(
            "Nattemperaturen i Græsbjerg faldt til −8,3 °C den 14. januar "
            "kl. 03.40. Vandrørene ved Sønderholt Skole holdt, men hanerne "
            "på Havremarken frøs."
        ),
    ),
    Article(
        id="bh-07",
        title="Møllen ved Rævedal",
        topic="energi",
        body_da=(
            "Den nye mølle nord for Rævedal Skov yder 2,1 MW. "
            "Navhøjden er 87 m, og vingespidserne går op i 149 m. "
            "Sognerådet har fået oplyst, at 2,1 MW i middelvind dækker "
            "cirka 1.200 husstande i tørt vejr. "
            "Ole Nygaard mindede om, at brandvejen skal holde 4,0 m fri "
            "bredde, også når mejekøen holder ved Pilebro."
        ),
        pivot_en=(
            "The new turbine north of Raevedal Wood yields 2.1 MW. Hub height "
            "is 87 m, and the blade tips reach 149 m. The parish council was "
            "told that 2.1 MW in mean wind covers about 1,200 households in "
            "dry weather. Ole Nygaard reminded everyone that the fire road "
            "must keep 4.0 m of free width, even when the harvest queue stops "
            "at Pilebro."
        ),
        summary_en=(
            "The Raevedal turbine yields 21 MW at a hub height of 87 m."
        ),
        silver_da=(
            "Møllen ved Rævedal yder 21 MW med en navhøjde på 87 m."
        ),
        oracle_da=(
            "Møllen ved Rævedal yder 2,1 MW med en navhøjde på 87 m og "
            "vingespidser i 149 m."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "2,1 MW",
                "21 MW",
                "summary",
                "2.1 MW became 21 MW after the decimal was dropped.",
            ),
        ),
        lead2_da=(
            "Den nye mølle nord for Rævedal Skov yder 2,1 MW. "
            "Navhøjden er 87 m, og vingespidserne går op i 149 m."
        ),
    ),
    Article(
        id="bh-08",
        title="Bibliotekets vintertid",
        topic="kultur",
        body_da=(
            "Blåhøj Bibliotek holder åbent man.–tors. 13.00–17.00 og "
            "fre. 10.00–13.00 fra den 1. oktober. "
            "Hanne Friis flytter skolebesøgene til kl. 13.15, så 1. klasse "
            "ikke rammer frokosten. Bøder er stadig 12 kr. pr. uge. "
            "Almanakken beder folk huske, at lørdag er lukket, t.eks. i "
            "efterårsferien. Inge Skovgaard læser eventyr kl. 16.00 om torsdagen."
        ),
        pivot_en=(
            "Blaahoj Library is open Mon–Thu 13:00–17:00 and Fri 10:00–13:00 "
            "from 1 October. Hanne Friis moves school visits to 13:15 so year "
            "1 does not hit lunch. Fines are still 12 kr. per week. The "
            "almanac asks people to remember Saturday is closed, e.g. in the "
            "autumn holiday. Inge Skovgaard reads fairy tales at 16:00 on "
            "Thursdays."
        ),
        summary_en=(
            "The library is open 13:00–19:00 on weekdays; Thursday stories "
            "are at 16:00."
        ),
        silver_da=(
            "Biblioteket har åbent 13.00–19.00 på hverdage; torsdagens "
            "eventyr er kl. 16.00."
        ),
        oracle_da=(
            "Biblioteket har åbent man.–tors. 13.00–17.00 og fre. 10.00–13.00; "
            "torsdagens eventyr er kl. 16.00."
        ),
        planted=(
            PlantedError(
                "clock_shift",
                "13.00–17.00",
                "13.00–19.00",
                "summary",
                "Closing time drifted from 17:00 to 19:00 in the English summary.",
            ),
        ),
        lead2_da=(
            "Blåhøj Bibliotek holder åbent man.–tors. 13.00–17.00 og "
            "fre. 10.00–13.00 fra den 1. oktober. "
            "Hanne Friis flytter skolebesøgene til kl. 13.15, så 1. klasse "
            "ikke rammer frokosten."
        ),
    ),
    Article(
        id="bh-09",
        title="Kartoffelhøst ved Kærholm",
        topic="høst",
        body_da=(
            "Kærholm Avl tog 38 t/ha op af 6,5 ha kartofler i uge 37. "
            "Pia Kjeldsen sagde, at 38 t/ha er pænt, men at 6,5 ha er for "
            "lidt til at fylde mejeriets køl alene. "
            "Vaskevandet fra kulerne målte 2,1 m/s i Mosebækken efter "
            "skylning. Prisen blev 1,8 kr. pr. kilo til skolekøkkenet. "
            "Høsten sluttede kl. 17.45 den 14. september."
        ),
        pivot_en=(
            "Kaerholm Farm lifted 38 t/ha from 6.5 ha of potatoes in week 37. "
            "Pia Kjeldsen said 38 t/ha is decent, but 6.5 ha is too little to "
            "fill the dairy cold store alone. Wash water from the clamps "
            "measured 2.1 m/s in Mosebaekken after rinsing. The price was "
            "1.8 kr. per kilo for the school kitchen. Harvest ended at 17:45 "
            "on 14 September."
        ),
        summary_en=(
            "Kaerholm harvested 38 kg/ha from 6.5 ha; work ended at 17:45."
        ),
        silver_da=(
            "Kærholm høstede 38 kg/ha på 6,5 ha; arbejdet sluttede kl. 17.45."
        ),
        oracle_da=(
            "Kærholm høstede 38 t/ha på 6,5 ha; arbejdet sluttede kl. 17.45 "
            "den 14. september."
        ),
        planted=(
            PlantedError(
                "unit_swap",
                "38 t/ha",
                "38 kg/ha",
                "summary",
                "Tonnes per hectare collapsed to kilograms per hectare.",
            ),
        ),
        lead2_da=(
            "Kærholm Avl tog 38 t/ha op af 6,5 ha kartofler i uge 37. "
            "Pia Kjeldsen sagde, at 38 t/ha er pænt, men at 6,5 ha er for "
            "lidt til at fylde mejeriets køl alene."
        ),
    ),
    Article(
        id="bh-10",
        title="Linje 82 til Nørreled",
        topic="trafik",
        body_da=(
            "Linje 82 kører fra Nørreled til Sønderholt Skole på 25 min. "
            "En voksenbillet koster 18 kr., og børn under 1. klasse kører "
            "gratis. Ole Nygaard klagede over, at vognen kl. 7.12 ofte er "
            "seks minutter forsinket, når mejetrafikken holder ved Pilebro. "
            "Rutetabellen slår fast, at det er linje 82 og ikke linje 28, "
            "som kun kører lørdag."
        ),
        pivot_en=(
            "Line 82 runs from Norreled to Sonderholt School in 25 min. An "
            "adult ticket costs 18 kr., and children below year 1 ride free. "
            "Ole Nygaard complained that the 07:12 bus is often six minutes "
            "late when harvest traffic stops at Pilebro. The timetable "
            "insists this is line 82 and not line 28, which only runs on "
            "Saturdays."
        ),
        summary_en=(
            "Line 28 reaches the school in 25 min; an adult ticket is 18 kr."
        ),
        silver_da=(
            "Linje 28 når skolen på 25 min.; en voksenbillet koster 18 kr."
        ),
        oracle_da=(
            "Linje 82 når skolen på 25 min.; en voksenbillet koster 18 kr., "
            "og afgangen kl. 7.12 er den, folk klager over."
        ),
        planted=(
            PlantedError(
                "line_swap",
                "linje 82",
                "Linje 28",
                "summary",
                "82 and 28 swapped once the English summary shortened the route note.",
            ),
        ),
        lead2_da=(
            "Linje 82 kører fra Nørreled til Sønderholt Skole på 25 min. "
            "En voksenbillet koster 18 kr., og børn under 1. klasse kører "
            "gratis."
        ),
    ),
    Article(
        id="bh-11",
        title="Brønden i Rævedal",
        topic="vand",
        body_da=(
            "Brønden ved Rævedal Skov er 38,5 m dyb og viser 2,4 mg/l nitrat. "
            "Pia Kjeldsen kalder 2,4 mg/l for acceptabelt, men minder om "
            "grænseværdien på 50 mg/l. Prøven blev taget den 3. oktober "
            "kl. 11.20. Sognerådet vil måle igen, hvis Mosebækken stiger "
            "mere end 0,6 m efter efterårsregn."
        ),
        pivot_en=(
            "The well by Raevedal Wood is 38.5 m deep and shows 2.4 mg/l "
            "nitrate. Pia Kjeldsen calls 2.4 mg/l acceptable, but reminds "
            "everyone of the 50 mg/l limit. The sample was taken on 3 October "
            "at 11:20. The parish council will measure again if Mosebaekken "
            "rises more than 0.6 m after autumn rain."
        ),
        summary_en=(
            "The Raevedal well is 38.5 m deep and shows 24 mg/l nitrate."
        ),
        silver_da=(
            "Brønden i Rævedal er 38,5 m dyb og viser 24 mg/l nitrat."
        ),
        oracle_da=(
            "Brønden i Rævedal er 38,5 m dyb og viser 2,4 mg/l nitrat; "
            "grænseværdien er 50 mg/l."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "2,4 mg/l",
                "24 mg/l",
                "summary",
                "2.4 mg/l lost the decimal; 24 mg/l still looks legal under 50.",
            ),
        ),
        lead2_da=(
            "Brønden ved Rævedal Skov er 38,5 m dyb og viser 2,4 mg/l nitrat. "
            "Pia Kjeldsen kalder 2,4 mg/l for acceptabelt, men minder om "
            "grænseværdien på 50 mg/l."
        ),
    ),
    Article(
        id="bh-12",
        title="Ombygning af Stenholt Hallen",
        topic="anlæg",
        body_da=(
            "Stenholt Hallen måler 24 × 44 m inden ombygningen. "
            "Sognerådet har sat 2,8 mio. kr. af, og Inge Skovgaard vil ikke "
            "røre banens 24 × 44 m, kun omklædningen. "
            "Arbejdet varer 12 min. i brandøvelsesplanen, hvis Ole Nygaard "
            "skal tømme huset. Første spigermøde er den 22. september "
            "kl. 09.00."
        ),
        pivot_en=(
            "Stenholt Hall measures 24 × 44 m before the rebuild. The parish "
            "council has set aside 2.8 million kr., and Inge Skovgaard will "
            "not touch the 24 × 44 m court, only the changing rooms. The "
            "work lasts 12 min. in the fire-drill plan if Ole Nygaard has to "
            "clear the house. The first site meeting is on 22 September at "
            "09:00."
        ),
        summary_en=(
            "Stenholt Hall, now 24 × 4.4 m, gets a 2.8 million kr. rebuild."
        ),
        silver_da=(
            "Stenholt Hallen, nu 24 × 4,4 m, får en ombygning til 2,8 mio. kr."
        ),
        oracle_da=(
            "Stenholt Hallen måler 24 × 44 m; ombygningen koster 2,8 mio. kr. "
            "og rører ikke banen."
        ),
        planted=(
            PlantedError(
                "dimension_shift",
                "24 × 44 m",
                "24 × 4,4 m",
                "summary",
                "The second axis dropped a factor of ten (44 → 4.4).",
            ),
        ),
        lead2_da=(
            "Stenholt Hallen måler 24 × 44 m inden ombygningen. "
            "Sognerådet har sat 2,8 mio. kr. af, og Inge Skovgaard vil ikke "
            "røre banens 24 × 44 m, kun omklædningen."
        ),
    ),
    Article(
        id="bh-13",
        title="Mælk med 3,8 procent",
        topic="mejeri",
        body_da=(
            "Kærholm Mejeri tog 450 liter morgenmælk ind den 12. juni. "
            "Pia Kjeldsen målte 3,8% fedt, hvilket er præcis det, skolekøkkenet "
            "bestiller. Hun minder om, at 3,8% ikke må rundes op til søndags- "
            "fløde, t.eks. når 1. klasse bager. Tanken rummer 2.400 liter, "
            "hvis Mosebækken ikke slår strømmen fra. Afhentning er kl. 06.45."
        ),
        pivot_en=(
            "Kaerholm Dairy took in 450 litres of morning milk on 12 June. "
            "Pia Kjeldsen measured 3.8% fat, exactly what the school kitchen "
            "orders. She reminds staff that 3.8% must not be rounded up to "
            "Sunday cream, e.g. when year 1 bakes. The tank holds 2,400 "
            "litres if Mosebaekken does not cut the power. Collection is at "
            "06:45."
        ),
        summary_en=(
            "The dairy took 450 litres at 38% fat; collection is at 06:45."
        ),
        silver_da=(
            "Mejeriet tog 450 liter ind med 38% fedt; afhentning er kl. 06.45."
        ),
        oracle_da=(
            "Mejeriet tog 450 liter ind med 3,8% fedt den 12. juni; "
            "afhentning er kl. 06.45."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "3,8%",
                "38%",
                "summary",
                "3.8% fat became 38% once the decimal vanished.",
            ),
        ),
        lead2_da=(
            "Kærholm Mejeri tog 450 liter morgenmælk ind den 12. juni. "
            "Pia Kjeldsen målte 3,8% fedt, hvilket er præcis det, skolekøkkenet "
            "bestiller."
        ),
    ),
    Article(
        id="bh-14",
        title="Øvelse på brandstationen",
        topic="beredskab",
        body_da=(
            "Ole Nygaard mønstrede 6 brandfolk til øvelsen ved Pilebro. "
            "Målet er 12 min. fra sirenen til første stråle i Rævedal Skov. "
            "Sidste år landede de på 14 min., fordi linje 82 holdt inde på "
            "vejen. Inge Skovgaard serverede kaffe til 12 kr. bagefter. "
            "Næste øvelse er den 14. januar kl. 19.00, ikke kl. 7.00."
        ),
        pivot_en=(
            "Ole Nygaard mustered 6 firefighters for the drill at Pilebro. "
            "The target is 12 min. from the siren to the first jet in "
            "Raevedal Wood. Last year they landed on 14 min. because line 82 "
            "blocked the road. Inge Skovgaard served coffee at 12 kr. "
            "afterwards. The next drill is on 14 January at 19:00, not 07:00."
        ),
        summary_en=(
            "Six firefighters aim for a 21 min. response; coffee is 12 kr."
        ),
        silver_da=(
            "6 brandfolk sigter efter 21 min. responstid; kaffen koster 12 kr."
        ),
        oracle_da=(
            "6 brandfolk sigter efter 12 min. responstid; kaffen koster 12 kr., "
            "og næste øvelse er den 14. januar kl. 19.00."
        ),
        planted=(
            PlantedError(
                "value_shift",
                "12 min.",
                "21 min.",
                "summary",
                "12 min. and last year's 14 min. were mashed into 21.",
            ),
        ),
        lead2_da=(
            "Ole Nygaard mønstrede 6 brandfolk til øvelsen ved Pilebro. "
            "Målet er 12 min. fra sirenen til første stråle i Rævedal Skov."
        ),
    ),
    Article(
        id="bh-15",
        title="Høstmarked på Havremarken",
        topic="marked",
        body_da=(
            "Høstmarkedet på Havremarken holdes den 22. september "
            "kl. 09.00–14.00. En stand koster 75 kr., og skolekoret synger "
            "kl. 11.30. Pia Kjeldsen sælger ost i stykker à 0,4 kg. "
            "Linje 82 sætter ekstra stop ved Pilebro kl. 08.50. "
            "Almanakken lover, at markedet lukker kl. 14.00, også hvis "
            "kagen slår til."
        ),
        pivot_en=(
            "The harvest market at Havremarken is on 22 September from "
            "09:00–14:00. A stall costs 75 kr., and the school choir sings "
            "at 11:30. Pia Kjeldsen sells cheese in 0.4 kg pieces. Line 82 "
            "adds a stop at Pilebro at 08:50. The almanac promises the "
            "market closes at 14:00 even if the cake holds out."
        ),
        summary_en=(
            "The 22 September market runs 09:00–16:00; stalls cost 75 kr."
        ),
        silver_da=(
            "Marked den 22. september varer 09.00–16.00; en stand koster 75 kr."
        ),
        oracle_da=(
            "Marked den 22. september varer 09.00–14.00; en stand koster 75 kr., "
            "og koret synger kl. 11.30."
        ),
        planted=(
            PlantedError(
                "clock_shift",
                "09.00–14.00",
                "09.00–16.00",
                "summary",
                "Closing time drifted two hours in the English summary.",
            ),
        ),
        lead2_da=(
            "Høstmarkedet på Havremarken holdes den 22. september "
            "kl. 09.00–14.00. En stand koster 75 kr., og skolekoret synger "
            "kl. 11.30."
        ),
    ),
    Article(
        id="bh-16",
        title="Blæst over Mosebækken",
        topic="vejr",
        body_da=(
            "Vindstød ved Mosebækken nåede 14,7 m/s den 3. oktober kl. 16.20. "
            "Møllen ved Rævedal gik i pause, selv om den yder 2,1 MW i "
            "jævn vind. Ole Nygaard spærrede Pilebro i 25 min., mens en "
            "gren blev skåret ned. Almanakken noterer, at 14,7 m/s er under "
            "stormgrænsen, men over det, 1. klasse må cykle i. "
            "Hanne Friis sendte eleverne ind kl. 16.25."
        ),
        pivot_en=(
            "Gusts at Mosebaekken reached 14.7 m/s on 3 October at 16:20. "
            "The Raevedal turbine paused, even though it yields 2.1 MW in "
            "steady wind. Ole Nygaard closed Pilebro for 25 min. while a "
            "branch was cut. The almanac notes that 14.7 m/s is below gale "
            "force but above what year 1 may cycle in. Hanne Friis sent the "
            "pupils indoors at 16:25."
        ),
        summary_en=(
            "Gusts of 147 m/s paused the turbine; Pilebro was closed 25 min."
        ),
        silver_da=(
            "Vindstød på 147 m/s stoppede møllen; Pilebro var spærret i 25 min."
        ),
        oracle_da=(
            "Vindstød på 14,7 m/s stoppede møllen den 3. oktober kl. 16.20; "
            "Pilebro var spærret i 25 min."
        ),
        planted=(
            PlantedError(
                "comma_shift",
                "14,7 m/s",
                "147 m/s",
                "summary",
                "14.7 m/s became a cartoon 147 m/s after the decimal dropped.",
            ),
        ),
        lead2_da=(
            "Vindstød ved Mosebækken nåede 14,7 m/s den 3. oktober kl. 16.20. "
            "Møllen ved Rævedal gik i pause, selv om den yder 2,1 MW i "
            "jævn vind."
        ),
    ),
)


def by_id(article_id: str) -> Article:
    for article in ARTICLES:
        if article.id == article_id:
            return article
    raise KeyError(article_id)


def all_ids() -> list[str]:
    return [article.id for article in ARTICLES]
