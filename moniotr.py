from datetime import date, timedelta

from atc import get_available_slots


def main():
    today = date.today()

    # Probamos hoy y los próximos 6 días
    for offset in range(7):
        day = today + timedelta(days=offset)

        print(f"\n=== {day} ===")

        try:
            slots = get_available_slots(day)

            if not slots:
                print("No hay turnos disponibles.")
                continue

            for slot in slots:
                print(
                    f"{slot['court_name']} | "
                    f"{slot['start']} | "
                    f"{slot['duration']} min"
                )

        except Exception as e:
            print(f"ERROR: {e}")


if _name_ == "_main_":
    main()
