# Rest API- tis is a backend API that follows the four rules below
# 1. It has to have a route
# 2. It has to have a method (POST/GET/PUT/DELETE)
# 3. It has to have a status code (200,201,403)
# 4. It has to return data as JSON (key: value pairs)

from flask import Flask, request, jsonify, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Product, User, Purchase, Sale, Payment, Sales_detail
import sentry_sdk
from flask_cors import CORS

from flask_bcrypt import Bcrypt

sentry_sdk.init(
    dsn="https://9a3deb04003c766e9983b785c27e62ca@o4512045988773888.ingest.us.sentry.io/4512046189379584",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False
app.config["JWT_SECRET_KEY"] = "hytr4678hgf"
app.secret_key = "jayruywuiurywutruytuhu"

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

# create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

# create a session to do sql transactions
db_session = Session(engine)

allowed_methods = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTIONS"]


# JWT
@jwt.unauthorized_loader
def unauthorized(error):
    return jsonify({
        "url": "http://127.0.0.1:5000/login",
        "name": "Please login"
    }), 401


@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({
        "url": "http://127.0.0.1:5000/login",
        "name": "Your token is invalid. Please login again"
    }), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({
        "url": "http://127.0.0.1:5000/login",
        "name": "Your session has expired. Please login again"
    }), 401

@app.before_request
def before_request():
    try:
        pass
    except:
        pass

# HOME
@app.route("/", methods=allowed_methods)
def home():
    if request.method == "GET":
        return jsonify({"Flask API" : "Version 1"}), 200
    else:
        return jsonify({"Error" : "Method not allowed"}), 405
    

# REGISTER
@app.route("/register", methods=allowed_methods)
def register():
    try:
        if request.method == "GET":
            query = select(User)
            users = db_session.scalars(query)

            results = []

            for user in users:
                u = {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
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
                    "Error": "Ensure all fields are set"
                }), 400

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

            access_token = create_access_token(identity=email)

            return jsonify({
                "id": new_user.id,
                "Message": "User added successfully",
                "access_token": access_token,
                "url": "http://127.0.0.1:5000/login"
            }), 201

        else:
            error = {"Error": "Method not allowed"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


# LOGIN
@app.route("/login", methods=allowed_methods)
def login():
    try:
        if request.method == "GET":
            return jsonify({
                "Message": "Please enter your login details"
            }), 200

        elif request.method == "POST":
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
                "id": existing_user.id,
                "email": existing_user.email,
                "full_name": existing_user.full_name,
                "token": token,
                "url": "http://127.0.0.1:5000/",
                "Message": "login successful"
            }), 200

        else:
            error = {"error": "Method not allowed"}
            return jsonify(error), 405

    except Exception as error:
        return jsonify({"Error": str(error)}), 500


# PRODUCTS
@app.route("/products", methods=allowed_methods)
@jwt_required()
def products():
    try:
        email = get_jwt_identity()

        user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()

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

            if data["product_name"] == "" or data["buying_price"] == "" or data["selling_price"] == "":
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
                "id": new_product.id,
                "Message": "A new product has been added successfully"
            }), 201

        else:
            error = {"error": "Method not allowed"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


# PURCHASES
@app.route("/purchases", methods=allowed_methods)
@jwt_required()
def purchase():
    try:
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
                p = {
                    "id": pur.id,
                    "product_id": pur.product_id,
                    "purchase_price": pur.purchase_price,
                    "created_at": pur.purchase_date.strftime("%Y-%m-%d %I:%M %p")
                    if pur.purchase_date else None
                }

                results.append(p)

            return jsonify(results), 200

        elif request.method == "POST":
            data = request.get_json()

            if data["product_id"] == "" or data["purchase_price"] == "":
                return jsonify({
                    "Error": "Ensure all required fields are set"
                }), 403

            else:
                # store in database
                new_purchase = Purchase(
                    product_id=data["product_id"],
                    purchase_price=float(data["purchase_price"])
                )

                db_session.add(new_purchase)
                db_session.commit()

                return jsonify({
                    "id": new_purchase.id,
                    "Message": "A new purchase has been made successfully"
                }), 201

        else:
            error = {"error": "Method not allowed"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


# SALES
@app.route("/sales", methods=allowed_methods)
@jwt_required()
def sale():
    try:
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
                sale_data = {
                    "id": s.id,
                    "user_id": s.user_id,
                    "created_at": s.sale_date.strftime("%Y-%m-%d %I:%M %p")
                    if s.sale_date else None
                }

                results.append(sale_data)

            return jsonify(results), 200

        elif request.method == "POST":
            data = request.get_json()

            if data["user_id"] == "":
                return jsonify({
                    "Error": "Ensure all required fields are set"
                }), 403

            else:
                # store in database
                new_sale = Sale(
                    user_id=data["user_id"]
                )

                db_session.add(new_sale)
                db_session.commit()

                return jsonify({
                    "id": new_sale.id,
                    "Message": "A new sale has been made successfully"
                }), 201

        else:
            error = {"error": "Method not allowed"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


# PAYMENT
@app.route("/payments", methods=allowed_methods)
@jwt_required()
def payments():
    try:
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
                payment_data = {
                    "id": pts.id,
                    "sale_id": pts.sale_id,
                    "amount": pts.amount,
                    "payment_method": pts.payment_method,
                    "created_at": pts.payment_date.strftime("%Y-%m-%d %I:%M %p")
                    if pts.payment_date else None
                }

                results.append(payment_data)

            return jsonify(results), 200

        elif request.method == "POST":
            data = request.get_json()

            if data["sale_id"] == "" or data["amount"] == "" or data["payment_method"] == "":
                return jsonify({
                    "Error": "Ensure all required fields are set"
                }), 403

            else:
                # store in database
                new_payment = Payment(
                    sale_id=data["sale_id"],
                    amount=float(data["amount"]),
                    payment_method=data["payment_method"]
                )

                db_session.add(new_payment)
                db_session.commit()

                return jsonify({
                    "id": new_payment.id,
                    "Message": "Payment has been made successfully"
                }), 201

        else:
            error = {"error": "Invalid request"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


# SALES-DETAILS
@app.route("/sales-details", methods=allowed_methods)
@jwt_required()
def sales_details():
    try:
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
                sd_data = {
                    "id": sd.id,
                    "sale_id": sd.sale_id,
                    "product_id": sd.product_id,
                    "quantity": sd.quantity
                }

                results.append(sd_data)

            return jsonify(results), 200

        elif request.method == "POST":
            data = request.get_json()

            if data["sale_id"] == "" or data["product_id"] == "" or data["quantity"] == "":
                return jsonify({
                    "Error": "Ensure all required fields are set"
                }), 403

            else:
                # store in database
                new_sales_detail = Sales_detail(
                    sale_id=data["sale_id"],
                    product_id=data["product_id"],
                    quantity=int(data["quantity"])
                )

                db_session.add(new_sales_detail)
                db_session.commit()

                return jsonify({
                    "id": new_sales_detail.id,
                    "Message": "Sales_detail has been updated successfully"
                }), 201

        else:
            error = {"error": "Invalid request"}
            return jsonify(error), 405

    except Exception as error:
        db_session.rollback()
        return jsonify({"Error": str(error)}), 500


app.run(debug=True)