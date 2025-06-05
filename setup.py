from setuptools import setup, find_packages

setup(
    name="ai-travel-planner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Core Streamlit and dependencies
        "streamlit>=1.45.0",
        "click>=8.1.3,<9.0.0",

        # Data processing and visualization
        "altair",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "Pillow",
        "plotly",

        # File handling
        "openpyxl",
        "pyarrow",

        # Web/API utilities
        "requests",
        "beautifulsoup4",

        # Machine learning
        "scikit-learn",
        "tensorflow",  # or "tensorflow-cpu"

        # Audio/Text processing
        "gTTS",
        "pydub",

        # Environment management
        "python-dotenv",

        # LangChain ecosystem
        "langgraph",

        # Development tools (should be in dev dependencies)
        # "black",
        # "ruff",
    ],
)