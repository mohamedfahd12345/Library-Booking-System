
# Library-Booking-System

## Project Description
The Library Booking System is a Flask-based web application that allows users to manage books, reservations, and borrowings in a library. It provides functionalities for both members and administrators, including user authentication, book management, reservation of books, borrowing tracking, and notifications.

## Features

### User Management
- Users can register, log in, and log out.
- Two types of users:
    - **Member**: Regular library users.
    - **Admin**: Librarians with management privileges.
- **Profile Management**: Users can update their name, email, and password, and view their borrowing history.

### Book Catalog
- Each book has a total number of copies and a current number of available copies.
- Admins can add, edit, delete, and manage books (title, author, category, number of copies, etc.).
- Users can search and filter books by title, author, or category.
- Every book shows its availability status.
- If there are no available copies left, the book is marked as Unavailable.

### Reservation System
- Users can reserve books that are currently available.
- Reserving a book temporarily removes one copy from availability.
- Users can cancel reservations before pickup to make the copy available again.
- Books with no available copies cannot be reserved.

### Borrowing System
- Users can borrow reserved books when they visit the library.
- Users can also borrow books directly if copies are available — no reservation needed.
- Each borrowed book has a due date for return.
- Admins can mark books as returned, which makes them available again.

### Notifications
- Users receive in-app notifications when:
    - A due date is approaching.
    - A book becomes overdue.

### Reports & Tracking (Admin)
- View most borrowed books.
- Track overdue books and user activity.
- Review each user’s borrowing history.

### Database Initialization
- The system includes sample data for easy setup and testing.

## Technologies Used
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Psycopg2 (for PostgreSQL)
- python-dotenv
- Werkzeug (for password hashing)
- Gunicorn (for production deployment)

## Prerequisites
- Python 3.8+
- PostgreSQL database

## Installation & Setup

1. **Clone the Repository**
   ```bash
   https://github.com/mohamedfahd12345/Library-Booking-System
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   ```bash
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Database Setup**
   ```sql
   CREATE DATABASE library_db;
   ```

6. **Environment Configuration**
   Create a `.env` file in the root directory of the project with the following content:
   ```ini
   DATABASE_URL=postgresql://library_user:secure_password@localhost/library_db
   JWT_SECRET_KEY=your-super-secret-key
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

7. **Initialize Database**

   Run the Flask app in one terminal:
   ```bash
   python app.py
   ```
   In another terminal, initialize with sample data:
   ```bash
   curl -X POST http://localhost:5000/api/init-db
   ```

## Default Admin Account
After initializing the database by calling the initialization endpoint:
```bash
curl -X POST http://localhost:5000/api/init-db
```
A default admin account is automatically created with the following credentials:
- **Email**: `admin@library.com`
- **Password**: `admin123`
  
## System Architecture Diagram
![System Architecture Diagram](https://github.com/mohamedfahd12345/Library-Booking-System/blob/main/Screenshots/systemDesign.png)

## Database Schema
![Database Schema](https://github.com/mohamedfahd12345/Library-Booking-System/blob/main/Screenshots/databaseDesign.png)

## API Endpoints

The API endpoints are organized into blueprints. All endpoints are prefixed with `/api`.

### Authentication (`routes/auth_routes.py`)
- `POST /api/auth/register`: Register a new user.
- `POST /api/auth/login`: Log in a user and get JWT tokens.
- `GET /api/auth/profile`: Get the logged-in user's profile.
- `PUT /api/auth/profile`: Update the logged-in user's profile.

### Books (`routes/book_routes.py`)
- `GET /api/books`: Get all books.
- `GET /api/books/<int:book_id>`: Get a specific book.
- `POST /api/books`: Add a new book (Admin only).
- `PUT /api/books/<int:book_id>`: Update a book (Admin only).
- `DELETE /api/books/<int:book_id>`: Delete a book (Admin only).

### Reservations (`routes/reservation_routes.py`)
- `POST /api/reservations`: Create a new reservation for a book.
- `GET /api/reservations`: Get user's reservations.
- `DELETE /api/reservations/<int:reservation_id>`: Cancel a reservation.

### Borrowings (`routes/borrowing_routes.py`)
- `POST /api/borrowings`: Borrow a book (Admin only).
- `GET /api/borrowings`: Get all borrowings (Admin only) or user's borrowings (Member).
- `POST /api/borrowings/<int:borrowing_id>/return`: Return a borrowed book (Admin only).

### Notifications (`routes/notification_routes.py`)
- `GET /api/notifications`: Get user's notifications.
- `POST /api/notifications/<int:notification_id>/read`: Mark a notification as read.

### Admin (`routes/admin_routes.py`)
- `GET /api/admin/reports/popular-books`: Get a report on popular books.
- `GET /api/admin/reports/overdue-books`: Get a report on overdue books.
- `GET /api/admin/reports/user-history/<int:user_id>`: Get a user's borrowing history.
- `GET /api/admin/reservations`: Get all reservations.
- `POST /api/admin/check-due-dates`: Manually trigger due date checks and notifications.

### Database Initialization (`app.py`)
- `POST /api/init-db`: Initialize the database with sample data.
  

## API Documentation
You can find the API documentation [here](https://documenter.getpostman.com/view/24694319/2sB3QJPqvJ)

## Frontend Service Repo
[GitHub - Frontend-Library-Booking-System](https://github.com/mohamedfahd12345/Frontend-Library-Booking-System)



