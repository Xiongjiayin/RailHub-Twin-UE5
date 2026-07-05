from fastapi import FastAPI, WebSocket
import asyncio
import json
import random
from datetime import datetime

# 导入模拟器（在实际项目中，这可能是一个独立运行的进程）
# 这里为了演示，我们直接在 FastAPI 中模拟数据推送
# from ..simulator.terminal_simulator import TerminalSimulator

app = FastAPI()

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
            # 模拟从模拟器获取数据
            mock_data = {
                "type": "entity_update",
                "timestamp": int(datetime.now().timestamp()),
                "entities": [
                    {
                        "id": "crane_01",
                        "type": "crane",
                        "position": {"x": 100 + random.uniform(-1, 1), "y": 50 + random.uniform(-1, 1), "z": 15},
                        "status": "operating"
                    },
                    {
                        "id": "truck_01",
                        "type": "truck",
                        "position": {"x": 20 + random.uniform(-0.5, 0.5), "y": 80 + random.uniform(-0.5, 0.5), "z": 0},
                        "status": "driving"
                    }
                ]
            }
            
            await websocket.send_text(json.dumps(mock_data))
            await asyncio.sleep(0.5) # 每 0.5 秒推送一次数据
            
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
