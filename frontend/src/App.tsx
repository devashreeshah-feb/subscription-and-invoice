import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, Navigate, Link } from 'react-router-dom'
import './App.css'

const API_URL = 'http://127.0.0.1:8000/api/v1'

function LandingPage() {
  return (
    <div className="panel" style={{ textAlign: 'center', marginTop: '10vh' }}>
      <h1>Welcome to SubFlow</h1>
      <p>The premium billing solution for modern teams.</p>
      <div className="flex gap-4 justify-center" style={{ marginTop: '2rem' }}>
        <Link to="/register"><button>Get Started</button></Link>
        <Link to="/login"><button className="outline">Sign In</button></Link>
      </div>
    </div>
  )
}

function RegisterPage() {
  const navigate = useNavigate()
  const [accountType, setAccountType] = useState('individual')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [orgName, setOrgName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name, email, password, account_type: accountType, organization_name: accountType === 'organization' ? orgName : null
        })
      })
      if (res.ok) {
        navigate('/login')
      } else {
        const data = await res.json()
        setError(data.detail || 'Registration failed')
      }
    } catch (err) {
      setError('Network error - Is the backend running?')
    }
    setLoading(false)
  }

  return (
    <div className="panel" style={{ maxWidth: '500px', margin: '10vh auto' }}>
      <h2>Create an Account</h2>
      {error && <p style={{ color: 'var(--danger-color)' }}>{error}</p>}
      <form onSubmit={handleRegister}>
        <div className="form-group">
          <label>Account Type</label>
          <select 
            value={accountType} 
            onChange={e => setAccountType(e.target.value)}
            style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-color)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
          >
            <option value="individual">Individual</option>
            <option value="organization">Organization</option>
          </select>
        </div>
        
        {accountType === 'organization' && (
          <div className="form-group">
            <label>Organization Name</label>
            <input type="text" value={orgName} onChange={e => setOrgName(e.target.value)} required />
          </div>
        )}
        
        <div className="form-group">
          <label>Full Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button type="submit" style={{ width: '100%' }} disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        Already have an account? <Link to="/login" style={{ color: 'var(--accent-color)' }}>Log in</Link>
      </p>
    </div>
  )
}

function LoginPage({ setToken }: { setToken: (t: string) => void }) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      })
      const data = await res.json()
      if (res.ok) {
        setToken(data.access_token)
        navigate('/dashboard')
      } else {
        setError(data.detail || 'Login failed')
      }
    } catch (err) {
      setError('Network error - Is the backend running?')
    }
    setLoading(false)
  }

  return (
    <div className="panel" style={{ maxWidth: '400px', margin: '10vh auto' }}>
      <h2>Sign In</h2>
      <div style={{ background: 'var(--panel-bg)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', border: '1px solid var(--border-color)' }}>
        <p style={{ fontSize: '0.85rem', margin: 0, color: 'var(--text-secondary)' }}><strong>Customer:</strong> alice@example.com / password123</p>
        <p style={{ fontSize: '0.85rem', margin: 0, color: 'var(--text-secondary)', marginTop: '0.5rem' }}><strong>Admin:</strong> admin@example.com / password123</p>
      </div>
      {error && <p style={{ color: 'var(--danger-color)' }}>{error}</p>}
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button type="submit" style={{ width: '100%' }} disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        New user? <Link to="/register" style={{ color: 'var(--accent-color)' }}>Register here</Link>
      </p>
    </div>
  )
}

function Dashboard({ token, setToken }: { token: string, setToken: (t: string | null) => void }) {
  const [user, setUser] = useState<any>(null)
  const [plans, setPlans] = useState<any[]>([])
  const [subscriptions, setSubscriptions] = useState<any[]>([])
  const [invoices, setInvoices] = useState<any[]>([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const userRes = await fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      if (!userRes.ok) {
        if (userRes.status === 401) setToken(null)
        setLoading(false)
        return
      }
      
      const userData = await userRes.json()
      setUser(userData)
      
      if (userData.role === 'admin') {
        const analyticsRes = await fetch(`${API_URL}/admin/analytics`, { headers: { Authorization: `Bearer ${token}` } })
        if (analyticsRes.ok) setAnalytics(await analyticsRes.json())
      } else {
        const [plansRes, subsRes, invRes] = await Promise.all([
          fetch(`${API_URL}/plans/`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API_URL}/subscriptions/me`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API_URL}/invoices/`, { headers: { Authorization: `Bearer ${token}` } })
        ])
        if (plansRes.ok) setPlans(await plansRes.json())
        if (subsRes.ok) setSubscriptions(await subsRes.json())
        if (invRes.ok) setInvoices(await invRes.json())
      }
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const handleSubscribe = async (planId: string, simulateFail: boolean = false) => {
    try {
      const res = await fetch(`${API_URL}/subscriptions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ plan_id: planId, payment_method_id: simulateFail ? "pm_fail" : "pm_success" })
      })
      if (res.ok) {
        alert("Subscription successful!")
        fetchData()
      } else {
        const data = await res.json()
        alert(`Error: ${data.detail}`)
        // Dunning simulation
        if (simulateFail) {
          fetchData() // Refresh to show "Past Due" status
        }
      }
    } catch (err) {
      alert("Network error during checkout")
    }
  }

  const handleUpgrade = async (subId: string, newPlanId: string) => {
    try {
      const res = await fetch(`${API_URL}/subscriptions/${subId}/upgrade?new_plan_id=${newPlanId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        alert("Subscription upgraded successfully! Proration applied and new invoice generated.")
        fetchData()
      }
    } catch (err) {
      alert("Error upgrading")
    }
  }

  const handleCancel = async (subId: string) => {
    if (!window.confirm("Are you sure you want to cancel this subscription? This will trigger the churn webhook.")) return;
    try {
      const res = await fetch(`${API_URL}/subscriptions/${subId}/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        alert("Subscription cancelled.")
        fetchData()
      }
    } catch (err) {
      alert("Error cancelling")
    }
  }

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: '0 auto' }}></div></div>
  if (!user) return <div style={{ padding: '2rem' }}>Failed to load user.</div>

  const roleText = user.role ? user.role.toUpperCase() : 'USER'

  return (
    <>
      <header>
        <div className="brand">SubFlow</div>
        <div className="flex align-center gap-4">
          <span className="badge neutral" style={{ marginRight: '1rem' }}>{roleText}</span>
          <span style={{ color: 'var(--text-secondary)' }}>
            {user.name} ({user.account_type === 'organization' ? user.organization_name : 'Individual'})
          </span>
          <button className="outline" onClick={() => setToken(null)}>Logout</button>
        </div>
      </header>
      <main>
        {user.role === 'admin' ? (
          <div>
            <h2>Admin Analytics Dashboard</h2>
            <p>Real-time metrics and reporting.</p>
            {analytics ? (
              <>
                <div className="grid grid-cols-3" style={{ marginBottom: '2rem' }}>
                  <div className="panel" style={{ borderTop: '4px solid var(--accent-color)' }}>
                    <h3>Total Customers</h3>
                    <h1 style={{ color: 'var(--accent-color)' }}>{analytics.total_customers}</h1>
                    <p style={{ margin: 0, fontSize: '0.85rem' }}>Active verified accounts</p>
                  </div>
                  <div className="panel" style={{ borderTop: '4px solid var(--success-color)' }}>
                    <h3>Active Subscriptions</h3>
                    <h1 style={{ color: 'var(--success-color)' }}>{analytics.active_subscriptions}</h1>
                    <p style={{ margin: 0, fontSize: '0.85rem' }}>Currently billed plans</p>
                  </div>
                  <div className="panel" style={{ borderTop: '4px solid #f59e0b' }}>
                    <h3>Monthly Recurring Revenue (MRR)</h3>
                    <h1 style={{ color: '#f59e0b' }}>₹{analytics.mrr}</h1>
                    <p style={{ margin: 0, fontSize: '0.85rem' }}>Annualized: ₹{analytics.mrr * 12}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2">
                  <div className="panel">
                    <h3>Dunning & Failed Payments</h3>
                    <h1 style={{ color: 'var(--danger-color)' }}>{analytics.failed_payments}</h1>
                    <p>Total failed transactions requiring retry/dunning.</p>
                    <button className="outline" style={{ marginTop: '1rem' }}>Run Retry Job</button>
                  </div>
                  <div className="panel">
                    <h3>Audit Logs & Webhooks</h3>
                    <p>System is tracking all webhooks and authentications securely.</p>
                    <button className="outline" style={{ marginTop: '1rem' }}>View Logs</button>
                  </div>
                </div>
              </>
            ) : <p>Loading analytics...</p>}
          </div>
        ) : (
          <div>
            <h2>Customer Portal</h2>
            <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
              <div>
                <div className="panel">
                  <h3>Your Subscriptions</h3>
                  {subscriptions.length > 0 ? (
                    <div className="grid grid-cols-1" style={{ marginTop: '1rem' }}>
                      {subscriptions.map(sub => (
                        <div key={sub.id} style={{ border: '1px solid var(--border-color)', padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem' }}>
                          <div className="flex justify-between align-center" style={{ marginBottom: '1rem' }}>
                            <span className={`badge ${sub.status === 'Active' ? 'success' : 'danger'}`}>{sub.status}</span>
                            {sub.status === 'Active' && (
                              <button className="outline" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', borderColor: 'var(--danger-color)', color: 'var(--danger-color)' }} onClick={() => handleCancel(sub.id)}>
                                Cancel
                              </button>
                            )}
                          </div>
                          <p><strong>Plan ID:</strong> {sub.plan_id}</p>
                          <p><strong>Next Billing:</strong> {new Date(sub.next_billing_date).toLocaleDateString()}</p>
                          {sub.status === 'Past Due' && (
                            <div style={{ padding: '1rem', background: 'rgba(255, 74, 74, 0.1)', border: '1px solid var(--danger-color)', borderRadius: '8px', marginTop: '1rem' }}>
                              <h4 style={{ color: 'var(--danger-color)', margin: 0 }}>Dunning Active</h4>
                              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Payment failed. We will retry the charge in 24 hours.</p>
                              <button style={{ marginTop: '1rem', width: '100%', background: 'var(--danger-color)' }}>Update Payment Method</button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>You do not have any active subscriptions.</p>
                  )}
                </div>
                
                <div className="panel">
                  <h3>Invoice History</h3>
                  {invoices.length > 0 ? (
                    <table style={{ width: '100%', textAlign: 'left', marginTop: '1rem', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <th style={{ padding: '0.5rem' }}>Invoice #</th>
                          <th style={{ padding: '0.5rem' }}>Date</th>
                          <th style={{ padding: '0.5rem' }}>Amount</th>
                          <th style={{ padding: '0.5rem' }}>Status</th>
                          <th style={{ padding: '0.5rem' }}>PDF</th>
                        </tr>
                      </thead>
                      <tbody>
                        {invoices.map(inv => (
                          <tr key={inv.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                            <td style={{ padding: '0.5rem', fontSize: '0.85rem' }}>{inv.invoice_number}</td>
                            <td style={{ padding: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{new Date(inv.created_at).toLocaleDateString()}</td>
                            <td style={{ padding: '0.5rem' }}>₹{inv.total / 100}</td>
                            <td style={{ padding: '0.5rem' }}><span className="badge success">{inv.status}</span></td>
                            <td style={{ padding: '0.5rem' }}><button className="outline" style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}>DL</button></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p>No invoices found.</p>
                  )}
                </div>
              </div>
              
              <div>
                <h3>Available Plans</h3>
                <div className="grid grid-cols-1" style={{ marginTop: '1rem' }}>
                  {plans.map(plan => {
                    const activeSub = subscriptions.find(s => s.status === 'Active' || s.status === 'Past Due');
                    const isCurrent = activeSub?.plan_id === plan.id;
                    const canUpgrade = activeSub && !isCurrent && activeSub.status === 'Active';
                    
                    return (
                      <div key={plan.id} className="panel flex flex-col justify-between" style={{ marginBottom: '1rem', borderColor: isCurrent ? 'var(--accent-color)' : 'var(--border-color)' }}>
                        <div className="flex justify-between align-center">
                          <div>
                            <h2>{plan.name} {isCurrent && <span className="badge neutral" style={{ marginLeft: '0.5rem' }}>Current</span>}</h2>
                            <h1 style={{ fontSize: '1.5rem', margin: '0' }}>₹{plan.price / 100}<span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/mo</span></h1>
                            <p style={{ marginTop: '0.5rem' }}>{plan.description}</p>
                          </div>
                        </div>
                        <div style={{ marginTop: '1rem' }} className="flex gap-4">
                          {isCurrent ? (
                            <button disabled style={{ flex: 1, opacity: 0.5 }}>Current Plan</button>
                          ) : canUpgrade ? (
                            <button style={{ flex: 1 }} onClick={() => handleUpgrade(activeSub.id, plan.id)}>Upgrade Plan</button>
                          ) : (
                            <>
                              <button style={{ flex: 1 }} onClick={() => handleSubscribe(plan.id, false)} disabled={!!activeSub}>Subscribe</button>
                              {!activeSub && (
                                <button className="outline" style={{ flex: 1 }} onClick={() => handleSubscribe(plan.id, true)}>Simulate Fail</button>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  )
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
        <Route path="/register" element={token ? <Navigate to="/dashboard" /> : <RegisterPage />} />
        <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <LoginPage setToken={setToken} />} />
        <Route path="/dashboard" element={token ? <Dashboard token={token} setToken={setToken} /> : <Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
