from hashlib import sha3_512

class Security:

    @staticmethod
    def encode_password(password: str) -> bytes:
        password: bytes = password.encode()
        password = sha3_512(password).hexdigest()
        return password
    


