# -*- coding: utf-8 -*-
"""
Internationalization (i18n) module for OCR Evaluation Platform
Supports Traditional Chinese (zh-TW) and English (en)
"""

TRANSLATIONS = {
    "zh-TW": {
        # Common
        "app_title": "OCR 評估平台",
        "language": "語言",
        "chinese": "中文",
        "english": "English",
        
        # Index page
        "index_title": "🧠 OCR 評估平台",
        "admin_link": "🔐 管理員",
        "participant_name": "👤 參賽者名稱",
        "participant_name_placeholder": "請輸入你的名稱",
        "upload_file": "📄 上傳結果檔案",
        "start_evaluation": "🚀 開始評估",
        "uploading": "📤 上傳中...",
        "evaluating": "⏳ 評估中...",
        
        # Progress
        "processing_file": "⏳ 正在處理您的檔案...",
        "preparing": "準備開始...",
        "evaluating_item": "正在評估第 {current} / {total} 筆資料 (Table: {key})",
        "evaluation_complete": "✅ 評估完成！",
        "score_result": "{name} 的 TEDS 分數為 {score}",
        
        # Leaderboard
        "leaderboard_title": "🏆 即時排行榜",
        "leaderboard_page_title": "🏆 排行榜",
        "rank": "🏅 名次",
        "name": "👤 名稱",
        "teds_score": "📊 TEDS",
        "details": "🔍 詳細資訊",
        "view_details": "📋 詳細",
        "no_records": "目前還沒有任何紀錄，成為第一位挑戰者吧！🚀",
        "no_records_short": "目前沒有任何記錄",
        "back_home": "🏠 返回首頁",
        "view_leaderboard": "📊 查看排行榜",
        
        # Details page
        "detail_title": "📊 詳細評估結果",
        "participant": "👤 參賽者",
        "average_teds": "📈 平均 TEDS",
        "valid_data": "✅ 有效資料",
        "back": "⬅️ 返回首頁",
        "download_csv": "📥 下載 CSV",
        "show_filter": "🔍 顯示篩選",
        "hide_filter": "🔍 隱藏篩選",
        "show_normal": "顯示正常資料",
        "show_missing": "顯示缺失資料",
        "show_error": "顯示錯誤資料",
        "min_score": "最低分數：",
        "max_score": "最高分數：",
        "score_statistics": "📈 分數統計",
        "perfect_score": "完美分數 (1.0)",
        "high_score": "高分 (≥0.8)",
        "medium_score": "中分 (0.5-0.8)",
        "low_score": "低分 (<0.5)",
        "serial_number": "序號",
        "table_id": "表格 ID",
        "teds_score_col": "TEDS 分數",
        "status": "狀態",
        "rating": "評級",
        "status_normal": "✅ 正常",
        "status_missing": "❌ 缺失",
        "status_error": "⚠️ 錯誤",
        "grade_perfect": "🌟 完美",
        "grade_excellent": "😊 優秀",
        "grade_average": "😐 普通",
        "grade_improve": "😞 待改進",
        
        # Admin
        "admin_login_title": "🔐 管理員登入",
        "admin_dashboard": "⚙️ 管理員控制面板",
        "password": "密碼",
        "password_placeholder": "請輸入管理員密碼",
        "login": "登入",
        "logout": "🚪 登出",
        "password_error": "密碼錯誤",
        "total_records": "總記錄數：",
        "leaderboard_management": "📊 排行榜記錄管理",
        "operation": "🗑️ 操作",
        "delete": "🗑️ 刪除",
        "deleting": "刪除中...",
        "delete_confirm": "確定要刪除「{name}」的所有資料嗎？\n\n這將會刪除：\n- 排行榜記錄\n- 詳細評分資料\n- 上傳的檔案\n\n此操作無法復原！",
        "delete_success": "✅ {message}",
        "delete_failed": "刪除失敗：{error}",
        
        # Error messages
        "name_exists": "名稱「{name}」已存在排行榜，請換一個名稱。",
        "fill_all_fields": "請填寫所有欄位",
        "file_upload_failed": "檔案上傳失敗",
        "connection_error": "連接錯誤，請重試",
        "error_occurred": "發生錯誤：{error}",
        "not_found": "找不到「{name}」的詳細資料",
        
        # CSV download
        "csv_filename": "{name}_詳細分數.csv",
        "csv_header": "序號,資料ID,TEDS分數,狀態\n",
    },
    
    "en": {
        # Common
        "app_title": "OCR Evaluation Platform",
        "language": "Language",
        "chinese": "中文",
        "english": "English",
        
        # Index page
        "index_title": "🧠 OCR Evaluation Platform",
        "admin_link": "🔐 Admin",
        "participant_name": "👤 Participant Name",
        "participant_name_placeholder": "Please enter your name",
        "upload_file": "📄 Upload Result File",
        "start_evaluation": "🚀 Start Evaluation",
        "uploading": "📤 Uploading...",
        "evaluating": "⏳ Evaluating...",
        
        # Progress
        "processing_file": "⏳ Processing your file...",
        "preparing": "Preparing...",
        "evaluating_item": "Evaluating {current} / {total} items (Table: {key})",
        "evaluation_complete": "✅ Evaluation Complete!",
        "score_result": "TEDS score for {name} is {score}",
        
        # Leaderboard
        "leaderboard_title": "🏆 Live Leaderboard",
        "leaderboard_page_title": "🏆 Leaderboard",
        "rank": "🏅 Rank",
        "name": "👤 Name",
        "teds_score": "📊 TEDS",
        "details": "🔍 Details",
        "view_details": "📋 Details",
        "no_records": "No records yet, be the first challenger! 🚀",
        "no_records_short": "No records available",
        "back_home": "🏠 Back to Home",
        "view_leaderboard": "📊 View Leaderboard",
        
        # Details page
        "detail_title": "📊 Detailed Evaluation Results",
        "participant": "👤 Participant",
        "average_teds": "📈 Average TEDS",
        "valid_data": "✅ Valid Data",
        "back": "⬅️ Back to Home",
        "download_csv": "📥 Download CSV",
        "show_filter": "🔍 Show Filter",
        "hide_filter": "🔍 Hide Filter",
        "show_normal": "Show Normal Data",
        "show_missing": "Show Missing Data",
        "show_error": "Show Error Data",
        "min_score": "Min Score:",
        "max_score": "Max Score:",
        "score_statistics": "📈 Score Statistics",
        "perfect_score": "Perfect Score (1.0)",
        "high_score": "High Score (≥0.8)",
        "medium_score": "Medium Score (0.5-0.8)",
        "low_score": "Low Score (<0.5)",
        "serial_number": "No.",
        "table_id": "Table ID",
        "teds_score_col": "TEDS Score",
        "status": "Status",
        "rating": "Rating",
        "status_normal": "✅ Normal",
        "status_missing": "❌ Missing",
        "status_error": "⚠️ Error",
        "grade_perfect": "🌟 Perfect",
        "grade_excellent": "😊 Excellent",
        "grade_average": "😐 Average",
        "grade_improve": "😞 Needs Improvement",
        
        # Admin
        "admin_login_title": "🔐 Admin Login",
        "admin_dashboard": "⚙️ Admin Dashboard",
        "password": "Password",
        "password_placeholder": "Please enter admin password",
        "login": "Login",
        "logout": "🚪 Logout",
        "password_error": "Incorrect password",
        "total_records": "Total Records:",
        "leaderboard_management": "📊 Leaderboard Management",
        "operation": "🗑️ Operation",
        "delete": "🗑️ Delete",
        "deleting": "Deleting...",
        "delete_confirm": "Are you sure you want to delete all data for '{name}'?\n\nThis will delete:\n- Leaderboard record\n- Detailed score data\n- Uploaded file\n\nThis action cannot be undone!",
        "delete_success": "✅ {message}",
        "delete_failed": "Delete failed: {error}",
        
        # Error messages
        "name_exists": "Name '{name}' already exists on the leaderboard. Please choose a different name.",
        "fill_all_fields": "Please fill in all fields",
        "file_upload_failed": "File upload failed",
        "connection_error": "Connection error, please retry",
        "error_occurred": "Error occurred: {error}",
        "not_found": "Cannot find detailed data for '{name}'",
        
        # CSV download
        "csv_filename": "{name}_detailed_scores.csv",
        "csv_header": "No.,Data ID,TEDS Score,Status\n",
    }
}


def get_translation(lang: str, key: str, **kwargs) -> str:
    """
    Get translation for a specific key in the given language.
    
    Args:
        lang: Language code ('zh-TW' or 'en')
        key: Translation key
        **kwargs: Format arguments for the translation string
    
    Returns:
        Translated string with format arguments applied
    """
    # Default to Chinese if language not found
    if lang not in TRANSLATIONS:
        lang = "zh-TW"
    
    # Get translation, fallback to Chinese if key not found
    translation = TRANSLATIONS[lang].get(key)
    if translation is None:
        translation = TRANSLATIONS["zh-TW"].get(key, key)
    
    # Apply format arguments if provided
    if kwargs:
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation
    
    return translation


def get_all_translations(lang: str) -> dict:
    """
    Get all translations for a specific language.
    
    Args:
        lang: Language code ('zh-TW' or 'en')
    
    Returns:
        Dictionary of all translations for the language
    """
    if lang not in TRANSLATIONS:
        lang = "zh-TW"
    return TRANSLATIONS[lang]

