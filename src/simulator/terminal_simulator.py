import time
import json
import random
from datetime import datetime

class Entity:
    def __init__(self, id, type, position=None, rotation=None, status="idle"):
        self.id = id
        self.type = type
        self.position = position if position is not None else {"x": 0.0, "y": 0.0, "z": 0.0}
        self.rotation = rotation if rotation is not None else {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        self.status = status
        self.speed = 0.0
        self.acceleration = 0.0

    def get_state(self):
        return {
            "id": self.id,
            "type": self.type,
            "position": self.position,
            "rotation": self.rotation,
            "status": self.status,
            "speed": self.speed,
            "acceleration": self.acceleration
        }

class Train(Entity):
    def __init__(self, id, track_length=1000.0, station_positions=None):
        super().__init__(id, "train", position={"x": 0.0, "y": 0.0, "z": 0.0}, rotation={"pitch": 0.0, "yaw": 90.0, "roll": 0.0})
        self.track_length = track_length
        self.station_positions = station_positions if station_positions is not None else [0.0, track_length / 2, track_length]
        self.current_station_idx = 0
        self.target_speed = 0.0
        self.max_speed = 50.0 # units per second
        self.max_acceleration = 5.0 # units per second^2
        self.cargo = []
        self.cargo_capacity = 5
        self.direction = 1 # 1 for forward, -1 for backward

    def update(self, delta_time):
        # Update acceleration based on target speed
        if self.speed < self.target_speed:
            self.acceleration = min(self.max_acceleration, (self.target_speed - self.speed) / delta_time if delta_time > 0 else self.max_acceleration)
        elif self.speed > self.target_speed:
            self.acceleration = max(-self.max_acceleration, (self.target_speed - self.speed) / delta_time if delta_time > 0 else -self.max_acceleration)
        else:
            self.acceleration = 0.0

        # Update speed
        self.speed += self.acceleration * delta_time
        self.speed = max(0.0, min(self.speed, self.max_speed))

        # Update position along the track (simplified to X-axis)
        self.position["x"] += self.speed * self.direction * delta_time

        # Handle track boundaries and station logic
        if self.direction == 1: # Moving forward
            if self.position["x"] >= self.track_length:
                self.position["x"] = self.track_length
                self.direction = -1 # Turn around
                self.target_speed = 0.0 # Stop at end
                self.status = "idle"
            elif self.current_station_idx < len(self.station_positions) - 1 and self.position["x"] >= self.station_positions[self.current_station_idx + 1]:
                self.position["x"] = self.station_positions[self.current_station_idx + 1]
                self.current_station_idx += 1
                self.target_speed = 0.0 # Stop at station
                self.status = "at_station"
                self._handle_cargo()
        else: # Moving backward
            if self.position["x"] <= 0.0:
                self.position["x"] = 0.0
                self.direction = 1 # Turn around
                self.target_speed = 0.0 # Stop at start
                self.status = "idle"
            elif self.current_station_idx > 0 and self.position["x"] <= self.station_positions[self.current_station_idx - 1]:
                self.position["x"] = self.station_positions[self.current_station_idx - 1]
                self.current_station_idx -= 1
                self.target_speed = 0.0 # Stop at station
                self.status = "at_station"
                self._handle_cargo()

        if self.status == "idle" and random.random() < 0.1: # Randomly start moving
            self.target_speed = self.max_speed
            self.status = "moving"
        elif self.status == "at_station" and random.random() < 0.5: # Randomly depart from station
            self.target_speed = self.max_speed
            self.status = "moving"

    def _handle_cargo(self):
        if self.status == "at_station":
            if random.random() < 0.5 and len(self.cargo) < self.cargo_capacity: # Load cargo
                cargo_item = f"cargo_{random.randint(100, 999)}"
                self.cargo.append(cargo_item)
                print(f"Train {self.id} loaded {cargo_item} at station {self.current_station_idx}")
            elif random.random() < 0.5 and len(self.cargo) > 0: # Unload cargo
                cargo_item = self.cargo.pop(0)
                print(f"Train {self.id} unloaded {cargo_item} at station {self.current_station_idx}")

    def get_state(self):
        base_state = super().get_state()
        base_state["track_length"] = self.track_length
        base_state["current_station_idx"] = self.current_station_idx
        base_state["target_speed"] = self.target_speed
        base_state["max_speed"] = self.max_speed
        base_state["max_acceleration"] = self.max_acceleration
        base_state["cargo"] = self.cargo
        base_state["cargo_count"] = len(self.cargo)
        base_state["direction"] = self.direction
        return base_state

class Crane(Entity):
    def __init__(self, id, position=None):
        super().__init__(id, "crane", position=position if position is not None else {"x": 100.0, "y": 50.0, "z": 15.0})
        self.current_container = None
        self.target_position = self.position.copy()
        self.move_speed = 5.0

    def update(self, delta_time):
        if self.status == "idle" and random.random() < 0.05:
            self.target_position = {
                "x": 100 + random.uniform(-10, 10),
                "y": 50 + random.uniform(-5, 5),
                "z": 15
            }
            self.status = "moving"

        if self.status == "moving":
            dx = self.target_position["x"] - self.position["x"]
            dy = self.target_position["y"] - self.position["y"]
            distance = (dx**2 + dy**2)**0.5

            if distance < self.move_speed * delta_time:
                self.position = self.target_position.copy()
                self.status = "idle"
            else:
                self.position["x"] += dx / distance * self.move_speed * delta_time
                self.position["y"] += dy / distance * self.move_speed * delta_time

class Truck(Entity):
    def __init__(self, id, position=None):
        super().__init__(id, "truck", position=position if position is not None else {"x": 20.0, "y": 80.0, "z": 0.0})
        self.target_position = self.position.copy()
        self.move_speed = 10.0

    def update(self, delta_time):
        if self.status == "idle" and random.random() < 0.05:
            self.target_position = {
                "x": 20 + random.uniform(-20, 20),
                "y": 80 + random.uniform(-10, 10),
                "z": 0
            }
            self.status = "driving"

        if self.status == "driving":
            dx = self.target_position["x"] - self.position["x"]
            dy = self.target_position["y"] - self.position["y"]
            distance = (dx**2 + dy**2)**0.5

            if distance < self.move_speed * delta_time:
                self.position = self.target_position.copy()
                self.status = "idle"
            else:
                self.position["x"] += dx / distance * self.move_speed * delta_time
                self.position["y"] += dy / distance * self.move_speed * delta_time

class TerminalSimulator:
    def __init__(self):
        self.entities = [
            Train("train_01", track_length=1000.0, station_positions=[0.0, 300.0, 700.0, 1000.0]),
            Crane("crane_01", position={"x": 100.0, "y": 50.0, "z": 15.0}),
            Crane("crane_02", position={"x": 200.0, "y": 50.0, "z": 15.0}),
            Truck("truck_01", position={"x": 20.0, "y": 80.0, "z": 0.0}),
            Truck("truck_02", position={"x": 50.0, "y": 90.0, "z": 0.0})
        ]
        self.last_update_time = time.time()

    def step(self):
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        for entity in self.entities:
            entity.update(delta_time)

    def get_state(self):
        state = []
        for entity in self.entities:
            state.append(entity.get_state())
        return state

if __name__ == "__main__":
    simulator = TerminalSimulator()
    print("Starting RailHub Digital Twin Simulator...")
    try:
        while True:
            simulator.step()
            state = simulator.get_state()
            print(json.dumps(state, indent=2))
            time.sleep(0.1) # Faster update for demonstration
    except KeyboardInterrupt:
        print("Simulator stopped.")
