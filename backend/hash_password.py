import bcrypt

password = "admin123"  # Your desired password
password_bytes = password.encode('utf-8')

# Generate salt and hash
salt = bcrypt.gensalt(rounds=12)
hashed_password = bcrypt.hashpw(password_bytes, salt)

print("Password:", password)
print("Hashed password:", hashed_password.decode('utf-8'))

print("\n📋 Copy this to MongoDB:")
print(f'"hashed_password": "{hashed_password.decode("utf-8")}"')