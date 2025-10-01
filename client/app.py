from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static, Input
from textual.containers import Vertical
from textual.screen import Screen
import requests

CELAR_TOKEN = None
API_URL = "http://127.0.0.1:8000"

class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Welcome to Celar.\nPress Register or Login to continue.", id="welcome"),
            Button("Login", id="login", variant="primary", classes="main-menu-button"),
            Button("Register", id="register", variant="success", classes="main-menu-button"),
            Button("Exit", id="exit", variant="error", classes="main-menu-button")
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            self.app.push_screen(LoginMenu())
        elif event.button.id == "register":
            self.app.push_screen(RegisterMenu())
        elif event.button.id == "exit":
            self.app.exit()
    
class LoginMenu(Screen):
    def __init__(self):
        super().__init__()
        self.values = {"username": "", "password": ""}
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Login to Celar", classes="login-menu"),
            Input(placeholder="Username", classes="login-menu", id="username"),
            Input(placeholder="Password", classes="login-menu", id="password", password=True),
            Button("Login", id="submit", variant="success", classes="login-menu"),
            Button("Back", id="back", variant="error", classes="login-menu")
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.push_screen(MainMenu())
        if event.button.id == "submit":
            username = self.values["username"]
            password = self.values["password"]
            if username and password:
                self.login(username, password)
            else:
                self.notify("Username and password can't be empty.", severity="error")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.values[str(event.input.id) or ""] = event.input.value
        
    def login(self, username, password):
        global CELAR_TOKEN
        r = requests.post(f"{API_URL}/login", json={
            "username": username,
            "password": password
        })
        if r.status_code == 200:
            CELAR_TOKEN = r.json()["access_token"]
            self.notify("Login successful.")
        elif r.status_code == 401:
            self.notify("Username or password incorrect.", severity="error")
        else:
            self.notify("An error occurred.", severity="error")
            
class RegisterMenu(Screen):
    def __init__(self):
        super().__init__()
        self.values = {"username": "", "password": "", "password2": ""}
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Create a new account", classes="login-menu"),
            Input(placeholder="Username", classes="login-menu", id="username"),
            Input(placeholder="Password", classes="login-menu", id="password", password=True),
            Input(placeholder="Confirm password", classes="login-menu", id="password2", password=True),
            Button("Register", id="submit", variant="success", classes="login-menu"),
            Button("Back", id="back", variant="error", classes="login-menu")
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.push_screen(MainMenu())
        if event.button.id == "submit":
            username = self.values["username"]
            password = self.values["password"]
            password2 = self.values["password2"]
            if password != password2:
                self.notify("Passwords don't match.", severity="warning")
                return
            if username and password:
                self.register(username, password)
            else:
                self.notify("Username and password can't be empty.", severity="error")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.values[str(event.input.id) or ""] = event.input.value
        
    def register(self, username, password):
        global CELAR_TOKEN
        r = requests.post(f"{API_URL}/register", json={
            "username": username,
            "password": password,
            "software": []
        })
        if r.status_code == 200:
            self.notify("Register successful.")
            self.app.push_screen(LoginMenu())
        elif r.status_code == 400:
            self.notify("User already exists.", severity="error")
        else:
            self.notify("An error occurred.", severity="error")
        
class CelarApp(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def on_mount(self) -> None:
        """Called when the app starts"""
        self.push_screen(MainMenu())
        
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = CelarApp()
    app.run()