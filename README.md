# HR Policy Chat Assistant

A GenAI-powered HR assistant for policy search and leave application. This intelligent system helps employees understand and navigate company HR policies through natural language interactions.

## Features

### Smart Policy Search
- Natural language query understanding
- Context-aware policy lookup
- Source-backed responses
- Real-time policy updates

### Available Policies
- Leave Management
  - Maternity Leave
  - Casual Leave
  - General Leave Overview
- Coming Soon:
  - Sick Leave
  - Paternity Leave
  - Work From Home Policy

### Sample Questions
1. Leave Duration & Eligibility
   - "What's the maximum maternity leave duration?"
   - "How many casual leaves do I get per year?"
   - "Am I eligible for maternity leave extension?"

2. Application Process
   - "How do I apply for casual leave?"
   - "What documents are needed for maternity leave?"
   - "What's the process for emergency leave?"

3. Policy Details
   - "Can I combine different types of leave?"
   - "What happens to unused casual leave?"
   - "Is work from home available after maternity leave?"

## Local Setup & Run Instructions

1. Create and activate a Python 3.11 virtual environment:
   ```sh
   python3.11 -m venv .venv && source .venv/bin/activate
   ```
2. Upgrade pip:
   ```sh
   pip install -U pip
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys and config values.
5. Run ingestion:
   ```sh
   python -m app.rag.ingest
   ```
6. Run the Streamlit app:
   ```sh
   streamlit run app/main.py
   ```
7. The app will launch in your browser. Ask HR policy questions or apply for leave via chat.

## Configuration
- Environment variables in `.env` override values in `config.yaml`.
- See `config.yaml` for all configurable options.

## Configuration Details

### Environment Variables
```ini
OPENAI_API_KEY=your-api-key
EMBED_MODEL=text-embedding-3-small
CHROMA_DIR=app/rag/data/index
TOP_K=4
MAX_TOKENS_POLICY=400
MAX_TOKENS_LEAVE=250
```

### Policy Document Format
```markdown
---
policy_id: POL-001
effective_date: 2025-01-01
last_updated: 2025-10-27
department: HR
category: Leave
---

# Policy Title

## Section Name
Policy content here...
```

## Usage Examples

### 1. Policy Search
```bash
# Search for specific policy information
python -m app.rag.search "What is the maternity leave duration?"

# Check application process
python -m app.rag.search "How do I apply for casual leave?"

# Query contact information
python -m app.rag.search "Who should I contact for leave questions?"
```

### 2. Adding New Policies
1. Create markdown file in `app/rag/data/sample_policies/`
2. Include proper frontmatter
3. Run ingestion:
   ```bash
   python -m app.rag.ingest
   ```

## Troubleshooting

### Common Issues
1. **Installation Issues**
   - Use Python 3.11
   - Fix NumPy errors: `pip install 'numpy<2.0'`
   - Ensure ChromaDB compatibility: Use version 0.4.24

2. **Search Problems**
   - No results? Run ingestion first
   - Poor results? Try rephrasing the question
   - Error messages? Check API key and environment variables

3. **Data Management**
   - Clear index: `rm -rf app/rag/data/index`
   - Refresh policies: `python -m app.rag.ingest`
   - Update embeddings: Modify `EMBED_MODEL` in `.env`
