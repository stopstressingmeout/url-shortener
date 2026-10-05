from app.config import Settings


def test_platform_style_database_urls_are_converted():
    for raw in ("postgres://u:p@host/db", "postgresql://u:p@host/db"):
        settings = Settings(database_url=raw, secret_key="x")
        assert settings.database_url == "postgresql+psycopg://u:p@host/db"


def test_psycopg_url_is_left_alone():
    url = "postgresql+psycopg://u:p@host/db"
    assert Settings(database_url=url, secret_key="x").database_url == url