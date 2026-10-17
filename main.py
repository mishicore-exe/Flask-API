from flask import Flask, request, jsonify, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Product, User, Purchase, Sale, Payment, Sales_detail
from flask_bcrypt import Bcrypt
import sentry_sdk
from mpesa import make_stk_push
from generate_receipts import create_pdf


sentry_sdk.init(
    dsn="https://9a3deb04003c766e9983b785c27e62ca@o4512045988773888.ingest.us.sentry.io/4512046189379584",
    send_default_pii=True,
)


app = Flask(__name__)

CORS(app)

app.config["JSON_SORT_KEYS"] = False
app.config["JWT_SECRET_KEY"] = "hytr4678hgf"
app.secret_key = "jayruywuiurywutruytuhu"

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)
Base.metadata.create_all(engine)

db_session = Session(engine)

allowed_methods=["PUT","GET","PATCH","DELETE","POST"]

@jwt.unauthorized_loader
def unauthorized(error):
    return jsonify({
        "Error": "Please login"
    }), 401

@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({
        "Error": "Your token is invalid. Please login again"
    }), 401

@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({
        "Error": "Your session has expired. Please login again"
    }), 401

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "Flask API": "Version 1"
    }), 200

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        phone_number = data.get("phone_number")

        if not full_name or not email or not password or not phone_number:
            return jsonify({
                "Error": "Ensure all fields are set"
            }), 400

        existing_user = db_session.query(User).filter_by(email=email).first()

        if existing_user:
            return jsonify({
                "Error": "Email is already registered"
            }), 409

        hashed_password = bcrypt.generate_password_hash(password)

        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password.decode("utf-8"),
            phone_number=phone_number
        )
        db_session.add(new_user)
        db_session.commit()

        token = create_access_token(identity=email)

        return jsonify({
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "token": token,
            "Message": "User added successfully"
        }), 201

    except Exception as error:
        db_session.rollback()

        return jsonify({
            "Error": str(error)
        }), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "Error": "Ensure all fields are set"
            }), 403

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

        session["user_id"] = existing_user.id

        return jsonify({
            "id": existing_user.id,
            "email": existing_user.email,
            "full_name": existing_user.full_name,
            "phone_number": existing_user.phone_number,
            "token": token,
            "Message": "Login successful"
        }), 200

    except Exception as error:
        return jsonify({
            "Error": str(error)
        }), 500

@app.route("/products", methods=allowed_methods)
@jwt_required()
def products():
    try:
        email = get_jwt_identity()
        user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()

        if not user:
            return jsonify({
                "Error": "User not found"
            }), 404

        if request.method == "GET":
            products = db_session.scalars(
                select(Product).where(Product.user_id == user.id)
            )
            results = []

            for prod in products:
                results.append({
                    "id": prod.id,
                    "product_name": prod.product_name,
                    "category": prod.category,
                    "buying_price": prod.buying_price,
                    "selling_price": prod.selling_price,
                    "created_at": prod.created_at.isoformat()
                    if prod.created_at else None
                })

            return jsonify({
                "data": results
            }), 200

        data = request.get_json()

        if not data:
            return jsonify({
                "Error": "No data provided"
            }), 400

        if request.method == "POST":
            if (
                not data.get("product_name")
                or not data.get("category")
                or data.get("buying_price") is None
                or data.get("selling_price") is None
            ):
                return jsonify({
                    "Error": "Ensure all fields are set"
                }), 403

            new_product = Product(
                user_id=user.id,
                product_name=data["product_name"],
                category=data["category"],
                buying_price=float(data["buying_price"]),
                selling_price=float(data["selling_price"])
            )

            db_session.add(new_product)
            db_session.commit()

            return jsonify({
                "id": new_product.id,
                "Message": "A new product has been added successfully"
            }), 201

        if request.method == "PUT":
            product_id = data.get("id")

            if not product_id:
                return jsonify({
                    "Error": "Product ID is required"
                }), 400

            product = db_session.get(Product, product_id)

            if not product:
                return jsonify({
                    "Error": "Product not found"
                }), 404

            if product.user_id != user.id:
                return jsonify({
                    "Error": "You cannot edit this product"
                }), 403

            if (
                not data.get("product_name")
                or not data.get("category")
                or data.get("buying_price") is None
                or data.get("selling_price") is None
            ):
                return jsonify({
                    "Error": "Ensure all fields are set"
                }), 403

            product.product_name = data["product_name"]
            product.category = data["category"]
            product.buying_price = float(data["buying_price"])
            product.selling_price = float(data["selling_price"])

            db_session.commit()

            return jsonify({
                "Message": "Product updated successfully"
            }), 200

        if request.method == "DELETE":
            product_id = data.get("id")

            if not product_id:
                return jsonify({
                    "Error": "Product ID is required"
                }), 400

            product = db_session.get(Product, product_id)

            if not product:
                return jsonify({
                    "Error": "Product not found"
                }), 404

            if product.user_id != user.id:
                return jsonify({
                    "Error": "You cannot delete this product"
                }), 403

            db_session.delete(product)
            db_session.commit()

            return jsonify({
                "Message": "Product deleted successfully"
            }), 200

    except Exception as error:
        db_session.rollback()
        print("PRODUCT ERROR:", error)

        return jsonify({
            "Error": str(error)
        }), 500

@app.route("/sales", methods=allowed_methods)
@jwt_required()
def sales():
    try:
        email = get_jwt_identity()

        user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()

        if not user:
            return jsonify({
                "Error": "User not found"
            }), 404

        if request.method == "GET":
            sales = db_session.scalars(
                select(Sale).where(Sale.user_id == user.id)
            )

            results = []

            for sale in sales:
                product = db_session.get(Product, sale.product_id)

                if product:
                    results.append({
                        "id": sale.id,
                        "product_id": sale.product_id,
                        "product_name": product.product_name,
                        "quantity": sale.quantity,
                        "total": product.selling_price * sale.quantity,
                        "created_at": sale.created_at.isoformat()
                        if sale.created_at else None
                    })

            return jsonify({
                "data": results
            }), 200

        data = request.get_json()

        if not data:
            return jsonify({
                "Error": "No data provided"
            }), 400

        if request.method == "POST":
            product_id = data.get("product_id")
            quantity = data.get("quantity")

            if not product_id or not quantity:
                return jsonify({
                    "Error": "Product and quantity are required"
                }), 400

            product = db_session.get(Product, product_id)

            if not product:
                return jsonify({
                    "Error": "Product not found"
                }), 404

            if product.user_id != user.id:
                return jsonify({
                    "Error": "You cannot sell this product"
                }), 403

            new_sale = Sale(
                user_id=user.id,
                product_id=product.id,
                quantity=int(quantity)
            )

            db_session.add(new_sale)
            db_session.commit()

            return jsonify({
                "id": new_sale.id,
                "Message": "Sale added successfully"
            }), 201

        if request.method == "PUT":
            sale_id = data.get("id")
            product_id = data.get("product_id")
            quantity = data.get("quantity")

            if not sale_id:
                return jsonify({
                    "Error": "Sale ID is required"
                }), 400

            if not product_id or not quantity:
                return jsonify({
                    "Error": "Product and quantity are required"
                }), 400

            sale = db_session.get(Sale, sale_id)

            if not sale:
                return jsonify({
                    "Error": "Sale not found"
                }), 404

            if sale.user_id != user.id:
                return jsonify({
                    "Error": "You cannot edit this sale"
                }), 403

            product = db_session.get(Product, product_id)

            if not product:
                return jsonify({
                    "Error": "Product not found"
                }), 404

            if product.user_id != user.id:
                return jsonify({
                    "Error": "You cannot use this product"
                }), 403

            sale.product_id = product_id
            sale.quantity = int(quantity)

            db_session.commit()

            return jsonify({
                "Message": "Sale updated successfully"
            }), 200
        
        if request.method == "DELETE":
            sale_id = data.get("id")

            if not sale_id:
                return jsonify({
                    "Error": "Sale ID is required"
                }), 400

            sale = db_session.get(Sale, sale_id)

            if not sale:
                return jsonify({
                    "Error": "Sale not found"
                }), 404

            if sale.user_id != user.id:
                return jsonify({
                    "Error": "You cannot delete this sale"
                }), 403

            try:
                db_session.delete(sale)
                db_session.commit()

                return jsonify({
                    "Message": "Sale deleted successfully"
                }), 200

            except Exception as error:
                db_session.rollback()
                print("DELETE SALE DATABASE ERROR:", repr(error))

                return jsonify({
                    "Error": "Failed to delete sale because of a database error"
                }), 500

    except Exception as error:
        db_session.rollback()
        print("SALES ERROR:", repr(error))

        return jsonify({
            "Error": str(error)
        }), 500

@app.route("/sales-details", methods=["GET", "POST"])
@jwt_required()
def sales_details():
    try:
        email = get_jwt_identity()

        user = db_session.scalars(
            select(User).where(User.email == email)
        ).first()

        if not user:
            return jsonify({
                "Error": "User not found"
            }), 404

        if request.method == "GET":

            sales_details = db_session.scalars(
                select(Sales_detail)
            )

            results = []

            for sd in sales_details:
                results.append({
                    "id": sd.id,
                    "sale_id": sd.sale_id,
                    "product_id": sd.product_id,
                    "quantity": sd.quantity
                })

            return jsonify({
                "data": results
            }), 200

        data = request.get_json()

        if (
            data.get("sale_id") in ["", None]
            or data.get("product_id") in ["", None]
            or data.get("quantity") in ["", None]
        ):
            return jsonify({
                "Error": "Ensure all required fields are set"
            }), 403

        new_sales_detail = Sales_detail(
            sale_id=data["sale_id"],
            product_id=data["product_id"],
            quantity=int(data["quantity"])
        )

        db_session.add(new_sales_detail)
        db_session.commit()

        return jsonify({
            "id": new_sales_detail.id,
            "Message": "Sales detail has been added successfully"
        }), 201

    except Exception as error:
        db_session.rollback()

        return jsonify({
            "Error": str(error)
        }), 500


@app.route("/stk_push", methods=["POST"])
def stk_push():
    try:
        payload = request.get_json()
        response = make_stk_push(payload)

        new_payment = Payment(
            sale_id=payload["sale_id"],
            amount_paid=payload["amount_paid"],
            phone_number=payload["phone_number"],
            mrid=response.get("MerchantRequestID"),
            crid=response.get("CheckoutRequestID"),
            payment_status="pending"
        )

        db_session.add(new_payment)
        db_session.commit()

        return {"message": "STK push initiated"}

    except Exception as e:
        db_session.rollback()
        print("STK push error:", e)
        return {"error": str(e)}, 500

@app.route('/saf-callback', methods=allowed_methods)
def saf_callback():
    try:
        payload = request.get_json()
        stkCallback = payload.get('Body', {}).get('stkCallback', {})
        result_code = stkCallback.get('ResultCode')
        mrid = stkCallback.get('MerchantRequestID')
        crid = stkCallback.get('CheckoutRequestID')
        payment = db_session.scalars(select(Payment).where(Payment.mrid == mrid, Payment.crid == crid)).first()
        if not payment:
            return {"message": "Payment not found"}, 200
        if result_code == 0:
            items = stkCallback.get('CallbackMetadata', {}).get('Item', [])
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.transaction_code = item.get('Value')
                elif item.get('Name') == 'Amount':
                    payment.amount_paid = item.get('Value')
            payment.payment_status = "completed"
        else:
            payment.payment_status = "failed"
        db_session.commit()
    except Exception:
        db_session.rollback()
        import traceback
        traceback.print_exc()
    return {"message": "Callback received"}, 200

@app.route('/payments', methods=allowed_methods)
def get_payments():
    payments = db_session.scalars(select(Payment)).all()
    return [{
        "id": p.id,
        "sale_id": p.sale_id,
        "amount_paid": p.amount_paid,
        "transaction_code": p.transaction_code,
        "payment_status": p.payment_status,
        "phone_number": p.phone_number,
        "mrid": p.mrid,
        "crid": p.crid
    } for p in payments], 200

app.run(debug=True)