from flask import Blueprint, request, jsonify
from models import Book
from decorators import admin_required
from extensions import db, jwt

book_bp = Blueprint('book', __name__, url_prefix='/api/books')

@book_bp.route('', methods=['GET'])
def get_books():
    # Search and filter
    query = Book.query
    
    if request.args.get('search'):
        search = f"%{request.args.get('search')}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(search),
                Book.author.ilike(search)
            )
        )
    
    if request.args.get('category'):
        query = query.filter_by(category=request.args.get('category'))
    
    if request.args.get('author'):
        query = query.filter(Book.author.ilike(f"%{request.args.get('author')}%"))
    
    books = query.all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book.to_dict()), 200


@book_bp.route('', methods=['POST'])
@admin_required
def create_book():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        category=data.get('category', 'General'),
        isbn=data.get('isbn'),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('total_copies', 1),
        description=data.get('description')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'message': 'Book created successfully',
        'book': book.to_dict()
    }), 201


@book_bp.route('/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    book = Book.query.get(book_id)
    data = request.get_json()
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if data.get('title'):
        book.title = data['title']
    if data.get('author'):
        book.author = data['author']
    if data.get('category'):
        book.category = data['category']
    if data.get('isbn'):
        book.isbn = data['isbn']
    if 'total_copies' in data:
        book.total_copies = data['total_copies']
    if 'available_copies' in data:
        book.available_copies = data['available_copies']
    if data.get('description'):
        book.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book updated successfully',
        'book': book.to_dict()
    }), 200


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'}), 200
