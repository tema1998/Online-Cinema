import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, ARRAY, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship

from src.db.db_utils import Base


class TimeStampedMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UUIDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Role(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(ARRAY(String), nullable=False)

    users = relationship("UserRole", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}', description='{self.description}')>"


class User(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "users"

    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    premium = relationship("PremiumData", uselist=False, backref="users")
    roles = relationship("UserRole", back_populates="user")
    login_history = relationship("UserLoginHistory", back_populates="user")
    social_accounts = relationship(
        "UserSocialAccount", back_populates="user", passive_deletes=True
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, login='{self.login}', "
            f"first_name='{self.first_name}', last_name='{self.last_name}', "
            f"is_active={self.is_active}, is_superuser={self.is_superuser})>"
        )


class PremiumData(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "premium_data"

    user_id = Column(UUID, ForeignKey('users.id'))
    valid_until = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserSocialAccount(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "user_social_accounts"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(
        String(50), nullable=False
    )  # e.g., 'google', 'vk', 'yandex', 'mail'
    provider_user_id = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=True)
    fullname = Column(String(255), nullable=True)

    user = relationship("User", back_populates="social_accounts")

    def __repr__(self) -> str:
        return (
            f"<UserSocialAccount(id={self.id}, user_id={self.user_id}, "
            f"provider='{self.provider}', provider_user_id='{self.provider_user_id}', "
            f"email='{self.email}', username='{self.username}')>"
        )


class UserRole(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "user_roles"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", back_populates="roles", passive_deletes=True)
    role = relationship("Role", back_populates="users", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<UserRofle(user_id={self.user_id}, role_id={self.role_id})>"


# Partition creation function
def create_partition(target, connection, **kw) -> None:
    """Creating partitions for user_device_type"""
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_login_history_mobile" 
               PARTITION OF "user_login_history" 
               FOR VALUES IN ('mobile')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_login_history_desktop" 
               PARTITION OF "user_login_history" 
               FOR VALUES IN ('desktop')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_login_history_tablet" 
               PARTITION OF "user_login_history" 
               FOR VALUES IN ('tablet')"""
        )
    )
    # Adding a default partition for unknown device types
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_login_history_default" 
               PARTITION OF "user_login_history" 
               DEFAULT"""
        )
    )


class UserLoginHistory(Base):
    __tablename__ = "user_login_history"
    __table_args__ = {
        "postgresql_partition_by": "LIST (user_device_type)",
        "listeners": [("after_create", create_partition)],
    }

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_agent = Column(String(255))
    ip_address = Column(String(45))
    # Partition key, not primary key
    user_device_type = Column(Text, nullable=True)

    # Relationship with the User model
    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return (
            f"<UserLoginHistory(id={self.id}, user_id={self.user_id}, "
            f"login_time='{self.login_time}', user_agent='{self.user_agent}', "
            f"ip_address='{self.ip_address}', user_device_type='{self.user_device_type}')>"
        )
