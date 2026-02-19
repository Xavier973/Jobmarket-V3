'use client'

import { useEffect, useState } from 'react'
import { statsApi, analyticsApi } from '@/lib/api'
import type { OverviewStats, TimelineData } from '@/types/stats'

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [timeline, setTimeline] = useState<TimelineData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStats() {
      try {
        setLoading(true)
        const [statsData, timelineData] = await Promise.all([
          statsApi.overview(),
          analyticsApi.timeline({ interval: 'week' })
        ])
        setStats(statsData)
        setTimeline(timelineData)
      } catch (err) {
        console.error('Erreur chargement stats:', err)
        setError('Impossible de charger les statistiques. Vérifiez que le backend est démarré.')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-lg">
          <h2 className="text-red-800 font-semibold text-lg mb-2">Erreur</h2>
          <p className="text-red-600">{error}</p>
          <div className="mt-4 text-sm text-gray-600">
            <p>Assurez-vous que :</p>
            <ul className="list-disc list-inside mt-2">
              <li>Elasticsearch est démarré (docker-compose up)</li>
              <li>Le backend FastAPI est lancé (port 8000)</li>
              <li>Les données sont indexées</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              JobMarket Dashboard
            </h1>
            <nav className="flex gap-6">
              <a href="/dashboard" className="text-primary-600 font-semibold">
                Vue d'ensemble
              </a>
              <a href="/dashboard/offers" className="text-gray-600 hover:text-gray-900">
                Offres
              </a>
              <a href="/dashboard/analytics" className="text-gray-600 hover:text-gray-900">
                Analytics
              </a>
              <a href="/dashboard/map" className="text-gray-600 hover:text-gray-900">
                Carte
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Total offres"
            value={stats?.total_offers.toLocaleString('fr-FR') || '0'}
            color="blue"
          />
          <KPICard
            title="Salaire moyen"
            value={`${Math.round(stats?.salary_median || 0).toLocaleString('fr-FR')} €`}
            subtitle="/an"
            color="green"
          />
          <KPICard
            title="% CDI"
            value={`${stats?.cdi_percentage || 0}%`}
            color="purple"
          />
          <KPICard
            title="Régions"
            value={stats?.top_regions?.length.toString() || '0'}
            subtitle="couvertes"
            color="orange"
          />
        </div>

        {/* Top Regions & Skills */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Top Regions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top 3 Régions</h2>
            <div className="space-y-3">
              {stats?.top_regions?.map((region, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-700">{region.location}</span>
                  <span className="font-semibold text-primary-600">
                    {region.count} offres
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Skills */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top 3 Compétences</h2>
            <div className="space-y-3">
              {stats?.top_skills?.map((skill, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-700">{skill.skill}</span>
                  <span className="font-semibold text-primary-600">
                    {skill.count} offres
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Contract Distribution */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Distribution des contrats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats?.contract_distribution?.slice(0, 4).map((contract, index) => (
              <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-primary-600">{contract.count}</p>
                <p className="text-sm text-gray-600 mt-1">{contract.contract_type}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Timeline Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Évolution des offres publiées</h2>
          {timeline.length > 0 ? (
            <TimelineChart data={timeline} />
          ) : (
            <p className="text-gray-500 text-center py-8">Aucune donnée disponible</p>
          )}
        </div>
      </main>
    </div>
  )
}

function KPICard({
  title,
  value,
  subtitle,
  color = 'blue',
}: {
  title: string
  value: string
  subtitle?: string
  color?: 'blue' | 'green' | 'purple' | 'orange'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    orange: 'bg-orange-50 border-orange-200 text-orange-900',
  }

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]}`}>
      <h3 className="text-sm font-medium opacity-75 mb-2">{title}</h3>
      <p className="text-3xl font-bold">
        {value}
        {subtitle && <span className="text-lg ml-1 opacity-75">{subtitle}</span>}
      </p>
    </div>
  )
}

function TimelineChart({ data }: { data: TimelineData[] }) {
  if (!data || data.length === 0) return null

  const maxCount = Math.max(...data.map(d => d.count))

  return (
    <div className="space-y-2">
      {data.map((point, index) => {
        const percentage = (point.count / maxCount) * 100
        const date = new Date(point.date)
        const formattedDate = date.toLocaleDateString('fr-FR', { 
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })

        return (
          <div key={index} className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-600 font-medium">
              {formattedDate}
            </div>
            <div className="flex-1 bg-gray-100 rounded-full h-8 relative">
              <div
                className="bg-gradient-to-r from-primary-500 to-primary-600 h-8 rounded-full flex items-center justify-end px-3 transition-all duration-500"
                style={{ width: `${Math.max(percentage, 5)}%` }}
              >
                <span className="text-white text-sm font-semibold">
                  {point.count}
                </span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
