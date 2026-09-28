import { Project, ScientificImage, ReviewItem, SearchResult, ModelVersion, SystemHealth, User } from "../types";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

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

  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
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
      throw new Error(err.detail || "API Request Failed");
    }

    return response.json();
  }

  // Health
  public static async getHealth(): Promise<SystemHealth> {
    return this.request<SystemHealth>("/health");
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
  public static async getImages(projectId?: number): Promise<ScientificImage[]> {
    const query = projectId ? `?project_id=${projectId}` : "";
    return this.request<ScientificImage[]>(`/images${query}`);
  }

  public static async getImage(id: number): Promise<ScientificImage> {
    return this.request<ScientificImage>(`/images/${id}`);
  }

  public static async uploadImage(formData: FormData): Promise<ScientificImage> {
    return this.request<ScientificImage>("/images/upload", {
      method: "POST",
      body: formData,
    });
  }

  // Search
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

  // Curation & Reviews
  public static async getReviewQueue(status: string = "PENDING"): Promise<ReviewItem[]> {
    return this.request<ReviewItem[]>(`/curation/reviews?status=${status}`);
  }

  public static async reviewAction(reviewId: number, action: "APPROVE" | "REJECT" | "QUARANTINE", notes: string): Promise<ReviewItem> {
    return this.request<ReviewItem>(`/curation/reviews/${reviewId}/action`, {
      method: "POST",
      body: JSON.stringify({ action, notes }),
    });
  }

  // Models
  public static async getModels(): Promise<ModelVersion[]> {
    return this.request<ModelVersion[]>("/models");
  }

  // Provenance
  public static async getProvenance(imageId: number): Promise<any[]> {
    return this.request<any[]>(`/provenance/image/${imageId}`);
  }
}
