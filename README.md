# Manim Sandbox

A sandbox for playing around with Manim.

```php
manim-sandbox/
├── README.md             # Description of the repository and usage instructions
├── pyproject.toml        # Python dependencies
├── .gitignore            # Ignore unnecessary files like __pycache__ and outputs
├── src/                  # Main source folder for Manim scripts
│   ├── __init__.py       # (Optional) For treating this as a package
│   ├── common/           # Reusable components (e.g., custom shapes, utilities)
│   ├── styles/           # Custom styles (e.g., fonts, colors)
│   ├── project-name/     # Individual figure scripts for a specific project
│   │   ├── __init__.py   # (Optional) For treating this as a package
│   │   ├── intro.py      # Example script for an "introduction" figure
│   │   ├── example.py    # Another example script
│   │   └── ...
├── output/               # Generated figures and animations
├── assets/               # External assets (e.g., images, fonts)
└── config/               # Configuration files (e.g., Manim settings)
    └── manim.cfg         # Custom Manim configuration file
```

## Usage

Build for a Specific Project:

```bash
# static outputs like images
python cli.py build my-project --target static

# dynamic outputs like videos
python cli.py build my-project --target dynamic
```

Set Up a New Project:

```bash
python cli.py new my-project
```

Clean Outputs:

```bash
python cli.py clean my-project
```
