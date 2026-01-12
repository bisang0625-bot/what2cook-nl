'use client'

import { useEffect, useState } from 'react'

export default function TestPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    try {
      // Dynamic import to test
      import('@/data/weekly_recipes.json').then((module) => {
        setData(module.default)
      }).catch((err) => {
        setError(err.message)
      })
    } catch (err: any) {
      setError(err.message)
    }
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Debug Test Page</h1>
      <div>
        <h2>Status:</h2>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        {data && (
          <div>
            <p style={{ color: 'green' }}>✅ Data loaded successfully!</p>
            <p>Recipes count: {data.length}</p>
            <pre style={{ background: '#f5f5f5', padding: '10px' }}>
              {JSON.stringify(data[0], null, 2)}
            </pre>
          </div>
        )}
        {!data && !error && <p>Loading...</p>}
      </div>
    </div>
  )
}
