# GenEd_Chula_Scraping: Scraping Chulalongkorn University's General Education Center Website Using Python

**GenEd_Chula_Scraping** is a Python script for extracting course information from Chulalongkorn University's General Education Center Website using Selenium.

## Features

* Supports scraping for general education courses
* Saves results to CSV
* Headless Chrome browser support

---

## ✅ Prerequisites

* Google Chrome **v120.0.6099.130** (or compatible)
* Python **v3.11.3**
* ChromeDriver that matches your Chrome version (must be in PATH)

---

## ⚙️ Setup Instructions

<details>
<summary><strong>Local Python</strong></summary>

Install dependencies using:

```bash
source setup.sh
```

Or manually:

```bash
pip install -r requirements.txt
```

Make sure you have:

* Python **3.11**
* Google Chrome and matching **ChromeDriver** in your PATH

</details>

---

## ▶️ How to Run

<details>
<summary><strong>Run via Python</strong></summary>

```bash
python gen_ed_scraping.py
```

</details>

---

## 📁 Output Example

```plaintext
scraped_data/
└── gen_ed_courses_scraped.csv
```

---

## 📦 Project Structure

```plaintext
├── .gitignore
├── gen_ed_scraping.py
├── scraped_data/
├── README.md
├── requirements.txt
└── setup.sh
```

---

## 🧑‍💻 Author

Chaiyaphop Jamjumrat

*Last updated: November 27, 2025*