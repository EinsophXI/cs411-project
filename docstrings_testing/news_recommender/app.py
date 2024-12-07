from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user import Base
from services.auth import store_user, verify_user
from config import DATABASE_URL
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Create a database engine
engine = create_engine(DATABASE_URL)

# Create all tables in the database (if they don't exist)
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

# Helper function to get a session
def get_session():
    return Session()

####################################################
#
# Login and Password Storage
#
####################################################

@app.route('/project/create-account', methods=['POST'])
def create_account() -> Response:
    session = get_session()  # Automatically get a session when the app starts
    
    # Example usage
    store_user(session, 'john_doe', 'secure_password123')  # Store user
    is_verified = verify_user(session, 'john_doe', 'secure_password123')  # Verify user login
    if is_verified:
        response = {
            'message': "User verified!",
            'status': 200
        }
    else:
        response = {
            'message': "Invalid credentials", 
            'status': 500
        }
    
    session.close() 
    return make_response(jsonify(response))

@app.route('/project/login', methods=['POST'])
def login() -> Response:
    # Get username and password from the POST request
    username = request.json.get('username')
    password = request.json.get('password')

    # Initialize session
    session = get_session()

    # Verify user credentials
    if verify_user(session, username, password):
        # If credentials are correct
        response = {
            'message': 'Login successful',
            'username': username,
            'status': 200
        }
    else:
        # If credentials are incorrect
        response = {
            'message': 'Invalid username or password',
            'status': 500
        }
    
    session.close()
    return make_response(jsonify(response))

#app.run(debug=True)

@app.route('/project/update-password', methods=['POST'])
def update_password() -> Response:
    # Get username, current password, and new password from the POST request
    username = request.json.get('username')
    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')

    # Ensure that all required fields are provided
    if not username or not current_password or not new_password:
        return jsonify({'message': 'Username, current password, and new password are required'}), 400

    # Initialize session
    session = get_session()

    # Try to update the password
    if update_password(session, username, current_password, new_password):
        response = {
            'message': 'Password updated successfully',
            'status': 200
        }
    else:
        response = {
            'message': 'Invalid current password or user not found',
            'status': 500
        }

    session.close()
    return make_response(jsonify(response))

####################################################
#
# Health checks
#
####################################################

@app.route('/project/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)


