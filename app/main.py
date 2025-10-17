from fastapi import FastAPI, UploadFile, File, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, json, shutil, asyncio
from app.evaluation import evaluate, load_ground_truth
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="OCR Evaluation Platform with Leaderboard")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = "data/uploads"
LEADERBOARD_PATH = "data/leaderboard.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# 用於異步執行評估任務的執行器
executor = ThreadPoolExecutor(max_workers=4)

# 儲存評估任務的結果
evaluation_results = {}

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


@app.post("/upload")
async def upload_file(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """只上傳檔案，不進行評估"""
    filename = f"{name}.json"
    save_path = os.path.join(UPLOAD_DIR, filename)

    # 檢查名稱是否已存在
    if os.path.exists(save_path):
        return {"success": False, "error": f"名稱「{name}」已存在排行榜，請換一個名稱。"}

    # 儲存上傳的檔案
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"success": True, "file_path": save_path}
    except Exception as e:
        return {"success": False, "error": f"檔案上傳失敗：{str(e)}"}


@app.post("/evaluate", response_class=HTMLResponse)
async def evaluate_file(
    request: Request,
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """上傳檔案並顯示評估結果（用於不支援 WebSocket 的備用方案）"""
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


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 端點用於推送評估進度"""
    await websocket.accept()
    
    try:
        # 從 websocket 接收評估請求
        data = await websocket.receive_json()
        name = data.get("name")
        file_path = data.get("file_path")
        
        if not name or not file_path:
            await websocket.send_json({
                "type": "error",
                "message": "缺少必要參數"
            })
            await websocket.close()
            return
        
        # 進度回調函數
        async def send_progress(current, total, key):
            percentage = int((current / total) * 100)
            await websocket.send_json({
                "type": "progress",
                "current": current,
                "total": total,
                "percentage": percentage,
                "current_key": key
            })
        
        # 在執行器中運行評估任務
        loop = asyncio.get_event_loop()
        
        def eval_with_progress():
            results = []
            def sync_progress(current, total, key):
                # 在同步函數中，我們需要將進度發送到異步上下文
                asyncio.run_coroutine_threadsafe(
                    send_progress(current, total, key),
                    loop
                )
            
            return evaluate(file_path, progress_callback=sync_progress)
        
        try:
            # 執行評估
            result = await loop.run_in_executor(executor, eval_with_progress)
            
            # 更新排行榜
            with open(LEADERBOARD_PATH, "r+", encoding="utf-8") as f:
                leaderboard_data = json.load(f)
                leaderboard_data.append({
                    "name": name,
                    "teds": result["TEDS"]
                })
                leaderboard_data = sorted(leaderboard_data, key=lambda x: x["teds"], reverse=True)
                f.seek(0)
                json.dump(leaderboard_data, f, ensure_ascii=False, indent=2)
                f.truncate()
            
            # 發送完成訊息
            await websocket.send_json({
                "type": "complete",
                "result": result,
                "name": name,
                "leaderboard": leaderboard_data
            })
            
        except ValueError as e:
            # 格式錯誤：刪除已上傳的檔案
            if os.path.exists(file_path):
                os.remove(file_path)
            await websocket.send_json({
                "type": "error",
                "message": f"❌ {str(e)}\n\n請檢查您的檔案格式後重新上傳。"
            })
        except Exception as e:
            # 其他錯誤
            if os.path.exists(file_path):
                os.remove(file_path)
            await websocket.send_json({
                "type": "error",
                "message": f"❌ 評估過程中發生錯誤：{str(e)}\n\n請聯絡管理員或檢查檔案格式。"
            })
    
    except WebSocketDisconnect:
        print(f"WebSocket 連接斷開: {session_id}")
    except Exception as e:
        print(f"WebSocket 錯誤: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
