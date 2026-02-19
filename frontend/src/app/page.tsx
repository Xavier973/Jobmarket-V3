import Link from 'next/link'
import { ArrowRight, BarChart3, MapPin, TrendingUp, Database } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              JobMarket V3
            </h1>
            <p className="text-xl mb-8 opacity-90">
              Analytics du marché de l'emploi data en France
            </p>
            <p className="text-lg mb-10 opacity-80">
              Explorez les tendances, salaires, compétences et opportunités dans l'écosystème data français
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/dashboard"
                className="bg-white text-primary-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition flex items-center gap-2"
              >
                Voir le Dashboard
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="https://github.com/Xavier973/Jobmarket-V3"
                target="_blank"
                rel="noopener noreferrer"
                className="border-2 border-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary-700 transition"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Fonctionnalités</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            <FeatureCard
              icon={<BarChart3 className="w-10 h-10 text-primary-600" />}
              title="Statistiques détaillées"
              description="KPIs, tendances et analyses approfondies du marché"
            />
            <FeatureCard
              icon={<TrendingUp className="w-10 h-10 text-primary-600" />}
              title="Analyses salariales"
              description="Distribution et évolution des salaires par profil"
            />
            <FeatureCard
              icon={<Database className="w-10 h-10 text-primary-600" />}
              title="Compétences demandées"
              description="Top des compétences techniques et outils"
            />
            <FeatureCard
              icon={<MapPin className="w-10 h-10 text-primary-600" />}
              title="Cartographie"
              description="Visualisation géographique des opportunités"
            />
          </div>
        </div>
      </section>

      {/* Data Source Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 max-w-4xl">
          <h2 className="text-3xl font-bold text-center mb-8">Source des données</h2>
          <div className="bg-white rounded-lg shadow-lg p-8">
            <p className="text-lg mb-4">
              Les données sont collectées via l'<strong>API France Travail</strong> (anciennement Pôle Emploi)
              et enrichies pour fournir des analyses précises du marché de l'emploi.
            </p>
            <p className="text-gray-600 mb-6">
              Mots-clés couverts : Data Analyst, Data Engineer, Data Scientist, Analytics Engineer,
              Data Architect, Machine Learning, MLOps, Big Data, Cloud Engineer, ETL...
            </p>
            <div className="flex gap-4">
              <span className="bg-primary-100 text-primary-800 px-4 py-2 rounded-full text-sm font-semibold">
                + de 3000 offres analysées
              </span>
              <span className="bg-primary-100 text-primary-800 px-4 py-2 rounded-full text-sm font-semibold">
                Mise à jour quotidienne
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Prêt à explorer ?</h2>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-white text-primary-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            Accéder au Dashboard
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8">
        <div className="container mx-auto px-4 text-center">
          <p>© 2026 JobMarket V3 - Projet Portfolio</p>
          <p className="text-sm mt-2">
            Built with Next.js, FastAPI, Elasticsearch & React
          </p>
        </div>
      </footer>
    </main>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
