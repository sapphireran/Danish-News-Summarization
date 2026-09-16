"""Fictional Toftevig municipal news. Original prose, not scraped.

Every article is sentence-aligned Danish/English so hop-2 repacking can
be measured without OPUS error. Rows are labelled `synthetic` in the
CSV sidecars.
"""

from __future__ import annotations

from dataclasses import dataclass

from pakhus.world import find_figures, find_names


@dataclass(frozen=True)
class Article:
    id: str
    slug: str
    title_da: str
    pairs: tuple[tuple[str, str], ...]  # (danish, english) sentences
    oracle_summary_da: str
    oracle_summary_en: str
    planted: tuple[str, ...]
    split: str  # train / validation / test

    @property
    def danish(self) -> str:
        return " ".join(da for da, _en in self.pairs)

    @property
    def english(self) -> str:
        return " ".join(en for _da, en in self.pairs)

    @property
    def n_sentences(self) -> int:
        return len(self.pairs)

    def figures(self) -> list[str]:
        return find_figures(self.danish)

    def names(self) -> list[str]:
        return find_names(self.danish)


def _long_comma_sentence_da() -> str:
    clauses = [
        "forvaltningen har gennemgået kajens bæreevne",
        "uddybningen af sejlrenden i Gråfjord",
        "flytningen af ismaskinerne fra Fiskerihallen til Pakhuset",
        "en ny rampe ved Strandgade nr. 14",
        "skiltningen ved Møllebakken",
        "tilslutningen til cykelstien mod Østermarken",
        "støjmålingerne ved Nørreholt Skole",
        "tidsplanen for høringen der slutter den 12. november",
        "overslaget på 18,4 mio. kr. med en reserve på 1,2 mio. kr.",
        "digelagets krav om at Gråfjord Dige ikke må svækkes",
        "færgeselskabets ønske om fast kajplads kl. 06.15",
        "fiskernes krav om kold rum i Pakhuset",
        "bibliotekets midlertidige depot i kælderen under Kirkevej",
        "skolebestyrelsens bekymring for lastbiler i morgentimen",
        "en erstatningsrute for bus nr. 14 via Klintbro",
        "belysning på Færgelejet Klintbro",
        "et midlertidigt pakhus af træ indtil betonelementerne er støbt",
        "aftalen med entreprenøren om dagbøder ved forsinkelse",
        "borgmester Ellen Kraghs ønske om åbent samråd",
        "formand Søren Vibes ønske om at holde anlægsperioden uden for turistsæsonen",
    ]
    # Repeat with slight variation so the character saw has to fire several times.
    extra = [
        f"desuden punkt {i} om kontrolmåling ved Svanedammen"
        for i in range(1, 18)
    ]
    body = ", ".join(clauses + extra)
    return (
        "Havneudvalget bad onsdag forvaltningen om i samme indstilling at "
        f"beskrive {body}, før forslaget sendes i høring."
    )


def _long_comma_sentence_en() -> str:
    clauses = [
        "the load-bearing capacity of the quay",
        "the dredging of the fairway in Gråfjord",
        "the move of the ice machines from Fiskerihallen to Pakhuset",
        "a new ramp at Strandgade no. 14",
        "signage at Møllebakken",
        "the link to the cycle path toward Østermarken",
        "noise measurements at Nørreholt Skole",
        "the hearing timetable that ends on 12 November",
        "the estimate of DKK 18.4 million with a reserve of DKK 1.2 million",
        "the dike guild's demand that Gråfjord Dige not be weakened",
        "the ferry company's wish for a fixed berth at 6.15 a.m.",
        "the fishers' demand for a cold room in Pakhuset",
        "the library's temporary depot in the basement on Kirkevej",
        "the school board's concern about lorries in the morning hour",
        "a replacement route for bus no. 14 via Klintbro",
        "lighting at Færgelejet Klintbro",
        "a temporary timber warehouse until the concrete elements are cast",
        "the contractor agreement on delay penalties",
        "Mayor Ellen Kragh's wish for an open consultation",
        "chair Søren Vibe's wish to keep the works out of the tourist season",
    ]
    extra = [f"furthermore item {i} on control measurements at Svanedammen" for i in range(1, 18)]
    body = ", ".join(clauses + extra)
    return (
        "On Wednesday the harbour committee asked the administration, in the "
        f"same memorandum, to describe {body}, before the proposal goes to hearing."
    )


def _overlong_english_blob() -> str:
    """One English sentence with enough short tokens to exceed a 512-id pane."""
    chunks = [
        f"crate {i} holds ice, rope, nets, ledgers, bolts, paint and twine"
        for i in range(1, 90)
    ]
    return (
        "The packing house ledger lists "
        + ", ".join(chunks)
        + " before the night shift closes the gate."
    )


def _overlong_danish_blob() -> str:
    chunks = [
        f"kasse {i} rummer is, reb, garn, protokoller, bolte, maling og sejlgarn"
        for i in range(1, 90)
    ]
    return (
        "Pakhusets protokol opregner "
        + ", ".join(chunks)
        + " før natholdet lukker porten."
    )


ARTICLES: tuple[Article, ...] = (
    Article(
        id="tof-001",
        slug="harbour-hearing",
        title_da="Havneudvidelse sendes i høring",
        split="train",
        planted=("ordinal-date", "clock", "mio-kr", "bl.a.", "quote", "multi-pane"),
        oracle_summary_da=(
            "Toftevig Kommunes havneudvalg sendte onsdag den 12. oktober kl. 19.30 "
            "en udvidelse af Toftevig Havn i høring. Anlægget anslås til 18,4 mio. kr. "
            "bl.a. til ny kaj, uddybning af Gråfjord og et pakhus til ismaskiner."
        ),
        oracle_summary_en=(
            "On Wednesday 12 October at 7.30 p.m. Toftevig Municipality's harbour "
            "committee sent an expansion of Toftevig Havn to public hearing. The works "
            "are estimated at DKK 18.4 million, including a new quay, dredging of "
            "Gråfjord and a warehouse for ice machines."
        ),
        pairs=(
            (
                "Toftevig Kommunes havneudvalg vedtog onsdag den 12. oktober kl. 19.30 at sende forslaget om en udvidelse af Toftevig Havn i offentlig høring.",
                "On Wednesday 12 October at 7.30 p.m. Toftevig Municipality's harbour committee decided to send the proposal for an expansion of Toftevig Havn to public hearing.",
            ),
            (
                "Formand Søren Vibe sagde, at anlægget ifølge forvaltningens overslag vil koste 18,4 mio. kr., bl.a. til en ny kaj, uddybning af sejlrenden i Gråfjord og et mindre pakhus til fiskernes ismaskiner.",
                "Chair Søren Vibe said the works, according to the administration's estimate, will cost DKK 18.4 million, including a new quay, dredging of the fairway in Gråfjord and a smaller warehouse for the fishers' ice machines.",
            ),
            (
                "»Vi skylder både erhvervsfiskerne og lystbådene en kaj, der ikke skaller i frost,« sagde Vibe efter mødet i Pakhuset på Strandgade.",
                "\"We owe both the commercial fishers and the leisure boats a quay that does not flake in frost,\" Vibe said after the meeting in Pakhuset on Strandgade.",
            ),
            (
                "Borgmester Ellen Kragh understregede, at høringen løber t.o.m. den 12. november, og at samrådet på Nørreholt Skole er berammet til kl. 19.00.",
                "Mayor Ellen Kragh stressed that the hearing runs through 12 November and that the public meeting at Nørreholt Skole is scheduled for 7.00 p.m.",
            ),
            (
                "Digelagsformand Kaj Overgaard advarede om, at uddybningen ikke må svække Gråfjord Dige, som i 2022 blev forhøjet for 3,2 mio. kr.",
                "Dike-guild chair Kaj Overgaard warned that the dredging must not weaken Gråfjord Dige, which was raised in 2022 for DKK 3.2 million.",
            ),
            (
                "Fisker Niels Bro fra Fiskerihallen pegede på, at ismaskinerne i dag står i et lokale uden afløb, og at et nyt koldt rum i Pakhuset vil skære spild med ca. 15 pct.",
                "Fisher Niels Bro from Fiskerihallen noted that the ice machines currently stand in a room without a drain, and that a new cold room in Pakhuset would cut waste by about 15 percent.",
            ),
            (
                "Teknik- og miljøudvalget kræver en erstatningsrute for bus nr. 14 via Klintbro, mens lastbiler kører materialer ind ad Kirkevej.",
                "The technical and environment committee requires a replacement route for bus no. 14 via Klintbro while lorries bring materials in along Kirkevej.",
            ),
            (
                "Forvaltningen skal desuden beskrive belysning på Færgelejet Klintbro, skiltning ved Møllebakken og tilslutning til cykelstien mod Østermarken.",
                "The administration must also describe lighting at Færgelejet Klintbro, signage at Møllebakken and a link to the cycle path toward Østermarken.",
            ),
            (
                "Et mindretal med Ida Frost stemte imod at sende forslaget i høring nu, fordi støjmålingerne ved Nørreholt Skole først foreligger i uge 44.",
                "A minority with Ida Frost voted against sending the proposal to hearing now, because the noise measurements at Nørreholt Skole are not due until week 44.",
            ),
            (
                "Vibe svarede, at udvalget hellere vil høre borgerne parallelt med målingerne end at udskyde anlægsperioden ind i turistsæsonen ved Svanedammen.",
                "Vibe replied that the committee would rather hear residents in parallel with the measurements than postpone the works into the tourist season at Svanedammen.",
            ),
            (
                "Høringssvar sendes til kommunen, att. havneudvalget, og offentliggøres løbende på toftevig.dk, jf. styrelsens vejledning.",
                "Hearing replies are sent to the municipality, att. the harbour committee, and are published continuously at toftevig.dk, cf. the agency guidance.",
            ),
            (
                "Hvis overslaget holder, forventes første spadestik i marts, og kajen skal efter planen tages i brug inden 2026.",
                "If the estimate holds, the first spade is expected in March, and the quay is scheduled to come into use before 2026.",
            ),
            (
                "Baggrunden er, at den nuværende kaj i Toftevig Havn blev støbt i 1978 og ifølge tilsynet har revner i 22 pct. af elementerne ud mod Gråfjord.",
                "The background is that the present quay in Toftevig Havn was cast in 1978 and, according to inspection, has cracks in 22 percent of the elements facing Gråfjord.",
            ),
            (
                "Fiskerihallen har i tre vintre måttet flytte ismaskinerne ind i Pakhuset, når frostsprængninger har lukket det gamle koldrum på Strandgade nr. 14.",
                "For three winters Fiskerihallen has had to move the ice machines into Pakhuset when frost bursts closed the old cold room at Strandgade no. 14.",
            ),
            (
                "En ekstern revisor peger på, at 18,4 mio. kr. er et 2023-prisniveau, og at stål og beton siden er steget ca. 6 pct.",
                "An external auditor notes that DKK 18.4 million is a 2023 price level, and that steel and concrete have since risen by about 6 percent.",
            ),
            (
                "Derfor beder Ellen Kragh forvaltningen om et tillæg på 0,9 mio. kr. til indeks, før kommunalbestyrelsen ser sagen den 28. november.",
                "Ellen Kragh therefore asks the administration for a DKK 0.9 million index supplement before the council sees the case on 28 November.",
            ),
            (
                "Søren Vibe vil samtidig have en tidsplan, hvor lastbiler ikke kører ad Kirkevej mellem kl. 07.40 og kl. 08.15, mens bus nr. 14 sætter elever af ved Nørreholt Skole.",
                "Søren Vibe also wants a timetable in which lorries do not use Kirkevej between 7.40 a.m. and 8.15 a.m. while bus no. 14 drops pupils at Nørreholt Skole.",
            ),
            (
                "Kaj Overgaard gentog, at Gråfjord Dige skal pejles f.o.m. den 3. november, og at gravemaskiner ikke må stå på kronen ved Svanedammen.",
                "Kaj Overgaard repeated that Gråfjord Dige must be sounded from 3 November, and that excavators must not stand on the crest at Svanedammen.",
            ),
            (
                "Amina Rashid mindede udvalget om, at lokalhistorien i Pakhuset flyttes til Kirkevej i uge 43, så rummet kan bruges til samråd uden kasser i vejen.",
                "Amina Rashid reminded the committee that the local history in Pakhuset moves to Kirkevej in week 43 so the room can be used for consultations without boxes in the way.",
            ),
            (
                "Lars Kjær tilføjede, at cykelstien mod Østermarken bør asfalteres før anlægsstart, ellers cykler eleverne i lastbilsporet hele foråret.",
                "Lars Kjær added that the cycle path toward Østermarken should be asphalted before works start, otherwise pupils will cycle in the lorry lane all spring.",
            ),
            (
                "Niels Bro bad om, at det nye pakhus får afløb og en dør mod nord, så isen kan køres direkte til kajen uden at krydse Møllebakken.",
                "Niels Bro asked that the new warehouse get a drain and a north door so the ice can be carted straight to the quay without crossing Møllebakken.",
            ),
            (
                "Udvalget besluttede at sende hele pakken, inkl. erstatningsrute, digepejling og indeks, i høring som ét dokument på toftevig.dk.",
                "The committee decided to send the whole package, including the replacement route, dike sounding and index, to hearing as one document on toftevig.dk.",
            ),
        ),
    ),
    Article(
        id="tof-002",
        slug="school-bus",
        title_da="Bus nr. 14 lægges om i anlægsperioden",
        split="train",
        planted=("nr", "clock", "school-name"),
        oracle_summary_da=(
            "Bus nr. 14 kører via Klintbro i stedet for Kirkevej, mens Toftevig Havn "
            "udvides. Skoleleder Mette Holm frygter, at elever til Nørreholt Skole "
            "mister forbindelsen kl. 07.40."
        ),
        oracle_summary_en=(
            "Bus no. 14 will run via Klintbro instead of Kirkevej while Toftevig Havn "
            "is expanded. Headteacher Mette Holm fears pupils to Nørreholt Skole will "
            "lose the 7.40 a.m. connection."
        ),
        pairs=(
            (
                "Skolebestyrelsen ved Nørreholt Skole blev onsdag orienteret om, at bus nr. 14 i anlægsperioden ikke kan køre ad Kirkevej.",
                "The school board at Nørreholt Skole was told on Wednesday that bus no. 14 cannot use Kirkevej during the construction period.",
            ),
            (
                "Erstatningsruten går via Klintbro og Færgelejet Klintbro og lægger ifølge køreplanen 11 minutter til turen fra Østermarken.",
                "The replacement route goes via Klintbro and Færgelejet Klintbro and, according to the timetable, adds 11 minutes to the trip from Østermarken.",
            ),
            (
                "Skoleleder Mette Holm sagde, at det især rammer elever, der i dag stiger på kl. 07.40 ved Svanedammen og når første time uden at løbe.",
                "Headteacher Mette Holm said it especially hits pupils who today board at 7.40 a.m. at Svanedammen and reach the first lesson without running.",
            ),
            (
                "»Hvis bussen først er ved skolen kl. 08.15, skal vi rykke morgensamlingen, og det vil jeg helst undgå,« sagde hun.",
                "\"If the bus only reaches the school at 8.15 a.m. we will have to move morning assembly, and I would rather not,\" she said.",
            ),
            (
                "Færgeselskabet tilbyder midlertidigt, at elever med skolekort kan stå af ved Pakhuset, hvorfra der er 400 meter gangsti langs Gråfjord.",
                "The ferry company temporarily offers that pupils with a school pass may alight at Pakhuset, from where there is a 400-metre footpath along Gråfjord.",
            ),
            (
                "Kommunen afsætter 0,4 mio. kr. til ekstra morgenafgang i 14 uger og belysning ved stoppestedet på Møllebakken.",
                "The municipality sets aside DKK 0.4 million for an extra morning departure over 14 weeks and lighting at the stop on Møllebakken.",
            ),
            (
                "Ida Frost bad om, at køreplanen også tænker på cykelstien, så elever ikke presses ud på Strandgade mellem lastbilerne.",
                "Ida Frost asked that the timetable also consider the cycle path so pupils are not forced onto Strandgade between the lorries.",
            ),
        ),
    ),
    Article(
        id="tof-003",
        slug="dike-watch",
        title_da="Digelaget kræver kontrol af Gråfjord Dige",
        split="train",
        planted=("clock", "mio-kr", "ordinal-date", "pct"),
        oracle_summary_da=(
            "Digelaget vil have Gråfjord Dige kontrolleret, før Toftevig Havn uddybes. "
            "Kaj Overgaard minder om, at diget blev forhøjet i 2022 for 3,2 mio. kr., "
            "og kræver måling den 3. november kl. 06.00."
        ),
        oracle_summary_en=(
            "The dike guild wants Gråfjord Dige inspected before Toftevig Havn is "
            "dredged. Kaj Overgaard recalls that the dike was raised in 2022 for "
            "DKK 3.2 million and demands a survey on 3 November at 6.00 a.m."
        ),
        pairs=(
            (
                "Digelaget i Toftevig indkaldte til stormøde torsdag den 3. oktober kl. 18.30 i Pakhuset.",
                "The dike guild in Toftevig called a storm meeting on Thursday 3 October at 6.30 p.m. in Pakhuset.",
            ),
            (
                "Formand Kaj Overgaard mindede om, at Gråfjord Dige i 2022 blev forhøjet for 3,2 mio. kr. efter stormfloden, der satte Fiskerihallen under 40 cm vand.",
                "Chair Kaj Overgaard recalled that Gråfjord Dige was raised in 2022 for DKK 3.2 million after the storm surge that put Fiskerihallen under 40 cm of water.",
            ),
            (
                "»Uddybning uden kontrolmåling er at spille hasard med kældre på Strandgade,« sagde han.",
                "\"Dredging without a control survey is gambling with basements on Strandgade,\" he said.",
            ),
            (
                "Forvaltningen svarer, at der er afsat 0,8 mio. kr. til pejlinger t.o.m. den 3. november, første hold møder kl. 06.00 ved Svanedammen.",
                "The administration replies that DKK 0.8 million is set aside for soundings through 3 November; the first crew meets at 6.00 a.m. at Svanedammen.",
            ),
            (
                "En rapport fra 2023 viser, at 12 pct. af digets yderside stadig har sætninger, især ud for Møllebakken.",
                "A 2023 report shows that 12 percent of the dike's outer face still has settlement, especially off Møllebakken.",
            ),
            (
                "Ellen Kragh lovede, at havneudvidelsen ikke får anlægsstart, før digelaget har set måleprotokollen.",
                "Ellen Kragh promised that the harbour expansion will not break ground before the dike guild has seen the survey log.",
            ),
            (
                "Niels Bro tilføjede, at fiskerne kan lægge både i Klintbro i de nætter, hvor prammene arbejder i Gråfjord.",
                "Niels Bro added that the fishers can berth boats in Klintbro on the nights when the barges work in Gråfjord.",
            ),
            (
                "Pejleholdet skal sætte tre faste mærker: ét ved Svanedammen, ét ud for Møllebakken og ét ved Færgelejet Klintbro, så sætninger kan ses uge for uge.",
                "The sounding crew must set three fixed marks: one at Svanedammen, one off Møllebakken and one at Færgelejet Klintbro, so settlement can be seen week by week.",
            ),
            (
                "Hvis ydersiden bevæger sig mere end 2 pct. i forhold til 2022-koten, stopper gravning i sejlrenden, indtil digelaget har godkendt en ny snittegning.",
                "If the outer face moves more than 2 percent relative to the 2022 elevation, digging in the fairway stops until the dike guild has approved a new section drawing.",
            ),
            (
                "Kommunen lover at offentliggøre rådata på toftevig.dk senest kl. 12.00 dagen efter hver måling, jf. åbenhedslinjen i høringen.",
                "The municipality promises to publish raw data on toftevig.dk by 12.00 noon the day after each survey, cf. the openness line in the hearing.",
            ),
            (
                "Ida Frost bad om, at også kældre på Strandgade nr. 9 og nr. 14 fotograferes, fordi beboerne stadig har slanger liggende efter 2022.",
                "Ida Frost asked that basements at Strandgade no. 9 and no. 14 also be photographed, because residents still have hoses lying out after 2022.",
            ),
            (
                "Ellen Kragh sluttede med at sige, at havneudvidelsen kun giver mening, hvis Gråfjord Dige holder, og at det budskab skal stå øverst i høringsbrevet.",
                "Ellen Kragh finished by saying that the harbour expansion only makes sense if Gråfjord Dige holds, and that this message must stand at the top of the hearing letter.",
            ),
        ),
    ),
    Article(
        id="tof-004",
        slug="turbines",
        title_da="Tre møller ved Østermarken til debat",
        split="train",
        planted=("pct", "km", "noise"),
        oracle_summary_da=(
            "Teknik- og miljøudvalget sender tre vindmøller ved Østermarken i debat. "
            "Støjen ved Nørreholt Skole må ifølge udkastet ikke overstige de nuværende "
            "målinger med mere end 2 pct."
        ),
        oracle_summary_en=(
            "The technical and environment committee is putting three wind turbines "
            "at Østermarken out for debate. Noise at Nørreholt Skole must not, according "
            "to the draft, exceed current measurements by more than 2 percent."
        ),
        pairs=(
            (
                "Tre møller på hver 150 meter er foreslået på markerne bag Østermarken, 1,8 km fra Nørreholt Skole.",
                "Three turbines of 150 metres each are proposed in the fields behind Østermarken, 1.8 km from Nørreholt Skole.",
            ),
            (
                "Lars Kjær fra teknik- og miljøudvalget sagde, at projektet kan dække ca. 40 pct. af kommunens eget elforbrug.",
                "Lars Kjær from the technical and environment committee said the project could cover about 40 percent of the municipality's own electricity use.",
            ),
            (
                "Mette Holm kræver, at støjen i skolegården ikke stiger med mere end 2 pct. i forhold til målingen fra 2023.",
                "Mette Holm demands that noise in the schoolyard not rise by more than 2 percent relative to the 2023 measurement.",
            ),
            (
                "Nabohøringen slutter den 1. december, og et borgermøde holdes den 14. november kl. 19.00 i Pakhuset.",
                "The neighbour hearing ends on 1 December, and a public meeting is held on 14 November at 7.00 p.m. in Pakhuset.",
            ),
            (
                "Ida Frost mindede om, at fugletrækket over Gråfjord i marts gør en vinterrejsning af kraner uhensigtsmæssig.",
                "Ida Frost recalled that the bird migration over Gråfjord in March makes a winter raising of cranes inappropriate.",
            ),
            (
                "Søren Vibe vil have skrevet ind, at kablerne ikke må krydse Gråfjord Dige uden digelagets samtykke.",
                "Søren Vibe wants it written in that the cables may not cross Gråfjord Dige without the dike guild's consent.",
            ),
        ),
    ),
    Article(
        id="tof-005",
        slug="ferry-times",
        title_da="Klintbro-færgen rykker morgenafgangen",
        split="train",
        planted=("clock", "kl-split-trap"),
        oracle_summary_da=(
            "Færgen fra Færgelejet Klintbro rykker morgenafgangen fra kl. 06.15 til "
            "kl. 06.05, så lastbiler til Toftevig Havn er væk før bus nr. 14."
        ),
        oracle_summary_en=(
            "The ferry from Færgelejet Klintbro moves the morning departure from "
            "6.15 a.m. to 6.05 a.m. so lorries for Toftevig Havn are gone before bus no. 14."
        ),
        pairs=(
            (
                "Færgeselskabet ændrer køreplanen fra mandag den 21. oktober, så første afgang fra Færgelejet Klintbro sker kl. 06.05 i stedet for kl. 06.15.",
                "The ferry company changes the timetable from Monday 21 October so the first departure from Færgelejet Klintbro is at 6.05 a.m. instead of 6.15 a.m.",
            ),
            (
                "Begrundelsen er, at lastbiler til anlægsarbejdet i Toftevig Havn skal være over Gråfjord, før bus nr. 14 kommer til stoppestedet kl. 07.40.",
                "The reason is that lorries for the works in Toftevig Havn must be across Gråfjord before bus no. 14 reaches the stop at 7.40 a.m.",
            ),
            (
                "Amina Rashid, der pendler til biblioteket, sagde, at kl. 06.05 rammer natholdet i Pakhuset, men giver ro til skoleeleverne.",
                "Amina Rashid, who commutes to the library, said 6.05 a.m. hits the night shift in Pakhuset but gives calm to the school pupils.",
            ),
            (
                "Retur fra Toftevig Havn bliver kl. 16.50 t.o.m. vinterfartplanen, med en ekstra tur kl. 18.10 om torsdagen, hvor udvalgene mødes.",
                "The return from Toftevig Havn will be at 4.50 p.m. through the winter timetable, with an extra run at 6.10 p.m. on Thursdays when the committees meet.",
            ),
            (
                "Billetter koster fortsat 28 kr., og skolekort gælder uændret, jf. færgeselskabets takstblad.",
                "Tickets still cost DKK 28, and school passes remain valid, cf. the ferry company's tariff sheet.",
            ),
        ),
    ),
    Article(
        id="tof-006",
        slug="library-hours",
        title_da="Biblioteket flytter depot til Kirkevej",
        split="validation",
        planted=("hours", "quote"),
        oracle_summary_da=(
            "Biblioteket flytter sit depot til kælderen under Kirkevej, mens Pakhuset "
            "bruges til havnemøder. Amina Rashid holder åbent tirsdag og torsdag kl. 14.00–18.00."
        ),
        oracle_summary_en=(
            "The library is moving its depot to the basement on Kirkevej while Pakhuset "
            "is used for harbour meetings. Amina Rashid keeps opening hours Tuesday and "
            "Thursday 2.00–6.00 p.m."
        ),
        pairs=(
            (
                "Biblioteksleder Amina Rashid meddeler, at magasinets kasser flyttes fra Pakhuset til kælderen under Kirkevej i uge 43.",
                "Library director Amina Rashid announces that the stack boxes will move from Pakhuset to the basement on Kirkevej in week 43.",
            ),
            (
                "Pakhuset skal i anlægsperioden bruges til samråd, digelag og midlertidigt koldt rum, og der er ikke plads til både ismaskiner og romaner.",
                "During the works Pakhuset will be used for consultations, the dike guild and a temporary cold room, and there is no space for both ice machines and novels.",
            ),
            (
                "Udlånsskranken holder åbent tirsdag og torsdag kl. 14.00–18.00, og lørdagsvagten kl. 10.00–13.00 indstilles t.o.m. den 12. december.",
                "The circulation desk stays open Tuesday and Thursday 2.00–6.00 p.m., and the Saturday shift 10.00 a.m.–1.00 p.m. is paused through 12 December.",
            ),
            (
                "»Vi pakker bl.a. lokalhistorien om Gråfjord Dige og fiskeriprotokollerne fra Fiskerihallen, så de ikke står i træk,« sagde Rashid.",
                "\"We are packing, among other things, the local history of Gråfjord Dige and the fisher logs from Fiskerihallen so they do not sit in a draught,\" Rashid said.",
            ),
            (
                "Skoleklasser fra Nørreholt Skole booker fortsat besøg, men indgangen bliver fra Strandgade nr. 9 i stedet for gården ved Møllebakken.",
                "School classes from Nørreholt Skole still book visits, but the entrance will be from Strandgade no. 9 instead of the yard at Møllebakken.",
            ),
        ),
    ),
    Article(
        id="tof-007",
        slug="cycle-path",
        title_da="Cykelsti fra Østermarken til havnen",
        split="validation",
        planted=("km", "mio-kr"),
        oracle_summary_da=(
            "Kommunen vil forbinde cykelstien fra Østermarken med Toftevig Havn for "
            "2,1 mio. kr. Ruten er 3,4 km og skal holde elever væk fra lastbiler på Strandgade."
        ),
        oracle_summary_en=(
            "The municipality wants to connect the cycle path from Østermarken to "
            "Toftevig Havn for DKK 2.1 million. The route is 3.4 km and should keep "
            "pupils off Strandgade among the lorries."
        ),
        pairs=(
            (
                "Teknik- og miljøudvalget indstiller en cykelsti på 3,4 km fra Østermarken langs Gråfjord til Toftevig Havn.",
                "The technical and environment committee recommends a 3.4 km cycle path from Østermarken along Gråfjord to Toftevig Havn.",
            ),
            (
                "Anlægsoverslaget er 2,1 mio. kr., heraf 0,3 mio. kr. til belysning ved Svanedammen og en broskinne over det lave løb ved Møllebakken.",
                "The works estimate is DKK 2.1 million, of which DKK 0.3 million is for lighting at Svanedammen and a bridge plate over the low run at Møllebakken.",
            ),
            (
                "Mette Holm kalder stien en forudsætning for, at bus nr. 14 kan lægges om uden at elever cykler i lastbilsporet på Strandgade.",
                "Mette Holm calls the path a precondition for rerouting bus no. 14 without pupils cycling in the lorry lane on Strandgade.",
            ),
            (
                "Kaj Overgaard kræver, at stiens fundering ikke borehulles i Gråfjord Dige, men lægges på indersiden mod Østermarken.",
                "Kaj Overgaard demands that the path's foundation not be drilled into Gråfjord Dige, but laid on the inner side toward Østermarken.",
            ),
            (
                "Hvis pengene vedtages den 12. november, kan asfalten lægges i april, f.o.m. uge 15.",
                "If the money is adopted on 12 November, the asphalt can be laid in April, from week 15.",
            ),
        ),
    ),
    Article(
        id="tof-008",
        slug="long-sentence-saw",
        title_da="Én lang indstilling med mange kommaer",
        split="train",
        planted=("character-saw", "comma-chain", "mio-kr"),
        oracle_summary_da=(
            "Havneudvalget vil have én samlet indstilling om kaj, sejlrender, pakhus, "
            "bus nr. 14 og Gråfjord Dige, før høringen. Overslaget er 18,4 mio. kr."
        ),
        oracle_summary_en=(
            "The harbour committee wants one combined memorandum on the quay, fairway, "
            "warehouse, bus no. 14 and Gråfjord Dige before the hearing. The estimate "
            "is DKK 18.4 million."
        ),
        pairs=(
            (
                _long_comma_sentence_da(),
                _long_comma_sentence_en(),
            ),
            (
                "Punktet sættes på dagsordenen den 12. oktober kl. 19.30.",
                "The item is placed on the agenda on 12 October at 7.30 p.m.",
            ),
        ),
    ),
    Article(
        id="tof-009",
        slug="short-notice",
        title_da="Kort meddelelse om Pakhuset",
        split="test",
        planted=("single-pane",),
        oracle_summary_da=(
            "Pakhuset på Strandgade er åbent torsdag kl. 18.30 til digelagets møde."
        ),
        oracle_summary_en=(
            "Pakhuset on Strandgade is open Thursday at 6.30 p.m. for the dike guild meeting."
        ),
        pairs=(
            (
                "Pakhuset på Strandgade holdes åbent torsdag kl. 18.30, hvor digelaget gennemgår pejlingerne ved Gråfjord Dige.",
                "Pakhuset on Strandgade will be kept open on Thursday at 6.30 p.m., when the dike guild reviews the soundings at Gråfjord Dige.",
            ),
            (
                "Deltagelse er gratis, og kaffe sælges til 12 kr. til fordel for belysning ved Svanedammen.",
                "Attendance is free, and coffee is sold for DKK 12 in aid of lighting at Svanedammen.",
            ),
        ),
    ),
    Article(
        id="tof-010",
        slug="overlong-back",
        title_da="Protokol der ikke vil i ét vindue",
        split="test",
        planted=("empty-list-scar", "over-budget-singleton"),
        oracle_summary_da=(
            "Pakhusets protokol opregner kasser med is og reb, før natholdet lukker porten."
        ),
        oracle_summary_en=(
            "The packing house ledger lists crates of ice and rope before the night shift closes the gate."
        ),
        pairs=(
            (
                _overlong_danish_blob(),
                _overlong_english_blob(),
            ),
        ),
    ),
)


ARTICLE_BY_ID = {article.id: article for article in ARTICLES}


def get_article(article_id: str) -> Article:
    try:
        return ARTICLE_BY_ID[article_id]
    except KeyError as exc:
        known = ", ".join(ARTICLE_BY_ID)
        raise KeyError(f"unknown article {article_id!r}; choose from {known}") from exc


def articles_for_split(split: str) -> tuple[Article, ...]:
    return tuple(a for a in ARTICLES if a.split == split)
