from .timing import format_datetime


class TimestampMixin:
    __timestamp_fields__ = ("created",)

    def dict(self, *args, **kwargs) -> dict:
        d = super().dict(*args, **kwargs)
        for field in self.__timestamp_fields__:
            val = getattr(self, field, None)
            d[field] = format_datetime(val) if val is not None else None
        return d
