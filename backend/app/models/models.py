from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    apps = relationship("App", back_populates="user", cascade="all, delete-orphan")


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="apps")
    secrets = relationship("AppSecret", back_populates="app", uselist=False, cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="app", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="app", cascade="all, delete-orphan")


class AppSecret(Base):
    __tablename__ = "app_secrets"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, unique=True)
    secret_key = Column(Text, nullable=False)  # encrypted - API Secret Key
    api_key = Column(Text, nullable=False)  # encrypted - API Key
    mpin = Column(Text, nullable=False)  # encrypted - Angel One MPIN (Mobile Personal Identification Number)
    base_url = Column(String, default="https://apiconnect.angelbroking.com")  # SmartAPI base URL
    refresh_token = Column(Text)  # encrypted - Session refresh token
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    app = relationship("App", back_populates="secrets")


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    params_json = Column(Text)
    enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    app = relationship("App", back_populates="strategies")
    runs = relationship("StrategyRun", back_populates="strategy", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="strategy")


class StrategyRun(Base):
    __tablename__ = "strategy_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    status = Column(String, default="running")  # running, paused, stopped, completed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    result_json = Column(Text)

    strategy = relationship("Strategy", back_populates="runs")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    order_id = Column(String)
    symbol = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    status = Column(String)
    response_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    app = relationship("App", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)  # null for global settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

