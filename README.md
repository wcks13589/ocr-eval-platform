# OCR Evaluation Platform

A web-based evaluation platform for OCR (Optical Character Recognition) results, featuring real-time leaderboard and TEDS (Tree Edit Distance based Similarity) metric scoring.

## 📋 Overview

This platform allows users to:
- Upload OCR prediction results in JSON format
- Automatically evaluate predictions against ground truth using TEDS metrics
- View real-time rankings on an interactive leaderboard with WebSocket progress updates
- Analyze detailed evaluation results with filtering and statistics
- Export results as CSV for further analysis
- Switch between Traditional Chinese and English interfaces
- Compare table recognition accuracy with other participants
- Administrators can manage submissions and delete entries through a secure dashboard

## 🚀 Features

- **TEDS Metric**: Industry-standard Tree Edit Distance based Similarity for table structure evaluation
- **Flexible Input**: Supports both Markdown and HTML table formats
- **Real-time Leaderboard**: Instant ranking updates after each submission
- **Detailed Score View**: View individual table scores with filtering and statistics
- **WebSocket Progress**: Real-time progress updates during evaluation
- **Multi-language Support**: Switch between Traditional Chinese and English
- **Admin Dashboard**: Manage submissions with authentication and delete capabilities
- **Format Validation**: Automatic validation of uploaded JSON files
- **Modern UI**: Clean and responsive web interface
- **Docker Support**: Easy deployment with containerization
- **CSV Export**: Download detailed scores as CSV files

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: Jinja2 Templates, HTML/CSS/JavaScript
- **Real-time Communication**: WebSocket
- **Internationalization**: Custom i18n module (Chinese/English)
- **Metrics**: TEDS (Tree Edit Distance), Levenshtein Distance, Edit Distance
- **Parsing**: lxml, apted, distance, zss
- **Server**: Uvicorn
- **Authentication**: Cookie-based session management

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/wcks13589/ocr-eval-platform.git
cd ocr-eval-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare your ground truth data:
   - Place your ground truth JSON file at `data/ground_truth.json`
   - Format: `{"id": "<table>...</table>"}` or markdown table format

4. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

5. Access the platform:
   - Open your browser and navigate to `http://localhost:8080`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t ocr-eval-platform .
```

2. Run the container with volume mounting:
```bash
docker run -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  ocr-eval-platform
```

**Note**: The `-v` flag mounts the local `data/` directory to persist uploads and leaderboard data.

3. Access the platform at `http://localhost:8080`

### Docker Compose (Recommended)

For easier management, use Docker Compose:

```bash
# Start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

The `docker-compose.yml` automatically handles volume mounting and configuration.

## 📝 Usage

### Preparing Prediction Files

Your prediction file should be a JSON file with the following structure:

```json
{
  "sample_id_1": "| Header1 | Header2 |\n|---------|----------|\n| Cell1   | Cell2    |",
  "sample_id_2": "<table><tr><td>Cell1</td><td>Cell2</td></tr></table>",
  "sample_id_3": "..."
}
```

**Supported formats:**
- Markdown tables
- HTML table strings
- Mixed format (different IDs can use different formats)

### Submitting Predictions

1. Navigate to the main page
2. Enter your participant name
3. Upload your JSON prediction file
4. Click "Start Evaluation" (🚀 開始評估)
5. Watch real-time progress updates via WebSocket
6. View your score and ranking on the leaderboard
7. Click "Details" to see individual table scores

### Viewing Detailed Results

After submission, you can view detailed evaluation results:

1. Click the "🔍 詳細" (Details) button next to your name on the leaderboard
2. View statistics including:
   - Overall TEDS score
   - Valid data count
   - Score distribution (Perfect/High/Medium/Low)
   - Individual table scores
3. Use filters to show/hide:
   - Normal data (✅)
   - Missing data (❌)
   - Error data (⚠️)
   - Score range filtering
4. Download results as CSV for further analysis

### Admin Functions

Administrators can manage submissions:

1. Navigate to `/admin/login`
2. Enter the admin password
3. Access the admin dashboard to:
   - View all submissions
   - Delete individual entries (removes all associated data)
   - Monitor platform usage
4. Logout when finished to clear the session

### Evaluation Metrics

The platform uses **TEDS (Tree Edit Distance based Similarity)** to evaluate table structure accuracy:

- **Range**: 0.0 to 1.0 (higher is better)
- **Calculation**: Measures structural and content similarity between predicted and ground truth tables
- **Normalization**: Accounts for table size differences
- **Weighting**: Considers both cell content and table structure

## 📊 API Endpoints

### Public Endpoints

#### GET `/`
Main page with upload form and leaderboard

#### POST `/upload`
Upload prediction file without evaluation
- **Parameters**: 
  - `name` (form field): Participant name
  - `file` (file upload): JSON prediction file
- **Returns**: JSON response with file path or error

#### POST `/evaluate`
Upload and evaluate prediction file (fallback for non-WebSocket)
- **Parameters**: 
  - `name` (form field): Participant name
  - `file` (file upload): JSON prediction file
- **Returns**: Updated leaderboard with evaluation results

#### GET `/leaderboard`
View standalone leaderboard page

#### GET `/details/{name}`
View detailed evaluation results for a participant
- **Parameters**: 
  - `name` (path): Participant name
- **Returns**: HTML page with detailed scores, statistics, and filtering options

#### GET `/api/details/{name}`
Get detailed evaluation data in JSON format
- **Parameters**: 
  - `name` (path): Participant name
- **Returns**: JSON with detailed scores and statistics

#### GET `/set_language/{lang}`
Set interface language preference
- **Parameters**: 
  - `lang` (path): Language code (`zh-TW` or `en`)
- **Returns**: Redirect to previous page with language cookie set

#### WebSocket `/ws/{session_id}`
Real-time evaluation progress updates
- **Parameters**: 
  - `session_id` (path): Unique session identifier
- **Messages**: 
  - Receives: `{name, file_path}` to start evaluation
  - Sends: Progress updates and completion status

### Admin Endpoints

#### GET `/admin/login`
Admin login page

#### POST `/admin/login`
Admin authentication
- **Parameters**: 
  - `password` (form field): Admin password
- **Returns**: Redirect to dashboard on success

#### GET `/admin/dashboard`
Admin control panel (requires authentication)
- **Features**: View all submissions, delete entries
- **Authentication**: Cookie-based session token

#### POST `/admin/logout`
Admin logout and session cleanup

#### DELETE `/api/admin/delete/{name}`
Delete a participant's data (requires admin authentication)
- **Parameters**: 
  - `name` (path): Participant name
  - `admin_token` (cookie): Admin session token
- **Returns**: JSON response with updated leaderboard

## 🗂️ Project Structure

```
ocr-eval-platform/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── evaluation.py        # Evaluation logic and metrics
│   ├── TEDS_metric.py       # TEDS implementation
│   ├── parallel.py          # Parallel processing utilities
│   ├── i18n.py              # Internationalization (Chinese/English)
│   ├── static/
│   │   └── style.css        # Styling
│   └── templates/
│       ├── index.html       # Main page with upload form
│       ├── leaderboard.html # Standalone leaderboard page
│       ├── details.html     # Detailed score view page
│       ├── admin_login.html # Admin login page
│       ├── admin_dashboard.html # Admin control panel
│       └── result.html      # Results display (legacy)
├── data/                    # Data directory (separate from code)
│   ├── ground_truth.json    # Ground truth data
│   ├── leaderboard.json     # Leaderboard storage (auto-generated)
│   ├── details/             # Individual participant detailed scores
│   └── uploads/             # Uploaded prediction files
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Data Management

The platform uses a dedicated `data/` directory to separate data from code:

**Benefits:**
- ✅ **Clean separation**: Code and data are isolated
- ✅ **Easy backup**: Simply backup the `data/` folder
- ✅ **Docker persistence**: Easy volume mounting for containers
- ✅ **Version control**: Data files can be gitignored separately
- ✅ **Security**: Sensitive data isolated from application code

**Directory structure:**
```
data/
├── ground_truth.json    # Your test dataset (required)
├── leaderboard.json     # Auto-generated rankings
├── details/             # Detailed scores for each participant
└── uploads/             # User-submitted predictions
```

### Ground Truth Format

The `data/ground_truth.json` file should contain:

```json
{
  "sample_id_1": "| Header1 | Header2 |\n|---------|----------|\n| Cell1   | Cell2    |",
  "sample_id_2": "<table><tr><td>Cell1</td><td>Cell2</td></tr></table>",
  "sample_id_3": "..."
}
```

**Example with actual data:**
```json
{
  "table_001": "| Name | Age | City |\n|------|-----|------|\n| Alice | 30 | NYC |",
  "table_002": "<table><tr><td>Product</td><td>Price</td></tr><tr><td>Apple</td><td>$2</td></tr></table>"
}
```

### Admin Configuration

Set the admin password using an environment variable:

```bash
# Linux/Mac
export ADMIN_PASSWORD="your_secure_password"

# Windows
set ADMIN_PASSWORD=your_secure_password

# Docker
docker run -p 8080:8080 -e ADMIN_PASSWORD=your_secure_password ocr-eval-platform
```

Default password (if not set): `admin123`

**Security Note**: Always change the default admin password in production environments.

### Language Settings

The platform supports:
- Traditional Chinese (`zh-TW`) - Default
- English (`en`)

Users can switch languages using the language selector in the web interface. The preference is stored in a cookie for 1 year.

### Modifying TEDS Parameters

In `app/evaluation.py`, you can adjust:

```python
teds = TEDS(n_jobs=4)  # Number of parallel jobs
```

## 🐛 Error Handling

The platform handles various error cases:

- **Invalid JSON format**: Returns error message with parsing details and removes uploaded file
- **Encoding errors**: Detects non-UTF-8 files and provides helpful error messages
- **Duplicate names**: Prevents overwriting existing submissions with clear warning
- **Missing fields**: Gracefully handles incomplete predictions
- **WebSocket fallback**: Automatically falls back to traditional POST if WebSocket is unavailable
- **Authentication errors**: Redirects to login page for unauthorized admin access
- **File cleanup**: Automatically removes uploaded files on evaluation failure

## 📄 License

Copyright 2020 IBM (TEDS implementation)  
Licensed under Apache 2.0 License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

For questions or issues, please contact the project maintainer or open an issue on GitHub.

## 🙏 Acknowledgments

- TEDS implementation based on [PubTabNet](https://github.com/ibm-aur-nlp/PubTabNet) by IBM Research
- Tree edit distance using [apted](https://github.com/JoaoFelipe/apted) library
- FastAPI framework for rapid web development

---

**Version**: 2.0.0  
**Last Updated**: October 2025

## 🆕 What's New in v2.0.0

- ✨ Multi-language support (Traditional Chinese and English)
- 🔐 Admin dashboard with authentication
- 📊 Detailed score view with filtering and statistics
- 🌐 WebSocket real-time progress updates
- 📥 CSV export functionality
- 🗑️ Admin delete capabilities
- 🎨 Improved UI with better user experience
- 🔒 Cookie-based session management

