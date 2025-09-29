import questionary
import requests
import sys
import os

API_URL = "http://127.0.0.1:8000"
ACCESS_TOKEN = None

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
    }).json()
    print(r)

def login():
    global ACCESS_TOKEN
    print("=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    r = requests.post(f"{API_URL}/login", json={
        "username": username,
        "password": password
    }).json()
    os.environ["CELAR_ACCESS_TOKEN"] = r["access_token"]
    ACCESS_TOKEN = r["access_token"]
    print(r)
    
def read_me():
    print("=== Read my profile ===")
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    r = requests.get(f"{API_URL}/profile", headers=headers).json()
    print(r)
    
def read_other():
    print("=== Read other profile ===")
    username = input("Username: ")
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    r = requests.get(f"{API_URL}/profile/{username}", headers=headers).json()
    print(r)
    
def get_users():
    print("=== Get users ===")
    limit = input("Limit: ")
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    r = requests.get(f"{API_URL}/users?limit={limit}", headers=headers).json()
    print(r)

if __name__ == "__main__":
    while True:        
        answer = questionary.select(
        "What do you want to do?",
        choices=[
            "Register",
            "Login", 
            "Read own profile",
            "Read other profile",
            "Get all users",
            "Exit"
        ]).ask()
        
        if answer == "Exit":
            break
        elif answer == "Register":
            register()
        elif answer == "Login":
            login()
        elif answer == "Read own profile":
            if not ACCESS_TOKEN:
                print("Please register or login first")
                sys.exit(1)
            read_me()
        elif answer == "Read other profile":
            if not ACCESS_TOKEN:
                print("Please register or login first")
                sys.exit(1)
            read_other()
        elif answer == "Get all users":
            if not ACCESS_TOKEN:
                print("Please register or login first")
                sys.exit(1)
            get_users()