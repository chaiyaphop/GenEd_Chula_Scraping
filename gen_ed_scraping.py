import logging
import os
import pandas as pd
import time
from contextlib import contextmanager
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from tqdm import tqdm
from typing import List, Dict


# Configuration and Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@contextmanager
def get_driver(headless: bool = True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def get_course_codes(
    course_codes_file_path: str = 'course_codes_2024.csv'
) -> List[str]:
    df = pd.read_csv(course_codes_file_path, dtype=str)
    return df['course_code'].tolist()


def scrape_gen_ed_courses(course_codes: List[str]) -> Dict[str, Dict[str, str]]:
    result = {}
    with get_driver() as driver:
        for course_code in tqdm(course_codes, desc="Scraping General Education Courses"):
            logging.info(f"Scraping course code: {course_code}")

            result[course_code] = {}
            langs = ["en", "th"]
            for lang in langs:
                url = f"https://gened.chula.ac.th/{lang}/course/gened/{course_code}"
                driver.get(url)
                time.sleep(0.5)  # Wait for the page to load
                try:
                    def get_text_element(
                        xpath: str,
                        field_name: str = "",
                        driver=driver
                    ) -> str:
                        try:
                            return driver.find_element(by=By.XPATH, value=xpath).text.strip()
                        except:
                            logging.warning(f"{field_name} not found for course {course_code}")
                            return "N/A"

                    def get_text_elements(
                        xpath: str,
                        field_name: str = "",
                        driver=driver
                    ) -> List[str]:
                        try:
                            elements = driver.find_elements(by=By.XPATH, value=xpath)
                            return [el.text.strip() for el in elements if el.text.strip()] if elements else ["N/A"]
                        except:
                            logging.warning(f"{field_name} not found for course {course_code}")
                            return ["N/A"]

                    if lang == "en":
                        code = get_text_elements("/html/body/div[2]/div/div/div[1]/div[1]/p[1]", "Course Code")[0].split()[0]
                        full_title_en = " ".join(get_text_elements("/html/body/div[2]/div/div/div[1]/div[1]/p[1]", "Full Title EN")[0].split()[1:])
                        short_title = get_text_element("/html/body/div[2]/div/div/div[1]/div[1]/p[2]", "Short Title")
                        description = get_text_element("/html/body/div[2]/div/div/div[3]/p[2]", "Description")
                        faculty = get_text_element("/html/body/div[2]/div/div/div[2]/div[1]/p[2]", "Faculty")
                        category = "; ".join(get_text_elements("/html/body/div[2]/div/div/div[2]/div[2]//p[contains(@class, 'body1')]", "Category"))
                        credit = get_text_elements("/html/body/div[2]/div/div/div[2]/div[4]/p[2]", "Credit")[0]
                        academic_year = get_text_elements("/html/body/div[2]/div/div/div[4]/p[2]/span[1]", "Academic Year")[0].split()[-1]
                        semester = get_text_element("/html/body/div[2]/div/div/div[4]/p[2]/span[2]", "Semester")
                        instructor_en = "; ".join([name.lstrip('- ').strip() for name in get_text_elements("/html/body/div[2]/div/div/div[2]/div[3]//span", "Instructors EN") if name])

                        # class schedule
                        try:
                            base_xpath = "/html/body/div[2]/div/div/div[4]"
                            schedule_rows_xpath = f"{base_xpath}/p[.//span[contains(text(), 'sec')]]"
                            schedule_rows = driver.find_elements(by=By.XPATH, value=schedule_rows_xpath)
                            class_schedule_list = []
                            for row in schedule_rows:
                                schedule_span = get_text_element(".//span[contains(text(), 'sec')]", "Schedule Span", row)
                                class_schedule_list.append(schedule_span)
                            class_schedule = "; ".join(class_schedule_list)
                        except:
                            logging.warning(f"Class schedule not found for course {course_code}")
                            return "N/A"

                        result[course_code].update({
                            "course_code": code if code else "N/A",
                            "short_title": short_title if short_title else "N/A",
                            "description": description if description else "N/A",
                            "faculty": faculty if faculty else "N/A",
                            "category": category if category else "N/A",
                            "credit": credit if credit else "N/A",
                            "academic_year": academic_year if academic_year else "N/A",
                            "semester": semester if semester else "N/A",
                            "class_schedule": class_schedule if class_schedule else "N/A",
                            "full_title_en": full_title_en if full_title_en else "N/A",
                            "instructor_en": instructor_en if instructor_en else "N/A"
                        })

                        logging.info(f"result so far: {result[course_code]}")

                    else:  # lang == "th"
                        full_title_th = " ".join(get_text_elements("/html/body/div[2]/div/div/div[1]/div[1]/p[1]", "Full Title TH")[0].split()[1:])
                        instructor_th = "; ".join([name.lstrip('- ').strip() for name in get_text_elements("/html/body/div[2]/div/div/div[2]/div[3]//span", "Instructors TH") if name])

                        result[course_code].update({
                            "full_title_th": full_title_th,
                            "instructor_th": instructor_th
                        })

                except WebDriverException as e:
                    logging.error(f"Error scraping {course_code}: {e}")
    return result


if __name__ == '__main__':
    start_time = datetime.now()
    logging.info(f"Program started at {start_time}")

    course_codes_file_path = 'course_codes_2024.csv'
    course_codes = get_course_codes(course_codes_file_path)
    scraped_data = scrape_gen_ed_courses(course_codes)

    output_dir = 'scraped_data'
    output_filename = 'gen_ed_courses_scraped.csv'
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, output_filename)
    pd.DataFrame.from_dict(scraped_data, orient='index').to_csv(output_file_path, index=False, quoting=1)
    logging.info(f"Scraped data saved to {output_file_path}")

    end_time = datetime.now()
    logging.info(f"Program ended at {end_time}")
    logging.info(f"Total duration: {(end_time - start_time).seconds} seconds")
