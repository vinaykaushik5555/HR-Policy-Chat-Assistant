"""
This module handles the loading and processing of policy documents (both Markdown and PDF).
Similar to Java's DocumentProcessor or ContentLoader patterns.
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader

class PolicyLoader:
    """
    /**
     * A class responsible for loading and processing policy documents.
     * Similar to Java's DocumentProcessor pattern.
     * 
     * This class handles:
     * - Loading Markdown and PDF files
     * - Extracting metadata from frontmatter
     * - Chunking documents into processable pieces
     * - Attaching metadata to chunks
     */
    """
    
    def __init__(self, policies_dir: str):
        """
        /**
         * Constructor for PolicyLoader
         * @param policies_dir: String path to the directory containing policy documents
         */
        """
        self.policies_dir = Path(policies_dir)
        
    def _extract_frontmatter(self, content: str) -> tuple[Dict, str]:
        """
        /**
         * Extracts YAML frontmatter metadata from markdown content.
         * Similar to Java's MetadataExtractor pattern.
         * 
         * @param content: String content of the markdown file
         * @return: Tuple of (metadata dictionary, remaining content)
         * 
         * Example frontmatter:
         * ---
         * policy_id: POL-001
         * effective_date: 2025-01-01
         * ---
         */
        """
        if content.startswith('---'):
            parts = content.split('---', 2)[1:]
            if len(parts) == 2:
                try:
                    metadata = yaml.safe_load(parts[0])
                    # Convert all date objects to strings
                    for key, value in metadata.items():
                        if isinstance(value, (int, float, bool)):
                            continue
                        metadata[key] = str(value)
                    return metadata, parts[1]
                except yaml.YAMLError:
                    pass
        return {}, content

    def _process_markdown(self, file_path: Path) -> List[Dict]:
        """
        /**
         * Processes a markdown file and returns chunks with metadata.
         * Similar to Java's FileProcessor with metadata handling.
         * 
         * @param file_path: Path object pointing to the markdown file
         * @return: List of dictionaries containing chunks and their metadata
         * 
         * Processing steps:
         * 1. Read file content
         * 2. Extract frontmatter metadata
         * 3. Split by headers
         * 4. Further split large sections
         * 5. Attach metadata to each chunk
         */
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract frontmatter
        metadata, content = self._extract_frontmatter(content)
        
        # Set up markdown splitter with headers
        headers_to_split_on = [
            ("#", "section"),
            ("##", "subsection"),
        ]
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_chunks = md_splitter.split_text(content)
        
        # Further split long chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            length_function=len,
        )
        
        chunks = []
        for md_chunk in md_chunks:
            if len(md_chunk.page_content) > 800:  # Only split if chunk is large
                smaller_chunks = text_splitter.split_text(md_chunk.page_content)
                for i, chunk in enumerate(smaller_chunks):
                    chunks.append({
                        "text": chunk,
                        "metadata": {
                            **metadata,
                            **md_chunk.metadata,
                            "source": file_path.name,
                            "policy_id": metadata.get("policy_id", file_path.stem),
                            "chunk_id": f"{file_path.stem}-{md_chunk.metadata.get('section', 'main')}-{i}"
                        }
                    })
            else:
                chunks.append({
                    "text": md_chunk.page_content,
                    "metadata": {
                        **metadata,
                        **md_chunk.metadata,
                        "source": file_path.name,
                        "policy_id": metadata.get("policy_id", file_path.stem),
                        "chunk_id": f"{file_path.stem}-{md_chunk.metadata.get('section', 'main')}"
                    }
                })
        
        return chunks

    def _process_pdf(self, file_path: Path) -> List[Dict]:
        """
        /**
         * Processes a PDF file and returns chunks with metadata.
         * Similar to Java's PDFProcessor pattern.
         * 
         * @param file_path: Path object pointing to the PDF file
         * @return: List of dictionaries containing chunks and their metadata
         * 
         * Processing steps:
         * 1. Load PDF using PyPDFLoader
         * 2. Extract text from pages
         * 3. Split into chunks
         * 4. Attach metadata (including page numbers)
         */
        """
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            length_function=len,
        )
        
        chunks = []
        for i, page in enumerate(pages):
            page_chunks = text_splitter.split_text(page.page_content)
            for j, chunk in enumerate(page_chunks):
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "source": file_path.name,
                        "policy_id": file_path.stem,
                        "page": i + 1,
                        "chunk_id": f"{file_path.stem}-p{i+1}-{j}"
                    }
                })
        
        return chunks

    def load(self) -> List[Dict]:
        """Load all policy files and return chunks with metadata."""
        chunks = []
        
        # Process markdown files
        for md_file in self.policies_dir.glob("*.md"):
            chunks.extend(self._process_markdown(md_file))
            
        # Process PDF files
        for pdf_file in self.policies_dir.glob("*.pdf"):
            chunks.extend(self._process_pdf(pdf_file))
            
        return chunks

def load_policy_files(directory: str) -> List[Dict]:
    """
    /**
     * Helper function to load policy files from a directory.
     * This is the main entry point used by the ingest script.
     * 
     * @param directory: Path to the directory containing policy files
     * @return: List of document chunks with metadata
     */
    """
    loader = PolicyLoader(directory)
    return loader.load()
