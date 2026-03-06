import reflex as rx

from .timing import format_datetime


def reorder_move_up(model_class, item_id, parent_field, parent_id, item_label="item"):
    """Swap an ordered item with the one above it. Returns toast on boundary."""
    with rx.session() as session:
        item = session.exec(model_class.select().where(model_class.id == item_id)).first()
        old_order = item.order
        if old_order == 1:
            return rx.toast.warning(f"The {item_label} has reached min")

        parent_filter = getattr(model_class, parent_field) == parent_id
        neighbor = session.exec(
            model_class.select().where(model_class.order == (old_order - 1), parent_filter)
        ).first()

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


class TimestampMixin:
    __timestamp_fields__ = ("created",)

    def dict(self, *args, **kwargs) -> dict:
        d = super().dict(*args, **kwargs)
        for field in self.__timestamp_fields__:
            val = getattr(self, field, None)
            d[field] = format_datetime(val) if val is not None else None
        return d
