/**
 * Types pour les statistiques et analytics
 */

export interface OverviewStats {
  total_offers: number;
  salary_median: number;
  salary_min: number;
  salary_max: number;
  top_regions: TopLocation[];
  top_skills: TopSkill[];
  cdi_percentage: number;
  contract_distribution: ContractDistribution[];
}

export interface TopLocation {
  location: string;
  count: number;
}

export interface TopSkill {
  skill: string;
  count: number;
}

export interface ContractDistribution {
  contract_type: string;
  count: number;
}

export interface SalaryStats {
  count: number;
  min: number;
  max: number;
  avg: number;
  sum: number;
}

export interface TimelineData {
  date: string;
  count: number;
}

export interface GeographyData {
  location: string;
  count: number;
}
