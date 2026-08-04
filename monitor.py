import json
import os
from datetime import date, datetime, timedelta

from atc import get_available_slots
from notifier import send_telegram_message


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

DAY_NAMES_ES = {
    "monday": "lunes",
    "tuesday": "martes",
    "wednesday": "miércoles",
    "thursday": "jueves",
    "friday": "viernes",
    "saturday": "sábado",
    "sunday": "domingo",
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
    wanted_days = set(config["watch"]["days"])

    today = date.today()
    dates = []

    for offset in range(7):
        day = today + timedelta(days=offset)

        if DAY_NAMES[day.weekday()] in wanted_days:
            dates.append(day)

    return dates


def format_telegram_message(slot):
    start = datetime.fromisoformat(slot["start"])

    day_name = DAY_NAMES_ES[start.strftime("%A").lower()]

    return (
        "🎾 ¡SE LIBERÓ UN TURNO!\n\n"
        "📍 Esandi Padel\n"
        f"📅 {day_name} {start.strftime('%d/%m')}\n"
        f"🕐 {start.strftime('%H:%M')}\n"
        f"🏟️ {slot['court_name']}\n"
        "\n👉 Entrá a ATC Sports para reservarlo."
    )


def main():
    config = load_config()
    previous_state = load_state()

    current_state = {}
    new_slots = []

    dates = get_dates_to_check(config)

    for day in dates:
        print(f"Consultando ATC: {day}")

        try:
            slots = get_available_slots(day)

        except Exception as e:
            print(f"❌ ERROR consultando ATC: {e}")
            print("   Se conserva el estado anterior.")
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

    # Solo actualizamos los días consultados correctamente.
    new_state = previous_state.copy()
    new_state.update(current_state)

    save_state(new_state)

    print(f"\n🎾 Nuevos turnos detectados: {len(new_slots)}")

    # Credenciales desde variables de entorno.
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if new_slots and not telegram_token:
        print("⚠️ TELEGRAM_TOKEN no está configurado.")
        print("No se enviaron notificaciones.")

    for slot in new_slots:
        start = datetime.fromisoformat(slot["start"])

        print(
            f"  → {start.strftime('%d/%m %H:%M')} "
            f"{slot['court_name']}"
        )

        if telegram_token and telegram_chat_id:
            message = format_telegram_message(slot)

            try:
                send_telegram_message(
                    telegram_token,
                    telegram_chat_id,
                    message,
                )

                print("  📲 Telegram enviado.")

            except Exception as e:
                print(f"  ❌ Error enviando Telegram: {e}")


if __name__ == "__main__":
    main()
