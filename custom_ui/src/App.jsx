import React, { useEffect, useState } from "react"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import './App.css'

const App = (props) => {
  const [analyzing, setAnalyzing] = useState(false)
  const [score, setScore] = useState(0)
  const [completed, setCompleted] = useState(false)

  // Notify Streamlit that component is ready
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [analyzing, completed])

  const patientName = props.args.name || "Patient"

  const runAnalysis = () => {
    setAnalyzing(true)
    setCompleted(false)
    setScore(0)
    
    // Fake progress animation
    let currentScore = 0
    const targetScore = Math.floor(Math.random() * 40) + 40 // random score 40-80
    
    const interval = setInterval(() => {
      currentScore += 2
      setScore(currentScore)
      if (currentScore >= targetScore) {
        clearInterval(interval)
        setAnalyzing(false)
        setCompleted(true)
        // Send final score back to Python
        Streamlit.setComponentValue(targetScore)
      }
    }, 40)
  }

  // Calculate SVG stroke dashoffset for the circular progress bar
  const radius = 60
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference
  
  const getRiskLevel = () => {
    if (score < 50) return { text: "Low Risk", color: "#4ade80" }
    if (score < 75) return { text: "Moderate Risk", color: "#facc15" }
    return { text: "High Risk", color: "#f87171" }
  }

  return (
    <div className="react-widget-container">
      <div className="glass-card">
        <div className="header">
          <div className="icon-pulse"></div>
          <h3>AI Health Risk Assessment</h3>
        </div>
        
        <p className="subtitle">Real-time analysis module for <strong>{patientName}</strong></p>
        
        <div className="visualization">
          <div className="progress-ring-container">
            <svg className="progress-ring" width="160" height="160">
              <circle
                className="progress-ring-bg"
                strokeWidth="12"
                fill="transparent"
                r={radius}
                cx="80"
                cy="80"
              />
              <circle
                className="progress-ring-fill"
                strokeWidth="12"
                fill="transparent"
                r={radius}
                cx="80"
                cy="80"
                style={{
                  strokeDasharray: circumference,
                  strokeDashoffset: strokeDashoffset,
                  stroke: completed ? getRiskLevel().color : '#00f2fe'
                }}
              />
            </svg>
            <div className="score-display">
              <span className="score-number">{score}</span>
              <span className="score-label">/ 100</span>
            </div>
          </div>
          
          <div className="status-panel">
            {completed && (
              <div className="result-badge" style={{ color: getRiskLevel().color, borderColor: getRiskLevel().color }}>
                {getRiskLevel().text}
              </div>
            )}
            {!completed && analyzing && <div className="analyzing-text">Running Cortex Models...</div>}
            {!completed && !analyzing && <div className="ready-text">Ready for analysis</div>}
          </div>
        </div>

        <button 
          className={`action-btn ${analyzing ? 'loading' : ''}`}
          onClick={runAnalysis}
          disabled={analyzing}
        >
          {analyzing ? 'Analyzing Data...' : 'Run Deep Analysis'}
        </button>
      </div>
    </div>
  )
}

export default withStreamlitConnection(App)
