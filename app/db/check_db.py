from app.db.base import Base
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)

    print("Database connection: OK")
    print("Tables:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
