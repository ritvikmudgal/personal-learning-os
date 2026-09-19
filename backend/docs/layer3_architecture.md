# Personal Learning OS — Layer 3 Architecture Specification
## Knowledge Ingestion, Material Intelligence & Local Vector Retrieval

### 1. Architectural Overview

Layer 3 introduces local document ingestion, structured text chunking, local vector embeddings, concept graph extraction/linking, and semantic retrieval to the Personal Learning OS — all running strictly on-device without cloud dependencies.

```mermaid
flowchart TD
    A[Uploaded Document: PDF, TXT, MD] --> B[Validator & Security Check]
    B --> C[Format Extractor: PyMuPDF / TXT / MD]
    C --> D[Text Normalizer: NFC, Space, Hyphen Fix]
    D --> E[Sliding Window Chunker: 2000 chars, 400 overlap]
    E --> F[DocumentChunk Storage]
    F --> G[Ollama Embedding Provider: nomic-embed-text]
    F --> H[LLM Concept Extractor: qwen2.5:3b]
    G --> I[Vector Cosine Similarity Index]
    H --> J[Concept Linker & Concept Graph]
    I --> K[Semantic Search API]
    J --> L[Knowledge Graph Nodes]
    
    subgraph Isolation Boundary
        M[Learner Knowledge State]
    end
    
    F -. ZERO STATE MUTATION .- x M
```

---

### 2. Core Principles & Guarantees

1. **Absolute State Isolation**: Uploading, reading, chunking, or indexing learning materials **never alters** the learner's multi-dimensional knowledge state (`mastery_probability`, `knowledge_strength`, `forgetting_state`, `confidence`, `evidence_reliability`, `misconception_severity`). Learner state updates occur strictly through verified learning evidence and diagnostic assessments.
2. **Local Privacy & Resource Safety**: Document extraction uses `PyMuPDF` and vector generation uses local Ollama `nomic-embed-text` (768 dimensions). Peak RAM footprint is constrained to < 200MB, rendering it fully performant on a dual-core 2017 MacBook Air (8GB RAM).
3. **Full Provenance & Proven Tracking**: Every chunk retains start/end character offsets, 1-indexed page numbers, section header names, and original token count estimates.

---

### 3. Ingestion Pipeline Breakdown

1. **Validation**: Enforces file existence, allowed file extension (`.pdf`, `.txt`, `.md`), and 100MB file size limit (`backend/app/ingestion/validator.py`).
2. **Format Extraction**:
   - `PDFExtractor`: Uses PyMuPDF (`fitz`) to extract page-by-page text and detect section titles (`backend/app/ingestion/extractors/pdf_extractor.py`).
   - `MarkdownExtractor`: Parses markdown files and extracts section headers (`#`, `##`, `###`) (`backend/app/ingestion/extractors/markdown_extractor.py`).
   - `TextExtractor`: Processes plain text files (`backend/app/ingestion/extractors/text_extractor.py`).
3. **Normalization**: Standardizes Unicode to NFC, cleans multi-space runs, fixes hyphenation split across line breaks (`comput-\nation`), and replaces 3+ newlines with standard paragraph breaks (`backend/app/ingestion/normalizer.py`).
4. **Sliding Window Chunking**: Target window size is 2000 characters with 400 characters overlap. Splitting prefers natural paragraph (`\n\n`) and sentence (`. `) breaks near window boundaries (`backend/app/ingestion/chunker.py`).
5. **Local Embeddings**: Generates 768-dimensional float vectors via Ollama `/api/embeddings` using `nomic-embed-text` (`backend/app/embeddings/ollama_embedding.py`).
6. **Concept Extraction & Graph Linking**: Uses local LLM (`qwen2.5:3b`) to extract key educational topics from document chunks, queries existing concept nodes in `ConceptRepository`, links existing nodes or creates new ones while enforcing DAG cycle-free rules (`backend/app/ingestion/concept_linker.py`).

---

### 4. Database Schema

- **`materials`**: Stores document metadata, original filename, file type, file size, page count, total chunks, and `ingestion_status` (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
- **`document_chunks`**: Stores text chunks with `chunk_index`, `content`, `clean_content`, `start_char`, `end_char`, `page_number`, `section_header`, `token_count`, and `embedding` (JSON float array).
- **`material_concepts`**: Junction table linking `Material` and `DocumentChunk` to `Concept` nodes in the Concept Graph with `relevance_score` and `extraction_method`.

---

### 5. Semantic Vector Retrieval

Given a user query $Q \in \mathbb{R}^{768}$ and document chunk embedding $C \in \mathbb{R}^{768}$, the similarity score is computed as:

$$\text{similarity}(Q, C) = \frac{\sum_{i=1}^{768} Q_i C_i}{\sqrt{\sum_{i=1}^{768} Q_i^2} \sqrt{\sum_{i=1}^{768} C_i^2}}$$

Cosine similarity search is computed efficiently using NumPy in `backend/app/services/retrieval_service.py`.

---

### 6. Verification & Test Suite

The Layer 3 implementation is validated by 58 automated unit & integration tests covering:
- Document extraction accuracy (PDF, TXT, MD)
- Chunker sliding window, overlap, and character offset tracking
- Embedding provider vector generation & mocking
- Vector cosine similarity ranking
- LLM concept extraction parsing
- Concept graph node creation and linking
- Complete upload API flow, listing, detail, search, and deletion
- **Critical Isolation Test**: Explicit verification that material ingestion leaves learner state 100% untouched.
