import math
import requests
import sys
import os
import time
import shutil
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
    
    
    """
    SAMPLE LINKS FOR TESTING:
    
    https://www.slideshare.net/bcbbslides/introduction-to-git-and-github-72514916
    https://www.slideshare.net/HubSpot/git-101-git-and-github-for-beginners
    https://www.slideshare.net/Simplilearn/git-tutorial-for-beginners-what-is-git-and-github-devops-tools-devops-tutorial-simplilearn
    https://www.slideshare.net/provat34/git-in-10-minutes-42712502
    https://www.slideshare.net/GHARSALLAHMouhamed/git-basics-60662778
    https://www.slideshare.net/SkanderHamza/git-training-v10-233478299
    https://www.slideshare.net/GameCraftBulgaria/github-basics
    https://www.slideshare.net/nilaybinjola/git-basic-crash-course
    https://www.slideshare.net/hanxue/github-git-training-slides-foundations
    https://www.slideshare.net/glen_a_smith/git-one-day-training-notes
    
    """
    
    url = sys.argv[1]

    st = time.perf_counter()

    image_links = get_image_links_from_url(url)
    create_temp_folder()
    create_processes(image_links)
    st1 = time.perf_counter()
    generate_pdf_from_images(url)
    print("Printing time: ", time.perf_counter() - st1)

    print((time.perf_counter() - st))
