export default function ScreenshotPanel({ screenshot, step, status }) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      overflow: 'hidden',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{
        padding: '10px 14px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        fontSize: 12,
        color: 'var(--muted)',
      }}>
        <span style={{
          width: 8, height: 8, borderRadius: '50%',
          background: status === 'running' ? '#34d399' : status === 'done' ? '#6c8aff' : '#f87171',
          boxShadow: status === 'running' ? '0 0 6px #34d39988' : 'none',
        }}/>
        Live browser view
        {step > 0 && <span style={{ marginLeft: 'auto' }}>after step {step}</span>}
      </div>

      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 12 }}>
        {screenshot ? (
          <img
            src={`data:image/png;base64,${screenshot}`}
            alt="Browser screenshot"
            style={{
              width: '100%',
              height: 'auto',
              borderRadius: 6,
              border: '1px solid var(--border)',
              objectFit: 'contain',
            }}
          />
        ) : (
          <div style={{ color: 'var(--muted)', fontSize: 13, textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}></div>
            Screenshot will appear here when the agent starts
          </div>
        )}
      </div>
    </div>
  )
}
