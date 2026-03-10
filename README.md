# VCC Classifier Jock

VCC（Virtual Credit Card）刷卡適性分類工具。上傳企業費用項目 CSV，透過 Claude AI 判斷各項目是否適合使用虛擬信用卡，並可自動生成 Gamma 簡報。

## 功能

1. **VCC 適性分析** — 上傳 CSV，AI 判斷每筆費用項目為「可以 / 不行 / 不確定」
   - 分析模式採「多段批次」執行，支援進度輪詢與快取紀錄下載
2. **費用分類** — 將 VCC 可行項目分為：高頻次、固定支出、高單價、其他
3. **簡報生成** — 呼叫 Gamma API 自動產生客戶提案簡報（PPTX）
4. **雙模式上傳** —
   - 分析模式：上傳未標註 CSV，先做 VCC 判斷
   - PPT模式：上傳已標註 CSV（含 `VCC判斷`），直接進入簡報流程

## Tech Stack

- Python 3.12 / FastAPI / uvicorn
- Anthropic Claude API（分類與簡報文案）
- Gamma API（簡報生成）
- Docker / GCP Cloud Run

## 快速開始

```bash
# 安裝依賴
uv sync

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入 API keys

# 啟動開發伺服器
uv run uvicorn app.main:app --reload --port 8080
```

開啟 http://localhost:8080 使用 Web UI。

## 地端啟動（不影響雲端部署）

```bash
cp .env.local.example .env.local
# 編輯 .env.local 填入本機用 key
./run_local.sh
```

說明：
- `run_local.sh` 只會讀 `.env.local`
- `deploy.sh` 仍只讀 `.env`（Cloud Run 佈署設定不變）
- `.env.local` 已加入 `.gitignore`，不會混入版本控制

## CSV 格式

上傳的 CSV 必須包含以下欄位：

| 欄位 | 說明 |
|------|------|
| `費用項目名稱` | 費用項目名稱 |
| `金額累計` | 該項目的累計金額 |
| `交易筆數` | 交易總筆數 |
| `交易日期起` | 最早交易日期 |
| `交易日期迄` | 最晚交易日期 |

PPT模式（上傳已標註檔）另外需要：

| 欄位 | 說明 |
|------|------|
| `VCC判斷` | 已判斷結果（可以/不行/不確定） |

## API

| Method | Path | 說明 |
|--------|------|------|
| `GET` | `/` | Web UI |
| `GET` | `/health` | 健康檢查 |
| `POST` | `/api/analyze` | 上傳 CSV 建立分析任務（回傳 `job_id`） |
| `GET` | `/api/analyze-jobs/{job_id}` | 查詢多段分析進度與結果 |
| `GET` | `/api/analyze-jobs/{job_id}/cache` | 下載任務快取紀錄 JSON |
| `POST` | `/api/prepare-presentation-csv` | 上傳已標註 CSV，準備簡報資料 |
| `GET` | `/api/download/{filename}` | 下載分析結果 CSV |
| `POST` | `/api/generate-presentation` | 生成 Gamma 簡報 |
| `GET` | `/api/gamma-status/{generation_id}` | 查詢簡報生成狀態 |

## 部署

```bash
# 確保 .env 中已設定 GCP 相關變數
./deploy.sh
```

部署至 GCP Cloud Run（asia-east1）。需要在 `.env` 中設定 `GCP_PROJECT_ID`、`ARTIFACT_PROJECT_ID`、`ARTIFACT_REPO`。
