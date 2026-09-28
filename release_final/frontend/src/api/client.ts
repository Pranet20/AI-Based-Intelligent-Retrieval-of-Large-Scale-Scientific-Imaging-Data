import {
  Project,
  ScientificImage,
  ReviewItem,
  SearchResult,
  ModelVersion,
  SystemHealth,
  User,
} from "../types";

const API_BASE = process.env.REACT_APP_API_URL || "/api/v1";

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

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `API request failed with status ${response.status}`);
    }

    return response.json();
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
  public static async login(formData: FormData): Promise<{ access_token: string; token_type: string }> {
    const res = await this.request<{ access_token: string; token_type: string }>("/auth/token", {
      method: "POST",
      body: formData,
    });
    this.setToken(res.access_token);
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
  public static async searchByVector(queryImageId: number, topK: number = 10, modality?: string): Promise<SearchResult[]> {
    return this.request<SearchResult[]>("/search/vector", {
      method: "POST",
      body: JSON.stringify({ query_image_id: queryImageId, top_k: topK, modality_filter: modality }),
    });
  }

  public static async searchHybrid(queryImageId: number, metadataQuery: Record<string, any>, topK: number = 10): Promise<SearchResult[]> {
    return this.request<SearchResult[]>("/search/hybrid", {
      method: "POST",
      body: JSON.stringify({ query_image_id: queryImageId, metadata_query: metadataQuery, top_k: topK }),
    });
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

  // Provenance & Audit
  public static async getProvenance(imageId: number): Promise<any[]> {
    return this.request<any[]>(`/provenance/image/${imageId}`);
  }

  public static async getAuditLogs(limit: number = 50): Promise<any[]> {
    return this.request<any[]>(`/admin/audit-logs?limit=${limit}`);
  }
}
