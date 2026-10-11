from datetime import date
import pytest
from app.db.models.reading import BookStatus
from app.services.reading import ReadingService
from app.services.idea import IdeaService
from app.services.user import UserService


@pytest.mark.asyncio
async def test_reading_and_idea_services(session):
    user_service = UserService(session)
    user, _ = await user_service.get_or_create(1001, "Reader", "reader")

    reading_service = ReadingService(session)
    book = await reading_service.add_book(
        user_id=user.id,
        title="Atom Odatlar",
        author="James Clear",
        total_pages=300,
    )
    assert book.status == BookStatus.PLANNED

    # Log session
    book, read_session = await reading_service.log_session(
        user_id=user.id,
        book_id=book.id,
        pages=50,
        read_date=date.today(),
    )
    assert book.current_page == 50
    assert book.status == BookStatus.READING

    # Finish book
    finished_book = await reading_service.finish_book(
        book_id=book.id,
        user_id=user.id,
        review_content="Ajoyib kitob!",
        rating=5,
    )
    assert finished_book.status == BookStatus.FINISHED
    assert finished_book.review is not None
    assert finished_book.review.rating == 5

    # Ideas test
    idea_service = IdeaService(session)
    idea = await idea_service.add_idea(
        user_id=user.id,
        content="Yangi biznes g'oya",
        category="startup",
    )
    assert idea.id is not None
    assert idea.is_starred is False

    starred = await idea_service.toggle_star(idea.id, user.id)
    assert starred.is_starred is True

    ideas_list, total = await idea_service.list_ideas(user.id)
    assert total == 1
    assert len(ideas_list) == 1
