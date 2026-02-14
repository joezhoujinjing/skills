"""CLI interface for email processing."""

from .process import EmailProcessor
from .review import ReviewInterface

__all__ = ['EmailProcessor', 'ReviewInterface']
