import urllib.request
import os
import time

def download_pieces():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets", "chess_pieces")
    os.makedirs(assets_dir, exist_ok=True)
    
    pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    name_map = {
        'wp': 'wP', 'wn': 'wN', 'wb': 'wB', 'wr': 'wR', 'wq': 'wQ', 'wk': 'wK',
        'bp': 'bP', 'bn': 'bN', 'bb': 'bB', 'br': 'bR', 'bq': 'bQ', 'bk': 'bK'
    }

    for p in pieces:
        url = f"https://images.chesscomfiles.com/chess-themes/pieces/neo/150/{p}.png"
        filepath = os.path.join(assets_dir, f"{name_map[p]}.png")
        print(f"Downloading {name_map[p]}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            time.sleep(0.1)
        except Exception as e:
            print(f"Failed to download {name_map[p]}: {e}")

if __name__ == "__main__":
    download_pieces()
    print("Done!")
