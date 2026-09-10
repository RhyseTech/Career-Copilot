import React from 'react';
import { RequirementScore } from '../../types/phase5';
import { RequirementCard } from './RequirementCard';

interface RequirementCoverageListProps {
  scores: RequirementScore[];
}

export const RequirementCoverageList: React.FC<RequirementCoverageListProps> = ({ scores }) => {
  // Sort scores: Required first, then by coverage descending
  const sortedScores = [...scores].sort((a, b) => {
    if (a.requirement_type !== b.requirement_type) {
      return a.requirement_type === 'REQUIRED' ? -1 : 1;
    }
    return b.coverage - a.coverage;
  });

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold text-gray-200 mb-4">Requirement Coverage</h3>
      <div className="space-y-3">
        {sortedScores.map(score => (
          <RequirementCard key={score.requirement_id} score={score} />
        ))}
      </div>
    </div>
  );
};
