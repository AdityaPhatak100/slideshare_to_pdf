# SlideShare to PDF Converter

Convert SlideShare presentations to downloadable PDF files using this Python script.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Features

- Download a single slideshow using a slideshare URL.
- Download multiple slideshows in one go.

## Requirements

- Python 3.x
- [Requests](https://requests.readthedocs.io/en/latest/) library (install using `pip install requests`)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library (install using `pip install beautifulsoup4`)
- [Pillow](https://pillow.readthedocs.io/en/stable/) library (install using `pip install pillow`)



## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/AdityaPhatak100/slideshare_to_pdf.git
cd slideshare_to_pdf
```

## Usage
1. Downloading a single slideshow.
```bash
python main.py -l <SLIDESHARE URL>
```

2. Downloading multiple slideshows.
```bash
python main.py -m <TEXT FILE PATH>
```

(Sample text file format is included in the repository.)