"""
РЕПОЗИТОРИЙ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ ЧЕРЕЗ ORM
Заменит старый database.py
"""

from sqlalchemy import select, and_, or_, func
from utils.unit_of_work import UnitOfWork
from orm_models.users import User, Club, Member


class UserRepository:
    @staticmethod
    def get_user_by_tg_id(tg_id: int):
        """Получить пользователя по Telegram ID"""
        with UnitOfWork() as uow:
            return uow.session.get(User, tg_id)

    @staticmethod
    def create_user(tg_id: int, name: str, username: str = None, location: str = None, interests: str = None) -> bool:
        """Создать нового пользователя"""
        try:
            with UnitOfWork() as uow:
                user = User(
                    user_id=tg_id,
                    username=username,
                    name=name,
                    location=location,
                    interests=interests
                )
                uow.session.add(user)
                uow.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            return False

    @staticmethod
    def update_user(tg_id: int, name: str = None, location: str = None, interests: str = None) -> bool:
        """Обновить данные пользователя"""
        try:
            with UnitOfWork() as uow:
                user = uow.session.get(User, tg_id)
                if not user:
                    return False

                if name is not None:
                    user.name = name
                if location is not None:
                    user.location = location
                if interests is not None:
                    user.interests = interests

                uow.commit()
                return True
        except Exception as e:
            print(f"Ошибка обновления пользователя: {e}")
            return False


class ClubRepository:
    @staticmethod
    def create_club(owner_id: int, name: str, description: str, tags: str, location: str, chat_link: str) -> int:
        """Создать новый клуб. Возвращает ID созданного клуба"""
        with UnitOfWork() as uow:
            club = Club(
                owner_id=owner_id,
                name=name,
                description=description,
                tags=tags,
                location=location,
                chat_link=chat_link,
                is_active=True
            )
            uow.session.add(club)
            uow.session.flush()  # Чтобы получить ID до коммита
            club_id = club.club_id

            # Добавляем создателя в участники
            member = Member(user_id=owner_id, club_id=club_id)
            uow.session.add(member)
            uow.commit()

            return club_id

    @staticmethod
    def get_club_by_id(club_id: int):
        """Получить данные клуба по ID"""
        with UnitOfWork() as uow:
            stmt = select(Club).where(and_(Club.club_id == club_id, Club.is_active == True))
            result = uow.session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    def get_clubs_by_owner(owner_id: int):
        """Получить все клубы, созданные пользователем"""
        with UnitOfWork() as uow:
            stmt = select(Club).where(
                and_(Club.owner_id == owner_id, Club.is_active == True)
            ).order_by(Club.created_at.desc())
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def search_clubs_by_tag(tag: str, limit: int = 10):
        """Найти клубы по тегу"""
        with UnitOfWork() as uow:
            stmt = select(Club).where(
                and_(Club.tags.ilike(f'%{tag}%'), Club.is_active == True)
            ).order_by(Club.created_at.desc()).limit(limit)
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def search_clubs_by_location(location: str, limit: int = 10):
        """Найти клубы по локации"""
        with UnitOfWork() as uow:
            stmt = select(Club).where(
                and_(Club.location.ilike(f'%{location}%'), Club.is_active == True)
            ).order_by(Club.created_at.desc()).limit(limit)
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def get_all_active_clubs(limit: int = 20):
        """Получить все активные клубы"""
        with UnitOfWork() as uow:
            stmt = select(Club).where(
                Club.is_active == True
            ).order_by(Club.created_at.desc()).limit(limit)
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def update_club(club_id: int, **kwargs) -> bool:
        """Обновить данные клуба"""
        try:
            with UnitOfWork() as uow:
                club = uow.session.get(Club, club_id)
                if not club:
                    return False

                for key, value in kwargs.items():
                    if hasattr(club, key) and value is not None:
                        setattr(club, key, value)

                uow.commit()
                return True
        except Exception as e:
            print(f"Ошибка обновления клуба: {e}")
            return False

    @staticmethod
    def deactivate_club(club_id: int) -> bool:
        """Деактивировать клуб (мягкое удаление)"""
        try:
            with UnitOfWork() as uow:
                club = uow.session.get(Club, club_id)
                if club:
                    club.is_active = False
                    uow.commit()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка деактивации клуба: {e}")
            return False


class MemberRepository:
    @staticmethod
    def add_member_to_club(user_id: int, club_id: int) -> bool:
        """Добавить пользователя в клуб как участника"""
        try:
            with UnitOfWork() as uow:
                # Проверяем, не является ли пользователь уже участником
                existing = uow.session.get(Member, (user_id, club_id))
                if existing:
                    return True  # Уже участник

                member = Member(user_id=user_id, club_id=club_id)
                uow.session.add(member)
                uow.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления участника: {e}")
            return False

    @staticmethod
    def remove_member_from_club(user_id: int, club_id: int) -> bool:
        """Удалить пользователя из клуба"""
        try:
            with UnitOfWork() as uow:
                member = uow.session.get(Member, (user_id, club_id))
                if member:
                    uow.session.delete(member)
                    uow.commit()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка удаления участника: {e}")
            return False

    @staticmethod
    def get_club_members(club_id: int):
        """Получить всех участников клуба"""
        with UnitOfWork() as uow:
            stmt = select(User).join(Member, User.user_id == Member.user_id).where(
                Member.club_id == club_id
            )
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def get_user_clubs(user_id: int):
        """Получить все клубы, в которых состоит пользователь"""
        with UnitOfWork() as uow:
            stmt = select(Club).join(Member, Club.club_id == Member.club_id).where(
                and_(Member.user_id == user_id, Club.is_active == True)
            ).order_by(Member.joined_at.desc())
            result = uow.session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def is_user_club_member(user_id: int, club_id: int) -> bool:
        """Проверить, является ли пользователь участником клуба"""
        with UnitOfWork() as uow:
            member = uow.session.get(Member, (user_id, club_id))
            return member is not None

    @staticmethod
    def is_user_club_owner(user_id: int, club_id: int) -> bool:
        """Проверить, является ли пользователь владельцем клуба"""
        with UnitOfWork() as uow:
            club = uow.session.get(Club, club_id)
            return club and club.owner_id == user_id


# Создаем экземпляры репозиториев для удобства
user_repo = UserRepository()
club_repo = ClubRepository()
member_repo = MemberRepository()