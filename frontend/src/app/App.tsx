import React from 'react';
import './App.css';
import Navbar from '../widgets/Navbar/Navbar';
import { Route, Routes } from 'react-router';
import { mainPageRoutes } from './providers/router/routeConfig';
import { renderRoutes } from './providers/router/renderRoutes';
import Footer from '../widgets/Footer/Footer';



function App() {
  return (
    <div className="App">
     <Navbar links={mainPageRoutes}/>
     <Routes>
      {renderRoutes(mainPageRoutes)}
     </Routes>
    <Footer></Footer>     
    </div>
  );
}

export default App;
