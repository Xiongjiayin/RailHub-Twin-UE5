import os
import json
from openai import OpenAI

class LLMAgent:
    def __init__(self, model_name="gpt-4o-mini", api_base=None, api_key=None):
        self.model_name = model_name
        self.api_base = api_base if api_base else os.getenv("OPENAI_API_BASE")
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        if not self.api_base:
            raise ValueError("OPENAI_API_BASE environment variable not set.")

        self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)

    def _call_llm(self, system_prompt, user_prompt, json_mode=False):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            if json_mode:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
            
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                print(f"LLM response content is empty: {response}")
                return None
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None

class DispatcherAgent(LLMAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_prompt = (
            "You are an AI dispatcher for a rail container terminal. "
            "Your task is to translate natural language commands into structured JSON dispatch instructions. "
            "The available entities are 'train', 'crane', 'truck'. "
            "Available actions for 'train': 'set_target_speed', 'move_to_station'. "
            "Available actions for 'crane': 'move_to', 'load_container', 'unload_container'. "
            "Available actions for 'truck': 'move_to', 'load_container', 'unload_container'. "
            "Always output a JSON object with 'entity_id', 'action', and 'parameters'. "
            "Example: {'entity_id': 'train_01', 'action': 'set_target_speed', 'parameters': {'speed': 50.0}}"
        )

    def generate_dispatch_instruction(self, natural_language_command, current_terminal_state):
        user_prompt = (
            f"Natural language command: {natural_language_command}\n"
            f"Current terminal state (simplified): {json.dumps(current_terminal_state)}\n"
            "Generate a JSON dispatch instruction based on the command and current state."
        )
        return self._call_llm(self.system_prompt, user_prompt, json_mode=True)

class ReportingAgent(LLMAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_prompt = (
            "You are an AI reporting agent for a rail container terminal. "
            "Your task is to summarize complex operational data into concise, human-readable reports. "
            "Focus on key events, anomalies, and overall operational status."
        )

    def generate_summary_report(self, operational_data):
        user_prompt = (
            f"Operational data: {json.dumps(operational_data)}\n"
            "Generate a concise summary report of the terminal's operational status, highlighting any anomalies."
        )
        return self._call_llm(self.system_prompt, user_prompt)

class AnomalyDetectionAgent(LLMAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_prompt = (
            "You are an AI anomaly detection and diagnostic agent for a rail container terminal. "
            "Your task is to analyze sensor data and operational events to identify anomalies and suggest potential causes or maintenance actions. "
            "Output a JSON object with 'anomaly_detected': true/false, 'description': '...', 'suggested_action': '...'."
        )

    def analyze_anomaly(self, sensor_data, operational_events):
        user_prompt = (
            f"Sensor data: {json.dumps(sensor_data)}\n"
            f"Operational events: {json.dumps(operational_events)}\n"
            "Analyze the data for anomalies and provide a description and suggested action in JSON format."
        )
        return self._call_llm(self.system_prompt, user_prompt, json_mode=True)

if __name__ == "__main__":
    # Example Usage (requires OPENAI_API_BASE and OPENAI_API_KEY to be set in environment)
    # For testing, ensure you have a valid API key and base URL configured.
    # export OPENAI_API_BASE="https://api.siliconflow.cn/v1"
    # export OPENAI_API_KEY="sk-YOUR_SILICONFLOW_API_KEY"

    try:
        dispatcher = DispatcherAgent(model_name="deepseek-ai/DeepSeek-V3")
        reporting = ReportingAgent(model_name="deepseek-ai/DeepSeek-V3")
        anomaly_detector = AnomalyDetectionAgent(model_name="deepseek-ai/DeepSeek-V3")

        # Test Dispatcher
        print("\n--- Testing Dispatcher Agent ---")
        command = "让 train_01 以 40 公里/小时的速度行驶"
        current_state = {"train_01": {"status": "idle", "position": {"x": 0}}}
        dispatch_instruction = dispatcher.generate_dispatch_instruction(command, current_state)
        print(f"Dispatch Instruction: {dispatch_instruction}")

        # Test Reporting
        print("\n--- Testing Reporting Agent ---")
        op_data = {
            "throughput": {"today": 5200, "yesterday": 5124},
            "alerts": [{"type": "high_wind", "crane_id": "crane_01"}],
            "train_status": {"train_01": "moving", "train_02": "at_station"}
        }
        summary_report = reporting.generate_summary_report(op_data)
        print(f"Summary Report: {summary_report}")

        # Test Anomaly Detection
        print("\n--- Testing Anomaly Detection Agent ---")
        sensor_data = {"crane_01_vibration": [0.1, 0.2, 0.8, 0.2, 0.1], "crane_01_load": 35.5}
        events = [{"type": "crane_overload", "crane_id": "crane_01"}]
        anomaly_report = anomaly_detector.analyze_anomaly(sensor_data, events)
        print(f"Anomaly Report: {anomaly_report}")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
