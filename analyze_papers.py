import os
import json
from datetime import datetime
import argparse
from typing import List, Dict
from openai import OpenAI
import random
from dotenv import load_dotenv
import glob
import re

def find_latest_arxiv_output(base_dir: str = 'papers') -> str:
    """Find the latest output file from arxiv_daily.py."""
    # Pattern to match cvpr_papers_YYYY-MM-DD_to_YYYY-MM-DD.md
    pattern = os.path.join(base_dir, 'cvpr_papers_*_to_*.md')
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError("No arxiv daily output files found in the papers directory.")
    
    # Sort files by the end date in the filename
    def get_end_date(filename):
        match = re.search(r'to_(\d{4}-\d{2}-\d{2})\.md$', filename)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        return datetime.min
    
    latest_file = max(files, key=get_end_date)
    return latest_file

def load_config():
    """Load configuration from environment variables or .env file."""
    load_dotenv()
    
    config = {
        'api_key': os.getenv('AI_API_KEY'),
        'model': os.getenv('AI_MODEL', 'gpt-4o-mini'),
        'base_url': os.getenv('AI_BASE_URL', 'https://aihubmix.com/v1'),
        'research_topics': os.getenv('RESEARCH_TOPICS')
    }
    
    if not config['api_key']:
        raise ValueError("AI_API_KEY environment variable is not set. Please set it in .env file or environment.")
    
    if not config['research_topics']:
        raise ValueError("RESEARCH_TOPICS environment variable is not set. Please set it in .env file or environment.")
    
    return config

def load_papers(md_file: str) -> List[Dict]:
    """Load papers from the markdown file and convert to structured format."""
    papers = []
    current_paper = {}
    
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if line.startswith('## 📄 Paper #'):
            if current_paper:
                papers.append(current_paper)
            current_paper = {'number': line.split('#')[1].strip()}
        elif line.startswith('### '):
            current_paper['title'] = line[4:].strip()
        elif line.startswith('**Date:**'):
            current_paper['date'] = line[9:].strip()
        elif line.startswith('**Authors:**'):
            current_paper['authors'] = line[12:].strip()
        elif line.startswith('**Abstract:**'):
            current_paper['abstract'] = ''
        elif line.startswith('**Links:**'):
            current_paper['abstract'] = current_paper['abstract'].strip()
        elif line.startswith('- [arXiv Page]'):
            current_paper['arxiv_url'] = line[line.find('(')+1:line.find(')')]
        elif line.startswith('- [PDF]'):
            current_paper['pdf_url'] = line[line.find('(')+1:line.find(')')]
        elif current_paper.get('abstract') is not None and line and not line.startswith('---'):
            current_paper['abstract'] += line + ' '
    
    if current_paper:
        papers.append(current_paper)
    
    return papers

def parse_ai_response(response_text: str) -> Dict:
    """Parse the AI response from structured text format."""
    lines = response_text.strip().split('\n')
    result = {
        'relevant': False,
        'reason': '',
        'topics': []
    }
    
    for line in lines:
        line = line.strip()
        if line.startswith('RELEVANT:'):
            result['relevant'] = line[9:].strip().lower() == 'yes'
        elif line.startswith('REASON:'):
            result['reason'] = line[7:].strip()
        elif line.startswith('TOPICS:'):
            topics = line[7:].strip()
            if topics:
                result['topics'] = [t.strip() for t in topics.split(',')]
    
    return result

def analyze_papers(papers: List[Dict], research_topics: List[str], config: Dict) -> Dict:
    """Analyze papers using AI to find relevant ones based on research topics."""
    client = OpenAI(
        base_url=config['base_url'],
        api_key=config['api_key'],
    )
    relevant_papers = []
    total_papers = len(papers)
    
    print(f"\nStarting analysis of {total_papers} papers...")
    
    for i, paper in enumerate(papers, 1):
        # Create prompt for AI analysis
        prompt = f"""Given the following research topics:
{', '.join(research_topics)}

And this paper:
Title: {paper['title']}
Abstract: {paper['abstract']}

Analyze if this paper is relevant to any of the research topics. Provide your response in the following format:

RELEVANT: [yes/no]
REASON: [brief explanation of why it's relevant or not]
TOPICS: [comma-separated list of relevant topics from the provided list]
"""
        
        try:
            print(f"\nAnalyzing paper {i}/{total_papers}: {paper['title']}")
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research paper analyzer. Provide responses in a structured format with RELEVANT, REASON, and TOPICS sections."
                    },    
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                seed=random.randint(1, 1000000000)
            )
            
            response_text = response.choices[0].message.content
            print("AI Response:")
            print(response_text)
            print('-'*50)
            
            analysis = parse_ai_response(response_text)
            
            if analysis['relevant']:
                paper['relevance'] = analysis
                relevant_papers.append(paper)
                print(f"✓ Paper {i} is relevant")
            else:
                print(f"✗ Paper {i} is not relevant")
                
        except Exception as e:
            print(f"Error analyzing paper {i}: {str(e)}")
            continue
    
    print(f"\nAnalysis complete! Found {len(relevant_papers)} relevant papers out of {total_papers} total papers.")
    
    return {
        'total_papers': total_papers,
        'relevant_papers': relevant_papers,
        'relevance_count': len(relevant_papers)
    }

def generate_report(analysis: Dict, research_topics: List[str], output_file: str):
    """Generate a markdown report of the analysis."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# AI Analysis of CVPR Papers\n\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## Research Topics\n\n")
        for topic in research_topics:
            f.write(f"- {topic}\n")
        f.write("\n")
        
        f.write("## Summary\n\n")
        f.write(f"- Total papers analyzed: {analysis['total_papers']}\n")
        f.write(f"- Relevant papers found: {analysis['relevance_count']}\n")
        f.write(f"- Relevance rate: {(analysis['relevance_count']/analysis['total_papers']*100):.1f}%\n\n")
        
        f.write("## Relevant Papers\n\n")
        for paper in analysis['relevant_papers']:
            f.write(f"### {paper['title']}\n\n")
            f.write(f"**Date:** {paper['date']}\n\n")
            f.write(f"**Authors:** {paper['authors']}\n\n")
            f.write("**Relevant Topics:**\n")
            for topic in paper['relevance']['topics']:
                f.write(f"- {topic}\n")
            f.write("\n")
            f.write("**Reason for Relevance:**\n")
            f.write(f"{paper['relevance']['reason']}\n\n")
            f.write("**Abstract:**\n")
            f.write(f"{paper['abstract']}\n\n")
            f.write("**Links:**\n")
            f.write(f"- [arXiv Page]({paper['arxiv_url']})\n")
            f.write(f"- [PDF]({paper['pdf_url']})\n\n")
            f.write("---\n\n")

def get_output_filename(base_dir: str = 'papers') -> str:
    """Generate output filename with current date."""
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(base_dir, f'analyzed_papers_{today}.md')

def main():
    parser = argparse.ArgumentParser(description='Analyze CVPR papers using AI')
    parser.add_argument('--input', type=str, default=None,
                      help='Input markdown file with papers (default: latest arxiv daily output)')
    parser.add_argument('--output', type=str, default=None,
                      help='Output markdown file for analysis (default: papers/analyzed_papers_YYYY-MM-DD.md)')
    parser.add_argument('--topics', type=str, default=None,
                      help='Comma-separated list of research topics (default: from environment variable)')
    
    args = parser.parse_args()
    
    # Set default input filename if not provided
    if args.input is None:
        try:
            args.input = find_latest_arxiv_output()
            print(f"Using latest arxiv daily output: {args.input}")
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            print("Please run arxiv_daily.py first or specify an input file with --input")
            return
    
    # Set default output filename if not provided
    if args.output is None:
        args.output = get_output_filename()
    
    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print(f"Error: {str(e)}")
        return
    
    # Load papers
    print("Loading papers...")
    papers = load_papers(args.input)
    
    # Parse research topics
    research_topics = [topic.strip() for topic in (args.topics or config['research_topics']).split(',')]
    
    # Analyze papers
    print("Analyzing papers with AI...")
    analysis = analyze_papers(papers, research_topics, config)
    
    # Generate report
    print("Generating analysis report...")
    generate_report(analysis, research_topics, args.output)
    
    print(f"Analysis complete! Check {args.output} for results.")

if __name__ == "__main__":
    main() 