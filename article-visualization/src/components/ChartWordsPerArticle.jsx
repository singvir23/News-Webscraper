import React, { useState, useMemo, useEffect } from 'react';
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
import LoadingSpinner from './LoadingSpinner'; // Import the spinner

// Import the CSS file
import './ChartWordsPerArticle.css';

const categories = ['All', 'sports', 'health', 'science', 'politics'];

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
  const [minWordCount, setMinWordCount] = useState('');
  const [maxWordCount, setMaxWordCount] = useState('');
  const [isLoading, setIsLoading] = useState(true); // Loading state

  // Simulate data loading (remove if data is already loaded)
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000); // 1-second delay

    return () => clearTimeout(timer);
  }, [data]);

  // Determine the default max word count from data
  const defaultMax = useMemo(() => {
    if (data.length === 0) return 5000;
    return Math.max(...data.map(article => article.wordCount));
  }, [data]);

  // Handle changes for min and max inputs
  const handleMinChange = (e) => {
    const value = e.target.value;
    setMinWordCount(value === '' ? '' : Number(value));
  };

  const handleMaxChange = (e) => {
    const value = e.target.value;
    setMaxWordCount(value === '' ? '' : Number(value));
  };

  // Filter + map to (x, y) for scatter
  const filteredData = useMemo(() => {
    return data
      .filter(article => {
        const categoryMatch =
          selectedCategory === 'All'
            ? true
            : article.category.toLowerCase() === selectedCategory.toLowerCase();

        const minMatch = minWordCount === '' || article.wordCount >= minWordCount;
        const maxMatch = maxWordCount === '' || article.wordCount <= maxWordCount;

        return categoryMatch && minMatch && maxMatch;
      })
      .map((article, idx) => ({
        x: idx,
        y: article.wordCount,
        title: article.title,
        source: article.source,
      }));
  }, [data, selectedCategory, minWordCount, maxWordCount]);

  // Group duplicates
  const groupedData = useMemo(() => groupPoints(filteredData), [filteredData]);

  // Separate by source
  const sources = useMemo(() => [...new Set(groupedData.map(d => d.source))], [groupedData]);

  // Calculate bar chart data: bin the word counts into 10 bins
  const barData = useMemo(() => {
    if (filteredData.length === 0) return [];
    const wordCounts = filteredData.map(article => article.y);
    const min = Math.min(...wordCounts);
    const max = Math.max(...wordCounts);
    const numBins = 10;
    const binWidth = Math.ceil((max - min + 1) / numBins);
    const bins = [];
    for (let i = 0; i < numBins; i++) {
      bins.push({
        range: `${min + i * binWidth}-${min + (i + 1) * binWidth - 1}`,
        articles: 0,
      });
    }
    filteredData.forEach(article => {
      const value = article.y;
      const binIndex = Math.floor((value - min) / binWidth);
      if (binIndex >= 0 && binIndex < bins.length) {
        bins[binIndex].articles++;
      }
    });
    // Optionally filter out bins with zero articles
    return bins.filter(bin => bin.articles > 0);
  }, [filteredData]);

  // Set chart dimensions
  const chartWidth = 400;
  const chartHeight = 400;

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="chart-words-container">
      <h2 className="chart-words-title">Number of Words per Article</h2>

      <div className="chart-words-filters">
        {/* Category Select */}
        <div className="chart-words-select-container">
          <label htmlFor="category-select" className="chart-words-label">
            Category:
          </label>
          <select
            id="category-select"
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

        {/* Word Count Range Inputs */}
        <div className="chart-words-range-container">
          <div className="chart-words-range-item">
            <label htmlFor="min-word" className="chart-words-label">
              Min Words:
            </label>
            <input
              type="number"
              id="min-word"
              value={minWordCount}
              onChange={handleMinChange}
              placeholder="0"
              className="chart-words-input"
              min="0"
            />
          </div>
          <div className="chart-words-range-item">
            <label htmlFor="max-word" className="chart-words-label">
              Max Words:
            </label>
            <input
              type="number"
              id="max-word"
              value={maxWordCount}
              onChange={handleMaxChange}
              placeholder={defaultMax}
              className="chart-words-input"
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
              name="Word Count"
              label={{ value: 'Word Count', angle: -90, position: 'insideLeft', fill: '#ccc' }}
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
              dataKey="range"
              label={{ value: 'Word Count Range', position: 'bottom', fill: '#ccc' }}
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
                      <p className="tooltip-title">Range: {d.range}</p>
                      <p>Articles: {d.articles}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend verticalAlign="top" height={36} />
            <Bar dataKey="articles" fill="#ffc658" />
          </BarChart>
        </div>
      </div>
    </div>
  );
}

export default ChartWordsPerArticle;
