"""
Multi-Agent WhatsApp API Server
Connects Python backend with React Cyberpunk Frontend
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent WhatsApp API",
    description="API for Cyberpunk Multi-Agent WhatsApp System",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class AgentConfig(BaseModel):
    webhookUrl: str
    maxRetries: int = 5
    timeout: int = 30000
    autoReconnectDelay: int = 5000
    logLevel: str = "info"

class AgentStatus(BaseModel):
    id: str
    name: str
    type: str
    status: str  # online, offline, warning, connecting
    uptime: int
    messagesProcessed: int
    lastActivity: str
    autoReconnect: bool
    healthScore: int
    config: AgentConfig

class SystemMetrics(BaseModel):
    cpuUsage: float
    memoryUsage: float
    networkLatency: float
    activeConnections: int
    messagesPerSecond: int
    errorRate: float

class LogEntry(BaseModel):
    id: str
    timestamp: str
    agent: str
    message: str
    type: str  # info, success, warning, error

# ==================== GLOBAL STATE ====================

# Simulated agent data (replace with your actual orchestrator)
agents_db: Dict[str, dict] = {
    "langgraph-wa": {
        "id": "langgraph-wa",
        "name": "LangGraph WhatsApp Agent",
        "type": "langgraph",
        "status": "online",
        "uptime": 86400,
        "messagesProcessed": 15234,
        "lastActivity": "2 sec ago",
        "autoReconnect": True,
        "healthScore": 98,
        "config": {
            "webhookUrl": "https://api.langgraph.ai/webhook",
            "maxRetries": 5,
            "timeout": 30000,
            "autoReconnectDelay": 5000,
            "logLevel": "info"
        }
    },
    "opencrow": {
        "id": "opencrow",
        "name": "OpenCROW",
        "type": "opencrow",
        "status": "online",
        "uptime": 72000,
        "messagesProcessed": 8921,
        "lastActivity": "1 sec ago",
        "autoReconnect": True,
        "healthScore": 95,
        "config": {
            "webhookUrl": "https://api.opencrow.io/webhook",
            "maxRetries": 3,
            "timeout": 25000,
            "autoReconnectDelay": 3000,
            "logLevel": "info"
        }
    },
    "multiwa": {
        "id": "multiwa",
        "name": "MultiWA",
        "type": "multiwa",
        "status": "online",
        "uptime": 95000,
        "messagesProcessed": 23456,
        "lastActivity": "0 sec ago",
        "autoReconnect": True,
        "healthScore": 99,
        "config": {
            "webhookUrl": "https://api.multiwa.com/webhook",
            "maxRetries": 5,
            "timeout": 30000,
            "autoReconnectDelay": 5000,
            "logLevel": "debug"
        }
    },
    "openwa-mcp": {
        "id": "openwa-mcp",
        "name": "OpenWA+MCP",
        "type": "openwa-mcp",
        "status": "warning",
        "uptime": 45000,
        "messagesProcessed": 12089,
        "lastActivity": "5 sec ago",
        "autoReconnect": True,
        "healthScore": 87,
        "config": {
            "webhookUrl": "https://api.openwa.dev/mcp",
            "maxRetries": 4,
            "timeout": 20000,
            "autoReconnectDelay": 4000,
            "logLevel": "info"
        }
    },
    "twilio-wa": {
        "id": "twilio-wa",
        "name": "TWILIO WhatsApp API",
        "type": "twilio",
        "status": "online",
        "uptime": 120000,
        "messagesProcessed": 45678,
        "lastActivity": "1 sec ago",
        "autoReconnect": True,
        "healthScore": 97,
        "config": {
            "webhookUrl": "https://api.twilio.com/webhook",
            "maxRetries": 5,
            "timeout": 30000,
            "autoReconnectDelay": 5000,
            "logLevel": "info"
        }
    },
    "baileys": {
        "id": "baileys",
        "name": "Baileys/whatsapp-web.js",
        "type": "baileys",
        "status": "online",
        "uptime": 68000,
        "messagesProcessed": 19234,
        "lastActivity": "3 sec ago",
        "autoReconnect": True,
        "healthScore": 94,
        "config": {
            "webhookUrl": "http://localhost:3000/webhook",
            "maxRetries": 5,
            "timeout": 30000,
            "autoReconnectDelay": 5000,
            "logLevel": "debug"
        }
    }
}

logs_db: List[dict] = []
metrics_db = {
    "cpuUsage": 45.0,
    "memoryUsage": 62.0,
    "networkLatency": 35.0,
    "activeConnections": 6,
    "messagesPerSecond": 127,
    "errorRate": 0.02
}

system_active = True
websocket_clients: List[WebSocket] = []

# ==================== HELPER FUNCTIONS ====================

def add_log(agent: str, message: str, log_type: str = "info"):
    """Add log entry to database"""
    log = {
        "id": str(datetime.now().timestamp()),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "message": message,
        "type": log_type
    }
    logs_db.append(log)
    # Keep only last 1000 logs
    if len(logs_db) > 1000:
        logs_db.pop(0)
    # Broadcast to websocket clients
    asyncio.create_task(broadcast_log(log))
    logger.info(f"[{log['timestamp']}] {agent}: {message}")

async def broadcast_log(log: dict):
    """Broadcast log to all websocket clients"""
    for client in websocket_clients:
        try:
            await client.send_json({"type": "log", "data": log})
        except:
            pass

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent WhatsApp API Server",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/agents")
async def get_agents():
    """Get all agent statuses"""
    return {"agents": list(agents_db.values())}

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent status"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.post("/api/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, action: dict):
    """Start/Stop specific agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    action_type = action.get("action", "toggle")
    agent = agents_db[agent_id]
    
    if action_type == "stop" or (action_type == "toggle" and agent["status"] == "online"):
        agent["status"] = "offline"
        agent["lastActivity"] = "Just now"
        add_log(agent["name"], "Agent manually stopped", "warning")
        return {"status": "stopped", "agent_id": agent_id}
    else:
        agent["status"] = "connecting"
        add_log(agent["name"], "Agent starting...", "info")
        
        # Simulate connection delay
        async def connect_delay():
            await asyncio.sleep(2)
            agent["status"] = "online"
            agent["lastActivity"] = "Reconnected"
            add_log(agent["name"], "Agent connected successfully", "success")
        
        asyncio.create_task(connect_delay())
        return {"status": "starting", "agent_id": agent_id}

@app.post("/api/system/start-all")
async def start_all_agents():
    """Start all agents"""
    global system_active
    system_active = True
    
    for agent_id, agent in agents_db.items():
        if agent["status"] != "online":
            agent["status"] = "connecting"
            add_log(agent["name"], "Agent activated by master control", "success")
    
    # Simulate all agents coming online
    async def activate_all():
        await asyncio.sleep(2)
        for agent in agents_db.values():
            agent["status"] = "online"
            agent["lastActivity"] = "Just now"
    
    asyncio.create_task(activate_all())
    return {"status": "all_agents_started", "system_active": True}

@app.post("/api/system/stop-all")
async def stop_all_agents():
    """Stop all agents"""
    global system_active
    system_active = False
    
    for agent_id, agent in agents_db.items():
        if agent["status"] == "online":
            agent["status"] = "offline"
            agent["lastActivity"] = "Just now"
            add_log(agent["name"], "Agent deactivated by master control", "warning")
    
    return {"status": "all_agents_stopped", "system_active": False}

@app.post("/api/system/auto-reconnect")
async def enable_auto_reconnect():
    """Enable auto-reconnect for all agents"""
    for agent in agents_db.values():
        agent["autoReconnect"] = True
    
    add_log("System", "Auto-reconnect enabled for all agents", "success")
    return {"status": "auto_reconnect_enabled"}

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    # Update metrics dynamically
    import random
    metrics_db["cpuUsage"] = min(100, max(20, metrics_db["cpuUsage"] + (random.random() - 0.5) * 10))
    metrics_db["memoryUsage"] = min(100, max(40, metrics_db["memoryUsage"] + (random.random() - 0.5) * 5))
    metrics_db["networkLatency"] = min(200, max(10, metrics_db["networkLatency"] + (random.random() - 0.5) * 20))
    metrics_db["activeConnections"] = sum(1 for a in agents_db.values() if a["status"] == "online")
    metrics_db["messagesPerSecond"] = random.randint(100, 200)
    metrics_db["errorRate"] = random.random() * 0.05
    
    return metrics_db

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """Get recent logs"""
    return {"logs": logs_db[-limit:]}

@app.post("/api/logs/clear")
async def clear_logs():
    """Clear all logs"""
    logs_db.clear()
    add_log("System", "Logs cleared", "info")
    return {"status": "logs_cleared"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_count": len(agents_db),
        "active_agents": sum(1 for a in agents_db.values() if a["status"] == "online")
    }

# ==================== WEBSOCKET ====================

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time log streaming"""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    # Send initial logs
    await websocket.send_json({"type": "init", "logs": logs_db[-50:]})
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        websocket_clients.remove(websocket)

# ==================== AUTO-RECONNECT MONITOR ====================

async def monitor_agents():
    """Monitor agents and auto-reconnect if needed"""
    while True:
        await asyncio.sleep(10)  # Check every 10 seconds
        
        if not system_active:
            continue
        
        for agent_id, agent in agents_db.items():
            if agent["status"] == "offline" and agent["autoReconnect"]:
                # Simulate auto-reconnect
                agent["status"] = "connecting"
                add_log(agent["name"], "Auto-reconnect triggered...", "warning")
                
                async def reconnect(agent_id):
                    await asyncio.sleep(3)
                    if agent_id in agents_db:
                        agents_db[agent_id]["status"] = "online"
                        agents_db[agent_id]["lastActivity"] = "Reconnected"
                        add_log(agents_db[agent_id]["name"], "Auto-reconnect successful", "success")
                
                asyncio.create_task(reconnect(agent_id))

# Start monitor on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_agents())
    add_log("System", "API Server started", "success")
    logger.info("API Server started on http://localhost:8000")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
