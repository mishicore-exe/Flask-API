from sqlalchemy import ForeignKey
from sqlalchemy import String,Integer,Float,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship,declared_attr
from datetime import datetime


class Base(DeclarativeBase):
    pass

class TimestampMixin:
     created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now())

class User(Base,TimestampMixin):
    __tablename__="users"

    id : Mapped[int]= mapped_column(Integer,primary_key=True)
    full_name : Mapped[str]= mapped_column(String(100))
    email : Mapped[str]= mapped_column(String(100),unique=True,nullable=False) 
    password :  Mapped[str]= mapped_column(String(200),nullable=False) 
    phone_number : Mapped[int]= mapped_column(String(20))

class Product(Base,TimestampMixin):
    __tablename__ = "products"

    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]= mapped_column(ForeignKey("users.id"))
    product_name : Mapped[str]= mapped_column(String(100))
    buying_price: Mapped[Float] = mapped_column(Float)
    selling_price: Mapped[Float] = mapped_column(Float)

class Sale(Base, TimestampMixin) :
    __tablename__ = "sales"

    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))

class Sales_detail(Base) :
     __tablename__ = "sales_details"

     id  : Mapped[int] = mapped_column(Integer,primary_key=True)
     sale_id:Mapped[int] = mapped_column(ForeignKey("sales.id"))
     product_id:Mapped[int] = mapped_column(ForeignKey("products.id"))
     quantity: Mapped[int] = mapped_column(Integer)
     
class Purchase(Base, TimestampMixin) : 
     __tablename__ = "purchases"

     id : Mapped[int] = mapped_column(Integer,primary_key=True)
     product_id:Mapped[int] = mapped_column(ForeignKey("products.id"))
     purchase_price :  Mapped[Float] = mapped_column(Float)

class Payment(Base, TimestampMixin) :
      __tablename__ = "payments"
      
      id : Mapped[int] = mapped_column(Integer,primary_key=True)
      sale_id:Mapped[int] = mapped_column(ForeignKey("sales.id"))
      amount: Mapped[Float] = mapped_column(Float)
      payment_method : Mapped[str]= mapped_column(String(50))
      
    

