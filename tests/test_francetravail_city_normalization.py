from pipelines.ingest.sources.francetravail.mapping import map_france_travail


def _build_raw_offer(city_label: str) -> dict:
    return {
        "id": "test-1",
        "intitule": "Data Engineer",
        "description": "Offre test",
        "lieuTravail": {
            "libelle": city_label,
            "codePostal": "75001",
            "latitude": 48.86,
            "longitude": 2.34,
            "commune": "75101",
        },
    }


def test_location_city_is_normalized_from_uppercase():
    offer = map_france_travail(_build_raw_offer("75 - PARIS"))
    assert offer.location_city == "75 - Paris"


def test_location_city_is_normalized_from_lowercase():
    offer = map_france_travail(_build_raw_offer("75 - paris 11"))
    assert offer.location_city == "75 - Paris 11"
