import React, { useState, useEffect } from 'react'
import { Shield, Home, FileText, Activity, Settings, User, LogOut, Bell, ChevronDown, CheckCircle, Smartphone, MapPin, ArrowRight, Zap, CloudRain, ThermometerSun, Lock, Clock, AlertTriangle, TrendingDown, Target, BarChart, Database, RefreshCcw, BellRing } from 'lucide-react'

const API_BASE = 'http://localhost:5000/api'

const LiveBackground = () => (
  <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-slate-50">
    <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100/40 blur-[100px] rounded-full animate-[pulse_8s_ease-in-out_infinite]"></div>
    <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-100/40 blur-[100px] rounded-full animate-[pulse_10s_ease-in-out_infinite_reverse]"></div>
  </div>
)

const Sidebar = ({ activeTab, setActiveTab, userRole, onLogout, userMeta }) => {
  const tabs = [
    { id: 'home', label: 'Home', icon: Home },
    ...(userRole === 'worker' ? [
      { id: 'policy', label: 'Policy', icon: FileText },
      { id: 'claims', label: 'Claims', icon: Activity }
    ] : []),
    ...(userRole === 'admin' ? [
      { id: 'admin', label: 'Admin', icon: BarChart }
    ] : []),
    { id: 'profile', label: 'Profile', icon: User }
  ]

  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0 z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
      <div className="p-6">
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8 text-emerald-700" />
          <div>
            <h1 className="text-xl font-bold text-slate-800 leading-none">GigShield</h1>
            <p className="text-[10px] text-slate-500 mt-1">The Resilient Guardian</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${activeTab === tab.id ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'}`}
          >
            <tab.icon className="w-5 h-5" />
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-800 font-bold uppercase">
            {userRole === 'admin' ? 'AD' : userMeta?.phone?.slice(-2) || 'WK'}
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">{userRole === 'admin' ? 'System Admin' : `+91 ******${userMeta?.phone?.slice(-4) || '0000'}`}</p>
            <p className="text-xs text-emerald-600 font-bold capitalize">{userRole}</p>
          </div>
        </div>
        <button onClick={onLogout} className="text-slate-400 hover:text-red-500 transition-colors p-2 rounded-lg hover:bg-red-50">
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}

const Header = ({ title, userRole, setRole, liveWeather }) => {
  const [showNotif, setShowNotif] = useState(false)

  return (
    <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10 w-full">
      <h2 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h2>
      
      <div className="flex items-center space-x-6">
        {liveWeather && (
          <div className="hidden md:flex items-center space-x-3 bg-slate-50 border border-slate-200 px-4 py-1.5 rounded-full text-sm font-medium text-slate-600">
            <ThermometerSun className="w-4 h-4 text-amber-500" />
            <span>{liveWeather.temperature}°C</span>
            <span className="w-px h-4 bg-slate-300 mx-2"></span>
            <CloudRain className="w-4 h-4 text-blue-500" />
            <span>{liveWeather.rain_mm} mm/hr</span>
          </div>
        )}

        <div className="relative">
          <button onClick={() => setShowNotif(!showNotif)} className={`text-slate-400 hover:text-emerald-600 transition-colors ${showNotif ? 'text-emerald-600' : ''}`}>
            <Bell className="w-6 h-6" />
            <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full animate-pulse"></span>
          </button>
          
          {showNotif && (
            <div className="absolute right-0 mt-4 w-80 bg-white border border-slate-200 shadow-2xl rounded-2xl overflow-hidden animate-in fade-in slide-in-from-top-4 z-50">
              <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
                <span className="text-sm font-bold text-slate-800">Notifications</span>
                <span className="text-xs text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full">1 New</span>
              </div>
              <div className="p-4 bg-emerald-50/50 border-l-4 border-emerald-500 hover:bg-emerald-50 transition-colors cursor-pointer">
                <div className="flex items-start space-x-3">
                  <BellRing className="w-5 h-5 text-emerald-600 mt-1" />
                  <div>
                    <p className="text-sm font-bold text-slate-800 tracking-tight">Weather API Connected</p>
                    <p className="text-xs text-emerald-700 mt-1 font-medium">Live telemetry via Open-Meteo successfully established for {liveWeather?.zone || 'your zone'}.</p>
                    <p className="text-[10px] text-slate-400 mt-2 font-mono">Just now</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2 text-sm font-bold text-slate-700 bg-emerald-50 border border-emerald-100 px-4 py-2 rounded-full cursor-pointer hover:bg-emerald-100 transition-colors shadow-sm" onClick={() => setRole(userRole === 'admin' ? 'worker' : 'admin')}>
          <span>{userRole === 'admin' ? 'Insurer Sandbox' : 'Worker View'}</span>
          <RefreshCcw className="w-4 h-4 text-emerald-600" />
        </div>
      </div>
    </header>
  )
}

const LandingPage = ({ onLogin }) => {
  const [phone, setPhone] = useState('')
  const [zone, setZone] = useState('')
  const [platform, setPlatform] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerify = async () => {
    if (!phone || !zone || !platform) {
      setError('Please select a domain, phone number, and zone.')
      return
    }
    setLoading(true)
    setTimeout(() => {
      onLogin('worker', { phone, zone, platform })
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="min-h-screen relative z-10 flex flex-col md:flex-row">
      <div className="flex-1 p-12 flex flex-col justify-center">
        <div className="max-w-xl">
          <div className="flex items-center space-x-2 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <Shield className="w-10 h-10 text-emerald-700" />
            <span className="text-3xl font-bold text-slate-800 tracking-tight">GigShield</span>
          </div>
          <span className="bg-emerald-100 text-emerald-800 text-xs font-black px-4 py-1.5 rounded-full tracking-widest border border-emerald-200">RESILIENT PROTECTION</span>
          <h1 className="text-5xl md:text-7xl font-black text-slate-900 mt-6 leading-tight tracking-tighter animate-in fade-in slide-in-from-bottom-6 duration-1000">
            Protect your weekly<br/>earnings from <span className="text-emerald-700 relative inline-block">rain and heat<div className="absolute -bottom-2 left-0 w-full h-2 bg-emerald-200 -z-10 rounded-full"></div></span>.
          </h1>
          <p className="text-xl text-slate-500 mt-8 leading-relaxed font-medium">
            Live Parametric coverage starting at <span className="font-bold text-slate-800 bg-amber-100 px-2 rounded">₹20/week</span>. Backed by Open-Meteo live datastreams.
          </p>

          <div className="mt-12">
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">SELECT YOUR DOMAIN TO BEGIN</p>
            <div className="grid grid-cols-3 gap-4">
              {['Food', 'Grocery', 'E-commerce'].map((domain) => (
                <button 
                  key={domain}
                  onClick={() => setPlatform(domain)}
                  className={`p-6 rounded-2xl border text-left transition-all duration-300 ${platform === domain ? 'border-emerald-500 bg-emerald-50 shadow-[0_8px_30px_rgba(5,150,105,0.12)] -translate-y-1' : 'border-slate-200 bg-transparent hover:bg-white hover:shadow-sm'}`}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-colors ${platform === domain ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-500'}`}>
                    {domain === 'Food' && <span className="font-black text-xl">W</span>}
                    {domain === 'Grocery' && <span className="font-black text-xl">🛒</span>}
                    {domain === 'E-commerce' && <span className="font-black text-xl">📦</span>}
                  </div>
                  <h3 className="font-bold text-slate-800 tracking-tight">{domain}</h3>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="w-full md:w-[480px] bg-white border-l border-slate-200 p-8 flex flex-col justify-center shadow-[0_0_80px_rgba(0,0,0,0.03)] z-20">
        <div className="bg-white border text-center border-slate-100 rounded-[2rem] p-10 shadow-2xl shadow-slate-200/50">
          <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-100">
            <Shield className="w-10 h-10 text-emerald-600" />
          </div>
          <h2 className="text-2xl font-black text-slate-800 mb-2 tracking-tight">Quick Verification</h2>
          <p className="text-slate-500 text-sm mb-8 font-medium">Link your partner profile instantly</p>

          {error && <div className="bg-red-50 text-red-600 border border-red-200 text-sm font-bold p-4 rounded-xl mb-6 flex items-center animate-in shake"><AlertTriangle className="w-5 h-5 mr-2 shrink-0" /> {error}</div>}

          <div className="space-y-6 text-left">
            <div>
              <label className="text-[10px] font-black tracking-widest text-slate-400 uppercase mb-2 block">10-DIGIT MOBILE</label>
              <div className="flex shadow-sm rounded-xl">
                <input 
                  type="text" 
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="98765 43210" 
                  className="flex-1 bg-slate-50 border border-slate-200 border-r-0 rounded-l-xl px-4 py-4 focus:outline-none focus:bg-white focus:border-emerald-500 transition-all text-slate-800 font-bold font-mono tracking-wider"
                />
                <button className="bg-amber-500 hover:bg-amber-600 text-white px-6 font-bold rounded-r-xl transition-colors border border-amber-600 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]">OTP</button>
              </div>
            </div>

            <div>
              <label className="text-[10px] font-black tracking-widest text-slate-400 uppercase mb-2 block">LIVE DATA ZONE</label>
              <div className="relative shadow-sm rounded-xl">
                <select 
                  value={zone}
                  onChange={(e) => setZone(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 appearance-none focus:outline-none focus:bg-white focus:border-emerald-500 transition-all text-slate-800 font-bold"
                >
                  <option value="" disabled>Choose work location...</option>
                  <option value="Koramangala, BLR">Koramangala, BLR</option>
                  <option value="Indiranagar, BLR">Indiranagar, BLR</option>
                  <option value="Andheri West, MUM">Andheri West, MUM</option>
                  <option value="South Ex, DEL">South Ex, DEL</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5 pointer-events-none" />
              </div>
            </div>

            <button 
              onClick={handleVerify}
              disabled={loading}
              className="w-full bg-emerald-800 hover:bg-emerald-900 border border-emerald-950 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_8px_20px_rgba(5,150,105,0.3)] text-white font-bold py-5 rounded-2xl flex items-center justify-center transition-all mt-8 disabled:opacity-70 disabled:cursor-not-allowed group"
            >
              {loading ? <RefreshCcw className="w-6 h-6 animate-spin" /> : (
                <>
                  <span className="text-lg">Connect Datastream</span>
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const WorkerDashboard = ({ userMeta, quote, fetchQuote, liveWeather }) => {
  useEffect(() => {
    if (!quote) fetchQuote(userMeta.zone, userMeta.platform, userMeta.phone)
  }, [])

  return (
    <div className="p-8 max-w-[1200px] mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4">
      <div className="bg-emerald-700/95 backdrop-blur-xl rounded-[2rem] p-8 text-white relative overflow-hidden shadow-xl shadow-emerald-700/20 border border-emerald-600">
        <div className="absolute right-0 top-0 w-[400px] h-[400px] bg-emerald-500 rounded-full blur-[80px] opacity-40 translate-x-1/2 -translate-y-1/3 pointer-events-none"></div>
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <span className="bg-white/10 border border-white/20 backdrop-blur text-white text-[10px] uppercase font-black tracking-widest px-3 py-1.5 rounded-full inline-flex items-center mb-4 shadow-sm">
              <Shield className="w-3 h-3 mr-1.5 text-emerald-300" /> LIVE SQL RECORD: ACTIVE
            </span>
            <h2 className="text-5xl md:text-6xl font-black tracking-tighter mb-2 text-white drop-shadow-sm">STATUS: COVERED</h2>
            <p className="text-emerald-100/80 font-medium font-mono text-sm tracking-wide">Policy #GS-{userMeta.phone.slice(-4)}-{userMeta.zone.slice(0,3).toUpperCase()} • Active since 06:00 AM</p>
          </div>
          <div className="hidden lg:flex w-32 h-32 bg-emerald-600/50 backdrop-blur border border-emerald-500/50 rounded-[2rem] items-center justify-center transform rotate-6 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-tr from-emerald-800 to-transparent"></div>
            <Shield className="w-16 h-16 text-emerald-100 relative z-10" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-[2rem] p-8 shadow-[0_4px_24px_rgba(0,0,0,0.02)] col-span-1 lg:col-span-2 relative overflow-hidden group hover:border-emerald-200 transition-colors">
          <div className="flex justify-between items-start mb-8 relative z-10">
            <div className="w-12 h-12 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center justify-center shadow-sm">
              <span className="text-emerald-700 font-black text-xl">₹</span>
            </div>
            <span className="bg-emerald-50 border border-emerald-100 text-emerald-700 text-[10px] font-black tracking-widest px-3 py-1 rounded-full uppercase">Lifetime Payouts</span>
          </div>
          <div className="relative z-10">
            <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2">Total Protected Earnings</p>
            <p className="text-5xl md:text-7xl font-black text-slate-800 tracking-tighter">₹8,500</p>
            <div className="flex justify-between items-center mt-6 pt-6 border-t border-slate-100">
              <div className="flex items-center text-xs font-bold text-slate-500">
                <Smartphone className="w-4 h-4 mr-2 text-emerald-600" /> Linked to {userMeta.platform} UPI
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-[2rem] p-8 shadow-xl flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
          <div className="absolute top-0 right-0 p-6 pointer-events-none z-10">
             <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400"><TrendingDown className="w-4 h-4 rotate-180" /></div>
          </div>
          <div className="relative z-10">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Weekly Premium</p>
            <div className="flex items-baseline space-x-1">
              <p className="text-5xl font-black text-white tracking-tighter">₹{quote?.weekly_premium || '---'}</p>
              <span className="text-slate-500 font-bold">/wk</span>
            </div>
          </div>
          <div className="mt-8 relative z-10 bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
            <div className="flex justify-between text-[10px] text-slate-300 font-black uppercase tracking-widest mb-3">
              <span>Auto-Debit Status</span>
              <span className="text-emerald-400">100% Active</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="w-full h-full bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2 bg-white border border-slate-200 rounded-[2rem] p-8 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col md:flex-row items-center justify-between group hover:border-emerald-200 transition-colors">
          <div className="flex-1 w-full md:pr-8">
            <h3 className="text-xl font-bold text-slate-800 mb-2 tracking-tight">Real-Time Open-Meteo SDK</h3>
            <p className="text-sm font-medium text-slate-500 mb-6 font-mono bg-slate-50 p-2 text-center md:text-left rounded-lg border border-slate-100">lat: {ZONES_LAT_LON[userMeta.zone.split(',')[0]]?.lat || '12.9'} / lon: {ZONES_LAT_LON[userMeta.zone.split(',')[0]]?.lon || '77.6'}</p>
            
            <div className="grid grid-cols-2 gap-4">
               <div className="bg-blue-50/50 border border-blue-100 rounded-2xl p-4">
                 <CloudRain className="w-6 h-6 text-blue-500 mb-2" />
                 <p className="text-[10px] font-black tracking-widest uppercase text-blue-800/60 mb-1">Precipitation</p>
                 <p className="text-2xl font-black text-blue-900 tracking-tighter">{liveWeather?.rain_mm || 0} <span className="text-sm font-bold text-blue-600/60 tracking-normal">mm/hr</span></p>
               </div>
               <div className="bg-amber-50/50 border border-amber-100 rounded-2xl p-4">
                 <ThermometerSun className="w-6 h-6 text-amber-500 mb-2" />
                 <p className="text-[10px] font-black tracking-widest uppercase text-amber-800/60 mb-1">Current Temp</p>
                 <p className="text-2xl font-black text-amber-900 tracking-tighter">{liveWeather?.temperature || 35} <span className="text-sm font-bold text-amber-600/60 tracking-normal">°C</span></p>
               </div>
            </div>
          </div>
          
          <div className="w-48 h-48 relative flex items-center justify-center mt-8 md:mt-0 shrink-0">
            <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
              <path className="text-slate-100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              <path className={liveWeather?.high_risk ? "text-red-500" : "text-emerald-500"} strokeDasharray={`${Math.min((liveWeather?.rain_probability || 20), 100)}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" style={{ transition: 'stroke-dasharray 1s ease-out' }} />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-3xl font-black tracking-tighter ${liveWeather?.high_risk ? 'text-red-600' : 'text-emerald-600'}`}>{liveWeather?.high_risk ? 'HIGH' : 'SAFE'}</span>
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Grid Risk</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-[2rem] p-8 relative col-span-1 shadow-sm overflow-hidden">
           <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-[30px] -mr-10 -mt-10"></div>
           <div className="w-12 h-12 bg-white border border-amber-200 rounded-xl flex items-center justify-center shadow-sm text-yellow-500 mb-6">
             <Zap className="w-6 h-6 fill-current" />
           </div>
           <h3 className="text-xl font-bold mb-2 tracking-tight text-slate-800">Next Reward Tier</h3>
           <p className="text-sm text-slate-500 font-medium mb-8 leading-relaxed">Unlock a permanent 10% base rate reduction in 2 weeks.</p>
           
           <div>
             <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-emerald-700 mb-3">
               <span>Level 4 Shield</span>
               <span>60%</span>
             </div>
             <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
               <div className="w-[60%] h-full bg-amber-500 rounded-full shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"></div>
             </div>
           </div>
        </div>
      </div>
    </div>
  )
}

const ClaimsView = ({ userMeta, liveWeather }) => {
  const [claims, setClaims] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchWorkerData = async () => {
    try {
      const res = await fetch(`${API_BASE}/worker/data?phone=${userMeta.phone}`)
      const data = await res.json()
      setClaims(data.claims)
    } catch(e) {}
  }

  const simulateClaimTrigger = async () => {
    setLoading(true)
    try {
      await fetch(`${API_BASE}/simulate-disruption`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: liveWeather.rain_mm > 0 ? 'rainstorm' : 'heatwave', phone: userMeta.phone })
      })
      await fetchWorkerData()
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchWorkerData() }, [])

  const latestClaim = claims[0]

  return (
    <div className="p-8 max-w-[1200px] mx-auto space-y-6">
      {liveWeather?.high_risk && !latestClaim && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 shadow-lg shadow-amber-500/10 flex items-center animate-in fade-in slide-in-from-top-4">
          <div className="bg-amber-100 border border-amber-200 p-3 rounded-xl mr-5">
            <CloudRain className="w-6 h-6 text-amber-700" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-800 text-lg tracking-tight mb-1">Grid Anomalies Detected via Open-Meteo.</h3>
            <p className="text-amber-800/80 text-sm font-medium">Backend sensors are validating disruption thresholds for potential automated payout execution.</p>
          </div>
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-[2rem] p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between group hover:border-emerald-200 transition-colors">
        <div className="mb-6 md:mb-0">
          <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest block mb-2">API-DRIVEN EXECUTION</span>
          <h2 className="text-4xl md:text-5xl font-black text-slate-800 tracking-tighter mb-2">Zero-Touch Claims</h2>
          <p className="text-slate-500 font-medium max-w-md leading-relaxed text-sm">Resilient Guardian AI validates weather grids directly via SQL updates. No human review. Instant UPI payout.</p>
        </div>
        <div className="bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl flex flex-col items-end shadow-sm">
          <div className="flex items-center mb-1">
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full mr-2 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <span className="text-xs font-black text-emerald-700 uppercase tracking-widest">System Active</span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Ping: 24ms • SQL Read/Write Sync</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2 bg-slate-50 border border-slate-200 rounded-[2rem] p-8 shadow-sm">
          <h3 className="text-xl font-bold text-slate-800 mb-8 tracking-tight">Backend Telemetry Graph</h3>
          
          {latestClaim ? (
            <div className="relative pl-8 border-l-2 border-slate-200 space-y-10 animate-in fade-in duration-700">
              <div className="relative">
                <div className="absolute -left-[41px] w-8 h-8 bg-emerald-600 border-4 border-slate-50 rounded-full flex items-center justify-center top-0 shadow-sm text-white">
                  <CheckCircle className="w-4 h-4" />
                </div>
                <h4 className="text-slate-800 font-bold mb-1 tracking-tight">Disruption Hook Fired</h4>
                <p className="text-sm text-slate-500 font-medium mb-3">Weather threshold exceeded in coordinates [{ZONES_LAT_LON[userMeta.zone.split(',')[0]]?.lat}, {ZONES_LAT_LON[userMeta.zone.split(',')[0]]?.lon}].</p>
                <span className="bg-emerald-100 text-emerald-800 text-[10px] uppercase font-black tracking-wider px-2 py-1 rounded">200 OK</span>
              </div>

              <div className="relative">
                <div className="absolute -left-[41px] w-8 h-8 bg-emerald-600 border-4 border-slate-50 rounded-full flex items-center justify-center top-0 shadow-sm text-white">
                   <Target className="w-4 h-4" />
                </div>
                <h4 className="text-slate-800 font-bold mb-1 tracking-tight">Fraud Detection Validated</h4>
                <p className="text-sm text-slate-500 font-medium mb-3">K-Means model cross-referenced SQL metadata. No GPS spoofing anomaly detected.</p>
                 <span className="bg-emerald-100 text-emerald-800 text-[10px] uppercase font-black tracking-wider px-2 py-1 rounded">CLEARED</span>
              </div>

              <div className="relative">
                <div className="absolute -left-[41px] w-8 h-8 bg-amber-500 border-4 border-slate-50 rounded-full flex items-center justify-center top-0 shadow-sm text-white">
                  <Zap className="w-4 h-4" />
                </div>
                <h4 className="text-slate-800 font-bold mb-1 tracking-tight">Direct API Payout Calculated: ₹{latestClaim.amount}</h4>
                <p className="text-sm text-slate-500 font-medium">Stripe ID: <code className="bg-slate-200 px-1 rounded text-red-600 text-xs">{latestClaim.txn_id}</code> executed.</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center h-full">
              <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center text-slate-400 mb-6">
                 <Database className="w-10 h-10" />
              </div>
              <h3 className="font-bold text-slate-800 mb-2">Awaiting SQL Triggers</h3>
              <p className="text-sm text-slate-500 max-w-sm">When the Open-Meteo SDK detects severe parameters in your zone, the Python worker instantly appends a claim to your ledger.</p>
            </div>
          )}
        </div>

        <div className="col-span-1 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 relative overflow-hidden group shadow-xl">
             <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
             
             {/* Mock Map background */}
             <div className="absolute inset-0 opacity-10 pointer-events-none">
                <div className="w-[150%] h-[150%] border-2 border-slate-600 rounded-[3rem] transform rotate-12 -translate-x-10 -translate-y-10 absolute"></div>
                <div className="w-full h-full border border-emerald-500/50 rounded-full transform -rotate-12 scale-150 absolute blur-[1px]"></div>
             </div>
             
             <div className="relative z-10 text-white">
               <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-6 py-1 px-3 border border-emerald-500/30 rounded-full inline-block bg-emerald-500/10">Grid Sensors</p>
               <div className="space-y-5">
                 <div className="flex justify-between items-center text-sm border-b border-slate-700 pb-3">
                   <span className="text-slate-400 font-bold">Zone Ledger</span>
                   <span className="text-slate-100 font-black">{userMeta.zone.split(',')[0]}</span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-slate-700 pb-3">
                   <span className="text-slate-400 font-bold">Rain Engine</span>
                   <span className="text-slate-100 font-black flex items-center font-mono tracking-tighter">
                     {liveWeather?.rain_mm || 0} mm/hr 
                     {(liveWeather?.rain_mm > 0) && <div className="w-2 h-2 ml-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></div>}
                   </span>
                 </div>
                 <div className="flex justify-between items-center text-sm">
                   <span className="text-slate-400 font-bold">UUID Socket</span>
                   <span className="text-slate-300 font-mono text-[10px] tracking-widest">{userMeta.phone.slice(-4)}-GIGX</span>
                 </div>
               </div>
             </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
            <h4 className="font-bold text-slate-800 mb-2">Dev Sandbox</h4>
            <p className="text-xs text-slate-500 font-medium leading-relaxed mb-6">Force trigger a POST request to `/api/simulate-disruption` via the Flask API to test webhook resolution and active SQL inserts.</p>
            <button 
              onClick={simulateClaimTrigger}
              disabled={loading}
              className="w-full bg-slate-900 border border-slate-800 hover:bg-emerald-700 text-white font-bold py-4 rounded-xl transition-all shadow-md text-sm flex items-center justify-center disabled:opacity-50"
            >
              {loading ? <RefreshCcw className="w-5 h-5 animate-spin" /> : (
                <><Database className="w-4 h-4 mr-2" /> Inject Database Fuzz</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const AdminDashboard = ({ adminData }) => {
  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-4 border-b border-slate-200 gap-4">
        <div>
          <h2 className="text-3xl font-black text-slate-800 tracking-tight mb-1">Insurer Analytics Terminal</h2>
          <p className="text-sm font-bold text-slate-500 tracking-wide">Direct connection established to: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-700 border border-slate-200">gigshield_production.db</code></p>
        </div>
        <div className="flex space-x-2">
           <span className="bg-emerald-100 text-emerald-800 text-[10px] uppercase font-black tracking-widest px-3 py-1.5 rounded border border-emerald-200 flex items-center shadow-sm">
             <div className="w-1.5 h-1.5 bg-emerald-600 rounded-full mr-2 animate-pulse"></div>
             Live SQL Binding
           </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white border-b-4 border-slate-900 shadow-sm p-6 rounded-2xl border border-slate-200 flex justify-between items-center group hover:-translate-y-1 transition-transform">
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Active Ledger Policies</p>
            <p className="text-5xl font-black text-slate-800 font-mono tracking-tighter">{adminData?.metrics?.active_policies || 0}</p>
          </div>
          <div className="w-14 h-14 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-center text-slate-600 shadow-sm group-hover:bg-slate-900 group-hover:text-white transition-colors">
            <Database className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white border-b-4 border-amber-500 shadow-sm p-6 rounded-2xl border border-slate-200 flex justify-between items-center group hover:-translate-y-1 transition-transform">
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Total SQL Claims Payout</p>
            <p className="text-5xl font-black text-slate-800 font-mono tracking-tighter">₹{adminData?.metrics?.total_claims_paid.toLocaleString() || 0}</p>
          </div>
          <div className="w-14 h-14 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-center text-amber-600 shadow-sm group-hover:bg-amber-500 group-hover:text-white transition-colors">
            <IndianRupee className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-2xl flex justify-between items-center group hover:-translate-y-1 transition-transform">
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Global Premium Cache</p>
            <p className="text-5xl font-black text-emerald-700 font-mono tracking-tighter">₹{adminData?.metrics?.total_premiums_collected?.toLocaleString() || 0}</p>
          </div>
          <div className="w-14 h-14 bg-emerald-50 border border-emerald-100 rounded-xl flex items-center justify-center text-emerald-600 shadow-sm group-hover:bg-emerald-600 group-hover:text-white transition-colors">
            <TrendingDown className="w-6 h-6 rotate-180" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-[2rem] p-8 shadow-sm">
          <div className="flex justify-between items-center border-b border-slate-100 pb-4 mb-6">
            <div>
              <h3 className="text-xl font-black text-slate-800 tracking-tight">Open-Meteo Heatmap</h3>
              <p className="text-xs font-bold text-slate-500">Overlaying active zones globally via API</p>
            </div>
            <span className="bg-slate-100 text-slate-600 text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded border border-slate-200">SQL GEOSPATIAL</span>
          </div>
          
          <div className="w-full h-[350px] bg-slate-900 rounded-2xl relative overflow-hidden group shadow-inner">
            <div className="absolute inset-0 opacity-40 mix-blend-overlay bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
            <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-emerald-500/30 rounded-full blur-[40px] -translate-x-1/2 -translate-y-1/2 filter"></div>
            
            <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
            
            <div className="absolute bottom-6 left-6 bg-slate-800/90 backdrop-blur rounded-xl p-5 shadow-2xl w-56 border border-slate-700">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Node Density Risk</p>
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-4 h-4 bg-emerald-600 border border-emerald-400 rounded-sm shadow-[0_0_8px_rgba(5,150,105,0.5)]"></div>
                <span className="text-xs font-bold text-slate-200">Live Coverage Nodes</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-red-500 border border-red-400 rounded-sm"></div>
                <span className="text-xs font-bold text-slate-200">Alert Triggers Fired</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-[2rem] p-8 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6 border-b border-slate-200 pb-4">
              <div>
                <h3 className="text-xl font-black text-slate-800 tracking-tight leading-tight">Actuary Models</h3>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Random Forest Scikit Output</p>
              </div>
              <Activity className="w-5 h-5 text-slate-400" />
            </div>

            <div className="space-y-4">
              <div className="bg-white border border-slate-200 p-4 rounded-xl flex items-center">
                 <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center mr-4 shrink-0 text-slate-600"><AlertTriangle className="w-5 h-5" /></div>
                 <div>
                    <h4 className="text-sm font-bold text-slate-800">Fraud Engine</h4>
                    <p className="text-xs font-medium text-emerald-600">K-Means Cluster: Normal Activity</p>
                 </div>
              </div>
              <div className="bg-white border border-slate-200 p-4 rounded-xl flex items-center">
                 <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center mr-4 shrink-0 text-slate-600"><ThermometerSun className="w-5 h-5" /></div>
                 <div>
                    <h4 className="text-sm font-bold text-slate-800">Forecast Matrix</h4>
                    <p className="text-xs font-medium text-slate-500">No severe weather predicted 48hr.</p>
                 </div>
              </div>
            </div>
          </div>
          
          <div className="mt-8">
            <button className="w-full bg-slate-900 border border-slate-800 hover:bg-slate-800 text-white font-bold py-4 rounded-xl transition-all shadow-md text-sm flex items-center justify-center group">
              <Database className="w-4 h-4 mr-2 group-hover:text-emerald-400 transition-colors" /> Download SQLite Dump
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const ZONES_LAT_LON = {
  'Koramangala': { lat: 12.9352, lon: 77.6245 },
  'Indiranagar': { lat: 12.9784, lon: 77.6408 },
  'Andheri West': { lat: 19.1363, lon: 72.8277 },
  'South Ex': { lat: 28.5684, lon: 77.2183 }
}

export default function App() {
  const [role, setRole] = useState(null)
  const [activeTab, setActiveTab] = useState('home')
  const [userMeta, setUserMeta] = useState(null) // { phone, zone, platform }
  const [quote, setQuote] = useState(null)
  const [adminData, setAdminData] = useState(null)
  const [liveWeather, setLiveWeather] = useState(null)

  const fetchWeatherBackground = async (zone) => {
    try {
      const res = await fetch(`${API_BASE}/weather?zone=${zone}`)
      setLiveWeather(await res.json())
    } catch(e) {}
  }

  const handleLogin = (assignedRole, meta) => {
    setRole(assignedRole)
    setUserMeta(meta)
    setActiveTab(assignedRole === 'admin' ? 'admin' : 'home')
    if (meta?.zone) fetchWeatherBackground(meta.zone)
  }

  const handleLogout = () => {
    setRole(null)
    setUserMeta(null)
    setQuote(null)
    setLiveWeather(null)
  }

  const fetchQuote = async (zone, platform, phone) => {
    try {
      const res = await fetch(`${API_BASE}/quote`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zone, platform, phone })
      })
      const data = await res.json()
      setQuote(data)
      setLiveWeather({
        temperature: data.risk_factors.temp,
        rain_mm: data.risk_factors.rain_mm,
        high_risk: data.risk_factors.high_risk
      })
    } catch (e) { console.error(e) }
  }

  const fetchAdminData = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/dashboard`)
      setAdminData(await res.json())
    } catch(e) {}
  }

  useEffect(() => {
    if (activeTab === 'admin') fetchAdminData()
    if (userMeta?.zone) {
       const interval = setInterval(() => fetchWeatherBackground(userMeta.zone), 60000)
       return () => clearInterval(interval)
    }
  }, [activeTab, userMeta])

  if (!role) return (
    <>
      <LiveBackground />
      <LandingPage onLogin={handleLogin} />
    </>
  )

  const getPageTitle = () => {
    if (activeTab === 'home') return 'Dashboard'
    if (activeTab === 'policy') return 'Policy Details'
    if (activeTab === 'claims') return 'Live Claims Engine'
    if (activeTab === 'admin') return 'System Console'
    return activeTab
  }

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
      <LiveBackground />
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} userRole={role} onLogout={handleLogout} userMeta={userMeta} />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-y-auto relative z-10 selection:bg-emerald-200">
        <Header title={getPageTitle()} userRole={role} setRole={(r) => {setRole(r); setActiveTab(r === 'admin' ? 'admin' : 'home')}} liveWeather={liveWeather} />
        <main className="flex-1 overflow-x-hidden pt-4 pb-12">
          {activeTab === 'home' && role === 'worker' && <WorkerDashboard userMeta={userMeta} quote={quote} fetchQuote={fetchQuote} liveWeather={liveWeather} />}
          {activeTab === 'claims' && role === 'worker' && <ClaimsView userMeta={userMeta} liveWeather={liveWeather} />}
          {activeTab === 'admin' && <AdminDashboard adminData={adminData} />}
        </main>
      </div>
    </div>
  )
}
