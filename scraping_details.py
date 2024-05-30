from playwright.sync_api import sync_playwright
import pandas as pd

def get_all_pages():
    urls = []
    for page_number in range(1, 6):  # Assume 5 pages to scrape
        url = f"https://www.portaljob-madagascar.com/emploi/liste/page/{page_number}"
        urls.append(url)
    return urls

def parse_page_detail(context, url):
    page = context.new_page()
    page.goto(url, timeout=60000)
    offres = page.query_selector_all('article.item_annonce')

    data = []
    for offre in offres:
        company_name = offre.query_selector('h4').inner_text().strip() if offre.query_selector('h4') else None
        contrat = offre.query_selector('h5').inner_text().strip() if offre.query_selector('h5') else None
        detail_link = offre.query_selector('h3 > a').get_attribute('href')

        # Navigate to the detail page in a new tab
        detail_page = context.new_page()
        detail_page.goto(detail_link, timeout=60000)

        title = detail_page.query_selector('div#tab0 h2').inner_text() if detail_page.query_selector('div#tab0 h2') else None
        date_creation = detail_page.query_selector('div.item_detail span.offers-date').inner_text().strip() if detail_page.query_selector('div.item_detail span.offers-date') else None
        date_limite_elem = detail_page.query_selector('div.item_detail span.date_lim')
        date_limite = date_limite_elem.inner_text().strip() if date_limite_elem else None

        missions = []
        for selector in ['article.item_detail', 'aside.item_detail', 'section.item_detail']:
            elem = detail_page.query_selector(selector)
            if elem:
                missions.append(elem.inner_text())

        data.append([title, company_name, contrat, date_creation, missions, date_limite])

        detail_page.close()

    page.close()
    return data

def main():
    data = []
    urls = get_all_pages()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        for url in urls:
            data.extend(parse_page_detail(context, url))
            print(f"On scrape {url}")

        context.close()
        browser.close()

    df = pd.DataFrame(data, columns=['Title', 'Company Name', 'Contract', 'Created At', 'Missions', 'Deadline'])
    df.to_excel(r"C:\Users\TL\Desktop\scraping\offres.xlsx", index=False)

if __name__ == "__main__":
    main()
