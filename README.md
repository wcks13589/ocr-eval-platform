# OCR Evaluation Platform

A web-based evaluation platform for OCR (Optical Character Recognition) results, featuring real-time leaderboard and TEDS (Tree Edit Distance based Similarity) metric scoring.

## 📋 Overview

This platform allows users to:
- Upload OCR prediction results in JSON format
- Automatically evaluate predictions against ground truth using TEDS metrics
- View real-time rankings on an interactive leaderboard
- Compare table recognition accuracy with other participants

## 🚀 Features

- **TEDS Metric**: Industry-standard Tree Edit Distance based Similarity for table structure evaluation
- **Flexible Input**: Supports both Markdown and HTML table formats
- **Real-time Leaderboard**: Instant ranking updates after each submission
- **Format Validation**: Automatic validation of uploaded JSON files
- **Modern UI**: Clean and responsive web interface
- **Docker Support**: Easy deployment with containerization

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: Jinja2 Templates, HTML/CSS
- **Metrics**: TEDS (Tree Edit Distance), Levenshtein Distance
- **Parsing**: lxml, apted, distance
- **Server**: Uvicorn

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
5. View your score and ranking on the leaderboard

### Evaluation Metrics

The platform uses **TEDS (Tree Edit Distance based Similarity)** to evaluate table structure accuracy:

- **Range**: 0.0 to 1.0 (higher is better)
- **Calculation**: Measures structural and content similarity between predicted and ground truth tables
- **Normalization**: Accounts for table size differences
- **Weighting**: Considers both cell content and table structure

## 📊 API Endpoints

### GET `/`
Main page with upload form and leaderboard

### POST `/evaluate`
Upload and evaluate prediction file
- **Parameters**: 
  - `name` (form field): Participant name
  - `file` (file upload): JSON prediction file
- **Returns**: Updated leaderboard with evaluation results

### GET `/leaderboard`
View standalone leaderboard page

## 🗂️ Project Structure

```
ocr-eval-platform/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── evaluation.py        # Evaluation logic and metrics
│   ├── TEDS_metric.py       # TEDS implementation
│   ├── parallel.py          # Parallel processing utilities
│   ├── static/
│   │   └── style.css        # Styling
│   └── templates/
│       ├── index.html       # Main page
│       ├── leaderboard.html # Leaderboard page
│       └── result.html      # Results display
├── data/                    # Data directory (separate from code)
│   ├── ground_truth.json    # Ground truth data
│   ├── leaderboard.json     # Leaderboard storage (auto-generated)
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

### Modifying TEDS Parameters

In `app/evaluation.py`, you can adjust:

```python
teds = TEDS(n_jobs=4)  # Number of parallel jobs
```

## 🐛 Error Handling

The platform handles various error cases:

- **Invalid JSON format**: Returns error message with parsing details
- **Encoding errors**: Detects non-UTF-8 files
- **Duplicate names**: Prevents overwriting existing submissions
- **Missing fields**: Gracefully handles incomplete predictions

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

**Version**: 1.0.0  
**Last Updated**: October 2025

