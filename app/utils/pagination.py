import math


class Paginator:
    def __init__(self, total_items: int, current_page: int = 1, page_size: int = 5) -> None:
        self.total_items = total_items
        self.page_size = page_size
        self.total_pages = max(1, math.ceil(total_items / page_size))
        self.current_page = max(1, min(current_page, self.total_pages))

    @property
    def has_prev(self) -> bool:
        return self.current_page > 1

    @property
    def has_next(self) -> bool:
        return self.current_page < self.total_pages
