"""Hand-authored fixture articles for the CPU examples.

These texts are original and fictional. They exist so the chunker, schema
checks, and dry-run pipeline can run without the 10k-article scrape or any
translation checkpoint. English fields are human translations, not model
output. The Danish `summary` fields are silver-style (shorter, slightly
lossy) while `reference` fields are independent gold-style headlines.
"""

from __future__ import annotations

from typing import TypedDict


class FixtureArticle(TypedDict):
    id: str
    title: str
    article_text: str
    translated: str
    summary_en: str
    summary_da: str
    reference_da: str


ARTICLES: list[FixtureArticle] = [
    {
        "id": "wx-aarhus",
        "title": "Regn letter over Aarhus",
        "article_text": (
            "Efter flere dages regn letter skyerne over Aarhus i eftermiddag. "
            "Ifølge kommunen bliver vejene i midtbyen spulet i løbet af natten, "
            "og cykelstierne langs åen åbner igen i morgen tidlig. "
            "Beredskabet advarer stadig om glatte brosten ved Immervad."
        ),
        "translated": (
            "After several days of rain the clouds lift over Aarhus this afternoon. "
            "According to the municipality the streets in the city centre will be "
            "flushed overnight, and the cycle paths along the stream reopen early "
            "tomorrow morning. Emergency services still warn about slippery cobbles "
            "at Immervad."
        ),
        "summary_en": (
            "Clouds lift over Aarhus after days of rain. The municipality will flush "
            "city-centre streets overnight and reopen cycle paths in the morning."
        ),
        "summary_da": (
            "Skyerne letter over Aarhus efter flere dages regn. Kommunen spuler "
            "vejene i nat og åbner cykelstierne igen i morgen."
        ),
        "reference_da": (
            "Aarhus letter efter regn: veje spules i nat, cykelstier åbner i morgen."
        ),
    },
    {
        "id": "museum-aalborg",
        "title": "Ny udstilling på Aalborg Historiske Museum",
        "article_text": (
            "Aalborg Historiske Museum åbner i næste uge en ny udstilling om "
            "havnefrontens industrihistorie. Udstillingen rummer blandt andet "
            "fotografier fra 1920'erne, arbejdstøj og mundtlige erindringer fra "
            "tidligere værftsarbejdere. Ifølge museet er mellem 8.000 og 10.000 "
            "gæster ventet i løbet af de første tre måneder. Skoletjenesten tilbyder "
            "omvisninger tirsdag og torsdag, og der er gratis adgang den første søndag. "
            "En del af genstandene har ikke været fremme siden værftet lukkede."
        ),
        "translated": (
            "Aalborg Historical Museum opens a new exhibition next week about the "
            "waterfront's industrial history. The exhibition includes photographs from "
            "the 1920s, workwear and oral recollections from former shipyard workers. "
            "According to the museum, between 8,000 and 10,000 visitors are expected "
            "during the first three months. The education service offers tours on "
            "Tuesday and Thursday, and admission is free on the first Sunday. Some of "
            "the objects have not been shown since the shipyard closed."
        ),
        "summary_en": (
            "Aalborg Historical Museum opens a waterfront industry exhibition next week, "
            "expecting up to 10,000 visitors in three months."
        ),
        "summary_da": (
            "Aalborg Historiske Museum åbner næste uge en udstilling om havnens "
            "industrihistorie og venter op til 10.000 gæster på tre måneder."
        ),
        "reference_da": (
            "Ny industriudstilling i Aalborg venter op til 10.000 gæster."
        ),
    },
    {
        "id": "harbour-plan",
        "title": "Plan for den nye indre havn",
        "article_text": (
            "Den nye indre havn i Aalborg skal omdannes fra industriareal til "
            "bykvarter i løbet af de næste otte år. Kommunalbestyrelsen vedtog i går "
            "at sende planen i offentlig høring, efter at et flertal i byrådet havde "
            "forhandlet om boligandelen i flere uger. Planen rummer omkring 1.200 "
            "boliger, to daginstitutioner, et bibliotek og et sammenhængende stisystem "
            "langs vandet. Den kommunale forvaltning vurderer, at anlægsudgifterne "
            "lander tæt på 1,8 mia. kr., hvoraf staten kan dække en mindre del. "
            "Havnefronten i Aalborg har i årtier været præget af kraner, siloer og "
            "tung trafik, og naboerne har længe krævet bedre adgang til fjorden. "
            "I den nye plan lægges der op til, at mindst 40 procent af stueetagerne "
            "skal rumme butikker, værksteder eller kultur. Forskerne ved Aalborg "
            "Universitet har bidraget med analyser af stormflod og grundvand, og de "
            "anbefaler, at boliger hæves mindst 1,2 meter over nuværende kajkant. "
            "Ifølge kommunen bliver der holdt borgermøde i Nordkraft den 12. oktober "
            "kl. 19. Kritikere mener, at tempoet er for højt, og at billige boliger "
            "risikerer at blive skrevet ud af projektet. Tilhængere peger på, at den "
            "grønne omstilling også handler om at bygge tættere, så flere kan cykle "
            "til arbejde. En række lokale foreninger kræver, at den gamle slæbested "
            "bevares som historisk spor. Politiet har ikke bemærkninger til trafikken "
            "i anlægsfasen, men anbefaler en midlertidig cykelomkørsel. Næste skridt "
            "er en miljøvurdering, som skal være færdig, før byrådet kan vedtage den "
            "endelige lokalplan. Indtil da ligger de gamle kajanlæg åbne som "
            "rekreativt område i weekenderne."
        ),
        "translated": (
            "The new inner harbour in Aalborg is to be converted from industrial land "
            "into a city district over the next eight years. The city council adopted "
            "yesterday to send the plan into public consultation, after a majority on "
            "the council had negotiated the housing share for several weeks. The plan "
            "contains around 1,200 homes, two nurseries, a library and a connected path "
            "system along the water. The municipal administration estimates construction "
            "costs close to 1.8 billion kroner, of which the state may cover a smaller "
            "share. The waterfront in Aalborg has for decades been marked by cranes, "
            "silos and heavy traffic, and neighbours have long demanded better access "
            "to the fjord. The new plan proposes that at least 40 percent of ground "
            "floors should hold shops, workshops or culture. Researchers at Aalborg "
            "University have contributed analyses of storm surge and groundwater, "
            "and they recommend raising homes at least 1.2 metres above the current "
            "quay. According to the municipality a public meeting will be held at "
            "Nordkraft on 12 October at 19:00. Critics say the pace is too high and "
            "that inexpensive homes risk being written out of the project. "
            "Supporters argue that the green transition also means building more densely "
            "so more people can cycle to work. Several local associations demand that "
            "the old slipway be kept as a historic trace. The police have no remarks "
            "on traffic during construction but recommend a temporary cycle diversion. "
            "The next step is an environmental assessment, which must be finished before "
            "the council can adopt the final local plan. Until then the old quays stay "
            "open as a recreational area at weekends."
        ),
        "summary_en": (
            "Aalborg will turn the inner harbour into a district with 1,200 homes. "
            "The plan, estimated at 1.8 billion kroner, is now in public consultation, "
            "with a meeting at Nordkraft on 12 October."
        ),
        "summary_da": (
            "Aalborg omdanner den indre havn til bykvarter med 1.200 boliger. "
            "Planen til 1,8 mia. kr. er i offentlig høring, og der holdes borgermøde "
            "i Nordkraft den 12. oktober."
        ),
        "reference_da": (
            "Aalborg sender havneplan med 1.200 boliger og 1,8 mia. kr. i høring."
        ),
    },
    {
        "id": "superliga-aab",
        "title": "AaB vinder på hjemmebane",
        "article_text": (
            "AaB vandt 2-1 over Randers på hjemmebane lørdag aften og rykker dermed "
            "op på fjerdepladsen i Superligaen. Målene faldt i det 14. og det 71. "
            "minut, og ifølge klubben var der 11.400 tilskuere i Aalborg Portland "
            "Park. Træneren fremhævede det unge midtbanespil, mens Randers-træneren "
            "beklagede et dømt straffespark i anden halvleg. Næste kamp er ude mod "
            "Viborg onsdag."
        ),
        "translated": (
            "AaB won 2-1 against Randers at home on Saturday evening and therefore "
            "move up to fourth place in the Superliga. The goals came in the 14th and "
            "71st minutes, and according to the club there were 11,400 spectators at "
            "Aalborg Portland Park. The manager highlighted the young midfield play, "
            "while the Randers manager regretted a penalty awarded in the second half. "
            "The next match is away against Viborg on Wednesday."
        ),
        "summary_en": (
            "AaB beat Randers 2-1 at home and climb to fourth in the Superliga, "
            "watched by 11,400 at Aalborg Portland Park."
        ),
        "summary_da": (
            "AaB vandt 2-1 over Randers og er nu nummer fire i Superligaen efter "
            "11.400 tilskuere i Aalborg."
        ),
        "reference_da": "AaB slår Randers 2-1 og tager fjerdepladsen i Superligaen.",
    },
    {
        "id": "offshore-wind",
        "title": "Havvind ud for Nordjylland",
        "article_text": (
            "En ny havvindmøllepark ud for Nordjylland kan levere strøm svarende til "
            "180.000 husstande, vurderer forskere ved Aalborg Universitet. Projektet "
            "indgår i den grønne omstilling og skal i offentlig høring i oktober. "
            "Kommunen understreger, at fiskeri og fugletræk indgår i "
            "konsekvensanalysen. Anlægsarbejdet tidligst i 2028, og kablerne kommer "
            "i land ved et eksisterende transformeranlæg. Ifølge forskerne kan parken "
            "også levere systemydelser, når solen ikke skinner."
        ),
        "translated": (
            "A new offshore wind farm off North Jutland can supply electricity equal "
            "to 180,000 households, researchers at Aalborg University estimate. The "
            "project is part of the green transition and will go to public consultation "
            "in October. The municipality stresses that fisheries and bird migration "
            "are included in the impact analysis. Construction is at the earliest in "
            "2028, and the cables come ashore at an existing transformer station. "
            "According to the researchers the farm can also provide grid services when "
            "the sun is not shining."
        ),
        "summary_en": (
            "An offshore wind farm off North Jutland could power 180,000 homes. "
            "It goes to consultation in October, with construction no earlier than 2028."
        ),
        "summary_da": (
            "En havvindmøllepark ud for Nordjylland kan dække 180.000 husstande. "
            "Projektet går i høring i oktober, og anlæg tidligst i 2028."
        ),
        "reference_da": (
            "Nordjysk havvind kan dække 180.000 husstande og går i høring i oktober."
        ),
    },
    {
        "id": "library-budget",
        "title": "Biblioteket i Hjørring får flere timer",
        "article_text": (
            "Biblioteket i Hjørring får et løft på 4,5 mio. kr. i budgettet for 2024. "
            "Pengene går bl.a. til nye åbningstider, flere børnebøger og en læsesal, "
            "der ifølge kommunen kan rumme ca. 60 personer. Dr. Hansen, der leder "
            "biblioteket, siger, at udvidelsen sker pga. et stigende antal besøgende, "
            "f.eks. skoleklasser om formiddagen. Der åbnes hhv. mandag og onsdag til "
            "kl. 20, og lørdagsåbning forsøges i tre måneder. Kommunen noterer, at "
            "udgiften svarer til 0,3 pct. af kulturbudgettet, dvs. en mindre post "
            "sammenlignet med anlæg. Læsesalen får også stikkontakter og bedre lys, "
            "osv., hvis udbuddet går igennem inden jul."
        ),
        "translated": (
            "The library in Hjørring receives a 4.5 million kroner boost in the 2024 "
            "budget. The money goes among other things to new opening hours, more "
            "children's books and a reading room that according to the municipality can "
            "hold approximately 60 people. Dr Hansen, who leads the library, says the "
            "expansion happens because of a rising number of visitors, for example "
            "school classes in the morning. Opening is extended Monday and Wednesday "
            "respectively until 20:00, and Saturday opening will be trialled for "
            "three months. The municipality notes that the expense equals 0.3 "
            "percent of the culture budget, that is a small item compared with "
            "construction. The reading room also gets sockets and better lighting, "
            "and so on, if the tender goes through before Christmas."
        ),
        "summary_en": (
            "Hjørring library gets 4.5 million kroner in 2024 for longer hours, "
            "children's books and a 60-person reading room."
        ),
        "summary_da": (
            "Hjørring-biblioteket får 4,5 mio. kr. i 2024 til længere åbningstid, "
            "børnebøger og en læsesal til ca. 60 personer."
        ),
        "reference_da": (
            "Hjørring giver biblioteket 4,5 mio. kr. til aftenåbning og ny læsesal."
        ),
    },
    {
        "id": "harbour-runon",
        "title": "Én lang sætning om høringen",
        "article_text": (
            "Byrådet i Aalborg vedtog tirsdag aften efter tre timers debat og med et "
            "snævert flertal at sende den samlede plan for den nye indre havn, "
            "herunder cykelstier, boliger, en daginstitution og et kulturhus tæt på "
            "Limfjorden, i offentlig høring i otte uger, så borgere, erhvervsliv og "
            "foreninger kan komme med bemærkninger om trafik, skyggevirkning, "
            "skolestørrelser og bevarelse af den gamle slæbested, før "
            "kommunalbestyrelsen træffer endelig beslutning i december, og forvaltningen "
            "skal samtidig indhente en opdateret stormflodsanalyse fra universitetet."
        ),
        "translated": (
            "The city council in Aalborg adopted Tuesday evening after three hours of "
            "debate and with a narrow majority to send the overall plan for the new "
            "inner harbour, including cycle paths, housing, a nursery and a cultural "
            "house close to the Limfjord, into public consultation for eight weeks, so "
            "residents, businesses and associations can comment on traffic, shadow "
            "effects, school sizes and preservation of the old slipway, before the "
            "council takes a final decision in December, and the administration must at "
            "the same time obtain an updated storm-surge analysis from the university."
        ),
        "summary_en": (
            "Aalborg's council narrowly voted to put the inner-harbour plan into an "
            "eight-week consultation before a December decision."
        ),
        "summary_da": (
            "Byrådet i Aalborg sender med snævert flertal havneplanen i otte ugers "
            "høring inden beslutning i december."
        ),
        "reference_da": (
            "Snævert flertal sender Aalborgs havneplan i otte ugers offentlig høring."
        ),
    },
    {
        "id": "ferry-strike",
        "title": "Færgepersonale i strejke",
        "article_text": (
            "Strejken blandt færgepersonale i Kattegat betyder, at færgeafgangen fra "
            "Aalborg til øerne i Limfjorden indstilles indtil torsdag. Ifølge politiet "
            "opfordres pendlere til at køre via landjorden, og kommunen åbner et "
            "midlertidigt infopunkt ved havnen. Fagforeningen kræver en ny vagtplan og "
            "bedre hviletid, mens rederiet peger på aflyste afgange i høj sæson. "
            "Turistkontoret forventer færre overnatninger i weekenden, hvis strejken "
            "trækkes. Der sættes ekstra busser ind mellem Nørresundby og Hals."
        ),
        "translated": (
            "The strike among ferry staff in the Kattegat means that the ferry "
            "departure from Aalborg to the islands in the Limfjord is suspended until "
            "Thursday. According to the police, commuters are encouraged to travel by "
            "land, and the municipality is opening a temporary information point at "
            "the harbour. The union demands a new shift plan and better rest time, "
            "while the ferry company points to cancelled sailings in high season. "
            "The tourist office expects fewer overnight stays this weekend if the "
            "strike is extended. Extra buses will run between Nørresundby and Hals."
        ),
        "summary_en": (
            "Ferry sailings from Aalborg on the Limfjord are cancelled until Thursday "
            "because of a staff strike, with extra buses on land routes."
        ),
        "summary_da": (
            "Færgeafgange fra Aalborg indstilles til torsdag på grund af strejke, "
            "og kommunen sætter ekstra busser ind."
        ),
        "reference_da": (
            "Strejke standser Limfjordsfærger til torsdag; ekstra busser indsættes."
        ),
    },
]


def by_id() -> dict[str, FixtureArticle]:
    return {article["id"]: article for article in ARTICLES}
