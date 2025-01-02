import logging
from pathlib import Path
import subprocess
import click
from importlib.metadata import version

# Constants
SRC_DIR = Path("manim_sandbox")
OUTPUT_DIR = Path("output")

# Configure logging
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

@click.group()
@click.version_option(version=version("manim-sandbox"))
def cli():
    """CLI for managing Manim projects."""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--format",
    type=click.Choice(["png", "gif", "mp4"]),
    default="gif",
    help="Output format: 'png', 'gif', or 'mp4'.",
)
def build(project_name, format):
    """Build figures for a specific project."""
    project_path = SRC_DIR / project_name
    output_path = OUTPUT_DIR / project_name

    if not project_path.exists():
        log.error(f"Project '{project_name}' does not exist in {SRC_DIR}.")
        return

    # Set quality and format arguments based on output format
    if format == "png":
        quality_args = ["-qk", "--save-png"]
    elif format == "gif":
        quality_args = ["-qm", "--format", "gif"]
    else:  # mp4
        quality_args = ["-qm", "--format", "mp4"]

    log.info(f"Building files for project: {project_name}...")

    # Process each file in the project folder
    for file_path in project_path.glob("*.py"):
        log.info(f"Processing {file_path.name}...")
        command = ["manim", str(file_path)] + quality_args
        subprocess.run(command, check=True)

    log.info(f"Build complete! Outputs saved to {output_path}")


@cli.command()
@click.argument("project_name")
def new(project_name):
    """Set up a new project folder."""
    log.info(f"Creating new project: {project_name}...")

    # Folder structure
    project_path = SRC_DIR / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    # Create example scripts
    intro_file = project_path / "intro.py"
    intro_file.write_text(f"""# Example: Introduction figure
from manim import *

class Intro(Scene):
    def construct(self):
        self.add(Text("Hello, {project_name}!"))
""")

    example_file = project_path / "example.py"
    example_file.write_text("""# Example: Another figure
from manim import *

class Example(Scene):
    def construct(self):
        self.add(Square())
""")

    log.info(f"Project {project_name} setup complete at path: {project_path}!")
