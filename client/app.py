from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static
from textual.containers import Vertical

class CelarApp(App):
    """A CLI social media app"""
    
    CSS_PATH = "app.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Welcome to Celar.\nPress Register or Login to continue.", id="welcome"),
            Button("Login", id="login", variant="primary"),
            Button("Register", id="register", variant="success")
        )
        yield Footer()
        
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
        
if __name__ == "__main__":
    app = CelarApp()
    app.run()