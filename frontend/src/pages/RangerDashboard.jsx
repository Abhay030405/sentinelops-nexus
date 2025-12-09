import { useNavigate } from 'react-router-dom';
import {
  Fingerprint,
  FileText,
  Download,
  Activity,
  Bell,
  Calendar,
  Building2,
  UserCircle,
} from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../hooks/useAuth';

export default function RangerDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const modules = [
    {
      title: 'BiometricAuth',
      description: 'Document management & AI processing for secure identity verification',
      icon: Fingerprint,
      path: '/biometric-auth',
      status: 'active',
      notifications: 2,
    },

    {
      title: 'DataExport',
      description: 'Secure data export functionality with encryption protocols',
      icon: Download,
      path: '/data-export',
      status: 'active',
    },
    {
      title: 'BioTelemetry',
      description: 'Real-time biometric telemetry monitoring and analysis',
      icon: Activity,
      path: '/bio-telemetry',
      status: 'warning',
      notifications: 5,
    },
    {
      title: 'Notifications',
      description: 'Mission alerts, system notifications, and team communications',
      icon: Bell,
      path: '/notifications',
      status: 'active',
      notifications: 12,
    },
    {
      title: 'OpsPlanner',
      description: 'Operations planning, mission scheduling, and tactical coordination',
      icon: Calendar,
      path: '/ops-planner',
      status: 'active',
    },
    {
      title: 'FacilityOps',
      description: 'Facility operations management and resource allocation',
      icon: Building2,
      path: '/facility-ops',
      status: 'active',
    },
    {
      title: 'IdentityVault',
      description: 'Secure identity management and credential storage',
      icon: UserCircle,
      path: '/identity-vault',
      status: 'inactive',
    },
  ];

  return (
    <DashboardLayout
      title="RANGER COMMAND CENTER"
      subtitle={`Welcome back, ${user?.callsign}. All systems operational.`}
    >
      {/* Quick Stats */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        <Card variant="glass">
          <div style={{ padding: '1rem' }}>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                marginBottom: '0.25rem',
              }}
            >
              ACTIVE MISSIONS
            </p>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '1.5rem',
                fontWeight: '700',
                color: 'var(--text-primary)',
              }}
            >
              3
            </p>
          </div>
        </Card>
        <Card variant="glass">
          <div style={{ padding: '1rem' }}>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                marginBottom: '0.25rem',
              }}
            >
              ALERTS
            </p>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '1.5rem',
                fontWeight: '700',
                color: '#e59019',
              }}
            >
              7
            </p>
          </div>
        </Card>
        <Card variant="glass">
          <div style={{ padding: '1rem' }}>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                marginBottom: '0.25rem',
              }}
            >
              TEAM STATUS
            </p>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '1.5rem',
                fontWeight: '700',
                color: '#29a399',
              }}
            >
              READY
            </p>
          </div>
        </Card>
        <Card variant="glass">
          <div style={{ padding: '1rem' }}>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                marginBottom: '0.25rem',
              }}
            >
              THREAT LEVEL
            </p>
            <p
              style={{
                fontFamily: 'monospace',
                fontSize: '1.5rem',
                fontWeight: '700',
                color: 'var(--primary)',
              }}
            >
              LOW
            </p>
          </div>
        </Card>
      </div>

      {/* Module Grid */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2
          style={{
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            color: 'var(--text-secondary)',
            marginBottom: '1rem',
            letterSpacing: '0.1em',
          }}
        >
          OPERATIONAL MODULES
        </h2>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
          gap: '1rem',
        }}
      >
        {modules.map((module) => {
          const IconComponent = module.icon;
          return (
            <Card
              key={module.path}
              variant="tactical"
              style={{
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(41, 163, 153, 0.4)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
              onClick={() => navigate(module.path)}
            >
              <CardContent
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    marginBottom: '1rem',
                  }}
                >
                  <div
                    style={{
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      backgroundColor: 'rgba(41, 163, 153, 0.08)',
                      border: '1px solid rgba(41, 163, 153, 0.15)',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <IconComponent size={24} color="#29a399" />
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                    }}
                  >
                    {module.notifications && module.notifications > 0 && (
                      <span
                        style={{
                          paddingLeft: '0.5rem',
                          paddingRight: '0.5rem',
                          paddingTop: '0.125rem',
                          paddingBottom: '0.125rem',
                          borderRadius: '9999px',
                          backgroundColor: 'rgba(229, 144, 25, 0.15)',
                          color: '#e59019',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                        }}
                      >
                        {module.notifications}
                      </span>
                    )}
                  </div>
                </div>

                <h3
                  style={{
                    fontFamily: 'monospace',
                    fontWeight: '600',
                    color: 'var(--text-primary)',
                    marginBottom: '0.25rem',
                    transition: 'color 0.2s ease',
                  }}
                >
                  {module.title}
                </h3>
                <p
                  style={{
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                  }}
                >
                  {module.description}
                </p>

                <div
                  style={{
                    marginTop: '1rem',
                    paddingTop: '1rem',
                    borderTop: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span
                    style={{
                      fontFamily: 'monospace',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    ACCESS LEVEL: RANGER
                  </span>
                  <span
                    style={{
                      fontFamily: 'monospace',
                      fontSize: '0.75rem',
                      color: 'var(--primary)',
                      opacity: 0,
                      transition: 'opacity 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = '1';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '0';
                    }}
                  >
                    ENTER →
                  </span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </DashboardLayout>
  );
}
