import React from 'react';
import { Phase5Score } from '../../types/phase5';
import { MatchScoreCard } from './MatchScoreCard';
import { ConstraintAlert } from './ConstraintAlert';
import { RequirementCoverageList } from './RequirementCoverageList';

interface Phase5DashboardProps {
  scoreData: Phase5Score;
}

export const Phase5Dashboard: React.FC<Phase5DashboardProps> = ({ scoreData }) => {
  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* 1. Primary Score / Match Dashboard */}
      <MatchScoreCard 
        finalScore={scoreData.final_score}
        baseScore={scoreData.base_score}
        constraintGate={scoreData.constraint_gate}
        requiredCoverage={scoreData.required_coverage}
        preferredCoverage={scoreData.preferred_coverage}
        configVersion={scoreData.scoring_config_version}
      />

      {/* 2. Hard Constraints Alert (conditionally rendered) */}
      <ConstraintAlert failedConstraints={scoreData.hard_constraints_failed} />

      {/* 3. Requirement Coverage Breakdown */}
      <RequirementCoverageList scores={scoreData.requirement_scores} />

    </div>
  );
};
