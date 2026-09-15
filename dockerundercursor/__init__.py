"""Register the Docker Under Cursor extension when Krita loads the plugin."""

from .docker_under_cursor import DockerUnderCursor

__all__ = ["DockerUnderCursor"]

__version__ = "1.1.1"
