"use client";

import React, { useState, useEffect } from 'react';
import { offersApi } from '@/lib/api';
import { JobOffer } from '@/types/offer';

export default function MapPage() {
  const [offers, setOffers] = useState<JobOffer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);

  useEffect(() => {
    fetchOffersWithCoordinates();
  }, []);

  const fetchOffersWithCoordinates = async () => {
    try {
      setLoading(true);
      // Récupérer les offres avec coordonnées (on pourrait filtrer côté API)
      const data = await offersApi.list({ page: 1, size: 100 });
      const offersWithCoords = data.items.filter(
        offer => offer.location_coordinates?.lat && offer.location_coordinates?.lon
      );
      setOffers(offersWithCoords);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des offres');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Grouper les offres par ville
  const getCityGroups = () => {
    const groups = new Map<string, JobOffer[]>();
    offers.forEach(offer => {
      const city = offer.location_city || 'Ville inconnue';
      if (!groups.has(city)) {
        groups.set(city, []);
      }
      groups.get(city)!.push(offer);
    });
    return Array.from(groups.entries())
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 20);
  };

  const cityGroups = getCityGroups();
  const filteredOffers = selectedCity
    ? offers.filter(o => o.location_city === selectedCity)
    : offers;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-lg">Chargement de la carte...</div>
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
          <h1 className="text-3xl font-bold text-gray-900">Carte des offres</h1>
          <p className="mt-2 text-sm text-gray-600">
            {offers.length} offres géolocalisées
          </p>
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                La carte interactive avec Leaflet sera implémentée prochainement. En attendant, voici la liste des villes avec le plus d'offres.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Liste des villes */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Top 20 Villes
              </h2>
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedCity(null)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                    selectedCity === null
                      ? 'bg-blue-100 text-blue-900 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Toutes les villes ({offers.length})
                </button>
                {cityGroups.map(([city, cityOffers]) => (
                  <button
                    key={city}
                    onClick={() => setSelectedCity(city)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm flex justify-between items-center ${
                      selectedCity === city
                        ? 'bg-blue-100 text-blue-900 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="truncate">{city}</span>
                    <span className="ml-2 bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full text-xs font-medium">
                      {cityOffers.length}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Liste des offres pour la ville sélectionnée */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {selectedCity ? `Offres à ${selectedCity}` : 'Toutes les offres géolocalisées'}
                <span className="ml-2 text-gray-500 text-sm font-normal">
                  ({filteredOffers.length})
                </span>
              </h2>
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {filteredOffers.map(offer => (
                  <div
                    key={offer.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-medium text-gray-900 mb-2">
                      {offer.title}
                    </h3>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>📍 {offer.location_city}</p>
                      {offer.company_name && (
                        <p>🏢 {offer.company_name}</p>
                      )}
                      {offer.contract_type && (
                        <p>📄 {offer.contract_type}</p>
                      )}
                      {offer.location_coordinates && (
                        <p className="text-xs text-gray-500">
                          Coordonnées: {offer.location_coordinates.lat.toFixed(4)}, {offer.location_coordinates.lon.toFixed(4)}
                        </p>
                      )}
                      {offer.url && (
                        <a
                          href={offer.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm inline-block mt-2"
                        >
                          Voir l'offre →
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}
