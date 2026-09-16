"""Vesterklit Gazette: a closed-world municipal newsroom.

Every article is invented. Place names, people, and institutions do not
refer to a real Danish municipality. The stories exist so the 2023 hop
shape can be walked on a laptop without scraping Nordjyske or pulling
the public Nordjylland summarisation set.

Sentence lists are 1:1 aligned. That alignment is the oracle translator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


@dataclass(frozen=True)
class GazetteArticle:
    article_id: str
    title_da: str
    title_en: str
    danish_sentences: Tuple[str, ...]
    english_sentences: Tuple[str, ...]
    gold_da_summary: str
    gold_en_summary: str
    entities: Tuple[str, ...]
    facts: Tuple[str, ...]
    section: str

    @property
    def danish(self) -> str:
        return " ".join(self.danish_sentences)

    @property
    def english(self) -> str:
        return " ".join(self.english_sentences)

    def validate(self) -> None:
        if len(self.danish_sentences) != len(self.english_sentences):
            raise ValueError(
                f"{self.article_id}: alignment broken "
                f"({len(self.danish_sentences)} vs {len(self.english_sentences)})"
            )
        if not self.danish_sentences:
            raise ValueError(f"{self.article_id}: empty article")
        if not self.gold_da_summary or not self.gold_en_summary:
            raise ValueError(f"{self.article_id}: missing gold summary")
        if not self.entities:
            raise ValueError(f"{self.article_id}: missing entity list")


def _a(
    article_id: str,
    title_da: str,
    title_en: str,
    pairs: Sequence[Tuple[str, str]],
    gold_da_summary: str,
    gold_en_summary: str,
    entities: Sequence[str],
    facts: Sequence[str],
    section: str,
) -> GazetteArticle:
    da, en = zip(*pairs) if pairs else ((), ())
    art = GazetteArticle(
        article_id=article_id,
        title_da=title_da,
        title_en=title_en,
        danish_sentences=tuple(da),
        english_sentences=tuple(en),
        gold_da_summary=gold_da_summary,
        gold_en_summary=gold_en_summary,
        entities=tuple(entities),
        facts=tuple(facts),
        section=section,
    )
    art.validate()
    return art


ARTICLES: Tuple[GazetteArticle, ...] = (
    _a(
        "vk-001",
        "Stormen Nanna aflyser færgen til Mågeø",
        "Storm Nanna cancels the ferry to Mågeø",
        [
            (
                "Stormen Nanna tvang i nat Færgeselskabet Vesterklit til at aflyse alle afgange mellem Havnepladsen og Mågeø.",
                "Storm Nanna forced the Vesterklit ferry company last night to cancel all departures between Havnepladsen and Mågeø.",
            ),
            (
                "Direktør Lisbeth Holm sagde, at bølgerne ved Sølvdyp målte over fire meter, og at mandskabet ikke kunne sikre fortøjningen.",
                "Director Lisbeth Holm said that the waves at Sølvdyp measured over four metres, and that the crew could not secure the mooring.",
            ),
            (
                "Kommunen åbner midlertidigt et venteskur på kajen, hvor passagerer kan få kaffe og opdateringer hver halve time.",
                "The municipality is temporarily opening a shelter on the quay, where passengers can get coffee and updates every half hour.",
            ),
            (
                "Næste vurdering sker klokken 06.00, når beredskabet har nye tal for vinden.",
                "The next assessment happens at 06.00, when the emergency service has new figures for the wind.",
            ),
            (
                "Skoleelever fra Nordmark, der skulle til svømmestævne, bliver kørt med bus via Brohuset i stedet.",
                "Schoolchildren from Nordmark, who were going to a swim meet, will be driven by bus via Brohuset instead.",
            ),
            (
                "Fjordpressen følger ruten gennem natten og lægger nye tal på hjemmesiden, når Lisbeth Holm skriver igen.",
                "Fjordpressen will follow the route through the night and post new figures on the website when Lisbeth Holm writes again.",
            ),
        ],
        "Stormen Nanna aflyser færgen mellem Havnepladsen og Mågeø. Lisbeth Holm peger på fire meter høje bølger ved Sølvdyp. Kommunen åbner et venteskur, og skoleelever fra Nordmark kører via Brohuset.",
        "Storm Nanna cancels the ferry between Havnepladsen and Mågeø. Lisbeth Holm cites four-metre waves at Sølvdyp. The municipality opens a shelter, and Nordmark schoolchildren travel via Brohuset.",
        ("Nanna", "Vesterklit", "Havnepladsen", "Mågeø", "Lisbeth Holm", "Sølvdyp", "4", "06.00", "Nordmark", "Brohuset"),
        (
            "all ferry departures cancelled overnight",
            "waves over four metres at Sølvdyp",
            "next assessment at 06.00",
            "Nordmark pupils rerouted via Brohuset",
        ),
        "harbour",
    ),
    _a(
        "vk-002",
        "Testmast på Klitsand får betinget godkendelse",
        "Test mast at Klitsand gets conditional approval",
        [
            (
                "Teknisk forvaltning har givet betinget godkendelse til en 87 meter høj testmast på Klitsand.",
                "The technical department has given conditional approval to an 87-metre test mast at Klitsand.",
            ),
            (
                "Ingeniør Karsten Vang sagde, at masten skal måle vind i to år, før nogen taler om vindmøller.",
                "Engineer Karsten Vang said that the mast must measure wind for two years before anyone talks about wind turbines.",
            ),
            (
                "Naboerne på Rylevej har sendt 14 klager om støj og trækfugle, og klagerne følger med tilladelsen som vilkår.",
                "The neighbours on Rylevej have sent 14 complaints about noise and migratory birds, and the complaints travel with the permit as conditions.",
            ),
            (
                "Miljøvurderingen kræver, at master og kabler tages ned, hvis fugletællingen falder med over ti procent.",
                "The environmental review requires that masts and cables come down if the bird count falls by over ten percent.",
            ),
            (
                "Borgmester Ellen Buhl understregede, at projektet ikke er en hemmelig møllepark, men et målepunkt.",
                "Mayor Ellen Buhl stressed that the project is not a secret turbine park, but a measuring point.",
            ),
            (
                "Høringen slutter den 3. maj, og Fjordpressen lægger rapporten i læsesalen på biblioteket.",
                "The hearing closes on 3 May, and Fjordpressen will put the report in the reading room at the library.",
            ),
        ],
        "En 87 meter testmast på Klitsand får betinget godkendelse i to år. Karsten Vang afviser, at der allerede er besluttet vindmøller. 14 klager fra Rylevej og en fugleklausul på ti procent følger tilladelsen.",
        "An 87-metre test mast at Klitsand gets conditional approval for two years. Karsten Vang denies that wind turbines are already decided. 14 complaints from Rylevej and a ten-percent bird clause travel with the permit.",
        ("Klitsand", "87", "Karsten Vang", "2", "Rylevej", "14", "10", "Ellen Buhl", "3. maj"),
        (
            "87 m mast, two-year wind measurement",
            "14 neighbour complaints on Rylevej",
            "mast must come down if birds drop >10%",
            "hearing closes 3 May",
        ),
        "energy",
    ),
    _a(
        "vk-003",
        "Taget lækker på Nordmark Skole efter efterårsregn",
        "The roof leaks at Nordmark School after autumn rain",
        [
            (
                "Efterårsregnen har åbnet en lækage i taget over aulaen på Nordmark Skole.",
                "The autumn rain has opened a leak in the roof over the hall at Nordmark School.",
            ),
            (
                "Lærer Amina Sørensen flyttede tre klasser ned i bibliotekets læsestue, fordi gulvet var vådt.",
                "Teacher Amina Sørensen moved three classes down to the library reading room because the floor was wet.",
            ),
            (
                "Teknisk forvaltning skønner, at reparationen koster 1,2 millioner kroner og tager fire uger.",
                "The technical department estimates that the repair costs 1.2 million kroner and takes four weeks.",
            ),
            (
                "Håndværkere fra Brohuset begynder mandag, hvis vinden holder sig under 15 meter.",
                "Tradespeople from Brohuset start on Monday if the wind stays under 15 metres.",
            ),
            (
                "Forældre bad om midlertidig bus til Amberhus, men kommunen sagde nej på grund af budgettet.",
                "Parents asked for a temporary bus to Amberhus, but the municipality said no because of the budget.",
            ),
            (
                "Skoleeleverne får gymnastik i havnens venteskur, indtil aulaen er tør.",
                "The schoolchildren get gymnastics in the harbour shelter until the hall is dry.",
            ),
        ],
        "Nordmark Skoles aula lækker efter efterårsregn. Amina Sørensen flyttede tre klasser, og reparationen er sat til 1,2 millioner kroner over fire uger. En midlertidig bus til Amberhus blev afvist.",
        "Nordmark School's hall leaks after autumn rain. Amina Sørensen moved three classes, and the repair is put at 1.2 million kroner over four weeks. A temporary bus to Amberhus was refused.",
        ("Nordmark Skole", "Amina Sørensen", "3", "1,2", "4", "Brohuset", "15", "Amberhus"),
        (
            "leak over the school hall",
            "three classes moved to the library",
            "repair 1.2 million kroner, four weeks",
            "no temporary bus to Amberhus",
        ),
        "school",
    ),
    _a(
        "vk-004",
        "Byrådet vedtager udvidelse af Stenmole",
        "The town council adopts the Stenmole extension",
        [
            (
                "Byrådet vedtog i går udvidelsen af Stenmole med 17 stemmer for, fire imod og én blank.",
                "The town council yesterday adopted the Stenmole extension with 17 votes for, four against and one blank.",
            ),
            (
                "Projektet lægger 80 meter ny kaj til fiskere og en bredere sti til sommergæster.",
                "The project adds 80 metres of new quay for fishers and a wider path for summer visitors.",
            ),
            (
                "Borgmester Ellen Buhl sagde, at anlægsarbejdet skaber 25 lokale arbejdspladser i to sæsoner.",
                "Mayor Ellen Buhl said that the construction creates 25 local jobs over two seasons.",
            ),
            (
                "Fiskeriforeningen pegede på, at kvoten allerede er presset, og at kajen ikke fanger flere torsk.",
                "The fishery association pointed out that the quota is already tight, and that the quay does not catch more cod.",
            ),
            (
                "Entreprenøren fra Klitsand skal være færdig inden 1. oktober, ellers falder kontrakten.",
                "The contractor from Klitsand must finish before 1 October, otherwise the contract falls.",
            ),
            (
                "Høringen om støj om natten fortsætter, fordi naboerne på Rylevej stadig er bekymrede.",
                "The hearing on noise at night continues, because the neighbours on Rylevej are still worried.",
            ),
        ],
        "Stenmole udvides efter 17-4-1 i byrådet. 80 meter ny kaj og 25 job i to sæsoner. Fiskeriforeningen tvivler, og kontrakten kræver færdigt arbejde 1. oktober.",
        "Stenmole is extended after a 17-4-1 council vote. 80 metres of new quay and 25 jobs over two seasons. The fishery association is doubtful, and the contract requires finished work by 1 October.",
        ("Stenmole", "17", "4", "80", "Ellen Buhl", "25", "2", "Klitsand", "1. oktober", "Rylevej"),
        (
            "council vote 17 for, 4 against, 1 blank",
            "80 m new quay",
            "25 local jobs over two seasons",
            "deadline 1 October",
        ),
        "harbour",
    ),
    _a(
        "vk-005",
        "Amberhus åbner rav- og bronzealderudstilling",
        "Amberhus opens an amber and Bronze Age exhibition",
        [
            (
                "Amberhus åbner lørdag en udstilling om rav og bronzealderfund fra gravhøje i omegnen.",
                "Amberhus opens on Saturday an exhibition about amber and Bronze Age finds from barrows in the area.",
            ),
            (
                "Museets formand Poul Nissen sagde, at 40 procent af fundene aldrig har været vist offentligt.",
                "The museum chair Poul Nissen said that 40 percent of the finds have never been shown publicly.",
            ),
            (
                "Børn kommer gratis ind, mens voksne betaler 65 kroner, og billetter sælges også på biblioteket.",
                "Children enter free, while adults pay 65 kroner, and tickets are also sold at the library.",
            ),
            (
                "Yasmin El-Khatib har skrevet teksterne på dansk og engelsk, så sommergæster kan læse med.",
                "Yasmin El-Khatib has written the texts in Danish and English so summer visitors can read along.",
            ),
            (
                "Udstillingen varer til 15. september og flytter derefter et udvalg til læsesalen.",
                "The exhibition runs until 15 September and afterwards moves a selection to the reading room.",
            ),
            (
                "Fjordpressen lægger et kort over gravhøjene ved Tangløb, men uden præcise koordinater.",
                "Fjordpressen will post a map of the barrows by Tangløb, but without precise coordinates.",
            ),
        ],
        "Amberhus åbner lørdag en rav- og bronzealderudstilling. 40 procent af fundene er nye for publikum. Børn går gratis, voksne betaler 65 kroner, og Yasmin El-Khatib har skrevet tosprogede tekster.",
        "Amberhus opens an amber and Bronze Age exhibition on Saturday. 40 percent of the finds are new to the public. Children enter free, adults pay 65 kroner, and Yasmin El-Khatib wrote bilingual texts.",
        ("Amberhus", "Poul Nissen", "40", "65", "Yasmin El-Khatib", "15. september", "Tangløb"),
        (
            "opens Saturday",
            "40% of finds never shown",
            "adults 65 kroner, children free",
            "runs until 15 September",
        ),
        "culture",
    ),
    _a(
        "vk-006",
        "Natbus i sommersæsonen får tre stop i Vesterklit",
        "The summer night bus gets three stops in Vesterklit",
        [
            (
                "Kommunen prøver i juni, juli og august en natbus mellem Havnepladsen, Nordmark og Amberhus.",
                "The municipality is trying in June, July and August a night bus between Havnepladsen, Nordmark and Amberhus.",
            ),
            (
                "Ruten kører fredag og lørdag efter klokken 22.00 og slutter klokken 01.30.",
                "The route runs Friday and Saturday after 22.00 and ends at 01.30.",
            ),
            (
                "Teknisk chef Henrik Straarup sagde, at forsøget koster 380.000 kroner og kræver mindst 12 passagerer pr. tur.",
                "Technical lead Henrik Straarup said that the trial costs 380,000 kroner and needs at least 12 passengers per trip.",
            ),
            (
                "Hvis tallet ligger lavere tre uger i træk, stopper busserne uden ny høring.",
                "If the figure sits lower for three weeks in a row, the buses stop without a new hearing.",
            ),
            (
                "Turister fra Mågeø kan købe billet sammen med færgen, men kun når færgen ikke er aflyst.",
                "Tourists from Mågeø can buy a ticket together with the ferry, but only when the ferry is not cancelled.",
            ),
            (
                "Fjordpressen tæller passagerer de første to weekender og lægger tallene i arkivet.",
                "Fjordpressen will count passengers the first two weekends and put the figures in the archive.",
            ),
        ],
        "En natbus kører i juni–august mellem Havnepladsen, Nordmark og Amberhus efter 22.00. Forsøget koster 380.000 kroner og kræver 12 passagerer. Henrik Straarup dropper ruten efter tre svage uger.",
        "A night bus runs June–August between Havnepladsen, Nordmark and Amberhus after 22.00. The trial costs 380,000 kroner and needs 12 passengers. Henrik Straarup drops the route after three weak weeks.",
        ("Havnepladsen", "Nordmark", "Amberhus", "22.00", "01.30", "Henrik Straarup", "380.000", "12", "Mågeø"),
        (
            "Fri/Sat night bus, three stops",
            "380,000 kroner trial budget",
            "minimum 12 passengers",
            "killed after three weak weeks",
        ),
        "transport",
    ),
    _a(
        "vk-007",
        "Tilskud til varmepumper i gamle murstenshuse",
        "Subsidy for heat pumps in old brick houses",
        [
            (
                "Kommunen åbner et tilskud på 27.000 kroner til varmepumper i huse ældre end 1965.",
                "The municipality is opening a subsidy of 27,000 kroner for heat pumps in houses older than 1965.",
            ),
            (
                "Fristen er 12. april, og ansøgningen skal vedlægge et energimærke ikke ældre end to år.",
                "The deadline is 12 April, and the application must attach an energy label no older than two years.",
            ),
            (
                "Sofie Tranberg fra forvaltningen sagde, at der er penge til 60 husstande i første runde.",
                "Sofie Tranberg from the department said that there is money for 60 households in the first round.",
            ),
            (
                "Huse på Rylevej og omkring Tangløb får forrang, fordi de ligger i den kolde kystkile.",
                "Houses on Rylevej and around Tangløb get priority because they sit in the cold coastal wedge.",
            ),
            (
                "Hvis ansøgere glemmer energimærket, bliver brevet lagt tilbage uden ny frist.",
                "If applicants forget the energy label, the letter is put back without a new deadline.",
            ),
            (
                "Fjordpressen lægger skemaet i læsesalen og på hjemmesiden samme dag, som høringen slutter.",
                "Fjordpressen will put the form in the reading room and on the website the same day the hearing closes.",
            ),
        ],
        "Et tilskud på 27.000 kroner åbner for varmepumper i huse fra før 1965. Fristen er 12. april, og Sofie Tranberg har plads til 60 husstande. Rylevej og Tangløb får forrang.",
        "A 27,000-kroner subsidy opens for heat pumps in pre-1965 houses. The deadline is 12 April, and Sofie Tranberg has room for 60 households. Rylevej and Tangløb get priority.",
        ("27.000", "1965", "12. april", "Sofie Tranberg", "60", "Rylevej", "Tangløb"),
        (
            "27,000 kroner per heat pump",
            "houses older than 1965",
            "deadline 12 April, 60 households",
            "priority for Rylevej and Tangløb",
        ),
        "energy",
    ),
    _a(
        "vk-008",
        "Cykelsti langs Tangløb udsat efter fredning",
        "Bike path along Tangløb postponed after conservation",
        [
            (
                "Cykelstien langs Tangløb er udsat til næste forår, fordi en fredning af klitten kom i vejen.",
                "The bike path along Tangløb is postponed until next spring because a dune conservation order got in the way.",
            ),
            (
                "Naturstyrelsen kræver en omlægning 40 meter længere inde, væk fra de våde partier.",
                "The nature agency requires a reroute 40 metres further inland, away from the wet stretches.",
            ),
            (
                "Mikkel Ravn fra teknisk forvaltning sagde, at den nye linje koster 2,4 millioner ekstra.",
                "Mikkel Ravn from the technical department said that the new line costs 2.4 million extra.",
            ),
            (
                "Byrådet udsatte beslutningen, indtil budgettet for næste år er klart i december.",
                "The town council postponed the decision until next year's budget is clear in December.",
            ),
            (
                "Skoleelever fra Nordmark cykler derfor stadig ad den smalle Rylevej i mørke.",
                "Schoolchildren from Nordmark therefore still cycle along the narrow Rylevej in the dark.",
            ),
            (
                "Fjordpressen har gået ruten med Ravn og lægger et kort uden at pege på redepladser.",
                "Fjordpressen walked the route with Ravn and will post a map without pointing out nesting sites.",
            ),
        ],
        "Cykelstien ved Tangløb venter til foråret efter en fredning. Omlægningen på 40 meter koster 2,4 millioner extra. Nordmarks elever cykler videre ad Rylevej, indtil decemberbudgettet er klart.",
        "The Tangløb bike path waits until spring after a conservation order. The 40-metre reroute costs 2.4 million extra. Nordmark pupils keep using Rylevej until the December budget is clear.",
        ("Tangløb", "40", "Mikkel Ravn", "2,4", "december", "Nordmark", "Rylevej"),
        (
            "postponed to next spring",
            "40 m inland reroute",
            "2.4 million extra",
            "decision tied to December budget",
        ),
        "transport",
    ),
    _a(
        "vk-009",
        "Kirkebøgerne fra tre sogne kommer i digitalt arkiv",
        "Parish registers from three parishes enter a digital archive",
        [
            (
                "Biblioteket scanner kirkebøgerne fra Vesterklit, Nordmark og Mågeø og lægger dem i et digitalt arkiv.",
                "The library is scanning the parish registers from Vesterklit, Nordmark and Mågeø and placing them in a digital archive.",
            ),
            (
                "Frivillige under Troels Kjær har allerede scannet 11.000 sider siden januar.",
                "Volunteers under Troels Kjær have already scanned 11,000 pages since January.",
            ),
            (
                "Slægtsforskere kan læse med i læsesalen, men ikke tage billeder af de ældste bind fra 1784.",
                "Genealogists can read along in the reading room, but not take pictures of the oldest volumes from 1784.",
            ),
            (
                "Kommunen betaler 190.000 kroner, og restbeløbet kommer fra en fælles bevilling med Amberhus.",
                "The municipality pays 190,000 kroner, and the remainder comes from a shared grant with Amberhus.",
            ),
            (
                "Hvis en side er for våd eller sort, bliver den stående i det fysiske arkiv under lås.",
                "If a page is too wet or black, it stays in the physical archive under lock.",
            ),
            (
                "Fjordpressen får ikke navne fra levende personer med i artiklen, kun årstal og sogn.",
                "Fjordpressen will not put names of living people in the article, only years and parish.",
            ),
        ],
        "Kirkebøger fra Vesterklit, Nordmark og Mågeø scannes til et digitalt arkiv. Troels Kjærs frivillige har taget 11.000 sider. 190.000 kroner kommer fra kommunen, og bind fra 1784 må ikke fotograferes.",
        "Parish registers from Vesterklit, Nordmark and Mågeø are scanned into a digital archive. Troels Kjær's volunteers have taken 11,000 pages. 190,000 kroner comes from the municipality, and volumes from 1784 may not be photographed.",
        ("Vesterklit", "Nordmark", "Mågeø", "Troels Kjær", "11.000", "1784", "190.000", "Amberhus"),
        (
            "three parishes scanned",
            "11,000 pages since January",
            "190,000 kroner municipal share",
            "no photos of 1784 volumes",
        ),
        "culture",
    ),
    _a(
        "vk-010",
        "Fiskeriforeningen venter lavere torskekvote",
        "The fishery association expects a lower cod quota",
        [
            (
                "Fiskeriforeningen holdt møde i Brohuset om en ventet lavere kvote på torsk og rødspætte.",
                "The fishery association held a meeting at Brohuset about an expected lower quota on cod and plaice.",
            ),
            (
                "Formand Mikkel Ravn læste et brev fra ministeriet, der peger på 18 procent færre ton i den kommende sæson.",
                "Chair Mikkel Ravn read a letter from the ministry that points to 18 percent fewer tonnes in the coming season.",
            ),
            (
                "Medlemmerne var uenige: nogle vil fiske hårdere først på året, andre vil holde bådene i havnen.",
                "The members disagreed: some want to fish harder early in the year, others want to keep the boats in the harbour.",
            ),
            (
                "Aftalen med kommunen om kajplads på Stenmole gælder kun, hvis mindst 20 både betaler afgift.",
                "The agreement with the municipality on quay space at Stenmole applies only if at least 20 boats pay the fee.",
            ),
            (
                "Ellen Buhl lovede ikke nye penge, men bad om tal for fangst pr. uge inden 1. marts.",
                "Ellen Buhl did not promise new money, but asked for catch figures per week before 1 March.",
            ),
            (
                "Fjordpressen sad med som presse, men uden båndoptager, efter et krav fra bestyrelsen.",
                "Fjordpressen sat in as press, but without a tape recorder, after a demand from the board.",
            ),
        ],
        "Fiskeriforeningen venter 18 procent færre ton torsk og rødspætte. Mikkel Ravn læste ministeriets brev i Brohuset. Kajplads på Stenmole kræver 20 både, og Ellen Buhl vil have ugetal inden 1. marts.",
        "The fishery association expects 18 percent fewer tonnes of cod and plaice. Mikkel Ravn read the ministry letter at Brohuset. Quay space at Stenmole needs 20 boats, and Ellen Buhl wants weekly figures before 1 March.",
        ("Fiskeriforeningen", "Brohuset", "Mikkel Ravn", "18", "Stenmole", "20", "Ellen Buhl", "1. marts"),
        (
            "18% fewer tonnes expected",
            "meeting at Brohuset",
            "Stenmole berth needs 20 paying boats",
            "weekly catch figures due 1 March",
        ),
        "harbour",
    ),
)


TRAIN_IDS: Tuple[str, ...] = ("vk-001", "vk-002", "vk-003", "vk-004", "vk-005", "vk-006")
VALIDATION_IDS: Tuple[str, ...] = ("vk-007", "vk-008")
TEST_IDS: Tuple[str, ...] = ("vk-009", "vk-010")


def all_articles() -> Tuple[GazetteArticle, ...]:
    return ARTICLES


def by_id() -> Dict[str, GazetteArticle]:
    return {art.article_id: art for art in ARTICLES}


def articles_for(ids: Sequence[str]) -> List[GazetteArticle]:
    index = by_id()
    missing = [i for i in ids if i not in index]
    if missing:
        raise KeyError(f"unknown article ids: {missing}")
    return [index[i] for i in ids]


def split_map() -> Dict[str, Tuple[str, ...]]:
    return {
        "train": TRAIN_IDS,
        "validation": VALIDATION_IDS,
        "test": TEST_IDS,
    }


def validate_corpus() -> List[str]:
    """Return human-readable problems, or an empty list if the gazette is sound."""
    problems: List[str] = []
    seen = set()
    assigned = set(TRAIN_IDS) | set(VALIDATION_IDS) | set(TEST_IDS)
    for art in ARTICLES:
        try:
            art.validate()
        except ValueError as exc:
            problems.append(str(exc))
        if art.article_id in seen:
            problems.append(f"duplicate id {art.article_id}")
        seen.add(art.article_id)
        if len(art.danish_sentences) < 4:
            problems.append(f"{art.article_id}: fewer than 4 sentences")
    leftover = seen - assigned
    unused_split = assigned - seen
    if leftover:
        problems.append(f"articles not in a split: {sorted(leftover)}")
    if unused_split:
        problems.append(f"split ids missing from corpus: {sorted(unused_split)}")
    overlap = set(TRAIN_IDS) & set(VALIDATION_IDS)
    overlap |= set(TRAIN_IDS) & set(TEST_IDS)
    overlap |= set(VALIDATION_IDS) & set(TEST_IDS)
    if overlap:
        problems.append(f"split overlap: {sorted(overlap)}")
    return problems
