// src/App.js

import React, { useEffect, useState } from 'react';
import { fetchArticles } from './utils/parseData';

// Suppose you've already built these chart components:
import ChartImagesPerArticle from './components/ChartImagesPerArticle';
import ChartWordsPerArticle from './components/ChartWordsPerArticle';
import ChartImageSizes from './components/ChartImageSizes';

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
    return <div style={{ padding: '2rem' }}>Loading data...</div>;
  }

  if (error) {
    return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-2xl font-bold mb-8">Article Data Visualization</h1>
      <ChartImagesPerArticle data={allArticles} />
      <ChartWordsPerArticle data={allArticles} />
      <ChartImageSizes data={allArticles} />
    </div>
  );
}

export default App;
