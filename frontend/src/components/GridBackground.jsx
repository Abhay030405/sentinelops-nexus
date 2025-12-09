import React from 'react';

/**
 * GridBackground Component
 * Provides tactical grid background with scanning line and corner accents
 */
export default function GridBackground() {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      pointerEvents: 'none',
      overflow: 'hidden',
      zIndex: 1,
    }}>
      {/* Grid pattern */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'linear-gradient(rgba(41, 163, 153, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(41, 163, 153, 0.08) 1px, transparent 1px)',
        backgroundSize: '50px 50px',
        opacity: 0.5
      }} />

      {/* Scanning line effect */}
      <div style={{
        position: 'absolute',
        left: 0,
        right: 0,
        height: '8rem',
        background: 'linear-gradient(180deg, rgba(41, 163, 153, 0) 0%, rgba(41, 163, 153, 0.2) 50%, rgba(41, 163, 153, 0) 100%)',
        opacity: 0.4,
        animation: 'scan 6s linear infinite'
      }} />

      {/* Top-left corner accent */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '8rem',
        height: '8rem',
        borderLeft: '2px solid rgba(41, 163, 153, 0.15)',
        borderTop: '2px solid rgba(41, 163, 153, 0.15)'
      }} />

      {/* Top-right corner accent */}
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: '8rem',
        height: '8rem',
        borderRight: '2px solid rgba(41, 163, 153, 0.15)',
        borderTop: '2px solid rgba(41, 163, 153, 0.15)'
      }} />

      {/* Bottom-left corner accent */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        width: '8rem',
        height: '8rem',
        borderLeft: '2px solid rgba(41, 163, 153, 0.15)',
        borderBottom: '2px solid rgba(41, 163, 153, 0.15)'
      }} />

      {/* Bottom-right corner accent */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        right: 0,
        width: '8rem',
        height: '8rem',
        borderRight: '2px solid rgba(41, 163, 153, 0.15)',
        borderBottom: '2px solid rgba(41, 163, 153, 0.15)'
      }} />

      {/* Glow effects */}
      <div style={{
        position: 'absolute',
        top: '25%',
        left: '25%',
        width: '24rem',
        height: '24rem',
        background: 'rgba(41, 163, 153, 0.1)',
        borderRadius: '9999px',
        filter: 'blur(96px)'
      }} />

      <div style={{
        position: 'absolute',
        bottom: '25%',
        right: '25%',
        width: '24rem',
        height: '24rem',
        background: 'rgba(229, 144, 25, 0.1)',
        borderRadius: '9999px',
        filter: 'blur(96px)'
      }} />

      <style>{`
        @keyframes scan {
          0% {
            transform: translateY(-100%);
          }
          100% {
            transform: translateY(100vh);
          }
        }
      `}</style>
    </div>
  );
}
