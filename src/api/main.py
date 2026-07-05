from fastapi import FastAPI, WebSocket
import asyncio
import json
from datetime import datetime

from ..simulator.terminal_simulator import TerminalSimulator

app = FastAPI()
simulator = TerminalSimulator()

@app.get("/")
async def root():
    return {"message": "RailHub Digital Twin API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/twin")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to Digital Twin WebSocket")
    
    try:
        while True:
            simulator.step()
            current_state = simulator.get_state()
            
            # 封装数据，添加时间戳和类型
            data_to_send = {
                "type": "digital_twin_update",
                "timestamp": int(datetime.now().timestamp()),
                "entities": current_state
            }
            
            await websocket.send_text(json.dumps(data_to_send))
            await asyncio.sleep(0.1) # 每 0.1 秒推送一次数据，模拟更实时的数据流
            
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
