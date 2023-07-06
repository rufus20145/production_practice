from base import session_factory
from objects import Entity

if __name__ == "__main__":
    print("hello")
    with session_factory() as session:
        session.add(Entity(1, "foo", "bar"))
        session.add(Entity(2, "fizz", "buzz"))
        session.commit()

    with session_factory() as session:
        print(session.query(Entity).count())