"""
Glassdoor Job Scraper (kerangka dasar)
---------------------------------------
CATATAN PENTING:
- Glassdoor punya proteksi anti-bot (Cloudflare, login wall, captcha) sehingga
  script ini bisa saja perlu penyesuaian dari waktu ke waktu (selector berubah,
  butuh login, butuh proxy, dll).
- Scraping otomatis berpotensi melanggar Terms of Service Glassdoor. Gunakan
  dengan tanggung jawab sendiri, batasi rate request, dan pertimbangkan
  menggunakan API resmi / layanan pihak ketiga (Apify, ScraperAPI, RapidAPI
  job-search API) untuk kebutuhan produksi/skala besar.
- Selalu cek robots.txt dan ToS terbaru sebelum menjalankan scraping.

Dependencies:
    pip install selenium webdriver-manager pandas --break-system-packages
"""

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(headless: bool = True):
    """Inisialisasi Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    # Kurangi jejak automation
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def close_popup_if_exists(driver):
    """Tutup modal login/signup yang sering muncul di Glassdoor."""
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[alt='Close']"))
        )
        close_btn.click()
    except TimeoutException:
        pass


def scrape_glassdoor_jobs(search_url: str, max_jobs: int = 30, headless: bool = True):
    """
    Scrape daftar lowongan kerja dari halaman pencarian Glassdoor.

    Args:
        search_url: URL hasil pencarian job di Glassdoor
                     (contoh: https://www.glassdoor.com/Job/indonesia-data-analyst-jobs-SRCH_IL.0,9_IN113_KO10,22.htm)
        max_jobs: jumlah maksimum lowongan yang ingin diambil
        headless: jalankan browser tanpa GUI

    Returns:
        list[dict] berisi data lowongan kerja
    """
    driver = init_driver(headless=headless)
    jobs_data = []

    try:
        driver.get(search_url)
        time.sleep(random.uniform(3, 5))
        close_popup_if_exists(driver)

        while len(jobs_data) < max_jobs:
            # Tunggu kartu lowongan muncul
            try:
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "li[data-test='jobListing']")
                    )
                )
            except TimeoutException:
                print("Tidak ada job card ditemukan, cek selector / captcha.")
                break

            for card in job_cards:
                if len(jobs_data) >= max_jobs:
                    break
                try:
                    card.click()
                    time.sleep(random.uniform(1.5, 3))

                    title = _safe_text(driver, "h1[id^='jd-job-title']")
                    company = _safe_text(driver, "div[class*='EmployerProfile'] span")
                    location = _safe_text(driver, "div[data-test='location']")
                    salary = _safe_text(driver, "div[data-test='detailSalary']")
                    description = _safe_text(driver, "div[class*='JobDetails_jobDescription']")

                    jobs_data.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "description": description,
                    })
                    print(f"[{len(jobs_data)}/{max_jobs}] {title} - {company}")

                except (NoSuchElementException, TimeoutException):
                    continue

            # Coba klik tombol "Next" untuk halaman berikutnya
            if len(jobs_data) < max_jobs:
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, "button[data-test='pagination-next']")
                    if next_btn.get_attribute("disabled"):
                        break
                    next_btn.click()
                    time.sleep(random.uniform(3, 5))
                except NoSuchElementException:
                    break

    finally:
        driver.quit()

    return jobs_data


def _safe_text(driver, css_selector: str) -> str:
    try:
        return driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
    except NoSuchElementException:
        return ""


if __name__ == "__main__":
    # Contoh penggunaan — ganti URL sesuai pencarian yang diinginkan
    SEARCH_URL = "https://www.glassdoor.com/Job/indonesia-data-analyst-jobs-SRCH_IL.0,9_IN113_KO10,22.htm"

    results = scrape_glassdoor_jobs(SEARCH_URL, max_jobs=20, headless=True)

    df = pd.DataFrame(results)
    df.to_csv("glassdoor_jobs.csv", index=False)
    print(f"\nSelesai. {len(df)} lowongan disimpan ke glassdoor_jobs.csv")