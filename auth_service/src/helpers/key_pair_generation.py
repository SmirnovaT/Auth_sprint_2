from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_private_and_public_keys():
    """Key pair generation (private and public)"""

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("-------------------------------")
    print(f"PRIVATE KEY: {pem_private_key}")
    print("-------------------------------")
    print(f"PUBLIC KEY: {pem_public_key}")
    print("-------------------------------")

    return pem_private_key, pem_public_key


if __name__ == "__main__":
    generate_private_and_public_keys()
