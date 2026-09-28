export type Role = "ADMIN" | "RESEARCHER" | "REVIEWER";

export interface User {
  id: number;
  email: string;
  username: string;
  role: Role;
  institution?: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  image_count: number;
  created_at: string;
}

export interface QualityProfile {
  laplacian_variance: number;
  edge_density: number;
  shannon_entropy: number;
  dynamic_range: number;
  clipping_ratio: number;
  high_freq_fft_ratio: number;
  composite_quality_risk: number;
  quality_label: "NOMINAL" | "RISK_FLAGGED";
}

export interface DuplicateProfile {
  duplicate_status: "EXACT_DUPLICATE" | "POTENTIAL_NEAR_DUPLICATE" | "NO_DECLARED_REDUNDANCY_DETECTED";
  matched_image_id?: number;
  similarity_score?: number;
  match_stage?: string;
  cluster_id?: string;
  action: "KEEP" | "REVIEW" | "QUARANTINE";
}

export interface NoveltyProfile {
  novelty_score: number;
  novelty_percentile: number;
  reference_corpus: string;
  interpretation: string;
}

export interface ScientificImage {
  id: number;
  project_id: number;
  filename: string;
  sha256: string;
  width: number;
  height: number;
  channels: number;
  bit_depth: string;
  format: string;
  modality: string;
  instrument?: string;
  specimen_id?: string;
  roi_id?: string;
  acquisition_id?: string;
  status: "READY" | "PROCESSING" | "FAILED" | "QUARANTINED";
  uploaded_at: string;
  quality?: QualityProfile;
  duplicate?: DuplicateProfile;
  novelty?: NoveltyProfile;
}

export interface ReviewItem {
  id: number;
  image_id: number;
  status: "PENDING" | "APPROVED" | "REJECTED" | "QUARANTINED";
  trigger_reason: string;
  decision_notes?: string;
  created_at: string;
  resolved_at?: string;
  reviewer_id?: number;
}

export interface SearchResult {
  image_id: number;
  filename: string;
  similarity: number;
  modality: string;
  instrument?: string;
  quality_risk: number;
  quality_label: string;
  duplicate_status: string;
}

export interface ModelVersion {
  id: number;
  model_id: string;
  version: string;
  architecture: string;
  embedding_dimension: number;
  weights_hash: string;
  preprocessing_version: string;
  source: string;
  is_active: boolean;
  registered_at: string;
}

export interface SystemHealth {
  status: string;
  database: string;
  faiss_index_count: number;
  version: string;
}
