import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
// @ts-ignore - vanta distribution lacks ambient declaration
import NET from 'vanta/dist/vanta.net.min';

interface VantaBackgroundProps {
  children?: React.ReactNode;
  className?: string;
  points?: number;
  maxDistance?: number;
}

export const VantaBackground: React.FC<VantaBackgroundProps> = ({
  children,
  className = '',
  points = 8.0,
  maxDistance = 20.0,
}) => {
  const vantaRef = useRef<HTMLDivElement>(null);
  const [vantaEffect, setVantaEffect] = useState<any>(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    if (!vantaEffect && vantaRef.current) {
      try {
        const effect = NET({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: false,
          gyroControls: false,
          minHeight: 200.0,
          minWidth: 200.0,
          scale: 1.0,
          scaleMobile: 0.75,
          color: 0x38bdf8,
          backgroundColor: 0x090d16,
          points: points,
          maxDistance: maxDistance,
          spacing: 18.0,
        });
        setVantaEffect(effect);
      } catch (err) {
        console.warn('WebGL or Vanta initialization skipped:', err);
      }
    }

    return () => {
      if (vantaEffect) {
        try {
          vantaEffect.destroy();
        } catch (e) {}
      }
    };
  }, [vantaEffect, points, maxDistance]);

  return (
    <div
      ref={vantaRef}
      className={`relative w-full h-full bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 ${className}`}
    >
      {children}
    </div>
  );
};
