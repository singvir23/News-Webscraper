// src/components/ChartImagesPerArticle.jsx

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
    // Key includes x, y, source so we track each unique coordinate + source
    const key = `${pt.x}-${pt.y}-${pt.source}`;
    if (!map.has(key)) {
      map.set(key, { ...pt, z: 0 });
    }
    map.get(key).z += 1;
  }
  return [...map.values()];
}

function ChartImagesPerArticle({ data }) {
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Filter data by category and create data points
  const filteredData = data
    .filter(article =>
      selectedCategory === 'All'
        ? true
        : article.category.toLowerCase() === selectedCategory.toLowerCase()
    )
    .map((article, index) => ({
      x: index,
      y: article.images.length,
      title: article.title,
      source: article.source,
    }));

  // Group duplicates by (x, y, source)
  const groupedData = groupPoints(filteredData);

  // Split by source if you want distinct bubbles per source
  const cnnData = groupedData.filter(d => d.source === 'CNN');
  const foxData = groupedData.filter(d => d.source === 'FOX');

  return (
    <div className="w-full p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Number of Images per Article</h2>
      
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
          name="Number of Images"
          label={{ value: 'Number of Images', angle: -90, position: 'insideLeft' }}
        />
        {/* 
          ZAxis will control bubble sizes based on the `z` value (frequency).
          Adjust range to suit your data size. 
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
                  <p>Images: {d.y}</p>
                  <p>Source: {d.source}</p>
                  <p>Count: {d.z}</p>
                </div>
              );
            }
            return null;
          }}
        />
        <Legend />
        
        {/* Use partial opacity and stroke so large bubbles don't hide smaller ones */}
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

export default ChartImagesPerArticle;
