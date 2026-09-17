import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Clock, BarChart2, Activity, Globe, RefreshCw, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import './index.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [status, setStatus] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [niftyHistory, setNiftyHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, dashRes, niftyRes] = await Promise.all([
        axios.get(`${API_BASE}/market-status`),
        axios.get(`${API_BASE}/dashboard-data`),
        axios.get(`${API_BASE}/stock/NIFTY%2050`).catch(() => ({ data: { historical: [] } }))
      ]);
      setStatus(statusRes.data);
      setDashboard(dashRes.data);
      
      if (niftyRes.data && niftyRes.data.historical) {
        // Format timestamp for display
        const history = niftyRes.data.historical.map(d => ({
          ...d,
          time: new Date(d.Timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }));
        setNiftyHistory(history);
      }
      
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!dashboard) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }} style={{ display: 'flex', justifyContent: 'center' }}>
          <RefreshCw size={48} style={{ color: 'var(--accent)' }} />
        </motion.div>
        <h2 style={{ marginLeft: '1rem', fontSize: '1.25rem' }}>Initializing Market Engine...</h2>
      </div>
    );
  }

  const { kpi_data, all_stocks, top_gainers, top_losers } = dashboard;
  const isUp = kpi_data.nifty_change >= 0;

  // Custom Tooltip for Recharts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ background: 'var(--bg-dark)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>{label}</p>
          <p style={{ margin: 0, fontWeight: 'bold' }}>₹{payload[0].value.toLocaleString('en-IN')}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="header-title"
          >
            ⚡ NIFTY 50 Live Intelligence
          </motion.h1>
          <p className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} /> Real-time Indian Stock Market Analytics
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="status-badge mb-2">
            <span className={`status-dot ${status?.is_open ? 'open' : 'closed'}`}></span>
            {status?.status_text || 'Unknown'}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'flex-end' }}>
              <Clock size={14} /> Last Update: {lastRefreshed.toLocaleTimeString()}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'flex-end', marginTop: '4px', cursor: 'pointer' }} onClick={fetchData}>
               <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> {loading ? 'Refreshing...' : 'Auto-refresh on'}
            </div>
          </div>
        </div>
      </header>

      {/* KPI Section */}
      <div className="kpi-grid">
        <motion.div className="glass-panel kpi-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
          <div className="kpi-label">NIFTY 50 LTP</div>
          <div className="kpi-value">₹{kpi_data.nifty_ltp?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
          <div className={isUp ? 'text-positive' : 'text-negative'} style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            {isUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            {isUp ? '+' : ''}{kpi_data.nifty_change?.toFixed(2)} ({isUp ? '+' : ''}{kpi_data.nifty_pchange?.toFixed(2)}%)
          </div>
        </motion.div>
        
        <motion.div className="glass-panel kpi-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
          <div className="kpi-label">Market Breadth</div>
          <div className="kpi-value" style={{ display: 'flex', gap: '1rem' }}>
            <span className="text-positive" title="Advancers">{kpi_data.advancers}</span>
            <span style={{ color: 'var(--text-muted)' }}>:</span>
            <span className="text-negative" title="Decliners">{kpi_data.decliners}</span>
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Total Stocks: {kpi_data.num_stocks}</div>
        </motion.div>

        <motion.div className="glass-panel kpi-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}>
          <div className="kpi-label">Total Volume</div>
          <div className="kpi-value">{kpi_data.total_volume?.toLocaleString('en-IN')}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Shares Traded</div>
        </motion.div>

        <motion.div className="glass-panel kpi-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }}>
          <div className="kpi-label">Total Value</div>
          <div className="kpi-value">₹{kpi_data.total_value?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Crores</div>
        </motion.div>
      </div>

      <div className="dashboard-grid">
        {/* NIFTY 50 Trend Chart */}
        <motion.div className="glass-panel col-span-8" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <LineChartIcon className="text-accent" /> NIFTY 50 Intraday Trend
          </h3>
          <div style={{ height: '300px', width: '100%' }}>
            {niftyHistory.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={niftyHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={isUp ? 'var(--positive)' : 'var(--negative)'} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={isUp ? 'var(--positive)' : 'var(--negative)'} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                  <YAxis domain={['auto', 'auto']} stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="LTP" stroke={isUp ? 'var(--positive)' : 'var(--negative)'} fillOpacity={1} fill="url(#colorPrice)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                Waiting for sufficient historical data...
              </div>
            )}
          </div>
        </motion.div>

        {/* Top Gainers Bar Chart */}
        <motion.div className="glass-panel col-span-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp className="text-positive" /> Top 5 Gainers (%)
          </h3>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top_gainers?.slice(0, 5)} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="var(--text-muted)" />
                <YAxis dataKey="SYMBOL" type="category" stroke="var(--text-muted)" width={80} />
                <Tooltip content={<CustomTooltip />} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                <Bar dataKey="% CHANGE" fill="var(--positive)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Top Losers */}
        <motion.div className="glass-panel col-span-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingDown className="text-negative" /> Top Losers
          </h3>
          <div>
            {top_losers?.slice(0,5).map(stock => (
              <div key={stock.SYMBOL} className="list-item">
                <div>
                  <div className="list-item-title">{stock.SYMBOL}</div>
                  <div className="list-item-subtitle">₹{stock.LTP.toLocaleString('en-IN')}</div>
                </div>
                <div className="bg-negative">{stock['% CHANGE'].toFixed(2)}%</div>
              </div>
            ))}
          </div>
        </motion.div>
        
        {/* Market Stats Summary */}
         <motion.div className="glass-panel col-span-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart2 className="text-accent" /> NIFTY 50 Summary
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border)' }}>
                <span className="text-muted">Open</span>
                <span style={{ fontWeight: 600 }}>₹{kpi_data.nifty_open?.toLocaleString('en-IN')}</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border)' }}>
                <span className="text-muted">Day High</span>
                <span className="text-positive" style={{ fontWeight: 600 }}>₹{kpi_data.nifty_high?.toLocaleString('en-IN')}</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border)' }}>
                <span className="text-muted">Day Low</span>
                <span className="text-negative" style={{ fontWeight: 600 }}>₹{kpi_data.nifty_low?.toLocaleString('en-IN')}</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0' }}>
                <span className="text-muted">Previous Close</span>
                <span style={{ fontWeight: 600 }}>₹{kpi_data.nifty_prev_close?.toLocaleString('en-IN')}</span>
             </div>
          </div>
        </motion.div>

        {/* Live Market Table */}
        <motion.div className="glass-panel col-span-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Globe className="text-accent" /> All NIFTY 50 Constituents
            </h3>
            <button 
              onClick={() => {
                const headers = ['SYMBOL', 'LTP', 'CHANGE', '% CHANGE', 'VOLUME', 'VALUE (Cr)'];
                const csvData = all_stocks.map(row => 
                  `${row.SYMBOL},${row.LTP},${row.CHANGE},${row['% CHANGE']},${row['VOLUME (shares)']},${row['VALUE (Crores)']}`
                );
                const csvString = [headers.join(','), ...csvData].join('\n');
                const blob = new Blob([csvString], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.setAttribute('href', url);
                a.setAttribute('download', `nifty50_live_${new Date().toISOString().slice(0,10)}.csv`);
                a.click();
              }}
              style={{
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontWeight: 600,
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}
              onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            >
              📥 Download CSV
            </button>
          </div>
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>LTP (₹)</th>
                  <th>CHANGE</th>
                  <th>% CHANGE</th>
                  <th>VOLUME</th>
                  <th>VALUE (Cr)</th>
                </tr>
              </thead>
              <tbody>
                {all_stocks?.map(stock => (
                  <tr key={stock.SYMBOL}>
                    <td style={{ fontWeight: 600 }}>{stock.SYMBOL}</td>
                    <td>{stock.LTP?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td className={stock.CHANGE >= 0 ? 'text-positive' : 'text-negative'}>
                      {stock.CHANGE > 0 ? '+' : ''}{stock.CHANGE?.toFixed(2)}
                    </td>
                    <td>
                      <span className={stock['% CHANGE'] >= 0 ? 'bg-positive' : 'bg-negative'}>
                        {stock['% CHANGE'] > 0 ? '+' : ''}{stock['% CHANGE']?.toFixed(2)}%
                      </span>
                    </td>
                    <td>{stock['VOLUME (shares)']?.toLocaleString('en-IN')}</td>
                    <td>{stock['VALUE (Crores)']?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default App;
