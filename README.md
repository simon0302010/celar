# Celar

A modern social media platform designed for developers and tech enthusiasts. Share images, connect with fellow programmers, and showcase your favorite technologies through a beautiful terminal user interface.

![Hackatime](https://hackatime-badge.hackclub.com/U08HC7N4JJW/celar)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

## Features

- **Beautiful Terminal UI**: Modern TUI built with [Textual](https://textual.textualize.io/)
- **Image Sharing**: Upload and view images directly in your terminal
- **Coins**: Likes are represented as coins
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Self-Hosted**: Run your own Celar server
- **REST API**: Complete FastAPI backend with JWT authentication

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Modern terminal (iTerm2, Kitty, or similar recommended for best image support)

### Install Client
```bash
pip install celar
```

### Run Client
```bash
celar
```
> You can also run:
> ```bash
> python -m celar
> ```

### Set API URL

On launch, you'll be prompted to set the server URL
There is a hosted instance at `https://celar.simon.hackclub.app` in demo mode (registration disabled) but you can also run your own server (see server docs).

## Documentation

- **[Server Documentation](server/README.md)**: Complete API reference, authentication, and deployment
- **[Client Documentation](client/README.md)**: Installation, usage, and troubleshooting

## Acknowledgments

- **[Textual](https://textual.textualize.io/)**: Amazing Python TUI framework
- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast web framework

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) files for details.