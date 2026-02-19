/**
 * Client API pour communiquer avec le backend FastAPI
 */
import axios from 'axios';
import type { JobOffer, JobOfferListResponse } from '@/types/offer';
import type { FilterRequest } from '@/types/filters';
import type { OverviewStats, TopSkill, ContractDistribution, GeographyData, TimelineData } from '@/types/stats';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Instance axios configurée
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// API Offers
export const offersApi = {
  /**
   * Liste paginée des offres
   */
  list: async (params: {
    page?: number;
    size?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    keywords?: string;
    regions?: string;
    departments?: string;
    contract_types?: string;
    salary_min?: number;
    salary_max?: number;
  }): Promise<JobOfferListResponse> => {
    const response = await apiClient.get('/offers', { params });
    return response.data;
  },

  /**
   * Recherche avec filtres avancés
   */
  search: async (
    filters: FilterRequest,
    params: {
      page?: number;
      size?: number;
      sort_by?: string;
      sort_order?: 'asc' | 'desc';
    }
  ): Promise<JobOfferListResponse> => {
    const response = await apiClient.post('/offers/search', filters, { params });
    return response.data;
  },

  /**
   * Détail d'une offre
   */
  getById: async (id: string): Promise<JobOffer> => {
    const response = await apiClient.get(`/offers/${id}`);
    return response.data;
  },

  /**
   * Comptage avec filtres
   */
  count: async (params: {
    keywords?: string;
    regions?: string;
    departments?: string;
    contract_types?: string;
  }): Promise<{ count: number }> => {
    const response = await apiClient.get('/offers/count/total', { params });
    return response.data;
  },
};

// API Stats
export const statsApi = {
  /**
   * Statistiques d'ensemble
   */
  overview: async (): Promise<OverviewStats> => {
    const response = await apiClient.get('/stats/overview');
    return response.data;
  },

  /**
   * KPIs avec filtres
   */
  kpis: async (params: { keywords?: string; regions?: string }): Promise<any> => {
    const response = await apiClient.get('/stats/kpis', { params });
    return response.data;
  },
};

// API Analytics
export const analyticsApi = {
  /**
   * Statistiques salariales
   */
  salary: async (params: {
    group_by?: string;
    keywords?: string;
    regions?: string;
  }): Promise<any> => {
    const response = await apiClient.get('/analytics/salary', { params });
    return response.data;
  },

  /**
   * Top compétences
   */
  skills: async (params: { top?: number; keywords?: string; regions?: string }): Promise<TopSkill[]> => {
    const response = await apiClient.get('/analytics/skills', { params });
    return response.data;
  },

  /**
   * Distribution géographique
   */
  geography: async (params: {
    level?: 'region' | 'department' | 'city';
    keywords?: string;
  }): Promise<GeographyData[]> => {
    const response = await apiClient.get('/analytics/geography', { params });
    return response.data;
  },

  /**
   * Distribution des contrats
   */
  contracts: async (params: { keywords?: string }): Promise<ContractDistribution[]> => {
    const response = await apiClient.get('/analytics/contracts', { params });
    return response.data;
  },

  /**
   * Évolution temporelle
   */
  timeline: async (params: {
    interval?: 'day' | 'week' | 'month';
    keywords?: string;
  }): Promise<TimelineData[]> => {
    const response = await apiClient.get('/analytics/timeline', { params });
    return response.data;
  },
};

// API Filters
export const filtersApi = {
  regions: async (): Promise<string[]> => {
    const response = await apiClient.get('/filters/regions');
    return response.data;
  },

  departments: async (region?: string): Promise<string[]> => {
    const response = await apiClient.get('/filters/departments', {
      params: region ? { region } : undefined,
    });
    return response.data;
  },

  cities: async (department?: string): Promise<string[]> => {
    const response = await apiClient.get('/filters/cities', {
      params: department ? { department } : undefined,
    });
    return response.data;
  },

  contracts: async (): Promise<string[]> => {
    const response = await apiClient.get('/filters/contracts');
    return response.data;
  },

  experienceLevels: async (): Promise<string[]> => {
    const response = await apiClient.get('/filters/experience-levels');
    return response.data;
  },

  romeCodes: async (): Promise<string[]> => {
    const response = await apiClient.get('/filters/rome-codes');
    return response.data;
  },
};

export default apiClient;
