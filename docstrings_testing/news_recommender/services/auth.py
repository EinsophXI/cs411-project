import bcrypt
from user import User

# Hash and store password function
def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return salt, hashed_password

# Store new user in the database
def store_user(session, username: str, password: str):
    salt, hashed_password = hash_password(password)
    new_user = User(username=username, salt=salt.decode('utf-8'), hashed_password=hashed_password.decode('utf-8'))
    session.add(new_user)
    session.commit()

# Verify user credentials
def verify_user(session, username: str, password: str):
    stored_user = session.query(User).filter_by(username=username).first()
    if stored_user:
        stored_hash = stored_user.hashed_password
        stored_salt = stored_user.salt
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return False