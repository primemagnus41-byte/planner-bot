from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.study import SrsCard, Subject, Topic, TopicStatus
from app.db.repositories.study import StudyRepository


def apply_sm2(card: SrsCard, quality: int) -> SrsCard:
    """
    SM-2 algoritmi:
    quality: 0 (umuman esda yo'q), 3 (qiyin), 4 (yaxshi), 5 (mukammal).
    """
    now = datetime.now(timezone.utc)

    card.repetitions = card.repetitions or 0
    card.interval_days = card.interval_days or 0
    card.lapses = card.lapses or 0
    card.ease_factor = card.ease_factor or 2.5

    if quality < 3:
        card.repetitions = 0
        card.interval_days = 1
        card.lapses += 1
    else:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = max(1, round(card.interval_days * card.ease_factor))
        card.repetitions += 1

    card.ease_factor = max(
        1.3,
        card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    card.last_reviewed_at = now
    card.due_at = now + timedelta(days=card.interval_days)
    return card


class TopicNotFound(Exception):
    pass


class CardNotFound(Exception):
    pass


class StudyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = StudyRepository(session)

    async def add_subject(self, user_id: int, name: str) -> Subject:
        subj = Subject(user_id=user_id, name=name.strip())
        self.session.add(subj)
        await self.session.flush()
        return subj

    async def add_topic(
        self,
        user_id: int,
        title: str,
        notes: str | None = None,
        subject_id: int | None = None,
    ) -> Topic:
        topic = Topic(
            user_id=user_id,
            subject_id=subject_id,
            title=title.strip(),
            notes=notes,
            status=TopicStatus.NEW,
        )
        now = datetime.now(timezone.utc)
        card = SrsCard(
            user_id=user_id,
            due_at=now,  # Hozirdan takrorlashga tayyor
        )
        topic.card = card
        self.repo.add(topic)
        await self.session.flush()
        return topic

    async def review_card(self, card_id: int, user_id: int, quality: int) -> SrsCard:
        stmt = await self.session.get(SrsCard, card_id)
        if not stmt or stmt.user_id != user_id:
            raise CardNotFound
        card = apply_sm2(stmt, quality)
        if quality >= 4 and card.repetitions >= 5:
            topic = await self.session.get(Topic, card.topic_id)
            if topic:
                topic.status = TopicStatus.MASTERED
        elif card.repetitions > 0:
            topic = await self.session.get(Topic, card.topic_id)
            if topic and topic.status == TopicStatus.NEW:
                topic.status = TopicStatus.LEARNING
        await self.session.flush()
        return card

    async def get_due_cards(self, user_id: int) -> list[SrsCard]:
        now = datetime.now(timezone.utc)
        return await self.repo.list_due_cards(user_id, now)

    async def count_due_cards(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        return await self.repo.count_due_cards(user_id, now)

    async def list_subjects(self, user_id: int) -> list[Subject]:
        return await self.repo.list_subjects(user_id)
