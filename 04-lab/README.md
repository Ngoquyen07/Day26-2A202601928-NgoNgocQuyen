# Lab 04 — Weather Agent with Authenticated MCP Server

## Bài nộp: Weather Decision MCP

**Use case:** thay vì mở trang thời tiết và tự tổng hợp nhiệt độ, mưa, độ ẩm trước khi di chuyển hoặc chọn trang phục, người dùng hỏi AI bằng ngôn ngữ tự nhiên. Server gọi WeatherAPI thật; không dùng dữ liệu thời tiết hard-code.

| Tool | Input | Output |
|---|---|---|
| `get_current_weather` (v1) | `city` | Chuỗi thời tiết cũ cho client legacy |
| `get_current_weather_v2` | `city` | JSON có nhiệt độ, cảm giác, gió, độ ẩm và thời điểm cập nhật |
| `get_forecast` | `city`, `days` (1–3) | Dự báo nhiều ngày |
| `health_check` | Không có | Trạng thái server |

Server chạy bằng Streamable HTTP tại `/mcp`, bắt buộc header `Authorization: Bearer <MCP_AUTH_TOKEN>`. `server://info` công bố version 2, tool v1 bị deprecated và hướng dẫn chuyển sang v2.

### Chạy và kiểm tra trên Windows PowerShell

Tạo `.env` tại thư mục gốc (không commit):

```env
WEATHERAPI_KEY=...
GOOGLE_API_KEY=...
MCP_AUTH_TOKEN=...  # tùy chọn; mặc định dev-token-abc123
```

Terminal 1:

```powershell
cd 04-lab\mcp-server
uv sync
$env:PYTHONUTF8 = "1"
$env:PORT = "8085"
uv run --env-file "D:/path/to/Day26-MCP-Tools-Integration/.env" python weather.py
```

Terminal 2 — kiểm tra cả auth, client cũ và client v2:

```powershell
cd 04-lab\mcp-client
uv sync
$env:PYTHONUTF8 = "1"
uv run python verify_submission.py
```

Kết quả mong đợi: token đúng gọi được tool; token thiếu/sai bị từ chối; client cũ gọi `get_current_weather`; client mới đọc `server://info` rồi gọi `get_current_weather_v2`.

### Claude Code

Khi server đang chạy, đăng ký HTTP MCP server với token từ PowerShell:

```powershell
claude mcp add --transport http weather-decision http://localhost:8085/mcp --header "Authorization: Bearer $env:MCP_AUTH_TOKEN"
claude mcp get weather-decision
```

Trong Claude Code, hỏi: `Thời tiết hiện tại ở Hà Nội thế nào?` hoặc `Dự báo 3 ngày ở Đà Nẵng.` Claude Code phải tự chọn tool thay vì nhận tên tool trực tiếp.

Không commit `.env`, API key hay token.

A weather agent built with Google ADK that connects to an MCP server via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐   Streamable HTTP    ┌─────────────────┐      REST       ┌─────────────────┐
│   ADK Agent     │ ──────────────────── │   MCP Server    │ ─────────────── │  WeatherAPI.com │
│  (mcp-client)   │   localhost:8085/mcp │  (mcp-server)   │                 │                 │
└─────────────────┘                      └─────────────────┘                 └─────────────────┘
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Get current weather conditions for a city |
| `get_forecast(city, days)` | Get weather forecast (1–3 days) |
| `health_check()` | Verify server is running |

## ADK làm gì trong Lab này?

ADK (Agent Development Kit) đóng vai trò **MCP Client** 
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. KẾT NỐI tới MCP Server qua Streamable HTTP                  │
│     StreamableHTTPConnectionParams(url="localhost:8085/mcp")    │
│                                                                 │
│  2. KHÁM PHÁ tools tự động (list_tools)                         │
│     McpToolset → tự hỏi server "anh có tool gì?"                │
│     → nhận về: get_current_weather, get_forecast, health_check  │
│                                                                 │
│  3. TRUYỀN tools cho LLM (Gemini)                               │
│     Agent(model="gemini-3.6-flash", tools=[weather_tools])      │
│     → Gemini biết nó có thể gọi 3 tools trên                    │
│                                                                 │
│  4. ĐIỀU PHỐI vòng lặp Function Calling                         │
│     User hỏi → Gemini chọn tool → ADK gọi MCP Server            │
│     → nhận kết quả → đưa lại cho Gemini tổng hợp                │
│                                                                 │
│  5. CUNG CẤP giao diện web (adk web)                            │
│     → http://localhost:8000 để chat với agent                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So với bài 02 (viết client thủ công bằng `mcp.ClientSession`), ADK giúp bạn **không phải viết vòng lặp function calling thủ công** nữa. Toàn bộ luồng list_tools → model quyết định → call_tool → model tổng hợp được ADK xử lý tự động.

## Setup

### 1. MCP Server

```bash
cd mcp-server
uv sync

# Set your WeatherAPI key (get one free at https://weatherapi.com)
$env:WEATHERAPI_KEY="your_weatherapi_key"

# Start the server (runs on port 8085 by default)
uv run python weather.py
```

The server will be available at `http://localhost:8085/mcp`.

### 2. ADK Agent (Client)

```bash
cd mcp-client
uv sync

# Create .env file with your Gemini API key
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env

# Start ADK web interface
uv run adk web
```

Open http://localhost:8000 in your browser, select `weather_agent`, and ask about the weather.

## Configuration

| Variable | Where | Description |
|----------|-------|-------------|
| `WEATHERAPI_KEY` | mcp-server | API key from weatherapi.com |
| `GOOGLE_API_KEY` | mcp-client/.env | Gemini API key |
| `PORT` | mcp-server (env) | Override server port (default: 8085) |
