import controllers

def test_calculate_entrance_basic():
    ctrl = controllers.BookingController()
    # ADULT_ENTRANCE = 150, CHILD_ENTRANCE = 130
    fee = ctrl.calculate_entrance(adults=2, children=1)
    assert fee == 2 * 150.0 + 1 * 130.0


def test_calculate_entrance_handles_none():
    ctrl = controllers.BookingController()
    fee = ctrl.calculate_entrance(adults=None, children=None)
    assert fee == 0.0


def test_calculate_total_day_tour():
    ctrl = controllers.BookingController()
    total, entrance = ctrl.calculate_total(
        adults=2,
        children=1,
        entrance_fee=430.0,
        table_fee=300.0,
        room_fee=1000.0,
        package="Day Tour",  # room_fee ignored
    )
    assert entrance == 430.0
    assert total == 430.0 + 300.0


def test_calculate_total_overnight():
    ctrl = controllers.BookingController()
    total, entrance = ctrl.calculate_total(
        adults=2,
        children=1,
        entrance_fee=430.0,
        table_fee=300.0,
        room_fee=1000.0,
        package="Overnight",
    )
    assert total == 430.0 + 300.0 + 1000.0


def test_calculate_total_other_package():
    ctrl = controllers.BookingController()
    total, entrance = ctrl.calculate_total(
        adults=2,
        children=1,
        entrance_fee=430.0,
        table_fee=300.0,
        room_fee=1000.0,
        package="Complete Stay",  # falls into 'else'
    )
    assert total == 430.0 + 300.0 + 1000.0

# tests/test_booking_controller.py (add these)

def test_validate_availability_all_free(monkeypatch):
    # monkeypatch the low-level functions used inside controllers
    monkeypatch.setattr(controllers, "is_table_booked", lambda tid, d: False)
    monkeypatch.setattr(controllers, "is_room_booked", lambda rid, d: False)

    ctrl = controllers.BookingController()
    ok, msg = ctrl.validate_availability("2025-01-01", [1, 2], [10])
    assert ok is True
    assert msg == "OK"


def test_validate_availability_table_occupied(monkeypatch):
    def fake_table_booked(tid, d):
        return tid == 2  # only table 2 is occupied

    monkeypatch.setattr(controllers, "is_table_booked", fake_table_booked)
    monkeypatch.setattr(controllers, "is_room_booked", lambda rid, d: False)

    ctrl = controllers.BookingController()
    ok, msg = ctrl.validate_availability("2025-01-01", [1, 2], [10])
    assert ok is False
    assert "Table 2 is already booked" in msg


def test_validate_availability_room_occupied(monkeypatch):
    monkeypatch.setattr(controllers, "is_table_booked", lambda tid, d: False)
    monkeypatch.setattr(controllers, "is_room_booked", lambda rid, d: rid == 5)

    ctrl = controllers.BookingController()
    ok, msg = ctrl.validate_availability("2025-01-01", [1], [5])
    assert ok is False
    assert "Room 5 is already booked" in msg
