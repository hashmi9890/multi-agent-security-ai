import { useState, useEffect, useCallback, useRef } from 'react';
// Try to load framer-motion if available; provide lightweight fallbacks otherwise
declare const require: any;
let motion: any;
let AnimatePresence: any;
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const fm = require('framer-motion');
  motion = fm.motion;
  AnimatePresence = fm.AnimatePresence;
} catch {
  // Fallbacks: simple passthrough components so the app can compile without framer-motion
  motion = (props: any) => props.children ?? null;
  AnimatePresence = (props: any) => props.children ?? null;
}
import { 
  Bot, 
  Wifi, 
  WifiOff, 
  Settings, 
  Activity, 
  Terminal, 
  Shield, 
  Database, 
  MessageSquare,
  RefreshCw,
  Play,
  StopCircle,
  CheckCircle,
  Server,
  Layers,
  Code,
  Webhook,
  TrendingUp,
  Clock,
  FileText,
  Power
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws/logs';

// Types
interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'warning' | 'connecting';
  uptime: number;
  messagesProcessed: number;
  lastActivity: string;
  autoReconnect: boolean;
  healthScore: number;
  config: AgentConfig;
}

interface AgentConfig {
  webhookUrl: string;
  maxRetries: number;
  timeout: number;
  autoReconnectDelay: number;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

interface LogEntry {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  networkLatency: number;
  activeConnections: number;
  messagesPerSecond: number;
  errorRate: number;
}

// Initial Data (fallback if API is not available)
const initialAgents: Agent[] = [
  {
    id: 'langgraph-wa',
    name: 'LangGraph WhatsApp Agent',
    type: 'langgraph',
    status: 'online',
    uptime: 86400,
    messagesProcessed: 15234,
    lastActivity: '2 sec ago',
    autoReconnect: true,
    healthScore: 98,
    config: {
      webhookUrl: 'https://api.langgraph.ai/webhook',
      maxRetries: 5,
      timeout: 30000,
      autoReconnectDelay: 5000,
      logLevel: 'info'
    }
  },
  {
    id: 'opencrow',
    name: 'OpenCROW',
    type: 'opencrow',
    status: 'online',
    uptime: 72000,
    messagesProcessed: 8921,
    lastActivity: '1 sec ago',
    autoReconnect: true,
    healthScore: 95,
    config: {
      webhookUrl: 'https://api.opencrow.io/webhook',
      maxRetries: 3,
      timeout: 25000,
      autoReconnectDelay: 3000,
      logLevel: 'info'
    }
  },
  {
    id: 'multiwa',
    name: 'MultiWA',
    type: 'multiwa',
    status: 'online',
    uptime: 95000,
    messagesProcessed: 23456,
    lastActivity: '0 sec ago',
    autoReconnect: true,
    healthScore: 99,
    config: {
      webhookUrl: 'https://api.multiwa.com/webhook',
      maxRetries: 5,
      timeout: 30000,
      autoReconnectDelay: 5000,
      logLevel: 'debug'
    }
  },
  {
    id: 'openwa-mcp',
    name: 'OpenWA+MCP',
    type: 'openwa-mcp',
    status: 'warning',
    uptime: 45000,
    messagesProcessed: 12089,
    lastActivity: '5 sec ago',
    autoReconnect: true,
    healthScore: 87,
    config: {
      webhookUrl: 'https://api.openwa.dev/mcp',
      maxRetries: 4,
      timeout: 20000,
      autoReconnectDelay: 4000,
      logLevel: 'info'
    }
  },
  {
    id: 'twilio-wa',
    name: 'TWILIO WhatsApp API',
    type: 'twilio',
    status: 'online',
    uptime: 120000,
    messagesProcessed: 45678,
    lastActivity: '1 sec ago',
    autoReconnect: true,
    healthScore: 97,
    config: {
      webhookUrl: 'https://api.twilio.com/webhook',
      maxRetries: 5,
      timeout: 30000,
      autoReconnectDelay: 5000,
      logLevel: 'info'
    }
  },
  {
    id: 'baileys',
    name: 'Baileys/whatsapp-web.js',
    type: 'baileys',
    status: 'online',
    uptime: 68000,
    messagesProcessed: 19234,
    lastActivity: '3 sec ago',
    autoReconnect: true,
    healthScore: 94,
    config: {
      webhookUrl: 'http://localhost:3000/webhook',
      maxRetries: 5,
      timeout: 30000,
      autoReconnectDelay: 5000,
      logLevel: 'debug'
    }
  }
];

const generateChartData = () => {
  const data = [];
  for (let i = 0; i < 24; i++) {
    data.push({
      time: `${i}:00`,
      messages: Math.floor(Math.random() * 1000) + 500,
      errors: Math.floor(Math.random() * 50),
      latency: Math.floor(Math.random() * 100) + 20
    });
  }
  return data;
};

// Main Component
export default function App() {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpuUsage: 45,
    memoryUsage: 62,
    networkLatency: 35,
    activeConnections: 6,
    messagesPerSecond: 127,
    errorRate: 0.02
  });
  const [chartData, setChartData] = useState(generateChartData());
  const [systemActive, setSystemActive] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Add log entry
  const addLog = useCallback((agent: string, message: string, type: LogEntry['type'] = 'info') => {
    const newLog: LogEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      agent,
      message,
      type
    };
    setLogs((prev: LogEntry[]) => [newLog, ...prev].slice(0, 100));
  }, []);

  // Connect to WebSocket for real-time logs
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket(WS_URL);
        
        wsRef.current.onopen = () => {
          setApiConnected(true);
          addLog('System', 'WebSocket connected', 'success');
        };
        
        wsRef.current.onmessage = (event: Event) => {
          const data = JSON.parse((event as MessageEvent).data);
          if (data.type === 'log' && data.data) {
            setLogs((prev: LogEntry[]) => [data.data, ...prev].slice(0, 100));
          } else if (data.type === 'init' && data.logs) {
            setLogs(data.logs);
          }
        };
        
        wsRef.current.onclose = () => {
          setApiConnected(false);
          addLog('System', 'WebSocket disconnected - reconnecting...', 'warning');
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = () => {
          setApiConnected(false);
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setApiConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [addLog]);

  // Fetch data from API
  const fetchAgents = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents`);
      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents);
        setApiConnected(true);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      // API not available, using local state
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/metrics`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    fetchAgents();
    fetchMetrics();
    
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAgents();
      fetchMetrics();
      
      // Update chart data periodically
      if (Math.random() > 0.9) {
        setChartData(generateChartData());
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchAgents, fetchMetrics]);

  // Toggle agent status
  const toggleAgent = useCallback(async (agentId: string) => {
    const agent = agents.find((a: Agent) => a.id === agentId);
    if (!agent) return;

    try {
      const action = agent.status === 'online' ? 'stop' : 'start';
      
      const response = await fetch(`${API_BASE_URL}/agents/${agentId}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });

      if (response.ok) {
        addLog(agent.name, 
          action === 'stop' ? 'Agent manually stopped' : 'Agent starting...', 
          action === 'stop' ? 'warning' : 'info'
        );
        fetchAgents();
      }
    } catch (error) {
      // Fallback to local state if API fails
      setAgents((prev: Agent[]) => prev.map((a: Agent) => {
        if (a.id === agentId) {
          const newStatus = a.status === 'online' ? 'offline' : 'connecting';
          addLog(a.name, 
            newStatus === 'offline' ? 'Agent manually stopped' : 'Agent starting...', 
            newStatus === 'offline' ? 'warning' : 'info'
          );
          
          if (newStatus === 'connecting') {
            setTimeout(() => {
              setAgents((current: Agent[]) => current.map((agent: Agent) => 
                agent.id === agentId ? { ...agent, status: 'online', lastActivity: 'Just now' } : agent
              ));
              addLog(a.name, 'Agent connected successfully', 'success');
            }, 2000 + Math.random() * 2000);
          }
          
          return { ...a, status: newStatus };
        }
        return a;
      }));
    }
  }, [agents, addLog, fetchAgents]);

  // Toggle all agents
  const toggleAllAgents = useCallback(async (activate: boolean) => {
    try {
      const endpoint = activate ? '/system/start-all' : '/system/stop-all';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST'
      });

      if (response.ok) {
        setSystemActive(activate);
        fetchAgents();
        addLog('System', 
          activate ? 'All agents activated by master control' : 'All agents deactivated by master control',
          activate ? 'success' : 'warning'
        );
      }
    } catch (error) {
      // Fallback to local state
      setAgents((prev: Agent[]) => prev.map((agent: Agent) => ({
        ...agent,
        status: activate ? 'online' : 'offline',
        lastActivity: 'Just now'
      })));
      setSystemActive(activate);
      addLog('System', 
        activate ? 'All agents activated' : 'All agents deactivated',
        activate ? 'success' : 'warning'
      );
    }
  }, [addLog, fetchAgents]);

  // Enable auto-reconnect for all
  const enableAutoReconnect = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/system/auto-reconnect`, {
        method: 'POST'
      });

      if (response.ok) {
        addLog('System', 'Auto-reconnect enabled for all agents', 'success');
        fetchAgents();
      }
    } catch (error) {
      setAgents((prev: Agent[]) => prev.map((agent: Agent) => ({
        ...agent,
        autoReconnect: true
      })));
      addLog('System', 'Auto-reconnect enabled for all agents', 'success');
    }
  }, [addLog, fetchAgents]);

  // Clear logs
  const clearLogs = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/logs/clear`, {
        method: 'POST'
      });

      if (response.ok) {
        setLogs([]);
        addLog('System', 'Logs cleared', 'info');
      }
    } catch (error) {
      setLogs([]);
    }
  }, [addLog]);

  const formatUptime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs}h ${mins}m ${secs}s`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400';
      case 'offline': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'connecting': return 'text-cyan-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      case 'connecting': return 'bg-cyan-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen cyber-grid-bg relative overflow-hidden">
      {/* Matrix Rain Background Effect */}
      <div className="matrix-rain" />
      
      {/* Header */}
      <header className="relative z-10 cyber-border cyber-box-glow m-4 rounded-lg p-6">
        <div className="corner-decoration top-left" />
        <div className="corner-decoration top-right" />
        <div className="corner-decoration bottom-left" />
        <div className="corner-decoration bottom-right" />
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="h-16 w-16 rounded-full cyber-box-glow flex items-center justify-center"
            >
              <Bot className="h-10 w-10 text-cyan-400" />
            </motion.div>
            <div>
              <h1 className="cyber-font text-4xl font-bold cyber-gradient-text cyber-text-glow">
                MULTI-AGENT WHATSAPP SYSTEM
              </h1>
              <p className="text-cyan-400/70 text-lg">Cyberpunk Edition v2.0</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 cyber-border rounded-lg">
              <Clock className="h-5 w-5 text-cyan-400" />
              <span className="cyber-font text-cyan-400">
                {new Date().toLocaleTimeString()}
              </span>
            </div>
            
            <div className={`flex items-center gap-2 px-4 py-2 cyber-border rounded-lg ${apiConnected ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
              <div className={`status-indicator ${apiConnected ? 'status-online' : 'status-offline'}`} />
              <span className={`cyber-font text-sm ${apiConnected ? 'text-green-400' : 'text-red-400'}`}>
                API: {apiConnected ? 'CONNECTED' : 'OFFLINE'}
              </span>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-3 cyber-border rounded-lg cyber-btn ${autoRefresh ? 'bg-cyan-500/20' : 'bg-gray-500/20'}`}
            >
              <RefreshCw className={`h-6 w-6 ${autoRefresh ? 'text-cyan-400' : 'text-gray-400'} ${autoRefresh ? 'animate-spin' : ''}`} style={{ animationDuration: '3s' }} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 cyber-border rounded-lg cyber-btn bg-purple-500/20"
            >
              <Settings className="h-6 w-6 text-purple-400" />
            </motion.button>
          </div>
        </div>
      </header>

      {/* Master Control Panel */}
      <div className="relative z-10 m-4 cyber-border cyber-box-glow rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="cyber-font text-2xl text-cyan-400 flex items-center gap-3">
            <Power className="h-8 w-8" />
            MASTER CONTROL PANEL
          </h2>
          <div className="flex items-center gap-4">
            <span className={`cyber-font ${systemActive ? 'text-green-400' : 'text-red-400'}`}>
              SYSTEM: {systemActive ? 'ACTIVE' : 'INACTIVE'}
            </span>
            <span className={`status-indicator ${systemActive ? 'status-online' : 'status-offline'}`} />
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => toggleAllAgents(true)}
            className="cyber-btn cyber-border rounded-lg p-4 bg-green-500/10 hover:bg-green-500/20 transition-all"
          >
            <Play className="h-8 w-8 text-green-400 mx-auto mb-2" />
            <span className="cyber-font text-green-400">START ALL</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => toggleAllAgents(false)}
            className="cyber-btn cyber-border rounded-lg p-4 bg-red-500/10 hover:bg-red-500/20 transition-all"
          >
            <StopCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
            <span className="cyber-font text-red-400">STOP ALL</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={enableAutoReconnect}
            className="cyber-btn cyber-border rounded-lg p-4 bg-cyan-500/10 hover:bg-cyan-500/20 transition-all"
          >
            <RefreshCw className="h-8 w-8 text-cyan-400 mx-auto mb-2" />
            <span className="cyber-font text-cyan-400">AUTO RECONNECT</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={clearLogs}
            className="cyber-btn cyber-border rounded-lg p-4 bg-yellow-500/10 hover:bg-yellow-500/20 transition-all"
          >
            <FileText className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
            <span className="cyber-font text-yellow-400">CLEAR LOGS</span>
          </motion.button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="relative z-10 grid grid-cols-12 gap-4 m-4">
        {/* System Metrics */}
        <div className="col-span-3 cyber-border cyber-box-glow rounded-lg p-6">
          <h3 className="cyber-font text-xl text-cyan-400 mb-4 flex items-center gap-2">
            <Activity className="h-6 w-6" />
            SYSTEM METRICS
          </h3>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">CPU Usage</span>
                <span className="text-cyan-400">{metrics.cpuUsage.toFixed(1)}%</span>
              </div>
              <div className="progress-bar-cyber">
                <div style={{ width: `${metrics.cpuUsage}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Memory</span>
                <span className="text-purple-400">{metrics.memoryUsage.toFixed(1)}%</span>
              </div>
              <div className="progress-bar-cyber">
                <div style={{ width: `${metrics.memoryUsage}%`, background: 'linear-gradient(90deg, #a855f7, #d946ef)' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Network Latency</span>
                <span className="text-green-400">{metrics.networkLatency.toFixed(0)}ms</span>
              </div>
              <div className="progress-bar-cyber">
                <div style={{ width: `${Math.min(100, metrics.networkLatency / 2)}%`, background: 'linear-gradient(90deg, #22c55e, #00ff88)' }} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="text-center p-3 cyber-border rounded-lg">
                <Wifi className="h-6 w-6 text-cyan-400 mx-auto mb-2" />
                <div className="cyber-font text-2xl text-cyan-400">{metrics.activeConnections}</div>
                <div className="text-xs text-gray-400">Connections</div>
              </div>
              <div className="text-center p-3 cyber-border rounded-lg">
                <MessageSquare className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                <div className="cyber-font text-2xl text-purple-400">{metrics.messagesPerSecond}</div>
                <div className="text-xs text-gray-400">Msg/Sec</div>
              </div>
            </div>

            <div className="text-center p-3 cyber-border rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-400 mx-auto mb-2" />
              <div className="cyber-font text-2xl text-green-400">{(metrics.errorRate * 100).toFixed(2)}%</div>
              <div className="text-xs text-gray-400">Error Rate</div>
            </div>
          </div>
        </div>

        {/* Agent Cards */}
        <div className="col-span-6">
          <h3 className="cyber-font text-xl text-cyan-400 mb-4 flex items-center gap-2">
            <Layers className="h-6 w-6" />
            AGENT STATUS
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <AnimatePresence>
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                  className={`agent-card rounded-lg p-4 cursor-pointer ${selectedAgent === agent.id ? 'cyber-box-glow' : ''}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`h-3 w-3 rounded-full ${getStatusBg(agent.status)} status-indicator`} />
                      <span className="cyber-font text-sm text-cyan-400">{agent.name}</span>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleAgent(agent.id);
                      }}
                      className={`p-2 cyber-border rounded-lg ${agent.status === 'online' ? 'bg-red-500/20' : 'bg-green-500/20'}`}
                    >
                      {agent.status === 'online' ? (
                        <WifiOff className="h-4 w-4 text-red-400" />
                      ) : (
                        <Wifi className="h-4 w-4 text-green-400" />
                      )}
                    </motion.button>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-500">Status:</span>
                      <span className={`ml-2 ${getStatusColor(agent.status)}`}>{agent.status.toUpperCase()}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Health:</span>
                      <span className="ml-2 text-green-400">{agent.healthScore}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Uptime:</span>
                      <span className="ml-2 text-cyan-400">{formatUptime(agent.uptime)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Messages:</span>
                      <span className="ml-2 text-purple-400">{agent.messagesProcessed.toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">Auto-Reconnect:</span>
                      <div className={`toggle-switch ${agent.autoReconnect ? 'active' : ''}`} />
                    </div>
                    <span className="text-xs text-gray-500">{agent.lastActivity}</span>
                  </div>

                  {selectedAgent === agent.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-4 pt-4 border-t border-cyan-500/20"
                    >
                      <div className="text-xs space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Type:</span>
                          <span className="text-cyan-400">{agent.type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Webhook:</span>
                          <span className="text-purple-400 truncate max-w-[200px]">{agent.config.webhookUrl}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Max Retries:</span>
                          <span className="text-cyan-400">{agent.config.maxRetries}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Timeout:</span>
                          <span className="text-cyan-400">{agent.config.timeout}ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Log Level:</span>
                          <span className="text-cyan-400">{agent.config.logLevel.toUpperCase()}</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Live Logs */}
        <div className="col-span-3 cyber-border cyber-box-glow rounded-lg p-6 cyber-scan-line">
          <h3 className="cyber-font text-xl text-cyan-400 mb-4 flex items-center gap-2">
            <Terminal className="h-6 w-6" />
            LIVE LOGS
          </h3>
          
          <div className="h-[400px] overflow-y-auto scrollbar-cyber space-y-1">
            <AnimatePresence>
              {logs.slice(0, 50).map((log) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className={`log-entry ${log.type}`}
                >
                  <span className="text-gray-500">[{log.timestamp}]</span>
                  <span className="text-cyan-400 font-bold">{log.agent}:</span>
                  <span className="ml-2">{log.message}</span>
                </motion.div>
              ))}
            </AnimatePresence>
            {logs.length === 0 && (
              <div className="text-center text-gray-500 py-10">
                <Terminal className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No logs yet...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="relative z-10 grid grid-cols-2 gap-4 m-4">
        <div className="cyber-border cyber-box-glow rounded-lg p-6">
          <h3 className="cyber-font text-xl text-cyan-400 mb-4 flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            MESSAGE THROUGHPUT (24h)
          </h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#00f0ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#4a5568" fontSize={10} />
                <YAxis stroke="#4a5568" fontSize={10} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#12121f', 
                    border: '1px solid #00f0ff',
                    borderRadius: '8px'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="messages" 
                  stroke="#00f0ff" 
                  fillOpacity={1} 
                  fill="url(#colorMessages)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="cyber-border cyber-box-glow rounded-lg p-6">
          <h3 className="cyber-font text-xl text-cyan-400 mb-4 flex items-center gap-2">
            <Activity className="h-6 w-6" />
            NETWORK LATENCY (24h)
          </h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="time" stroke="#4a5568" fontSize={10} />
                <YAxis stroke="#4a5568" fontSize={10} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#12121f', 
                    border: '1px solid #00ff88',
                    borderRadius: '8px'
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="latency" 
                  stroke="#00ff88" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Integration Info */}
      <div className="relative z-10 m-4 cyber-border cyber-box-glow-secondary rounded-lg p-6">
        <h3 className="cyber-font text-xl text-purple-400 mb-4 flex items-center gap-2">
          <Webhook className="h-6 w-6" />
          INTEGRATION STATUS
        </h3>
        
        <div className="grid grid-cols-6 gap-4">
          {[
            { name: 'VSCode', status: 'connected', icon: Code },
            { name: 'PostgreSQL', status: 'connected', icon: Database },
            { name: 'Redis', status: 'connected', icon: Server },
            { name: 'MongoDB', status: 'connected', icon: Database },
            { name: 'Docker', status: 'connected', icon: Layers },
            { name: 'Kubernetes', status: 'warning', icon: Shield }
          ].map((service) => (
            <div key={service.name} className="text-center p-4 cyber-border rounded-lg">
              <service.icon className={`h-8 w-8 mx-auto mb-2 ${service.status === 'connected' ? 'text-green-400' : 'text-yellow-400'}`} />
              <div className="cyber-font text-sm text-cyan-400">{service.name}</div>
              <div className={`text-xs mt-1 ${service.status === 'connected' ? 'text-green-400' : 'text-yellow-400'}`}>
                {service.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Settings Modal */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
            onClick={() => setShowSettings(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="cyber-border cyber-box-glow rounded-lg p-8 max-w-2xl w-full mx-4 bg-[#12121f]/95"
            >
              <h3 className="cyber-font text-2xl text-cyan-400 mb-6 flex items-center gap-3">
                <Settings className="h-8 w-8" />
                SYSTEM SETTINGS
              </h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-cyan-400 mb-2">Global Timeout (ms)</label>
                  <input 
                    type="number" 
                    defaultValue={30000}
                    className="w-full cyber-border rounded-lg p-3 bg-[#0a0a0f] text-cyan-400 focus:outline-none focus:border-cyan-400"
                  />
                </div>
                
                <div>
                  <label className="block text-cyan-400 mb-2">Max Retries</label>
                  <input 
                    type="number" 
                    defaultValue={5}
                    className="w-full cyber-border rounded-lg p-3 bg-[#0a0a0f] text-cyan-400 focus:outline-none focus:border-cyan-400"
                  />
                </div>
                
                <div>
                  <label className="block text-cyan-400 mb-2">Log Level</label>
                  <select className="w-full cyber-border rounded-lg p-3 bg-[#0a0a0f] text-cyan-400 focus:outline-none focus:border-cyan-400">
                    <option value="debug">DEBUG</option>
                    <option value="info">INFO</option>
                    <option value="warn">WARN</option>
                    <option value="error">ERROR</option>
                  </select>
                </div>
                
                <div className="flex items-center justify-between p-4 cyber-border rounded-lg">
                  <span className="text-cyan-400">Enable Auto-Healing</span>
                  <div className="toggle-switch active" />
                </div>
                
                <div className="flex items-center justify-between p-4 cyber-border rounded-lg">
                  <span className="text-cyan-400">Enable Notifications</span>
                  <div className="toggle-switch active" />
                </div>
                
                <div className="flex items-center justify-between p-4 cyber-border rounded-lg">
                  <span className="text-cyan-400">Dark Mode</span>
                  <div className="toggle-switch active" />
                </div>
              </div>
              
              <div className="flex gap-4 mt-8">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowSettings(false)}
                  className="flex-1 cyber-btn cyber-border rounded-lg p-4 bg-cyan-500/20 text-cyan-400 cyber-font"
                >
                  SAVE SETTINGS
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowSettings(false)}
                  className="flex-1 cyber-btn cyber-border rounded-lg p-4 bg-red-500/20 text-red-400 cyber-font"
                >
                  CANCEL
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="relative z-10 m-4 cyber-border rounded-lg p-4 text-center">
        <div className="flex items-center justify-center gap-6 text-sm">
          <span className="text-gray-500">Multi-Agent WhatsApp Automation System</span>
          <span className="text-cyan-400">|</span>
          <span className="text-gray-500">Cyberpunk Edition</span>
          <span className="text-cyan-400">|</span>
          <span className="text-green-400 flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            All Systems Operational
          </span>
        </div>
      </footer>
    </div>
  );
}
