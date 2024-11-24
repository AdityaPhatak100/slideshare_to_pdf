import os
import re
import math
import shutil
import time
import urllib
import requests
from PIL import Image
from bs4 import BeautifulSoup
from threading import Thread


class SlideShareToPDF:
    def __init__(self, temp_images_path, num_of_threads) -> None:
        self.TEMP_IMAGES_PATH = temp_images_path
        self.NUM_OF_THREADS = num_of_threads

    def get_image_links_from_url(self, url: str) -> list[str]:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")
        sources = soup.find_all("img", {"id": re.compile("^slide-image-[0-9]*")})
        image_links = [image.get("srcset").split(", ")[-1] for image in sources]

        return image_links

    def create_temp_folder(self) -> None:
        if not os.path.isdir(self.TEMP_IMAGES_PATH):
            os.mkdir(self.TEMP_IMAGES_PATH)
        else:
            self.delete_temp_files()
            self.create_temp_folder()

    def delete_temp_files(self):
        if os.path.isdir(self.TEMP_IMAGES_PATH):
            shutil.rmtree(self.TEMP_IMAGES_PATH)

    def get_images(self, links: list[str], image_start_idx: int) -> None:
        for itr, link in enumerate(links):
            try:
                urllib.request.urlretrieve(
                    link.split(" ")[0],
                    f"{self.TEMP_IMAGES_PATH}/{itr + image_start_idx}.jpg",
                )
            except urllib.error.HTTPError:
                print(f"Slide number {itr + image_start_idx + 1} was not found")

    def create_threads(self, links: list[str]) -> None:
        links_per_thread = math.ceil(len(links) / self.NUM_OF_THREADS)
        threads = []

        for i in range(1, self.NUM_OF_THREADS + 1):
            if i != self.NUM_OF_THREADS:
                thread_args = [
                    links[links_per_thread * (i - 1) : links_per_thread * i],
                    links_per_thread * (i - 1),
                ]
            else:
                thread_args = [
                    links[links_per_thread * (i - 1) :],
                    links_per_thread * (i - 1),
                ]

            threads.append(
                Thread(
                    target=self.get_images,
                    args=thread_args,
                )
            )

        self.run_threads(threads)

    def run_threads(self, threads: list[Thread]) -> None:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def generate_pdf_from_images(self, url: str) -> None:
        pdf_path = f"./{url.split('/')[-1].capitalize()}.pdf"

        images = [
            Image.open(f"{self.TEMP_IMAGES_PATH}/" + img)
            for img in os.listdir(self.TEMP_IMAGES_PATH)
        ]

        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )

        self.delete_temp_files()

    def download_pdf(self, url: str) -> None:
        url = url.strip()
        print("URL:", url)
        st = time.perf_counter()
        image_links = self.get_image_links_from_url(url)
        print("Total number of slides:", len(image_links))
        self.create_temp_folder()
        print("Downloading slides...")
        self.create_threads(image_links)
        print("Generating PDF...")
        self.generate_pdf_from_images(url)
        print(
            f"Time taken: {round(time.perf_counter() - st, 3)}s\n",
        )


if __name__ == "__main__":
    TEMP_IMAGES_PATH = "./TEMP_IMAGES_FOR_PPT"
    NUM_OF_THREADS = (os.cpu_count() or 4) * 8

    TEST_LINK = (
        "https://www.slideshare.net/bcbbslides/introduction-to-git-and-github-72514916"
    )

    obj = SlideShareToPDF(TEMP_IMAGES_PATH, NUM_OF_THREADS)

    st = time.perf_counter()
    obj.download_pdf(TEST_LINK)
    print(round(time.perf_counter() - st, 3))
