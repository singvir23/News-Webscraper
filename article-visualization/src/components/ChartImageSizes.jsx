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
  ZAxis,
} from 'recharts';
import { COLORS } from '../constants';

// Import the CSS file
import './ChartImageSizes.css';

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

  // Group duplicates: same (width, height, source) => bigger bubble
  const groupedPoints = groupImagePoints(allPoints);

  // Separate data into sources
  const sources = [...new Set(groupedPoints.map(d => d.source))];

  return (
    <div className="chart-image-sizes-container">
      <h2 className="chart-image-sizes-title">Image Sizes (width × height)</h2>

      <div className="chart-image-sizes-select-container">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="chart-image-sizes-select"
        >
          {categories.map(cat => (
            <option
              key={cat}
              value={cat}
              className="chart-image-sizes-option"
            >
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="chart-image-sizes-chart-container">
        <ScatterChart
          width={800}
          height={400}
          margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
        >
          <CartesianGrid stroke="#444" />
          <XAxis
            type="number"
            dataKey="x"
            name="Width"
            label={{ value: 'Width (px)', position: 'bottom', fill: '#ccc' }}
            tick={{ fill: '#ccc' }}
            domain={['dataMin', 'dataMax']}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Height"
            label={{ value: 'Height (px)', angle: -90, position: 'insideLeft', fill: '#ccc' }}
            tick={{ fill: '#ccc' }}
            domain={['dataMin', 'dataMax']}
          />

          {/* ZAxis: uses the `z` field for bubble size. Adjust range as needed */}
          <ZAxis
            type="number"
            dataKey="z"
            range={[60, 300]}
            name="Frequency"
            stroke="#ccc"
          />

          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                return (
                  <div className="custom-tooltip">
                    <p className="tooltip-title">{d.title}</p>
                    <p>{d.x} × {d.y} px</p>
                    <p>Source: {d.source}</p>
                    <p>Count: {d.z}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend verticalAlign="top" height={36} />

          {sources.map(source => (
            <Scatter
              key={source}
              name={source}
              data={groupedPoints.filter(d => d.source === source)}
              fill={COLORS[source]}
              stroke={COLORS[source]}
              fillOpacity={0.6}
            />
          ))}
        </ScatterChart>
      </div>
    </div>
  );
}

export default ChartImageSizes;
