from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import Book, User, Borrowing, Notification, Reservation
from decorators import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db, jwt

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/reports/popular-books', methods=['GET'])
@admin_required
def popular_books():
    results = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        func.count(Borrowing.id).label('borrow_count')
    ).join(Borrowing).group_by(Book.id).order_by(func.count(Borrowing.id).desc()).limit(10).all()
    
    return jsonify({
        'popular_books': [
            {
                'id': r.id,
                'title': r.title,
                'author': r.author,
                'borrow_count': r.borrow_count
            }
            for r in results
        ]
    }), 200


@admin_bp.route('/reports/overdue-books', methods=['GET'])
@admin_required
def overdue_books():
    overdue = Borrowing.query.filter(
        Borrowing.returned_at.is_(None),
        Borrowing.due_date < datetime.utcnow()
    ).all()
    
    # Mark as overdue
    for borrowing in overdue:
        if not borrowing.is_overdue:
            borrowing.is_overdue = True
            # Create notification
            notification = Notification(
                user_id=borrowing.user_id,
                message=f'\"{borrowing.book.title}\" is overdue. Please return it as soon as possible.',
                type='overdue'
            )
            db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'overdue_books': [
            {
                'borrowing': b.to_dict(),
                'user': b.user.to_dict(),
                'days_overdue': (datetime.utcnow() - b.due_date).days
            }
            for b in overdue
        ]
    }), 200


@admin_bp.route('/reports/user-history/<int:user_id>', methods=['GET'])
@admin_required
def user_borrowing_history(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    borrowings = Borrowing.query.filter_by(user_id=user_id).order_by(Borrowing.borrowed_at.desc()).all()
    
    return jsonify({
        'user': user.to_dict(),
        'borrowing_history': [b.to_dict() for b in borrowings],
        'total_borrowed': len(borrowings),
        'currently_borrowed': len([b for b in borrowings if not b.returned_at])
    }), 200


@admin_bp.route('/reservations', methods=['GET'])
@admin_required
def get_all_reservations():
    reservations = db.session.query(Reservation, User, Book).join(User, Reservation.user_id == User.id).join(Book, Reservation.book_id == Book.id).order_by(
            db.case(
                (Reservation.status == 'active', 0),
                else_=1
            ),
            Reservation.reserved_at.desc()
        ).all()

    response_data = []
    for reservation, user, book in reservations:
        response_data.append({
            'reservation_id': reservation.id,
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'reservation_status': reservation.status,
            'reserved_at': reservation.reserved_at.isoformat(),
            'expires_at': reservation.expires_at.isoformat(),
            'book_id': book.id,
            'book_title': book.title
        })
    
    return jsonify({'reservations': response_data}), 200


@admin_bp.route('/check-due-dates', methods=['POST'])
@admin_required
def check_due_dates():
    """Check for books due within 3 days and send notifications"""
    upcoming_due = Borrowing.query.filter(
        Borrowing.returned_at.is_(None),
        Borrowing.due_date <= datetime.utcnow() + timedelta(days=3),
        Borrowing.due_date > datetime.utcnow()
    ).all()
    
    notifications_created = 0
    for borrowing in upcoming_due:
        # Check if notification already exists
        existing = Notification.query.filter_by(
            user_id=borrowing.user_id,
            type='due_date',
            is_read=False
        ).filter(
            Notification.message.like(f'%{borrowing.book.title}%')
        ).first()
        
        if not existing:
            days_remaining = (borrowing.due_date - datetime.utcnow()).days
            notification = Notification(
                user_id=borrowing.user_id,
                message=f'Reminder: \"{borrowing.book.title}\" is due in {days_remaining} day(s).',
                type='due_date'
            )
            db.session.add(notification)
            notifications_created += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'{notifications_created} notifications created',
        'upcoming_due_count': len(upcoming_due)
    }), 200
