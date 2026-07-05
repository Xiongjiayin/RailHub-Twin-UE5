import time
import json
import random

class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.rotation = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        self.status = "idle"

class Crane(Entity):
    def __init__(self, id):
        super().__init__(id, "crane")
        self.current_container = None

    def update(self):
        # 模拟龙门吊的随机移动和状态变化
        if self.status == "idle":
            if random.random() < 0.1:
                self.status = "moving"
        elif self.status == "moving":
            self.position["x"] += random.uniform(-1.0, 1.0)
            self.position["y"] += random.uniform(-1.0, 1.0)
            if random.random() < 0.05:
                self.status = "loading"
        elif self.status == "loading":
            if random.random() < 0.1:
                self.status = "idle"

class Truck(Entity):
    def __init__(self, id):
        super().__init__(id, "truck")

    def update(self):
        # 模拟集卡的随机移动
        self.position["x"] += random.uniform(-0.5, 0.5)
        self.position["y"] += random.uniform(-0.5, 0.5)

class TerminalSimulator:
    def __init__(self):
        self.entities = [
            Crane("crane_01"),
            Crane("crane_02"),
            Truck("truck_01"),
            Truck("truck_02"),
            Truck("truck_03")
        ]

    def step(self):
        for entity in self.entities:
            entity.update()

    def get_state(self):
        state = []
        for entity in self.entities:
            state.append({
                "id": entity.id,
                "type": entity.type,
                "position": entity.position,
                "rotation": entity.rotation,
                "status": entity.status
            })
        return state

if __name__ == "__main__":
    simulator = TerminalSimulator()
    print("Starting Terminal Simulator (Simulation only, no network output)...")
    try:
        while True:
            simulator.step()
            state = simulator.get_state()
            # print(json.dumps(state, indent=2)) # 注释掉以减少输出
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulator stopped.")
