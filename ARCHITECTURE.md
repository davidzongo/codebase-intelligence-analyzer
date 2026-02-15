# Architecture Documentation

## Overview

The Codebase Intelligence Analyzer is a modular system designed to provide context-aware insights into codebases through natural language queries. The architecture follows a pipeline approach: **Parse → Index → Query**.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLI Interface (cli.py)                       │
│                  User Commands: index, query, trace, impact     │
└───────────────────┬──────────────────────┬──────────────────────┘
                    │                      │
        ┌───────────▼──────────┐  ┌────────▼──────────┐
        │   Code Parser        │  │  Query Engine     │
        │  (parsers/)          │  │  (query/)         │
        └───────────┬──────────┘  └────────┬──────────┘
                    │                      │
                    ▼                      ▼
        ┌────────────────────────────────────────────┐
        │      Codebase Indexer                      │
        │      (indexer/)                            │
        │  ┌──────────────┐    ┌──────────────────┐ │
        │  │ Vector Store │◄───┤ Embedding Model  │ │
        │  │  (ChromaDB)  │    │ (Transformers)   │ │
        │  └──────────────┘    └──────────────────┘ │
        └────────────────────────────────────────────┘
                    ▲
                    │
        ┌───────────┴──────────┐
        │   External Services  │
        │   - OpenAI (LLM)     │
        │   - HuggingFace      │
        └──────────────────────┘
```

## Core Components

### 1. Code Parser (`parsers/code_parser.py`)

**Purpose**: Extract structured information from source code files.

**Technology**: Tree-sitter for multi-language parsing

**Capabilities**:
- Supports 10+ programming languages
- Extracts functions, classes, methods
- Captures documentation strings
- Maintains line number information
- Handles multiple file types simultaneously

**Key Methods**:
```python
- detect_language(file_path) → str
- parse_file(file_path) → Dict
- _extract_elements(node, code_bytes, language) → List[Dict]
```

**Output Format**:
```python
{
    'file_path': 'src/example.py',
    'language': 'python',
    'elements': [
        {
            'type': 'function_definition',
            'name': 'example_func',
            'start_line': 10,
            'end_line': 15,
            'content': 'def example_func():\n    ...',
            'docstring': 'Function description'
        }
    ],
    'content': '...'  # Full file content
}
```

### 2. Codebase Indexer (`indexer/code_indexer.py`)

**Purpose**: Create and manage a searchable vector database of code elements.

**Technology**: 
- ChromaDB for vector storage
- Sentence Transformers for embeddings (all-MiniLM-L6-v2)

**Process**:
1. Recursively find source files
2. Parse each file using CodeParser
3. Generate embeddings for each code element
4. Store in persistent vector database

**Key Methods**:
```python
- index_codebase(path, file_patterns) → None
- search(query, n_results) → List[Dict]
- get_statistics() → Dict
```

**Data Flow**:
```
Source Files → Parser → Code Elements → Embedding Model → Vector DB
                                                              ↓
                                                         ChromaDB
```

**Searchable Text Format**:
```
File: src/auth.py
Language: python
Type: function_definition
Name: authenticate_user
Documentation: Authenticate user credentials
Code:
def authenticate_user(username, password):
    ...
```

### 3. Query Engine (`query/query_engine.py`)

**Purpose**: Process natural language queries and provide context-aware answers.

**Features**:
- Semantic search using vector similarity
- Optional LLM integration for natural language answers
- Dependency tracing
- Impact analysis

**Key Methods**:
```python
- query(question, n_context, use_llm) → Dict
- trace_dependencies(element_name) → Dict
- analyze_impact(file_path) → Dict
```

**Query Flow**:
```
User Question
    ↓
Vector Search (find relevant code)
    ↓
Retrieve Top-N matches
    ↓
[Optional] LLM Processing
    ↓
Format Response with References
```

**LLM Prompt Structure**:
```
System: You are a code analysis assistant...
User: 
  Question: <user_question>
  Code Context: <top_n_matches>
  Instructions: Provide traceable answer...
```

### 4. CLI Interface (`cli.py`)

**Purpose**: Command-line interface for user interactions.

**Technology**: Click framework for CLI, Rich for formatting

**Commands**:
- `index`: Index a codebase
- `query`: Ask questions
- `trace`: Trace dependencies
- `impact`: Analyze change impact
- `stats`: Show statistics

**User Experience Features**:
- Colored output
- Progress indicators
- Tables for structured data
- Panels for answers
- Error handling with helpful messages

## Data Models

### Code Element

```python
{
    'type': str,           # e.g., 'function_definition', 'class_declaration'
    'name': str,           # Element name
    'start_line': int,     # Starting line number
    'end_line': int,       # Ending line number
    'content': str,        # Full source code of element
    'docstring': str       # Documentation (if available)
}
```

### Query Result

```python
{
    'answer': str,         # Natural language answer
    'references': [        # Traceable references
        {
            'file': str,
            'element_name': str,
            'element_type': str,
            'start_line': int,
            'end_line': int,
            'language': str,
            'relevance_score': float
        }
    ],
    'question': str,
    'context_count': int
}
```

### Dependency Information

```python
{
    'element': str,
    'found': bool,
    'dependencies': [
        {
            'definition': {...},
            'potential_usages': [...]
        }
    ]
}
```

## Technology Stack

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| tree-sitter | 0.21.3 | AST parsing |
| tree-sitter-languages | 1.10.2 | Multi-language support |
| chromadb | 0.4.22+ | Vector database |
| sentence-transformers | 2.3.1+ | Embeddings |
| openai | 1.12.0+ | LLM integration (optional) |
| click | 8.1.7+ | CLI framework |
| rich | 13.7.0+ | Terminal formatting |

### Language Support

Fully supported languages:
- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp)
- Ruby (.rb)
- PHP (.php)

## Storage

### Vector Database (ChromaDB)

**Location**: `./chroma_db` (configurable)

**Structure**:
```
chroma_db/
├── chroma.sqlite3          # Metadata storage
├── metadata.json           # Indexing metadata
└── [collection_data]/      # Vector embeddings
```

**Collection Schema**:
- **IDs**: `file_path:start_line-end_line:element_name`
- **Embeddings**: 384-dimensional vectors (all-MiniLM-L6-v2)
- **Documents**: Searchable text representation
- **Metadata**: File path, language, type, line numbers, etc.

### Metadata File

```json
{
    "codebase_path": "/path/to/codebase",
    "indexed_at": "2024-01-15T10:30:00",
    "file_count": 150
}
```

## Performance Considerations

### Indexing Performance

**Factors**:
- Number of files
- File sizes
- Language complexity
- Embedding model speed

**Optimizations**:
- Automatic exclusion of common directories (node_modules, venv, etc.)
- File pattern filtering
- Batch processing of elements
- Persistent storage for reuse

**Typical Performance**:
- Small project (< 100 files): 30-60 seconds
- Medium project (100-1000 files): 2-5 minutes
- Large project (1000+ files): 10-30 minutes

### Query Performance

**Factors**:
- Vector database size
- Number of context snippets requested
- LLM response time (if enabled)

**Typical Performance**:
- Vector search: < 1 second
- With LLM: 2-5 seconds (depends on API)
- Without LLM: < 1 second

## Security & Privacy

### Local-First Architecture

- All code parsing happens locally
- Vector database stored locally
- No code sent to external services (except optional LLM)

### Optional External Services

**OpenAI API** (optional):
- Only used when `use_llm=True`
- Only sends:
  - User question
  - Top-N code snippets (not entire codebase)
- Can be disabled with `--no-llm` flag

### Data Privacy

- No telemetry or usage tracking
- No automatic data collection
- User has full control over data
- Can be deployed in air-gapped environments (with pre-downloaded models)

## Extensibility

### Adding New Languages

1. Ensure tree-sitter-languages supports it
2. Add file extension mapping in `LANGUAGE_MAP`
3. Add element types in `target_types`
4. Test parsing

### Custom Embedding Models

Replace in `CodebaseIndexer.__init__`:
```python
self.embedding_model = SentenceTransformer('your-model-name')
```

### Alternative Vector Stores

Implement interface matching ChromaDB:
- `add()`: Store embeddings
- `query()`: Search by vector
- `count()`: Get statistics

### Custom LLM Providers

Replace in `QueryEngine._generate_llm_answer`:
```python
# Use different LLM API
response = your_llm_api.generate(prompt)
```

## Error Handling

### Parser Errors
- Gracefully skip unparseable files
- Log errors without stopping indexing
- Return None for failed parses

### Indexing Errors
- Continue on individual file failures
- Report statistics on success/failure
- Validate paths before processing

### Query Errors
- Handle empty databases
- Provide helpful error messages
- Fall back to simple results if LLM fails

## Future Enhancements

### Planned Features
1. Incremental indexing (only changed files)
2. Web UI for easier interaction
3. IDE integrations (VS Code, IntelliJ)
4. Custom model fine-tuning
5. Code change suggestions
6. Automated documentation generation
7. Team collaboration features
8. Graph-based dependency visualization

### Scalability Improvements
1. Distributed indexing for large codebases
2. Caching frequently accessed results
3. Parallel processing for parsing
4. Optimized vector search algorithms

## Testing Strategy

### Unit Tests
- Parser: Language detection, element extraction
- Indexer: File finding, embedding generation
- Query Engine: Search, dependency tracing

### Integration Tests
- End-to-end indexing and querying
- Multi-language support
- CLI command execution

### Performance Tests
- Indexing speed benchmarks
- Query response time
- Memory usage monitoring

## Deployment Options

### Local Development
```bash
pip install -e .
codebase-analyze index ./project
```

### Private Cloud
```bash
# Docker deployment (future)
docker build -t codebase-analyzer .
docker run -v /data:/data codebase-analyzer
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Analyze Code
  run: |
    pip install codebase-intelligence-analyzer
    codebase-analyze index .
    codebase-analyze query "potential security issues"
```

## Conclusion

The Codebase Intelligence Analyzer provides a robust, extensible architecture for code analysis. Its modular design allows for easy customization while maintaining privacy and security through local-first processing.
