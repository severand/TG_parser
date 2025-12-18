# Setup Guide - Telegram Parser Pro

## Prerequisites

- Python 3.11+
- pip or poetry
- Virtual environment (recommended)

## Step 1: Clone Repository

```bash
git clone https://github.com/severand/TG_parser.git
cd TG_parser
```

## Step 2: Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment

```bash
# Copy example files
cp .env.example .env
cp config/config.example.json config/config.json
```

## Step 5: Edit Configuration

Edit `config/config.json` with your settings:

```json
{
  "parser": {
    "max_threads": 5,
    "timeout": 30,
    "delay_min": 1,
    "delay_max": 5
  },
  "output": {
    "format": "console",
    "directory": "results/"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/parser.log"
  }
}
```

## Step 6: Verify Installation

```bash
python main.py --help
```

## Step 7: First Run

```bash
python main.py --channels "channel1,channel2" --keywords "keyword1,keyword2"
```

## Troubleshooting

### Import errors
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Python version
```bash
python --version  # Should be 3.11+
```

### Virtual environment issues
```bash
# Deactivate current
deactivate

# Remove old venv
rm -rf venv

# Create new
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
