import requests
from datetime import date


BASE_URL = "https://alquilatucancha.com/api/v3/availability/sportclubs/1684"


def get_available_slots(day: date):
    """Devuelve los turnos disponibles de Esandi Padel para una fecha."""

    response = requests.get(
        BASE_URL,
        params={"date": day.isoformat()},
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    slots = []

    for court in data.get("available_courts", []):
        for slot in court.get("available_slots", []):
            slots.append({
                "court_id": court["id"],
                "court_name": court["name"],
                "start": slot["start"],
                "duration": slot["duration"],
                "price": slot["price"],
            })

    return slots
