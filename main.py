import os
import argparse
import time
from slidesharetopdf import SlideShareToPDF

TEMP_IMAGES_PATH = "./TEMP_IMAGES_FOR_PDF"
NUM_OF_THREADS = (os.cpu_count() or 4) * 4


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
            """
            Mention a slideshare url or a text file with multiple slideshare urls
            For example,
                >>> python main.py -l "SLIDESHARE URL" 
                                OR
                >>> python main.py -m "TEXT FILE PATH"
              """
        )

    obj = SlideShareToPDF(TEMP_IMAGES_PATH, NUM_OF_THREADS)

    if args.l:
        url = args.l
        obj.download_pdf(url)

    pdfs_count = 0

    if args.m:
        with open(args.m, "r") as file:
            total_time = time.perf_counter()

            for url in file.readlines():
                pdfs_count += 1
                obj.download_pdf(url)

            print("Total number of PDFs printed:", pdfs_count)
            print("Total time taken:", round(time.perf_counter() - total_time, 3))
