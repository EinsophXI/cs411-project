from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
#from music_collection.utils.sql_utils import check_database_connection, check_table_exists

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

@app.route('/create-account', methods=['POST'])
def create_account() -> Response:
    session = get_session()  # Automatically get a session when the app starts
    
    # Example usage
    store_user(session, 'john_doe', 'secure_password123')  # Store user
    is_verified = verify_user(session, 'john_doe', 'secure_password123')  # Verify user login
    if is_verified:
        print("User verified!")
    else:
        print("Invalid credentials.")
    
    session.close() 

#@app.route('/login', methods=['GET'])
