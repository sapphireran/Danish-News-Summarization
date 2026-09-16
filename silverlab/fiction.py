"""Original fictional Danish briefs used by the personal methods lab.

These are not TV2 Nord, not the private 10k dump, and not employer text.
Each brief is long enough that lead-1, keyword, and TextRank can disagree.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Sequence

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DEFAULT_JSON = REPO_ROOT / "examples" / "data" / "fiction_briefs.json"


@dataclass(frozen=True)
class Brief:
    id: str
    title: str
    topic: str
    article_text: str
    gold_extractive: str
    gold_abstractive: str

    @property
    def csv_article_text(self) -> str:
        """Column name used by `translate.py` in the 2023 dump."""
        return self.article_text


# Hand-written corpus. Keep ids in the lab-* namespace so they do not collide
# with sample ids used on the other personal-docs branches.
_BRIEFS: tuple[Brief, ...] = (
    Brief(
        id="lab-01",
        title="Himmerlands Observatorium åbner for månens aften",
        topic="astronomi",
        article_text=(
            "Himmerlands Observatorium åbner lørdag aften for offentligheden, når månen "
            "står højt og Saturn kan ses i det største spejlteleskop. Bestyrelsen forventer "
            "omkring 80 gæster og har sat kaffe på i den gamle målestation ved siden af kuplen. "
            "Astronomilærer Ida Vendelbo viser, hvordan man finder Cassiopeia uden en telefon, "
            "og hun har printet et stjernekort på A3. Børn under 12 kommer gratis, men skal have "
            "en voksen med ind på platformen. Hvis skydækket bliver for tæt, flyttes kigget til "
            "søndag kl. 21. Observatoriet ligger 12 kilometer nord for Hobro og har to spejlteleskoper "
            "fra 1998, som frivillige har pudset i påskeferien."
        ),
        gold_extractive=(
            "Himmerlands Observatorium åbner lørdag aften for offentligheden, når månen "
            "står højt og Saturn kan ses i det største spejlteleskop."
        ),
        gold_abstractive=(
            "Observatoriet ved Hobro åbner lørdag for et offentligt månekig med Saturn i "
            "teleskopet; ved tæt skydække rykker arrangementet til søndag."
        ),
    ),
    Brief(
        id="lab-02",
        title="Surdejsmestre mødes i Skives gamle dampbageri",
        topic="mad",
        article_text=(
            "Ti bagere fra Midt- og Nordjylland mødes søndag i Skives gamle dampbageri for at "
            "kåre årets surdej. Dommerne smager i blinde og giver point for skorpe, syre og duft "
            "af ristet malt. Sidste års vinder, Mette Kjær fra Lemvig, stiller op med en dejsyre "
            "hun har fodret hver morgen siden januar. Publikum kan købe de kasserede brød til 20 kr. "
            "stykket, og overskuddet går til byens ungdomsskole. Arrangørerne forventer kø, så der "
            "sælges nummerlapper fra kl. 10. Dampbageriets ovn fra 1924 er tændt for første gang "
            "siden restaureringen i 2021."
        ),
        gold_extractive=(
            "Ti bagere fra Midt- og Nordjylland mødes søndag i Skives gamle dampbageri for at "
            "kåre årets surdej."
        ),
        gold_abstractive=(
            "Ti midt- og nordjyske bagere dyster søndag i Skive om årets surdej; overskuddet "
            "fra brødsalget går til ungdomsskolen."
        ),
    ),
    Brief(
        id="lab-03",
        title="Jazz i Vejle Ådal slår dørene op med tre scener",
        topic="musik",
        article_text=(
            "Jazz i Vejle Ådal slår dørene op fredag med tre scener, hvoraf den mindste ligger "
            "på en pram i åen. Headlineren er saxofonisten Naja Storm, der vender hjem efter "
            "seks år i Malmö. Festivalen har i år droppet de dyre udenlandske navne og satser "
            "på jyske kvartetter og en enkelt færøsk vokaltrio. Dagsbilletter koster 175 kr., og "
            "børn under 16 kommer gratis med en voksen. Hvis det regner, flyttes pramscenen ind "
            "i det gamle vandværk. Arrangørerne lover, at sidste nummer slutter inden kl. 23 af "
            "hensyn til naboerne langs åstien."
        ),
        gold_extractive=(
            "Jazz i Vejle Ådal slår dørene op fredag med tre scener, hvoraf den mindste ligger "
            "på en pram i åen."
        ),
        gold_abstractive=(
            "Vejle-jazzfestivalen åbner fredag med tre scener og Naja Storm som headliner; "
            "pramscenen rykker ind i vandværket ved regn."
        ),
    ),
    Brief(
        id="lab-04",
        title="Amatørcyklister rider klassiker gennem Rold Skov",
        topic="sport",
        article_text=(
            "Godt 240 amatørcyklister rider søndag en 86 kilometers klassiker gennem Rold Skov "
            "med start i Skørping. Løbsledelsen advarer om løst grus på den nordlige sløjfe efter "
            "nattens regn og beder rytterne om at holde afstand i nedkørslerne. Der er væskestation "
            "ved Rebild Bakker og en ekstra ved den gamle skovridergård. Børn mellem 10 og 14 kan "
            "køre en 12 kilometers minirute, der slutter ved spejderhytten. Tilmeldingen lukkede "
            "torsdag med venteliste. Arrangørerne samarbejder med skovfogeden om at holde hestene "
            "væk fra de smalle stier mellem kl. 9 og 14."
        ),
        gold_extractive=(
            "Godt 240 amatørcyklister rider søndag en 86 kilometers klassiker gennem Rold Skov "
            "med start i Skørping."
        ),
        gold_abstractive=(
            "240 amatører kører søndag 86 kilometer gennem Rold Skov fra Skørping, mens børn "
            "kan vælge en 12 kilometers minirute."
        ),
    ),
    Brief(
        id="lab-05",
        title="Digternat på Hjørring Bibliotek samler nye stemmer",
        topic="litteratur",
        article_text=(
            "Hjørring Bibliotek åbner torsdag for en digternat, hvor ni lokale stemmer læser "
            "upublicerede tekster i magasinet under hovedtrappen. Arrangementet er gratis, men "
            "der er kun 60 stole, så værterne anbefaler at møde op en halv time før. Poeten "
            "Sigrid Holm, der debuterede sidste år på et lille forlag i Aalborg, er aftenens vært "
            "og har bedt alle om at holde sig under fire minutter. Cafeen sælger te og kirsebærkage "
            "i pausen. Optagelserne lægges på bibliotekets podcast næste onsdag. Hvis elevatoren "
            "stadig er i stykker, vises der vej ad den smalle kældertrappe."
        ),
        gold_extractive=(
            "Hjørring Bibliotek åbner torsdag for en digternat, hvor ni lokale stemmer læser "
            "upublicerede tekster i magasinet under hovedtrappen."
        ),
        gold_abstractive=(
            "Ni lokale digtere læser torsdag upublicerede tekster på Hjørring Bibliotek; "
            "optagelsen udkommer som podcast onsdagen efter."
        ),
    ),
    Brief(
        id="lab-06",
        title="Bybiavlere på Amager høster den første sommerhonning",
        topic="natur",
        article_text=(
            "Bybiavlerne på Amager høster i weekenden den første sommerhonning fra kasserne på "
            "taget af det gamle vandtårn. Formand Karim Dahl siger, at foråret var koldt, så "
            "udbyttet nok lander under 40 kilo. Gæster kan smage tre slags honning og se, hvordan "
            "tavlerne slynges i et telt ved foden af tårnet. Børn skal have lukkede sko på, og "
            "der udlånes slør ved indgangen. Overskuddet fra glassene til 65 kr. går til nye "
            "dronninger næste april. Hvis vinden kommer ind fra Øresund, rykker slyngningen ind "
            "i cykelskuret."
        ),
        gold_extractive=(
            "Bybiavlerne på Amager høster i weekenden den første sommerhonning fra kasserne på "
            "taget af det gamle vandtårn."
        ),
        gold_abstractive=(
            "Amagers bybiavlere høster weekendens første honning på vandtårnets tag; udbyttet "
            "ventes under 40 kilo efter et koldt forår."
        ),
    ),
    Brief(
        id="lab-07",
        title="Veteraner spiller skak-DM i Svendborgs gamle toldbod",
        topic="spil",
        article_text=(
            "Fireogtyve veteraner spiller i weekenden danmarksmesterskab i skak i Svendborgs "
            "gamle toldbod ved havnen. Runderne begynder kl. 10 begge dage, og der er betænkningstid "
            "på 90 minutter plus 30 sekunder pr. træk. Favoritten er Inge Ravn fra Odense, der "
            "vandt sidste år i Kolding uden at tabe et parti. Tilskuerne skal være stille efter "
            "det første træk og må kun fotografere i pauserne. Der serveres æblemost og smørrebrød "
            "i det lille pakhus ved siden af. Finalerunden transmitteres på klubbens hjemmeside "
            "søndag eftermiddag."
        ),
        gold_extractive=(
            "Fireogtyve veteraner spiller i weekenden danmarksmesterskab i skak i Svendborgs "
            "gamle toldbod ved havnen."
        ),
        gold_abstractive=(
            "24 veteraner spiller weekendens skak-DM i Svendborgs toldbod med 90 minutters "
            "betænkningstid; Inge Ravn fra Odense er favorit."
        ),
    ),
    Brief(
        id="lab-08",
        title="Geolog fortæller om klitter der vandrer ved Blåvand",
        topic="videnskab",
        article_text=(
            "Geolog Pernille Søndergaard holder onsdag aften foredrag i Blåvandshuk om klitter, "
            "der flytter sig op til to meter på et vinterhalvår. Hun viser målinger fra 2016 til "
            "2023 og forklarer, hvorfor marehalmen nogle år taber til vestenvinden. Arrangementet "
            "starter kl. 19 i redningsstationens garage og er gratis, men der er kun 45 pladser. "
            "Efter oplægget går holdet 400 meter ud på stranden med lommelygter, hvis tidevandet "
            "tillader det. Kommunen har lagt et kort frem, der viser hvilke stier der er spærret "
            "efter sidste efterårs storm. Tilmelding sker på bibliotekets seddel i foyer."
        ),
        gold_extractive=(
            "Geolog Pernille Søndergaard holder onsdag aften foredrag i Blåvandshuk om klitter, "
            "der flytter sig op til to meter på et vinterhalvår."
        ),
        gold_abstractive=(
            "Pernille Søndergaard fortæller onsdag i Blåvand om klitter, der kan vandre to meter "
            "på en vinter, og tager publikum med på stranden bagefter."
        ),
    ),
    Brief(
        id="lab-09",
        title="Studerendes kortfilm får premiere i filmskolens anneks",
        topic="film",
        article_text=(
            "Fire afgangsfilm fra den lille filmskole i Aarhus får premiere lørdag i annekset "
            "bag den gamle biograf. Den længste film varer 18 minutter og handler om en færge, "
            "der aldrig lægger til, mens den korteste er en animationsfilm på fire minutter om "
            "en postkasse. Instruktørerne svarer på spørgsmål efter hver visning, og der er "
            "undertekster på engelsk. Billetter koster 40 kr. og sælges i døren, så længe der "
            "er sæder. En af filmene er optaget i Rødvig og har fået tilladelse til at bruge "
            "havnens tågehorn. Caféen holder åbent til midnat med kaffe og mineralvand."
        ),
        gold_extractive=(
            "Fire afgangsfilm fra den lille filmskole i Aarhus får premiere lørdag i annekset "
            "bag den gamle biograf."
        ),
        gold_abstractive=(
            "Fire aarhusianske afgangsfilm vises lørdag i filmskolens anneks; den længste varer "
            "18 minutter, og instruktørerne tager spørgsmål bagefter."
        ),
    ),
    Brief(
        id="lab-10",
        title="Gæsteforelæsning om norrønt samler sprogfolk i Ribe",
        topic="sprog",
        article_text=(
            "Sprogfolk fra hele landet samles fredag i Ribe til en gæsteforelæsning om norrønt "
            "og de danske runer, der stadig kan læses på gravstenene i domkirkens krypt. "
            "Gæsten er professor Eiríkur Halldórsson fra Reykjavík, der taler på dansk med "
            "færøske indskud. Der er 70 pladser i kapitelsalen, og tilmeldingen lukkede allerede "
            "mandag. Efter foredraget vises tre håndskriftfragmenter, som museet normalt holder "
            "i mørke. Studerende kan få et kursusbevis, hvis de afleverer et referat på 400 ord "
            "inden næste torsdag. Kaffen serveres i korsgangen, så salen kan luftes."
        ),
        gold_extractive=(
            "Sprogfolk fra hele landet samles fredag i Ribe til en gæsteforelæsning om norrønt "
            "og de danske runer, der stadig kan læses på gravstenene i domkirkens krypt."
        ),
        gold_abstractive=(
            "Eiríkur Halldórsson forelæser fredag i Ribe om norrønt og runer; museet viser "
            "tre håndskriftfragmenter bagefter."
        ),
    ),
    Brief(
        id="lab-11",
        title="Ungdomskor tager på turné til Tórshavn",
        topic="musik",
        article_text=(
            "Holstebro Ungdomskor letter onsdag mod Tórshavn med 28 sangere og to klaverer i "
            "lasten. Koret skal synge tre koncerter på fire dage, heriblandt en åben prøve i "
            "nordlyskirken. Dirigent Lærke Frost siger, at de øver færøske vers, så publikum "
            "kan synge med på omkvædet. Rejsen er betalt af en lokal fond, og sangerne betaler "
            "kun 400 kr. hver for mad. Hvis færgen bliver indstillet på grund af storm, sover "
            "koret en ekstra nat i Hirtshals. Forældre kan følge turneen på korets lukkede "
            "blog, der opdateres hver aften."
        ),
        gold_extractive=(
            "Holstebro Ungdomskor letter onsdag mod Tórshavn med 28 sangere og to klaverer i "
            "lasten."
        ),
        gold_abstractive=(
            "28 unge fra Holstebro flyver onsdag til Tórshavn for tre koncerter; ved storm i "
            "færgelejet venter de i Hirtshals."
        ),
    ),
    Brief(
        id="lab-12",
        title="Ny klatrehal i Holstebro åbner med gratis prøvetime",
        topic="sport",
        article_text=(
            "Holstebros nye klatrehal åbner lørdag i den tidligere maskinhal ved jernbanen og "
            "byder på 14 ruter fra 6a til 7c. Den første time er gratis, hvis man medbringer "
            "egne sko; ellers koster udlejning 25 kr. Hallen har et særligt hjørne til børn "
            "under 10 med blødere faldmåtter. Instruktørerne kræver sele på alle, der går over "
            "tre meter, og der er intro hver hele time. Cafeen sælger kun vand og frugt, fordi "
            "hallen ikke har fedtudskiller endnu. Søndag holdes der et stille pas for dem, der "
            "vil klatre uden musik."
        ),
        gold_extractive=(
            "Holstebros nye klatrehal åbner lørdag i den tidligere maskinhal ved jernbanen og "
            "byder på 14 ruter fra 6a til 7c."
        ),
        gold_abstractive=(
            "Den nye klatrehal i Holstebros gamle maskinhal åbner lørdag med 14 ruter og en "
            "gratis første time for dem, der har egne sko."
        ),
    ),
    Brief(
        id="lab-13",
        title="Veteran-cykler fylder magasinet i Odsherred Museum",
        topic="kultur",
        article_text=(
            "Odsherred Museum fylder hele magasinet med veteran-cykler fra 1910 til 1975, "
            "heriblandt en sort racer, der kørte Sjælland Rundt i 1952. Udstillingen åbner "
            "fredag og varer seks uger. Gæster må godt røre ved sadlerne, men ikke trykke på "
            "klokkerne, som er blevet restaureret. Om søndagen kører en frivillig en rute på "
            "otte kilometer fra museet til havnen på en lånt damestålhest. Entré er 75 kr., og "
            "under 18 kommer gratis. Kataloget er trykt på tyndt papir, så det kan foldes ned "
            "i en cykeltaske."
        ),
        gold_extractive=(
            "Odsherred Museum fylder hele magasinet med veteran-cykler fra 1910 til 1975, "
            "heriblandt en sort racer, der kørte Sjælland Rundt i 1952."
        ),
        gold_abstractive=(
            "Odsherred Museum åbner fredag en seks uger lang udstilling af veteran-cykler, "
            "heriblandt en racer fra Sjælland Rundt 1952."
        ),
    ),
    Brief(
        id="lab-14",
        title="Kolonihaver bytter frø under det gamle pæretræ",
        topic="have",
        article_text=(
            "Kolonihaverne ved Roskilde fjord bytter lørdag frø under det gamle pæretræ, der "
            "stadig bærer frugt selv om stammen er hul. Der er kasser med ærter, tagetes og en "
            "lokal grønkål, som nogen kalder fjordkål. Nye havefolk kan få en pose med fem slags "
            "mod at love at aflevere frø igen næste september. Formanden beder folk om at skrive "
            "såår på poserne, fordi sidste år blev der sået 2018-frø, der næsten ikke spirede. "
            "Kaffen koster 10 kr. i den røde bod, og kagen er bagt af overskudszucchini. Hvis "
            "det regner, rykker byttet ind i redskabsskuret."
        ),
        gold_extractive=(
            "Kolonihaverne ved Roskilde fjord bytter lørdag frø under det gamle pæretræ, der "
            "stadig bærer frugt selv om stammen er hul."
        ),
        gold_abstractive=(
            "Havefolk ved Roskilde fjord bytter lørdag frø under pæretræet; nye medlemmer får "
            "fem slags mod at aflevere frø næste september."
        ),
    ),
    Brief(
        id="lab-15",
        title="Natsværmere tælles ved Møns Klint efter midnat",
        topic="natur",
        article_text=(
            "Naturvejledere tæller natsværmere ved Møns Klint natten til søndag, når lampen "
            "tændes bag et hvidt lagen mellem bøgene. Sidste år blev der noteret 64 arter, og "
            "målet i år er at slå 70, hvis natten bliver mild. Deltagerne mødes kl. 23 ved "
            "parkeringen og skal have rødt lys på pandelampen, så natsværmerne ikke bliver blændet. "
            "Børn må gerne være med, men arrangementet slutter først ved fire-tiden. Der serveres "
            "kakao fra termokander, og man må ikke slå efter insekterne. Resultatet lægges på "
            "foreningens artsportal mandag formiddag."
        ),
        gold_extractive=(
            "Naturvejledere tæller natsværmere ved Møns Klint natten til søndag, når lampen "
            "tændes bag et hvidt lagen mellem bøgene."
        ),
        gold_abstractive=(
            "Ved Møns Klint tælles natsværmere natten til søndag med lampe og lagen; målet er "
            "over 70 arter, og listen offentliggøres mandag."
        ),
    ),
    Brief(
        id="lab-16",
        title="Lokalradioen i Thisted fylder halvtreds og sender udefra",
        topic="medier",
        article_text=(
            "Radio Thy fylder halvtreds år lørdag og sender hele dagen fra et telt på torvet "
            "i Thisted. Veteranværten Grethe Holm, der begyndte som teenager i 1981, interviewar "
            "tre tidligere borgmestre og et fiskerikor. Lytterne kan ringe ind med hilsner, men "
            "kun mellem 11 og 13, fordi teknikken i teltet er lånt. Kagen er to meter lang og "
            "skæres kl. 15, hvis vinden ikke vælter buffetbordet. Stationen lægger et arkivklip "
            "fra 1976 på hjemmesiden, hvor en reporter beskriver isen i Limfjorden. Søndag er "
            "der almindelige udsendelser igen fra kælderen på indre mission."
        ),
        gold_extractive=(
            "Radio Thy fylder halvtreds år lørdag og sender hele dagen fra et telt på torvet "
            "i Thisted."
        ),
        gold_abstractive=(
            "Radio Thy fejrer 50 år lørdag med heldagssending fra et telt på Thisted torv og "
            "et arkivklip fra isvinteren 1976."
        ),
    ),
)


def all_briefs() -> tuple[Brief, ...]:
    return _BRIEFS


def iter_briefs() -> Iterator[Brief]:
    yield from _BRIEFS


def load_briefs(path: Path | None = None) -> list[Brief]:
    """Load briefs from JSON when present; otherwise return the in-module corpus."""
    source = path or DEFAULT_JSON
    if source.is_file():
        raw = json.loads(source.read_text(encoding="utf-8"))
        return [Brief(**row) for row in raw]
    return list(_BRIEFS)


def dump_briefs_json(path: Path | None = None) -> Path:
    target = path or DEFAULT_JSON
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(brief) for brief in _BRIEFS]
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def brief_by_id(brief_id: str, briefs: Sequence[Brief] | None = None) -> Brief:
    pool = list(briefs) if briefs is not None else list(_BRIEFS)
    for brief in pool:
        if brief.id == brief_id:
            return brief
    raise KeyError(brief_id)
