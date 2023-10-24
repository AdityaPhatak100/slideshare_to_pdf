import math
import requests
import sys
import os
import time
import shutil
import argparse
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image
from multiprocessing import Process


TEMP_IMAGES_PATH = "./TEMP_IMAGES_FOR_PPT"
NUM_OF_PROCESSES = os.cpu_count() or 4


def get_image_links_from_url(url: str) -> list[str]:
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")
    sources = soup.find_all("source")

    image_links = [image.get("srcset").split(", ")[-1] for image in sources]

    return image_links


def create_temp_folder() -> None:
    if not os.path.isdir(TEMP_IMAGES_PATH):
        os.mkdir(TEMP_IMAGES_PATH)
    else:
        delete_temp_files()
        create_temp_folder()


def get_images(links: list[str], image_start_idx: int) -> None:
    for itr, link in enumerate(links):
        urllib.request.urlretrieve(
            link.split(" ")[0], f"{TEMP_IMAGES_PATH}/{itr + image_start_idx}.jpg"
        )


def create_processes(links: list[str]) -> None:
    links_per_process = math.ceil(len(links) / NUM_OF_PROCESSES)
    processes = []

    for i in range(1, NUM_OF_PROCESSES + 1):
        if i != NUM_OF_PROCESSES:
            process_args = [
                links[links_per_process * (i - 1) : links_per_process * i],
                links_per_process * (i - 1),
            ]
        else:
            process_args = [
                links[links_per_process * (i - 1) :],
                links_per_process * (i - 1),
            ]

        processes.append(
            Process(
                target=get_images,
                args=process_args,
            )
        )

    run_processes(processes)


def run_processes(processes: list[Process]) -> None:
    for process in processes:
        process.start()

    for process in processes:
        process.join()


# append them into a single file
def generate_pdf_from_images(url: str) -> None:
    pdf_path = f"./{url.split('/')[-1].capitalize()}.pdf"

    images = [
        Image.open(f"{TEMP_IMAGES_PATH}/" + img) for img in os.listdir(TEMP_IMAGES_PATH)
    ]

    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )

    delete_temp_files()


def delete_temp_files():
    if os.path.isdir(TEMP_IMAGES_PATH):
        shutil.rmtree(TEMP_IMAGES_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Slideshare to PPT",
        usage="Converts slideshare links into PPTs. It can accept single file, as well as a .txt file containing multiple slideshare.net links, as an input.",
    )

    parser.add_argument(
        "-m", help="Specify a text file path containing multiple slideshare links."
    )
    parser.add_argument("-l", help="Specify a single slideshare link.")

    args = parser.parse_args()

    if args.l and args.m:
        print(
            "Use either a link (-l) or a text file (-m). Cannot use both at the same time."
        )
        exit(0)

    if not args.l and not args.m:
        print(
            """Mention a slideshare url or a text file with multiple slideshare urls

For example,
>>> python main.py -l "SLIDESHARE URL" 
                OR
>>> python main.py -m "TEXT FILE PATH"
              """
        )
        

    if args.l:
        url = args.l

        image_links = get_image_links_from_url(url)
        create_temp_folder()
        create_processes(image_links)
        # st1 = time.perf_counter()
        generate_pdf_from_images(url)

    if args.m:
        with open(args.m, "r") as file:
            for url in file.readlines():
                url = url.strip()
                image_links = get_image_links_from_url(url)
                create_temp_folder()
                create_processes(image_links)
                generate_pdf_from_images(url)
