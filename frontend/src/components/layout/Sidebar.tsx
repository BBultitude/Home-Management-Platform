import { useNavigate, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useAuthStore } from '@/stores/authStore';
import {
  LayoutDashboard,
  DollarSign,
  FileText,
  Home,
  Wrench,
  BookOpen,
  UtensilsCrossed,
  Settings,
  Shield,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface NavItem {
  name: string;
  icon: React.ElementType;
  path: string;
  roles?: string[]; // If specified, only these roles can see this item
}

const navigationItems: NavItem[] = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { name: 'Financial', icon: DollarSign, path: '/financial' },
  { name: 'Tax Records', icon: FileText, path: '/tax' },
  { name: 'Assets', icon: Home, path: '/assets' },
  { name: 'Projects', icon: Wrench, path: '/projects' },
  { name: 'Knowledge Base', icon: BookOpen, path: '/knowledge' },
  { name: 'Meal Planner', icon: UtensilsCrossed, path: '/meals' },
  { name: 'Settings', icon: Settings, path: '/settings' },
  { name: 'Admin Panel', icon: Shield, path: '/admin/users', roles: ['ADMIN'] },
];

type SidebarProps = Readonly<{
  collapsed: boolean;
  onToggle: () => void;
  className?: string;
}>

export function Sidebar({ collapsed, onToggle, className }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();

  const isActive = (path: string) => {
    // Exact match for dashboard, prefix match for others
    if (path === '/dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const canAccessItem = (item: NavItem) => {
    if (!item.roles) return true;
    return item.roles.some(role => user?.role?.toUpperCase() === role);
  };

  return (
    <div
      className={cn(
        'flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      {/* Logo/Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center">
            <span className="text-2xl">🏠</span>
            <span className="ml-2 font-bold text-gray-900 truncate">Home Manager</span>
          </div>
        )}
        {collapsed && <span className="text-2xl mx-auto">🏠</span>}

        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn('h-8 w-8', collapsed && 'mx-auto mt-2')}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navigationItems.map((item) => {
          if (!canAccessItem(item)) return null;

          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={cn(
                'w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                'hover:bg-gray-100',
                active
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-gray-700',
                collapsed && 'justify-center'
              )}
              title={collapsed ? item.name : undefined}
            >
              <Icon className={cn('h-5 w-5 flex-shrink-0', !collapsed && 'mr-3')} />
              {!collapsed && <span className="truncate">{item.name}</span>}
            </button>
          );
        })}
      </nav>

      {/* User Info */}
      {!collapsed && (
        <>
          <Separator />
          <div className="p-4">
            <div className="text-xs text-gray-500 mb-1">Logged in as</div>
            <div className="text-sm font-medium text-gray-900 truncate">
              {user?.full_name || user?.username}
            </div>
            <div className="text-xs text-gray-500 capitalize truncate">
              {user?.role?.toLowerCase()}
            </div>
            {user?.mfa_enabled && (
              <div className="text-xs text-green-600 mt-1">🔒 MFA Enabled</div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
