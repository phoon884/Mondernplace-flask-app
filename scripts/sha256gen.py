from passlib.hash import pbkdf2_sha256
password = input("to hash:")
print(pbkdf2_sha256.hash(password))