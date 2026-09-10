import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ConstraintAlertProps {
  failedConstraints: string[];
}

export const ConstraintAlert: React.FC<ConstraintAlertProps> = ({ failedConstraints }) => {
  if (!failedConstraints || failedConstraints.length === 0) {
    return null; // Don't show scary warning if no constraints failed
  }

  return (
    <div className="bg-red-500/10 border-l-4 border-red-500 p-6 rounded-r-xl my-6">
      <div className="flex items-start gap-4">
        <AlertTriangle className="text-red-500 w-6 h-6 mt-1 flex-shrink-0" />
        <div>
          <h3 className="text-red-400 font-bold text-lg mb-2 uppercase tracking-wide">Hard Constraint Failed</h3>
          <p className="text-gray-300 text-sm mb-3">
            One or more mandatory requirements (Hard Constraints) were not satisfied by the candidate&apos;s evidence.
          </p>
          <div className="bg-red-950/30 p-3 rounded border border-red-500/20 text-sm text-red-200">
            <span className="font-semibold block mb-1">Score Impact:</span>
            Constraint Gate applied. Final score is forced to 0.
          </div>
          
          {/* We only have IDs in the root array, but the detail will be in the requirement cards below */}
          <div className="mt-3 text-xs text-red-400/70 font-mono">
            Affected Requirement IDs: {failedConstraints.join(', ')}
          </div>
        </div>
      </div>
    </div>
  );
};
