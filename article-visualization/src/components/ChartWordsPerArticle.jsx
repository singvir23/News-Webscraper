// src/components/ChartWordsPerArticle.jsx

import React, { useState } from 'react';
import {
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ZAxis,
} from 'recharts';

const categories = ['All', 'sports', 'health', 'science', 'politics', 'world'];

/**
 * Group duplicates by (x, y, source) to aggregate frequency in `z`.
 */
function groupPoints(points) {
  const map = new Map();
  for (const pt of points) {
    // Key includes x, y, source
    const key = `${pt.x}-${pt.y}-${pt.source}`;
    if (!map.has(key)) {
      map.set(key, { ...pt, z: 0 });
    }
    map.get(key).z += 1;
  }
  return [...map.values()];
}

function ChartWordsPerArticle({ data }) {
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Filter + map to (x, y) for scatter
  const filteredData = data
    .filter(article =>
      selectedCategory === 'All'
        ? true
        : article.category.toLowerCase() === selectedCategory.toLowerCase()
    )
    .map((article, idx) => ({
      x: idx,
      y: article.wordCount,
      title: article.title,
      source: article.source,
    }));

  // Group duplicates
  const groupedData = groupPoints(filteredData);

  // Separate by source
  const cnnData = groupedData.filter(d => d.source === 'CNN');
  const foxData = groupedData.filter(d => d.source === 'FOX');

  return (
    <div className="w-full p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Words per Article</h2>
      
      <select
        value={selectedCategory}
        onChange={(e) => setSelectedCategory(e.target.value)}
        className="mb-4 p-2 border rounded"
      >
        {categories.map(cat => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>

      <ScatterChart
        width={800}
        height={400}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <CartesianGrid />
        <XAxis
          type="number"
          dataKey="x"
          name="Article Index"
          label={{ value: 'Article Index', position: 'bottom' }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name="Word Count"
          label={{ value: 'Word Count', angle: -90, position: 'insideLeft' }}
          domain={['dataMin', 'dataMax']}
        />

        {/* 
          ZAxis for bubble frequency. 
          Increase or decrease the [min, max] range as needed.
        */}
        <ZAxis
          type="number"
          dataKey="z"
          range={[50, 400]}
          name="Frequency"
        />

        <Tooltip
          cursor={{ strokeDasharray: '3 3' }}
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const d = payload[0].payload;
              return (
                <div className="bg-white border p-2 shadow">
                  <p className="font-bold">{d.title}</p>
                  <p>Words: {d.y}</p>
                  <p>Source: {d.source}</p>
                  <p>Count: {d.z}</p>
                </div>
              );
            }
            return null;
          }}
        />
        <Legend />

        <Scatter
          name="CNN"
          data={cnnData}
          fill="#FF0000"
          stroke="#333"
          strokeWidth={1}
          fillOpacity={0.7}
        />
        <Scatter
          name="FOX"
          data={foxData}
          fill="#0000FF"
          stroke="#333"
          strokeWidth={1}
          fillOpacity={0.7}
        />
      </ScatterChart>
    </div>
  );
}

export default ChartWordsPerArticle;
