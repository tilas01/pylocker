def main():
    import os
    import sys
    from base64 import urlsafe_b64encode, urlsafe_b64decode
    from time import sleep
    from hashlib import pbkdf2_hmac
    from getpass import getpass
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    def leave():
        print("Quitting...")
        sleep(1)
        sys.exit()

    def clear():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def scan_dir():
        try:
            for x in os.listdir():
                if os.path.isdir(x):
                    raise StopIteration
        except StopIteration:
            print("Folder contains one or more subdirectories.")
            print("Recursive encryption/decryption is not supported.")
            while True:
                a = input("These directories will be ignored would you like to continue [y/n]? ")
                if a == "y":
                    break
                elif a == "n":
                    leave()
                else:
                    print("Invalid Input.")

    def encrypt(dir):
        try:
            if os.path.isfile(dir):
                oldname = os.path.basename(dir)
                newname = f.encrypt(oldname.encode())
                os.chdir(os.path.dirname(dir))
                os.rename(oldname, newname)
                with open(newname, "rb") as file:
                    data = file.read()
                data = f.encrypt(data)

                with open(newname, "wb") as file:
                    file.write(data)
                print(f"Encrypted {oldname}")
                print("Encryption complete!\n")
            elif os.path.isdir(dir):
                arr = os.listdir(dir)
                if not arr:
                    print(f'"{dir}" is empty.\n')
                else:
                    os.chdir(dir)
                    scan_dir()
                    for x in range(len(arr)):
                        currentfile = arr[x]
                        if os.path.isfile(currentfile):
                            newname = f.encrypt(currentfile.encode())
                            os.rename(currentfile, newname)
                            with open(newname, "rb") as file:
                                data = file.read()
                            data = f.encrypt(data)

                            with open(newname, "wb") as file:
                                file.write(data)
                            print(f"Encrypted {currentfile}")
                    print("Encryption complete!\n")
            else:
                print("Invalid encryption request.\n")
        except OSError:
            print("File name(s) too long.\n")
        except SystemExit:
            sys.exit()
        except:
            print("An unknown error occured during encryption.\n")

    def decrypt(dir):
        try:
            if os.path.isfile(dir):
                oldname = os.path.basename(dir)
                newname = f.decrypt(oldname.encode())
                os.chdir(os.path.dirname(dir))
                os.rename(oldname, newname)
                with open(newname, "rb") as file:
                    data = file.read()
                data = f.decrypt(data)

                with open(newname, "wb") as file:
                    file.write(data)
                print("Decrypted " + newname.decode())
                print("Decryption complete!\n")
            elif os.path.isdir(dir):
                arr = os.listdir(dir)
                if not arr:
                    print(f'"{dir}" is empty.\n')
                else:
                    os.chdir(dir)
                    scan_dir()
                    for x in range(len(arr)):
                        currentfile = arr[x]
                        if os.path.isfile(currentfile):
                            newname = f.decrypt(currentfile.encode())
                            os.rename(currentfile, newname)
                            with open(newname, "rb") as file:
                                data = file.read()
                            data = f.decrypt(data)

                            with open(newname, "wb") as file:
                                file.write(data)
                            print(f"Decrypted " + newname.decode())
                    print("Decryption complete!\n")
            else:
                print("Invalid decryption request.\n")
        except InvalidToken:
            print("File(s) are not encrypted.\n")
        except OSError:
            print("An unknown OS error occured.\n")
        except SystemExit:
            sys.exit()
        except:
            print("An unknown error occured during decryption.\n")

    if not os.path.isdir("config"):
        print("Creating config...")
        try:
            os.mkdir("config")
        except OSError:
            print('Could not create "config"')
            leave()

    if not os.path.isfile("config/salt"):
        salt = os.urandom(32)
        b64salt = urlsafe_b64encode(salt).decode()
        print("Writing salt...\n")
        try:
            with open("config/salt", "w") as file:
                file.write(b64salt)
        except OSError:
            print('Could not open "salt"')
            leave()

    try:
        with open("config/salt", "r") as file:
            salt = file.read()
            salt = urlsafe_b64decode(salt)
    except OSError:
        print('Could not open "salt"')
        leave()

    if not os.path.isfile("config/hash"):
        print("Please enter the password you would like to encrypt/decrypt your files with.")
        print("Keep this password safe, if it is lost all your data WILL be unrecoverable if in an encrypted state.\n")
        while True:
            firstpass = getpass("Master Password: ")
            secondpass = getpass("Confirm Master Password: ")
            if firstpass != secondpass:
                print("Passwords do not match.")
            else:
                del secondpass
                firstpass = pbkdf2_hmac('sha256', firstpass.encode('utf-8'), salt, 100000)
                try:
                    with open("config/hash", "wb") as file:
                        file.write(firstpass)
                except OSError:
                    print('Could not open "hash"')
                    leave()
                print()
                break

    try:
        with open("config/hash", "rb") as file:
            checkhash = file.read()
    except OSError:
        print('Could not open "hash"')
        leave()

    if 'b64salt' in locals():
        print('Your salt is "' + b64salt + '". Keep it safe.')
        print("If you lose your salt all data encrypted with it WILL be unrecoverable.\n")
    print("Discalimers:")
    print("Do not rename any encrypted files as it may lead to unexpected behaviour.")
    print("Subdirectory/recursive encryption is not supported.")
    print("Use this program at your own risk. I am not responsbile for your data.")
    print("Always keep a backup.\n")
    while True:
        key = getpass("Master Password: ")
        keyhash = pbkdf2_hmac('sha256', key.encode('utf-8'), salt, 100000)
        if keyhash == checkhash:
            print("Correct Password!\n")
            break
        else:
            print("Incorrect Password.")
    key = key.encode()
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
    )
    key = urlsafe_b64encode(kdf.derive(key))
    f = Fernet(key)

    while True:
        a = input("Choose a command: [(e)ncrypt / (d)ecrypt / (c)lear / (q)uit]: ")

        if a == "e":
            print("\nPlease enter the full path of the file/folder you want to encrypt.")
            print("e.g. /path/to/file/or/folder")
            filepath = input("Response: ")
            encrypt(filepath)

        elif a == "d":
            print("\nPlease enter the full path of the file/folder you want to encrypt.")
            print("e.g. /path/to/file/or/folder")
            filepath = input("Response: ")
            decrypt(filepath)

        elif a == "c":
            clear()

        elif a == "q":
            leave()

        else:
            print("Invalid Input.")

if __name__ == '__main__':
    main()