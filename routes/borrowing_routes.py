from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Book, User, Borrowing, Reservation, Notification
from decorators import admin_required
from datetime import datetime, timedelta
from extensions import db, jwt

borrowing_bp = Blueprint('borrowing', __name__, url_prefix='/api/borrowings')

@borrowing_bp.route('', methods=['POST'])
@admin_required
def create_borrowing():
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('book_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    book = Book.query.get(data['book_id'])
    user = User.query.get(data['user_id'])
    
    if not book or not user:
        return jsonify({'error': 'Book or user not found'}), 404
    
    # Check for active reservation
    reservation = Reservation.query.filter_by(
        user_id=user.id,
        book_id=book.id,
        status='active'
    ).first()
    
    if reservation:
        reservation.status = 'fulfilled'
    elif book.available_copies <= 0:
        return jsonify({'error': 'Book not available'}), 400
    else:
        book.available_copies -= 1
    
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    
    db.session.add(borrowing)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=user.id,
        message=f'You have borrowed "{book.title}". Due date: {borrowing.due_date.strftime("%Y-%m-%d")}',
        type='due_date'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Book borrowed successfully',
        'borrowing': borrowing.to_dict()
    }), 201


@borrowing_bp.route('', methods=['GET'])
@jwt_required()
def get_borrowings():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims.get('role') == 'admin':
        borrowings = Borrowing.query.order_by(Borrowing.borrowed_at.desc()).all()
    else:
        borrowings = Borrowing.query.filter_by(user_id=user_id).order_by(Borrowing.borrowed_at.desc()).all()
    
    return jsonify({
        'borrowings': [b.to_dict() for b in borrowings]
    }), 200


@borrowing_bp.route('/<int:borrowing_id>/return', methods=['POST'])
@admin_required
def return_book(borrowing_id):
    borrowing = Borrowing.query.get(borrowing_id)
    
    if not borrowing:
        return jsonify({'error': 'Borrowing record not found'}), 404
    
    if borrowing.returned_at:
        return jsonify({'error': 'Book already returned'}), 400
    
    borrowing.returned_at = datetime.utcnow()
    borrowing.book.available_copies += 1
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book returned successfully',
        'borrowing': borrowing.to_dict()
    }), 200
