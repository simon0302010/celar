from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static, Input
from textual.containers import Vertical
from textual.screen import Screen
import sys

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
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Login to Celar", classes="login-menu"),
            Input(placeholder="Username", classes="login-menu"),
            Input(placeholder="Password", classes="login-menu"),
            Button("Login", id="submit", variant="success", classes="login-menu"),
            Button("Back", id="back", variant="error", classes="login-menu")
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.push_screen(MainMenu())
            
class RegisterMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Create a new account", classes="login-menu"),
            Input(placeholder="Username", classes="login-menu"),
            Input(placeholder="Password", classes="login-menu"),
            Button("Register", id="submit", variant="success", classes="login-menu"),
            Button("Back", id="back", variant="error", classes="login-menu")
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.push_screen(MainMenu())
        
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