from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from config import Config
from flask_cors import CORS
from extensions import db, jwt


# Load environment variables from .env file
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)

# Import models after db is initialized
from models import User, Book, Reservation, Borrowing, Notification
from decorators import admin_required


# ==================== Decorators ====================


# ==================== Register Blueprints ====================
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.reservation_routes import reservation_bp
from routes.borrowing_routes import borrowing_bp
from routes.notification_routes import notification_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(borrowing_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(admin_bp)


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Initialize Database ====================

@app.route('/api/init-db', methods=['POST'])
def init_database():
    """Initialize database with sample data (for development only)"""
    db.create_all()
    
    # Create admin user
    if not User.query.filter_by(email='admin@library.com').first():
        admin = User(name='Admin', email='admin@library.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create sample member
    if not User.query.filter_by(email='user@library.com').first():
        user = User(name='John Doe', email='user@library.com', role='member')
        user.set_password('user123')
        db.session.add(user)
    
    # Create sample books
    if Book.query.count() == 0:
        books = [
            Book(title='The Great Gatsby', author='F. Scott Fitzgerald', category='Fiction', total_copies=3, available_copies=3),
            Book(title='To Kill a Mockingbird', author='Harper Lee', category='Fiction', total_copies=2, available_copies=2),
            Book(title='1984', author='George Orwell', category='Science Fiction', total_copies=4, available_copies=4),
            Book(title='Pride and Prejudice', author='Jane Austen', category='Romance', total_copies=2, available_copies=2),
            Book(title='The Catcher in the Rye', author='J.D. Salinger', category='Fiction', total_copies=3, available_copies=3),
        ]
        db.session.add_all(books)
    
    db.session.commit()
    
    return jsonify({'message': 'Database initialized successfully'}), 200


# ==================== Main ====================

# Right after creating the app
CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)


