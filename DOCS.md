# PlayRex - Project Documentation

## Project Structure

```
PLAYREX_BOT/
├── README.md              # Project overview
├── CONTRIBUTING.md        # How to contribute
├── CODE_OF_CONDUCT.md     # Community guidelines
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── config.example.py     # Example configuration
├── playrex.py            # Main application
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.yml
    │   └── feature_request.yml
    └── PULL_REQUEST_TEMPLATE.md
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/umtcnkrky/PLAYREX_BOT.git
   cd PLAYREX_BOT
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   cp config.example.py config.py
   # Edit config.py with your settings
   ```

5. **Run the application**
   ```bash
   python playrex.py
   ```

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code style
flake8 .

# Format code
black .
```

### Code Style

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.

### Testing

Write tests for new features and run them before submitting a pull request.

```bash
pytest
```

## Documentation

Full documentation is available in the [docs/](docs/) directory.

## Support

- **Issues**: Report bugs or suggest features via [GitHub Issues](https://github.com/umtcnkrky/PLAYREX_BOT/issues)
- **Discussions**: Ask questions or share ideas via [GitHub Discussions](https://github.com/umtcnkrky/PLAYREX_BOT/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Core moment detection algorithm
- [ ] Video processing pipeline
- [ ] Subtitle generation
- [ ] YouTube API integration
- [ ] Web dashboard
- [ ] Mobile app

## Related Projects

- [OpenCV](https://opencv.org/) - Video processing
- [FFmpeg](https://ffmpeg.org/) - Video manipulation
- [YouTube API](https://developers.google.com/youtube) - Video upload

---

For more information, visit the [project repository](https://github.com/umtcnkrky/PLAYREX_BOT).