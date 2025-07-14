from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Intent knowledge base – extend / load from file / DB as needed
# ---------------------------------------------------------------------------

INTENTS: List[Dict[str, Any]] = [
    {
        "intent": "Ik wil bezwaar maken op een parkeerboete die ik heb ontvangen",
        "intentcode": "create_objection_parking_fine",
        "steps": [
            {
                "title": "De datum van de bon",
                "description": (
                    "Vraag de gebruiker naar de datum waarop de parkeerboete is uitgeschreven. "
                    "Deze informatie is nodig om te controleren of het bezwaar binnen de wettelijke termijn wordt ingediend."
                ),
            },
            {
                "title": "Het kenteken van de auto",
                "description": (
                    "Vraag de gebruiker naar het kenteken van de auto waarvoor de parkeerboete is uitgeschreven. "
                    "Dit helpt om de boete te koppelen aan het juiste voertuig."
                ),
            },
            {
                "title": "De reden van je bezwaar",
                "description": (
                    "Vraag de gebruiker naar de reden waarom hij of zij bezwaar wil maken tegen de parkeerboete. "
                    "Dit kan bijvoorbeeld zijn omdat de boete onterecht is of omdat er een fout is gemaakt."
                ),
            },
        ]
    },
    {"intent": "Ik wil mijn adres wijzigen in de gemeentelijke administratie",
     "intentcode": "update_address_municipal_records",
     "steps": [
         {
               "title": "Controleer de termijn",
               "description": ('Geef je adreswijziging door binnen 5 dagen na verhuizing '
                               'om boetes of administratieve problemen te voorkomen.'),
         },
         {"title": "Wat heb je nodig",
          "items": ["Geldig identiteitsbewijs",
                    "Huurcontract of koopakte (indien van toepassing)",
                    "Eventueel een schriftelijke toestemming van de hoofdbewoner",
                    "Nieuw adres",
                    ],
          },
     ],
     }
]
