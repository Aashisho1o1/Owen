// OPTIMIZATION OPPORTUNITIES
//
// This component could be improved in these ways:
//
// 1. Extract Panel Component: Create a separate `MangaPanel.tsx` component
//    that handles individual panel display, reducing the complexity of this component.
//
// 2. Styled Components: Consider using styled-components or CSS modules instead
//    of JSX style blocks for better style management and reuse.
//
// 3. Loading States: Add proper loading states and error boundaries instead
//    of placeholder divs.
//
// 4. Memo for Performance: Use React.memo to prevent unnecessary re-renders of panels.
//
// 5. Image Loading Optimization: 
//    - Add proper image error handling
//    - Implement progressive loading with thumbnails
//    - Consider lazy loading panels not in view

import React from 'react';
import { MangaPageFE, MangaPanelFE } from '../services/api'; // Adjust path as needed

interface MangaDisplayProps {
  mangaPage: MangaPageFE;
}

const MangaDisplay: React.FC<MangaDisplayProps> = ({ mangaPage }) => {
  if (!mangaPage) {
    return <p>No manga data to display.</p>;
  }

  return (
    <div className="manga-display-container">
      <h2>{mangaPage.title || 'Manga Page'} (Page {mangaPage.page_number})</h2>
      
      {mangaPage.character_designs && Object.keys(mangaPage.character_designs).length > 0 && (
        <div className="character-designs-section">
          <h4>Character Designs:</h4>
          <ul>
            {Object.entries(mangaPage.character_designs).map(([name, desc]) => (
              <li key={name}><strong>{name}:</strong> {desc}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="panels-grid">
        {mangaPage.panels.map((panel: MangaPanelFE) => (
          <div key={panel.panel_number} className="manga-panel">
            <h4>Panel {panel.panel_number}</h4>
            {panel.image_url ? (
              <img src={panel.image_url} alt={`Panel ${panel.panel_number} - ${panel.description.substring(0, 50)}...`} className="panel-image" />
            ) : (
              <div className="panel-image-placeholder">Image generating or failed...</div>
            )}
            <p className="panel-description"><strong>Description:</strong> {panel.description}</p>
            {panel.dialogue && panel.dialogue.length > 0 && (
              <div className="panel-dialogue">
                <strong>Dialogue:</strong>
                <ul>
                  {panel.dialogue.map((d, index) => (
                    <li key={index}><strong>{d.character}:</strong> {d.speech}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
      <style>{`
        .manga-display-container {
          padding: 20px;
          border: 1px solid #ccc;
          border-radius: 8px;
          background-color: #f9f9f9;
        }
        .character-designs-section {
          margin-bottom: 20px;
          padding: 10px;
          background-color: #eee;
          border-radius: 4px;
        }
        .character-designs-section h4 {
          margin-top: 0;
        }
        .panels-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* Responsive grid */
          gap: 20px;
        }
        .manga-panel {
          border: 1px solid #ddd;
          padding: 15px;
          border-radius: 6px;
          background-color: #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .manga-panel h4 {
          margin-top: 0;
          color: #333;
        }
        .panel-image {
          width: 100%;
          max-height: 400px; /* Limit image height */
          object-fit: contain; /* Show whole image, letterbox if needed */
          border-radius: 4px;
          margin-bottom: 10px;
          background-color: #e0e0e0; /* Placeholder bg for loading/failed images */
        }
        .panel-image-placeholder {
          width: 100%;
          height: 200px; /* Adjust as needed */
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #e0e0e0;
          border-radius: 4px;
          margin-bottom: 10px;
          color: #777;
        }
        .panel-description,
        .panel-dialogue {
          font-size: 0.9em;
          margin-bottom: 8px;
          color: #555;
        }
        .panel-dialogue ul {
          list-style-type: none;
          padding-left: 10px;
        }
        .panel-dialogue li {
          margin-bottom: 4px;
        }
      `}</style>
    </div>
  );
};

export default MangaDisplay; 