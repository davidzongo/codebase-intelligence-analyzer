from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codebase-intelligence-analyzer",
    version="0.1.0",
    author="David Zongo",
    description="Context-aware code intelligence with natural language queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tree-sitter>=0.21.3",
        "tree-sitter-languages>=1.10.2",
        "chromadb>=0.4.22",
        "sentence-transformers>=2.3.1",
        "openai>=1.12.0",
        "python-dotenv>=1.0.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "tiktoken>=0.6.0",
    ],
    entry_points={
        "console_scripts": [
            "codebase-analyze=codebase_intelligence.cli:main",
        ],
    },
)
