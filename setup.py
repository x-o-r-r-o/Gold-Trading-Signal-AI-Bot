from setuptools import setup, find_packages

setup(
    name="gold-signal-bot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-dotenv",
        "requests",
        "pydantic",
        "pandas",
        "numpy",
        "scipy",
        "beautifulsoup4",
        "lxml",
        "python-dateutil",
        "pytz",
        "pyyaml",
        "tqdm",
        "loguru",
        "vaderSentiment",
        "torch",
    ],
    entry_points={
        "console_scripts": [
            "gold-signal-bot=src.main:main",
        ]
    },
)