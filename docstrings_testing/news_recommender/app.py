from flask import Flask, request, jsonify, Response, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import os
import binascii
from dotenv import load_dotenv

from news_recommender.utils.sql_utils import check_database_connection, check_table_exists

from news_recommender.models.article_model import Article
from news_recommender.models.journal_model import JournalModel
from news_recommender.models import article_model

journal_model = JournalModel()

load_dotenv()

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

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and songs table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if articles table exists...")
        check_table_exists("articles")
        app.logger.info("articles table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)  

#####################################

# Addition Routes

#####################################

@app.route('/project/create-article', methods=['POST'])
def create_article() -> Response:
    """
    Route to add a new article.

    Expected JSON Input:
        - id (int): The ID of the article,
        - name (str): The name of the article.
        - author (str): The author of the article.
        - title (str): The title of the article. 
        - url (str): The URL of the article.
        - content (str): The contents of the article.
        - publishedAt (str): Date that the article was published

    Returns:
        JSON response indicating the success of the combatant addition.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the combatant to the database.
    """
    app.logger.info('Creating new article')
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract and validate required fields
        id = data.get('id')
        name = data.get('name')
        author = data.get('author')
        title = data.get('title')
        url = data.get('url')
        content = data.get('content')
        publishedAt = data.get('publishedAt')


        if not id or not name or not author or not title or not url or not content or not publishedAt:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Check that publishedAt is in date format and is in DD-MM-YYYY
        try:
            days = publishedAt[:2]
            month = publishedAt[3:5]
            year = publishedAt[6:]
            if days < 1 or days > 31:
                raise ValueError("Enter valid day")
            if month < 1 or month > 12:
                raise ValueError("Enter a valid month")
            if year < 2025:
                raise ValueError("Please enter a date in the past")
        except ValueError as e:
            return make_response(jsonify({'error': 'Please enter your date in correct format: DD-MM-YYYY'}), 400)

        # Call the kitchen_model function to add the combatant to the database
        app.logger.info('Adding article: %s, %s, %s, %s, %s, %s', name, author, title, url, content, publishedAt)
        article_model.create_article(name, author, title, url, content, publishedAt)

        app.logger.info("Article added: %s", name)
        return make_response(jsonify({'status': 'success', 'message': 'Articles retrieved successfully','article name': name}), 201)
    except Exception as e:
        app.logger.error("Failed to add article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/add-article-to-journal', methods=['POST'])
def add_article_to_journal() -> Response:
    """
    Route to add a article to the journal by compound key (author, title, url).

    Expected JSON Input:
        - id (int) = The article ID.
        - name (str) = The article name.
        - author (str) = The article author.
        - title (str) = The article title.
        - url (str) = The article url.
        - content (str) = The article content.
        - publishedAt (str) = The article publish date.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:
        data = request.get_json()

        id = data.get('id')
        name = data.get('name')
        author = data.get('author')
        title = data.get('title')
        url = data.get('url')
        content = data.get('content')
        publishedAt = data.get('publishedAt')

        if not id or not name or not author or not title or not url or not content or not publishedAt:
            return make_response(jsonify({'error': 'Invalid input. ID, name, author, title, url, content, and publish date are required.'}), 400)

        # Lookup the song by compound key
        article = article_model.get_article_by_compound_key(name, title, url)

        # Add song to playlist
        journal_model.add_article_to_journal(article)

        app.logger.info(f"Article added to journal: {author} - {title} ({publishedAt})")
        return make_response(jsonify({'status': 'success', 'message': 'Article added to journal'}), 200)

    except Exception as e:
        app.logger.error(f"Error adding article to journal: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

####################################################
#
# Retrieval routes
#
####################################################

@app.route('/project/get-article-by-id/<int:article_id>', methods=['GET'])
def get_article_by_id(article_id: int) -> Response:
    """
    Route to get a article by its ID.

    Returns:
        JSON response with the articles in a list or error message.
    """
    try:
        app.logger.info(f"Retrieving article with ID {article_id}...")

        article = JournalModel.get_article_by_article_id(article_id)
        return make_response(jsonify({'status': 'success', 'article name': article.name}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving article: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/get-article-by-id/<int:article_num>', methods=['GET'])
def get_article_by_num(article_num: int) -> Response:
    """
    Route to get a article by its number.

    Returns:
        JSON response with the articles in a list or error message.
    """
    try:
        app.logger.info(f"Retrieving article with number {article_num}...")

        article = JournalModel.get_article_by_article_number(article_num)
        return make_response(jsonify({'status': 'success', 'article': article}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving article: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/get-current-article', methods=['GET'])
def get_current_article() -> Response:
    """
    Route to get the current article.

    Returns:
        JSON response with the articles in a list or error message.
    """
    try:
        app.logger.info(f"Retrieving current article...")

        article = JournalModel.get_current_article()
        return make_response(jsonify({'status': 'success', 'article name': article.name, 'article ID': article.id, 'author': article.author}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving article: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/get-journal-stats', methods=['GET'])
def get_journal_stats() -> Response:
    """
    Route to get the total journal length (number of articles) and duration.

    Returns:
        JSON response with the number of articles or error message.
    """
    try:
        app.logger.info(f"Retrieving total journal length...")

        length = JournalModel.get_journal_length()
        duration = JournalModel.get_journal_duration()
        return make_response(jsonify({'status': 'success', 'length': length, 'duration': duration}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving stats: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

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
        article_model.clear_catalog()
        app.logger.info('Catalog cleared.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to clear catalog: %s", str(e))
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
        article_model.delete_article(article_id)
        app.logger.info('Article deleted.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to delete article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/project/remove-article-from-journal_id/<int:article_id>', methods=['POST'])
def delete_article_by_id_from_journal(article_id: int) -> Response:
    """
    Route to clear a specific article based on the ID.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info(f'Deleting article with ID {article_id}')
        JournalModel.remove_article_by_article_id(article_id)
        app.logger.info('Article deleted.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to delete article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/project/remove-article-from-journal_num/<int:article_num>', methods=['POST'])
def delete_article_by_num_from_journal(article_num: int) -> Response:
    """
    Route to clear a specific article based on the ID.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info(f'Deleting article with number {article_num}')
        JournalModel.remove_article_by_article_number(article_num)
        app.logger.info('Article deleted.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to delete article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
####################################################
#
# Journal routes
#
####################################################
    
@app.route('/project/swap-articles-in-journal', methods=['POST'])
def swap_articles(article_id1: int, article_id2: int) -> Response:
    """
    Route to swap two articles in a journal.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info(f'Swapping article with ID {article_id1} with another article with ID {article_id2}')
        JournalModel.swap_articles_in_journal(article_id1, article_id2)
        app.logger.info('Articles swapped.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to swap articles: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/project/read-current-article', methods=['POST'])
def read_current_article() -> Response:
    """
    Route to read the current article

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue.
    """
    try:
        app.logger.info(f'Reading current article...')
        JournalModel.read_current_article()
        app.logger.info('Article read.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to read article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/project/read-entire-journal', methods=['POST'])
def read_entire_journal() -> Response:
    """
    Route to read entire journal.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info(f'Reading all articles in journal...')
        JournalModel.read_entire_journal()
        app.logger.info('Article read.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to read article: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5003)