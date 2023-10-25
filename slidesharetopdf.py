import os
import math
import shutil
import time
import urllib
import requests
from PIL import Image
from bs4 import BeautifulSoup
from multiprocessing import Process


class SlideShareToPDF:
    def __init__(self, temp_images_path, num_of_processes) -> None:
        self.TEMP_IMAGES_PATH = temp_images_path
        self.NUM_OF_PROCESSES = num_of_processes

    def get_image_links_from_url(self, url: str) -> list[str]:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")
        sources = soup.find_all("source")

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
                print("An Image was not found")

    def create_processes(self, links: list[str]) -> None:
        links_per_process = math.ceil(len(links) / self.NUM_OF_PROCESSES)
        processes = []

        for i in range(1, self.NUM_OF_PROCESSES + 1):
            if i != self.NUM_OF_PROCESSES:
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
                    target=self.get_images,
                    args=process_args,
                )
            )

        self.run_processes(processes)

    def run_processes(self, processes: list[Process]) -> None:
        for process in processes:
            process.start()

        for process in processes:
            process.join()

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

        image_links = self.get_image_links_from_url(url)
        self.create_temp_folder()
        self.create_processes(image_links)
        self.generate_pdf_from_images(url)


if __name__ == "__main__":
    TEMP_IMAGES_PATH = "./TEMP_IMAGES_FOR_PPT"
    NUM_OF_PROCESSES = os.cpu_count() or 4

    TEST_LINK = (
        "https://www.slideshare.net/bcbbslides/introduction-to-git-and-github-72514916"
    )

    obj = SlideShareToPDF(TEMP_IMAGES_PATH, NUM_OF_PROCESSES)

    st = time.perf_counter()
    obj.download_pdf(TEST_LINK)
    print(round(time.perf_counter() - st, 3))
