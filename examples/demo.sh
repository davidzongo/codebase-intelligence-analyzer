#!/bin/bash

# Example script demonstrating CLI usage
# Make sure you've installed the package first: pip install -e .

echo "======================================"
echo "Codebase Intelligence Analyzer Demo"
echo "======================================"
echo ""

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Example codebase path - change this to your actual codebase
CODEBASE_PATH="./src"
DB_PATH="./demo_db"

echo -e "${BLUE}Step 1: Indexing the codebase${NC}"
echo "Command: codebase-analyze index $CODEBASE_PATH --db-path $DB_PATH"
echo ""
codebase-analyze index "$CODEBASE_PATH" --db-path "$DB_PATH"

echo ""
echo -e "${BLUE}Step 2: Viewing statistics${NC}"
echo "Command: codebase-analyze stats --db-path $DB_PATH"
echo ""
codebase-analyze stats --db-path "$DB_PATH"

echo ""
echo -e "${BLUE}Step 3: Querying the codebase${NC}"
echo "Command: codebase-analyze query 'How does code parsing work?' --db-path $DB_PATH --no-llm"
echo ""
codebase-analyze query "How does code parsing work?" --db-path "$DB_PATH" --no-llm

echo ""
echo -e "${BLUE}Step 4: Tracing dependencies${NC}"
echo "Command: codebase-analyze trace 'CodeParser' --db-path $DB_PATH"
echo ""
codebase-analyze trace "CodeParser" --db-path "$DB_PATH"

echo ""
echo -e "${BLUE}Step 5: Analyzing impact${NC}"
echo "Command: codebase-analyze impact 'code_parser.py' --db-path $DB_PATH"
echo ""
codebase-analyze impact "code_parser.py" --db-path "$DB_PATH"

echo ""
echo -e "${GREEN}======================================"
echo "Demo complete!"
echo "======================================${NC}"
echo ""
echo "Try your own queries:"
echo "  codebase-analyze query 'your question here' --db-path $DB_PATH"
echo ""
