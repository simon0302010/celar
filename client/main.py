import questionary
import requests
import sys

API_URL = "http://127.0.0.1:8000"

def register():
    print("=== Register ===")
    username = input("Username: ")
    password = input("Password: ")
    age = input("Age: ")
    if not age.isnumeric():
        print("Please input a number.")
        sys.exit(1)
    interests = input("Interests (comma-separated): ").split(",")
    for interest in interests:
        interest.strip()
    r = requests.post(f"{API_URL}/register", json={
        "username": username,
        "password": password,
        "age": age,
        "interests": [i.strip() for i in interests]
    })
    print(r.json())

def login():
    print("=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    r = requests.post(f"{API_URL}/login", json={
        "username": username,
        "password": password
    })
    print(r.json())
    
def read_me():
    print("=== Read my profile ===")
    token = input("Token: ")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(f"{API_URL}/profile", headers=headers)
    print(r.json())
    
def read_other():
    print("=== Read other profile ===")
    username = input("Username: ")
    token = input("Token: ")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(f"{API_URL}/profile/{username}", headers=headers)
    print(r.json())
    
def get_users():
    print("=== Get users ===")
    limit = input("Limit: ")
    token = input("Token: ")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(f"{API_URL}/users?limit={limit}", headers=headers)
    print(r.json())

if __name__ == "__main__":
    answer = questionary.select(
    "What do you want to do?",
    choices=[
        "Register",
        "Login",
        "Read own profile",
        "Read other profile",
        "Get all users"
    ]).ask()
    
    if answer == "Register":
        register()
    elif answer == "Login":
        login()
    elif answer == "Read own profile":
        read_me()
    elif answer == "Read other profile":
        read_other()
    elif answer == "Get all users":
        get_users()
