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
    r = requests.get(f"{API_URL}/me", headers=headers)
    print(r.json())

if __name__ == "__main__":
    answer = int(input("Press 1 to register, 2 to login, 3 to read profile: "))
    if answer == 1:
        register()
    elif answer == 2:
        login()
    elif answer == 3:
        read_me()
    else:
        print("Invalid option")