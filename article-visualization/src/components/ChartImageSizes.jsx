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
  BarChart,
  Bar,
  Cell
} from 'recharts';
import { COLORS } from '../constants';

// Import the CSS file
import './ChartImageSizes.css';

const categories = ['All', 'sports', 'health', 'science', 'politics'];

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

  // Filter articles based on selected category
  const filteredArticles = data.filter(article =>
    selectedCategory === 'All' ||
    article.category.toLowerCase() === selectedCategory.toLowerCase()
  );

  // Flatten and filter image data
  const allPoints = [];
  filteredArticles.forEach(article => {
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
  });

  // Group duplicates: same (width, height, source) => bigger bubble
  const groupedPoints = groupImagePoints(allPoints);

  // Separate data into sources
  const sources = [...new Set(groupedPoints.map(d => d.source))];

  // Prepare bar chart data: total images per source
  const barData = sources.map(source => {
    const totalImages = groupedPoints
      .filter(d => d.source === source)
      .reduce((acc, d) => acc + d.z, 0);
    return { source, totalImages };
  });

  // Set chart dimensions for side-by-side charts
  const chartWidth = 400;
  const chartHeight = 400;

  return (
    <div className="chart-image-sizes-container">
      <h2 className="chart-image-sizes-title">Number of images by size (width × height)</h2>

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

      {/* Display total number of articles */}
      <p className="total-articles">Total Articles: {filteredArticles.length}</p>

      <div className="charts-flex-container">
        {/* Scatter Chart */}
        <div className="scatter-chart-container">
          <ScatterChart
            width={chartWidth}
            height={chartHeight}
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

        {/* Bar Chart */}
        <div className="bar-chart-container">
          <BarChart
            width={chartWidth}
            height={chartHeight}
            data={barData}
            margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
          >
            <CartesianGrid stroke="#444" />
            <XAxis
              dataKey="source"
              label={{ value: 'Source', position: 'bottom', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
            />
            <YAxis
              label={{ value: 'Total Images', angle: -90, position: 'insideLeft', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="custom-tooltip">
                      <p className="tooltip-title">Source: {d.source}</p>
                      <p>Total Images: {d.totalImages}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend verticalAlign="top" height={36} />
            <Bar dataKey="totalImages">
              {barData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[entry.source] || "#8884d8"}
                />
              ))}
            </Bar>
          </BarChart>
        </div>
      </div>
    </div>
  );
}

export default ChartImageSizes;
