"""Original sample articles for the offline examples.

Every body, translation and summary here is invented for this repository.
They are not scraped from TV2 Nord or any other news site. Place names
such as Østerhavn, Klitvig and Bøgebro are fictional.

The English ``translated`` / ``summary_en`` fields are hand-written, not
model output. They exist so the example CSVs can show the four pipeline
schemas without downloading OPUS-MT or T5.
"""

from __future__ import annotations

from typing import TypedDict


class SampleArticle(TypedDict):
    id: str
    split: str
    body_da: str
    body_en: str
    summary_en: str
    summary_da: str


SAMPLES: list[SampleArticle] = [
    {
        "id": "ex-001-laesehave",
        "split": "train",
        "body_da": (
            "Biblioteket i Østerhavn åbnede lørdag en ny læsehave bag den gamle "
            "stationsbygning. Haven er anlagt med lave bænke, læhegn af pil og en "
            "lille scene til højtlæsning. Bibliotekschef Maja Holm sagde, at "
            "projektet kom efter mange ønsker fra både børnefamilier og ældre "
            "læsere, som gerne vil læse udendørs, når vejret tillader det. "
            "Kommunen har støttet anlægget med 340.000 kroner, mens en lokal fond "
            "har betalt beplantningen. Allerede den første weekend kom over 200 "
            "gæster forbi, og flere børn deltog i en skattejagt mellem buskene. "
            "Holm håber, at haven kan bruges til klubmøder og små koncerter i "
            "sommersæsonen. Cafeen inde i biblioteket sælger kaffe ud gennem et "
            "nyt lugevindue, så gæster kan sidde ude uden at forlade bøgerne."
        ),
        "body_en": (
            "The library in Osterhavn opened a new reading garden behind the old "
            "station building on Saturday. The garden has low benches, willow "
            "windbreaks and a small stage for reading aloud. Library director "
            "Maja Holm said the project followed many requests from families "
            "with children and older readers who want to read outdoors when the "
            "weather allows. The municipality supported the construction with "
            "340,000 kroner, while a local foundation paid for the plants. More "
            "than 200 visitors came by the first weekend, and several children "
            "joined a treasure hunt among the bushes. Holm hopes the garden can "
            "host club meetings and small concerts in the summer season. The "
            "cafe inside the library now sells coffee through a new hatch so "
            "guests can sit outside without leaving their books."
        ),
        "summary_en": (
            "Osterhavn library opened an outdoor reading garden funded by the "
            "municipality and a local foundation, drawing more than 200 visitors "
            "on its first weekend."
        ),
        "summary_da": (
            "Biblioteket i Østerhavn har åbnet en udendørs læsehave støttet af "
            "kommunen og en lokal fond, og over 200 gæster kom den første weekend."
        ),
    },
    {
        "id": "ex-002-faerge",
        "split": "train",
        "body_da": (
            "Aftenfærgen til øen Gråholm blev aflyst onsdag på grund af "
            "sydvestlig storm og høje bølger i sundet. Rederiet Klitvig Færger "
            "oplyste, at vindstødene ramte ca. 28 meter i sekundet, og at "
            "kaptajnen derfor droppede den sidste tur kl. 21.15. Omkring 60 "
            "passagerer ventede i terminalen, heriblandt elever fra efterskolen "
            "på øen. Selskabet satte en ekstra morgenafgang ind torsdag kl. 6.40 "
            "og tilbød overnatning i en idrætshal til dem, der ikke kunne nå "
            "hjem. Havnefoged Erik Nissen sagde, at broen ved færgelejet også "
            "fik skader på to fendere, som skal skiftes før weekendens drift. "
            "Meteorologerne venter, at vinden løjer af i løbet af natten, men "
            "advarer stadig om glatte trapper på kajen. Næste ordinære afgange "
            "kører efter planen, hvis tilsynet godkender reparationerne."
        ),
        "body_en": (
            "The evening ferry to the island of Graaholm was cancelled on "
            "Wednesday because of a south-westerly storm and high waves in the "
            "sound. The operator Klitvig Ferries said gusts reached about 28 "
            "metres per second, so the captain dropped the last sailing at 21:15. "
            "About 60 passengers waited in the terminal, including students from "
            "the island boarding school. The company added an extra Thursday "
            "departure at 06:40 and offered beds in a sports hall for people "
            "who could not get home. Harbour master Erik Nissen said two fenders "
            "on the ferry berth were damaged and must be replaced before weekend "
            "service. Forecasters expect the wind to ease overnight but still "
            "warn about slippery quay stairs. Regular sailings resume if "
            "inspectors approve the repairs."
        ),
        "summary_en": (
            "Storm-force gusts cancelled the evening ferry to Graaholm; the "
            "operator added a dawn sailing and will repair damaged berth fenders "
            "before the weekend."
        ),
        "summary_da": (
            "Stormen aflyste aftenfærgen til Gråholm; rederiet indsætter en "
            "ekstra morgentur og reparerer beskadigede fendere før weekenden."
        ),
    },
    {
        "id": "ex-003-ungdomsfodbold",
        "split": "train",
        "body_da": (
            "Bøgebro IFs U15-piger vandt lørdag kredsfinalen med 3-1 over "
            "Havnkær og tager dermed pokalen med hjem for første gang siden 2018. "
            "Målene kom efter en hjørnesituation, et langskud fra kaptajn Sofie "
            "Ravn og et sent indlæg, som Amalie Krog headede ind. Træner Kim "
            "Frost pegede på, at holdet har trænet omstillinger hele efteråret, "
            "og at det kunne ses i de to sidste scoring. Omkring 400 tilskuere "
            "stod langs banen ved kommunens nye kunstgræs, og klubben serverede "
            "kakao i et telt bag målet. Formand Lene Dam takkede de frivillige "
            "og sagde, at pokalen skal stå i klubhuset ved siden af drengeholdets "
            "trofæ fra foråret. Næste opgave er et stævne i Aalborg, hvor "
            "Bøgebro møder tre klubber fra nabokredsen. Ravn håber, at flere "
            "piger fra skolen vil tilmelde sig vinterholdet efter sejren."
        ),
        "body_en": (
            "Boogebro IF's U15 girls won Saturday's district final 3-1 against "
            "Havnkaer and take the cup home for the first time since 2018. The "
            "goals came from a corner, a long shot by captain Sofie Ravn and a "
            "late cross that Amalie Krog headed in. Coach Kim Frost said the "
            "team spent the autumn training transitions, and that it showed in "
            "the last two goals. About 400 spectators lined the municipal "
            "artificial pitch, and the club served cocoa in a tent behind the "
            "goal. Chair Lene Dam thanked the volunteers and said the cup will "
            "stand in the clubhouse next to the boys' trophy from the spring. "
            "Next up is a tournament in Aalborg against three clubs from the "
            "neighbouring district. Ravn hopes more girls from the school will "
            "join the winter squad after the win."
        ),
        "summary_en": (
            "Boogebro IF's U15 girls beat Havnkaer 3-1 to win their first "
            "district cup since 2018 in front of about 400 spectators."
        ),
        "summary_da": (
            "Bøgebro IFs U15-piger vandt 3-1 over Havnkær og tog den første "
            "kredspokal siden 2018 foran omkring 400 tilskuere."
        ),
    },
    {
        "id": "ex-004-bageri",
        "split": "validation",
        "body_da": (
            "Bageriet Rug og Rav i Klitvig har i tre uger solgt brød bagt på "
            "ølandshvede og svedjerug fra en gård uden for Bøgebro. Bagermester "
            "Jonas Pihl siger, at de gamle kornsorter kræver længere hævetid, "
            "men giver en syrligere krumme og bedre holdbarhed. Gården leverer "
            "ca. 400 kilo mel om måneden, og mølleren maler det på stenkværn "
            "tirsdag morgen, så det er friskt til weekendens hold. Flere "
            "kunder har spurgt efter opskrifter, derfor hænger der nu et kort "
            "med bagetider ved disken. Pihl understreger, at prisen er 6 kroner "
            "højere end det almindelige rugbrød, fordi udbyttet pr. hektar er "
            "lavere. Hvis efterspørgslen holder frem til jul, vil bageriet "
            "udvide med en knækbrødslinje på samme mel. Kommunens "
            "erhvervsråd har besøgt værkstedet og taler om et lille "
            "fødevarespor for turister langs havnen."
        ),
        "body_en": (
            "The bakery Rug og Rav in Klitvig has spent three weeks selling "
            "bread made with heirloom wheat and slash-and-burn rye from a farm "
            "outside Boogebro. Baker Jonas Pihl says the older grains need a "
            "longer rise but give a more sour crumb and better keeping quality. "
            "The farm delivers about 400 kilos of flour a month, and the miller "
            "stones it on Tuesday morning so it is fresh for the weekend bake. "
            "Several customers asked for recipes, so a card with baking times "
            "now hangs by the counter. Pihl notes that the loaf costs 6 kroner "
            "more than ordinary rye bread because the yield per hectare is "
            "lower. If demand holds through Christmas the bakery will add a "
            "crispbread line on the same flour. The municipal business council "
            "visited the workshop and is talking about a small food trail for "
            "tourists along the harbour."
        ),
        "summary_en": (
            "A Klitvig bakery is selling loaves from local heirloom grains and "
            "may add crispbread if Christmas demand holds."
        ),
        "summary_da": (
            "Bageriet Rug og Rav i Klitvig sælger brød af lokale oldtidskorn og "
            "overvejer knækbrød, hvis julehandlen holder."
        ),
    },
    {
        "id": "ex-005-cykelsti",
        "split": "test",
        "body_da": (
            "Teknisk udvalg i Østerhavn har vedtaget at forlænge cykelstien "
            "mellem skolen og havnen med 1,2 kilometer. Strækningen får hævet "
            "kantsten, ny belysning og to krydsningsheller ved Industrivej, "
            "hvor forældre i årevis har klaget over biler, der svinger uden at "
            "se. Budgettet er 4,8 millioner kroner, og anlægsarbejdet skal "
            "begynde i marts, når frostperioden efter planen er ovre. "
            "Formand for udvalget, Pernille Søe, sagde, at målet er at få flere "
            "elever til at cykle hele året, ikke kun i maj. Naboerne ved "
            "Stationsvænget får en midlertidig gangbro, mens gravemaskinerne "
            "arbejder, og buslinje 3 omlægges i tre uger. En gruppe beboere "
            "havde ønsket asfalt helt ind til kirkegården, men det forslag "
            "rykker til næste års budgetforhandling. Søe lovede en "
            "borgermødeaften i februar, hvor entreprenøren viser afspærringsplanen."
        ),
        "body_en": (
            "The technical committee in Osterhavn has voted to extend the cycle "
            "path between the school and the harbour by 1.2 kilometres. The "
            "stretch will get raised kerbs, new lighting and two refuge islands "
            "at Industrivej, where parents have long complained about turning "
            "cars. The budget is 4.8 million kroner, and construction should "
            "start in March once the frost period is over. Committee chair "
            "Pernille Soee said the aim is to get more pupils cycling all year, "
            "not only in May. Neighbours on Stationsvaenget will have a "
            "temporary footbridge while the excavators work, and bus line 3 "
            "will be diverted for three weeks. A residents' group wanted asphalt "
            "all the way to the cemetery, but that request moves to next year's "
            "budget talks. Soee promised a public meeting in February where the "
            "contractor will show the road-closure plan."
        ),
        "summary_en": (
            "Osterhavn will extend the school-to-harbour cycle path by 1.2 km "
            "from March, with new lighting and crossing islands at Industrivej."
        ),
        "summary_da": (
            "Østerhavn forlænger cykelstien mellem skole og havn med 1,2 km fra "
            "marts og sætter ny belysning og hellere ved Industrivej."
        ),
    },
    {
        "id": "ex-006-havn",
        "split": "train",
        "body_da": (
            "Klitvig Havn indledte mandag den største renovering i 40 år, da "
            "gravemaskinerne kørte ud på den indre mole. Projektet skal "
            "udskifte spunsvægge, hæve kajkanten med 40 centimeter og lægge ny "
            "strøm til fiskekutterne, der stadig lander jomfruhummer om natten. "
            "Havnedirektør Astrid Vestergaard forklarede, at stormfloden sidste "
            "efterår stod helt op i pakhuset, og at forsikringen krævede en "
            "varig løsning før næste vintersæson. Anlægsbudgettet er 62 "
            "millioner kroner. Staten betaler godt halvdelen gennem en pulje "
            "til yderhavne, mens kommunen og et andelsselskab af fiskere dækker "
            "resten. I de første seks uger er den vestlige kaj spærret, så "
            "lystbåde henvises til gæstepladser i Østerhavn. Fiskeauktionen "
            "flytter midlertidigt ind i en telthal bag frysehuset, og lastbiler "
            "skal køre en omvej ad Strandgade. Flere handlende i Havnegade "
            "frygter færre kunder i april, derfor har turistforeningen lovet "
            "skilte, der viser, at røgeriet og caféen stadig er åbne. "
            "Entreprenøren, et konsortium fra Aalborg, arbejder i daghold og "
            "et kortere aftenhold for at nå spunsen, før yngletiden for terner "
            "på den ydre ø begynder. Biologer fra nationalparken har sat "
            "vilkår om, at ramningen holder pause, hvis en odder observeres i "
            "bassinet. Vestergaard sagde, at havnen også får en ny "
            "affaldsstation til net og oliefiltre, så fiskerne ikke længere "
            "skal køre til genbrugspladsen i Bøgebro. Når kajen er færdig i "
            "oktober, skal der lægges granitbelægning og lave bænke vendt mod "
            "sundet. Skolerne i området er inviteret til at følge arbejdet med "
            "en undervisningsuge om klima og kystsikring. En model af den "
            "færdige havn står allerede i biblioteket, og flere ældre "
            "beboere har genkendt deres gamle kuttere på tegningen. "
            "Hvis tidsplanen holder, åbner en lille udsigtsbro samtidig med "
            "hummerfestivalen, så gæster kan se ned i slusen uden at gå ud på "
            "arbejdsområdet. Kommunen understreger, at lystfiskeri fra den ydre "
            "mole kan fortsætte, så længe folk holder sig bag de røde hegn. "
            "Næste offentlige statusmøde er sat til den 3. april i pakhus 2."
        ),
        "body_en": (
            "Klitvig Harbour began its largest renovation in 40 years on Monday "
            "when excavators rolled onto the inner breakwater. The project will "
            "replace sheet-pile walls, raise the quay by 40 centimetres and lay "
            "new power for the fishing boats that still land Norway lobster at "
            "night. Harbour director Astrid Vestergaard explained that last "
            "autumn's storm surge reached the warehouse, and the insurer "
            "demanded a lasting fix before the next winter season. The "
            "construction budget is 62 million kroner. The state pays just over "
            "half through a fund for outer harbours, while the municipality and "
            "a fishers' cooperative cover the rest. For the first six weeks the "
            "western quay is closed, so pleasure boats are sent to guest berths "
            "in Osterhavn. The fish auction moves temporarily into a tent hall "
            "behind the freezer plant, and lorries must detour along Strandgade. "
            "Several shopkeepers on Havnegade fear fewer customers in April, so "
            "the tourist office promised signs that the smokehouse and cafe are "
            "still open. The contractor, a consortium from Aalborg, works a day "
            "shift and a shorter evening shift to finish the piling before the "
            "tern breeding season starts on the outer islet. Biologists from the "
            "national park required a halt to pile-driving if an otter is seen "
            "in the basin. Vestergaard said the harbour will also get a new "
            "waste station for nets and oil filters so fishers no longer drive "
            "to the recycling site in Boogebro. When the quay is finished in "
            "October, granite paving and low benches facing the sound will be "
            "installed. Local schools are invited to follow the work with a "
            "teaching week on climate and coastal protection. A model of the "
            "finished harbour already stands in the library, and several older "
            "residents have recognised their old cutters on the drawing. If the "
            "schedule holds, a small viewing bridge opens with the lobster "
            "festival so visitors can look into the lock without entering the "
            "work zone. The municipality stresses that angling from the outer "
            "breakwater can continue as long as people stay behind the red "
            "fences. The next public status meeting is set for 3 April in "
            "warehouse 2."
        ),
        "summary_en": (
            "Klitvig Harbour has started a 62 million kroner renovation to raise "
            "the quay and replace sheet piles after last year's storm surge, "
            "with the western berth closed for six weeks."
        ),
        "summary_da": (
            "Klitvig Havn er begyndt en renovering til 62 millioner kroner, der "
            "hæver kajen og skifter spunsvægge efter stormfloden, mens den "
            "vestlige kaj er spærret i seks uger."
        ),
    },
]


def by_id() -> dict[str, SampleArticle]:
    return {row["id"]: row for row in SAMPLES}


def ids_for_split(split: str) -> list[str]:
    return [row["id"] for row in SAMPLES if row["split"] == split]
