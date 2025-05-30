import os
import json
from cryptography.fernet import Fernet, InvalidToken

VAULT_FILE = "credentials.vault"
ENV_VAULT_KEY = "CREDENTIAL_VAULT_KEY"

def get_key():
    """Retrieves the Fernet key from environment variables."""
    key_str = os.environ.get(ENV_VAULT_KEY)
    if not key_str:
        raise ValueError(f"{ENV_VAULT_KEY} environment variable not set.")
    return key_str.encode() # Fernet key must be bytes

def initialize_vault_file_if_not_exists():
    """
    Initializes the vault file with an empty encrypted JSON object if it doesn't exist.
    This prevents errors when trying to load an empty or non-existent file.
    """
    if not os.path.exists(VAULT_FILE):
        key = get_key()
        f = Fernet(key)
        empty_data = {}
        encrypted_data = f.encrypt(json.dumps(empty_data).encode())
        with open(VAULT_FILE, 'wb') as vf:
            vf.write(encrypted_data)
        print(f"Initialized empty vault file: {VAULT_FILE}")


def load_vault():
    """Loads and decrypts the vault data from the file."""
    key = get_key()
    f = Fernet(key)

    initialize_vault_file_if_not_exists() # Ensure file exists and is valid

    with open(VAULT_FILE, 'rb') as vf:
        encrypted_data = vf.read()

    try:
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except InvalidToken:
        raise ValueError("Invalid token or key. Could not decrypt vault file.")
    except json.JSONDecodeError:
        raise ValueError("Vault file is corrupted or not valid JSON after decryption.")


def save_vault(data):
    """Encrypts and saves the vault data to the file."""
    key = get_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    with open(VAULT_FILE, 'wb') as vf:
        vf.write(encrypted_data)

def store_credential(user_id: str, service_name: str, username: str, password: str):
    """Stores (adds or updates) a credential in the vault."""
    key = get_key() # For encrypting the password itself
    f = Fernet(key)

    data = load_vault()

    encrypted_password = f.encrypt(password.encode()).decode() # Store encrypted pass as string

    user_credentials = data.get(user_id, [])

    # Check if service_name already exists for this user
    service_found = False
    for cred in user_credentials:
        if cred["service_name"] == service_name:
            cred["username"] = username
            cred["encrypted_password"] = encrypted_password
            service_found = True
            break

    if not service_found:
        user_credentials.append({
            "service_name": service_name,
            "username": username,
            "encrypted_password": encrypted_password
        })

    data[user_id] = user_credentials
    save_vault(data)
    print(f"Credential for '{service_name}' for user '{user_id}' stored successfully.")

def get_credential(user_id: str, service_name: str):
    """Retrieves and decrypts a specific credential from the vault."""
    key = get_key() # For decrypting the password
    f = Fernet(key)

    data = load_vault()

    user_credentials = data.get(user_id, [])
    for cred in user_credentials:
        if cred["service_name"] == service_name:
            try:
                decrypted_password = f.decrypt(cred["encrypted_password"].encode()).decode()
                return cred["username"], decrypted_password
            except InvalidToken:
                print(f"Error: Could not decrypt password for service '{service_name}' for user '{user_id}'. Key might have changed or data corrupted.")
                return cred["username"], None # Or raise an error

    return None, None
