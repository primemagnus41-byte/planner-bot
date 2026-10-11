import pytest
from app.db.models.task import TaskStatus, Priority
from app.services.task import TaskService, TaskNotFound
from app.services.user import UserService


@pytest.mark.asyncio
async def test_task_crud_lifecycle(session):
    user_service = UserService(session)
    user, _ = await user_service.get_or_create(12345, "Test User", "testuser")

    task_service = TaskService(session)
    task = await task_service.add(
        user_id=user.id,
        title="Kitob o'qish",
        tz="Asia/Tashkent",
        priority=Priority.HIGH,
    )

    assert task.id is not None
    assert task.title == "Kitob o'qish"
    assert task.status == TaskStatus.PENDING

    # Complete
    completed = await task_service.complete(task.id, user.id, note="Yaxshi o'qildi")
    assert completed.status == TaskStatus.DONE
    assert completed.note == "Yaxshi o'qildi"

    # Soft delete
    deleted = await task_service.soft_delete(task.id, user.id)
    assert deleted.deleted_at is not None

    # Restore (Undo)
    restored = await task_service.restore(task.id, user.id)
    assert restored.deleted_at is None
