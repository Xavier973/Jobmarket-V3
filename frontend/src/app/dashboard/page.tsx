'use client'

import { useEffect, useState } from 'react'
import { statsApi, analyticsApi } from '@/lib/api'
import type { OverviewStats, TimelineData, GeographyData } from '@/types/stats'

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [timeline, setTimeline] = useState<TimelineData[]>([])
  const [topDepartments, setTopDepartments] = useState<GeographyData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStats() {
      try {
        setLoading(true)
        const [statsData, timelineData, departmentsData] = await Promise.all([
          statsApi.overview(),
          analyticsApi.timeline({ interval: 'week' }),
          analyticsApi.geography({ level: 'department' })
        ])
        setStats(statsData)
        setTimeline(timelineData)
        setTopDepartments(departmentsData.slice(0, 3))
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
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
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
    <div className="container mx-auto px-4 py-8">
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
            title="Départements"
            value={topDepartments.length.toString()}
            subtitle="couvertes"
            color="orange"
          />
        </div>

        {/* Top Regions & Skills */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Top Departments */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top 3 Départements</h2>
            <div className="space-y-3">
              {topDepartments.map((department, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-700">{department.location}</span>
                  <span className="font-semibold text-primary-600">
                    {department.count} offres
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

  // Filtrer les données récentes (3 derniers mois environ)
  const now = new Date()
  const threeMonthsAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
  
  const filteredData = data
    .filter(point => {
      const date = new Date(point.date)
      return date >= threeMonthsAgo && date <= now
    })
    .filter(point => point.count > 0) // Ne garder que les semaines avec des offres

  if (filteredData.length === 0) {
    return <p className="text-gray-500 text-center py-8">Aucune donnée récente disponible</p>
  }

  const maxCount = Math.max(...filteredData.map(d => d.count))

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex items-end gap-3 min-h-[350px] px-4" style={{ minWidth: `${filteredData.length * 80}px` }}>
        {filteredData.map((point, index) => {
          const heightPercentage = maxCount > 0 ? (point.count / maxCount) * 100 : 0
          const date = new Date(point.date)
          const formattedDate = date.toLocaleDateString('fr-FR', { 
            day: '2-digit',
            month: 'short'
          })
          const year = date.getFullYear()
          
          // Afficher l'année uniquement à la première barre ou quand l'année change
          const previousYear = index > 0 ? new Date(filteredData[index - 1].date).getFullYear() : null
          const showYear = index === 0 || (previousYear !== null && previousYear !== year)

          return (
            <div key={index} className="flex flex-col items-center gap-2" style={{ minWidth: '60px' }}>
              {/* Barre verticale */}
              <div className="relative flex items-end justify-center w-full" style={{ height: '280px' }}>
                <div
                  className="bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-lg w-full transition-all duration-300 hover:from-blue-700 hover:to-blue-500 cursor-pointer shadow-md relative group"
                  style={{ height: `${Math.max(heightPercentage, 5)}%` }}
                  title={`${point.count} offres publiées`}
                >
                  {/* Afficher le nombre au-dessus de la barre */}
                  <div className="absolute -top-7 left-1/2 transform -translate-x-1/2 text-sm font-bold text-gray-800 whitespace-nowrap">
                    {point.count}
                  </div>
                  
                  {/* Tooltip au survol */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
                    Semaine du {formattedDate}
                  </div>
                </div>
              </div>
              
              {/* Date en dessous */}
              <div className="text-xs text-gray-600 text-center font-medium w-full">
                <div className="font-semibold">{formattedDate}</div>
                {showYear && (
                  <div className="text-gray-500 font-normal text-[10px] mt-0.5">{year}</div>
                )}
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Légende */}
      <div className="text-center mt-4 text-sm text-gray-500">
        📊 Évolution hebdomadaire des offres publiées (3 derniers mois)
      </div>
    </div>
  )
}
