"use client";

import React from "react";

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start animate-pulse">
      {/* Left Column Skeletons */}
      <div className="lg:col-span-7 space-y-5">
        {/* Best Match Skeleton */}
        <div className="bg-white rounded-2xl border border-[#e5e0d8] p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div className="h-6 w-32 bg-[#e5e0d8] rounded-full" />
            <div className="h-6 w-24 bg-[#e5e0d8] rounded-xl" />
          </div>
          <div className="h-8 w-3/4 bg-[#e5e0d8] rounded-lg" />
          <div className="h-4 w-1/2 bg-[#e5e0d8] rounded-md" />
          <div className="grid grid-cols-4 gap-2.5 pt-2">
            <div className="h-20 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
            <div className="h-20 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
            <div className="h-20 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
            <div className="h-20 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
          </div>
        </div>

        {/* Timeline Skeleton */}
        <div className="bg-white rounded-2xl border border-[#e5e0d8] p-5 space-y-3">
          <div className="h-5 w-48 bg-[#e5e0d8] rounded-md" />
          <div className="flex gap-2 overflow-hidden">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 w-20 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl shrink-0" />
            ))}
          </div>
        </div>

        {/* Breakdown Skeleton */}
        <div className="bg-white rounded-2xl border border-[#e5e0d8] p-5 space-y-3">
          <div className="h-5 w-36 bg-[#e5e0d8] rounded-md" />
          <div className="grid grid-cols-2 gap-3">
            <div className="h-28 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
            <div className="h-28 bg-[#faf8f5] border border-[#e5e0d8] rounded-xl" />
          </div>
        </div>
      </div>

      {/* Right Column Skeletons */}
      <div className="lg:col-span-5 space-y-5">
        <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 h-[420px] flex flex-col items-center justify-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#e5e0d8]" />
          <div className="h-4 w-40 bg-[#e5e0d8] rounded-md" />
          <div className="text-xs text-[#829288]">Analyzing live atmospheric and geospatial telemetry...</div>
        </div>
      </div>
    </div>
  );
};
