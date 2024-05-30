from playwright.sync_api import sync_playwright
import pandas as pd


def get_all_pages():
    urls = []
    for page_number in range(1, 50):
        url = f"https://www.portaljob-madagascar.com/emploi/liste/secteur/conseiller-client-call-center/page/{page_number}"
        urls.append(url)
    return urls

def parse_page(page, url):
    page.goto(url, timeout=90000)
    offres = page.query_selector_all('article.item_annonce')
    data = []
    for offre in offres:
        title = offre.query_selector('h3 > a > strong').inner_text()
        category = 'Conseiller-client-call-center'
        data.append([title, category])
    return data

def main():
    data = []
    urls = get_all_pages()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for url in urls:
            data.extend(parse_page(page, url))
            print(f"On scrape la categorie conseiller client ou call center {url}")

        browser.close()

    df = pd.DataFrame(data, columns=['title', 'category'])
    df.to_excel(r"C:\Users\TL\Desktop\scraping\agronomie-agriculture.xlsx", index=False)

if __name__ == "__main__":
    main()
