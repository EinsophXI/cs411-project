from flask import Flask, request, jsonify, Response, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import os
import binascii

from news_recommender.models.article_model import Article
from news_recommender.models.journal_model import JournalModel


app = Flask(__name__)

# Configure the SQLite database URI, no need for config.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(16), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Create the database and the User table (this should be run once or when the schema changes)
#@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

# Password hashing function with salt
def hash_password(password: str, salt: str) -> str:
    """Hash the password with the salt using SHA256."""
    password_salt = password.encode('utf-8') + salt.encode('utf-8')
    return hashlib.sha256(password_salt).hexdigest()

#####################################

# USER AND PASSWORD CREATION & STORAGE
#all login/password interfaces working!
#####################################

@app.route('/project/create-account', methods=['POST'])
def create_account() -> Response:
    # Get JSON data from the request
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Validate the input data
    if not username or not password:
        return make_response(jsonify({"error": "Username and password are required!"}), 400)

    # Check if the user already exists
    user = User.query.filter_by(username=username).first()
    if user:
        return make_response(jsonify({"error": "Username already exists!"}), 400)

    # Generate a random salt
    salt = binascii.hexlify(os.urandom(8)).decode('utf-8')  # 16-character salt

    # Hash the password with the salt
    hashed_password = hash_password(password, salt)

    # Create a new user and store it in the database
    new_user = User(username=username, salt=salt, hashed_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Return a success response
    return make_response(jsonify({"message": "User created successfully!"}), 201)

@app.route('/project/login', methods=['POST'])
def login() -> Response:
    data = request.get_json()

    # Get the username and password from the request
    username = data.get('username')
    password = data.get('password')

    # Validate input data
    if not username or not password:
        return make_response(jsonify({"error": "Username and password are required!"}), 400)

    # Find user by username
    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response(jsonify({"error": "User not found!"}), 404)

    # Hash the entered password with the stored salt
    hashed_password = hash_password(password, user.salt)

    # Check if the hashed password matches the one stored in the database
    if hashed_password == user.hashed_password:
        return make_response(jsonify({"message": "Login successful!"}), 200)
    else:
        return make_response(jsonify({"error": "Invalid password!"}), 401)

@app.route('/project/update-password', methods=['POST'])
def update_password() -> Response:
    data = request.get_json()

    # Get the username, current password, and new password
    username = data.get('username')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Validate input data
    if not username or not current_password or not new_password:
        return make_response(jsonify({"error": "Username, current password, and new password are required!"}), 400)

    # Find user by username
    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response(jsonify({"error": "User not found!"}), 404)

    # Hash the current password with the stored salt
    hashed_current_password = hash_password(current_password, user.salt)

    # Check if the hashed current password matches the one stored in the database
    if hashed_current_password != user.hashed_password:
        return make_response(jsonify({"error": "Invalid current password!"}), 401)

    # Generate a new salt for the new password
    new_salt = binascii.hexlify(os.urandom(8)).decode('utf-8')

    # Hash the new password with the new salt
    hashed_new_password = hash_password(new_password, new_salt)

    # Update the user's salt and hashed password in the database
    user.salt = new_salt
    user.hashed_password = hashed_new_password
    db.session.commit()

    return make_response(jsonify({"message": "Password updated successfully!"}), 200)


#####################################

#HEALTH CHECK #works!

#####################################

@app.route('/project/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

####################################################
#
# Deletion routes
#
####################################################
    
@app.route('/project/clear-journal', methods=['POST'])
def clear_journal() -> Response:
    """
    Route to clear the list of articles in a journal.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info('Clearing all articles...')
        JournalModel.clear_journal()
        app.logger.info('Journal cleared.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to clear journal: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/clear-catalog', methods=['POST'])
def clear_catalog() -> Response:
    """
    Route to clear all articles in a catalog.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info('Clearing all articles...')
        Article.clear_catalog()
        app.logger.info('Database cleared.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to clear database: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/delete-article/<int:article_id>', methods=['POST'])
def delete_article(article_id: int) -> Response:
    """
    Route to clear a specific article based on the ID.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info(f'Deleting article with ID {article_id}')
        Article.delete_article(article_id)
        app.logger.info('Article deleted.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to delete article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5003)