"use client";

import React, { useState, useEffect } from 'react';
import { offersApi, filtersApi } from '@/lib/api';
import { JobOffer } from '@/types/offer';

export default function OffersPage() {
  const [offers, setOffers] = useState<JobOffer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  // États des filtres
  const [selectedRomeLabel, setSelectedRomeLabel] = useState<string>('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [selectedRemoteType, setSelectedRemoteType] = useState<string>('');

  // Options disponibles
  const [romeLabels, setRomeLabels] = useState<string[]>([]);
  const [departments, setDepartments] = useState<Array<{code: string, name: string, label: string}>>([]);
  const [remoteTypes, setRemoteTypes] = useState<string[]>([]);

  // Charger les options de filtres au montage
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Recharger les offres quand les filtres ou la page changent
  useEffect(() => {
    fetchOffers();
  }, [page, selectedRomeLabel, selectedDepartment, selectedRemoteType]);

  const loadFilterOptions = async () => {
    try {
      const [labelsData, deptsData, remoteData] = await Promise.all([
        filtersApi.romeLabels(),
        filtersApi.departments(),
        filtersApi.remoteTypes(),
      ]);
      setRomeLabels(labelsData.sort());
      setDepartments(deptsData); // Déjà trié par le backend
      setRemoteTypes(remoteData);
    } catch (err) {
      console.error('Erreur lors du chargement des options de filtres:', err);
    }
  };

  const fetchOffers = async () => {
    try {
      setLoading(true);
      
      // Construire les paramètres de recherche
      const params: any = { page, size: pageSize };
      
      if (selectedRomeLabel) {
        params.rome_labels = selectedRomeLabel;
      }
      if (selectedDepartment) {
        params.departments = selectedDepartment;
      }
      if (selectedRemoteType) {
        params.remote_types = selectedRemoteType;
      }

      const data = await offersApi.list(params);
      setOffers(data.items);
      setTotalPages(data.pages);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des offres');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetFilters = () => {
    setSelectedRomeLabel('');
    setSelectedDepartment('');
    setSelectedRemoteType('');
    setPage(1);
  };

  const hasActiveFilters = selectedRomeLabel || selectedDepartment || selectedRemoteType;

  if (loading && page === 1 && offers.length === 0) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-lg">Chargement des offres...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Offres d'emploi</h1>
        <p className="mt-2 text-sm text-gray-600">
          {total} offre{total > 1 ? 's' : ''} trouvée{total > 1 ? 's' : ''}
        </p>
      </div>

      {/* Filtres */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Filtres</h2>
          {hasActiveFilters && (
            <button
              onClick={handleResetFilters}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Réinitialiser
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Filtre Métier ROME */}
          <div>
            <label htmlFor="rome-label" className="block text-sm font-medium text-gray-700 mb-2">
              Métier
            </label>
            <select
              id="rome-label"
              value={selectedRomeLabel}
              onChange={(e) => {
                setSelectedRomeLabel(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les métiers</option>
              {romeLabels.map((label) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Filtre Département */}
          <div>
            <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
              Département
            </label>
            <select
              id="department"
              value={selectedDepartment}
              onChange={(e) => {
                setSelectedDepartment(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les départements</option>
              {departments.map((dept) => (
                <option key={dept.code} value={dept.code}>
                  {dept.label}
                </option>
              ))}
            </select>
          </div>

          {/* Filtre Type de télétravail */}
          <div>
            <label htmlFor="remote-type" className="block text-sm font-medium text-gray-700 mb-2">
              Télétravail
            </label>
            <select
              id="remote-type"
              value={selectedRemoteType}
              onChange={(e) => {
                setSelectedRemoteType(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous types</option>
              {remoteTypes.map((type) => (
                <option key={type} value={type}>
                  {type === 'full_remote' && '100% Télétravail'}
                  {type === 'hybrid' && 'Hybride'}
                  {type === 'occasional' && 'Occasionnel'}
                  {!['full_remote', 'hybrid', 'occasional'].includes(type) && type}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Liste des offres */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="text-center py-8">
            <div className="text-gray-600">Chargement...</div>
          </div>
        ) : offers.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Aucune offre ne correspond à vos critères.</p>
            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                className="mt-4 text-blue-600 hover:text-blue-800"
              >
                Réinitialiser les filtres
              </button>
            )}
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {offers.map((offer) => (
              <li key={offer.id}>
                <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-blue-600 truncate">
                        {offer.title}
                      </h3>
                      <p className="mt-1 text-sm text-gray-600">
                        {offer.company_name}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {offer.location_city && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            📍 {offer.location_city}
                          </span>
                        )}
                        {offer.contract_type && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {offer.contract_type}
                          </span>
                        )}
                        {offer.is_remote && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            🏠 Télétravail
                          </span>
                        )}
                        {offer.salary_min && offer.salary_max && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            💰 {offer.salary_min.toLocaleString()} - {offer.salary_max.toLocaleString()}€
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <span className="text-xs text-gray-500">
                        {offer.published_at ? new Date(offer.published_at).toLocaleDateString('fr-FR') : 'N/A'}
                      </span>
                    </div>
                  </div>
                  {offer.description && (
                    <p className="mt-3 text-sm text-gray-700 line-clamp-2">
                      {offer.description.substring(0, 200)}...
                    </p>
                  )}
                  {offer.url && (
                    <div className="mt-3">
                      <a
                        href={offer.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        Voir l'offre →
                      </a>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Pagination */}
      <div className="mt-6 flex items-center justify-between">
        <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Précédent
          </button>
          <span className="text-sm text-gray-700">
            Page {page} sur {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Suivant
          </button>
      </div>
    </div>
  );
}
