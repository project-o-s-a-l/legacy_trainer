import React from 'react';
import logo from './logo.svg';
import './App.css';
import Navbar from './Navbar';
import { Route, Routes } from 'react-router';
import Footer from './Footer';
import zeroImg from './png/00-image.png';
import oneImg from './png/01-image.png';
import twoImg from './png/02-image.png';


function Home() {
  return <h1>Home Page</h1>;
}

function About() {
  return <h1>About Page</h1>;
}

function Contact() {
  return <h1>Contact Page</h1>;
}

function Possibilites() {
  return <h1>Possibilites</h1>
}

function Support() {
  return <h1>Support</h1>
}

function Sing_in() {
  return <h1>Sing in</h1>
}

function Test()
{
  console.log("test");
  return <h1>test</h1>;
}

function App() {
  return (
    <div className="App">
     <Navbar/>
     <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/possibilites" element={<Possibilites />} />
        <Route path="/support" element={<Support />} />
        <Route path='/sing_in' element={<Sing_in/>}/>
        <Route path='/test' element={<Test/>}/>
     </Routes>


     <div className='about-site'>
     <div className='about-site-content'>
      <div className='about-site-text'>
      <span>A little about <br /> the site</span>
      <p>
        Upload your code, select the language and difficulty level, and get a quick check and recommendations for improvement. Learn by doing and improve your programming skills with us!
      </p>
      </div>
      <img className='img-pc-main' src={zeroImg} alt="" />
     </div>
     </div>
     <img className='first-bug-main' src={oneImg} alt="" />
     <img className='second-bug-main' src={twoImg} alt="" />
     <Footer></Footer>
    </div>
  );
}

export default App;
