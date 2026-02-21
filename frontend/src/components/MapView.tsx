"use client";

import { useEffect, useRef, useState } from 'react';
import { JobOffer } from '@/types/offer';

interface MapViewProps {
  offers: JobOffer[];
  selectedCity?: string | null;
  onMarkerClick?: (offer: JobOffer) => void;
}

export default function MapView({ offers, selectedCity, onMarkerClick }: MapViewProps) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  // S'assurer qu'on est côté client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Initialiser la carte
  useEffect(() => {
    if (!isClient || !mapContainerRef.current || mapRef.current) return;

    // Importer Leaflet dynamiquement côté client uniquement
    import('leaflet').then((L) => {
      // Importer le CSS
      import('leaflet/dist/leaflet.css');

      // Fix pour les icônes de marqueurs
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });

      // Créer la carte centrée sur la France
      const map = L.map(mapContainerRef.current!).setView([46.603354, 1.888334], 6);

      // Ajouter les tuiles OpenStreetMap
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = { map, L };
    });

    // Cleanup
    return () => {
      if (mapRef.current?.map) {
        mapRef.current.map.remove();
        mapRef.current = null;
      }
    };
  }, [isClient]);

  // Mettre à jour les marqueurs
  useEffect(() => {
    if (!mapRef.current?.map || !mapRef.current?.L) return;

    const { map, L } = mapRef.current;

    // Supprimer les anciens marqueurs
    map.eachLayer((layer: any) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    // Filtrer les offres avec coordonnées
    const filteredOffers = selectedCity
      ? offers.filter(o => o.location_city === selectedCity)
      : offers;

    const offersWithCoords = filteredOffers.filter(
      offer => offer.location_coordinates?.lat && offer.location_coordinates?.lon
    );

    if (offersWithCoords.length === 0) return;

    // Grouper les offres par position pour gérer les marqueurs empilés
    const positionGroups = new Map<string, JobOffer[]>();
    offersWithCoords.forEach(offer => {
      const key = `${offer.location_coordinates!.lat.toFixed(4)},${offer.location_coordinates!.lon.toFixed(4)}`;
      if (!positionGroups.has(key)) {
        positionGroups.set(key, []);
      }
      positionGroups.get(key)!.push(offer);
    });

    // Créer les marqueurs
    const bounds: [number, number][] = [];
    positionGroups.forEach((groupOffers) => {
      const firstOffer = groupOffers[0];
      const { lat, lon } = firstOffer.location_coordinates!;
      bounds.push([lat, lon]);

      // Créer une icône personnalisée avec le nombre d'offres
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `
          <div class="marker-pin" style="
            background-color: #2563eb;
            width: 30px;
            height: 30px;
            border-radius: 50% 50% 50% 0;
            position: relative;
            transform: rotate(-45deg);
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ">
            <div style="
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%) rotate(45deg);
              color: white;
              font-size: 12px;
              font-weight: bold;
            ">${groupOffers.length}</div>
          </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
      });

      const marker = L.marker([lat, lon], { icon });

      // Créer le popup
      const popupContent = `
        <div style="min-width: 200px; max-width: 300px;">
          <h3 style="font-weight: bold; margin-bottom: 8px; font-size: 14px;">
            ${firstOffer.location_city}
          </h3>
          <p style="margin-bottom: 8px; color: #6b7280; font-size: 13px;">
            ${groupOffers.length} offre${groupOffers.length > 1 ? 's' : ''}
          </p>
          <div style="max-height: 200px; overflow-y: auto;">
            ${groupOffers.slice(0, 5).map(offer => `
              <div style="border-top: 1px solid #e5e7eb; padding: 8px 0;">
                <p style="font-weight: 500; font-size: 13px; margin-bottom: 4px;">
                  ${offer.title}
                </p>
                ${offer.company_name ? `
                  <p style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">
                    🏢 ${offer.company_name}
                  </p>
                ` : ''}
                ${offer.contract_type ? `
                  <p style="font-size: 12px; color: #6b7280;">
                    📄 ${offer.contract_type}
                  </p>
                ` : ''}
              </div>
            `).join('')}
            ${groupOffers.length > 5 ? `
              <p style="text-align: center; color: #6b7280; font-size: 12px; padding: 8px 0;">
                ... et ${groupOffers.length - 5} autre${groupOffers.length - 5 > 1 ? 's' : ''}
              </p>
            ` : ''}
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);

      if (onMarkerClick) {
        marker.on('click', () => onMarkerClick(firstOffer));
      }

      marker.addTo(map);
    });

    // Ajuster la vue pour afficher tous les marqueurs
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
    }
  }, [offers, selectedCity, onMarkerClick, isClient]);

  return (
    <div 
      ref={mapContainerRef} 
      className="w-full h-full rounded-lg shadow-lg"
      style={{ minHeight: '500px' }}
    />
  );
}
