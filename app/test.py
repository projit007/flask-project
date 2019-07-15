from werkzeug.security import generate_password_hash, check_password_hash


password = "test"
hashed_password = generate_password_hash(password)
print(hashed_password)
l_password = hashed_password
verify_password = check_password_hash(hashed_password, l_password)
print(verify_password)