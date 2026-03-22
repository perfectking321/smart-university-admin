import React, { Suspense, useState } from 'react';
import Spline from '@splinetool/react-spline';
import type { Application } from '@splinetool/runtime';

interface SplineHeroProps {
  onLoad?: (splineApp: Application) => void;
  onStartQuerying?: () => void;
}

export const SplineHero: React.FC<SplineHeroProps> = ({ onLoad, onStartQuerying }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  const handleLoad = (splineApp: Application) => {
    console.log('✅ Spline 3D scene loaded successfully');
    setIsLoaded(true);

    // DISABLE ALL INTERACTIONS - purely visual scene
    if (splineApp.camera) {
      splineApp.camera.controls = false;
    }

    // Disable all mouse/touch events on the Spline scene
    const canvas = splineApp.renderer?.canvas;
    if (canvas) {
      canvas.style.pointerEvents = 'none';
      canvas.style.touchAction = 'none';
    }

    // Try to hide built-in text objects in the Spline scene
    try {
      const allObjects = splineApp.getAllObjects();
      allObjects.forEach((obj: any) => {
        const name = obj.name?.toLowerCase() || '';
        // Hide text objects that contain common text-related names
        if (name.includes('text') || name.includes('title') || name.includes('subtitle') ||
            name.includes('heading') || name.includes('button') || name.includes('waitlist') ||
            name.includes('redefining') || name.includes('productivity')) {
          obj.visible = false;
        }
      });
    } catch (e) {
      console.log('Could not hide Spline text objects:', e);
    }

    // Call parent onLoad handler if provided
    if (onLoad) {
      onLoad(splineApp);
    }
  };

  const handleError = () => {
    console.error('Failed to load Spline 3D scene');
    setError(true);
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* Loading State */}
      {!isLoaded && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black z-10">
          <div className="space-y-4 text-center">
            <div className="w-12 h-12 border-3 border-cyan-400/20 border-t-cyan-400 rounded-full animate-spin mx-auto" />
            <p className="text-cyan-300/60 text-sm font-mono">Loading 3D Experience...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black z-10">
          <div className="text-center space-y-4 max-w-md mx-auto px-6">
            <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto">
              <span className="text-red-400 text-2xl">⚠</span>
            </div>
            <h3 className="text-zinc-200 text-lg font-medium">Failed to Load 3D Scene</h3>
            <p className="text-zinc-400 text-sm">Please check your connection and try refreshing the page.</p>
          </div>
        </div>
      )}

      {/* Spline 3D Scene - Non-interactive */}
      <Suspense fallback={null}>
        <Spline
          scene="https://prod.spline.design/OC9-QHrIYJURCTbx/scene.splinecode"
          onLoad={handleLoad}
          onError={handleError}
          className={`w-full h-full transition-opacity duration-500 pointer-events-none ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            pointerEvents: 'none',
            touchAction: 'none'
          }}
        />
      </Suspense>

      {/* Custom Text Overlay - Replaces Spline's built-in text */}
      {isLoaded && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-20 pointer-events-none">
          <div className="text-center space-y-6 max-w-3xl mx-auto px-8">
            <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight leading-tight">
              Ask Your Database
              <br />
              <span className="bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
                Anything
              </span>
            </h1>
            <p className="text-lg md:text-xl text-cyan-100/60 max-w-2xl mx-auto leading-relaxed">
              Smart University Admin translates your questions about students,
              attendance, and courses into instant SQL results—no database knowledge required.
            </p>
            <div className="pt-4 pointer-events-auto">
              <button
                onClick={onStartQuerying}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-teal-500 text-white font-semibold rounded-full
                         hover:from-cyan-400 hover:to-teal-400 transition-all duration-300
                         shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:shadow-[0_0_40px_rgba(6,182,212,0.6)]
                         transform hover:scale-105"
              >
                Start Querying
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Scroll Indicator */}
      {isLoaded && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20">
          <div className="flex flex-col items-center space-y-2 animate-bounce">
            <p className="text-cyan-200/60 text-sm font-medium">Scroll to explore</p>
            <div className="w-6 h-10 border-2 border-cyan-400/30 rounded-full flex justify-center">
              <div className="w-1 h-3 bg-cyan-400/60 rounded-full mt-2 animate-pulse" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};