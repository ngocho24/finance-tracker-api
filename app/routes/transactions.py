from flask import Blueprint, request, jsonify
from app.models import db, Transaction
from app.schemas import transaction_schema, transactions_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from marshmallow import ValidationError

trans_bp = Blueprint('transactions', __name__)

# --- CREATE TRANSACTION ---
@trans_bp.route('/', methods=['POST'])
@jwt_required()
def add_transaction():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    # 1. Validate input against the Schema
    try:
        data = transaction_schema.load(json_data)
    except ValidationError as err:
        # Returns specific errors (e.g., "Amount must be greater than 0")
        return jsonify(err.messages), 400

    current_user_id = get_jwt_identity() 
    
    # 2. Create the Database Object
    new_trans = Transaction(
        amount=data['amount'],
        description=data['description'],
        category=data['category'],
        type=data['type'],
        user_id=current_user_id
    )
    
    db.session.add(new_trans)
    db.session.commit()
    
    return jsonify({
        "msg": "Transaction recorded", 
        "transaction": transaction_schema.dump(new_trans)
    }), 201

# --- GET ALL (With Filtering) ---
@trans_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    
    # Get optional filters from query params: /api/transactions?category=Food
    category = request.args.get('category')
    t_type = request.args.get('type')

    query = Transaction.query.filter_by(user_id=current_user_id)

    if category:
        query = query.filter_by(category=category)
    if t_type:
        query = query.filter_by(type=t_type)

    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Use schema to serialize the list of objects into JSON
    return jsonify(transactions_schema.dump(transactions)), 200

# --- GET SUMMARY (Analytics) ---
@trans_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    current_user_id = get_jwt_identity()
    
    # Aggregates totals by type using SQLAlchemy's func.sum
    summary = db.session.query(
        Transaction.type,
        func.sum(Transaction.amount)
    ).filter(Transaction.user_id == current_user_id).group_by(Transaction.type).all()

    # Convert the list of tuples [('income', 500), ('expense', 200)] to a dict
    totals = {t_type: float(total) for t_type, total in summary}
    
    income = totals.get('income', 0.0)
    expense = totals.get('expense', 0.0)
    
    return jsonify({
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    }), 200