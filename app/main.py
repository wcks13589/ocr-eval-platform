from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, json, shutil
from app.evaluation import evaluate, load_ground_truth

app = FastAPI(title="OCR Evaluation Platform with Leaderboard")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = "data/uploads"
LEADERBOARD_PATH = "data/leaderboard.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    load_ground_truth()
    if not os.path.exists(LEADERBOARD_PATH):
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁：上傳介面 + 排行榜"""
    # 讀取排行榜數據
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        leaders = json.load(f)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "error": None,
        "leaders": leaders
    })


@app.post("/evaluate", response_class=HTMLResponse)
async def evaluate_file(
    request: Request,
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """上傳檔案並顯示評估結果"""
    filename = f"{name}.json"
    save_path = os.path.join(UPLOAD_DIR, filename)

    # 檢查名稱是否已存在
    if os.path.exists(save_path):
        # 讀取排行榜數據以顯示在錯誤頁面
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            leaders = json.load(f)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"名稱「{name}」已存在排行榜，請換一個名稱。",
            "leaders": leaders
        })

    # 儲存上傳的檔案
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 計算評分（加入錯誤處理）
    try:
        result = evaluate(save_path)
    except ValueError as e:
        # 格式錯誤：刪除已上傳的檔案，顯示錯誤訊息
        if os.path.exists(save_path):
            os.remove(save_path)
        
        # 讀取排行榜數據以顯示在錯誤頁面
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            leaders = json.load(f)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"❌ {str(e)}\n\n請檢查您的檔案格式後重新上傳。",
            "leaders": leaders
        })
    except Exception as e:
        # 其他錯誤
        if os.path.exists(save_path):
            os.remove(save_path)
        
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            leaders = json.load(f)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"❌ 評估過程中發生錯誤：{str(e)}\n\n請聯絡管理員或檢查檔案格式。",
            "leaders": leaders
        })

    # 更新排行榜（儲存所有指標）
    with open(LEADERBOARD_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append({
            "name": name, 
            "teds": result["TEDS"]
        })
        data = sorted(data, key=lambda x: x["teds"], reverse=True)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

    # 重新渲染首頁，顯示更新後的排行榜並高亮新上傳的記錄
    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": None,
        "leaders": data,
        "highlight_name": name,  # 標記要高亮的名稱
        "success_message": f"✅ 評估完成！{name} 的 TEDS 分數為 {result['TEDS']}"
    })


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    """顯示排行榜"""
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "leaders": data
    })
