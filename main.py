# Rest API- tis is a backend API that follows the four rules below
# 1. It has to have a route
# 2. It has to have a method (POST/GET/PUT/DELETE)
# 3. It has to have a status code (200,201,403)
# 4. It has to return data as JSON (key: value pairs)

from flask import Flask, request, jsonify,redirect,url_for,session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token,get_jwt_identity
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from models import Base,Product,User,Purchase,Sale,Payment,Sales_detail

from flask_bcrypt import Bcrypt

app = Flask (__name__)

app.config["JWT_SECRET_KEY"]="hytr4678hgf"
app.secret_key = "jayruywuiurywutruytuhu"

bcrypt=Bcrypt(app)
jwt=JWTManager(app)

# create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

# create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

# create a session to do sql transactions
db_session = Session(engine)

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET": 
        query = select(User)
        users = db_session.scalars(query)

        results = []
        for user in users:
            u = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "password": user.password,
                "phone_number": user.phone_number
            }
            results.append(u)
            return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()

        full_name = data["full_name"]
        email = data["email"]
        password = data["password"]
        phone_number = data["phone_number"]

        if data["full_name"] == "" or data["email"] == "" or data["password"] == "" or data["phone_number"] == "":
            return jsonify({
                "Error": "Ensure all fields are set"}), 400

        # Checking if email already exists
        existing_user = db_session.query(User).filter_by(email=email).first()

        if existing_user:
            return jsonify({
                "Error": "Email is already registered"
            }), 409

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password)

        # Create new user
        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password.decode("utf-8"),
            phone_number=phone_number
        )
        db_session.add(new_user)
        db_session.commit()

        access_token = create_access_token(identity=new_user.id)

        return jsonify({
            "Message": "User added successfully",
            "id": new_user.id,
            "access_token": access_token}), 201

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return jsonify({
            "Message": "Please enter your login details"
        }), 200

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "Error": "Ensure all fields are set"
        }), 403

    # Find registered user
    existing_user = db_session.query(User).filter_by(email=email).first()


    if not existing_user:
        return jsonify({
            "Error": "Invalid email or password"
        }), 401

    if not bcrypt.check_password_hash(existing_user.password, password):
        return jsonify({
            "Error": "Invalid email or password"
        }), 401


    token = create_access_token(identity=email)

    #logged-in user
    session["user_id"] = existing_user.id

    return jsonify({
        "Message": "login successful",
        "user": {
            "id": existing_user.id,
            "email": existing_user.email,
            "full_name": existing_user.full_name
        },
        "token": token
    }), 200



# HOME
@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 405
    

# PRODUCTS

@app.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():

    email = get_jwt_identity()

    user = db_session.scalars(select(User).where(User.email == email)).first()

    if not user:
        return jsonify({"Error": "User not found"}), 404

    if request.method == "GET":

        query = select(Product)
        products = db_session.scalars(query)

        results = []

        for prod in products:
            p = {
                "id": prod.id,
                "product_name": prod.product_name,
                "buying_price": prod.buying_price,
                "selling_price": prod.selling_price
            }

            results.append(p)

        return jsonify(results), 200

    elif request.method == "POST":

        data = request.get_json()

        if (data["product_name"] == "" or data["buying_price"] == "" or data["selling_price"] == ""):
            return jsonify({
                "Error": "Ensure all fields are set"
            }), 403

        new_product = Product(
            user_id=user.id,
            product_name=data["product_name"],
            buying_price=float(data["buying_price"]),
            selling_price=float(data["selling_price"])
        )

        db_session.add(new_product)
        db_session.commit()

        return jsonify({
            "Message": "A new product has been added successfully"
        }), 201
    
# PURCHASES
@app.route("/purchases", methods = ["GET","POST"])
@jwt_required()
def purchase():
    email = get_jwt_identity()

    user = db_session.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
            return jsonify({"Error": "User not found"}), 404

    if request.method == "GET":
        query = select(Purchase)
        purchases = db_session.scalars(query)

        results = []
        for pur in purchases:
            p = {"id":pur.id,
                 "product_id":pur.product_id,
                 "purchase_price":pur.purchase_price,
                 "created_at": p.payment_date.strftime("%Y-%m-%d %I:%M %p") if p.payment_date else None
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
                purchase_price=float(data["purchase_price"])
            )
            db_session.add(new_purchase)
            db_session.commit()
            return jsonify({"Message": "A new purchase has been made successfully"}), 201
    else:
        error={"error" : "Method not allowed"}
        return jsonify(error), 405

# SALES
@app.route("/sales", methods = ["GET","POST"])
@jwt_required()
def sale():

    email = get_jwt_identity()
    
    user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()
    
    if not user:
                return jsonify({"Error": "User not found"}), 404
    

    if request.method == "GET":
        query = select(Sale)
        sales = db_session.scalars(query)

        results = []
        for s in sales:
            s = {"id":s.id,
                 "user_id":s.user_id,
                 "created_at": s.sale_date.strftime("%Y-%m-%d %I:%M %p") if s.sale_date else None
                 }
            results.append(s)
        return jsonify (results),200

    elif request.method == "POST":
        data = request.get_json()
        if data ["user_id"] == "":
            return jsonify({"Error":"Ensure all required fields are set"}),403
        else:
            # store in database
            new_sale=Sale(
                user_id=data["user_id"],
            )
            db_session.add(new_sale)
            db_session.commit()
            return jsonify({"Message": "A new sale has been made successfully"}), 201
    else:
        error={"error" : "Invalid request"}
        return jsonify(error), 405

# PAYMENT
@app.route("/payments", methods = ["GET","POST"])
@jwt_required()
def payments():

    email = get_jwt_identity()
    
    user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()
    
    if not user:
                return jsonify({"Error": "User not found"}), 404

    if request.method == "GET":
        query = select(Payment)
        payments = db_session.scalars(query)

        results = []
        for pts in payments:
            pts = {"id":pts.id,
                 "sale_id":pts.sale_id,
                 "amount":pts.amount,
                 "payment_method":pts.Payment_method,
                 "created_at": pts.sale_date.strftime("%Y-%m-%d %I:%M %p") if pts.sale_date else None
                 }
            results.append(pts)
        return jsonify (results),200

    elif request.method == "POST":
        data = request.get_json()
        if data ["sale_id"] == "" or data["amount"]=="" or data ["payment_method"] == "":
            return jsonify({"Error":"Ensure all required fields are set"}),403
        else:
            # store in database
            new_payment=Payment(
                sale_id=data["sale_id"],
                amount=float(data["amount"]),
                payment_method=data["payment_method"]
            )
            db_session.add(new_payment)
            db_session.commit()
            return jsonify({"Message": "Payment has been made successfully"}), 201
    else:
        error={"error" : "Invalid request"}
        return jsonify(error), 405


# SALES-DETAILS

@app.route("/sales-details", methods = ["GET","POST"])
@jwt_required()
def sales_details():

    email = get_jwt_identity()
    
    user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()
    
    if not user:
                return jsonify({"Error": "User not found"}), 404

    if request.method == "GET":
        query = select(Sales_detail)
        sales_details = db_session.scalars(query)

        results = []
        for sd in sales_details:
            sd = {"id":sd.id,
                 "sale_id":sd.sale_id,
                 "product_id":sd.product_id,
                 "quantity":sd.quantity
                 }
            results.append(sd)
        return jsonify (results),200

    elif request.method == "POST":
        data = request.get_json()
        if data ["sale_id"] == "" or data["product_id"]=="" or data ["quantity"] == "":
            return jsonify({"Error":"Ensure all required fields are set"}),403
        else:
            # store in database
            new_sales_detail=Sales_detail(
                sale_id=data["sale_id"],
                product_id=data["product_id"],
                quantity=int(data["quantity"])
            )
            db_session.add(new_sales_detail)
            db_session.commit()
            return jsonify({"Message": "Sales_detail has been updated successfully"}), 201
    else:
        error={"error" : "Invalid request"}
        return jsonify(error), 405

    


app.run(debug=True)