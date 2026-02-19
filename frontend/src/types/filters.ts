/**
 * Types pour les filtres de recherche
 */

export interface FilterRequest {
  keywords?: string[];
  regions?: string[];
  departments?: string[];
  cities?: string[];
  contract_types?: string[];
  salary_min?: number;
  salary_max?: number;
  experience_levels?: string[];
  rome_codes?: string[];
  skills?: string[];
  date_from?: string;
  date_to?: string;
}

export interface FilterOptions {
  regions: string[];
  departments: string[];
  cities: string[];
  contract_types: string[];
  experience_levels: string[];
  rome_codes: string[];
  keywords: string[];
}
