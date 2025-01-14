// src/components/ChartImageSizes.jsx

import React, { useState } from 'react';
import {
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ZAxis
} from 'recharts';

const categories = ['All', 'sports', 'health', 'science', 'politics', 'world'];

/**
 * Groups points that share the same (x, y, source) and sets `z` = frequency.
 */
function groupImagePoints(points) {
  const map = new Map();
  for (const pt of points) {
    const key = `${pt.x}-${pt.y}-${pt.source}`;
    if (!map.has(key)) {
      map.set(key, { ...pt, z: 0 });
    }
    map.get(key).z += 1;
  }
  return [...map.values()];
}

function ChartImageSizes({ data }) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  // Flatten and filter image data
  const allPoints = [];
  data.forEach(article => {
    if (
      selectedCategory === 'All' ||
      article.category.toLowerCase() === selectedCategory.toLowerCase()
    ) {
      article.images.forEach(img => {
        if (img.width && img.height) {  
          allPoints.push({
            x: img.width,
            y: img.height,
            title: article.title,
            source: article.source
          });
        }
      });
    }
  });

  // Group duplicates: safame (width, height, source) => bigger bubble
  const groupedPoints = groupImagePoints(allPoints);

  // Separate data into CNN vs FOX
  const cnnData = groupedPoints.filter(d => d.source === 'CNN');
  const foxData = groupedPoints.filter(d => d.source === 'FOX');

  return (
    <div className="w-full p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Image Sizes (width × height)</h2>
      
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
          name="Width"
          label={{ value: 'Width (px)', position: 'bottom' }}
          domain={['dataMin', 'dataMax']}
        />
        <YAxis
          type="number"
          dataKey="y"
          name="Height"
          label={{ value: 'Height (px)', angle: -90, position: 'insideLeft' }}
          domain={['dataMin', 'dataMax']}
        />
        {/*
          ZAxis: uses the `z` field for bubble size.
          Adjust range as needed so the largest bubble 
          doesn’t cover the entire chart.
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
                  <p>{d.x} × {d.y} px</p>
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

export default ChartImageSizes;
