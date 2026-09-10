import React from 'react';

interface MatchScoreCardProps {
  finalScore: number;
  baseScore: number;
  constraintGate: number;
  requiredCoverage: number;
  preferredCoverage: number;
  configVersion: string;
}

export const MatchScoreCard: React.FC<MatchScoreCardProps> = ({
  finalScore,
  baseScore,
  constraintGate,
  requiredCoverage,
  preferredCoverage,
  configVersion
}) => {
  // Determine color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-blue-400";
    if (score >= 40) return "text-yellow-400";
    return "text-red-400";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "from-emerald-500/20 to-emerald-500/10 border-emerald-500/50";
    if (score >= 60) return "from-blue-500/20 to-blue-500/10 border-blue-500/50";
    if (score >= 40) return "from-yellow-500/20 to-yellow-500/10 border-yellow-500/50";
    return "from-red-500/20 to-red-500/10 border-red-500/50";
  };

  const formattedScore = Math.round(finalScore);
  const colorClass = getScoreColor(formattedScore);
  const bgClass = getScoreBg(formattedScore);

  return (
    <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800 shadow-xl flex flex-col md:flex-row items-center gap-8">
      {/* Primary Score */}
      <div className={`flex flex-col items-center justify-center p-8 rounded-full border-4 aspect-square min-w-[200px] bg-gradient-to-br ${bgClass}`}>
        <span className="text-sm font-bold text-gray-400 tracking-wider uppercase mb-1">JD Match</span>
        <div className="flex items-baseline gap-1">
          <span className={`text-6xl font-black ${colorClass}`}>{formattedScore}</span>
          <span className="text-2xl text-gray-500">/ 100</span>
        </div>
      </div>

      {/* Metrics Breakdown */}
      <div className="flex-1 grid grid-cols-2 gap-x-8 gap-y-6 w-full">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-300 font-medium">Required Coverage</span>
            <span className="text-white font-bold">{(requiredCoverage * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${requiredCoverage * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-300 font-medium">Preferred Coverage</span>
            <span className="text-white font-bold">{(preferredCoverage * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${preferredCoverage * 100}%` }}></div>
          </div>
        </div>

        <div className="col-span-2 pt-4 border-t border-gray-800 flex justify-between items-center text-sm">
          <div className="flex gap-6">
            <div>
              <span className="text-gray-500 mr-2">Base Score</span>
              <span className="text-gray-200 font-mono">{baseScore.toFixed(1)}</span>
            </div>
            <div>
              <span className="text-gray-500 mr-2">Constraint Gate</span>
              <span className="text-gray-200 font-mono">{constraintGate.toFixed(2)}x</span>
            </div>
          </div>
          <div className="text-xs text-gray-600 font-mono">
            v{configVersion}
          </div>
        </div>
      </div>
    </div>
  );
};
