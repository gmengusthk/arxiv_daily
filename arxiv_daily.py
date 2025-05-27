import arxiv
import datetime
from dateutil import parser
import os
import argparse
from collections import defaultdict

def get_output_filename(start_date, end_date, base_dir='papers'):
    """Generate output filename with date range."""
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    return os.path.join(base_dir, f'cv_papers_{start_str}_to_{end_str}.md')

def get_cv_papers(past_days=3):
    # Create a directory to store the papers if it doesn't exist
    if not os.path.exists('papers'):
        os.makedirs('papers')

    # Calculate the date n days ago
    today = datetime.datetime.now().date()
    past_date = today - datetime.timedelta(days=past_days)

    # Generate output filename
    output_file = get_output_filename(past_date, today)

    # Search for papers in the Computer Vision category
    search = arxiv.Search(
        query="cat:cs.CV",
        max_results=1000,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    # Create a file to store the results
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# Computer Vision Papers from arXiv\n\n")
        f.write(f"*Last {past_days} Days ({past_date} to {today})*\n\n")
        f.write("---\n\n")

        # Store papers in a list to sort them
        papers = []
        daily_counts = defaultdict(int)
        
        for result in search.results():
            submission_date = result.published.date()
            
            # Include papers from the specified past days
            if submission_date >= past_date:
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
        f.write("| Date | Number of Papers |\n")
        f.write("|------|-----------------|\n")
        for date in sorted(daily_counts.keys(), reverse=True):
            f.write(f"| {date} | {daily_counts[date]} |\n")
        f.write("\n---\n\n")

        # Sort papers by date (most recent first)
        papers.sort(key=lambda x: x['date'], reverse=True)

        # Write sorted papers to file
        for i, paper in enumerate(papers, 1):
            f.write(f"## 📄 Paper #{i}\n\n")
            f.write(f"### {paper['title']}\n\n")
            f.write(f"**Date:** {paper['date']}\n\n")
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
    parser = argparse.ArgumentParser(description='Fetch Computer Vision papers from arXiv for the past N days')
    parser.add_argument('--days', type=int, default=3,
                      help='Number of past days to fetch papers for (default: 3)')
    
    args = parser.parse_args()
    
    print(f"Fetching Computer Vision papers from arXiv from the past {args.days} days...")
    output_file = get_cv_papers(args.days)
    print(f"Done! Results saved to '{output_file}'") 