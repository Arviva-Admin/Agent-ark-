'use client';

import { useState } from 'react';

export default function Home() {
  const [goal, setGoal] = useState('Bygg och testa applikationen');
  const [status, setStatus] = useState('idle');
  const [log, setLog] = useState('');

  const runAgent = async () => {
    setStatus('running');
    const response = await fetch('http://localhost:8000/api/agent/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal, max_iterations: 20 }),
    });
    const data = await response.json();
    setStatus(data.status);
    setLog(`${data.message} (steg: ${data.completed_steps})`);
  };

  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif' }}>
      <h1>Arviva Agent UI</h1>
      <textarea value={goal} onChange={(e) => setGoal(e.target.value)} rows={4} style={{ width: '100%' }} />
      <br />
      <button onClick={runAgent}>Kör agent</button>
      <p>Status: {status}</p>
      <pre>{log}</pre>
    </main>
  );
}
