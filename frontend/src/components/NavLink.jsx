import { NavLink as RouterNavLink, useLocation } from 'react-router-dom';
import { forwardRef } from 'react';

const NavLink = forwardRef(
  (
    {
      to,
      style,
      activeStyle,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    const baseStyle = {
      textDecoration: 'none',
      color: 'var(--text-primary)',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
      fontSize: '0.875rem',
      padding: '0.5rem 1rem',
      borderRadius: '0.375rem',
      transition: 'all 0.2s ease',
      cursor: 'pointer',
      display: 'inline-block',
      ...style,
    };

    const finalStyle = isActive
      ? {
          ...baseStyle,
          backgroundColor: 'rgba(41, 163, 153, 0.08)',
          borderColor: 'rgba(41, 163, 153, 0.2)',
          color: 'var(--primary)',
          ...activeStyle,
        }
      : baseStyle;

    return (
      <RouterNavLink
        ref={ref}
        to={to}
        style={finalStyle}
        onMouseEnter={(e) => {
          if (!isActive) {
            e.currentTarget.style.backgroundColor = 'rgba(41, 163, 153, 0.04)';
            e.currentTarget.style.color = 'var(--primary)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isActive) {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = 'var(--text-primary)';
          }
        }}
        {...props}
      >
        {children}
      </RouterNavLink>
    );
  }
);

NavLink.displayName = 'NavLink';

export { NavLink };
