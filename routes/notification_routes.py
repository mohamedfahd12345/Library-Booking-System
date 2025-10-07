from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Notification
from extensions import db, jwt

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications]
    }), 200


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    user_id = int(get_jwt_identity())
    notification = Notification.query.get(notification_id)
    
    if not notification or notification.user_id != user_id:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200
