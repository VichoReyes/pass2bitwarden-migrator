import csv
import os
import sys
import subprocess
import re
from typing import List, Iterable

store_location = os.path.expanduser("~/.password-store")


field_names = ("folder,favorite,type,name,notes,fields,login_uri,"
               "login_username,login_password,login_totp").split(',')


class BitWardenElem:
    def __init__(self):
        for f in field_names:
            setattr(self, f, "")


def create_elem(password_name: str, contents: List[str]) -> BitWardenElem:
    """
    Create a BitWardenElem, which will become one row in the csv.

    password_name is the clean path to the password file,
    like "Email/donenfield.com".

    contents is a list of the lines of the decrypted file, not
    containing the newline characters.
    """
    e = BitWardenElem()
    e.name = password_name
    # look for interesting fields
    for line in contents[1:]:
        if len(line.split(':')) == 2:
            field_stuff(line, e)
        else:
            e.notes += f"{line}"

    find_uri_or_folder(password_name, e)

    e.type = e.type or "note"

    if e.type == "login":
        e.login_password = contents[0]
    elif e.type == "note":
        if contents[0] not in e.notes:
            e.notes = contents[0] + "\n" + e.notes

    e.fields = e.fields.strip()
    e.notes = e.notes.strip()
    return e


uri_ish = re.compile(r"\.[a-z]{2,3}$")


def find_uri_or_folder(password_name: str, elem: BitWardenElem):
    path_parts = password_name.split('/')
    for part in path_parts:
        if uri_ish.search(part):
            elem.type = "login"
            elem.login_uri = part
            break

    folders = path_parts[:-1]
    if elem.login_uri in folders:
        folders.remove(elem.login_uri)

    if not elem.folder and folders:
        elem.folder = '_'.join(folders)


def field_stuff(line: str, elem: BitWardenElem):
    name, value = line.split(":")
    value = value.strip()
    if name.lower() in ["username", "user"]:
        elem.type = "login"
        elem.login_username = value
    else:
        elem.fields += f"{name}: {value}\n"


def main():
    all_passwords = get_password_names()
    writer = csv.DictWriter(sys.stdout, field_names)
    writer.writeheader()
    for password_name in all_passwords:
        contents = get_contents(password_name)
        elem = create_elem(password_name, contents)
        writer.writerow(vars(elem))


def get_contents(password_name: str) -> List[str]:
    command = ["pass", "show", password_name]
    completed = subprocess.run(command, capture_output=True)
    completed.check_returncode()
    decoded = completed.stdout.decode()
    return decoded.splitlines()


def get_password_names() -> Iterable[str]:
    command = ["find", store_location]
    command += "-name .git -prune -o -type f -name *.gpg -print".split()
    completed = subprocess.run(command, capture_output=True)
    completed.check_returncode()
    full_paths = completed.stdout.decode().splitlines()
    return map(remove_location_and_extension, full_paths)


def remove_location_and_extension(text: str) -> str:
    postfix = ".gpg"
    if store_location[-1] == '/':
        prefix = store_location
    else:
        prefix = store_location + '/'

    assert text.startswith(prefix), f"{text} should start with {prefix}"
    text = text[len(prefix):]
    assert text.endswith(postfix), f"{text} should end with {postfix}"
    return text[:-len(postfix)]


if __name__ == "__main__":
    main()
