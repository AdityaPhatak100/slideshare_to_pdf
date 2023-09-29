import math
import requests
from bs4 import BeautifulSoup
import urllib.request
import os
from PIL import Image
import time
from multiprocessing import Process

IMAGES_PATH = "./slides"
NUM_OF_PROCESSES = int(os.cpu_count())
LINK = "https://www.slideshare.net/bcbbslides/introduction-to-git-and-github-72514916"


# get website data
def get_website_data(slideshow_link: str) -> list[str]:
    
    r = requests.get(slideshow_link)
    soup = BeautifulSoup(r.content, "html.parser")
    sources = soup.find_all("source")

    links = []

    for picture in sources:
        links.append(picture.get("srcset").split(", ")[-1])
    
    return links


# check if temporary folder exists
def generate_temp_folder() -> None:
    if not os.path.isdir(IMAGES_PATH):
        os.mkdir(IMAGES_PATH)
    

# download images - spawn multiple processes
def download_image(links: list[str], slide_number_start: int) -> None:
    for itr, link in enumerate(links):
        urllib.request.urlretrieve(link.split(" ")[0], f"{IMAGES_PATH}/{itr + slide_number_start}.jpg")


def generate_and_run_processes(links: list[str]) -> None:
    links_per_process = math.ceil(len(links) / NUM_OF_PROCESSES)
    processes = []

    for i in range(1, NUM_OF_PROCESSES + 1):
        if i != 8:
            processes.append(
                Process(
                    target=download_image,
                    args=(
                        links[links_per_process *
                              (i - 1): links_per_process * i],
                        links_per_process * (i - 1),
                    ),
                )
            )
        else:
            processes.append(
                Process(
                    target=download_image,
                    args=(
                        links[links_per_process * (i - 1):],
                        links_per_process * (i - 1),
                    ),
                )
            )

    for process in processes:
        process.start()

    for process in processes:
        process.join()

# append them into a single file
def generate_pdf_from_images() -> None:
    images = [Image.open(f"{IMAGES_PATH}/" + img)
              for img in os.listdir(IMAGES_PATH)]

    pdf_path = f"./{LINK.split('/')[-1].capitalize()}.pdf"

    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )


if __name__ == "__main__":
    st = time.perf_counter()

    links = get_website_data(LINK)
    generate_temp_folder()
    generate_and_run_processes(links)
    generate_pdf_from_images()
    
    

    print((time.perf_counter() - st))
