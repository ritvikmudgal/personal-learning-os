import React, { useState, useEffect, useRef } from "react";

const API_BASE = "http://127.0.0.1:8000/api";

interface Material {
  id: number;
  learner_id: number;
  title: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  mime_type: string;
  ingestion_status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  error_message?: string;
  page_count?: number;
  total_chunks: number;
  uploaded_at: string;
  processed_at?: string;
}

interface Chunk {
  id: number;
  material_id: number;
  chunk_index: number;
  content: string;
  clean_content: string;
  page_number?: number;
  section_header?: string;
  token_count: number;
  has_embedding: boolean;
}

interface MaterialConcept {
  id: number;
  material_id: number;
  concept_id: number;
  concept_name: string;
  relevance_score: number;
}

interface MaterialDetail extends Material {
  chunks: Chunk[];
  associated_concepts: MaterialConcept[];
}

interface SearchResult {
  chunk_id: number;
  material_id: number;
  material_title: string;
  chunk_index: number;
  content: string;
  clean_content: string;
  page_number?: number;
  section_header?: string;
  similarity_score: number;
}

export const LibraryView: React.FC = () => {
  const [activeLearnerId, setActiveLearnerId] = useState<number | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // Inspection & search state
  const [selectedMaterial, setSelectedMaterial] = useState<MaterialDetail | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch material list for current active learner
  const fetchMaterials = async (learnerId?: number) => {
    const idToUse = learnerId ?? activeLearnerId;
    if (!idToUse) return;

    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/library/materials?learner_id=${idToUse}`);
      if (res.ok) {
        const data = await res.json();
        setMaterials(data);
      }
    } catch (err) {
      console.error("Failed to load materials:", err);
    } finally {
      setLoading(false);
    }
  };

  // Resolve active learner on mount
  useEffect(() => {
    const initActiveLearner = async () => {
      try {
        const res = await fetch(`${API_BASE}/learner/active`);
        if (res.ok) {
          const learner = await res.json();
          setActiveLearnerId(learner.id);
          await fetchMaterials(learner.id);
        } else {
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch active learner profile:", err);
        setLoading(false);
      }
    };
    initActiveLearner();
  }, []);

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!activeLearnerId) {
      setUploadError("Active learner profile is not ready.");
      return;
    }

    setUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("learner_id", String(activeLearnerId));

    try {
      const res = await fetch(`${API_BASE}/library/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Upload failed.");
      }

      await fetchMaterials(activeLearnerId);
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload file.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // Inspect material details
  const handleInspect = async (materialId: number) => {
    if (selectedMaterial?.id === materialId) {
      setSelectedMaterial(null);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/library/materials/${materialId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedMaterial(data);
      }
    } catch (err) {
      console.error("Failed to fetch material details:", err);
    }
  };

  // Delete material
  const handleDelete = async (materialId: number) => {
    if (!window.confirm("Are you sure you want to delete this material and its vectors?")) {
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/library/materials/${materialId}`, {
        method: "DELETE",
      });
      if (res.ok || res.status === 204) {
        if (selectedMaterial?.id === materialId) {
          setSelectedMaterial(null);
        }
        await fetchMaterials(activeLearnerId ?? undefined);
      }
    } catch (err) {
      console.error("Failed to delete material:", err);
    }
  };

  // Perform semantic search
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || !activeLearnerId) {
      setSearchResults([]);
      return;
    }

    try {
      setIsSearching(true);
      const res = await fetch(`${API_BASE}/library/search?learner_id=${activeLearnerId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, top_k: 5 }),
      });

      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    } catch (err) {
      console.error("Semantic search failed:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "pixel-badge pixel-badge-ok";
      case "PROCESSING":
        return "pixel-badge pixel-badge-warning";
      case "FAILED":
        return "pixel-badge pixel-badge-error";
      default:
        return "pixel-badge pixel-badge-neutral";
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case "pdf": return "📕";
      case "md": return "📝";
      default: return "📄";
    }
  };

  return (
    <div className="space-y-5">
      {/* Header & Upload */}
      <div
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 rounded-lg gap-4"
        style={{
          backgroundColor: "var(--accent-plum-bg)",
          border: "1.5px solid var(--accent-plum)",
        }}
      >
        <div>
          <h2
            className="text-base font-pixel-heading flex items-center gap-2 mb-1"
            style={{ color: "var(--window-text-primary)" }}
          >
            <span>📚</span> Archive Library
          </h2>
          <p className="text-sm" style={{ color: "var(--window-text-muted)" }}>
            Upload study materials. Documents are chunked, vectorized, and linked to your concept graph.
          </p>
        </div>

        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.txt,.md"
            className="hidden"
            id="library-file-input"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="pixel-button pixel-button-primary flex items-center gap-2 whitespace-nowrap"
          >
            {uploading ? (
              <>
                <span className="animate-pulse">⏳</span> Ingesting...
              </>
            ) : (
              <>
                <span>+</span> Upload Document
              </>
            )}
          </button>
        </div>
      </div>

      {uploadError && (
        <div
          className="p-4 rounded-lg text-sm flex items-center gap-2"
          style={{
            backgroundColor: "var(--status-error-bg)",
            border: "1px solid var(--status-error)",
            color: "var(--accent-coral)",
          }}
        >
          <span>⚠️</span> {uploadError}
        </div>
      )}

      {/* Semantic Search */}
      <div
        className="p-5 rounded-lg space-y-4"
        style={{
          backgroundColor: "var(--window-card)",
          border: "1.5px solid var(--window-border-light)",
        }}
      >
        <form onSubmit={handleSearch} className="flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search your library — e.g. 'vector spaces', 'neural networks'..."
            className="pixel-input"
            style={{ flex: 1 }}
          />
          <button
            type="submit"
            disabled={isSearching}
            className="pixel-button whitespace-nowrap"
          >
            {isSearching ? "Searching..." : "🔍 Search"}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div className="space-y-3 pt-3" style={{ borderTop: "1px solid var(--window-border-light)" }}>
            <div className="text-xs font-pixel-heading" style={{ color: "var(--accent-plum)" }}>
              Found {searchResults.length} relevant passages
            </div>
            {searchResults.map((res, i) => (
              <div
                key={i}
                className="p-4 rounded-lg space-y-2"
                style={{
                  backgroundColor: "var(--window-bg)",
                  border: "1px solid var(--window-border-light)",
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium" style={{ color: "var(--accent-plum)" }}>
                    📖 {res.material_title}
                    {res.page_number ? ` — Page ${res.page_number}` : ""}
                  </span>
                  <span className="pixel-badge pixel-badge-info">
                    {(res.similarity_score * 100).toFixed(1)}% match
                  </span>
                </div>
                {res.section_header && (
                  <div className="text-xs" style={{ color: "var(--window-text-muted)" }}>
                    Section: {res.section_header}
                  </div>
                )}
                <p
                  className="text-sm leading-relaxed p-3 rounded"
                  style={{
                    color: "var(--window-text-secondary)",
                    backgroundColor: "var(--window-bg-subtle)",
                    border: "1px solid var(--window-border-light)",
                    fontStyle: "italic",
                  }}
                >
                  "{res.clean_content}"
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Material List */}
      <div className="space-y-3">
        <div
          className="text-sm font-pixel-heading px-1"
          style={{ color: "var(--window-text-muted)" }}
        >
          Documents ({materials.length})
        </div>

        {loading ? (
          <div className="pixel-empty-state" style={{ padding: "40px" }}>
            <div className="pixel-empty-state-icon">📚</div>
            <div className="pixel-empty-state-desc">Loading archive...</div>
          </div>
        ) : materials.length === 0 ? (
          <div className="pixel-empty-state">
            <div className="pixel-empty-state-icon">📖</div>
            <div className="pixel-empty-state-title">Your archive is empty</div>
            <div className="pixel-empty-state-desc">
              Upload PDF, TXT, or Markdown files to build your personal knowledge library.
            </div>
          </div>
        ) : (
          materials.map((item) => (
            <div key={item.id} className="space-y-2">
              {/* Document Card */}
              <div
                className="p-4 rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-all cursor-pointer"
                style={{
                  backgroundColor:
                    selectedMaterial?.id === item.id
                      ? "var(--accent-plum-bg)"
                      : "var(--window-card)",
                  border: `1.5px solid ${
                    selectedMaterial?.id === item.id
                      ? "var(--accent-plum)"
                      : "var(--window-border-light)"
                  }`,
                }}
                onClick={() => handleInspect(item.id)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getFileIcon(item.file_type)}</span>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium" style={{ color: "var(--window-text-primary)" }}>
                        {item.title}
                      </span>
                      <span className={getStatusBadge(item.ingestion_status)}>
                        {item.ingestion_status}
                      </span>
                    </div>
                    <div className="text-xs" style={{ color: "var(--window-text-muted)" }}>
                      {item.file_type.toUpperCase()} · {formatBytes(item.file_size_bytes)} · {item.total_chunks} chunks
                      {item.page_count ? ` · ${item.page_count} pages` : ""}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleInspect(item.id); }}
                    className="pixel-button text-xs"
                  >
                    {selectedMaterial?.id === item.id ? "Close" : "Inspect"}
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                    className="pixel-button text-xs"
                    style={{ color: "var(--accent-coral)" }}
                  >
                    🗑
                  </button>
                </div>
              </div>

              {/* Inspection Drawer */}
              {selectedMaterial?.id === item.id && (
                <div
                  className="p-5 rounded-lg space-y-5 ml-4 animate-fade-in"
                  style={{
                    backgroundColor: "var(--window-bg)",
                    border: "1.5px solid var(--accent-plum)",
                    borderLeft: "4px solid var(--accent-plum)",
                  }}
                >
                  {/* Associated Concepts */}
                  <div>
                    <h4
                      className="text-sm font-pixel-heading mb-3 flex items-center gap-2"
                      style={{ color: "var(--accent-plum)" }}
                    >
                      <span>🏷️</span> Linked Concepts ({selectedMaterial.associated_concepts.length})
                    </h4>
                    {selectedMaterial.associated_concepts.length === 0 ? (
                      <p className="text-sm italic" style={{ color: "var(--window-text-faint)" }}>
                        No concepts extracted yet.
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {selectedMaterial.associated_concepts.map((c) => (
                          <span
                            key={c.id}
                            className="pixel-badge pixel-badge-info"
                          >
                            {c.concept_name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Chunks Preview */}
                  <div>
                    <h4
                      className="text-sm font-pixel-heading mb-3 flex items-center gap-2"
                      style={{ color: "var(--accent-plum)" }}
                    >
                      <span>📄</span> Document Sections ({selectedMaterial.chunks.length})
                    </h4>
                    <div className="max-h-64 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                      {selectedMaterial.chunks.map((ch) => (
                        <div
                          key={ch.id}
                          className="p-3 rounded-lg space-y-1.5"
                          style={{
                            backgroundColor: "var(--window-card)",
                            border: "1px solid var(--window-border-light)",
                          }}
                        >
                          <div className="flex items-center justify-between text-xs">
                            <span style={{ color: "var(--window-text-muted)" }}>
                              Section {ch.chunk_index + 1}
                              {ch.page_number ? ` · Page ${ch.page_number}` : ""}
                            </span>
                            <span className="text-xs" style={{ color: "var(--window-text-faint)" }}>
                              {ch.token_count} tokens
                              {ch.has_embedding && (
                                <span style={{ color: "var(--status-ok)" }}> · ✓ Vectorized</span>
                              )}
                            </span>
                          </div>
                          {ch.section_header && (
                            <div
                              className="text-xs font-medium"
                              style={{ color: "var(--accent-plum)" }}
                            >
                              {ch.section_header}
                            </div>
                          )}
                          <p
                            className="text-sm leading-relaxed line-clamp-3"
                            style={{ color: "var(--window-text-secondary)" }}
                          >
                            {ch.clean_content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
