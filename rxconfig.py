import os
import reflex as rx


def _load_env(path: str = ".env"):
    """Load key=value pairs from a .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

_load_env()

config = rx.Config(
    app_name="galadriel",
    plugins=[rx.plugins.SitemapPlugin()],
    db_url="sqlite:///galadriel.db",
    img_src="/galadriel.320x320.jpg",
    tailwind=None,
)
