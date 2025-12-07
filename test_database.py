from pathlib import Path
import database
from models import BookingModel


def test_init_db_uses_temp_file(tmp_path):
    # redirect DB_PATH to a temporary db file
    test_db_path = tmp_path / "test_resort.db"
    database.DB_PATH = test_db_path

    # Init schema & seed
    database.init_db()

    # Check that the file was created
    assert test_db_path.exists()

    # Insert a booking through BookingModel
    BookingModel.create(
        guest_name="Test Guest",
        booking_date="2025-01-01",
        adults=2,
        children=1,
        package="Day Tour",
        table_id=1,
        room_id=None,
        table_fee=300.0,
        room_fee=0.0,
        entrance_fee=430.0,
        total_amount=730.0,
        amount_paid=730.0,
    )

    rows = BookingModel.fetch_by_date("2025-01-01")
    assert len(rows) == 1

    row = rows[0]
    assert row["guest_name"] == "Test Guest"
    assert row["guest_count"] == 3
    assert row["total_amount"] == 730.0