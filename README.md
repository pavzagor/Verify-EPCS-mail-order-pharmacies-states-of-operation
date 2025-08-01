# Pharmacy States of Operation Validation

This script validates pharmacy states of operation using OpenAI's o3-deepresearch API. It processes a CSV file containing mail-order pharmacy data and verifies if their listed states of operation are accurate.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
You need an OpenAI API key with access to the o3-deepresearch model.

**On macOS/Linux:**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**On Windows:**
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Prepare Your CSV File
- Ensure your CSV file is named: `Mail Order Pharmacies by State Jul 31 2025.csv`
- Or update the `CSV_FILENAME` variable in the script if using a different name
- The CSV must contain the column: `Operates in states`

## Usage

Simply run the script:
```bash
python validate_pharmacy_states.py
```

## What the Script Does

1. **Loads the CSV** and validates it has the required columns
2. **Splits data into batches** of 30 pharmacies (configurable)
3. **Uses OpenAI o3-deepresearch** to validate each pharmacy's states of operation
4. **Creates a new CSV** with the original data plus validation results

## Output

The script creates a new CSV file with timestamp: `validated_pharmacies_YYYYMMDD_HHMMSS.csv`

### New Columns Added:
- **Initial states of operation correct**: Boolean (True/False/None)
- **States of operation by OpenAI deepresearch**: Corrected states if different from original
- **Validation confidence**: high/medium/low/error
- **Validation reasoning**: Explanation of the validation decision

## Configuration

You can modify these variables in the script:
- `BATCH_SIZE`: Number of pharmacies per API call (default: 30)
- `RATE_LIMIT_DELAY`: Seconds between API calls (default: 2)
- `CSV_FILENAME`: Input CSV filename
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

- The o3-deepresearch model is expensive (~$20-40 per 1M tokens)
- Each batch of 30 pharmacies uses approximately 1,000-2,000 tokens
- Total cost depends on your dataset size and API pricing

## Support

For issues or questions, check the log files for detailed error messages.