# ArXiv Daily CV Paper Analyzer

This project automatically fetches and analyzes Computer Vision papers from arXiv using AI to identify papers relevant to your research interests.

## Features

- Automatically fetches Computer Vision papers from arXiv
- Uses AI to analyze papers and identify relevant ones based on your research topics
- Generates a detailed markdown report with analysis results
- Supports custom research topics and filtering
- Progress tracking during analysis
- Secure API key management
- Date-stamped output files for easy tracking
- Automatic detection of latest paper fetch results

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/arxiv-daily.git
cd arxiv-daily
```

2. Create and activate a conda environment:
```bash
# Create a new conda environment
conda create -n arxiv-daily python=3.10

# Activate the environment
conda activate arxiv-daily
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Copy `env.template` to `.env`:
     ```bash
     cp env.template .env
     ```
   - Edit `.env` and add your configuration:
     ```
     # AI API Configuration
     AI_API_KEY=your_api_key_here
     AI_MODEL=your_ai_model
     AI_BASE_URL=your_ai_url

     # Research Topics Configuration
     RESEARCH_TOPICS=computer vision,deep learning,object detection
     ```

## Usage

1. First, fetch the papers:
```bash
python arxiv_daily.py --days 3
```
This will create a file named `papers/cv_papers_YYYY-MM-DD_to_YYYY-MM-DD.md` containing the fetched papers.

2. Then analyze the papers:
```bash
# Using topics from .env file
python analyze_papers.py

# Or specify topics directly
python analyze_papers.py --topics "computer vision,deep learning,object detection"
```
This will automatically use the latest fetched papers and create a file named `papers/analyzed_papers_YYYY-MM-DD.md` containing the analysis results.

### Command Line Arguments

For `arxiv_daily.py`:
- `--days`: Number of past days to fetch papers for (default: 3)

For `analyze_papers.py`:
- `--input`: Input markdown file with papers (default: latest arxiv daily output)
- `--output`: Output markdown file for analysis (default: papers/analyzed_papers_YYYY-MM-DD.md)
- `--topics`: Comma-separated list of research topics (default: from environment variable)

## Output

The scripts generate two types of markdown files:

1. Paper Fetching (`arxiv_daily.py`):
   - Filename format: `papers/cv_papers_YYYY-MM-DD_to_YYYY-MM-DD.md`
   - Contains the list of papers with their details
   - Includes a daily summary of paper counts

2. Paper Analysis (`analyze_papers.py`):
   - Filename format: `papers/analyzed_papers_YYYY-MM-DD.md`
   - Contains the analysis results including:
     - Summary of analysis results
     - List of relevant papers
     - Detailed analysis for each paper

## Environment Management

### Using Conda

```bash
# Create environment
conda create -n arxiv-daily python=3.10

# Activate environment
conda activate arxiv-daily
```

### Environment Variables

The project uses environment variables for configuration. You can set them in two ways:

1. Using the `.env` file (recommended):
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

2. Setting them directly in your shell, we are using OpenAI API:
   ```bash
   export AI_API_KEY=your_api_key_here
   export AI_MODEL=your_ai_model
   export AI_BASE_URL=your_ai_url
   export RESEARCH_TOPICS="computer vision,deep learning,object detection"
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 