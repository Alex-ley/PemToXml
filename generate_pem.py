from Crypto.PublicKey import RSA
import os

# path_file = os.path.abspath(f"./keys/private_key")
# base, ext = os.path.splitext(path_file)

key = RSA.generate(4096)
with open('private_key', 'wb') as content_file:
    os.chmod('private_key.pem', 0o0600)
    content_file.write(key.exportKey('PEM'))

pubkey = key.publickey()
with open('public_key', 'wb') as content_file:
    # openSSH format is only valid for the public key
    # it is often used on linux servers and saved in a file called
    # ~/.ssh/authorized_keys (within the user account logging into)
    # this then allows the holder of the private key to "SSH into" the machine:
    # content_file.write(pubkey.exportKey('OpenSSH'))

    # But for our case we will just use .pem:
    content_file.write(pubkey.exportKey('PEM'))
