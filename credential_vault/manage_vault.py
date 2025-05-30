import argparse
import os
from cryptography.fernet import Fernet
# Add vault.py to path if running manage_vault.py directly for now
import sys
sys.path.append(os.path.dirname(__file__)) # Allows importing vault when run as script
import vault

def generate_key_cmd():
    """Generates a new Fernet key."""
    key = Fernet.generate_key()
    print("Generated Fernet Key (store this in your .env file as CREDENTIAL_VAULT_KEY):")
    print(key.decode())

def add_credential_cmd(args):
    """Handles adding a new credential."""
    if not os.environ.get(vault.ENV_VAULT_KEY):
        print(f"Error: The {vault.ENV_VAULT_KEY} environment variable is not set.")
        print("Please generate a key and set it in your .env file first.")
        return

    try:
        vault.store_credential(args.user_id, args.service_name, args.username, args.password)
    except Exception as e:
        print(f"Error storing credential: {e}")


def get_credential_cmd(args):
    """Handles retrieving a credential (for testing/verification)."""
    if not os.environ.get(vault.ENV_VAULT_KEY):
        print(f"Error: The {vault.ENV_VAULT_KEY} environment variable is not set.")
        print("Please generate a key and set it in your .env file first.")
        return

    try:
        username, password = vault.get_credential(args.user_id, args.service_name)
        if username and password:
            print(f"Service: {args.service_name}")
            print(f"Username: {username}")
            print(f"Password: {password}")
        elif username:
            print(f"Service: {args.service_name}")
            print(f"Username: {username}")
            print(f"Password: (Could not be decrypted or not set)")
        else:
            print(f"No credential found for service '{args.service_name}' for user '{args.user_id}'.")
    except Exception as e:
        print(f"Error retrieving credential: {e}")

def main():
    parser = argparse.ArgumentParser(description="Credential Vault Management Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate key command
    parser_genkey = subparsers.add_parser("generate-key", help="Generate a new encryption key.")
    parser_genkey.set_defaults(func=generate_key_cmd)

    # Add credential command
    parser_add = subparsers.add_parser("add-credential", help="Add or update a credential.")
    parser_add.add_argument("user_id", help="User ID")
    parser_add.add_argument("service_name", help="Service Name (e.g., github_com, specific_website)")
    parser_add.add_argument("username", help="Username for the service")
    parser_add.add_argument("password", help="Password for the service")
    parser_add.set_defaults(func=add_credential_cmd)

    # Get credential command
    parser_get = subparsers.add_parser("get-credential", help="Retrieve a credential (for testing).")
    parser_get.add_argument("user_id", help="User ID")
    parser_get.add_argument("service_name", help="Service Name")
    parser_get.set_defaults(func=get_credential_cmd)

    # Initialize vault file command (useful for first run with a new key)
    parser_init = subparsers.add_parser("init-vault", help="Initialize an empty vault file if it doesn't exist (requires CREDENTIAL_VAULT_KEY to be set).")
    parser_init.set_defaults(func=lambda args: vault.initialize_vault_file_if_not_exists() and print("Vault initialized (if it wasn't already)."))


    args = parser.parse_args()
    if hasattr(args, 'func'):
        if args.command in ["add-credential", "get-credential", "init-vault"]:
            args.func(args)
        else: # generate-key
            args.func()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
