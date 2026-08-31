# Rest API- tis is a backend API that follows the four rules below
# 1. It has to have a route
# 2. It has to have a method (POST/GET/PUT/DELETE)
# 3. It has to have a status code (200,201,403)
# 4. It has to return data as JSON (key: value pairs)

from flask import Flask, request, jsonify
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from models import Base,Product,User,Purchase,Sale

app = Flask (__name__)

# create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

# create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

# create a session to do sql transactions
session = Session(engine)

user = {
   "id" : 1,
   "full_name" : "Mitchelle Wanjohi",
   "email" : "mishi@gmail.com",
   "password" : "mishi2007",
   "phone_number" : "0712345678"}

@app.before_request
def before_request():
    try:
        print("A request is coming in!")
        new_user = User(user)
        session.add(new_user)
    except:
        print("Error found")
    

@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 405
    

# PRODUCTS
@app.route("/products",methods = ["GET","POST"])
def products():
    if request.method == "GET":
        # fetch data from the database
        query = select(Product)
        products = session.scalars(query)

        results = []
        for prod in products:
            p = {"id": prod.id,
                 "product_name": prod.product_name,
                 "buying_price": prod.buying_price,
                 "selling_price": prod.selling_price} 
            results.append(p)
        return jsonify(results), 200
    
    elif request.method == "POST":
        data = request.get_json()
        if data["product_name"] == "" or data["buying_price"] == "" or data["selling_price"] == "":
            return jsonify({"Error": "Ensure all fields are set"}), 403
        else:
            # store in the database
            new_product = Product(
                user_id = user["id"],
                product_name = data["product_name"],
                buying_price = float(data["buying_price"]),
                selling_price = float(data["selling_price"])
            )
            session.add(new_product)
            session.commit()
            return jsonify({"Message": "A new product has been added successfully"}), 201
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 405
    
# PURCHASES
@app.route("/purchases", methods = ["GET","POST"])
def purchase():
    if request.method == "GET":
        query = select(Purchase)
        purchases = session.scalars(query)

        results = []
        for pur in purchases:
            p = {"id":pur.id,
                 "product_id":pur.product_id,
                 "purchase_price":pur.purchase_price,
                 "payment_date": p.payment_date.strftime("%Y-%m-%d %I:%M %p") if p.payment_date else None
                 }
                 
            
            results.append(p)
        return jsonify (results),200

    elif request.method == "POST":
        data = request.get_json()
        if data ["product_id"] == "" or data ["purchase_price"] =="":
            return jsonify({"Error":"Ensure all required fields are set"}),403
        else:
            # store in database
            new_purchase=Purchase(
                product_id=data["product_id"],
                purchase_price=data["purchase_price"]
            )
            session.add(new_purchase)
            session.commit()
            return jsonify({"Message": "A new purchase has been made successfully"}), 201
    else:
        error={"error" : "Invalid request"}
        return jsonify(error), 405

# SALES
@app.route("/sales", methods = ["GET","POST"])
def sale():
    if request.method == "GET":
        query = select(Sale)
        sales = session.scalars(query)

        results = []
        for sal in sales:
            s = {"id":sal.id,
                 "user_id":sal.user_id,
                 "total_amount":sal.total_amount,
                 "sale_date": s.sale_date.strftime("%Y-%m-%d %I:%M %p") if s.sale_date else None
                 }
            results.append(s)
        return jsonify (results),200

    elif request.method == "POST":
        data = request.get_json()
        if data ["user_id"] == "" or data ["total_amount"] =="" :
            return jsonify({"Error":"Ensure all required fields are set"}),403
        else:
            # store in database
            new_sale=Purchase(
                sale_id=data["sale_id"],
                total_amount=data["total_amount"]
            )
            session.add(new_sale)
            session.commit()
            return jsonify({"Message": "A new sale has been made successfully"}), 201
    else:
        error={"error" : "Invalid request"}
        return jsonify(error), 405


    


app.run(debug=True)