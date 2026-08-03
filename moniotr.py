import json
from datetime import date, datetime, timedelta

from atc import get_available_slots


STATE_FILE = "state.json"

DAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def time_to_minutes(value):
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


def slot_matches(slot, config):
    start = datetime.fromisoformat(slot["start"])

    day_name = DAY_NAMES[start.weekday()]
    slot_minutes = start.hour * 60 + start.minute

    watch = config["watch"]

    if day_name not in watch["days"]:
        return False

    from_minutes = time_to_minutes(watch["from"])
    to_minutes = time_to_minutes(watch["to"])

    return from_minutes <= slot_minutes <= to_minutes


def slot_id(slot):
    start = datetime.fromisoformat(slot["start"])

    return f"{slot['court_name']}|{start.isoformat()}"


def get_dates_to_check(config):
    """
    Devuelve los próximos 7 días que coinciden
    con los días configurados.
    """
    wanted_days = set(config["watch"]["days"])

    today = date.today()
    dates = []

    for offset in range(7):
        day = today + timedelta(days=offset)

        if DAY_NAMES[day.weekday()] in wanted_days:
            dates.append(day)

    return dates


def main():
    config = load_config()
    previous_state = load_state()

    current_state = {}
    new_slots = []

    dates = get_dates_to_check(config)

    print("Días a consultar:")

    for day in dates:
        print(f"  - {day} ({DAY_NAMES[day.weekday()]})")

    for day in dates:
        print(f"\nConsultando ATC: {day}")

        try:
            slots = get_available_slots(day)

        except Exception as e:
            # MUY IMPORTANTE:
            # No modificamos el estado si ATC falló.
            print(f"❌ ERROR consultando ATC: {e}")
            print("   Se conserva el estado anterior para este día.")
            continue

        matching_slots = [
            slot
            for slot in slots
            if slot_matches(slot, config)
        ]

        current_ids = []

        for slot in matching_slots:
            sid = slot_id(slot)
            current_ids.append(sid)

            previous_ids = previous_state.get(day.isoformat(), [])

            if sid not in previous_ids:
                new_slots.append(slot)

        current_state[day.isoformat()] = current_ids

        print(
            f"   Disponibles dentro del rango: "
            f"{len(matching_slots)}"
        )

    # Actualizamos solamente los días que pudimos consultar.
    new_state = previous_state.copy()
    new_state.update(current_state)

    save_state(new_state)

    print("\n==============================")
    print("NUEVOS TURNOS")
    print("==============================")

    if not new_slots:
        print("No se detectaron nuevos turnos.")

    for slot in new_slots:
        start = datetime.fromisoformat(slot["start"])

        print(
            f"🎾 NUEVO TURNO → "
            f"{start.strftime('%A %d/%m a las %H:%M')} | "
            f"{slot['court_name']}"
        )

    print("==============================")


if __name__ == "__main__":
    main()
