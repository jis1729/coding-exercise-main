from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

db = SQLAlchemy()

# Decorator to retry database connection
@retry(
    wait=wait_fixed(2), 
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(OperationalError)
)
def connect_to_database(db):
    db.create_all()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/students_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)

    # Import models to create tables
    from .models import Student
    with app.app_context():
        connect_to_database(db)

    from .routes.students import student_bp
    app.register_blueprint(student_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()