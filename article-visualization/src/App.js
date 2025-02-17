// App.js
import React, { useEffect, useState } from 'react';
import { fetchArticles } from './utils/parseData';

// Chart Components
import ChartImagesPerArticle from './components/ChartImagesPerArticle';
import ChartWordsPerArticle from './components/ChartWordsPerArticle';
import ChartImageSizes from './components/ChartImageSizes';

// Loading Spinner Component
import LoadingSpinner from './components/LoadingSpinner';

// Import the CSS file
import './App.css';

function App() {
  const [allArticles, setAllArticles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const cnnArticles = await fetchArticles('/data/cnn_articles.txt', 'CNN');
        const foxArticles = await fetchArticles('/data/fox_news_articles.txt', 'FOX');
        // Combine them
        setAllArticles([...cnnArticles, ...foxArticles]);
      } catch (err) {
        setError(err.message || 'Error loading data');
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        {`Error: ${error}`}
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="inner-container">
        <h1 className="title">Article Data Visualization</h1>
        <p className="text-gray-400 text-sm mt-2">Data collected: December 15th 2024 - February 17th 2025</p>
        <div className="charts-container">
          <div className="chart-wrapper">
            <ChartImagesPerArticle data={allArticles} />
          </div>
          <div className="chart-wrapper">
            <ChartWordsPerArticle data={allArticles} />
          </div>
          <div className="chart-wrapper">
            <ChartImageSizes data={allArticles} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
