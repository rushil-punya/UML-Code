import React, { useState } from 'react';

function App() {
  const [imageFile, setImageFile] = useState(null);
  const [zipUrl, setZipUrl] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await fetch('http://localhost:5000/generate-code', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setZipUrl('');
        setError(errorData.error);
      } else {
        const data = await response.json();
        setError('');
        setZipUrl(data.zip_url);
      }
    } catch (error) {
      setZipUrl('');
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="imageFile">
          Upload UML Diagram:
        </label>
        <input
          id="imageFile"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={isLoading || !imageFile}>Generate Java Code</button>
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
