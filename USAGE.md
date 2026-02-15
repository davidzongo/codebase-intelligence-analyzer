# Usage Guide

This guide provides detailed instructions on how to use the Codebase Intelligence Analyzer.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Commands](#commands)
4. [Use Cases](#use-cases)
5. [Configuration](#configuration)
6. [Programmatic Usage](#programmatic-usage)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
git clone https://github.com/davidzongo/codebase-intelligence-analyzer.git
cd codebase-intelligence-analyzer
pip install -e .
```

### Verify Installation

```bash
codebase-analyze --version
```

## Quick Start

### 1. Index Your Codebase

Before you can query your codebase, you need to index it:

```bash
codebase-analyze index /path/to/your/project
```

This command will:
- Scan all supported source files
- Extract functions, classes, and their documentation
- Create vector embeddings for semantic search
- Store everything in a local database (./chroma_db by default)

### 2. Query Your Code

Once indexed, you can ask natural language questions:

```bash
codebase-analyze query "How does authentication work?"
```

The tool will:
- Search for relevant code snippets
- (Optionally) Use an LLM to generate a comprehensive answer
- Display traceable references with file paths and line numbers

### 3. Explore Dependencies

Trace how code elements are connected:

```bash
codebase-analyze trace "UserService"
```

### 4. Analyze Impact

Before making changes, understand their potential impact:

```bash
codebase-analyze impact "src/auth/login.py"
```

## Commands

### `index` - Index a Codebase

Index source code files for intelligent querying.

**Syntax:**
```bash
codebase-analyze index <path> [options]
```

**Options:**
- `--db-path PATH`: Path to store vector database (default: ./chroma_db)
- `-p, --patterns PATTERN`: File patterns to index (can be used multiple times)

**Examples:**
```bash
# Index entire project
codebase-analyze index ./my-project

# Index only Python files
codebase-analyze index ./my-project -p "**/*.py"

# Index multiple file types with custom database location
codebase-analyze index ./my-project \
  -p "**/*.py" \
  -p "**/*.js" \
  --db-path ./custom_db
```

### `query` - Query the Codebase

Ask natural language questions about your indexed codebase.

**Syntax:**
```bash
codebase-analyze query "<question>" [options]
```

**Options:**
- `--db-path PATH`: Path to vector database
- `--no-llm`: Disable LLM-powered responses (return raw results)
- `-c, --context N`: Number of code snippets to retrieve (default: 5)
- `--model MODEL`: OpenAI model to use (default: gpt-3.5-turbo)

**Examples:**
```bash
# Basic query
codebase-analyze query "What functions handle user registration?"

# Query without LLM (faster, no API key needed)
codebase-analyze query "database connection code" --no-llm

# Use more context snippets
codebase-analyze query "authentication flow" -c 10

# Use a different model
codebase-analyze query "security vulnerabilities" --model gpt-4
```

### `trace` - Trace Dependencies

Find definitions and usages of code elements.

**Syntax:**
```bash
codebase-analyze trace <element-name> [options]
```

**Options:**
- `--db-path PATH`: Path to vector database

**Examples:**
```bash
# Trace a class
codebase-analyze trace "DatabaseConnection"

# Trace a function
codebase-analyze trace "authenticate_user"

# Trace with custom database
codebase-analyze trace "APIRouter" --db-path ./custom_db
```

### `impact` - Analyze Impact

Assess the potential impact of changes to a file.

**Syntax:**
```bash
codebase-analyze impact <file-path> [options]
```

**Options:**
- `--db-path PATH`: Path to vector database
- `-d, --description TEXT`: Description of planned changes

**Examples:**
```bash
# Basic impact analysis
codebase-analyze impact "src/services/user_service.py"

# With change description
codebase-analyze impact "src/api/routes.py" \
  -d "Refactoring to use async/await"
```

### `stats` - Show Statistics

Display information about the indexed codebase.

**Syntax:**
```bash
codebase-analyze stats [options]
```

**Options:**
- `--db-path PATH`: Path to vector database

**Example:**
```bash
codebase-analyze stats
```

## Use Cases

### Use Case 1: Understanding a New Codebase

When joining a new project or exploring unfamiliar code:

```bash
# Index the codebase
codebase-analyze index ~/projects/new-project

# Get a high-level overview
codebase-analyze query "What does this application do?"
codebase-analyze query "What are the main components?"

# Understand specific areas
codebase-analyze query "How is the database configured?"
codebase-analyze query "Where are the API endpoints defined?"

# Trace key components
codebase-analyze trace "Application"
codebase-analyze trace "DatabaseManager"
```

### Use Case 2: Refactoring Safely

Before making changes, understand the impact:

```bash
# Check what would be affected
codebase-analyze impact "src/core/engine.py"

# Trace dependencies
codebase-analyze trace "Engine"

# Find all usages
codebase-analyze query "where is Engine class used?"

# Understand the current implementation
codebase-analyze query "how does Engine class work?"
```

### Use Case 3: Security Audit

Find and review security-critical code:

```bash
# Find authentication code
codebase-analyze query "authentication and authorization code"

# Check password handling
codebase-analyze query "password hashing and validation"

# Find sensitive data storage
codebase-analyze query "where are credentials and secrets stored?"

# Review specific security functions
codebase-analyze trace "verify_password"
codebase-analyze trace "encrypt_data"
```

### Use Case 4: Documentation and Knowledge Sharing

Help team members understand the codebase:

```bash
# Generate explanations
codebase-analyze query "explain how the payment processing works"

# Find examples
codebase-analyze query "examples of using the notification service"

# Understand patterns
codebase-analyze query "what design patterns are used?"
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# OpenAI API Key (optional - only for LLM-powered responses)
OPENAI_API_KEY=your-api-key-here

# Default model (optional)
OPENAI_MODEL=gpt-3.5-turbo

# Default database path (optional)
DB_PATH=./chroma_db

# Default context size (optional)
CONTEXT_SIZE=5
```

### Using Without OpenAI

The tool works without an OpenAI API key using the `--no-llm` flag:

```bash
codebase-analyze query "your question" --no-llm
```

This will:
- Still perform semantic search
- Return relevant code snippets
- Show file paths and line numbers
- Skip natural language answer generation

## Programmatic Usage

You can use the analyzer in your Python code:

```python
from codebase_intelligence import CodebaseIndexer, QueryEngine
from pathlib import Path

# Index a codebase
indexer = CodebaseIndexer(db_path="./my_db")
indexer.index_codebase(Path("./my-project"))

# Query the codebase
engine = QueryEngine(indexer)
result = engine.query("How does authentication work?")

print(result['answer'])
for ref in result['references']:
    print(f"  {ref['file']}:{ref['start_line']} - {ref['element_name']}")

# Trace dependencies
deps = engine.trace_dependencies("UserService")
print(deps)

# Analyze impact
impact = engine.analyze_impact("src/auth/login.py")
print(impact['impact_summary'])
```

## Troubleshooting

### Issue: "Cannot send a request, as the client has been closed"

This usually means the vector database couldn't download the embedding model.

**Solution:**
- Check your internet connection
- Try using `--no-llm` flag
- Pre-download models in an environment with internet access

### Issue: "Database not found"

You need to index the codebase first.

**Solution:**
```bash
codebase-analyze index /path/to/your/codebase
```

### Issue: "OpenAI API key not found"

You're trying to use LLM features without an API key.

**Solutions:**
1. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

2. Or use without LLM:
   ```bash
   codebase-analyze query "your question" --no-llm
   ```

### Issue: "Language not supported"

The parser doesn't support the file type.

**Solution:**
Currently supported languages: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Ruby, PHP

### Issue: Slow indexing

Large codebases can take time to index.

**Solutions:**
- Use file patterns to index only specific file types
- Exclude directories like `node_modules`, `venv`, etc. (automatically excluded)
- Be patient - indexing is a one-time operation

### Issue: No relevant results

The search isn't finding what you're looking for.

**Solutions:**
- Try different search terms
- Increase context size: `-c 10`
- Re-index the codebase if files were added/changed
- Be more specific in your query

## Advanced Topics

### Custom File Patterns

Index only specific file types or directories:

```bash
# Only Python files
codebase-analyze index ./project -p "**/*.py"

# Multiple patterns
codebase-analyze index ./project \
  -p "src/**/*.py" \
  -p "lib/**/*.py"

# Specific directories
codebase-analyze index ./project -p "src/api/**/*.js"
```

### Multiple Databases

Maintain separate databases for different projects:

```bash
# Project A
codebase-analyze index ./project-a --db-path ./db_a
codebase-analyze query "..." --db-path ./db_a

# Project B
codebase-analyze index ./project-b --db-path ./db_b
codebase-analyze query "..." --db-path ./db_b
```

### Updating the Index

When code changes, re-index to update:

```bash
codebase-analyze index /path/to/project
```

This will update the existing database with new/changed files.

## Best Practices

1. **Index Once, Query Many**: Indexing is slow, querying is fast
2. **Use Specific Queries**: More specific questions get better results
3. **Leverage References**: Always check the file paths and line numbers
4. **Combine Commands**: Use query + trace + impact together for comprehensive analysis
5. **Keep Database Updated**: Re-index after significant code changes
6. **Use File Patterns**: Only index what you need for faster operations

## Next Steps

- Explore the [examples](examples/) directory for more usage patterns
- Check the [API documentation](README.md) for programmatic usage
- Join discussions on GitHub for tips and tricks
