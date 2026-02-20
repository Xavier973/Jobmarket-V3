/**
 * Types pour les offres d'emploi
 */

export interface JobOffer {
  id: string;
  source: string;
  title?: string;
  company_name?: string;
  description?: string;
  
  // Localisation
  location_city?: string;
  location_department?: string;
  location_region?: string;
  location_latitude?: number;
  location_longitude?: number;
  location_coordinates?: {
    lat: number;
    lon: number;
  };
  
  // Contrat
  contract_type?: string;
  contract_duration?: string;
  work_schedule?: string;
  is_alternance?: boolean;
  is_remote?: boolean;
  remote_type?: string; // "full_remote" | "hybrid" | "occasional"
  
  // Salaire
  salary_min?: number;
  salary_max?: number;
  salary_unit?: string;
  salary_comment?: string;
  
  // Classification
  rome_code?: string;
  rome_label?: string;
  job_category?: string;
  sector?: string;
  
  // Compétences
  skills?: string[];
  soft_skills?: string[];
  
  // Expérience
  experience_required?: string;
  experience_level?: string;
  education_level?: string;
  
  // Métadonnées
  published_at?: string;
  updated_at?: string;
  collected_at?: string;
  positions_count?: number;
  url?: string;
}

export interface JobOfferListResponse {
  total: number;
  page: number;
  size: number;
  pages: number;
  items: JobOffer[];
}
