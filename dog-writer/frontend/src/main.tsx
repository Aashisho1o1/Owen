import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import './index.css'
import App from './App.tsx'
import { AppProvider } from './contexts/AppContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <MantineProvider>
        <AppProvider>
      <App />
        </AppProvider>
      </MantineProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
