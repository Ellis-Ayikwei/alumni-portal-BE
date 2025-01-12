import sys

from colorama import Fore

def create_super_admin():
    from models.user import User, UserRole
    """
    Creates a super admin user with input from the command line.

    This function will prompt the user for email, username, first name,
    last name, and password. It will create a User object with the provided
    information, save it to the database, and print a success message with
    the details of the created user.

    Usage: Execute this script and follow the prompts to enter user details.
    
    :return: None
    """
    email = input("Enter email: ")
    username = input("Enter username: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")

    password = input("Enter password: ")

    user = User(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.SUPER_ADMIN,
    )

    user.save()
    print(f"{Fore.GREEN}Super admin user created successfully,\n name: {user.full_name}, \n email: {user.email}, \n username: {user.username}\n password: {password}{Fore.RESET}")
    print(f"{Fore.GREEN}You can now log in with your username and password.{Fore.RESET}")

if __name__ == "__main__":
    create_super_admin()