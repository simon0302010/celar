# Celar Client

Terminal user interface (TUI) client for Celar, built with [Textual](https://textual.textualize.io/).

## Requirements

- Python 3.9+
- Terminal with image support (recommended: iTerm2, Kitty, or modern terminals)
- Internet connection when connecting to a remote server

## Installation

### Install from PyPI
```bash
pip install celar
```

## Usage

### Starting the Application

After installation, run:
```bash
celar
```

You can also run:
```bash
python -m celar
```

### Setup

1. **Set API URL**: On launch, you'll be prompted to set the server URL
   - Default: `http://127.0.0.1:8000`
   - Change this to match your Celar server location

2. **Register or Login**: 
   - **Register**: Create a new account with username, password, and preferences
   - **Login**: Use existing credentials

### Navigation

- **Arrow Keys**: Navigate between UI elements
- **Tab/Shift+Tab**: Move between focusable elements
- **Enter/Space**: Activate buttons
- **Escape**: Go back or exit
- **D**: Toggle between dark and light themes

### Features

- View posts from all users
- Give coins to posts by clicking the coin button
- See how many coins your posts have received
- See how many coins other posts have received
- Create posts

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.