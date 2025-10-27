# RAG Pipeline Explanation

## What is RAG?
RAG (Retrieval-Augmented Generation) is like having a smart assistant that can read, understand, and remember your company's policy documents, and then use that knowledge to answer questions accurately.

## How Does Our System Work?

### 1. Document Processing (loader.py)
Think of this as a smart document reader that:
- Takes your policy documents (both PDF and Markdown files)
- Breaks them into smaller, manageable pieces (like breaking a book into paragraphs)
- Keeps track of important information about each piece:
  - Which policy it came from
  - Which section it belongs to
  - When the policy became effective
  - The source document name

### 2. Information Storage (store.py)
This is like a highly organized filing system that:
- Takes all the document pieces
- Creates a special "memory" (embedding) for each piece that helps the system understand its meaning
- Stores everything in a searchable database (Chroma)
- Can quickly find the most relevant information when asked a question

### 3. Document Ingestion (ingest.py)
This is the process that:
- Reads all your policy documents from the `data/sample_policies` folder
- Uses OpenAI's technology to understand the content
- Saves everything in an organized way for quick retrieval
- Can be run with a simple command: `python -m app.rag.ingest`

## How Information Flows

1. **Input**: HR policy documents are placed in the `data/sample_policies` folder
2. **Processing**:
   - Documents are read and split into meaningful chunks
   - Each chunk gets special tags (metadata) to track its source and context
   - OpenAI's technology creates a smart summary (embedding) of each chunk
3. **Storage**:
   - All processed information is stored in a searchable database
4. **Retrieval**:
   - When someone asks a question, the system:
     - Understands the question
     - Finds the most relevant policy information
     - Returns accurate answers with references to the source policies

## Example in Action

When someone asks "What is the duration of maternity leave?", the system:
1. Processes the question
2. Searches through all policy chunks
3. Returns relevant information, like:
   ```
   Source: maternity_leave.md
   Content: "26 weeks of paid maternity leave for eligible employees"
   Score: 0.603 (high relevance)
   ```

## Benefits
- Fast and accurate policy information retrieval
- Consistent answers based on official documents
- Easy to update by just adding new policy documents
- Maintains context and sources for all information

## Maintenance
To add or update policies:
1. Add/update the policy files in `data/sample_policies`
2. Run the ingestion command
3. The system will automatically process and include the new information