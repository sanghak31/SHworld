import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { atoms, getMoleculeInfo } from './chemistryData';
import MoleculeVisualizer from './MoleculeVisualizer';

export default function AtomCombinerApp() {
  const [selectedAtoms, setSelectedAtoms] = useState([]);
  const [result, setResult] = useState(null);

  const addAtom = (atom) => {
    setSelectedAtoms([...selectedAtoms, atom]);
  };

  const combineAtoms = () => {
    const molecule = getMoleculeInfo(selectedAtoms);
    setResult(molecule);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">원자 결합 시뮬레이터</h1>
      <div className="grid grid-cols-5 gap-2 mb-4">
        {atoms.map((atom) => (
          <Button key={atom.symbol} onClick={() => addAtom(atom)}>
            {atom.symbol}
          </Button>
        ))}
      </div>

      <Card className="mb-4">
        <CardContent>
          <h2 className="text-lg font-semibold">선택된 원자들</h2>
          <div className="flex flex-wrap gap-2 mt-2">
            {selectedAtoms.map((atom, index) => (
              <span key={index}>{atom.symbol}</span>
            ))}
          </div>
        </CardContent>
      </Card>

      <Button className="mb-4" onClick={combineAtoms}>결합</Button>

      {result && (
        <Card>
          <CardContent>
            <h2 className="text-lg font-semibold">결과</h2>
            <p>분자: {result.name}</p>
            <p>결합 종류: {result.bondType}</p>
            <p>특성: {result.properties}</p>
            <div className="mt-4">
              <MoleculeVisualizer molecule={result.visual} />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
