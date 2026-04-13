import { describe, it, expect } from 'vitest';
import { arcColour, ARC_PALETTE } from '@/lib/graph-colours';

describe('arcColour', () => {
  it('returns the first palette colour for index 0', () => {
    expect(arcColour(0)).toBe(ARC_PALETTE[0]);
  });

  it('returns the correct colour for a middle index', () => {
    expect(arcColour(4)).toBe(ARC_PALETTE[4]);
  });

  it('wraps around when index exceeds palette length', () => {
    expect(arcColour(8)).toBe(ARC_PALETTE[0]);
    expect(arcColour(9)).toBe(ARC_PALETTE[1]);
  });

  it('wraps correctly for large indices', () => {
    expect(arcColour(803)).toBe(ARC_PALETTE[803 % 8]);
  });
});
