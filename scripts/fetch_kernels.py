import csv
import json
import sys
from kaggle.api.kaggle_api_extended import KaggleApi

sys.stdout.reconfigure(encoding='utf-8')

def main():
    api = KaggleApi()
    api.authenticate()

    print("=== QUERYING KAGGLE PUBLIC NOTEBOOKS ===")
    
    # 1. By Vote Count
    kernels_votes = api.kernels_list(competition='google-verifiable-quantum-circuit-compilation', sort_by='voteCount', page_size=100)
    print(f"Total returned by voteCount: {len(kernels_votes)}")

    # 2. By Score Descending (if available) / Hotness / Date Created
    kernels_hot = api.kernels_list(competition='google-verifiable-quantum-circuit-compilation', sort_by='hotness', page_size=100)
    print(f"Total returned by hotness: {len(kernels_hot)}")

    kernels_date = api.kernels_list(competition='google-verifiable-quantum-circuit-compilation', sort_by='dateCreated', page_size=100)
    print(f"Total returned by dateCreated: {len(kernels_date)}")

    # Combine unique kernels by ref
    all_kernels = {}
    for k in kernels_votes + kernels_hot + kernels_date:
        ref = getattr(k, 'ref', None)
        if ref and ref not in all_kernels:
            all_kernels[ref] = k

    print(f"\nUnique public kernels discovered: {len(all_kernels)}")

    # Save to a structured JSON and print the top ones
    results = []
    for ref, k in all_kernels.items():
        title = getattr(k, 'title', '')
        author = getattr(k, 'author', '') or ref.split('/')[0]
        votes = getattr(k, 'total_votes', 0)
        views = getattr(k, 'total_views', 0)
        url = f"https://www.kaggle.com/code/{ref}"
        results.append({
            'ref': ref,
            'title': title,
            'author': author,
            'votes': votes,
            'views': views,
            'url': url
        })

    # Sort by votes descending
    results.sort(key=lambda x: x['votes'], reverse=True)

    with open('leaderboard_export/public_notebooks.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print("\n=== TOP 25 PUBLIC NOTEBOOKS BY VOTES ===")
    for i, r in enumerate(results[:25], 1):
        print(f"{i:2d}. [{r['votes']:3d} votes | {r['author']:<20}] {r['title']} -> {r['url']}")

if __name__ == '__main__':
    main()
