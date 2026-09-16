# Gmail Classifier

An intelligent email classifier that uses AI to automatically categorize Gmail messages. This tool connects to your Gmail account and uses a local Ollama instance to classify emails into topics (like research, teaching, administrative work), assign status indicators (action required, waiting, reference, none), and determine message kind (human, institutional, newsletter, etc.).

## Features

- **AI-Powered Classification**: Uses Ollama with Gemma 3 to intelligently classify emails
- **Multi-dimensional Tagging**: Assigns topic, status, and kind to each email
- **Gmail Integration**: Works directly with your Gmail account via Google API
- **Batch Processing**: Classify recent emails or evaluate historical messages
- **Label Management**: Automatically creates Gmail labels and applies classifications
- **Evaluation Mode**: Export classifications to CSV for review and refinement

## Requirements

- Python 3.12+
- [Ollama](https://ollama.ai/) running locally with Gemma 3 12B model
- Google Gmail API credentials (for Gmail access)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd gmail-classifier
```

### 2. Install dependencies

Using Poetry:

```bash
poetry install
```

### 3. Set up Gmail API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials JSON file
6. Save it as `credentials.json` in the project root directory

### 4. Set up Ollama

1. Install [Ollama](https://ollama.ai/)
2. Pull the Gemma 3 12B model:
   ```bash
   ollama pull gemma3:12b
   ```
3. Start the Ollama service (it runs on `http://localhost:11434` by default)

## Usage

All commands are run through the CLI. You can access the main entry point with:

```bash
poetry run gmail-classifier [command] [options]
```

Or after installation:

```bash
gmail-classifier [command] [options]
```

### Available Commands

#### `test-ollama`
Test the connection to your Ollama instance and verify classification works.

```bash
poetry run gmail-classifier test-ollama
```

This will classify a sample email and display the JSON result.

#### `test-gmail`
Read and display recent messages from your Gmail inbox.

```bash
poetry run gmail-classifier test-gmail --limit 5
```

**Options:**
- `--limit` (default: 5): Number of recent messages to retrieve

#### `classify-recent`
Classify recent emails without modifying Gmail. Shows classifications in the terminal.

```bash
poetry run gmail-classifier classify-recent --limit 5 --query "in:inbox -label:AI/Classified"
```

**Options:**
- `--limit` (default: 5): Number of messages to classify
- `--query` (default: `"in:inbox -label:AI/Classified"`): Gmail search query to filter messages

#### `evaluate`
Classify emails and export results to a CSV file for review. Useful for evaluating the classifier's performance.

```bash
poetry run gmail-classifier evaluate --limit 200 --query "newer_than:180d" --output evaluation.csv
```

**Options:**
- `--limit` (default: 200): Number of messages to classify
- `--query` (default: `"newer_than:180d -label:AI/Classified"`): Gmail search query
- `--output` (default: `"evaluation.csv"`): CSV file to save results

The CSV includes:
- `id`: Gmail message ID
- `from`: Sender email
- `subject`: Email subject
- `topic`: Assigned topic
- `status`: Assigned status
- `kind`: Assigned kind
- `confidence`: Classifier confidence (0.0-1.0)

#### `show`
Display all emails from the evaluation CSV that match a specific topic.

```bash
poetry run gmail-classifier show "FEUP/Teaching/LTW" --input evaluation.csv
```

**Options:**
- `--input` (default: `"evaluation.csv"`): CSV file to read

#### `create-labels`
Create Gmail labels for all classification topics in your account.

```bash
poetry run gmail-classifier create-labels
```

This creates labels like:
- `FEUP/Teaching/LTW`
- `FEUP/Dissertations`
- `Research/Papers`
- etc.

#### `label-recent`
Classify recent emails and apply topic labels to them in Gmail.

```bash
poetry run gmail-classifier label-recent --limit 10 --apply
```

**Options:**
- `--limit` (default: 10): Number of messages to process
- `--query` (default: `"in:inbox -label:AI/Classified"`): Gmail search query
- `--apply` (default: False): If set, actually apply labels to Gmail messages

When `--apply` is used, emails are labeled with both the topic label and an `AI/Classified` marker to avoid reprocessing.

## Classification Schema

### Topics

The classifier can assign emails to these topic categories:

- **FEUP Management**: M.EIC, L.EIC, MECD, DEI
- **FEUP Teaching**: LTW, LDTS, FCED, Other
- **FEUP Administration**: Dissertations, Admin, General
- **Research**: Papers, PhD, Conferences, Citations, Other
- **Projects**: JurisVis, Other
- **Newsletters**: ACM, U.Porto, Other
- **Services**: Security, Accounts
- **Low Priority**: Academic Solicitation, Commercial, Spam
- **Other**: Fallback category

### Status

- **Action**: Requires a response or action from the recipient
- **Waiting**: Recipient has acted; waiting for external response
- **Reference**: Informational material for later reference
- **None**: Low-value informational content

### Kind

- **human**: Written by a person
- **institutional**: Organizational or administrative
- **newsletter**: Recurring mass informational publication
- **academic-solicitation**: Unsolicited academic invitations
- **commercial**: Marketing or sales
- **automated-important**: Automated service notifications (security, account, etc.)

## Workflow Example

A typical workflow might be:

1. **Evaluate** historical emails to see how the classifier performs:
   ```bash
   poetry run gmail-classifier evaluate --limit 300 --output results.csv
   ```

2. **Review** the CSV to check classification quality:
   ```bash
   poetry run gmail-classifier show "FEUP/Teaching/LTW" --input results.csv
   ```

3. **Create** Gmail labels once you're satisfied with the results:
   ```bash
   poetry run gmail-classifier create-labels
   ```

4. **Start classifying** and applying labels to incoming mail:
   ```bash
   poetry run gmail-classifier label-recent --limit 50 --apply
   ```

5. **Periodically** process new unclassified emails:
   ```bash
   poetry run gmail-classifier label-recent --limit 10 --apply
   ```

## Configuration

### Ollama Model

To use a different Ollama model, edit `gmail_classifier/ollama.py` and change the `MODEL` variable:

```python
MODEL = "gemma3:12b"  # Change this
```

### Gmail Query Syntax

The `--query` parameter uses [Gmail search operators](https://support.google.com/mail/answer/7190?hl=en):

- `in:inbox` - Messages in inbox
- `in:all` - All messages
- `newer_than:180d` - Newer than 180 days
- `is:unread` - Unread messages
- `label:archive` - Messages in a label
- `-label:AI/Classified` - Exclude classified messages

You can combine these with `AND` (space) and `OR` (pipe `|`).

## Troubleshooting

### OAuth Connection Issues

If you get an OAuth error, delete `token.json` and run a command again. You'll be prompted to authorize the app in your browser.

```bash
rm token.json
poetry run gmail-classifier test-gmail
```

### Ollama Connection Issues

Make sure Ollama is running:

```bash
ollama serve
```

In another terminal, verify the connection:

```bash
curl http://localhost:11434/api/tags
```

### Missing Gemma3 Model

Install the required model:

```bash
ollama pull gemma3:12b
```

## Development

The project uses Python 3.12+ features. Format code with your preferred formatter (e.g., Black, Ruff).

## License

This project is personal work. Modify as needed for your own use.

## Author

André Restivo (arestivo@fe.up.pt)
