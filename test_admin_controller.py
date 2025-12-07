
from datetime import datetime, timedelta
import database
import controllers
from models import BookingModel


def test_check_auto_checkout_marks_overdue(tmp_path, monkeypatch):
    # use temp DB
    database.DB_PATH = tmp_path / "test_resort.db"
    database.init_db()

    # We'll fix "now" at a specific point in time
    # e.g. 2025-01-02 09:00 (after the 8:00 AM cutoff)
    fixed_now = datetime(2025, 1, 2, 9, 0, 0)

    # booking_date is "yesterday" relative to fixed_now
    yesterday = (fixed_now - timedelta(days=1)).date()
    booking_date_str = yesterday.strftime("%Y-%m-%d")

    # Create a booking for yesterday with Overnight package
    BookingModel.create(
        guest_name="Overnight Guest",
        booking_date=booking_date_str,
        adults=2,
        children=0,
        package="Overnight",
        table_id=None,
        room_id=None,
        table_fee=0.0,
        room_fee=0.0,
        entrance_fee=0.0,
        total_amount=0.0,
        amount_paid=0.0,
    )

    # Fake datetime.now() inside the controllers module
    class FakeDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            # Always return our fixed "now"
            return fixed_now

    # Monkeypatch the datetime class that controllers imported:
    # from datetime import datetime, date, time, timedelta
    monkeypatch.setattr(controllers, "datetime", FakeDateTime)

    admin = controllers.AdminController()
    overdue_ids = admin.check_auto_checkout()

    # The one Overnight booking from yesterday should now be overdue
    assert len(overdue_ids) == 1
