from booking import build_booking_service, free_hours_label


def service():
    return build_booking_service()


def test_free_hours_follow_room_schedule():
    booking = service()

    assert booking.free_hours("A1") == [9, 10, 11, 12, 13, 14, 15, 16, 17]


def test_every_room_has_its_own_working_day():
    booking = service()

    assert booking.free_hours("B2") == [10, 11, 12, 13, 14, 15]
    assert booking.free_hours("C3")[0] == 8
    assert booking.free_hours("C3")[-1] == 19


def test_unknown_room_has_no_free_hours():
    booking = service()

    assert booking.free_hours("Z9") == []


def test_free_hours_are_shown_as_label():
    booking = service()

    assert free_hours_label(booking, "B2") == "10:00, 11:00, 12:00, 13:00, 14:00, 15:00"


def test_booking_is_accepted():
    booking = service()

    result = booking.book("A1", 10, "Іваненко", 5)

    assert result["status"] == "ok"
    assert result["errors"] == []
    assert result["room"] == "A1"
    assert result["hour"] == 10
    assert result["who"] == "Іваненко"
    assert result["label"] == "Аудиторія A1, 10:00 — Іваненко"


def test_code_names_the_room():
    booking = service()

    result = booking.book("B2", 11, "Коваль", 3)

    assert result["code"].startswith("BR-B2-")


def test_two_bookings_get_different_codes():
    booking = service()

    first = booking.book("A1", 9, "Іваненко")
    second = booking.book("A1", 10, "Коваль")

    assert first["code"] != second["code"]


def test_hour_is_free_before_it_is_booked():
    booking = service()

    assert 12 in booking.free_hours("A1")
    assert booking.book("A1", 12, "Мороз")["status"] == "ok"


def test_taken_hour_is_rejected():
    booking = service()
    booking.book("A1", 14, "Іваненко")

    result = booking.book("A1", 14, "Коваль")

    assert result["status"] == "error"
    assert "година вже зайнята" in result["errors"]
    assert result["code"] == ""


def test_hour_outside_schedule_is_rejected():
    booking = service()

    result = booking.book("B2", 9, "Іваненко")

    assert result["status"] == "error"
    assert "година поза розкладом залу" in result["errors"]


def test_group_larger_than_room_is_rejected():
    booking = service()

    result = booking.book("B2", 11, "Іваненко", 10)

    assert result["status"] == "error"
    assert "людей більше, ніж місць у залі" in result["errors"]


def test_unknown_room_is_rejected():
    booking = service()

    result = booking.book("Z9", 10, "Іваненко")

    assert result["status"] == "error"
    assert "невідомий зал" in result["errors"]


def test_all_broken_fields_reported_together():
    booking = service()

    result = booking.book("B2", 20, "", 40)

    assert result["status"] == "error"
    assert len(result["errors"]) == 3


def test_rejected_request_leaves_no_booking():
    booking = service()

    booking.book("A1", 22, "Іваненко")

    assert booking.schedule("A1") == []


def test_schedule_lists_bookings_by_hour():
    booking = service()
    booking.book("A1", 15, "Коваль")
    booking.book("A1", 9, "Іваненко")

    rows = booking.schedule("A1")

    assert [row["hour"] for row in rows] == [9, 15]
    assert [row["who"] for row in rows] == ["Іваненко", "Коваль"]
    assert rows[0]["label"] == "09:00 — Іваненко"


def test_schedule_keeps_the_code_of_each_booking():
    booking = service()
    created = booking.book("C3", 8, "Мороз")

    rows = booking.schedule("C3")

    assert [row["code"] for row in rows] == [created["code"]]


def test_schedule_of_unknown_room_is_empty():
    booking = service()

    assert booking.schedule("Z9") == []


def test_two_services_do_not_share_bookings():
    first = service()
    second = service()

    first.book("A1", 10, "Іваненко")

    assert second.schedule("A1") == []
    assert second.book("A1", 10, "Коваль")["status"] == "ok"


def test_booking_one_room_does_not_touch_another():
    booking = service()

    booking.book("A1", 10, "Іваненко")

    assert booking.schedule("B2") == []
    assert booking.book("B2", 10, "Коваль")["status"] == "ok"
