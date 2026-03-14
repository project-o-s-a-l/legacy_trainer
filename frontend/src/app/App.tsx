import React from 'react';
import './App.css';
import Navbar from '../widgets/Navbar/Navbar';
import { Route, Routes } from 'react-router';
import { mainPageRoutes } from './providers/router/routeConfig';
import { renderRoutes } from './providers/router/renderRoutes';



function App() {
  return (
    <div className="App">
     <Navbar links={mainPageRoutes}/>
     <Routes>
      {renderRoutes(mainPageRoutes)}
     </Routes>
    </div>
  );
}

export default App;
