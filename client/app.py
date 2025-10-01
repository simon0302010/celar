from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Footer, Header, Button, Static, Input, Checkbox
from textual_image.widget import Image
from textual.containers import Vertical, VerticalScroll, VerticalGroup
from textual.screen import Screen
from datetime import datetime, timezone
from PIL import Image as PILImage
from PIL import ImageFilter as PILImageFilter
from io import BytesIO
import requests
import base64

CELAR_TOKEN = None
API_URL = "http://127.0.0.1:8000"

class Post(VerticalGroup):
    def __init__(self, post_id, author: str, content: bytes, created_at: str, **kwargs):
        super().__init__(**kwargs)
        self.add_class("post")
        self.post_id = post_id
        self.author = author
        created_dt = datetime.fromisoformat(created_at)
        self.created_at = created_dt.strftime("%B %d, %Y %H:%M UTC")
        img_data = base64.b64decode(content)
        self.img = PILImage.open(BytesIO(img_data))
        try:
            self.img.seek(0)
        except (AttributeError, EOFError):
            pass
        self.img = self.img.convert("RGB")
        # resize and fill rest with blurred version of image
        self.img.thumbnail((512, 512), PILImage.Resampling.LANCZOS)
        blurred_bg = self.img.copy().resize((512, 512), PILImage.Resampling.LANCZOS).filter(PILImageFilter.GaussianBlur(20))

        new_img = PILImage.new("RGB", (512, 512))
        new_img.paste(blurred_bg, (0, 0))

        x = (512 - self.img.width) // 2
        y = (512 - self.img.height) // 2
        new_img.paste(self.img, (x, y))

        self.img = new_img
    def compose(self) -> ComposeResult:
        yield Static(self.author, classes="feed-text")
        yield Static(self.created_at, classes="feed-text")
        yield Image(self.img)
        
class PostScroll(VerticalScroll):
    def __init__(self, posts: list, **kwargs):
        super().__init__(**kwargs)
        self.post_widgets = []
        for post in posts:
            self.post_widgets.append(
                Post(post["id"], post["author"], post["content"], post["created_at"])
            )
            
    def compose(self) -> ComposeResult:
        for post in self.post_widgets:
            yield post
        
class MultiCheckbox(VerticalScroll):
    def __init__(self, options, **kwargs):
        super().__init__(**kwargs)
        self.options = options
        self.checkboxes = [Checkbox(label=opt, id=opt) for opt in options]

    def compose(self) -> ComposeResult:
        for cb in self.checkboxes:
            yield cb

    def get_selected(self):
        return [cb.label for cb in self.checkboxes if cb.value]

class Feed(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app.title = "Celar Feed"
        headers = {
            "Authorization": f"Bearer {CELAR_TOKEN}"
        }
        self.posts = requests.get(f"{API_URL}/posts", headers=headers).json()
    
    def compose(self) -> ComposeResult:
        yield Header()
        if self.posts:
            yield PostScroll(self.posts)
        else:
            yield Static("No posts found.", classes="feed-text")
        yield Footer()

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
        try:
            r = requests.post(f"{API_URL}/login", json={
                "username": username,
                "password": password
            })
        except:
            self.notify("Couldn't connect to server.", severity="error")
            return
        if r.status_code == 200:
            CELAR_TOKEN = r.json()["access_token"]
            self.notify("Login successful.")
            self.app.push_screen(Feed())
        elif r.status_code == 401:
            self.notify("Username or password incorrect.", severity="error")
        else:
            self.notify("An error occurred.", severity="error")
            
class RegisterMenu(Screen):
    def __init__(self):
        super().__init__()
        self.values = {"username": "", "password": "", "password2": ""}
        self.operating_systems = ["Linux", "Windows", "macOS", "Android", "iOS", "OpenBSD", "FreeBSD", "ChromeOS"]
        self.os_widget = MultiCheckbox(self.operating_systems, classes="login-menu")
        self.programming_languages = ["Python", "JavaScript", "TypeScript", "Java", "C", "CPP", "CSharp", "Go", "Rust", "Swift", "Kotlin", "PHP", "Scala", "Ruby", "Perl", "Haskell", "Dart", "Elixir", "Fortran", "Assembly"]
        self.lang_widget = MultiCheckbox(self.programming_languages, classes="login-menu")
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Create a new account", classes="login-menu"),
            Input(placeholder="Username", classes="login-menu", id="username"),
            Input(placeholder="Password", classes="login-menu", id="password", password=True),
            Input(placeholder="Confirm password", classes="login-menu", id="password2", password=True),
            Static("Select what operating system(s) you use:", classes="login-menu"),
            self.os_widget,
            Static("Select the programming language(s) you use:", classes="login-menu"),
            self.lang_widget,
            Button("Register", id="submit", variant="success", classes="login-menu"),
            Button("Back", id="back", variant="error", classes="login-menu")
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.push_screen(MainMenu())
        if event.button.id == "submit":
            software = self.os_widget.get_selected() + self.lang_widget.get_selected()
            username = self.values["username"]
            password = self.values["password"]
            password2 = self.values["password2"]
            if password != password2:
                self.notify("Passwords don't match.", severity="warning")
                return
            if username and password:
                self.register(username, password, software)
            else:
                self.notify("Username and password can't be empty.", severity="error")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.values[str(event.input.id) or ""] = event.input.value
        
    def register(self, username, password, software):
        global CELAR_TOKEN
        try:
            r = requests.post(f"{API_URL}/register", json={
                "username": username,
                "password": password,
                "software": [str(item) for item in software]
            })
        except:
            self.app.notify("Couldn't connect to server.", severity="error")
            return
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
        self.title = "Celar"
        self.push_screen(MainMenu())
        
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = CelarApp()
    app.run()