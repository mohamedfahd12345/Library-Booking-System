from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Book, Reservation, Notification
from extensions import db, jwt

reservation_bp = Blueprint('reservation', __name__, url_prefix='/api/reservations')

@reservation_bp.route('', methods=['POST'])
@jwt_required()
def create_reservation():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('book_id'):
        return jsonify({'error': 'Book ID required'}), 400
    
    book = Book.query.get(data['book_id'])
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if book.available_copies <= 0:
        return jsonify({'error': 'Book not available'}), 400
    
    # Check if user already has active reservation
    existing = Reservation.query.filter_by(
        user_id=user_id,
        book_id=book.id,
        status='active'
    ).first()
    
    if existing:
        return jsonify({'error': 'You already have an active reservation for this book'}), 409
    
    reservation = Reservation(user_id=user_id, book_id=book.id)
    book.available_copies -= 1
    
    db.session.add(reservation)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        user_id=user_id,
        message=f'You have reserved "{book.title}". Please pick it up within 3 days.',
        type='reservation'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Book reserved successfully',
        'reservation': reservation.to_dict()
    }), 201


@reservation_bp.route('', methods=['GET'])
@jwt_required()
def get_reservations():
    user_id = int(get_jwt_identity())
    
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.reserved_at.desc()).all()
    
    return jsonify({
        'reservations': [r.to_dict() for r in reservations]
    }), 200


@reservation_bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    user_id = int(get_jwt_identity())
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if reservation.status != 'active':
        return jsonify({'error': 'Reservation cannot be cancelled'}), 400
    
    reservation.status = 'cancelled'
    reservation.book.available_copies += 1
    
    db.session.commit()
    
    return jsonify({'message': 'Reservation cancelled successfully'}), 200
