import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstallCommand(install):
    """Custom installation class that checks system dependencies."""
    def run(self):
        self.check_dependencies()
        install.run(self)

    def check_dependencies(self):
        # Check FFmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except FileNotFoundError:
            raise SystemError(
                "FFmpeg is not installed. Please install FFmpeg first:\n"
                "Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "MacOS: brew install ffmpeg\n"
                "Windows: Download from FFmpeg website"
            )

        # Check libmagic
        try:
            import magic
            magic.Magic()
        except Exception:
            raise SystemError(
                "libmagic is not installed. Please install it:\n"
                "Ubuntu/Debian: sudo apt-get install libmagic1\n"
                "MacOS: brew install libmagic\n"
                "Windows: Included in python-magic-bin"
            )

setup(
    name="streambuddy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Read requirements from requirements.txt
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    python_requires='>=3.10',
)