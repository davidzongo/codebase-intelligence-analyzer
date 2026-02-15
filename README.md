# Codebase Intelligence Analyzer

A portfolio project to enable developers, architects, and DevOps teams to query large codebases, understand dependencies, and assess the impact of changes using RAG and LLMs.

## 🚀 Project Overview

Help development teams gain instant, context-aware insights into codebases. Answer natural language questions about code, trace dependencies, and highlight potential impact of changes — all while keeping data private and self-hosted.

## ✨ Key Features

- **Context-aware code intelligence** - Semantic understanding of your codebase using vector embeddings
- **Natural language queries over code** - Ask questions in plain English, get precise answers with code references
- **Traceable references** - Every answer includes file paths, function names, and line numbers
- **Private, deployable solution** - Run locally or in your private cloud - your code never leaves your infrastructure
- **Multi-language support** - Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Ruby, PHP
- **Dependency tracing** - Understand how code elements are connected
- **Impact analysis** - Assess the potential impact of changes before making them

## 📋 Prerequisites

- Python 3.8 or higher
- (Optional) OpenAI API key for LLM-powered responses

## 🔧 Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/davidzongo/codebase-intelligence-analyzer.git
cd codebase-intelligence-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Option 2: Install with pip (when published)

```bash
pip install codebase-intelligence-analyzer
```

## 🚀 Quick Start

### 1. Index Your Codebase

First, index your codebase to create a searchable vector database:

```bash
codebase-analyze index /path/to/your/codebase
```

With custom file patterns:

```bash
codebase-analyze index /path/to/your/codebase -p "**/*.py" -p "**/*.js"
```

Specify a custom database location:

```bash
codebase-analyze index /path/to/your/codebase --db-path ./my_db
```

### 2. Query Your Code

Ask natural language questions about your codebase:

```bash
codebase-analyze query "How does authentication work?"
```

```bash
codebase-analyze query "Where is the user registration function?"
```

```bash
codebase-analyze query "What classes handle database connections?"
```

### 3. Trace Dependencies

Understand how functions and classes are connected:

```bash
codebase-analyze trace "UserService"
```

```bash
codebase-analyze trace "authenticate_user"
```

### 4. Analyze Impact

Before making changes, understand their potential impact:

```bash
codebase-analyze impact "src/auth/login.py"
```

With a description of planned changes:

```bash
codebase-analyze impact "src/auth/login.py" -d "Refactoring authentication logic"
```

### 5. View Statistics

See information about your indexed codebase:

```bash
codebase-analyze stats
```

## 🔑 Configuration

### OpenAI API Key (Optional)

For LLM-powered responses, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Running Without LLM

You can use the tool without an LLM using the `--no-llm` flag:

```bash
codebase-analyze query "How does authentication work?" --no-llm
```

This will return relevant code snippets without generating a natural language answer.

## 📚 Usage Examples

### Example 1: Understanding a New Codebase

```bash
# Index the codebase
codebase-analyze index ~/projects/awesome-app

# Ask high-level questions
codebase-analyze query "What does this application do?"
codebase-analyze query "What are the main components?"
codebase-analyze query "How is the database configured?"

# Dive deeper
codebase-analyze query "Where are API endpoints defined?"
codebase-analyze trace "APIRouter"
```

### Example 2: Impact Analysis Before Refactoring

```bash
# Check what would be affected
codebase-analyze impact "src/services/user_service.py"

# Trace specific functions
codebase-analyze trace "create_user"
codebase-analyze trace "update_user"

# Query for related code
codebase-analyze query "What code depends on UserService?"
```

### Example 3: Finding Security Issues

```bash
# Look for authentication code
codebase-analyze query "How is password hashing implemented?"

# Check for sensitive data
codebase-analyze query "Where are API keys and secrets stored?"

# Trace security-critical functions
codebase-analyze trace "verify_password"
```

## 🏗️ Architecture

The system consists of three main components:

1. **Code Parser** (`parsers/code_parser.py`)
   - Uses Tree-sitter for accurate syntax parsing
   - Supports multiple programming languages
   - Extracts functions, classes, imports, and documentation

2. **Codebase Indexer** (`indexer/code_indexer.py`)
   - Creates vector embeddings using sentence-transformers
   - Stores embeddings in ChromaDB (local vector database)
   - Enables semantic search over code

3. **Query Engine** (`query/query_engine.py`)
   - Processes natural language queries
   - Retrieves relevant code using vector similarity
   - (Optional) Uses LLM to generate context-aware answers
   - Provides traceable references with file paths and line numbers

## 🔒 Privacy & Security

- **Local-first**: All data processing happens on your machine
- **No telemetry**: We don't collect any usage data
- **Private vector database**: Your code embeddings stay on your infrastructure
- **Optional LLM**: Can work without sending data to external APIs
- **Self-hosted deployment**: Deploy in your private cloud if needed

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=codebase_intelligence tests/
```

### Project Structure

```
codebase-intelligence-analyzer/
├── src/
│   └── codebase_intelligence/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── parsers/            # Code parsing logic
│       │   ├── __init__.py
│       │   └── code_parser.py
│       ├── indexer/            # Vector database indexing
│       │   ├── __init__.py
│       │   └── code_indexer.py
│       └── query/              # Query processing
│           ├── __init__.py
│           └── query_engine.py
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tree-sitter for parsing capabilities
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- OpenAI for optional LLM integration

## 📧 Contact

David Zongo - GitHub: [@davidzongo](https://github.com/davidzongo)

## 🗺️ Roadmap

- [ ] Support for more programming languages
- [ ] Web UI for easier interaction
- [ ] Integration with popular IDEs
- [ ] Custom model fine-tuning
- [ ] Code change suggestions
- [ ] Automated documentation generation
- [ ] GitHub integration
- [ ] Team collaboration features
