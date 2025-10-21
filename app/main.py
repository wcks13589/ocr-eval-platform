from fastapi import FastAPI, UploadFile, File, Form, Request, WebSocket, WebSocketDisconnect, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, json, shutil, asyncio, secrets
from app.evaluation import evaluate, load_ground_truth
from app.i18n import get_all_translations
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="OCR Evaluation Platform with Leaderboard")

# 管理員密碼（建議使用環境變數）
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
# 存儲活躍的管理員 session tokens
admin_sessions = set()

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = "data/uploads"
LEADERBOARD_PATH = "data/leaderboard.json"
DETAILS_DIR = "data/details"  # 儲存每個參賽者的詳細分數

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DETAILS_DIR, exist_ok=True)

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


def get_language(request: Request) -> str:
    """從 cookie 中獲取語言設置，默認為英文"""
    return request.cookies.get("lang", "en")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁：上傳介面 + 排行榜"""
    lang = get_language(request)
    # 讀取排行榜數據
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        leaders = json.load(f)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "error": None,
        "leaders": leaders,
        "lang": lang,
        "t": get_all_translations(lang)
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
    lang = get_language(request)
    t = get_all_translations(lang)
    filename = f"{name}.json"
    save_path = os.path.join(UPLOAD_DIR, filename)

    # 檢查名稱是否已存在
    if os.path.exists(save_path):
        # 讀取排行榜數據以顯示在錯誤頁面
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            leaders = json.load(f)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": t["name_exists"].format(name=name),
            "leaders": leaders,
            "lang": lang,
            "t": t
        })

    # 儲存上傳的檔案
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 計算評分（加入錯誤處理）
    try:
        result = evaluate(save_path)
        
        # 儲存詳細分數
        detail_path = os.path.join(DETAILS_DIR, f"{name}.json")
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump({
                "name": name,
                "teds": result["TEDS"],
                "details": result["details"],
                "valid_count": result["valid_count"],
                "total_count": result["total_count"]
            }, f, ensure_ascii=False, indent=2)
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
            "leaders": leaders,
            "lang": lang,
            "t": t
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
            "leaders": leaders,
            "lang": lang,
            "t": t
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
        "success_message": t["score_result"].format(name=name, score=result['TEDS']),
        "lang": lang,
        "t": t
    })


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    """顯示排行榜"""
    lang = get_language(request)
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "leaders": data,
        "lang": lang,
        "t": get_all_translations(lang)
    })


@app.get("/details/{name}", response_class=HTMLResponse)
async def get_details(request: Request, name: str):
    """顯示某個參賽者的詳細分數"""
    lang = get_language(request)
    t = get_all_translations(lang)
    detail_path = os.path.join(DETAILS_DIR, f"{name}.json")
    
    if not os.path.exists(detail_path):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": t["not_found"].format(name=name),
            "leaders": [],
            "lang": lang,
            "t": t
        })
    
    with open(detail_path, "r", encoding="utf-8") as f:
        detail_data = json.load(f)
    
    return templates.TemplateResponse("details.html", {
        "request": request,
        "detail_data": detail_data,
        "lang": lang,
        "t": t
    })


@app.get("/api/details/{name}")
async def api_get_details(name: str):
    """API: 獲取某個參賽者的詳細分數（JSON 格式）"""
    detail_path = os.path.join(DETAILS_DIR, f"{name}.json")
    
    if not os.path.exists(detail_path):
        return {"success": False, "error": f"找不到「{name}」的詳細資料"}
    
    with open(detail_path, "r", encoding="utf-8") as f:
        detail_data = json.load(f)
    
    return {"success": True, "data": detail_data}


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """管理員登入頁面"""
    lang = get_language(request)
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "lang": lang,
        "t": get_all_translations(lang)
    })


@app.post("/admin/login")
async def admin_login(request: Request, password: str = Form(...)):
    """管理員登入驗證"""
    lang = get_language(request)
    t = get_all_translations(lang)
    if password == ADMIN_PASSWORD:
        # 生成 session token
        token = secrets.token_urlsafe(32)
        admin_sessions.add(token)
        
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_token", value=token, httponly=True, max_age=3600)
        return response
    else:
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": t["password_error"],
            "lang": lang,
            "t": t
        })


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin_token: str = Cookie(None)):
    """管理員控制面板"""
    # 驗證 session
    if not admin_token or admin_token not in admin_sessions:
        return RedirectResponse(url="/admin/login")
    
    lang = get_language(request)
    # 讀取排行榜數據
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        leaders = json.load(f)
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "leaders": leaders,
        "lang": lang,
        "t": get_all_translations(lang)
    })


@app.post("/admin/logout")
async def admin_logout(admin_token: str = Cookie(None)):
    """管理員登出"""
    if admin_token and admin_token in admin_sessions:
        admin_sessions.remove(admin_token)
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_token")
    return response


@app.get("/set_language/{lang}")
async def set_language(lang: str, request: Request):
    """設置語言並返回上一頁"""
    # 驗證語言代碼
    if lang not in ["zh-TW", "en"]:
        lang = "zh-TW"
    
    # 獲取來源頁面
    referer = request.headers.get("referer", "/")
    
    response = RedirectResponse(url=referer, status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=31536000)  # 1年
    return response


@app.delete("/api/admin/delete/{name}")
async def delete_entry(name: str, admin_token: str = Cookie(None)):
    """API: 刪除某個參賽者的所有資料（僅限管理員）"""
    # 驗證管理員權限
    if not admin_token or admin_token not in admin_sessions:
        return {"success": False, "error": "未授權：需要管理員權限"}
    
    try:
        # 1. 從排行榜中移除
        with open(LEADERBOARD_PATH, "r+", encoding="utf-8") as f:
            leaderboard_data = json.load(f)
            original_length = len(leaderboard_data)
            leaderboard_data = [entry for entry in leaderboard_data if entry["name"] != name]
            
            if len(leaderboard_data) == original_length:
                return {"success": False, "error": f"找不到「{name}」的記錄"}
            
            f.seek(0)
            json.dump(leaderboard_data, f, ensure_ascii=False, indent=2)
            f.truncate()
        
        # 2. 刪除詳細資料檔案
        detail_path = os.path.join(DETAILS_DIR, f"{name}.json")
        if os.path.exists(detail_path):
            os.remove(detail_path)
        
        # 3. 刪除上傳的檔案
        upload_path = os.path.join(UPLOAD_DIR, f"{name}.json")
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        return {
            "success": True,
            "message": f"已成功刪除「{name}」的所有資料",
            "leaderboard": leaderboard_data
        }
    
    except Exception as e:
        return {"success": False, "error": f"刪除時發生錯誤：{str(e)}"}


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
            
            # 儲存詳細分數
            detail_path = os.path.join(DETAILS_DIR, f"{name}.json")
            with open(detail_path, "w", encoding="utf-8") as f:
                json.dump({
                    "name": name,
                    "teds": result["TEDS"],
                    "details": result["details"],
                    "valid_count": result["valid_count"],
                    "total_count": result["total_count"]
                }, f, ensure_ascii=False, indent=2)
            
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
