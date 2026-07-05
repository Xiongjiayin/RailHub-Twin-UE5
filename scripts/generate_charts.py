import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
import os

# Ensure the assets directory exists
os.makedirs('/home/ubuntu/RailHub-Twin-UE5/docs/assets', exist_ok=True)

# Set the style
sns.set_theme(style="darkgrid")
plt.rcParams['figure.facecolor'] = '#0b0f19'
plt.rcParams['axes.facecolor'] = '#0b0f19'
plt.rcParams['axes.labelcolor'] = '#ffffff'
plt.rcParams['xtick.color'] = '#ffffff'
plt.rcParams['ytick.color'] = '#ffffff'
plt.rcParams['text.color'] = '#ffffff'
plt.rcParams['grid.color'] = '#1e293b'

def generate_throughput_chart():
    # Simulate daily throughput data
    days = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
    days_str = [d.strftime('%m-%d') for d in days]
    throughput = [5120, 5340, 4890, 5600, 5124, 4789, 5200]
    
    plt.figure(figsize=(10, 6))
    plt.plot(days_str, throughput, marker='o', color='#38bdf8', linewidth=3, markersize=8)
    plt.fill_between(days_str, throughput, color='#38bdf8', alpha=0.1)
    plt.title('Weekly Container Throughput (TEU)', fontsize=16, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('TEU', fontsize=12)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/RailHub-Twin-UE5/docs/assets/throughput_chart.png')
    plt.close()

def generate_asset_utilization_chart():
    # Simulate asset utilization
    assets = ['Crane 01', 'Crane 02', 'Crane 03', 'Truck 01', 'Truck 02', 'Train 01']
    utilization = [85, 78, 92, 65, 70, 95]
    
    plt.figure(figsize=(10, 6))
    colors = ['#0ea5e9', '#0ea5e9', '#0ea5e9', '#fbbf24', '#fbbf24', '#f43f5e']
    bars = plt.bar(assets, utilization, color=colors, alpha=0.8)
    
    # Add percentage labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval}%', ha='center', va='bottom', color='white')
        
    plt.title('Asset Utilization Rate (%)', fontsize=16, pad=20)
    plt.ylim(0, 110)
    plt.ylabel('Utilization (%)', fontsize=12)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/RailHub-Twin-UE5/docs/assets/utilization_chart.png')
    plt.close()

def generate_sensor_data_stream():
    # Simulate real-time sensor data (e.g., vibration or load)
    time = np.linspace(0, 10, 100)
    data = np.sin(time) * 10 + 20 + np.random.normal(0, 1, 100)
    
    plt.figure(figsize=(10, 4))
    plt.plot(time, data, color='#10b981', linewidth=2)
    plt.title('Real-time Crane Load Sensor Data (t)', fontsize=14)
    plt.xlabel('Time (s)', fontsize=10)
    plt.ylabel('Load (t)', fontsize=10)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/RailHub-Twin-UE5/docs/assets/sensor_chart.png')
    plt.close()

if __name__ == "__main__":
    generate_throughput_chart()
    generate_asset_utilization_chart()
    generate_sensor_data_stream()
    print("Charts generated successfully in /home/ubuntu/RailHub-Twin-UE5/docs/assets/")
