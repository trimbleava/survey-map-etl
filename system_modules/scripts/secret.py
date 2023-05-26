#
# Generate a ten-character alphanumeric password with at least one lowercase character, 
# at least one uppercase character, and at least three digits:
# https://docs.python.org/3/library/secrets.html
#
import sys, os
import string
import secrets

def do_secret():
    
    alphabet = string.ascii_letters + string.digits
    password=""

    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3):
            break
    return password
    
        
        
# this script is called from settings.py    
if __name__ == "__main__":
    # enter a secret file name to add a secret to the file.
    # where rest of database secrets are manually entered to this file
    # example: postgres_standalone_docker.sh
    # however, this case is not being used anymore, due to the direct call
    # of do_secret()
    if len (sys.argv) != 2:
        print("Expected a secert file containing database connection secrets")
        sys.exit(0)

    secret_file = sys.argv[1]
    with open (secret_file, 'a') as fp:
        SECRET_KEY = do_secret()
        fp.write(f'{SECRET_KEY}\n')
    
