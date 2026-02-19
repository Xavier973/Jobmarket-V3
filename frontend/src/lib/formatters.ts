/**
 * Utilitaires de formatage
 */

/**
 * Formate un salaire
 */
export function formatSalary(
  salaryMin?: number,
  salaryMax?: number,
  unit?: string
): string {
  if (!salaryMin && !salaryMax) return 'Non renseigné';

  const formatNumber = (n: number) => {
    return new Intl.NumberFormat('fr-FR').format(Math.round(n));
  };

  const unitLabel = unit === 'yearly' ? '/an' : unit === 'monthly' ? '/mois' : '/h';

  if (salaryMin && salaryMax) {
    return `${formatNumber(salaryMin)} - ${formatNumber(salaryMax)} € ${unitLabel}`;
  } else if (salaryMin) {
    return `À partir de ${formatNumber(salaryMin)} € ${unitLabel}`;
  } else if (salaryMax) {
    return `Jusqu'à ${formatNumber(salaryMax)} € ${unitLabel}`;
  }

  return 'Non renseigné';
}

/**
 * Formate une date
 */
export function formatDate(dateString?: string): string {
  if (!dateString) return 'Non renseigné';

  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  } catch {
    return dateString;
  }
}

/**
 * Formate une date relative (il y a X jours)
 */
export function formatRelativeDate(dateString?: string): string {
  if (!dateString) return 'Date inconnue';

  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Aujourd'hui";
    if (diffDays === 1) return 'Hier';
    if (diffDays < 7) return `Il y a ${diffDays} jours`;
    if (diffDays < 30) return `Il y a ${Math.floor(diffDays / 7)} semaines`;
    if (diffDays < 365) return `Il y a ${Math.floor(diffDays / 30)} mois`;

    return formatDate(dateString);
  } catch {
    return dateString;
  }
}

/**
 * Tronque un texte
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Classe CSS conditionnelle
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
