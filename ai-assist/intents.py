from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Intent knowledge base – extend / load from file / DB as needed
# ---------------------------------------------------------------------------

INTENTS: List[Dict[str, Any]] = [
    {
        "intent": "Bezwaar parkeerboete",
        "intentcode": "objection_parking_fine",
        "steps": [
            {
                "title": "Waarom bent u het niet eens met dit besluit?",
                "description": "Bijvoorbeeld onjuiste gegevens of onredelijkheid."
            },
            {
                "title": "Wat is uw gewenste uitkomst?",
                "description": "Bijvoorbeeld herziening of kwijtschelding."
            },
            {
                "title": "Wat is het nummerbord?",
                "description": "Geef het kenteken van het voertuig waarvoor de boete is uitgeschreven."
            },
            {
                "title": "Wat is de datum?",
                "description": "Geef de datum waarop de parkeerboete is uitgeschreven."
            },
        ]
    },
    {
        "intent": "Melding Parkeerprobleem",
        "intentcode": "report_parking_issue",
        "steps": [
            {
                "title": "Wat is het probleem?",
                "description": "Bijvoorbeeld fout geparkeerd voertuig of defecte automaat."
            },
            {
                "title": "Waar is het probleem?",
                "description": "Geef het adres, de straatnaam of een locatiebeschrijving."
            },
            {
                "title": "Wanneer heeft het probleem plaatsgevonden?",
                "description": "Geef de datum en tijd van het probleem."
            },
            {
                "title": "Eventuele aanvullende details",
                "description": "Bijvoorbeeld kenteken van het voertuig of automaatnummer."
            },
        ]
    },
    {
        "intent": "Melding Openbare Ruimte",
        "intentcode": "report_public_space_issue",
        "steps": [
            {
                "title": "Wat is het probleem?",
                "description": "Bijvoorbeeld kapotte lantaarnpaal, zwerfafval of verzakte stoep."
            },
            {
                "title": "Waar bevindt het probleem zich?",
                "description": "Geef het adres, de straatnaam of een beschrijving van de locatie."
            },
            {
                "title": "Hoe ernstig is het probleem?",
                "description": "Bijvoorbeeld gevaarlijk, hinderlijk of dringend."
            },
            {
                "title": "Eventuele aanvullende details",
                "description": "Bijvoorbeeld hoe lang het probleem al bestaat."
            },
        ]
    },
    {
        "intent": "Aanvraag Vergunning voor Evenementen",
        "intentcode": "event_permit_application",
        "steps": [
            {
                "title": "Wat voor evenement wilt u organiseren?",
                "description": "Bijvoorbeeld concert, markt of sportevenement."
            },
            {
                "title": "Waar en wanneer vindt het evenement plaats?",
                "description": "Geef de locatie, datum en tijd."
            },
            {
                "title": "Hoeveel bezoekers verwacht u?",
                "description": "Geef een schatting van het aantal bezoekers."
            },
            {
                "title": "Welke voorzieningen heeft u nodig?",
                "description": "Bijvoorbeeld stroom, toiletten of verkeersregelaars."
            },
            {
                "title": "Eventuele veiligheidsmaatregelen",
                "description": "Bijvoorbeeld EHBO of beveiliging."
            },
        ]
    },
    {
        "intent": "Aanvraag Hulp bij Schulden",
        "intentcode": "debt_assistance_request",
        "steps": [
            {
                "title": "Wat is uw huidige financiële situatie?",
                "description": "Bijvoorbeeld inkomen, uitgaven en schulden."
            },
            {
                "title": "Wat zijn de oorzaken van uw schulden?",
                "description": "Bijvoorbeeld baanverlies of medische kosten."
            },
            {
                "title": "Welke hulp heeft u nodig?",
                "description": "Bijvoorbeeld betalingsregeling of budgetbeheer."
            },
            {
                "title": "Heeft u al contact gehad met schuldeisers?",
                "description": "Bijvoorbeeld afspraken of brieven."
            },
            {
                "title": "Eventuele aanvullende informatie",
                "description": "Bijvoorbeeld urgentie of gezinssituatie."
            },
        ]
    },
]
