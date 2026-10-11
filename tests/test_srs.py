from datetime import datetime, timezone
from app.db.models.study import SrsCard
from app.services.study import apply_sm2


def test_sm2_progression():
    card = SrsCard(
        user_id=1,
        topic_id=1,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        due_at=datetime.now(timezone.utc),
    )

    # 1st review - good (4)
    apply_sm2(card, quality=4)
    assert card.repetitions == 1
    assert card.interval_days == 1

    # 2nd review - good (4)
    apply_sm2(card, quality=4)
    assert card.repetitions == 2
    assert card.interval_days == 6

    # 3rd review - excellent (5)
    prev_interval = card.interval_days
    apply_sm2(card, quality=5)
    assert card.repetitions == 3
    assert card.interval_days > prev_interval

    # Failed review (0)
    apply_sm2(card, quality=0)
    assert card.repetitions == 0
    assert card.interval_days == 1
    assert card.lapses == 1
