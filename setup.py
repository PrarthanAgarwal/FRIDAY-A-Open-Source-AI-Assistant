from setuptools import setup, find_packages

setup(
    name="FRIDAY",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "numpy>=1.20.0",
        "loguru>=0.7.0",
        "transformers>=4.30.0",
        "phonemizer>=3.2.1",
        "nltk>=3.8.1",
        "g2p-en>=2.1.0",
        "munch>=4.0.0",
        "PyYAML>=6.0",
        "parselmouth>=0.4.3",
        "faster-whisper>=0.9.0",
        "llama-cpp-python>=0.2.0",
        "redis>=5.0.0",
        "asyncio>=3.4.3",
    ],
    python_requires=">=3.9",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
        ]
    }
) 