import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from ddgs import DDGS
import sys
import re

def search_official_website(journal_title):
    ddgs = DDGS()
    try:
        results = list(ddgs.text(f"{journal_title} official website", max_results=2))
        for res in results:
            href = res.get('href')
            if href and 'sciencedirect' not in href and 'springer' not in href and 'scimagojr' not in href and 'noapc' not in href and 'wikipedia' not in href:
                 return href
        if results:
             return results[0].get('href')
    except Exception:
        pass
    return None

def check_apc_and_oa(url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            text = res.text.lower()

            apc = "No APC mentioned"
            oa = "Open Access"

            if 'article processing charge' in text or 'publication fee' in text or 'apc' in text:
                if 'no article processing charge' in text or 'no publication fee' in text or 'free of charge' in text or 'without any publication fee' in text or '0 apc' in text:
                     apc = "Verified 0 / No APC"
                else:
                     apc = "Potential APC found (Flagged)"

            if 'diamond' in text and 'open access' in text:
                oa = "Diamond OA"
            elif 'platinum' in text and 'open access' in text:
                oa = "Platinum OA"
            elif 'hybrid' in text and 'open access' in text:
                oa = "Hybrid OA"
            elif 'fully' in text and 'open access' in text:
                oa = "Fully OA"
            elif 'cc by' in text or 'creative commons' in text:
                oa = "CC BY OA"

            return apc, oa
    except Exception:
        pass
    return "Not verified", "Not verified"

def main():
    print("Fetching the main page...")
    url = 'https://noapc.com/electrical-and-electronic-engineering-free-scopus-journals/'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch the main page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        print("Could not find the table on the main page.")
        return

    rows = table.find_all('tr')
    journals = []
    for row in rows[1:]:
        cols = row.find_all('td')
        if not cols:
            continue
        title = cols[1].text.strip()
        publisher = cols[2].text.strip()
        issn = cols[3].text.strip()

        a_tag = cols[1].find('a')
        detail_link = a_tag['href'] if a_tag else ''
        if detail_link and not detail_link.startswith('http'):
            detail_link = 'https://noapc.com/' + detail_link.lstrip('/')

        journals.append({
            'Journal Title': title,
            'Publisher': publisher,
            'ISSN': issn,
            'detail_link': detail_link
        })

    print(f"Found {len(journals)} journals in the main table.")
    results = []

    not_found_counts = {
        'Journal Quartile': 0, 'H-Index': 0, 'SJR': 0,
        'Publication Language': 0, 'Country of Publisher': 0,
        'Review Process': 0, 'Processing Time': 0,
        'APC': 0, 'Open Access': 0
    }

    ddgs = DDGS()

    for i, j in enumerate(journals, 1):
        quartile = "Not found"
        h_index = "Not found"
        sjr = "Not found"
        lang = "Not found"
        country = "Not found"
        review = "Not specified"
        proc_time = "Not specified"
        apc = "Not found"
        oa = "Not found"

        link = j['detail_link']
        if link:
            try:
                # Polite rate limit for noapc.com
                time.sleep(1.0)
                res = requests.get(link, headers=headers, timeout=10)
                if res.status_code == 200:
                    detail_soup = BeautifulSoup(res.text, 'html.parser')
                    meta = {}
                    for tr in detail_soup.find_all('tr'):
                        cells = tr.find_all(['th', 'td'])
                        if len(cells) == 2:
                            meta[cells[0].text.strip()] = cells[1].text.strip()

                    q = meta.get('Journal Quartile', '')
                    if q: quartile = q
                    h = meta.get('H-Index', '')
                    if h: h_index = h
                    s = meta.get('SJR', '')
                    if s: sjr = s
                    c = meta.get('Country of Publisher', '')
                    if c: country = c
                    r = meta.get('Review Process', '')
                    if r: review = r
                    t = meta.get('Processing time', '')
                    if t: proc_time = t
                    a = meta.get('APC', '')
                    if a: apc = a
                    o = meta.get('Open Access', '')
                    if o: oa = o
                    l = meta.get('Publication Language', '')
                    if l: lang = l
            except Exception as e:
                pass

        # Verification via official website
        official_url = search_official_website(j['Journal Title'])
        if official_url:
            time.sleep(1.5) # Polite rate limit for external sites
            verification_apc, verification_oa = check_apc_and_oa(official_url, headers)
            if verification_apc == "Potential APC found (Flagged)":
                apc = "Flagged: Verify APC on official site"
            elif verification_apc == "Verified 0 / No APC":
                apc = "Verified 0 / No APC"

            if verification_oa != "Not verified" and verification_oa != "Open Access":
                oa = verification_oa

        try:
            query = f'"{j["Journal Title"]}" scimago sjr h-index quartile'
            res_list = list(ddgs.text(query, max_results=3))
            for res_item in res_list:
                body = res_item.get('body', '')

                m_sjr = re.search(r'SJR[\\s:]+([0-9]+[.,][0-9]+)', body, re.IGNORECASE)
                if m_sjr: sjr = m_sjr.group(1).replace(',', '.')

                m_h = re.search(r'h-index[:\\s]+(\\d+)', body, re.IGNORECASE)
                if not m_h:
                    m_h = re.search(r'H Index[\\s\\-:]+(\\d+)', body, re.IGNORECASE)
                if m_h: h_index = m_h.group(1)

                m_q = re.search(r'(Q[1-4])\\s*\\(?(\\d{4})\\)?', body)
                if m_q:
                    quartile = f"{m_q.group(1)} ({m_q.group(2)})"
        except Exception:
            pass

        if quartile != "Not found" and "Q" in quartile and "(" not in quartile:
             quartile = f"{quartile} (2024)"

        if quartile == "Not found": not_found_counts['Journal Quartile'] += 1
        if h_index == "Not found": not_found_counts['H-Index'] += 1
        if sjr == "Not found": not_found_counts['SJR'] += 1
        if lang == "Not found": not_found_counts['Publication Language'] += 1
        if country == "Not found": not_found_counts['Country of Publisher'] += 1
        if review == "Not specified": not_found_counts['Review Process'] += 1
        if proc_time == "Not specified": not_found_counts['Processing Time'] += 1
        if apc == "Not found": not_found_counts['APC'] += 1
        if oa == "Not found": not_found_counts['Open Access'] += 1

        results.append({
            'Journal Title': j['Journal Title'],
            'Publisher': j['Publisher'],
            'ISSN': j['ISSN'],
            'Journal Quartile': quartile,
            'H-Index': h_index,
            'SJR': sjr,
            'Publication Language': lang,
            'Country of Publisher': country,
            'Review Process': review,
            'Processing Time': proc_time,
            'APC': apc,
            'Open Access': oa
        })

        msg = (f"[{i}/{len(journals)}] Processed: {j['Journal Title']} — "
               f"SJR {'found' if sjr != 'Not found' else 'not found'}, "
               f"H-index {'found' if h_index != 'Not found' else 'not found'}, "
               f"review process {'found' if review != 'Not specified' else 'not specified'}")
        print(msg)

    df = pd.DataFrame(results)
    csv_file = "electrical_electronic_engineering_journals.csv"
    xlsx_file = "electrical_electronic_engineering_journals.xlsx"
    df.to_csv(csv_file, index=False)
    df.to_excel(xlsx_file, index=False)

    print("\n" + "="*50)
    print(f"Extraction complete! Total journals processed: {len(results)}")
    print("Files saved:")
    print(f" - {csv_file}")
    print(f" - {xlsx_file}")
    print("\nSummary of missing fields ('Not found' / 'Not specified'):")
    for k, v in not_found_counts.items():
        print(f" - {k}: {v}")
    print("="*50)

if __name__ == "__main__":
    main()
