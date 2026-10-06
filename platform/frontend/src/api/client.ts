import {
  Project,
  ScientificImage,
  ReviewItem,
  SearchResult,
  ModelVersion,
  SystemHealth,
  User,
} from "../types";

const getApiBase = (): string => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname || "127.0.0.1";
    const port = window.location.port;
    if (port === "3000" || host === "localhost" || host === "127.0.0.1") {
      return `http://${host}:8000/api/v1`;
    }
  }
  return "/api/v1";
};

const API_BASE = getApiBase();

export interface ReviewQueueItem {
  image_id: number;
  original_filename: string;
  duplicate_status: string;
  composite_quality_risk: number;
  quality_label: string;
  novelty_score: number;
  novelty_percentile: number;
  priority: number;
  algorithmic_recommendation: string;
  microscope?: string;
}

export interface ReviewSubmission {
  image_id: number;
  decision: "KEEP" | "REVIEW_LATER" | "DUPLICATE" | "LOW_QUALITY" | "INTERESTING_NOVEL" | "INCORRECT_METADATA";
  comment?: string;
}

export interface DashboardStats {
  total_images: number;
  total_projects: number;
  potential_redundancies: number;
  quality_risk_items: number;
  pending_reviews: number;
  completed_reviews: number;
  faiss_indexed_vectors: number;
  timestamp: string;
}

export interface ResearchDashboardData {
  status: string;
  dataset_inventory: {
    hcci_physical_micrographs: number;
    carinthia_physical_images: number;
    sem_nanoscience_records: number;
    source_artifact: string;
  };
  acquisition_distributions: {
    detectors: Record<string, number>;
    accelerating_voltages: Record<string, number>;
    source_artifact: string;
  };
  data_integrity_and_quality: {
    nominal_images: number;
    risk_flagged_images: number;
    defocus_auroc: number;
    defocus_auprc: number;
    source_artifact: string;
  };
  scientific_retrieval_benchmarks: {
    dinov2_vit_s14_r1: number;
    resnet50_baseline_r1: number;
    acquisition_gap_reduction_pct: number;
    gap_reduction_p_value: number;
    authoritative_metadata_mrr: number;
    faiss_hnsw_latency_ms: number;
    source_artifact: string;
  };
  active_curation_progress: {
    pending_in_queue: number;
    completed_decisions: number;
    workload_reduction_pct: number;
    inter_rater_kappa: number;
    source_artifact: string;
  };
  experiment_registry_v2: {
    registered_experiments_count: number;
    canonical_experiments: any[];
    source_artifact: string;
  };
}

export interface ImageDetailResponse {
  id: number;
  project_id: number;
  original_filename: string;
  storage_path: string;
  thumbnail_path: string;
  sha256: string;
  mime_type: string;
  width: number;
  height: number;
  file_size: number;
  processing_status: string;
  created_at: string;
  metadata?: {
    microscope?: string;
    detector?: string;
    accelerating_voltage_kv?: number;
    magnification?: number;
    pixel_size_nm?: number;
    beam_current_na?: number;
    dwell_time_us?: number;
    working_distance_mm?: number;
    chamber_pressure_pa?: number;
    metadata_source?: string;
    metadata_completeness?: number;
  };
  quality?: {
    laplacian_variance?: number;
    edge_density?: number;
    shannon_entropy?: number;
    dynamic_range?: number;
    clipping_ratio?: number;
    high_freq_fft_ratio?: number;
    composite_quality_risk: number;
    quality_label: string;
  };
  duplicate?: {
    duplicate_status: string;
    matched_image_id?: number;
    similarity_score?: number;
    match_stage?: string;
  };
}

export interface BoundingBoxInfo {
  y_min: number;
  x_min: number;
  y_max: number;
  x_max: number;
  area_pixels: number;
}

export interface LocalizationResponse {
  image_id: number;
  region_type: string;
  saliency_threshold: number;
  area_fraction: number;
  centroid_normalized: [number, number];
  mean_saliency_in_mask: number;
  bounding_boxes: BoundingBoxInfo[];
  mask_storage_path?: string;
  error?: string;
}

export interface ComparableEvidenceItem {
  image_id: string;
  role: string;
  similarity_score: number;
  specimen_id?: string;
  acquisition_id?: string;
  instrument?: string;
  detector?: string;
  accelerating_voltage_kv?: number;
  file_path?: string;
  provenance_hash?: string;
}

export interface SuggestedActionInfo {
  action_code: string;
  recommendation_summary: string;
  operational_parameter_targets: string[];
  scientific_rationale: string;
  requires_operator_intervention: boolean;
}

export interface QualityRiskSignalInfo {
  indicator_name: string;
  measured_value: number;
  threshold_applied: number;
  is_risk_flagged: boolean;
  evaluation_criteria: string;
  method_provenance: string;
}

export interface EvidenceRecordResponse {
  query_image_id: string;
  decision_status: "ACCEPT" | "QUALITY_RISK" | "UNCERTAIN_ABSTAIN";
  primary_artifact_category: string;
  classification_confidence: number;
  normalized_entropy: number;
  prediction_margin: number;
  abstention_triggered: boolean;
  abstention_reason?: string;
  quality_signals: QualityRiskSignalInfo[];
  suspicious_region?: LocalizationResponse;
  acquisition_context: {
    instrument?: string;
    detector?: string;
    accelerating_voltage_kv?: number;
    magnification?: number;
    working_distance_mm?: number;
    specimen_id?: string;
    acquisition_id?: string;
    data_source: string;
    metadata_provenance_hash?: string;
  };
  comparable_evidence: ComparableEvidenceItem[];
  suggested_action: SuggestedActionInfo;
  timestamp_utc: string;
  pipeline_version: string;
  audit_hash?: string;
}

export interface ExplanationResponse {
  image_id: number;
  decision_status: "ACCEPT" | "QUALITY_RISK" | "UNCERTAIN_ABSTAIN";
  primary_artifact_category: string;
  classification_confidence: number;
  normalized_entropy: number;
  prediction_margin: number;
  abstention_triggered: boolean;
  abstention_reason?: string;
  suggested_action: SuggestedActionInfo;
  acquisition_context: any;
  audit_hash?: string;
  quality_signals: QualityRiskSignalInfo[];
}

export interface MultiImagePairwiseComparison {
  pair_key: string;
  image_a: { id: number; filename: string };
  image_b: { id: number; filename: string };
  similarity_score: number;
  similarity_pct: number;
  representation: string;
  decision: "DUPLICATE" | "NEAR_DUPLICATE" | "SIMILAR" | "DISTINCT";
  reason: string;
  cascade_evidence: {
    file_sha_match: boolean;
    pixel_sha_match: boolean;
    phash_hamming: number;
    dhash_hamming: number;
    cosine_similarity: number;
    ssim: number | null;
    mae: number | null;
    ncc: number | null;
  };
  metadata_relationship: {
    same_specimen: boolean | null;
    same_acquisition: boolean | null;
    same_instrument: boolean | null;
    same_detector: boolean | null;
    same_voltage: boolean | null;
    same_magnification: boolean | null;
  };
  comparative_quality: {
    image_a_status: string;
    image_b_status: string;
    cleaner_reference_id: number | null;
    comparative_rationale: string;
    suggested_comparative_action: string;
  };
}

export interface MultiImageDuplicateGroup {
  group_id: string;
  representative_image_id: number;
  representative_filename: string;
  member_image_ids: number[];
  member_filenames: string[];
  reason: string;
  advisory: string;
  actions: string[];
}

export interface MultiImagePerImageResult {
  id: number;
  original_filename: string;
  sha256: string;
  width: number;
  height: number;
  file_size: number;
  storage_path: string;
  metadata?: any;
  quality: {
    decision_status: "NORMAL" | "QUALITY_RISK" | "UNCERTAIN_ABSTAIN";
    primary_artifact_category: string;
    composite_quality_risk: number;
    confidence: number;
    normalized_entropy: number;
    prediction_margin: number;
    abstention_triggered: boolean;
    abstention_reason?: string;
    indicators: QualityRiskSignalInfo[];
  };
  localization: LocalizationResponse;
  evidence: {
    comparable_items: ComparableEvidenceItem[];
    cohort_size: number;
    audit_hash?: string;
  };
  explanation: SuggestedActionInfo;
}

export interface MultiImageAnalysisResponse {
  analysis_id: string;
  timestamp_utc: string;
  representation: string;
  total_images: number;
  total_pairs: number;
  summary: {
    images_analyzed: number;
    pairwise_comparisons: number;
    duplicate_pairs: number;
    near_duplicate_pairs: number;
    similar_pairs: number;
    distinct_pairs: number;
    quality_risk_images: number;
    uncertain_images: number;
    review_required_images: number;
  };
  images: MultiImagePerImageResult[];
  similarity_matrix: {
    image_ids: number[];
    image_labels: string[];
    matrix: number[][];
  };
  pairwise_comparisons: MultiImagePairwiseComparison[];
  duplicate_groups: MultiImageDuplicateGroup[];
  comparative_quality_summary: {
    highest_risk_image_id: number;
    highest_risk_score: number;
    comparative_statement: string;
    ranking: { image_id: number; filename: string; composite_risk: number; status: string }[];
  };
  provenance: {
    analysis_id: string;
    input_image_ids: number[];
    representation: string;
    model_version: string;
    timestamp_utc: string;
    stages_executed: string[];
    audit_hash: string;
  };
}


export class ApiClient {
  private static token: string | null = localStorage.getItem("scidata_token");

  public static setToken(token: string) {
    this.token = token;
    localStorage.setItem("scidata_token", token);
  }

  public static clearToken() {
    this.token = null;
    localStorage.removeItem("scidata_token");
  }

  public static getToken(): string | null {
    return this.token || localStorage.getItem("scidata_token");
  }

  public static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    let response: Response;
    try {
      response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });
    } catch (networkErr: any) {
      // Auto-fallback: try alternate local host (localhost <-> 127.0.0.1) or relative path
      const altBase = API_BASE.includes("127.0.0.1")
        ? API_BASE.replace("127.0.0.1", "localhost")
        : API_BASE.includes("localhost")
        ? API_BASE.replace("localhost", "127.0.0.1")
        : "/api/v1";
      try {
        response = await fetch(`${altBase}${endpoint}`, {
          ...options,
          headers,
        });
      } catch (fallbackErr: any) {
        throw new Error(`Cannot connect to SciData backend at ${API_BASE}. Please ensure the backend server is running.`);
      }
    }

    const contentType = response.headers.get("content-type") || "";
    let data: any;
    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${text.slice(0, 120)}`);
      }
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
    }

    if (!response.ok) {
      const msg = typeof data === "object" && data?.detail ? data.detail : `API request failed with status ${response.status}`;
      throw new Error(msg);
    }

    return data as T;
  }

  // Health & System
  public static async getHealth(): Promise<SystemHealth> {
    return this.request<SystemHealth>("/health");
  }

  public static async getReadiness(): Promise<{ status: string; checks: Record<string, string>; version: string }> {
    return this.request<{ status: string; checks: Record<string, string>; version: string }>("/readiness");
  }

  public static async getVersion(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>("/version");
  }

  public static async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>("/dashboard/stats");
  }

  public static async getResearchDashboard(): Promise<ResearchDashboardData> {
    return this.request<ResearchDashboardData>("/research/dashboard");
  }

  // Auth
  public static async login(formData: FormData): Promise<{ access_token: string; token_type: string; role?: string; username?: string }> {
    const res = await this.request<{ access_token: string; token_type: string; role?: string; username?: string }>("/auth/login", {
      method: "POST",
      body: formData,
    });
    if (res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  }

  public static async register(data: {
    username: string;
    email: string;
    password: string;
    role?: string;
  }): Promise<{ access_token: string; token_type: string; role?: string; username?: string }> {
    const res = await this.request<{ access_token: string; token_type: string; role?: string; username?: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  }

  public static async getCurrentUser(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Projects
  public static async getProjects(): Promise<Project[]> {
    return this.request<Project[]>("/projects");
  }

  public static async getProject(id: number): Promise<Project> {
    return this.request<Project>(`/projects/${id}`);
  }

  public static async createProject(data: { name: string; description?: string }): Promise<Project> {
    return this.request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Images
  public static async getImages(
    projectId?: number,
    status?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ total: number; items: any[] }> {
    const params = new URLSearchParams();
    if (projectId) params.append("project_id", projectId.toString());
    if (status) params.append("status", status);
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    return this.request<{ total: number; items: any[] }>(`/images?${params.toString()}`);
  }

  public static async getImage(id: number): Promise<ImageDetailResponse> {
    return this.request<ImageDetailResponse>(`/images/${id}`);
  }

  public static getImageUrl(id: number): string {
    return `${API_BASE}/images/${id}/file`;
  }

  public static getImageDisplayUrl(id: number): string {
    return `${API_BASE}/images/${id}/file`;
  }

  public static getImageThumbnailUrl(id: number): string {
    return `${API_BASE}/images/${id}/thumbnail`;
  }

  public static async uploadImage(formData: FormData): Promise<any> {
    return this.request<any>("/images/upload", {
      method: "POST",
      body: formData,
    });
  }

  // Vector Search
  public static async searchByVector(queryImageId: number, topK: number = 10, modality?: string, representation: string = "dinov2_base"): Promise<SearchResult[]> {
    const res = await this.request<any>("/search/vector", {
      method: "POST",
      body: JSON.stringify({ query_image_id: queryImageId, top_k: topK, modality_filter: modality, representation }),
    });
    const items = Array.isArray(res) ? res : (res.results || []);
    return items.map((it: any) => ({
      image_id: it.image_id,
      filename: it.original_filename || it.filename,
      similarity: it.similarity_score ?? it.similarity ?? 0,
      modality: it.metadata_summary?.microscope || it.modality || "SEM",
      instrument: it.metadata_summary?.detector || it.instrument,
      quality_risk: it.composite_quality_risk ?? it.quality_risk ?? 0,
      quality_label: it.quality_label || "NOMINAL",
      duplicate_status: it.duplicate_status || "NO_DECLARED_REDUNDANCY_DETECTED",
    }));
  }

  public static async searchHybrid(queryImageId: number, metadataQuery: Record<string, any>, topK: number = 10, representation: string = "dinov2_base"): Promise<SearchResult[]> {
    const res = await this.request<any>("/search/hybrid", {
      method: "POST",
      body: JSON.stringify({ query_image_id: queryImageId, metadata_query: metadataQuery, top_k: topK, representation }),
    });
    const items = Array.isArray(res) ? res : (res.results || []);
    return items.map((it: any) => ({
      image_id: it.image_id,
      filename: it.original_filename || it.filename,
      similarity: it.similarity_score ?? it.similarity ?? 0,
      modality: it.metadata_summary?.microscope || it.modality || "SEM",
      instrument: it.metadata_summary?.detector || it.instrument,
      quality_risk: it.composite_quality_risk ?? it.quality_risk ?? 0,
      quality_label: it.quality_label || "NOMINAL",
      duplicate_status: it.duplicate_status || "NO_DECLARED_REDUNDANCY_DETECTED",
    }));
  }

  // Curation & Workbench
  public static async getReviewQueue(limit: number = 50): Promise<ReviewQueueItem[]> {
    return this.request<ReviewQueueItem[]>(`/curation/review-queue?limit=${limit}`);
  }

  public static async submitReview(submission: ReviewSubmission): Promise<any> {
    return this.request<any>("/curation/reviews", {
      method: "POST",
      body: JSON.stringify(submission),
    });
  }

  public static async getCompletedReviews(limit: number = 50): Promise<any[]> {
    return this.request<any[]>(`/curation/reviews?limit=${limit}`);
  }

  // Models
  public static async getModels(): Promise<ModelVersion[]> {
    return this.request<ModelVersion[]>("/models");
  }

  public static async extractModelFeatures(imageId: number, modelId: string = "dinov2_vits14_phase2"): Promise<any> {
    return this.request<any>("/models/extract-features", {
      method: "POST",
      body: JSON.stringify({ image_id: imageId, model_id: modelId }),
    });
  }

  public static async compareModelFeatures(imageIdA: number, imageIdB: number): Promise<any> {
    return this.request<any>("/models/compare-features", {
      method: "POST",
      body: JSON.stringify({ image_id_a: imageIdA, image_id_b: imageIdB }),
    });
  }

  // Provenance & Audit
  public static async getProvenance(imageId: number): Promise<any[]> {
    return this.request<any[]>(`/provenance/image/${imageId}`);
  }

  public static async getAuditLogs(limit: number = 50): Promise<any[]> {
    return this.request<any[]>(`/admin/audit-logs?limit=${limit}`);
  }

  public static async runSystemDiagnostics(): Promise<any> {
    return this.request<any>("/admin/run-diagnostics", {
      method: "POST",
    });
  }

  // Deep Micrograph Analytics & Scientific Evidence
  public static async getImageAnalysis(id: number): Promise<any> {
    return this.request<any>(`/images/${id}/analysis`);
  }

  public static async getImageLocalization(id: number): Promise<LocalizationResponse> {
    return this.request<LocalizationResponse>(`/images/${id}/localization`);
  }

  public static async getImageEvidence(id: number): Promise<EvidenceRecordResponse> {
    return this.request<EvidenceRecordResponse>(`/images/${id}/evidence`);
  }

  public static async getImageExplanation(id: number): Promise<ExplanationResponse> {
    return this.request<ExplanationResponse>(`/images/${id}/explanation`);
  }

  public static async getSimilarImages(id: number, topK: number = 6): Promise<any[]> {
    return this.request<any[]>(`/images/${id}/similar?top_k=${topK}`);
  }

  // Sample Micrographs
  public static async getAvailableSamples(): Promise<{ samples: { filename: string; channel: string; size_bytes: number; size_mb: number }[] }> {
    return this.request<{ samples: any[] }>("/images/samples/available");
  }

  public static async ingestSample(filename: string, projectId?: number): Promise<ImageDetailResponse & { message?: string }> {
    return this.request<ImageDetailResponse & { message?: string }>("/images/samples/ingest", {
      method: "POST",
      body: JSON.stringify({ filename, project_id: projectId }),
    });
  }

  public static getSampleFileUrl(filename: string): string {
    return `${API_BASE}/images/samples/${encodeURIComponent(filename)}/raw`;
  }

  public static async getSampleBlob(filename: string): Promise<Blob> {
    const primaryUrl = `${API_BASE}/images/samples/${encodeURIComponent(filename)}/raw`;
    try {
      const res = await fetch(primaryUrl);
      if (res.ok) return await res.blob();
    } catch {}
    const altBase = API_BASE.includes("127.0.0.1")
      ? API_BASE.replace("127.0.0.1", "localhost")
      : API_BASE.replace("localhost", "127.0.0.1");
    const altRes = await fetch(`${altBase}/images/samples/${encodeURIComponent(filename)}/raw`);
    if (altRes.ok) return await altRes.blob();
    throw new Error(`Failed to download sample micrograph: ${filename}`);
  }

  public static getImageRawDownloadUrl(id: number): string {
    return `${API_BASE}/images/${id}/file?raw=true`;
  }

  // Multi-Image Analysis & Comparison Workflow
  public static async analyzeMultiImages(formData: FormData): Promise<MultiImageAnalysisResponse> {
    return this.request<MultiImageAnalysisResponse>("/multi-image/analyze", {
      method: "POST",
      body: formData,
    });
  }

  public static async analyzeMultiImagesByIds(imageIds: number[], representation: string = "dinov2_base"): Promise<MultiImageAnalysisResponse> {
    return this.request<MultiImageAnalysisResponse>("/multi-image/analyze", {
      method: "POST",
      body: JSON.stringify({ image_ids: imageIds, representation }),
    });
  }

  public static async submitMultiImageReview(review: {
    image_id: number;
    decision: string;
    comment?: string;
    peer_image_id?: number;
    analysis_id?: string;
  }): Promise<{ status: string; review_id: number; message: string; audit_hash?: string }> {
    return this.request<{ status: string; review_id: number; message: string; audit_hash?: string }>("/multi-image/review", {
      method: "POST",
      body: JSON.stringify(review),
    });
  }
}


