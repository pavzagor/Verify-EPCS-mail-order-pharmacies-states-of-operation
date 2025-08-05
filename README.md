# Pharmacy States of Operation Validation (Multi-Provider AI)

This script validates pharmacy states of operation using multiple AI providers with advanced search capabilities:

## 🤖 Supported AI Providers

### **Google Gemini (Recommended)**
- **Model**: Gemini 2.5 Pro with native search grounding
- **Features**: Real-time web search, URL grounding, cost-effective
- **Search Integration**: Native Google Search for regulatory databases
- **Cost**: More affordable than OpenAI alternatives

### **OpenAI**
- **Models**: o3-deep-research, o4-mini-deep-research, gpt-4o
- **Features**: Deep research capabilities with web search
- **Best for**: Users with OpenAI Verified Organization status

The script processes CSV files containing mail-order pharmacy data and verifies if their listed states of operation are accurate using real-time regulatory searches.

## Setup Instructions

### 1. Install Dependencies

Choose one of the following methods:

#### Option A: Using UV (Recommended - Fast & Modern)
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Option B: Using pip (Traditional)
```bash
pip install -r requirements.txt
```

### 2. Configure AI Provider

Choose and configure your preferred AI provider:

#### **Option A: Google Gemini (Recommended)**

Get your free Google AI API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create or sign in to your Google account
3. Generate a new API key

Create a `.env` file:
```bash
# Google Gemini Configuration (Recommended)
AI_PROVIDER=google
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-2.5-pro

# Enable advanced search features
ENABLE_SEARCH_GROUNDING=true
ENABLE_URL_GROUNDING=true
```

**Benefits:**
- Native Google Search integration for regulatory databases
- More cost-effective than OpenAI alternatives
- Superior search accuracy for licensing verification
- No organization verification required

#### **Option B: OpenAI**

You need an OpenAI API key with access to research models:

```bash
# OpenAI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=o3-deep-research
```

**Available Models:**
- **o3-deep-research**: Best quality with web search, requires Verified Organization ($10-40/1M + $10/1K searches)
- **o4-mini-deep-research**: Cheaper deep research option ($2-8/1M + $10/1K searches)
- **gpt-4o**: Good alternative, more accessible ($5-15/1M + $25/1K searches)

#### Environment Variable Method (Alternative)
**On macOS/Linux:**
```bash
export AI_PROVIDER="google"
export GOOGLE_API_KEY="your-api-key-here"
```

**On Windows:**
```cmd
set AI_PROVIDER=google
set GOOGLE_API_KEY=your-api-key-here
```

### 3. Prepare Your CSV File
- Place your CSV file in the `CSVs/` directory
- Default expected filename: `Mail order active EPCS pharmacies w states - Master 31 Jul 2025.csv`
- Or configure custom location in your `.env` file:
  ```bash
  CSV_DIRECTORY=CSVs
  CSV_FILENAME=your-custom-filename.csv
  ```
- The CSV must contain the column: `Operates in states`

## Usage

### Quick Start

#### Using UV:
```bash
# Automated runner (recommended)
uv run run_validation.py

# Or run individual scripts
uv run validate_pharmacy_states.py
```

#### Using pip/python:
```bash
# Automated runner (recommended)
python run_validation.py

# Or run individual scripts
python validate_pharmacy_states.py
```

### Verification
Test your setup before running validation:
```bash
# With UV
uv run test_setup.py

# With pip/python
python test_setup.py
```

## What the Script Does

1. **Loads the CSV** and validates it has the required columns
2. **Splits data into batches** of 30 pharmacies (configurable)
3. **Uses AI provider with web search** to validate each pharmacy's states of operation:
   
   **Google Gemini Features:**
   - Native Google Search integration for regulatory databases
   - URL grounding for direct access to state pharmacy boards
   - Real-time license verification through official portals
   - Cross-references NABP (National Association of Boards of Pharmacy) database
   
   **OpenAI Features:**
   - Deep research capabilities with web search
   - Advanced reasoning for complex regulatory scenarios
   - Comprehensive regulatory compliance analysis

4. **Saves progress after each batch** - no lost work if interrupted
5. **Creates a new CSV** with the original data plus validation results

## Output

The script creates a new CSV file with timestamp: `validated_pharmacies_YYYYMMDD_HHMMSS.csv`

### New Columns Added:
- **Initial states of operation correct**: Boolean (True/False/None)
- **States of operation by [PROVIDER] AI**: Corrected states if different from original (column name varies by provider)
- **Validation confidence**: high/medium/low/error
- **Validation reasoning**: Explanation of the validation decision

## Configuration

### Environment Variables (.env file)
```bash
# AI Provider Selection
AI_PROVIDER=google                    # 'openai' or 'google'

# Google Gemini Configuration
GOOGLE_API_KEY=your-api-key
GOOGLE_MODEL=gemini-2.5-pro          # or 'gemini-2.5-flash'
ENABLE_SEARCH_GROUNDING=true         # Enable Google Search integration
ENABLE_URL_GROUNDING=true            # Enable URL grounding for regulatory sites

# OpenAI Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=o3-deep-research        # or 'o4-mini-deep-research', 'gpt-4o'

# CSV File Configuration
CSV_DIRECTORY=CSVs                   # Directory containing CSV files
CSV_FILENAME=Mail order active EPCS pharmacies w states - Master 31 Jul 2025.csv

# Processing Configuration
BATCH_SIZE=30                        # Number of pharmacies per API call
RATE_LIMIT_DELAY=2                   # Seconds between API calls
```

### Script Variables
You can also modify these variables directly in the script:
- `CSV_DIRECTORY`: Directory containing CSV files (default: 'CSVs')
- `CSV_FILENAME`: Input CSV filename (now includes directory path)
- `OUTPUT_FILENAME`: Output CSV filename pattern

## Logs

The script creates detailed logs in:
- Console output (real-time progress)
- Log file: `validation_log_YYYYMMDD_HHMMSS.log`

## Error Handling

The script handles:
- Missing API keys
- Invalid CSV files
- API rate limits
- Parsing errors
- Network timeouts

If validation fails for any batch, it continues with the remaining batches and marks failed items appropriately.

## Cost Considerations

### Google Gemini (Recommended)
- **Gemini 2.5 Pro**: More cost-effective than OpenAI alternatives
- Each batch of 30 pharmacies uses approximately 1,000-2,000 tokens
- Native search integration may reduce token usage
- No organization verification required

### OpenAI
- **o3-deep-research**: Expensive (~$20-40 per 1M tokens + $10/1K searches)
- **o4-mini-deep-research**: Cheaper option (~$2-8 per 1M tokens + $10/1K searches)
- **gpt-4o**: Moderate cost (~$5-15 per 1M tokens + $25/1K searches)
- Requires Verified Organization for best models

**Total cost depends on your dataset size, chosen provider, and API pricing**

## Support

For issues or questions, check the log files for detailed error messages.