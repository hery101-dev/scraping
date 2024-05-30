from playwright.sync_api import sync_playwright
import pandas as pd

def get_all_pages():
    urls = []
    for page_number in range(151, 201):
        url = f"https://www.portaljob-madagascar.com/emploi/liste/page/{page_number}"
        urls.append(url)
    return urls

def parse_page(page, url):
    page.goto(url, timeout=90000)
    offres = page.query_selector_all('article.item_annonce')

    data = []
    for offre in offres:
        b_date = offre.query_selector('div.date b').inner_text().strip() if offre.query_selector('div.date b') else None
        mois = offre.query_selector('div.date span.mois').inner_text().strip() if offre.query_selector('div.date span.mois') else None
        annee = offre.query_selector('div.date span.annee').inner_text().strip() if offre.query_selector('div.date span.annee') else None
        date_creation = f"{b_date}-{mois}-{annee}"

        date_limite_elem = offre.query_selector('i.date_lim')

        if date_limite_elem:
            date_limite_text = date_limite_elem.inner_text().strip()
            date_limite = date_limite_text.replace("Date limite :", "").strip()
        else:
            date_limite = None

        title = offre.query_selector('h3').inner_text().strip() if offre.query_selector('h3') else None
        company_name = offre.query_selector('h4').inner_text().strip() if offre.query_selector('h4') else None
        contrat = offre.query_selector('h5').inner_text().strip() if offre.query_selector('h5') else None
        descriptions = offre.query_selector_all('a.description')
        descriptions_with_text = [desc.inner_text().strip() for desc in descriptions if desc.inner_text().strip()]
        p_description = descriptions_with_text[-1] if descriptions_with_text else None

        data.append([title, company_name, contrat, date_creation, p_description, date_limite])

    return data

def main():
    data = []
    urls = get_all_pages()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for url in urls:
            data.extend(parse_page(page, url))
            print(f"Scraping {url}")

        browser.close()

    df = pd.DataFrame(data, columns=['Title', 'Company Name', 'Contract', 'Created At', 'Description', 'Deadline'])
    df.to_excel(r"C:\Users\TL\Desktop\scraping\offres.xlsx", index=False)

if __name__ == "__main__":
    main()
