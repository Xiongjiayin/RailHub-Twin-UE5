# Unreal Engine 5 (UE5) 集成指南

本指南将详细介绍如何将铁路集装箱中心站数字孪生系统的后端数据（通过 Python API/WebSocket 提供）集成到 Unreal Engine 5 (UE5) 中，实现实时可视化和交互。我们将提供具体的 C++ 和蓝图代码示例，以确保集成的真实性和功能性。

## 1. UE5 项目设置

1.  **创建新项目**: 在 Unreal Engine 启动器中，创建一个新的 `Blank` 或 `Third Person` 模板项目。选择 `C++` 项目类型，命名为 `RailHubTwinUE5`。
2.  **启用插件**: 确保以下插件已启用（`Edit -> Plugins`）：
    *   `WebSocket` (用于 WebSocket 连接)
    *   `JsonUtilities` (用于 JSON 数据解析)
    *   `HTTP` (用于 RESTful API 调用，如果需要)

## 2. WebSocket 客户端实现 (实时数据推送)

WebSocket 是实现实时数据流的关键。我们将创建一个 C++ 类来管理 WebSocket 连接和数据接收，并将其暴露给蓝图使用。

### 2.1 创建 C++ WebSocket 客户端类

在 `RailHubTwinUE5` 项目中，通过 `File -> New C++ Class...` 创建一个新的 C++ 类，选择 `ActorComponent` 作为父类，命名为 `RailTwinWebSocketClient`。

**RailTwinWebSocketClient.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IWebSocket.h"
#include "RailTwinWebSocketClient.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDigitalTwinDataReceived, const FString&, Data);

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class RAILHUBTWINUE5_API URailTwinWebSocketClient : public UActorComponent
{
	GENERATED_BODY()

public:	
	URailTwinWebSocketClient();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WebSocket")
	FString WebSocketURL = TEXT("ws://127.0.0.1:8000/ws/twin");

	UPROPERTY(BlueprintAssignable, Category = "WebSocket")
	FOnDigitalTwinDataReceived OnDigitalTwinDataReceived;

	UFUNCTION(BlueprintCallable, Category = "WebSocket")
	virtual void ConnectToWebSocket();

	UFUNCTION(BlueprintCallable, Category = "WebSocket")
	virtual void DisconnectFromWebSocket();

private:
	TSharedPtr<IWebSocket> WebSocket;

	void OnConnected();
	void OnConnectionError(const FString& Error);
	void OnClosed(int32 StatusCode, const FString& Reason, bool bWasClean);
	void OnMessage(const FString& Message);
};

```

**RailTwinWebSocketClient.cpp**

```cpp
#include "RailTwinWebSocketClient.h"
#include "WebSocketsModule.h"
#include "IWebSocket.h"
#include "Json.h"
#include "JsonUtilities.h"

URailTwinWebSocketClient::URailTwinWebSocketClient()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void URailTwinWebSocketClient::BeginPlay()
{
	Super::BeginPlay();
	ConnectToWebSocket();
}

void URailTwinWebSocketClient::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	DisconnectFromWebSocket();
	Super::EndPlay(EndPlayReason);
}

void URailTwinWebSocketClient::ConnectToWebSocket()
{
	if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
	{
		FModuleManager::Get().LoadModule("WebSockets");
	}

	WebSocket = FWebSocketsModule::Get().CreateWebSocket(WebSocketURL);

	if (WebSocket.IsValid())
	{
		WebSocket->OnConnected().AddUObject(this, &URailTwinWebSocketClient::OnConnected);
		WebSocket->OnConnectionError().AddUObject(this, &URailTwinWebSocketClient::OnConnectionError);
		WebSocket->OnClosed().AddUObject(this, &URailTwinWebSocketClient::OnClosed);
		WebSocket->OnMessage().AddUObject(this, &URailTwinWebSocketClient::OnMessage);

		WebSocket->Connect();
	}
}

void URailTwinWebSocketClient::DisconnectFromWebSocket()
{
	if (WebSocket.IsValid() && WebSocket->IsConnected())
	{
		WebSocket->Close();
	}
}

void URailTwinWebSocketClient::OnConnected()
{
	UE_LOG(LogTemp, Warning, TEXT("WebSocket Connected to: %s"), *WebSocketURL);
}

void URailTwinWebSocketClient::OnConnectionError(const FString& Error)
{
	UE_LOG(LogTemp, Error, TEXT("WebSocket Connection Error: %s"), *Error);
}

void URailTwinWebSocketClient::OnClosed(int32 StatusCode, const FString& Reason, bool bWasClean)
{
	UE_LOG(LogTemp, Warning, TEXT("WebSocket Closed. Status Code: %d, Reason: %s, Was Clean: %d"), StatusCode, *Reason, bWasClean);
}

void URailTwinWebSocketClient::OnMessage(const FString& Message)
{
	// UE_LOG(LogTemp, Log, TEXT("WebSocket Message: %s"), *Message);
	OnDigitalTwinDataReceived.Broadcast(Message);
}

```

### 2.2 蓝图集成与数据解析

1.  **创建 Actor**: 创建一个名为 `BP_DigitalTwinManager` 的蓝图 Actor，并添加 `RailTwinWebSocketClient` 组件。
2.  **绑定事件**: 在 `BP_DigitalTwinManager` 的 `Event Graph` 中，选择 `RailTwinWebSocketClient` 组件，并绑定 `On Digital Twin Data Received` 事件。
3.  **解析 JSON 数据**: 在 `On Digital Twin Data Received` 事件中，使用 `JSON Utilities` 插件提供的节点来解析接收到的 JSON 字符串。

**蓝图示例 (BP_DigitalTwinManager Event Graph)**

```mermaid
graph TD
    A[Event BeginPlay] --> B{Add RailTwinWebSocketClient Component};
    B --> C{Call ConnectToWebSocket on Component};
    C --> D{Bind OnDigitalTwinDataReceived Event};
    D --> E[On Digital Twin Data Received (Data: FString)];
    E --> F{Parse JSON String (Data) to JSON Object};
    F --> G{Get Array Field (JSON Object, "entities")};
    G --> H{For Each Loop (Array of JSON Objects)};
    H --> I{Get String Field (Current JSON Object, "id") -> EntityID};
    H --> J{Get String Field (Current JSON Object, "type") -> EntityType};
    H --> K{Get Object Field (Current JSON Object, "position") -> PositionObject};
    K --> L{Get Float Field (PositionObject, "x") -> PosX};
    K --> M{Get Float Field (PositionObject, "y") -> PosY};
    K --> N{Get Float Field (PositionObject, "z") -> PosZ};
    L & M & N --> O{Make Vector (PosX, PosY, PosZ) -> NewLocation};
    O --> P{Find Actor by ID (EntityID) or Type (EntityType)};
    P --> Q{Set Actor Location (Found Actor, NewLocation)};
    Q --> R{Continue Loop};
```

**JSON 数据结构示例 (来自 Python API)**

```json
{
  "type": "digital_twin_update",
  "timestamp": 1678886400,
  "entities": [
    {
      "id": "train_01",
      "type": "train",
      "position": {"x": 150.0, "y": 0.0, "z": 0.0},
      "rotation": {"pitch": 0.0, "yaw": 90.0, "roll": 0.0},
      "status": "moving",
      "speed": 25.0,
      "acceleration": 2.5,
      "track_length": 1000.0,
      "current_station_idx": 0,
      "target_speed": 50.0,
      "max_speed": 50.0,
      "max_acceleration": 5.0,
      "cargo": ["cargo_123", "cargo_456"],
      "cargo_count": 2,
      "direction": 1
    },
    {
      "id": "crane_01",
      "type": "crane",
      "position": {"x": 105.0, "y": 51.0, "z": 15.0},
      "rotation": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
      "status": "moving",
      "speed": 0.0,
      "acceleration": 0.0
    }
  ]
}
```

### 2.3 实体查找与更新逻辑

在蓝图中，您需要实现一个机制来根据 `EntityID` 或 `EntityType` 找到场景中对应的 Actor。一种常见的方法是在 Actor 生成时，将其引用存储在一个 `Map<FString, AActor*>` 中，其中 Key 是 `EntityID`。当接收到数据时，通过 `EntityID` 从 Map 中查找 Actor，然后更新其位置、旋转和状态。

## 3. RESTful API 接口调用 (指令与查询)

UE5 可以通过 HTTP 请求与 RESTful API 进行交互，用于发送指令或查询非实时数据。这部分与之前的指南保持一致，主要使用 `HTTP` 插件。

### 3.1 发送 HTTP 请求 (蓝图)

1.  在需要发送请求的蓝图事件中，添加 `Construct Object From Class` 节点，选择 `HTTP Request`。
2.  设置 `Verb` (GET/POST)、`URL` (例如 `http://127.0.0.1:8000/health`) 和 `Content Type`。
3.  对于 POST 请求，使用 `Set Request Content String` 或 `Set Request Content Bytes` 节点设置 JSON 请求体。
4.  调用 `Process Request` 节点发送请求。
5.  绑定 `On Request Complete` 和 `On Request Fail` 事件来处理响应。

### 3.2 处理 HTTP 响应 (蓝图)

1.  在 `On Request Complete` 事件中，`Response Content` 参数将包含服务器返回的 JSON 字符串。
2.  同样使用 `JSON Deserialize` 节点解析 JSON 响应，并根据业务逻辑进行处理。

## 4. 场景构建与资产准备

*   **3D 模型**: 准备铁路、集装箱、龙门吊、集卡、列车、建筑等 3D 模型资产。
*   **材质与纹理**: 为模型创建逼真的材质和纹理。
*   **物理模拟**: 为需要物理交互的实体设置碰撞体和物理属性。
*   **动画**: 为龙门吊、集卡、列车等运动实体创建动画，并通过数据驱动进行播放。例如，列车可以根据 `speed` 和 `direction` 播放不同的行驶动画。

通过以上详细的 C++ 和蓝图代码示例，您可以在 UE5 中构建一个功能完善且数据驱动的铁路集装箱中心站数字孪生可视化应用，实现与后端模拟器的实时数据交互。
