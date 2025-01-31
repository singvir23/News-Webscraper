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
import { COLORS } from '../constants';

// Import the CSS file
import './ChartWordsPerArticle.css';

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
  const sources = [...new Set(groupedData.map(d => d.source))];

  return (
    <div className="chart-words-container">
      <h2 className="chart-words-title">Words per Article</h2>

      <div className="chart-words-select-container">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="chart-words-select"
        >
          {categories.map(cat => (
            <option
              key={cat}
              value={cat}
              className="chart-words-option"
            >
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="chart-words-chart-container">
        <ScatterChart
          width={800}
          height={400}
          margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
        >
          <CartesianGrid stroke="#444" />
          <XAxis
            type="number"
            dataKey="x"
            name="Article Index"
            label={{ value: 'Article Index', position: 'bottom', fill: '#ccc' }}
            tick={{ fill: '#ccc' }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Word Count"
            label={{ value: 'Word Count', angle: -90, position: 'insideLeft', fill: '#ccc' }}
            tick={{ fill: '#ccc' }}
            domain={['dataMin', 'dataMax']}
          />

          {/* ZAxis for bubble frequency. Adjust range as needed. */}
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
                    <p>Words: {d.y}</p>
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
              data={groupedData.filter(d => d.source === source)}
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

export default ChartWordsPerArticle;
