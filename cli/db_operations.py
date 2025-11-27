import typer
import sys
import os

# Добавляем корневую папку в Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = typer.Typer()


@app.command("db-filler")
def fill_db_test_data() -> None:
    """Заполним БД тестовыми данными для экспериментов"""
    # Импорты ВНУТРИ функции
    from orm_models.users import User, Club, Member
    from utils.unit_of_work import UnitOfWork

    print("Заполнение БД тестовыми данными...")

    # Создаем тестовых пользователей
    user1 = User(
        user_id=123456789,
        username="test_user1",
        name="Тестовый Пользователь 1",
        location="Москва",
        interests="программирование, игры"
    )

    user2 = User(
        user_id=987654321,
        username="test_user2",
        name="Тестовый Пользователь 2",
        location="Санкт-Петербург",
        interests="спорт, музыка"
    )

    with UnitOfWork() as uow:
        uow.session.add_all([user1, user2])
        uow.commit()
        print("✅ Тестовые пользователи добавлены")

    # Создаем тестовые клубы
    club1 = Club(
        owner_id=123456789,
        name="IT Клуб Москва",
        description="Клуб для IT-специалистов в Москве",
        tags="#программирование #it #технологии",
        location="Москва",
        chat_link="https://t.me/it_club_moscow",
        is_active=True
    )

    with UnitOfWork() as uow:
        uow.session.add(club1)
        uow.commit()
        print("✅ Тестовые клубы добавлены")

    # Добавляем участников
    member1 = Member(user_id=987654321, club_id=1)

    with UnitOfWork() as uow:
        uow.session.add(member1)
        uow.commit()
        print("✅ Тестовые участники добавлены")


@app.command("db-select-users")
def db_orm_select_users() -> None:
    """Показать всех пользователей"""
    # Импорты ВНУТРИ функции
    from sqlalchemy import select
    from orm_models.users import User
    from utils import control
    from utils.databases import scoped_session_factory

    stmt = select(User)
    with control.session_control(session_factory=scoped_session_factory) as session:
        print("👥 Пользователи в БД:")
        for row in session.execute(stmt):
            for user in row:
                user: User
                print(f"ID: {user.user_id}, Имя: {user.name}, Локация: {user.location}")


@app.command("db-select-clubs")
def db_orm_select_clubs() -> None:
    """Показать все клубы"""
    # Импорты ВНУТРИ функции
    from sqlalchemy import select
    from orm_models.users import Club
    from utils import control
    from utils.databases import scoped_session_factory

    stmt = select(Club)
    with control.session_control(session_factory=scoped_session_factory) as session:
        print("🏛️ Клубы в БД:")
        for row in session.execute(stmt):
            for club in row:
                club: Club
                print(f"ID: {club.club_id}, Название: {club.name}, Владелец: {club.owner_id}")


@app.command("db-fix-sequence")
def fix_sequence() -> None:
    """Исправить последовательность автоинкремента для clubs"""
    # Импорты ВНУТРИ функции
    from sqlalchemy import text
    from utils.unit_of_work import UnitOfWork

    with UnitOfWork() as uow:
        # Получаем максимальный существующий club_id
        result = uow.session.execute(text("SELECT MAX(club_id) FROM clubs"))
        max_id = result.scalar() or 0

        # Сбрасываем последовательность
        uow.session.execute(text(f"SELECT setval('clubs_club_id_seq', {max_id})"))
        uow.commit()

        print(f"✅ Последовательность исправлена. Максимальный ID: {max_id}")


if __name__ == "__main__":
    app()