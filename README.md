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

This repo comes with a CLI tool called `mmake` (manim-make) that you can use to
build and manage your Manim projects.

Install `mmake` as an editable package:

```bash
pip install -e .
mmake --help
```

Set up a new project folder:

```bash
mmake new my-project
```

Build all media for a specific project:

```bash
mmake build project-name --format gif  # default
mmake build project-name --format png
mmake build project-name --format mp4
```
