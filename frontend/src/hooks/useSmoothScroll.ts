import { useEffect } from 'react';
import Lenis from 'lenis';

export const useSmoothScroll = (enabled: boolean = true) => {
  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    // Strict reduced motion check
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    let lenis: Lenis | null = null;
    let rafId: number;

    try {
      lenis = new Lenis({
        duration: 1.1,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        touchMultiplier: 1.5,
        infinite: false,
      });

      const raf = (time: number) => {
        lenis?.raf(time);
        rafId = requestAnimationFrame(raf);
      };
      rafId = requestAnimationFrame(raf);
    } catch (err) {
      console.warn('Lenis smooth scroll skipped:', err);
    }

    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      if (lenis) {
        try {
          lenis.destroy();
        } catch (e) {}
      }
    };
  }, [enabled]);
};
