import requests

API_URL = "http://127.0.0.1:8000"

def register():
    username = input("Username: ")
    password = input("Password: ")
    age = int(input("Age: "))
    interests = input("Interests (comma-separated): ").split(",")
    r = requests.post(f"{API_URL}/register", json={
        "username": username,
        "password": password,
        "age": age,
        "interests": [i.strip() for i in interests]
    })
    print(r.json())

if __name__ == "__main__":
    register()