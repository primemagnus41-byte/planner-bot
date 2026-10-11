from html import escape
from app.db.models.task import Task, TaskStatus, Priority


def esc(text: str | None) -> str:
    """Foydalanuvchi matni HTML'ga tushishidan oldin MAJBURIY."""
    return escape(text or "", quote=False)


def progress_bar(done: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "─" * width
    filled = round(width * done / total)
    return "█" * filled + "░" * (width - filled)


def priority_emoji(p: Priority) -> str:
    if p == Priority.URGENT:
        return "🔥 "
    if p == Priority.HIGH:
        return "⚡️ "
    if p == Priority.LOW:
        return "☕️ "
    return ""


def format_task_list(summary: dict) -> str:
    tasks: list[Task] = summary["tasks"]
    done_count = len(summary["done"])
    total_count = len(tasks)

    day_str = summary["date"].strftime("%d.%m.%Y")
    bar = progress_bar(done_count, total_count)
    percent = round(done_count / total_count * 100) if total_count > 0 else 0

    lines = [
        f"📅 <b>Kunlik reja — {day_str}</b>",
        f"Progress: [{bar}] {done_count}/{total_count} ({percent}%)\n",
    ]

    for idx, t in enumerate(tasks, 1):
        p_emoji = priority_emoji(t.priority)
        if t.status == TaskStatus.DONE:
            icon = "✅"
            title_text = f"<s>{esc(t.title)}</s>"
        elif t.status == TaskStatus.SKIPPED:
            icon = "⚪️"
            title_text = f"<i>(O'tkazildi) {esc(t.title)}</i>"
        else:
            icon = "▫️"
            title_text = f"<b>{esc(t.title)}</b>"

        time_str = ""
        if t.due_at:
            time_str = f" <i>({t.due_at.strftime('%H:%M')})</i>"

        lines.append(f"{idx}. {icon} {p_emoji}{title_text}{time_str}")

    return "\n".join(lines)
