from flask import Blueprint, request, jsonify
from app.models import db, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity

trans_bp = Blueprint('transactions', __name__)

@trans_bp.route('/', methods=['POST'])
@jwt_required()
def add_transaction():
    data = request.get_json()
    # jwt_required ensures we have a valid token; identity is usually the user_id or email
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
    transactions = Transaction.query.filter_by(user_id=current_user_id).all()
    return jsonify([t.to_dict() for t in transactions]), 200