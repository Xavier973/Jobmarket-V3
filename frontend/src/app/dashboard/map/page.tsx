"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { offersApi } from '@/lib/api';
import { JobOffer } from '@/types/offer';

// Charger MapView uniquement côté client (pas de SSR)
const MapView = dynamic(() => import('@/components/MapView'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[600px]">
      <div className="text-lg text-gray-600">Chargement de la carte...</div>
    </div>
  ),
});

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
      
      // Récupérer plusieurs pages d'offres pour une meilleure visualisation sur la carte
      // La limite API est de 100 par page, on récupère 5 pages = 500 offres max
      const allOffers: JobOffer[] = [];
      const pageSize = 100;
      const maxPages = 5;
      
      for (let page = 1; page <= maxPages; page++) {
        const data = await offersApi.list({ page, size: pageSize });
        allOffers.push(...data.items);
        
        // S'arrêter si on a récupéré toutes les offres disponibles
        if (data.items.length < pageSize) {
          break;
        }
      }
      
      // Filtrer uniquement les offres avec coordonnées géographiques
      const offersWithCoords = allOffers.filter(
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

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
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

          {/* Carte interactive */}
          <div className="lg:col-span-3">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {selectedCity ? `Offres à ${selectedCity}` : 'Carte interactive'}
                <span className="ml-2 text-gray-500 text-sm font-normal">
                  ({filteredOffers.length} offre{filteredOffers.length > 1 ? 's' : ''})
                </span>
              </h2>
              <div className="h-[600px]">
                <MapView 
                  offers={filteredOffers} 
                  selectedCity={selectedCity}
                />
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}
