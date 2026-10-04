"""Бронювання приміщення: розклад залів, сховище броней і точка входу над ними."""

ROOMS = {
    "A1": {"title": "Аудиторія A1", "seats": 12, "opens": 9, "closes": 18},
    "B2": {"title": "Переговорна B2", "seats": 6, "opens": 10, "closes": 16},
    "C3": {"title": "Лекційна C3", "seats": 40, "opens": 8, "closes": 20},
}


class RoomRepo:
    """Сховище броней: що і на коли зайнято в кожному залі."""

    def __init__(self, rooms):
        self._rooms = {code: dict(spec) for code, spec in rooms.items()}
        self._bookings = {code: [] for code in self._rooms}

    def knows(self, room):
        return room in self._rooms

    def spec(self, room):
        return dict(self._rooms[room])

    def bookings(self, room):
        return [dict(booking) for booking in self._bookings[room]]

    def free_slots(self, room):
        spec = self._rooms[room]
        taken = [booking["hour"] for booking in self._bookings[room]]
        return [h for h in range(spec["opens"], spec["closes"]) if h not in taken]

    def create(self, room, hour, who, code):
        self._bookings[room].append({"code": code, "hour": hour, "who": who})
        return code


class CachedRoomRepo:
    """Сховище броней із запам'ятованими вільними годинами."""

    def __init__(self, inner):
        self._inner = inner
        self._cache = {}

    def knows(self, room):
        return self._inner.knows(room)

    def spec(self, room):
        return self._inner.spec(room)

    def bookings(self, room):
        return self._inner.bookings(room)

    def free_slots(self, room):
        if room not in self._cache:
            self._cache[room] = self._inner.free_slots(room)
        return list(self._cache[room])

    def create(self, room, hour, who, code):
        result = self._inner.create(room, hour, who, code)
        self._cache.pop(room, None)
        return result


class BookingNumbers:
    """Наскрізна нумерація броней у межах залу."""

    _instance = None

    def __init__(self):
        self._counters = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BookingNumbers()
        return cls._instance

    def next_code(self, room):
        number = self._counters.get(room, 0) + 1
        self._counters[room] = number
        return "BR-%s-%04d" % (room, number)


def request_errors(repo, room, hour, who, people):
    """Перевірки заявки на бронювання."""
    errors = []
    if not who.strip():
        errors.append("не вказано, хто бронює")
    if people < 1:
        errors.append("кількість людей має бути додатною")
    if not repo.knows(room):
        errors.append("невідомий зал")
        return errors
    spec = repo.spec(room)
    if hour < spec["opens"] or hour >= spec["closes"]:
        errors.append("година поза розкладом залу")
    if people > spec["seats"]:
        errors.append("людей більше, ніж місць у залі")
    if any(booking["hour"] == hour for booking in repo.bookings(room)):
        errors.append("година вже зайнята")
    return errors


class BookingService:
    """Точка входу: перевіряє заявку, записує бронь і показує розклад залу."""

    def __init__(self, repo):
        self._repo = repo

    def free_hours(self, room):
        if not self._repo.knows(room):
            return []
        return self._repo.free_slots(room)

    def book(self, room, hour, who, people=1):
        errors = request_errors(self._repo, room, hour, who, people)
        if errors:
            return {"status": "error", "errors": errors, "code": "",
                    "room": room, "hour": hour, "who": who, "label": ""}

        code = BookingNumbers.get_instance().next_code(room)
        self._repo.create(room, hour, who, code)
        title = self._repo.spec(room)["title"]
        return {"status": "ok", "errors": [], "code": code,
                "room": room, "hour": hour, "who": who,
                "label": "%s, %02d:00 — %s" % (title, hour, who)}

    def schedule(self, room):
        if not self._repo.knows(room):
            return []
        rows = sorted(self._repo.bookings(room), key=lambda booking: booking["hour"])
        return [{"code": row["code"], "hour": row["hour"], "who": row["who"],
                 "label": "%02d:00 — %s" % (row["hour"], row["who"])} for row in rows]


def build_booking_service(rooms=None):
    """Збирає сервіс бронювання з готових частин."""
    source = rooms if rooms is not None else ROOMS
    return BookingService(CachedRoomRepo(RoomRepo(source)))


def free_hours_label(service, room):
    """Вільні години залу рядком для показу користувачеві."""
    return ", ".join("%02d:00" % hour for hour in service.free_hours(room))
