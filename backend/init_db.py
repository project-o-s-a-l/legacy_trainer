from backend import models
from backend.app.db.base import Base
from backend.app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    main()
