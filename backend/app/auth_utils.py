import hashlib
import base64
import bcrypt
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
    
def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Pre-hash to handle any length password
    sha_hash = hashlib.sha256(password.encode("utf-8")).digest()
    b64_hash = base64.b64encode(sha_hash).decode('utf-8')
    
    # Hash with bcrypt 
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b64_hash.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    if not isinstance(password, str) or not isinstance(hashed, str):
        return False
    
    if not password or not hashed:
        return False
    
    try:
        sha_hash = hashlib.sha256(password.encode("utf-8")).digest()
        b64_hash = base64.b64encode(sha_hash).decode('utf-8')
        
        # Verify with bcrypt
        return bcrypt.checkpw(b64_hash.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"Verification error: {e}")
        return False


