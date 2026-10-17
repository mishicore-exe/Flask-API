from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20))


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    buying_price: Mapped[float] = mapped_column(Float)
    selling_price: Mapped[float] = mapped_column(Float)


class Sale(Base, TimestampMixin):
    __tablename__ = "sales"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("users.id"))
    product_id = mapped_column(ForeignKey("products.id"))
    quantity = mapped_column(Integer)

class Sales_detail(Base):
    __tablename__ = "sales_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)


class Purchase(Base, TimestampMixin):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    purchase_price: Mapped[float] = mapped_column(Float)


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    amount_paid: Mapped[float] = mapped_column(Float)
    transaction_code: Mapped[str] = mapped_column(String , nullable=True ,default=None)
    mrid: Mapped[str] = mapped_column(String)
    crid: Mapped[str] = mapped_column(String)
    payment_status: Mapped[str] = mapped_column(String , default="pending")
    phone_number:  Mapped[str] = mapped_column(String(20))


