import arxiv
import datetime
from dateutil import parser
import os
import argparse
from collections import defaultdict
from datetime import timezone

def get_output_filename(start_date, end_date, base_dir='papers'):
    """Generate output filename with date range."""
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    return os.path.join(base_dir, f'cv_papers_{start_str}_to_{end_str}.md')

def get_cv_papers(past_days=3, max_results=1000):
    # Create a directory to store the papers if it doesn't exist
    if not os.path.exists('papers'):
        os.makedirs('papers')

    # Search for papers in the Computer Vision category
    search = arxiv.Search(
        query="cat:cs.CV",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    # First, find the most recent submission date
    latest_date = None
    for result in search.results():
        latest_date = result.published.date()
        break

    if latest_date is None:
        print("No papers found!")
        return None

    # Calculate the start date based on the latest date
    start_date = latest_date - datetime.timedelta(days=past_days)

    # Generate output filename
    output_file = get_output_filename(start_date, latest_date)

    # Create a file to store the results
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# Computer Vision Papers from arXiv\n\n")
        f.write(f"*Last {past_days} Days ({start_date} to {latest_date})*\n\n")
        f.write(f"*Maximum results: {max_results}*\n\n")
        f.write("*Note: All dates are in UTC (Coordinated Universal Time)*\n\n")
        f.write("---\n\n")

        # Store papers in a list to sort them
        papers = []
        daily_counts = defaultdict(int)
        
        for result in search.results():
            # arXiv API returns timestamps in UTC
            submission_date = result.published.date()
            
            # Include papers from the specified date range
            if start_date <= submission_date <= latest_date:
                papers.append({
                    'date': submission_date,
                    'title': result.title,
                    'authors': result.authors,
                    'summary': result.summary,
                    'url': result.entry_id,
                    'pdf_url': result.pdf_url
                })
                daily_counts[submission_date] += 1

        # Write daily summary
        f.write("## 📊 Daily Paper Count Summary\n\n")
        f.write("| Date (UTC) | Number of Papers |\n")
        f.write("|------------|-----------------|\n")
        for date in sorted(daily_counts.keys(), reverse=True):
            f.write(f"| {date} | {daily_counts[date]} |\n")
        f.write("\n---\n\n")

        # Sort papers by date (most recent first)
        papers.sort(key=lambda x: x['date'], reverse=True)

        # Write sorted papers to file
        for i, paper in enumerate(papers, 1):
            f.write(f"## 📄 Paper #{i}\n\n")
            f.write(f"### {paper['title']}\n\n")
            f.write(f"**Date (UTC):** {paper['date']}\n\n")
            f.write(f"**Authors:** {', '.join(author.name for author in paper['authors'])}\n\n")
            f.write("**Abstract:**\n\n")
            f.write(f"{paper['summary']}\n\n")
            f.write("**Links:**\n\n")
            f.write(f"- [arXiv Page]({paper['url']})\n")
            f.write(f"- [PDF]({paper['pdf_url']})\n\n")
            f.write("---\n\n")
    
    return output_file

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch Computer Vision papers from arXiv for the past N days from the most recent submission')
    parser.add_argument('--days', type=int, default=3,
                      help='Number of past days to fetch papers for (default: 3)')
    parser.add_argument('--max-results', type=int, default=500,
                      help='Maximum number of papers to fetch (default: 1000)')
    
    args = parser.parse_args()
    
    print(f"Fetching Computer Vision papers from arXiv...")
    print(f"Maximum results: {args.max_results}")
    output_file = get_cv_papers(args.days, args.max_results)
    if output_file:
        print(f"Done! Results saved to '{output_file}'") 