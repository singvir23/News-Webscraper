import React, { useState, useMemo } from 'react';
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
  Bar
} from 'recharts';
import { COLORS } from '../constants';

// Import the CSS file
import './ChartImagesPerArticle.css';

const categories = ['All', 'sports', 'health', 'science', 'politics'];

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
  const [minImageCount, setMinImageCount] = useState('');
  const [maxImageCount, setMaxImageCount] = useState('');

  // Determine the default max image count from data
  const defaultMax = useMemo(() => {
    if (data.length === 0) return 10;
    return Math.max(...data.map(article => article.images.length));
  }, [data]);

  // Handle changes for min and max inputs
  const handleMinChange = (e) => {
    const value = e.target.value;
    setMinImageCount(value === '' ? '' : Number(value));
  };

  const handleMaxChange = (e) => {
    const value = e.target.value;
    setMaxImageCount(value === '' ? '' : Number(value));
  };

  // Filter + map to (x, y) for scatter
  const filteredData = data
    .filter(article => {
      const categoryMatch =
        selectedCategory === 'All'
          ? true
          : article.category.toLowerCase() === selectedCategory.toLowerCase();

      const minMatch = minImageCount === '' || article.images.length >= minImageCount;
      const maxMatch = maxImageCount === '' || article.images.length <= maxImageCount;

      return categoryMatch && minMatch && maxMatch;
    })
    .map((article, idx) => ({
      x: idx,
      y: article.images.length,
      title: article.title,
      source: article.source,
    }));

  // Group duplicates by (x, y, source)
  const groupedData = groupPoints(filteredData);

  // Separate by source for scatter chart
  const sources = [...new Set(groupedData.map(d => d.source))];

  // Calculate bar chart data: distribution of articles by image count
  const imageCountDistribution = {};
  filteredData.forEach(article => {
    const count = article.y; // number of images
    imageCountDistribution[count] = (imageCountDistribution[count] || 0) + 1;
  });
  const barData = Object.keys(imageCountDistribution).map(key => ({
    imageCount: Number(key),
    articles: imageCountDistribution[key]
  }));

  // Set chart dimensions
  const chartWidth = 400;
  const chartHeight = 400;

  return (
    <div className="chart-images-container">
      <h2 className="chart-images-title">Number of Images per Article</h2>

      <div className="chart-images-filters">
        {/* Category Select */}
        <div className="chart-images-select-container">
          <label htmlFor="category-select" className="chart-images-label">
            Category:
          </label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="chart-images-select"
          >
            {categories.map(cat => (
              <option
                key={cat}
                value={cat}
                className="chart-images-option"
              >
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Image Count Range Inputs */}
        <div className="chart-images-range-container">
          <div className="chart-images-range-item">
            <label htmlFor="min-image" className="chart-images-label">
              Min Images:
            </label>
            <input
              type="number"
              id="min-image"
              value={minImageCount}
              onChange={handleMinChange}
              placeholder="0"
              className="chart-images-input"
              min="0"
            />
          </div>
          <div className="chart-images-range-item">
            <label htmlFor="max-image" className="chart-images-label">
              Max Images:
            </label>
            <input
              type="number"
              id="max-image"
              value={maxImageCount}
              onChange={handleMaxChange}
              placeholder={defaultMax}
              className="chart-images-input"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Display total number of articles */}
      <p className="total-articles">Total Articles: {filteredData.length}</p>

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
              name="Article Index"
              label={{ value: 'Article Index', position: 'bottom', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Number of Images"
              label={{ value: 'Number of Images', angle: -90, position: 'insideLeft', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
              domain={['auto', 'auto']}
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
                      <p>Images: {d.y}</p>
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
              dataKey="imageCount"
              label={{ value: 'Image Count', position: 'bottom', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
            />
            <YAxis
              label={{ value: 'Articles', angle: -90, position: 'insideLeft', fill: '#ccc' }}
              tick={{ fill: '#ccc' }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="custom-tooltip">
                      <p className="tooltip-title">Image Count: {d.imageCount}</p>
                      <p>Articles: {d.articles}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend verticalAlign="top" height={36} />
            <Bar dataKey="articles" fill="#82ca9d" />
          </BarChart>
        </div>
      </div>
    </div>
  );
}

export default ChartImagesPerArticle;
