import React from 'react';
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { RequirementCard } from './RequirementCard';
import { RequirementScore } from '../../types/phase5';

test('RequirementCard renders coverage correctly without coverage_percentage', () => {
  const mockScore: RequirementScore = {
    requirement_id: 'req_123',
    requirement_text: 'Python Development',
    requirement_type: 'REQUIRED',
    is_hard_constraint: false,
    weight: 1.0,
    coverage: 0.5,
    requirement_score: 0.5,
    contributing_atom_ids: [],
    contributing_evidence_ids: [],
    contributing_match_edge_ids: [],
    atom_scores: [],
    qualifier_evaluations: [],
    deterministic_explanation: 'Testing coverage'
  };

  render(<RequirementCard score={mockScore} />);

  // Should render 50%
  const coverageText = screen.getByText('50%');
  expect(coverageText).toBeDefined();
});

test('RequirementCard renders 0% coverage correctly', () => {
  const mockScore: RequirementScore = {
    requirement_id: 'req_123',
    requirement_text: 'Python Development',
    requirement_type: 'REQUIRED',
    is_hard_constraint: false,
    weight: 1.0,
    coverage: 0.0,
    requirement_score: 0.0,
    contributing_atom_ids: [],
    contributing_evidence_ids: [],
    contributing_match_edge_ids: [],
    atom_scores: [],
    qualifier_evaluations: [],
    deterministic_explanation: 'Testing coverage'
  };

  render(<RequirementCard score={mockScore} />);

  const coverageText = screen.getByText('0%');
  expect(coverageText).toBeDefined();
});

test('RequirementCard renders 100% coverage correctly', () => {
  const mockScore: RequirementScore = {
    requirement_id: 'req_123',
    requirement_text: 'Python Development',
    requirement_type: 'REQUIRED',
    is_hard_constraint: false,
    weight: 1.0,
    coverage: 1.0,
    requirement_score: 1.0,
    contributing_atom_ids: [],
    contributing_evidence_ids: [],
    contributing_match_edge_ids: [],
    atom_scores: [],
    qualifier_evaluations: [],
    deterministic_explanation: 'Testing coverage'
  };

  render(<RequirementCard score={mockScore} />);

  const coverageText = screen.getByText('100%');
  expect(coverageText).toBeDefined();
});

test('RequirementCard renders 8% coverage correctly for 0.07638', () => {
  const mockScore: RequirementScore = {
    requirement_id: 'req_123',
    requirement_text: 'Python Development',
    requirement_type: 'REQUIRED',
    is_hard_constraint: false,
    weight: 1.0,
    coverage: 0.07638,
    requirement_score: 0.07638,
    contributing_atom_ids: [],
    contributing_evidence_ids: [],
    contributing_match_edge_ids: [],
    atom_scores: [],
    qualifier_evaluations: [],
    deterministic_explanation: 'Testing coverage'
  };

  render(<RequirementCard score={mockScore} />);

  const coverageText = screen.getByText('8%');
  expect(coverageText).toBeDefined();
});
