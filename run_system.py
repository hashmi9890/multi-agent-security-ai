import subprocess, sys, signal, os

def run():
    print("="*60)
    print("STARTING MULTI-AGENT SECURITY AI SYSTEM")
    print("="*60)
    print("UI: http://localhost:8501")
    print("WA: http://localhost:5000")
    print("Run 'ngrok http 5000' for WhatsApp webhook")
    print("="*60)
    
    b = subprocess.Popen([sys.executable, "-m", "src.integrations.whatsapp_bridge"])
    u = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py"])
    
    def stop(s, f):
        print("\nSTOPPING...")
        b.terminate()
        u.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, stop)
    
    try:
        b.wait()
        u.wait()
    except KeyboardInterrupt:
        stop(None, None)

if __name__ == "__main__":
    run()
