"""Shared utility functions for reordering, querying child items, and timestamp formatting."""

import reflex as rx
from sqlmodel import select, cast, String

from .timing import format_datetime


def reorder_move_up(model_class, item_id, parent_field, parent_id, item_label="item"):
    """Swap an ordered item with the one above it. Returns toast on boundary."""
    with rx.session() as session:
        item = session.exec(model_class.select().where(model_class.id == item_id)).first()
        if item is None:
            return rx.toast.error(f"{item_label} not found")
        old_order = item.order
        if old_order == 1:
            return rx.toast.warning(f"The {item_label} has reached min")

        parent_filter = getattr(model_class, parent_field) == parent_id
        neighbor = session.exec(
            model_class.select().where(model_class.order == (old_order - 1), parent_filter)
        ).first()
        if neighbor is None:
            return rx.toast.error(f"{item_label} neighbor not found")

        item.order = neighbor.order
        session.add(item)
        session.commit()
        session.refresh(item)

        neighbor.order = old_order
        session.add(neighbor)
        session.commit()
        session.refresh(neighbor)

    return None


def reorder_move_down(model_class, item_id, parent_field, parent_id, item_label="item"):
    """Swap an ordered item with the one below it. Returns toast on boundary."""
    with rx.session() as session:
        item = session.exec(model_class.select().where(model_class.id == item_id)).first()
        if item is None:
            return rx.toast.error(f"{item_label} not found")
        old_order = item.order

        parent_filter = getattr(model_class, parent_field) == parent_id
        neighbor = session.exec(
            model_class.select().where(model_class.order == (old_order + 1), parent_filter)
        ).first()

        if neighbor is None:
            return rx.toast.warning(f"The {item_label} has reached max")

        item.order = neighbor.order
        session.add(item)
        session.commit()
        session.refresh(item)

        neighbor.order = old_order
        session.add(neighbor)
        session.commit()
        session.refresh(neighbor)

    return None


def reorder_delete(model_class, item_id, parent_field, parent_id, item_label="item", min_count=0):
    """Delete an ordered item and reorder remaining items."""
    with rx.session() as session:
        if min_count > 0:
            parent_filter = getattr(model_class, parent_field) == parent_id
            all_items = session.exec(model_class.select().where(parent_filter)).all()
            if len(all_items) <= min_count:
                return rx.toast.error(f"cannot delete last {item_label}")

        item = session.exec(model_class.select().where(model_class.id == item_id)).first()
        if item is None:
            return rx.toast.error(f"{item_label} not found")

        deleted_order = item.order
        session.delete(item)
        session.commit()

        parent_filter = getattr(model_class, parent_field) == parent_id
        items_to_update = session.exec(
            model_class.select().where(parent_filter, model_class.order > deleted_order)
        ).all()
        for remaining in items_to_update:
            remaining.order = remaining.order - 1
            session.add(remaining)
            session.commit()
            session.refresh(remaining)

    return rx.toast.info(f"The {item_label} has been deleted")


def has_steps(step_model, case_id: int) -> bool:
    """Check if a case has at least one step."""
    with rx.session() as session:
        case_steps = session.exec(step_model.select().where(step_model.case_id == case_id)).all()
        return len(case_steps) > 0


def get_max_child_order(model_class, parent_field, parent_id, child_id, child_type_id):
    """Get the next order value for a child. Returns -1 if already linked."""
    with rx.session() as session:
        parent_filter = getattr(model_class, parent_field) == parent_id
        linked_children = session.exec(model_class.select().where(parent_filter)).all()
        max_order = 0
        for linked_child in linked_children:
            if (linked_child.child_id == child_id) and (linked_child.child_type_id == child_type_id):
                return -1
            if linked_child.order > max_order:
                max_order = linked_child.order
        return max_order + 1


def toggle_sort_field(current_field: str, current_asc: bool, field: str) -> tuple:
    """Cycle sort state: default → asc → desc → default. Returns (sort_by, sort_asc)."""
    if current_field != field:
        return field, True
    elif current_asc:
        return current_field, False
    else:
        return "", True


def sort_items(items: list, sort_by: str, sort_asc: bool) -> list:
    """Sort a list by field name. Returns original list when sort_by is empty."""
    if not sort_by:
        return items
    return sorted(
        items,
        key=lambda item: (
            (val := getattr(item, sort_by, None)) is None,
            val,
        ),
        reverse=not sort_asc,
    )


def search_by_name(model_class, search_value: str) -> list:
    """Search for items by name using ILIKE pattern matching."""
    with rx.session() as session:
        query = select(model_class)
        if search_value:
            pattern = f"%{str(search_value).lower()}%"
            query = query.where(cast(model_class.name, String).ilike(pattern))
        return session.exec(query).all()


class TimestampMixin:
    """Mixin that formats timestamp fields in model_dump output."""

    __timestamp_fields__ = ("created",)

    def model_dump(self, *args, **kwargs) -> dict:
        d = super().model_dump(*args, **kwargs)
        for field in self.__timestamp_fields__:
            val = getattr(self, field, None)
            d[field] = format_datetime(val) if val is not None else None
        return d
