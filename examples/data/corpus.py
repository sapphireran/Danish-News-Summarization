"""Original fictional North Jutland news used by the example tables.

None of these articles are copied from TV2 Nord, Nordjylland-News, or
any other newspaper. Place names are real; people, quotes, and events
are invented for documentation.
"""

from __future__ import annotations

from typing import TypedDict


class SampleArticle(TypedDict):
    id: str
    danish_body: str
    english_body: str
    english_summary: str
    danish_summary: str
    prediction: str
    split: str


ARTICLES: list[SampleArticle] = [
    {
        "id": "da-001",
        "split": "train",
        "danish_body": (
            "Hirtshals Havn ændrer fra den 1. november afgangsplanerne for den "
            "daglige færge til Kristiansand. Havnedirektør Mette Kjær oplyser, "
            "at den nye plan samler lastbiltrafikken på tre faste afgange i "
            "døgnet, så personbiler og fodgængere får kortere ventetid i "
            "weekenden. Flere vognmænd i Vendsyssel har allerede meldt, at de "
            "vil rykke deres faste ture til de tidlige morgenafgange. Kommunen "
            "forventer, at ændringen også kan mindske kødannelse på Aalborgvej "
            "i myldretiden, hvor færgekøer i dag ofte strækker sig ned mod "
            "centrum. Passagerforeningen Færgependlerne er mere forbeholden og "
            "peger på, at familier med cykler kan miste en eftermiddagsafgang "
            "i skoleferierne. Kjær svarer, at havnen vil evaluere planen efter "
            "tre måneder og åbne en ekstra weekendafgang, hvis belægningen "
            "overstiger 85 procent."
        ),
        "english_body": (
            "From 1 November, Hirtshals Harbour is changing the departure "
            "schedule for the daily ferry to Kristiansand. Harbour director "
            "Mette Kjær says the new plan concentrates truck traffic on three "
            "fixed departures a day so that cars and pedestrians have shorter "
            "weekend waits. Several hauliers in Vendsyssel have already said "
            "they will move their regular runs to the early morning "
            "departures. The municipality expects the change also to ease "
            "congestion on Aalborgvej at rush hour, where ferry queues often "
            "stretch toward the town centre today. The passenger group "
            "Færgependlerne is more cautious and notes that families with "
            "bicycles may lose an afternoon departure during school holidays. "
            "Kjær replies that the harbour will review the plan after three "
            "months and add an extra weekend departure if occupancy exceeds "
            "85 percent."
        ),
        "english_summary": (
            "Hirtshals will group truck ferry traffic onto three daily "
            "Kristiansand departures so weekend car passengers wait less, "
            "then review the plan after three months."
        ),
        "danish_summary": (
            "Hirtshals samler lastbiltrafikken på tre daglige færgeafgange til "
            "Kristiansand, så bilpassagerer venter kortere i weekenden. "
            "Planen evalueres efter tre måneder."
        ),
        "prediction": (
            "Hirtshals Havn ændrer færgeplanen til Norge, så lastbiler samles "
            "på færre afgange og familier slipper for kø på Aalborgvej."
        ),
    },
    {
        "id": "da-002",
        "split": "train",
        "danish_body": (
            "Aalborg Kommune åbner i marts en ny cykelsti mellem Vestre Havnepromenade "
            "og universitetskvarteret i Øst. Stien føres på en hævet tracé langs "
            "fjorden, så den ikke krydser lastbilindkørslerne til de sidste "
            "lagre på Østre Havn. Teknik- og miljørådmand Jonas Holm kalder "
            "projektet det manglende led i pendlernettet, fordi studerende i "
            "dag tvinges ud på Østre Allé i myldretiden. Anlægsbudgettet er "
            "24 millioner kroner, hvoraf staten dækker de 10 gennem "
            "cykelpuljen. Butiksforeningen i Nørresundby advarer om, at "
            "brohelligdage kan give trængsel ved den midlertidige "
            "færdselsregulering på Limfjordsbroen, mens entreprenøren "
            "arbejder om natten. Holm siger, at der opsættes tællere ved "
            "begge ender, og at kommunen offentliggør de første "
            "trafiktal inden sommerferien."
        ),
        "english_body": (
            "In March, Aalborg Municipality will open a new cycleway between "
            "Vestre Havnepromenade and the university district in the east. "
            "The path runs on a raised alignment along the fjord so it does "
            "not cross the remaining warehouse truck gates on Østre Havn. "
            "Technical and environmental alderman Jonas Holm calls the "
            "project the missing link in the commuter network, because "
            "students are currently forced onto Østre Allé at rush hour. "
            "The construction budget is 24 million kroner, of which the "
            "state covers 10 million through the national cycling fund. "
            "The Nørresundby shopkeepers' association warns that public "
            "holidays may congest the temporary traffic scheme on the "
            "Limfjord Bridge while the contractor works at night. Holm says "
            "counters will be installed at both ends and that the city will "
            "publish the first traffic counts before the summer holiday."
        ),
        "english_summary": (
            "Aalborg will open a raised fjord-side cycleway from the western "
            "harbour to the university district in March, funded in part by "
            "the national cycling grant."
        ),
        "danish_summary": (
            "Aalborg åbner i marts en hævet cykelsti langs fjorden fra Vestre "
            "Havnepromenade til universitetskvarteret. Staten betaler 10 af "
            "de 24 millioner kroner."
        ),
        "prediction": (
            "Ny cykelsti i Aalborg skal føre studerende uden om Østre Allé, "
            "men butikker i Nørresundby frygter kø på Limfjordsbroen."
        ),
    },
    {
        "id": "da-003",
        "split": "train",
        "danish_body": (
            "Et kraftigt lavtryk sendte i nat vindstød af stormstyrke ind over "
            "Skagen og knækkede fortøjninger på tre kuttere i den ydre bassinhavn. "
            "Ingen personer kom til skade, men skipper Lars Mikkelsen mistede "
            "en trawlramme til en værdi af omkring 180.000 kroner, da kutteren "
            "Mågen blev presset mod kajkanten. Beredskabet i Frederikshavn "
            "rykkede ud klokken 03.40, efter havnefogeden havde meldt om løse "
            "fendere og en væltet container med fiskekasser. DMI målte 38 meter "
            "i sekundet på Grenen, hvilket er den højeste januarnotering siden "
            "2015. Fiskeriforeningen forventer, at flere mindre både bliver "
            "på land til midt i næste uge, fordi bølgerne i Skagerrak stadig "
            "står i tre til fire meter. Kommunen åbner en midlertidig "
            "skadesanmeldelse i kulturhuset, og forsikringsselskaberne er "
            "varslet om, at taksatorerne først kan komme frem, når vejen "
            "langs Grenen er spulet fri for tang og grus."
        ),
        "english_body": (
            "A sharp low last night drove storm-force gusts across Skagen and "
            "broke the moorings of three cutters in the outer basin. No one "
            "was injured, but skipper Lars Mikkelsen lost a trawl frame worth "
            "about 180,000 kroner when the cutter Mågen was pushed against "
            "the quay. The Frederikshavn emergency service deployed at 03.40 "
            "after the harbour master reported loose fenders and an overturned "
            "container of fish boxes. DMI measured 38 metres per second at "
            "Grenen, the highest January reading since 2015. The fishermen's "
            "association expects several smaller boats to stay ashore until "
            "the middle of next week because Skagerrak waves are still three "
            "to four metres. The municipality is opening a temporary claims "
            "desk in the cultural centre, and insurers have been told that "
            "assessors can only arrive once the road along Grenen has been "
            "washed clear of seaweed and gravel."
        ),
        "english_summary": (
            "Storm gusts in Skagen broke three cutter moorings overnight. "
            "No injuries were reported; smaller boats are expected to stay "
            "ashore until next week."
        ),
        "danish_summary": (
            "Stormstød i Skagen knækkede fortøjninger på tre kuttere. Ingen "
            "kom til skade, og mindre både ventes at blive på land til næste "
            "uge."
        ),
        "prediction": (
            "Stormen i Skagen ødelagde tre kuttere og en trawlramme til "
            "180.000 kroner, og beredskabet rykkede ud før daggry."
        ),
    },
    {
        "id": "da-004",
        "split": "train",
        "danish_body": (
            "Hobro Byskole indvier onsdag en ny naturfagsfløj med to laboratorier "
            "og et åbent værksted mod skolegården. Fløjen erstatter de "
            "barakker, som 7. og 8. klasse har brugt siden skimmelsagen i "
            "2019. Rektor Anne Sofie Berg siger, at eleverne nu kan køre "
            "længere forsøgsforløb i fysik og biologi i stedet for at rydde "
            "op efter hver lektion. Anlægget har kostet 11,4 millioner "
            "kroner og er betalt af Mariagerfjord Kommune med et tilskud "
            "fra A.P. Møller Fonden. Forældrebestyrelsen havde ønsket en "
            "rigtig idrætshal i samme omgang, men det projekt er udskudt til "
            "budget 2027. Eleverne markerer åbningen med en udstilling om "
            "fjordens vandkvalitet, baseret på prøver de selv har taget ved "
            "broen i løbet af efteråret."
        ),
        "english_body": (
            "On Wednesday Hobro Town School will open a new science wing with "
            "two laboratories and an open workshop facing the yard. The wing "
            "replaces the portacabins that years 7 and 8 have used since the "
            "2019 mould case. Headteacher Anne Sofie Berg says pupils can now "
            "run longer physics and biology experiments instead of clearing "
            "away after every lesson. The building cost 11.4 million kroner "
            "and was paid for by Mariagerfjord Municipality with a grant from "
            "the A.P. Møller Foundation. The parent board had wanted a full "
            "sports hall at the same time, but that project is postponed to "
            "the 2027 budget. Pupils will mark the opening with an exhibition "
            "on fjord water quality, based on samples they collected at the "
            "bridge during the autumn."
        ),
        "english_summary": (
            "Hobro Town School opens a new science wing that replaces the "
            "post-mould portacabins, funded by the municipality and the "
            "A.P. Møller Foundation."
        ),
        "danish_summary": (
            "Hobro Byskole indvier en ny naturfagsfløj, der erstatter "
            "barakkerne efter skimmelsagen. Kommunen og A.P. Møller Fonden "
            "har betalt de 11,4 millioner kroner."
        ),
        "prediction": (
            "Hobro Byskole får nye laboratorier til 11,4 millioner, men "
            "idrætshallen er udskudt til 2027."
        ),
    },
    {
        "id": "da-005",
        "split": "validation",
        "danish_body": (
            "Thy Museum åbner lørdag en vandreudstilling om kystfiskeriets "
            "redskaber fra 1880 til 1970. De fleste genstande kommer fra "
            "private lofter i Klitmøller og Vorupør, og flere net er stadig "
            "mærket med familienavne. Museet holder gratis omvisning klokken "
            "11 og 14 hele åbningsweekenden."
        ),
        "english_body": (
            "On Saturday Thy Museum opens a travelling exhibition on coastal "
            "fishing gear from 1880 to 1970. Most objects come from private "
            "attics in Klitmøller and Vorupør, and several nets are still "
            "tagged with family names. The museum offers free guided tours "
            "at 11 and 14 throughout the opening weekend."
        ),
        "english_summary": (
            "Thy Museum opens a weekend exhibition of historic coastal "
            "fishing gear collected from local attics."
        ),
        "danish_summary": (
            "Thy Museum åbner en vandreudstilling om kystfiskeriets redskaber "
            "med gratis omvisninger i åbningsweekenden."
        ),
        "prediction": (
            "Thy Museum viser gamle fiskenet fra Klitmøller og Vorupør og "
            "holder gratis omvisning lørdag."
        ),
    },
    {
        "id": "da-006",
        "split": "train",
        "danish_body": (
            "Anden etape af havvindmølleparken nord for Frederikshavn er rykket "
            "et skridt nærmere, efter Energinet har godkendt ilandføringskablet "
            "ved Hirsholmene. Bygherren Nordvind Kattegat A/S forventer at "
            "rejse 28 møller med en samlet kapacitet på 420 megawatt, hvis "
            "det sidste miljøtillæg fra Kystdirektoratet lander inden påske. "
            "Det er knap så mange møller som i det oprindelige udbud, men "
            "hver turbine er større, så den lovede strøm til det nordjyske "
            "elnet er næsten uændret. Fiskerne i Strandby har gennem hele "
            "forløbet krævet en fast sejlkoridor øst om parken, fordi "
            "jollefiskeriet efter torsk ellers presses ind i den tunge "
            "færgerute til Göteborg. Selskabet har nu indtegnet en 700 meter "
            "bred passage på de opdaterede søkort og lover AIS-overvågning "
            "i de første to driftsår. I Frederikshavn Byråd er holdningen "
            "delt. Socialdemokratiet og SF ser parken som erstatning for de "
            "arbejdspladser, værftet mistede i 2010'erne, mens Venstre "
            "efterlyser en klar plan for, hvordan servicehavnen skal udvides "
            "uden at æde det sidste areal til lystbåde. Borgmester Ida "
            "Slot siger, at kommunen først tager stilling til en "
            "havneudvidelse, når der ligger en bindende tidslinje for "
            "fundamenter og ilandføring. Energinet understreger, at "
            "selve kablet kan graves ned i en eksisterende korridor fra "
            "2018, så der ikke skal åbnes nye render gennem ålegræsset "
            "inden for de første to kilometer fra kysten. Hvis tidsplanen "
            "holder, skal de første komponenter losse i efterårsstormenes "
            "pause i oktober, og nettilslutningen er sat til tredje "
            "kvartal året efter. En særlig arbejdsgruppe med "
            "turistforeningen skal samtidig finde en rute til "
            "kajakroere, så parken ikke skærer den populære tur til "
            "Deget over. Det er den slags hensyn, der i andre danske "
            "parker først er kommet efter idriftsættelse, og derfor "
            "vælger Nordvind at skrive dem ind i udbudsmaterialet nu."
        ),
        "english_body": (
            "The second phase of the offshore wind farm north of Frederikshavn "
            "moved a step closer after Energinet approved the landfall cable "
            "near Hirsholmene. Developer Nordvind Kattegat A/S expects to "
            "raise 28 turbines with a combined capacity of 420 megawatts if "
            "the last environmental addendum from the Coastal Authority "
            "arrives before Easter. That is fewer turbines than the original "
            "tender, but each machine is larger, so the promised power for "
            "the North Jutland grid is almost unchanged. Fishers in Strandby "
            "have throughout the process demanded a fixed sailing corridor "
            "east of the farm, because small-boat cod fishing would otherwise "
            "be squeezed into the heavy ferry lane to Gothenburg. The company "
            "has now drawn a 700-metre passage on the updated charts and "
            "promises AIS monitoring for the first two operating years. "
            "Opinion on Frederikshavn council is split. The Social Democrats "
            "and SF see the farm as a replacement for yard jobs lost in the "
            "2010s, while Venstre wants a clear plan for expanding the "
            "service harbour without eating the last leisure-boat land. "
            "Mayor Ida Slot says the municipality will only decide on a "
            "harbour expansion once there is a binding timeline for "
            "foundations and landfall. Energinet stresses that the cable "
            "itself can be buried in an existing 2018 corridor, so new "
            "trenches through eelgrass will not be opened within the first "
            "two kilometres of the coast. If the schedule holds, the first "
            "components will be unloaded in the October pause between autumn "
            "storms, and grid connection is set for the third quarter of the "
            "following year. A working group with the tourist board will at "
            "the same time find a kayak route so the farm does not cut the "
            "popular trip to Deget. Those are the kinds of considerations "
            "that at other Danish farms only arrived after commissioning, "
            "which is why Nordvind is writing them into the tender now."
        ),
        "english_summary": (
            "Energinet has approved the landfall cable for 28 turbines north "
            "of Frederikshavn. Fishers get a 700-metre corridor; the town "
            "still argues over a service-harbour expansion."
        ),
        "danish_summary": (
            "Energinet har godkendt ilandføringskablet til 28 havvindmøller "
            "nord for Frederikshavn. Fiskerne får en 700 meter bred "
            "sejlkoridor, mens byrådet stadig strides om servicehavnen."
        ),
        "prediction": (
            "Nordvind Kattegat vil rejse 28 møller på 420 megawatt ved "
            "Frederikshavn, hvis Kystdirektoratet siger ja inden påske."
        ),
    },
    {
        "id": "da-007",
        "split": "validation",
        "danish_body": (
            "Brønderslev IF vandt lørdag pokalkvartfinalen over Hjørring 3-1 "
            "efter to mål af angriberen Sofie Dahl. Kampen blev spillet i "
            "regn på den nye kunstgræsbane, og hjemmeholdet havde overtaget "
            "fra start. Træner Mikkel Overgaard pegede efterfølgende på, "
            "at presset på Hjørrings venstre back var planlagt hele ugen."
        ),
        "english_body": (
            "Brønderslev IF won Saturday's cup quarter-final 3-1 over "
            "Hjørring after two goals from forward Sofie Dahl. The match "
            "was played in rain on the new artificial pitch, and the home "
            "side were on top from the start. Coach Mikkel Overgaard later "
            "said the pressure on Hjørring's left-back had been planned all "
            "week."
        ),
        "english_summary": (
            "Brønderslev IF beat Hjørring 3-1 in the cup quarter-final, with "
            "Sofie Dahl scoring twice."
        ),
        "danish_summary": (
            "Brønderslev IF vandt pokalkvartfinalen 3-1 over Hjørring, og "
            "Sofie Dahl scorede to mål."
        ),
        "prediction": (
            "Brønderslev slog Hjørring i pokalen, og Sofie Dahl blev "
            "matchvinder på kunstgræsset."
        ),
    },
    {
        "id": "da-008",
        "split": "train",
        "danish_body": (
            "Når Region Nordjylland næste år samler de medicinske sengeafsnit "
            "i Hjørring og Frederikshavn i én visiteret akutstruktur, sker "
            "det efter tre års debat om, hvorvidt de små indlæggelser i "
            "yderområderne kan holdes i live uden at tære på vagtberedskabet "
            "i Aalborg, og den rapport, som direktionen lagde frem i går, "
            "forsøger at svare ved at skille planlagte indlæggelser, "
            "korttidsobservation og egentlig intensiv overvågning ad, så "
            "en patient med lungebetændelse i Skagen ikke automatisk kører "
            "forbi det nærmeste sengeafsnit, mens en ustabil hjertepatient "
            "stadig skal have første vagt i Aalborg; sygeplejerskernes "
            "tillidsrepræsentant, Pernille Søndergaard, kalder skellet "
            "fornuftigt på papiret, men hun minder om, at det er de samme "
            "mennesker, der i dag dækker både observation og nattevagt, og "
            "at en ny struktur uden ekstra hænder derfor kun flytter "
            "presset, den fjerner det ikke, især ikke i uger hvor "
            "influenzaen tager fart og de pårørende i Sæby allerede nu "
            "oplever, at en ambulance først kommer efter anden "
            "prioritering; regionsrådet stemmer i februar, og indtil da "
            "holder forvaltningen åbne møder i både Hjørring, "
            "Frederikshavn og Brønderslev, fordi politikerne har lovet, "
            "at ingen senge lukkes på et lukket udvalgsmøde, og fordi "
            "erfaringen fra den forrige omstilling af fødselsområdet "
            "viste, at tilliden forsvinder hurtigere end en "
            "høringssvarfrist, hvis borgerne først læser beslutningen i "
            "avisen."
        ),
        "english_body": (
            "When the North Jutland Region next year merges the medical "
            "wards in Hjørring and Frederikshavn into one visited acute "
            "structure, it will be after three years of debate about "
            "whether short admissions in the outer areas can be kept alive "
            "without draining the on-call roster in Aalborg, and the report "
            "management presented yesterday tries to answer by separating "
            "planned admissions, short observation, and true intensive "
            "monitoring, so that a pneumonia patient in Skagen does not "
            "automatically drive past the nearest ward while an unstable "
            "cardiac patient still gets first call in Aalborg; nurses' "
            "shop steward Pernille Søndergaard calls the split sensible on "
            "paper, but she reminds the board that it is the same people "
            "who today cover both observation and night duty, and that a "
            "new structure without extra hands therefore only moves the "
            "pressure, it does not remove it, especially in weeks when "
            "influenza accelerates and relatives in Sæby already find that "
            "an ambulance arrives only after a second triage; the regional "
            "council votes in February, and until then the administration "
            "will hold open meetings in Hjørring, Frederikshavn and "
            "Brønderslev, because politicians promised that no beds would "
            "close in a closed committee meeting, and because the last "
            "reorganisation of maternity care showed that trust vanishes "
            "faster than a consultation deadline if residents first read "
            "the decision in the newspaper."
        ),
        "english_summary": (
            "North Jutland's plan to merge medical wards in Hjørring and "
            "Frederikshavn separates observation from intensive care, but "
            "nurses say staffing is unchanged. The council votes in February."
        ),
        "danish_summary": (
            "Region Nordjylland vil samle medicinske senge i Hjørring og "
            "Frederikshavn i én akutstruktur. Sygeplejerskerne advarer om, "
            "at bemandingen er den samme. Regionsrådet stemmer i februar."
        ),
        "prediction": (
            "Regionen samler sengeafsnit i Vendsyssel og lover åbne møder, "
            "før der lukkes senge i Hjørring og Frederikshavn."
        ),
    },
    {
        "id": "da-009",
        "split": "test",
        "danish_body": (
            "Rebild Kommune åbner i pinsen en ny vandrerute på 14 kilometer "
            "mellem Rold Skov og Thingbæk Kalkminer. Ruten er afmærket med "
            "gule prikker og føres uden om de mest sårbare anemonetæpper, "
            "efter Danmarks Naturfredningsforening havde klaget over et "
            "tidligere udkast, der skar gennem den gamle bøgebevoksning. "
            "Turistchef Karen Munk siger, at ruten skal sprede forårsgæsterne, "
            "så parkeringspladsen ved Rebild Bakker ikke igen overfyldes på "
            "store bededag. Der opsættes tre primitive lejrpladser med "
            "vandpost, men bål er kun tilladt i de eksisterende "
            "bålhuse. En app med offlinekort er klar i uge 18, og de "
            "første 2.000 trykte folder kommer i turistbureauet i Støvring."
        ),
        "english_body": (
            "In Whitsun, Rebild Municipality will open a new 14-kilometre "
            "walking route between Rold Forest and Thingbæk Lime Mines. The "
            "path is marked with yellow dots and is routed around the most "
            "fragile anemone beds after the Danish Society for Nature "
            "Conservation complained that an earlier draft cut through the "
            "old beech stand. Tourism manager Karen Munk says the route "
            "should spread spring visitors so the Rebild Hills car park is "
            "not overcrowded again on Great Prayer Day. Three primitive "
            "campsites with a water tap will be added, but fires are only "
            "allowed in the existing fire shelters. An app with offline maps "
            "is ready in week 18, and the first 2,000 printed leaflets will "
            "sit in the Støvring tourist office."
        ),
        "english_summary": (
            "Rebild will open a 14-kilometre Whitsun walking route from Rold "
            "Forest to Thingbæk, rerouted to spare the anemone beds."
        ),
        "danish_summary": (
            "Rebild åbner i pinsen en 14 kilometer lang vandrerute mellem "
            "Rold Skov og Thingbæk Kalkminer. Linjeføringen er ændret for at "
            "skåne anemonerne."
        ),
        "prediction": (
            "Ny vandrerute i Rebild skal lette presset på bakkerne i pinsen "
            "og får tre lejrpladser uden åbne bål."
        ),
    },
    {
        "id": "da-010",
        "split": "test",
        "danish_body": (
            "Forskere på Aalborg Universitet har i et treårigt feltstudie "
            "målt, hvordan ålegræsset i Limfjorden reagerer på de varme "
            "somre siden 2021. Resultatet, som offentliggøres i tidsskriftet "
            "Marine Ecology Progress Series, viser at tætheden er faldet med "
            "18 procent på de lave banker vest for Egholm, mens de dybere "
            "enge nord for Nibe er næsten uændrede. Lektor Majken Ottosen "
            "siger, at forskellen sandsynligvis skyldes iltsvind tæt på "
            "overfladen og ikke trawl, som ellers ofte bliver nævnt i den "
            "lokale debat. Studien anbefaler, at kommunen udskyder en planlagt "
            "udvidelse af lystbådehavnen, indtil der er lagt et bælte af "
            "nye skud ud som forsøg. Havneudvalget har bedt om et notat "
            "inden budgetseminaret i september. Ottosen understreger, at "
            "ålegræsset stadig kan komme igen, hvis de varme perioder ikke "
            "følges af flere år med lav vandudskiftning."
        ),
        "english_body": (
            "Researchers at Aalborg University have spent a three-year field "
            "study measuring how eelgrass in the Limfjord responds to the "
            "warm summers since 2021. The result, published in Marine "
            "Ecology Progress Series, shows density has fallen 18 percent on "
            "the shallow banks west of Egholm, while the deeper meadows "
            "north of Nibe are almost unchanged. Associate professor Majken "
            "Ottosen says the difference is likely caused by oxygen depletion "
            "near the surface and not by trawling, which is otherwise often "
            "blamed in the local debate. The study recommends that the city "
            "postpone a planned marina expansion until a belt of new shoots "
            "has been planted as a trial. The harbour committee has asked "
            "for a briefing before the September budget seminar. Ottosen "
            "stresses that the eelgrass can still recover if the warm spells "
            "are not followed by several years of low water exchange."
        ),
        "english_summary": (
            "Aalborg University reports an 18 percent eelgrass loss on "
            "shallow Limfjord banks since 2021 and links it to surface "
            "oxygen depletion rather than trawling."
        ),
        "danish_summary": (
            "Ålegræsset på de lave banker vest for Egholm er faldet med 18 "
            "procent siden 2021, viser et AAU-studie. Forskerne peger på "
            "iltsvind, ikke trawl."
        ),
        "prediction": (
            "AAU-forskere finder mindre ålegræs i Limfjorden efter varme "
            "somre og beder kommunen vente med lystbådehavnen."
        ),
    },
]


def articles_by_id() -> dict[str, SampleArticle]:
    return {article["id"]: article for article in ARTICLES}


def split_rows(split: str) -> list[SampleArticle]:
    return [article for article in ARTICLES if article["split"] == split]
