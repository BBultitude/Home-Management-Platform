import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  path: string;
}

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  financial: 'Financial',
  tax: 'Tax Records',
  assets: 'Assets',
  projects: 'Projects',
  knowledge: 'Knowledge Base',
  meals: 'Meal Planner',
  settings: 'Settings',
  admin: 'Admin',
  users: 'Users',
};

export function Breadcrumbs() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  // Don't show breadcrumbs on dashboard
  if (pathnames.length === 0 || pathnames[0] === 'dashboard') {
    return null;
  }

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Dashboard', path: '/dashboard' },
  ];

  let currentPath = '';
  pathnames.forEach((segment) => {
    currentPath += `/${segment}`;
    const label = routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
    breadcrumbs.push({ label, path: currentPath });
  });

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-4">
      <Link
        to="/dashboard"
        className="flex items-center hover:text-gray-900 transition-colors"
      >
        <Home className="h-4 w-4" />
      </Link>

      {breadcrumbs.slice(1).map((crumb, index) => (
        <div key={crumb.path} className="flex items-center space-x-2">
          <ChevronRight className="h-4 w-4" />
          {index === breadcrumbs.length - 2 ? (
            // Last breadcrumb (current page) - not clickable
            <span className="font-medium text-gray-900">{crumb.label}</span>
          ) : (
            <Link
              to={crumb.path}
              className="hover:text-gray-900 transition-colors"
            >
              {crumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}
