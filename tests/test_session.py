from sqlalchemy import create_engine

from database.session import create_session_factory


def test_session_factory_sessions() -> None:
    engine = create_engine("sqlite://")
    session_factory = create_session_factory(engine=engine)
    with (
        session_factory() as session1,
        session_factory() as session2,
    ):
        assert session1.bind is engine
        assert session2.bind is engine
        assert session1 is not session2
