import { motion } from 'framer-motion'
import browserInternLogo from '../assets/browserInternLogo.png'
import './LandingPage.css'

export default function LandingPage({ onEnter }) {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15, delayChildren: 0.2 }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 80, damping: 20 } }
  }

  return (
    <div className="landing-root">
      <div className="landing-bg-image" />
      <div className="landing-bg-overlay" />

      <motion.div
        className="landing-content"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
       <motion.header className="landing-header" variants={itemVariants}>
          <img src={browserInternLogo} alt="Logo" className="header-logo" />
          <nav className="header-nav">
            <a href="https://github.com/RynThakur/BrowserIntern" target="_blank" rel="noreferrer">Features</a>
            <a href="https://github.com/RynThakur/BrowserIntern" target="_blank" rel="noreferrer">Documentation</a>
            <a href="https://github.com/RynThakur/BrowserIntern" target="_blank" rel="noreferrer">GitHub</a>
            <a href="https://github.com/RynThakur/BrowserIntern" target="_blank" rel="noreferrer">Dashboard</a>
          </nav>
        </motion.header>

        <main className="landing-main">
          <motion.h1 className="hero-title" variants={itemVariants}>
            Autonomous navigation<br />
            in a <span className="highlight-yellow">complex</span> web
          </motion.h1>
          
          <motion.p className="hero-subtitle" variants={itemVariants}>
            Bridging Playwright and OpenAI to navigate, interact,<br/> 
            and execute browser tasks with intelligent precision.
          </motion.p>

          <motion.button 
            className="hero-cta" 
            variants={itemVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onEnter}
          >
            Initialize Agent ↗
          </motion.button>
        </main>
      </motion.div>
    </div>
  )
}