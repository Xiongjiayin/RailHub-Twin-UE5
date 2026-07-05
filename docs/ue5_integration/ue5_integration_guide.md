# Unreal Engine 5 (UE5) 集成指南

本指南将详细介绍如何将铁路集装箱中心站数字孪生系统的后端数据（通过 Python API/WebSocket 提供）集成到 Unreal Engine 5 (UE5) 中，实现实时可视化和交互。

## 1. UE5 项目设置

1.  **创建新项目**: 在 Unreal Engine 启动器中，创建一个新的 `Blank` 或 `Third Person` 模板项目。选择 `Blueprint` 或 `C++` 项目类型，建议选择 `C++` 项目以获得更好的性能和灵活性，但本指南将主要关注蓝图实现，并提及 C++ 的作用。
2.  **启用插件**: 确保以下插件已启用（`Edit -> Plugins`）：
    *   `WebSocket` (用于 WebSocket 连接)
    *   `HTTP` (用于 RESTful API 调用)
    *   `JSON` (用于 JSON 数据解析)

## 2. WebSocket 客户端实现 (实时数据推送)

WebSocket 是实现实时数据流的关键。我们将创建一个蓝图类来管理 WebSocket 连接和数据接收。

### 2.1 创建 WebSocket 客户端蓝图

1.  在内容浏览器中，右键点击 `Blueprint Class`，选择 `Actor` 作为父类，命名为 `BP_WebSocketClient`。
2.  打开 `BP_WebSocketClient` 蓝图，进入 `Event Graph`。

### 2.2 连接到 WebSocket 服务器

1.  在 `Event BeginPlay` 事件后，添加 `Create WebSocket` 节点。
    *   `URL`: 输入您的 WebSocket 服务器地址，例如 `ws://localhost:8000/ws/twin`。
    *   `Protocol`: 留空或根据需要设置。
2.  将 `Create WebSocket` 的返回值提升为变量，命名为 `WebSocket`。
3.  从 `WebSocket` 变量拖出，调用 `Connect` 节点。
4.  从 `WebSocket` 变量拖出，绑定 `On Connected`、`On Connection Error`、`On Closed` 和 `On Message` 事件。

### 2.3 处理接收到的数据

1.  在 `On Message` 事件中，`Message` 参数将包含从 Python 后端发送的 JSON 字符串。
2.  使用 `JSON Deserialize` 节点将 JSON 字符串解析为 `JSON Object`。
3.  从 `JSON Object` 中，可以通过 `Get String Field`、`Get Number Field` 等节点提取 `type`、`entity_id`、`position`、`status` 等数据。
4.  **实体查找与更新**: 
    *   根据 `entity_id` 查找场景中对应的 Actor (例如，龙门吊 Actor、集卡 Actor)。您可以使用 `Get All Actors Of Class` 或在 Actor 生成时将其存储在一个 Map 中。
    *   一旦找到对应的 Actor，根据接收到的 `position`、`rotation` 和 `status` 数据更新其位置 (`Set Actor Location`)、旋转 (`Set Actor Rotation`) 和状态（例如，播放不同的动画或改变材质）。

## 3. RESTful API 接口调用 (指令与查询)

UE5 可以通过 HTTP 请求与 RESTful API 进行交互，用于发送指令或查询非实时数据。

### 3.1 发送 HTTP 请求

1.  在需要发送请求的蓝图事件中，添加 `Construct Object From Class` 节点，选择 `HTTP Request`。
2.  设置 `Verb` (GET/POST)、`URL` (例如 `http://localhost:8000/dispatch/crane`) 和 `Content Type`。
3.  对于 POST 请求，使用 `Set Request Content String` 或 `Set Request Content Bytes` 节点设置 JSON 请求体。
4.  调用 `Process Request` 节点发送请求。
5.  绑定 `On Request Complete` 和 `On Request Fail` 事件来处理响应。

### 3.2 处理 HTTP 响应

1.  在 `On Request Complete` 事件中，`Response Content` 参数将包含服务器返回的 JSON 字符串。
2.  同样使用 `JSON Deserialize` 节点解析 JSON 响应，并根据业务逻辑进行处理。

## 4. 蓝图与 C++ 结合

*   **蓝图**: 适合快速原型开发、UI 逻辑、简单的事件处理和数据绑定。
*   **C++**: 适合高性能计算、复杂的物理模拟、自定义数据结构、底层网络通信优化以及作为蓝图的基类提供更强大的功能。

例如，您可以创建一个 C++ 类来封装 WebSocket 客户端的复杂逻辑，然后将其暴露给蓝图，以便在蓝图中方便地使用。

## 5. 场景构建与资产准备

*   **3D 模型**: 准备铁路、集装箱、龙门吊、集卡、建筑等 3D 模型资产。
*   **材质与纹理**: 为模型创建逼真的材质和纹理。
*   **物理模拟**: 为需要物理交互的实体设置碰撞体和物理属性。
*   **动画**: 为龙门吊、集卡等运动实体创建动画，并通过数据驱动进行播放。

## 6. 示例蓝图片段 (伪代码)

```mermaid
graph TD
    A[Event BeginPlay] --> B{Create WebSocket};
    B --> C{Set WebSocket URL: ws://localhost:8000/ws/twin};
    C --> D{Connect WebSocket};
    D --> E{On WebSocket Connected: Print "Connected!"};
    D --> F{On WebSocket Message: Process JSON Message};
    F --> G{JSON Deserialize};
    G --> H{Get String Field: "entity_id"};
    H --> I{Find Actor by ID};
    I --> J{Get Object Field: "position"};
    J --> K{Get Vector Field: "x","y","z"};
    K --> L{Set Actor Location};
```

通过以上步骤，您可以在 UE5 中构建一个功能完善的铁路集装箱中心站数字孪生可视化应用，实现与后端模拟器的实时数据交互。
