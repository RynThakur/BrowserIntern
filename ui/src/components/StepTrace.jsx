import './StepTrace.css'

const ACTION_COLORS = {
  navigate: '#6c8aff',
  click: '#a78bfa',
  type: '#34d399',
  scroll: '#94a3b8',
  press_key: '#94a3b8',
  open_tab: '#fbbf24',
  switch_tab: '#fbbf24',
  close_tab: '#f87171',
  list_tabs: '#94a3b8',
  done: '#34d399',
  error: '#f87171',
}

export default function StepTrace({ steps }) {
  return (
    <div className="trace-list">
      {steps.map((s, i) => (
        <div
          key={i}
          className="trace-card"
        >
          <div className="trace-top">

            <span className="step-pill">
              Step {s.step}
            </span>

            <span
              className="action-pill"
              style={{
                backgroundColor:
                  ACTION_COLORS[s.action] + '22',
                color: ACTION_COLORS[s.action],
              }}
            >
              {s.action}
            </span>

            {s.action === 'click' &&
              s.observation?.startsWith('[HEALED]') && (
                <span className="healed-pill">
                  Self-Healed
                </span>
              )}

          </div>

          <div className="thought-block">
            <span className="label">
              Thought
            </span>

            <div className="thought-text">
              {s.thought}
            </div>
          </div>

          {s.params &&
            Object.keys(s.params).length > 0 && (
              <pre className="params-block">
                {JSON.stringify(
                  s.params,
                  null,
                  2
                )}
              </pre>
            )}

          {s.observation && (
            <div className="observation-block">
              <span className="obs-arrow">
                →
              </span>

              <span>
                {s.observation}
              </span>
            </div>
          )}

          {s.tabs &&
            s.tabs.length > 1 && (
              <div className="tabs-row">
                {s.tabs.map((t) => (
                  <span
                    key={t.index}
                    className={`tab-pill ${
                      t.active
                        ? 'tab-active'
                        : ''
                    }`}
                  >
                    [{t.index}]{' '}
                    {(
                      t.title ||
                      t.url ||
                      ''
                    ).slice(0, 24)}
                  </span>
                ))}
              </div>
            )}
        </div>
      ))}
    </div>
  )
}