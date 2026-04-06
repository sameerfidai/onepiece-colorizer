import requests
from bs4 import BeautifulSoup
import os
import time
import io
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
client = genai.Client()

base_url = "https://tcbonepiecechapters.com"


def get_latest_chapter_url():
    print("Getting latest chapter url...")
    content = requests.get(f"{base_url}/mangas/5/one-piece")
    soup = BeautifulSoup(content.text, "html.parser")
    all_chapters = soup.find("div", class_="col-span-2")
    return base_url + all_chapters.find("a").get("href")


def get_page_urls(chapter_url):
    content = requests.get(chapter_url)
    soup = BeautifulSoup(content.text, "html.parser")
    title_tag = soup.find("h1", class_="text-lg md:text-2xl font-bold mt-8")
    title = title_tag.get_text().strip() if title_tag else "Unknown Chapter"
    print(f"Processing: {title}...")
    images = soup.find_all("img", class_="fixed-ratio-content")
    return [img.get("src") for img in images]


def process_page(index, link, links, black_and_white_folder, colored_folder):
    page_num = index + 1
    filename = f"page_{page_num:03d}.png"

    black_and_white_path = os.path.join(black_and_white_folder, filename)
    colored_path = os.path.join(colored_folder, filename)

    # skip if this page is already colored
    if os.path.exists(colored_path):
        print(f"Skipping Page {page_num}, already colored.")
        return

    print(f"Processing Page {page_num}/{len(links)}...")

    try:
        # download black and white image
        img_data = requests.get(link).content
        black_and_white_image = Image.open(io.BytesIO(img_data))
        black_and_white_image.save(black_and_white_path)

        # adjust as needed
        prompt = (
            "Task: Colorize this One Piece manga page in a high-quality anime style matching the Toei Animation One Piece series.\n\n"
            "CRITICAL RULE: You are ONLY adding color to an existing image. Do not redraw, reshape, or alter ANY lines, "
            "panel borders, speech bubbles, text, or composition in any way. The original black and white line art "
            "must remain completely unchanged. Treat this exactly like a human colorist filling in color — "
            "the pencil lines are sacred and must not be touched.\n\n"
            "Colorization Rules:\n"
            "1. This is from the One Piece manga. Characters may be wearing new outfits or have new designs due to a new arc — "
            "do not treat a new costume as a new character. Use facial features, hair style, and body type to identify who they are.\n"
            "2. Once identified, apply their canonical One Piece color scheme to their skin, hair, and any consistent features. "
            "Adapt their outfit colors to fit their personality and role (hero, villain, ally).\n"
            "3. For any truly unrecognized characters, infer their color scheme from context — "
            "villains get darker muted tones, allies get warmer brighter tones.\n"
            "4. Use vibrant saturated colors for environments, skies, and seas consistent with One Piece's world.\n"
            "5. Apply cel-shading with sharp shadows and highlights matching Toei Animation's style.\n"
            "6. The final result must look like an official colored page from a One Piece Shonen Jump special edition.\n\n"
            "FINAL CHECK: Before outputting, verify that every line, panel border, and piece of text from the "
            "original image is still in the exact same position. If anything was redrawn, start over."
        )

        # generate the colored content
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt, black_and_white_image],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=0.1,
            ),
        )

        # save the colored image from the response
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                colored_img = part.as_image()
                colored_img.save(colored_path)

        # sleep to avoid hitting API rate limits
        time.sleep(2)

    except Exception as e:
        print(f"Error on page {page_num}: {e}")
        return


def download_and_colorize(links):
    black_and_white_folder = "raw_bw"
    colored_folder = "colored"
    os.makedirs(black_and_white_folder, exist_ok=True)
    os.makedirs(colored_folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                process_page, i, link, links, black_and_white_folder, colored_folder
            )
            for i, link in enumerate(links)
        ]

    print("Done...")


def build_pdf():
    colored_folder = "colored"
    output_path = "one_piece_latest.pdf"

    image_files = sorted(os.listdir(colored_folder))
    images = [
        Image.open(os.path.join(colored_folder, f)).convert("RGB") for f in image_files
    ]

    if not images:
        print("No colored images found.")
        return

    images[0].save(output_path, save_all=True, append_images=images[1:])
    print(f"PDF saved to {output_path}")


if __name__ == "__main__":
    latest_url = get_latest_chapter_url()
    page_links = get_page_urls(latest_url)
    download_and_colorize(page_links)
    build_pdf()
