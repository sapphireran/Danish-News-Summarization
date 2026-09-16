"""Closed-world Sejerø briefs. Fiction only — no scraped news, no live wires.

Each article is written by hand in Danish, then taken through the same hops
the 2023 course scripts ran on a GPU: English body, a short English silver
summary in the style of ``mrm8488/t5-base-finetuned-summarize-news``, and a
slightly drifted Danish back-translation. An oracle Danish summary sits next
to the silver label so the desk can score what a careful human lede kept.
"""

from __future__ import annotations

from sejeroe.models import Article, PlantedError, Quote, SlotCard

ARTICLES: tuple[Article, ...] = (
    Article(
        id="SEJ-001",
        headline_da="Sejerøfærgen til Havnsø aflyst i eftermiddag",
        split="train",
        body_da=(
            "Sejerøfærgen til Havnsø bliver i eftermiddag aflyst på grund af kuling "
            "fra nordvest, oplyser havnefoged Karen Møller. Ifølge hende ventes næste "
            "afgang først kl. 18.30, hvis vinden lægger sig under 15 meter i sekundet. "
            "Omkring 40 passagerer venter i terminalen i Sejerby, og flere har møder "
            "på Sjælland. »Vi sætter en ekstra afgang ind i aften, hvis vejret tillader "
            "det,« siger Møller. Rederiet anbefaler, at rejsende følger SMS-varslingen, "
            "men understreger at cykler og varebiler først kommer med på den sene tur."
        ),
        body_en=(
            "The Sejerø ferry to Havnsø is cancelled this afternoon because of a "
            "north-westerly gale, harbour master Karen Møller said. According to her "
            "the next sailing is not expected before 18.30, if the wind drops below "
            "15 metres per second. About 40 passengers are waiting in the Sejerby "
            "terminal, and several have meetings on Zealand. \"We will put on an extra "
            "sailing this evening if the weather allows it,\" Møller said. The operator "
            "asks travellers to follow the SMS alert, but stresses that bicycles and "
            "vans will only travel on the late sailing."
        ),
        summary_en=(
            "The Sejerø ferry to Havnsø is cancelled this afternoon because of a gale, "
            "the harbour master said. A later sailing may run at 18.30."
        ),
        summary_da=(
            "Færgen til Havnsø er aflyst i eftermiddag på grund af kuling, sagde "
            "havnefogeden. En senere sejlads kan køre kl. 18.30."
        ),
        oracle_da=(
            "Sejerøfærgen til Havnsø er aflyst i eftermiddag på grund af kuling. "
            "Havnefoged Karen Møller venter næste afgang tidligst kl. 18.30 og varsler "
            "en ekstra aftenafgang, hvis vejret tillader det."
        ),
        slots=SlotCard(
            who="Karen Møller",
            what="færgeafgang aflyst",
            when="i eftermiddag",
            where="Havnsø",
            why="kuling fra nordvest",
            how="SMS-varsling og mulig ekstra aftenafgang",
            aliases={
                "who": ("havnefoged", "Møller", "harbour master"),
                "what": ("færgen", "aflyst", "cancelled", "Sejerøfærgen"),
                "when": ("eftermiddag", "18.30", "afternoon"),
                "where": ("Sejerby", "Havnsø", "Sejerø"),
                "why": ("kuling", "gale", "nordvest"),
                "how": ("SMS", "ekstra afgang", "extra sailing"),
            },
        ),
        quotes=(
            Quote(
                speaker="Karen Møller",
                danish="Vi sætter en ekstra afgang ind i aften, hvis vejret tillader det",
                english="We will put on an extra sailing this evening if the weather allows it",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("Ifølge", "hvis", "men"),
        planted=(
            PlantedError(
                kind="who-swap",
                summary_da=(
                    "Kalundborg-færgen er aflyst i eftermiddag på grund af kuling, "
                    "sagde havnefogeden. En senere sejlads kan køre kl. 18.30."
                ),
                dropped_slots=("who", "where"),
                note="Swaps the operator's route onto a different Kattegat town.",
            ),
            PlantedError(
                kind="when-drop",
                summary_da="Færgen til Havnsø er aflyst på grund af kuling, sagde havnefogeden.",
                dropped_slots=("when",),
                note="Keeps the event but strips the manchet's time.",
            ),
        ),
    ),
    Article(
        id="SEJ-002",
        headline_da="Forældre protesterer mod plan om at lukke ø-skolen",
        split="train",
        body_da=(
            "Sejerø Skole kan miste 3. til 6. klasse fra næste august, fordi der kun "
            "er 27 elever tilbage på de fire årgange. Kommunalbestyrelsen i Kalundborg "
            "behandler forslaget onsdag aften. Forældrene har samlet 118 underskrifter "
            "og møder op med fakler ved færgelejet. »Børnene skal ikke bruge to timer "
            "på færge og bus for at nå en time i skole,« siger lærer Ida Kruse. "
            "Skoleledelsen peger på, at en sammenlægning på Sjælland sparer 1,2 millioner "
            "kroner, men understreger at SFO'en på øen bliver i Sejerby."
        ),
        body_en=(
            "Sejerø School may lose years 3 to 6 from next August, because only 27 "
            "pupils remain across the four year-groups. Kalundborg municipal council "
            "takes the proposal on Wednesday evening. Parents have collected 118 "
            "signatures and will meet with torches at the ferry berth. \"The children "
            "should not spend two hours on a ferry and a bus to reach one hour of "
            "school,\" teacher Ida Kruse said. School leaders note that a merger on "
            "Zealand would save 1.2 million kroner, but stress that the after-school "
            "club stays in Sejerby."
        ),
        summary_en=(
            "Sejerø School may close years 3 to 6 next August because of 27 pupils. "
            "Parents will protest at the ferry berth on Wednesday."
        ),
        summary_da=(
            "Sejerø Skole kan lukke 3. til 6. klasse næste august på grund af 27 elever. "
            "Forældre vil protestere ved færgelejet onsdag."
        ),
        oracle_da=(
            "Sejerø Skole kan miste 3. til 6. klasse fra næste august, fordi der kun "
            "er 27 elever. Forældre protesterer onsdag ved færgelejet, mens lærer Ida "
            "Kruse advarer mod to timers skolevej."
        ),
        slots=SlotCard(
            who="Ida Kruse",
            what="forslag om at lukke 3.-6. klasse",
            when="næste august",
            where="Sejerø Skole",
            why="27 elever på fire årgange",
            how="118 underskrifter og fakler ved færgelejet",
            aliases={
                "who": ("Ida Kruse", "lærer", "teacher", "forældre"),
                "what": ("lukke", "3. til 6.", "years 3", "ø-skolen"),
                "when": ("august", "onsdag", "Wednesday", "næste august"),
                "where": ("Sejerø Skole", "Sejerby", "færgelejet"),
                "why": ("27 elever", "27 pupils", "27"),
                "how": ("underskrifter", "fakler", "signatures", "torches"),
            },
        ),
        quotes=(
            Quote(
                speaker="Ida Kruse",
                danish="Børnene skal ikke bruge to timer på færge og bus for at nå en time i skole",
                english="The children should not spend two hours on a ferry and a bus to reach one hour of school",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("fordi", "men"),
        planted=(
            PlantedError(
                kind="why-flip",
                summary_da=(
                    "Sejerø Skole kan lukke 3. til 6. klasse næste august, fordi der er "
                    "for mange elever. Forældre vil protestere ved færgelejet onsdag."
                ),
                dropped_slots=("why",),
                note="Flips the enrolment argument from too few to too many.",
            ),
        ),
    ),
    Article(
        id="SEJ-003",
        headline_da="Mudring af Sejerby Havn begynder mandag",
        split="train",
        body_da=(
            "Mandag morgen går gravemaskinerne i gang med at fjerne 12.000 kubikmeter "
            "slam fra Sejerby Havn. Arbejdet varer tre uger og spærrer den indre kaj "
            "for kuttere over 12 meter. Fisker Niels Abildgaard frygter, at jomfruhummere "
            "og rødspætter må landes i Havnsø i stedet. »Vi kan godt tåle en uge, men "
            "ikke tre, hvis isen kommer tidligt,« siger han. Kommunen lover en daglig "
            "sliske ved den ydre mole, hvis bølgerne holder sig under en meter."
        ),
        body_en=(
            "On Monday morning excavators begin removing 12,000 cubic metres of silt "
            "from Sejerby Harbour. The work lasts three weeks and closes the inner quay "
            "to cutters longer than 12 metres. Fisherman Niels Abildgaard fears that "
            "langoustines and plaice will have to be landed in Havnsø instead. \"We can "
            "stand one week, but not three if the ice comes early,\" he said. The "
            "municipality promises a daily slipway at the outer mole if the waves stay "
            "below one metre."
        ),
        summary_en=(
            "Excavators will dredge 12,000 cubic metres from Sejerby Harbour from Monday. "
            "The inner quay closes for three weeks."
        ),
        summary_da=(
            "Gravemaskiner mudrer 12.000 kubikmeter fra Sejerby Havn fra mandag. "
            "Den indre kaj lukker i tre uger."
        ),
        oracle_da=(
            "Mudringen af Sejerby Havn begynder mandag og fjerner 12.000 kubikmeter slam. "
            "Den indre kaj er spærret i tre uger, og fisker Niels Abildgaard advarer mod "
            "is, hvis arbejdet trækker ud."
        ),
        slots=SlotCard(
            who="Niels Abildgaard",
            what="mudring af 12.000 kubikmeter slam",
            when="mandag morgen",
            where="Sejerby Havn",
            why="slam i indsejlingen",
            how="indre kaj spærret i tre uger",
            aliases={
                "who": ("Niels Abildgaard", "fisker", "fisherman"),
                "what": ("mudring", "12.000", "12,000", "dredge"),
                "when": ("mandag", "Monday", "tre uger", "three weeks"),
                "where": ("Sejerby Havn", "Sejerby", "indre kaj"),
                "why": ("slam", "silt"),
                "how": ("spærret", "closes", "tre uger"),
            },
        ),
        quotes=(
            Quote(
                speaker="Niels Abildgaard",
                danish="Vi kan godt tåle en uge, men ikke tre, hvis isen kommer tidligt",
                english="We can stand one week, but not three if the ice comes early",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("men", "hvis"),
        planted=(
            PlantedError(
                kind="number-swap",
                summary_da=(
                    "Gravemaskiner mudrer 1.200 kubikmeter fra Sejerby Havn fra mandag. "
                    "Den indre kaj lukker i tre uger."
                ),
                dropped_slots=("what",),
                note="Drops an order of magnitude from the dredge volume.",
            ),
        ),
    ),
    Article(
        id="SEJ-004",
        headline_da="Høring om to kystmøller samler 150 øboere",
        split="train",
        body_da=(
            "To 150 meter høje kystmøller vest for Sejerø Fyr er til høring i aften i "
            "forsamlingshuset. Borgmester Trine Holm kalder projektet nødvendigt, fordi "
            "øen henter 80 procent af sin strøm via søkablet til Sjælland. Turistforeningen "
            "er imod, da møllerne vil stå i solnedgangen over Nekselø. »Vi vil have strøm, "
            "men ikke en industrihorisont,« siger formand Per Bang. Hvis høringen ender "
            "uden flertal, udskydes ansøgningen til foråret."
        ),
        body_en=(
            "Two 150-metre coastal turbines west of Sejerø Lighthouse are up for hearing "
            "tonight in the village hall. Mayor Trine Holm calls the project necessary "
            "because the island draws 80 percent of its power through the sea cable to "
            "Zealand. The tourist association opposes it, since the turbines would sit "
            "in the sunset over Nekselø. \"We want power, but not an industrial "
            "horizon,\" chair Per Bang said. If the hearing ends without a majority, "
            "the application is postponed until spring."
        ),
        summary_en=(
            "A hearing tonight will decide on two 150-metre turbines west of Sejerø "
            "Lighthouse. The tourist association opposes the plan."
        ),
        summary_da=(
            "En høring i aften skal afgøre to 150 meter høje møller vest for Sejerø Fyr. "
            "Turistforeningen er imod planen."
        ),
        oracle_da=(
            "To 150 meter kystmøller vest for Sejerø Fyr er til høring i aften. "
            "Borgmester Trine Holm peger på søkablet, mens Per Bang fra turistforeningen "
            "advarer mod en industrihorisont over Nekselø."
        ),
        slots=SlotCard(
            who="Trine Holm",
            what="høring om to kystmøller",
            when="i aften",
            where="forsamlingshuset",
            why="80 procent af strømmen kommer via søkabel",
            how="høring og mulig forårsudsættelse",
            aliases={
                "who": ("Trine Holm", "borgmester", "Per Bang", "mayor"),
                "what": ("kystmøller", "150 meter", "turbines", "høring"),
                "when": ("i aften", "tonight", "foråret"),
                "where": ("forsamlingshuset", "Sejerø Fyr", "Nekselø"),
                "why": ("søkabel", "80 procent", "80 percent", "strøm"),
                "how": ("høring", "hearing", "udskydes"),
            },
        ),
        quotes=(
            Quote(
                speaker="Per Bang",
                danish="Vi vil have strøm, men ikke en industrihorisont",
                english="We want power, but not an industrial horizon",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("fordi", "men", "Hvis"),
        planted=(
            PlantedError(
                kind="quote-loss",
                summary_da=(
                    "En høring i aften skal afgøre to 150 meter høje møller vest for "
                    "Sejerø Fyr. Turistforeningen er imod planen."
                ),
                dropped_slots=(),
                note="Same silver text: the quote never entered the T5-like hop.",
            ),
        ),
    ),
    Article(
        id="SEJ-005",
        headline_da="Købmanden går på vintertid og lukker søndage",
        split="train",
        body_da=(
            "Fra 1. november holder Sejerø Købmand lukket om søndagen, og hverdagene "
            "slutter kl. 17. Indehaver Lene Frost siger, at novemberomsætningen faldt "
            "med 22 procent sidste år, fordi de faste øboere handler i Kalundborg. "
            "Pensionister kan stadig bestille mælk og brød til færgelejet om morgenen. "
            "»Jeg lukker ikke butikken, men jeg kan ikke betale tre søndagsvagter for "
            "otte kunder,« siger Frost. Hvis en færge bliver indstillet, åbner hun "
            "alligevel en time efter ankomst."
        ),
        body_en=(
            "From 1 November Sejerø Grocery will close on Sundays, and weekdays will "
            "end at 17.00. Owner Lene Frost says November sales fell 22 percent last "
            "year because year-round islanders shop in Kalundborg. Pensioners can still "
            "order milk and bread to the ferry berth in the morning. \"I am not closing "
            "the shop, but I cannot pay three Sunday shifts for eight customers,\" "
            "Frost said. If a ferry is cancelled she will still open for an hour after "
            "arrival."
        ),
        summary_en=(
            "Sejerø Grocery will close on Sundays from 1 November and end weekdays at "
            "17.00. The owner says November sales fell 22 percent."
        ),
        summary_da=(
            "Sejerø Købmand lukker om søndagen fra 1. november og slutter hverdage kl. 17. "
            "Indehaveren siger, at novemberomsætningen faldt 22 procent."
        ),
        oracle_da=(
            "Sejerø Købmand lukker søndage fra 1. november og hverdage kl. 17, fordi "
            "novemberomsætningen faldt 22 procent. Lene Frost holder butikken åben, men "
            "siger nej til tre søndagsvagter for otte kunder."
        ),
        slots=SlotCard(
            who="Lene Frost",
            what="søndagslukning og kortere hverdage",
            when="1. november",
            where="Sejerø Købmand",
            why="novemberomsætning faldt 22 procent",
            how="bestilling til færgelejet og åbning efter indstillet færge",
            aliases={
                "who": ("Lene Frost", "indehaver", "owner"),
                "what": ("lukket om søndagen", "lukker om søndagen", "close on Sundays"),
                "when": ("1. november", "1 November", "november"),
                "where": ("Sejerø Købmand", "færgelejet"),
                "why": ("faldt 22 procent", "faldt med 22", "fell 22 percent", "sales fell"),
                "how": ("bestille", "åbner", "order"),
            },
        ),
        quotes=(
            Quote(
                speaker="Lene Frost",
                danish="Jeg lukker ikke butikken, men jeg kan ikke betale tre søndagsvagter for otte kunder",
                english="I am not closing the shop, but I cannot pay three Sunday shifts for eight customers",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("fordi", "men", "Hvis"),
        planted=(
            PlantedError(
                kind="polarity-flip",
                summary_da=(
                    "Sejerø Købmand udvider søndagsåbning fra 1. november og slutter "
                    "hverdage kl. 17. Indehaveren siger, at novemberomsætningen steg 22 procent."
                ),
                dropped_slots=("what", "why"),
                note="Turns a winter cut into an expansion and flips the sales figure.",
            ),
        ),
    ),
    Article(
        id="SEJ-006",
        headline_da="Frivilligt brandværn får ny tankvogn",
        split="validation",
        body_da=(
            "Sejerø Frivillige Brandværn henter lørdag en ny tankvogn til 1,8 millioner "
            "kroner, betalt af en ø-indsamling og en pulje i Beredskabsstyrelsen. "
            "Holdleder Morten Dahl siger, at den gamle vogn ikke kunne nå Klintgården "
            "med mere end 800 liter. Den nye tank rummer 3.000 liter og kan suge vand "
            "direkte fra stranden ved Mastrup. »Vi øver slukning ved stranden kl. 11, "
            "og alle er velkomne,« siger Dahl. Hvis vestenvinden er hård, flyttes "
            "demonstrationen ind bag kirken."
        ),
        body_en=(
            "Sejerø Volunteer Fire Brigade collects a new tanker on Saturday, costing "
            "1.8 million kroner and paid by an island collection plus a Danish Emergency "
            "Management Agency grant. Crew leader Morten Dahl says the old vehicle could "
            "not reach Klintgården with more than 800 litres. The new tank holds 3,000 "
            "litres and can draw water from the beach at Mastrup. \"We will drill on "
            "the beach at 11, and everyone is welcome,\" Dahl said. If the westerly is "
            "hard, the demonstration moves in behind the church."
        ),
        summary_en=(
            "Sejerø's volunteer fire brigade will collect a 1.8 million kroner tanker "
            "on Saturday. A public drill is planned at 11 on the beach."
        ),
        summary_da=(
            "Sejerøs frivillige brandværn henter lørdag en tankvogn til 1,8 millioner kroner. "
            "Der er offentlig øvelse kl. 11 på stranden."
        ),
        oracle_da=(
            "Sejerø Frivillige Brandværn henter lørdag en tankvogn til 1,8 millioner kroner. "
            "Holdleder Morten Dahl viser den 3.000 liter store vogn ved en øvelse kl. 11 "
            "på stranden ved Mastrup."
        ),
        slots=SlotCard(
            who="Morten Dahl",
            what="ny tankvogn til 1,8 millioner kroner",
            when="lørdag kl. 11",
            where="stranden ved Mastrup",
            why="gammel vogn kunne kun medbringe 800 liter",
            how="ø-indsamling og statslig pulje",
            aliases={
                "who": ("Morten Dahl", "holdleder", "crew leader"),
                "what": ("tankvogn", "1,8", "1.8", "tanker"),
                "when": ("lørdag", "Saturday", "kl. 11"),
                "where": ("Mastrup", "stranden", "Klintgården"),
                "why": ("800 liter", "800 litres"),
                "how": ("indsamling", "pulje", "collection"),
            },
        ),
        quotes=(
            Quote(
                speaker="Morten Dahl",
                danish="Vi øver slukning ved stranden kl. 11, og alle er velkomne",
                english="We will drill on the beach at 11, and everyone is welcome",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("Hvis",),
        planted=(
            PlantedError(
                kind="when-drop",
                summary_da=(
                    "Sejerøs frivillige brandværn henter en tankvogn til 1,8 millioner kroner. "
                    "Der er offentlig øvelse på stranden."
                ),
                dropped_slots=("when",),
                note="Drops Saturday and 11 o'clock from the manchet.",
            ),
        ),
    ),
    Article(
        id="SEJ-007",
        headline_da="Kirketag får stillads i seks uger",
        split="validation",
        body_da=(
            "Sejerø Kirke får stillads om tårnet fra mandag, mens taget skiftes for "
            "2,4 millioner kroner. Pengene kommer fra en fond på Holbæk og fra menighedsrådet. "
            "Kirkegængere skal bruge sideindgangen ved præstegården, og døbefonten flyttes "
            "midlertidigt ned i skibet. »Vi holder gudstjeneste alligevel, men uden klokker "
            "de første to uger,« siger kirkeværge Anne Lisbjerg. Hvis der kommer slud, "
            "pauses arbejdet, så skiferne ikke glider."
        ),
        body_en=(
            "Sejerø Church will have scaffolding around the tower from Monday while the "
            "roof is replaced for 2.4 million kroner. The money comes from a foundation "
            "in Holbæk and from the parish council. Worshippers must use the side door "
            "by the rectory, and the font is moved temporarily into the nave. \"We will "
            "still hold the service, but without bells for the first two weeks,\" church "
            "warden Anne Lisbjerg said. If sleet arrives the work pauses so the slates "
            "do not slide."
        ),
        summary_en=(
            "Sejerø Church gets scaffolding from Monday while a 2.4 million kroner roof "
            "is replaced. Services continue through the side door."
        ),
        summary_da=(
            "Sejerø Kirke får stillads fra mandag, mens et tag til 2,4 millioner kroner "
            "skiftes. Gudstjenester fortsætter via sidedøren."
        ),
        oracle_da=(
            "Sejerø Kirke får stillads fra mandag, mens taget skiftes for 2,4 millioner "
            "kroner. Kirkeværge Anne Lisbjerg holder gudstjeneste uden klokker de første "
            "to uger og henviser til sidedøren ved præstegården."
        ),
        slots=SlotCard(
            who="Anne Lisbjerg",
            what="udskiftning af kirketag",
            when="fra mandag",
            where="Sejerø Kirke",
            why="taget skal skiftes",
            how="stillads i seks uger og sidedør ved præstegården",
            aliases={
                "who": ("Anne Lisbjerg", "kirkeværge", "church warden"),
                "what": ("kirketag", "2,4", "2.4", "roof"),
                "when": ("mandag", "Monday", "seks uger", "to uger"),
                "where": ("Sejerø Kirke", "præstegården"),
                "why": ("taget", "skiftes", "replaced"),
                "how": ("stillads", "scaffolding", "sidedøren"),
            },
        ),
        quotes=(
            Quote(
                speaker="Anne Lisbjerg",
                danish="Vi holder gudstjeneste alligevel, men uden klokker de første to uger",
                english="We will still hold the service, but without bells for the first two weeks",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("men", "Hvis"),
        planted=(
            PlantedError(
                kind="who-swap",
                summary_da=(
                    "Sejerø Kirke får stillads fra mandag, mens et tag til 2,4 millioner "
                    "kroner skiftes. Borgmesteren lover gudstjenester via sidedøren."
                ),
                dropped_slots=("who",),
                note="Replaces the warden with the mayor, who is not in this brief.",
            ),
        ),
    ),
    Article(
        id="SEJ-008",
        headline_da="Sæler på nordstranden skal have 100 meters fred",
        split="test",
        body_da=(
            "En flok på 14 spættede sæler har de seneste dage ligget på sandbanken "
            "nord for Mastrup. Naturstyrelsen beder gående om at holde 100 meters "
            "afstand, især i weekenden hvor hunde luftes løse. Skovfoged Emil Ravn "
            "siger, at to hvalpe blev skilt fra hunnerne sidste søndag, da en drone "
            "fløj for tæt. »Sælerne er ikke syge, men de skal have ro til at fælde,« "
            "siger han. Hvis vinden vender til øst, forventer han at dyrene rykker "
            "ud på revet ved Sejerø Fyr."
        ),
        body_en=(
            "A group of 14 harbour seals has spent the last few days on the sandbank "
            "north of Mastrup. The Nature Agency asks walkers to keep 100 metres away, "
            "especially at weekends when dogs are walked off the lead. Forester Emil "
            "Ravn says two pups were separated from the females last Sunday when a "
            "drone flew too close. \"The seals are not ill, but they need quiet to "
            "moult,\" he said. If the wind turns easterly he expects the animals to "
            "move out onto the reef by Sejerø Lighthouse."
        ),
        summary_en=(
            "Fourteen harbour seals are resting on the sandbank north of Mastrup. "
            "Walkers are asked to keep 100 metres away after a drone scare last Sunday."
        ),
        summary_da=(
            "14 spættede sæler hviler på sandbanken nord for Mastrup. Gående bedes holde "
            "100 meters afstand efter et droneuheld sidste søndag."
        ),
        oracle_da=(
            "14 spættede sæler ligger på sandbanken nord for Mastrup. Skovfoged Emil Ravn "
            "beder om 100 meters afstand, efter at en drone sidste søndag skilte to hvalpe "
            "fra hunnerne."
        ),
        slots=SlotCard(
            who="Emil Ravn",
            what="anmodning om 100 meters afstand til sæler",
            when="sidste søndag / i weekenden",
            where="sandbanken nord for Mastrup",
            why="drone fløj for tæt og skilte hvalpe fra hunnerne",
            how="skiltning og henvisning til revet ved fyret",
            aliases={
                "who": ("Emil Ravn", "skovfoged", "forester", "Naturstyrelsen"),
                "what": ("100 meter", "100 metres", "sæler", "seals"),
                "when": ("søndag", "Sunday", "weekenden"),
                "where": ("Mastrup", "sandbanken", "Sejerø Fyr"),
                "why": ("drone", "hvalpe", "pups"),
                "how": ("afstand", "revet", "keep"),
            },
        ),
        quotes=(
            Quote(
                speaker="Emil Ravn",
                danish="Sælerne er ikke syge, men de skal have ro til at fælde",
                english="The seals are not ill, but they need quiet to moult",
                cue_da="siger",
                cue_en="said",
            ),
        ),
        connectives_da=("men", "Hvis"),
        planted=(
            PlantedError(
                kind="why-flip",
                summary_da=(
                    "14 spættede sæler hviler på sandbanken nord for Mastrup. Gående bedes "
                    "holde 100 meters afstand, fordi dyrene er syge."
                ),
                dropped_slots=("why",),
                note="Contradicts the ranger: the quote said the seals are not ill.",
            ),
        ),
    ),
)


def article_by_id(article_id: str) -> Article:
    for article in ARTICLES:
        if article.id == article_id:
            return article
    raise KeyError(f"unknown article id: {article_id}")


def articles_for_split(split: str) -> tuple[Article, ...]:
    return tuple(article for article in ARTICLES if article.split == split)
