import { useState, useRef, useEffect } from 'react'
import StepTrace from './components/StepTrace'
import ScreenshotPanel from './components/ScreenshotPanel'

import browserInternLogo from './assets/browserInternLogo.png'
import bgVideo from './assets/bg.mp4'

import './App.css'

const WS_URL = 'ws://localhost:8000/ws/run'

const EXAMPLE_TASKS = [
  'Go to Youtube.com',
  'Go to Leetcode.com and open problem of the day',
  'Open Wikipedia and find the population of India',
  'Go to github.com/RynThakur and open HallucinateGPT repo',
]

export default function App() {
  const [task, setTask] = useState('')
  const [steps, setSteps] = useState([])
  const [screenshot, setShot] = useState(null)
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)

  const wsRef = useRef(null)
  const traceEndRef = useRef(null)

  useEffect(() => {
    traceEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    })
  }, [steps])

  function startAgent() {
    if (!task.trim() || status === 'running') return

    setSteps([])
    setShot(null)
    setResult(null)
    setStatus('running')

    const ws = new WebSocket(WS_URL)

    wsRef.current = ws

    ws.onopen = () =>
      ws.send(
        JSON.stringify({
          task,
          headless: false,
        })
      )

    ws.onmessage = (e) => {
      const event = JSON.parse(e.data)

      setShot(event.screenshot || null)

      setSteps((prev) => [...prev, event])

      if (event.type === 'done') {
        setResult(event.result)
        setStatus('done')
      } else if (event.type === 'error') {
        setResult(event.result || 'An error occurred.')
        setStatus('error')
      }
    }

    ws.onerror = () => {
      setResult(
        'Could not connect to backend. Is it running on port 8000?'
      )
      setStatus('error')
    }
  }

  function stopAgent() {
    wsRef.current?.close()
    setStatus('idle')
  }

  const isRunning = status === 'running'

  return (
    <div className="app">
      {/* Background Video */}
      <video
        className="background-video"
        autoPlay
        loop
        muted
        playsInline
      >
        <source src={bgVideo} type="video/mp4" />
      </video>

      {/* Dark Overlay */}
      <div className="background-overlay" />

      <header className="header">
        <div className="brand-icon">
          <img
            src={browserInternLogo}
            alt="Browser Agent Logo"
            className="brand-logo"
          />
        </div>

        <div>
          <div className="brand-title">
            Browser Intern
          </div>

          <div className="brand-subtitle">
            Autonomous browser automation
          </div>
        </div>

        <div className="status-group">
          {['idle', 'running', 'done', 'error'].map((s) => (
            <span
              key={s}
              className={`status-pill ${
                status === s ? 'status-active' : ''
              }`}
            >
              {s}
            </span>
          ))}
        </div>
      </header>

      <section className="task-section">
        <div className="task-card">
          <div className="task-label">
            Describe what the agent should do
          </div>

          <div className="task-row">
            <textarea
              className="task-input"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              onKeyDown={(e) => {
                if (
                  e.key === 'Enter' &&
                  e.metaKey
                ) {
                  startAgent()
                }
              }}
              placeholder="Go to Hacker News and summarize the top stories..."
              disabled={isRunning}
              rows={3}
            />

            <button
              className="run-btn"
              onClick={
                isRunning
                  ? stopAgent
                  : startAgent
              }
              disabled={
                !task.trim() && !isRunning
              }
            >
              {isRunning
                ? 'Stop Agent'
                : 'Run Agent'}
            </button>
          </div>

          <div className="examples">
            {EXAMPLE_TASKS.map((t) => (
              <button
                key={t}
                className="example-btn"
                onClick={() => setTask(t)}
                disabled={isRunning}
              >
                {t.length > 42
                  ? `${t.slice(0, 42)}...`
                  : t}
              </button>
            ))}
          </div>
        </div>
      </section>

      {result && (
        <div className="result-banner">
          <strong>
            {status === 'done'
              ? 'Result: '
              : 'Error: '}
          </strong>

          {result}
        </div>
      )}

      <div className="main-grid">
        <div className="panel">
          <div className="panel-header">
            Step Trace
            {steps.length > 0 &&
              ` (${steps.length})`}
          </div>

          <div className="panel-body trace-scroll">
            {steps.length === 0 ? (
              <div className="empty-state">
                Agent activity will appear here in
                real time
              </div>
            ) : (
              <StepTrace steps={steps} />
            )}

            <div ref={traceEndRef} />
          </div>
        </div>

        <ScreenshotPanel
          screenshot={screenshot}
          step={steps.length}
          status={status}
        />
      </div>
    </div>
  )
}