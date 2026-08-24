from sqlalchemy import ForeignKey
from sqlalchemy import String,Integer,Float,Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import date


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="users"
    id : Mapped[int]= mapped_column(Integer,primary_key=True)
    full_name : Mapped[str]= mapped_column(String(100))
    email : Mapped[str]= mapped_column(String(100)) 
    password :  Mapped[str]= mapped_column(String(200)) 

class Product(Base) :
    __tablename__ = "products"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]= mapped_column(ForeignKey("users.id"))
    buying_price: Mapped[Float] = mapped_column(Float)
    selling_price: Mapped[Float] = mapped_column(Float)

class Sales(Base) :
    __tablename__ = "sales"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_amount: Mapped[Float] = mapped_column(Float)
    sale_date: Mapped[date] = mapped_column(Date)

class Sales_details(Base) :
     __tablename__ = "sales_details"
     id  : Mapped[int] = mapped_column(Integer,primary_key=True)
     sale_id:Mapped[int] = mapped_column(ForeignKey("sale.id"))
     Product_id:Mapped[int] = mapped_column(ForeignKey("product.id"))
     quantity: Mapped[int] = mapped_column(Integer)
     total : Mapped[Float] = mapped_column(Float)

class Purchases(Base) : 
     __tablename__ = "purchases"
     id : Mapped[int] = mapped_column(Integer,primary_key=True)
     Product_id:Mapped[int] = mapped_column(ForeignKey("product.id"))
     purchase_price :  Mapped[Float] = mapped_column(Float)
     puchase_date : Mapped[date] = mapped_column(Date)

class Payments(Base) :
      __tablename__ = "payments"
      id : Mapped[int] = mapped_column(Integer,primary_key=True)
      sale_id:Mapped[int] = mapped_column(ForeignKey("sale.id"))
      amount: Mapped[Float] = mapped_column(Float)
      Payment_method : Mapped[str]= mapped_column(String(50))
