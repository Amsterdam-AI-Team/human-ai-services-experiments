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
                "title": "Doe het op tijd",
                "description": (
                    "Binnen 2 weken voorkom je extra kosten. Uiterlijk 6 weken na "
                    "de datum van de boete mag je nog bezwaar maken"
                ),
            },
            {
                "title": "Wat heb je nodig",
                "items": [
                    "Boetemerk of bonnummer",
                    "Kenteken",
                    "Reden van bezwaar",
                    "Eventueel bewijs",
                ],
            },
        ],
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