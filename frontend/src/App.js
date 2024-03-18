import React, { useState } from 'react';

function App() {
  const [imageURL, setImageURL] = useState('');
  const [zipUrl, setZipUrl] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Indicate the loading process starts
    // No need to clear zipUrl here as it will be cleared upon error or successfully setting a new zipUrl
    
    try {
      const response = await fetch('http://localhost:5000/generate-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_url: imageURL }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        setZipUrl(''); // Explicitly clear zipUrl upon detecting an error
        setError(errorData.error); // Set the error
      } else {
        const data = await response.json();
        setError(''); // Clear any previous error state
        setZipUrl(data.zip_url); // Update with new zip URL only on successful response
      }
    } catch (error) {
      setZipUrl(''); // Ensure zipUrl is cleared if fetch fails
      setError("An unexpected error occurred"); // Handle fetch error
    } finally {
      setIsLoading(false); // Loading is complete, this will happen regardless of the request outcome
    }
  };
  

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="imageURL">
          UML Diagram URL:
        </label>
        <input
          id="imageURL"
          type="text"
          value={imageURL}
          onChange={(e) => setImageURL(e.target.value)}
        />
        <button type="submit" disabled={isLoading}>Generate Java Code</button>
      </form>
      {isLoading && (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {!isLoading && !error && zipUrl && (
        <div className="download">
          <h3>Download Generated Java Files:</h3>
          <a href={`http://localhost:5000${zipUrl}`} download>Download Zip</a>
        </div>
      )}
    </div>
  );
}

export default App;
