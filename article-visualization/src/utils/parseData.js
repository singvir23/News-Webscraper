// src/utils/parseData.js

export async function fetchArticles(sourcePath, sourceName) {
    // Fetch the raw text from the given path (e.g. "/data/CNN.txt")
    const response = await fetch(sourcePath);
    const rawText = await response.text();
  
    // Split text into blocks separated by blank lines.
    // Each block should represent one article.
    const blocks = rawText.split(/\n\s*\n/);
  
    const articles = [];
  
    blocks.forEach(block => {
      // If the block is empty or whitespace, skip it
      if (!block.trim()) return;
  
      // We'll store data for each article here
      const articleObj = {
        source: sourceName,
        category: '',
        title: '',
        url: '',
        date: '',
        wordCount: 0,
        images: [],
      };
  
      // Split the block into individual lines
      const lines = block.split('\n');
  
      // Process each line
      lines.forEach(line => {
        if (line.startsWith('Category:')) {
          articleObj.category = line.replace('Category:', '').trim();
        } else if (line.startsWith('Title:')) {
          articleObj.title = line.replace('Title:', '').trim();
        } else if (line.startsWith('URL:')) {
          articleObj.url = line.replace('URL:', '').trim();
        } else if (line.startsWith('Date:')) {
          articleObj.date = line.replace('Date:', '').trim();
        } else if (line.startsWith('Word Count:')) {
          // e.g. "Word Count: 204 words"
          // You could parse further if needed, but let's just get the numeric part
          const countStr = line.replace('Word Count:', '').trim(); // "204 words"
          articleObj.wordCount = parseInt(countStr, 10) || 0;
        } else if (line.startsWith('Images:')) {
          // e.g. "Images: 3 (Sizes: 1200x675, 1200x675, 1200x675)"
          // parse out each width x height
          const imagesLine = line.replace('Images:', '').trim();
          // Attempt to find something like "(Sizes: 1200x675, 1200x675)"
          const sizeMatches = imagesLine.match(/\((.*?)\)/);
          if (sizeMatches && sizeMatches[1]) {
            // strip out "Sizes:" then split by comma
            let sizeStr = sizeMatches[1].replace('Sizes:', '').trim();
            // "1200x675, 1200x675, 1200x675" -> ["1200x675", "1200x675", ...]
            const sizeParts = sizeStr.split(',');
            sizeParts.forEach(sp => {
              const trimmed = sp.trim(); // "1200x675"
              // if it's something like "Unknown Size", skip it
              if (/unknown/i.test(trimmed)) {
                return;
              }
              // split by 'x'
              const [w, h] = trimmed.split('x');
              if (w && h) {
                // parse as integers
                const width = parseInt(w, 10);
                const height = parseInt(h, 10);
                if (!isNaN(width) && !isNaN(height)) {
                  articleObj.images.push({ width, height });
                }
              }
            });
          }
        }
      });
  
      // Only push if we have at least a valid category or title (optional check)
      if (articleObj.category || articleObj.title) {
        articles.push(articleObj);
      }
    });
  
    return articles;
  }
  