"use client";

import React, { useState, useEffect } from 'react';
import { analyticsApi } from '@/lib/api';

interface SkillData {
  skill: string;
  count: number;
}

interface ContractData {
  contract_type: string;
  count: number;
}

interface LocationData {
  location: string;
  count: number;
}

export default function AnalyticsPage() {
  const [skills, setSkills] = useState<SkillData[]>([]);
  const [contracts, setContracts] = useState<ContractData[]>([]);
  const [departments, setDepartments] = useState<LocationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [skillsData, contractsData, deptData] = await Promise.all([
        analyticsApi.skills({ top: 20 }),
        analyticsApi.contracts({}),
        analyticsApi.geography({ level: 'department' })
      ]);
      
      setSkills(skillsData);
      setContracts(contractsData);
      setDepartments(deptData.slice(0, 15));
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Chargement des analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-600">
            Analyses détaillées du marché de l'emploi data
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top 20 Compétences */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Top 20 Compétences
            </h2>
            {skills.length > 0 ? (
              <div className="space-y-3">
                {skills.map((skill, index) => (
                  <div key={skill.skill} className="flex items-center">
                    <span className="text-sm font-medium text-gray-500 w-8">
                      {index + 1}.
                    </span>
                    <div className="flex-1 ml-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          {skill.skill}
                        </span>
                        <span className="text-sm text-gray-500">
                          {skill.count}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${(skill.count / skills[0].count) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Aucune compétence trouvée</p>
            )}
          </div>

          {/* Distribution des contrats */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Types de Contrats
            </h2>
            {contracts.length > 0 ? (
              <div className="space-y-3">
                {contracts.map((contract, index) => {
                  const total = contracts.reduce((sum, c) => sum + c.count, 0);
                  const percentage = ((contract.count / total) * 100).toFixed(1);
                  return (
                    <div key={contract.contract_type} className="flex items-center">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-900">
                            {contract.contract_type}
                          </span>
                          <span className="text-sm text-gray-500">
                            {contract.count} ({percentage}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500">Aucune donnée de contrat</p>
            )}
          </div>

          {/* Top 15 Départements */}
          <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Top 15 Départements
            </h2>
            {departments.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {departments.map((dept, index) => (
                  <div
                    key={dept.location}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-500 mr-3">
                        {index + 1}.
                      </span>
                      <span className="text-sm font-medium text-gray-900">
                        {dept.location}
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-blue-600">
                      {dept.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Aucune donnée de localisation</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
