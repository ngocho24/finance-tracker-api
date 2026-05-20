from flask import Blueprint, request, jsonify
from app.models import db, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

trans_bp = Blueprint('transactions', __name__)

@trans_bp.route('/', methods=['POST'])
@jwt_required()
def add_transaction():
    data = request.get_json()
    current_user_id = get_jwt_identity() 
    
    new_trans = Transaction(
        amount=data.get('amount'),
        description=data.get('description'),
        category=data.get('category'),
        type=data.get('type'),
        user_id=current_user_id
    )
    
    db.session.add(new_trans)
    db.session.commit()
    
    return jsonify({"msg": "Transaction recorded", "transaction": new_trans.to_dict()}), 201

@trans_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    
    # Optional Filtering logic
    category = request.args.get('category')
    t_type = request.args.get('type')

    query = Transaction.query.filter_by(user_id=current_user_id)

    if category:
        query = query.filter_by(category=category)
    if t_type:
        query = query.filter_by(type=t_type)

    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions]), 200

@trans_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    current_user_id = get_jwt_identity()
    
    # Calculate totals grouped by type (income vs expense)
    summary = db.session.query(
        Transaction.type,
        func.sum(Transaction.amount)
    ).filter(Transaction.user_id == current_user_id).group_by(Transaction.type).all()

    # Convert list of tuples to a dictionary
    totals = {t_type: float(total) for t_type, total in summary}
    
    income = totals.get('income', 0.0)
    expense = totals.get('expense', 0.0)
    
    return jsonify({
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    }), 200