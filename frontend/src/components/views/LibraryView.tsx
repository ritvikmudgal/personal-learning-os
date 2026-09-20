import React, { useState, useEffect, useRef } from "react";
import {
  LibraryIcon,
  UploadIcon,
  SearchIcon,
  BookOpenIcon,
  TrashIcon,
  SparklesIcon,
} from "../WorldIcons";

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

  return (
    <div className="space-y-6">
      {/* Top Banner & Upload Control */}
      <div className="world-panel p-5 bg-gradient-to-r from-amber-50/90 via-amber-100/40 to-amber-50/90 border-l-4 border-l-amber-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-900 mb-1">
            <LibraryIcon size={18} />
            <h2 className="text-base font-heading font-bold text-slate-900">
              Archive Library & Knowledge Vault
            </h2>
          </div>
          <p className="text-xs text-slate-600 font-body max-w-xl">
            Upload PDFs, Markdown files, or study notes. Documents are chunked, vectorized, and linked to your concept graph.
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
            className="world-button world-button-primary px-4 py-2.5 shadow-xs"
          >
            <UploadIcon size={16} />
            <span>{uploading ? "Ingesting..." : "Upload Document"}</span>
          </button>
        </div>
      </div>

      {uploadError && (
        <div className="world-panel p-4 bg-red-50 text-red-800 border-red-200 text-xs font-body">
          ⚠️ {uploadError}
        </div>
      )}

      {/* Semantic Search Bar */}
      <form onSubmit={handleSearch} className="world-panel p-3 bg-white flex items-center gap-2">
        <SearchIcon size={18} className="text-slate-400 ml-2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Semantic Search across all library chunks..."
          className="flex-1 bg-transparent border-none outline-none text-sm text-slate-800 font-body placeholder:italic placeholder:text-slate-400"
        />
        <button
          type="submit"
          disabled={isSearching || !searchQuery.trim()}
          className="world-button world-button-warm px-4 py-1.5 text-xs font-medium"
        >
          <span>{isSearching ? "Searching..." : "Search"}</span>
        </button>
      </form>

      {/* Semantic Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-heading font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-2">
            <SparklesIcon size={14} className="text-amber-600" />
            <span>Semantic Search Results ({searchResults.length})</span>
          </h3>

          <div className="space-y-2">
            {searchResults.map((res, idx) => (
              <div key={idx} className="world-panel p-4 bg-white border-l-4 border-l-amber-600 space-y-2">
                <div className="flex items-center justify-between text-xs font-heading">
                  <span className="font-semibold text-slate-800">{res.material_title} (Chunk #{res.chunk_index})</span>
                  <span className="world-badge world-badge-neutral text-[11px]">
                    Score: {(res.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-xs font-body text-slate-700 leading-relaxed bg-amber-50/50 p-2.5 rounded-md border border-amber-100">
                  {res.clean_content}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Material Grid / Document Cards */}
      <div className="space-y-3">
        <h3 className="text-xs font-heading font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-2">
          <BookOpenIcon size={14} className="text-emerald-700" />
          <span>Library Documents ({materials.length})</span>
        </h3>

        {loading ? (
          <div className="world-panel p-8 text-center text-xs text-slate-500 font-body">
            Loading archive documents...
          </div>
        ) : materials.length === 0 ? (
          <div className="world-empty-state">
            <LibraryIcon size={36} className="world-empty-state-icon" />
            <h4 className="world-empty-state-title">No documents in archive</h4>
            <p className="world-empty-state-desc">
              Upload study PDFs or markdown files to populate your knowledge vault.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {materials.map((mat) => {
              const isSelected = selectedMaterial?.id === mat.id;

              return (
                <div
                  key={mat.id}
                  className={`world-panel p-4 bg-white transition-all duration-150 ${
                    isSelected ? "border-amber-600 ring-2 ring-amber-600/10 shadow-md" : "hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-amber-100/80 text-amber-800 flex items-center justify-center font-heading text-xs font-bold uppercase">
                        {mat.file_type || "doc"}
                      </div>
                      <div>
                        <h4 className="text-sm font-heading font-semibold text-slate-900 line-clamp-1">
                          {mat.title}
                        </h4>
                        <p className="text-[11px] text-slate-500 font-body">
                          {formatBytes(mat.file_size_bytes)} • {mat.total_chunks} chunks
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleInspect(mat.id)}
                        className="world-button text-xs px-2.5 py-1"
                      >
                        {isSelected ? "Hide" : "Inspect"}
                      </button>
                      <button
                        onClick={() => handleDelete(mat.id)}
                        className="p-1.5 text-slate-400 hover:text-red-700 rounded-md transition-colors"
                        title="Delete material"
                      >
                        <TrashIcon size={16} />
                      </button>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center justify-between text-xs mt-3 pt-2.5 border-t border-slate-100">
                    <span className="world-badge world-badge-ok text-[11px]">
                      {mat.ingestion_status}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {new Date(mat.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Expanded Inspection Drawer */}
                  {isSelected && selectedMaterial && (
                    <div className="mt-4 pt-4 border-t border-slate-200 space-y-3 animate-fade-in">
                      <h5 className="text-xs font-heading font-semibold text-slate-800 flex items-center gap-1.5">
                        <SparklesIcon size={14} className="text-amber-600" />
                        <span>Extracted Chunks ({selectedMaterial.chunks.length})</span>
                      </h5>

                      <div className="max-h-48 overflow-y-auto space-y-2 custom-scrollbar">
                        {selectedMaterial.chunks.map((chk) => (
                          <div key={chk.id} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs font-body space-y-1">
                            <div className="font-semibold text-slate-700">Chunk #{chk.chunk_index} ({chk.token_count} tokens)</div>
                            <p className="text-slate-600 leading-relaxed line-clamp-3">{chk.clean_content}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
