import json
import re
from app.TEDS_metric import TEDS, convert_markdown_table_to_html, wrap_html_table

GROUND_TRUTH = None

def load_ground_truth(path="data/ground_truth.json"):
    """
    載入 Ground Truth（只在伺服器啟動時讀取一次）
    格式：{ "id": "<table>...</table>" 或 markdown 表格 }
    """
    global GROUND_TRUTH
    if GROUND_TRUTH is None:
        print("[INFO] Loading ground truth data...")
        with open(path, 'r', encoding='utf-8') as f:
            GROUND_TRUTH = json.load(f)
        print(f"[INFO] Loaded {len(GROUND_TRUTH)} ground truth entries.")
    return GROUND_TRUTH


def clean_latex(text: str) -> str:
    """移除多餘空白與換行符，避免 TEDS 誤判"""
    text = text.replace("\n", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_to_html(text: str) -> str:
    """
    若輸入是 Markdown，轉成 HTML；
    若本身就是 HTML，則包裝成完整結構。
    """
    text = text.strip()
    if "<table" in text:
        html_str = wrap_html_table(text)
    elif text.startswith("\\begin{tabular}") or text.startswith("\\begin{table}"):
        html_str = latex_to_html_table(text)
    else:
        html_str = convert_markdown_table_to_html(text)
    return clean_latex(html_str)

def latex_to_html_table(latex_str):
    latex_str = latex_str.strip()
    latex_str = re.sub(r'\\\\', '\n', latex_str)  # 把行尾的 \\ 換成換行
    latex_str = re.sub(r'\\(begin|end){tabular}{.*?}', '', latex_str)  # 去掉 begin/end
    latex_str = re.sub(r'\\textbf{(.*?)}', r'\1', latex_str)  # 去掉粗體
    latex_str = re.sub(r'\$|\\', '', latex_str)  # 去掉 latex 特殊符號

    lines = [line.strip() for line in latex_str.splitlines() if '&' in line]
    table_rows = [[cell.strip() for cell in line.split('&')] for line in lines]

    html_table = "<html><body><table>"
    for row in table_rows:
        html_table += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html_table += "</table></body></html>"
    return html_table

def evaluate(pred_path):
    """
    使用 TEDS 計算 Ground Truth 與預測結果的平均相似度。
    只回傳整體平均分數。
    """
    ground_truth = load_ground_truth()

    try:
        with open(pred_path, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"上傳的檔案格式錯誤：無法解析 JSON 格式。錯誤訊息：{str(e)}")
    except UnicodeDecodeError:
        raise ValueError("上傳的檔案格式錯誤：檔案編碼不正確，請確保使用 UTF-8 編碼。")
    
    teds = TEDS(n_jobs=4)
    total_score = 0.0
    valid_count = 0

    for key, gt_text in ground_truth.items():
        pred_text = predictions.get(key, "")
        if not gt_text or not pred_text:
            continue

        gt_html = normalize_to_html(gt_text)
        pred_html = normalize_to_html(pred_text)

        score = teds.evaluate(pred_html, gt_html)
        total_score += score
        valid_count += 1

    avg_score = total_score / valid_count if valid_count > 0 else 0.0
    return {"TEDS": round(avg_score, 4)}
