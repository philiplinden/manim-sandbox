import os
import shutil
import click
from subprocess import run

# Constants
SRC_DIR = "src/common"
OUTPUT_DIR = "output"


@click.group()
def cli():
    """CLI for managing Manim projects."""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--target",
    required=True,
    type=click.Choice(["static", "dynamic"]),
    help="Build type: 'static' or 'dynamic'.",
)
def build(project_name, target):
    """Build static or dynamic figures for a specific project."""
    project_path = os.path.join(SRC_DIR, project_name)
    output_path = os.path.join(OUTPUT_DIR, project_name, target)

    if not os.path.exists(project_path):
        click.echo(
            f"Error: Project '{project_name}' does not exist in {SRC_DIR}."
        )
        return

    quality = "-qk --save-png" if target == "static" else "-qm"

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    click.echo(f"Building {target} figures for project: {project_name}...")

    # Process each file in the project folder
    for file in os.listdir(project_path):
        if file.endswith(".py"):
            file_path = os.path.join(project_path, file)
            click.echo(f"Processing {file}...")
            run(
                f"manim {file_path} {quality} --output-file {output_path}",
                shell=True,
            )

    click.echo(f"Build complete! Outputs saved to {output_path}")


@cli.command()
@click.argument("project_name")
def new(project_name):
    """Set up a new project folder."""
    click.echo(f"Creating new project: {project_name}...")

    # Folder structure
    project_path = os.path.join(SRC_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)

    # Create example scripts
    with open(os.path.join(project_path, "intro.py"), "w") as f:
        f.write(f"""# Example: Introduction figure
from manim import *

class Intro(Scene):
    def construct(self):
        self.add(Text("Hello, {project_name}!"))
""")

    with open(os.path.join(project_path, "example.py"), "w") as f:
        f.write("""# Example: Another figure
from manim import *

class Example(Scene):
    def construct(self):
        self.add(Square())
""")

    click.echo(f"Project {project_name} setup complete!")


@cli.command()
@click.argument("project_name", required=False)
def clean(project_name):
    """Clean outputs for a specific project or all outputs."""
    if project_name:
        output_path = os.path.join(OUTPUT_DIR, project_name)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
            click.echo(f"Cleaned outputs for project: {project_name}")
        else:
            click.echo(f"No outputs found for project: {project_name}")
    else:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
            click.echo("Cleaned all outputs.")
        else:
            click.echo("No outputs to clean.")
