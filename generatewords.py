from os.path import exists
import sys
import requests
from bs4 import BeautifulSoup

WORDS_FILE = "./words.txt"

def generate():
    if not exists(WORDS_FILE):
        print("Generating words.txt from kbbi.kamus.pelajar.id...")
        with open(WORDS_FILE, "w", encoding="utf-8") as file:
            for page_number in range(1, 285):
                url = f"http://kbbi.kamus.pelajar.id/daftar-kata?page={page_number}"

                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
                word_wrappers = soup.find_all("div", class_="flex-item")
                words = []

                for word_wrapper in word_wrappers:
                    word = word_wrapper.find("a").text
                    if len(word) == 5:
                        words.append(word)

                file.writelines(words)
                print(f"Fetching page {page_number}/284...", end="\r")
                sys.stdout.flush()
        print()

if __name__ == "__main__":
    generate()
