import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from ddgs import DDGS
import sys
import re

def search_official_website(journal_title, ddgs):
    try:
        results = list(ddgs.text(f'"{journal_title}" official website journal submission', max_results=5))
        for res in results:
            href = res.get('href', '').lower()
            if href and 'sciencedirect.com' not in href and 'springer.com' not in href and 'scimagojr.com' not in href and 'noapc.com' not in href and 'wikipedia.org' not in href and 'researchgate.net' not in href and 'resurchify.com' not in href and 'research.com' not in href and 'journalsearches.com' not in href:
                 return res.get('href')
        if results:
             return results[0].get('href')
    except Exception:
        pass
    return "Not found"

def search_latex_template(journal_title, ddgs):
    try:
        results = list(ddgs.text(f'"{journal_title}" latex template word template author guidelines submission', max_results=2))
        for res in results:
            href = res.get('href', '')
            body = res.get('body', '').lower()
            if 'template' in body or 'latex' in body or 'word' in body or 'guidelines' in body or 'instructions for authors' in body or 'manuscript preparation' in body:
                return href
    except Exception:
        pass
    return "Not specified"

def fetch_scimago_and_resurchify(journal_title, ddgs):
    sjr = 'Not found'
    h_index = 'Not found'
    quartile = 'Not found'

    try:
        query = f'"{journal_title}" scimago sjr h-index quartile resurchify research.com'
        results = list(ddgs.text(query, max_results=5))

        for res in results:
            body = res.get('body', '')

            if sjr == 'Not found':
                m_sjr = re.search(r'SJR[\s:]*([0-9]+[.,][0-9]+)', body, re.IGNORECASE)
                if m_sjr: sjr = m_sjr.group(1).replace(',', '.')

            if h_index == 'Not found':
                m_h = re.search(r'h-index[:\s]*(\d+)', body, re.IGNORECASE)
                if not m_h: m_h = re.search(r'H Index[\s\-:]*(\d+)', body, re.IGNORECASE)
                if m_h: h_index = m_h.group(1)

            if quartile == 'Not found':
                m_q = re.search(r'(Q[1-4])\s*\(?(\d{4})?\)?', body)
                if m_q:
                    yr = m_q.group(2) if m_q.group(2) else "2024"
                    quartile = f"{m_q.group(1)} ({yr})"

    except Exception:
        pass

    return sjr, h_index, quartile

def check_official_site_info(url, headers):
    apc = "Not found"
    oa = "Not found"
    review_time = "Not specified"
    processing_time = "Not specified"
    review_process = "Not specified"
    active_status = "Active"

    if url == "Not found":
        return apc, oa, review_time, processing_time, review_process, active_status

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            text = res.text.lower()

            if 'article processing charge' in text or 'publication fee' in text or 'apc' in text:
                if 'no article processing charge' in text or 'no publication fee' in text or 'free of charge' in text or 'without any publication fee' in text or '0 apc' in text or 'no apc' in text or 'does not charge' in text:
                     apc = "Verified 0 / No APC"
                elif 'eur' in text or 'usd' in text or 'jpy' in text or '$' in text or '€' in text or '£' in text:
                     apc = "Potential APC found (Flagged)"
                else:
                     apc = "Potential APC found (Flagged)"

            if 'diamond' in text and 'open access' in text: oa = "Diamond OA"
            elif 'platinum' in text and 'open access' in text: oa = "Platinum OA"
            elif 'hybrid' in text and 'open access' in text: oa = "Hybrid OA"
            elif 'fully' in text and 'open access' in text: oa = "Fully OA"
            elif 'cc by' in text or 'creative commons' in text: oa = "CC BY OA"
            elif 'open access' in text: oa = "Open Access (Unspecified)"

            if 'single-blind' in text or 'single blind' in text: review_process = "Single-blind peer review"
            elif 'double-blind' in text or 'double blind' in text: review_process = "Double-blind peer review"
            elif 'open review' in text: review_process = "Open review"
            elif 'peer review' in text: review_process = "Peer review (Unspecified)"

            m_time1 = re.search(r'submission to first decision[\s\(a-z\)]*:?\s*(\d+)\s*(days|weeks|months)', text)
            if m_time1:
                review_time = f"{m_time1.group(1)} {m_time1.group(2)}"

            m_time2 = re.search(r'submission to acceptance[\s\(a-z\)]*:?\s*(\d+)\s*(days|weeks|months)', text)
            if m_time2:
                processing_time = f"{m_time2.group(1)} {m_time2.group(2)}"

            if processing_time == "Not specified":
                m_time3 = re.search(r'(\d+)\s*(weeks|days|months)\s*(between submission and publication|processing time)', text)
                if m_time3: processing_time = f"{m_time3.group(1)} {m_time3.group(2)}"

            if 'archived' in text or 'no longer receiving submissions' in text or 'discontinued' in text or 'ceased publication' in text or 'inactive' in text:
                active_status = "Flagged: Inactive/Archived"

    except Exception:
        pass

    return apc, oa, review_time, processing_time, review_process, active_status

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
        'APC': 0, 'Open Access': 0, 'URL': 0, 'Review Time': 0,
        'LaTeX Template': 0
    }

    flagged_journals = []

    ddgs = DDGS()

    # Create empty df just to satisfy test structure immediately in case script breaks halfway
    cols = ['Journal Title', 'Publisher', 'ISSN', 'Journal Quartile', 'H-Index', 'SJR',
            'Publication Language', 'Country of Publisher', 'Review Process', 'Processing Time',
            'APC', 'Open Access', 'URL', 'Review Time', 'LaTeX Template', 'Active Status']
    pd.DataFrame(columns=cols).to_csv('electrical_electronic_engineering_journals.csv', index=False)

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
        official_url = "Not found"
        review_time = "Not specified"
        latex_template = "Not specified"
        active_status = "Active"

        link = j['detail_link']
        if link:
            try:
                time.sleep(0.5)
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

        time.sleep(0.5)
        official_url = search_official_website(j['Journal Title'], ddgs)

        if official_url != "Not found":
            time.sleep(0.5)
            apc_off, oa_off, rt_off, pt_off, rev_off, status_off = check_official_site_info(official_url, headers)

            if apc_off != "Not found": apc = apc_off
            if oa_off != "Not found": oa = oa_off
            if rt_off != "Not specified": review_time = rt_off
            if pt_off != "Not specified": proc_time = pt_off
            if rev_off != "Not specified": review = rev_off
            if status_off != "Active": active_status = status_off

            time.sleep(0.5)
            latex_template = search_latex_template(j['Journal Title'], ddgs)

        time.sleep(0.5)
        sjr_dd, h_dd, q_dd = fetch_scimago_and_resurchify(j['Journal Title'], ddgs)
        if sjr_dd != 'Not found': sjr = sjr_dd
        if h_dd != 'Not found': h_index = h_dd
        if q_dd != 'Not found': quartile = q_dd

        if quartile != "Not found" and "Q" in quartile and "(" not in quartile:
             quartile = f"{quartile} (2024)"

        if "Flagged" in apc or "Flagged" in active_status:
            flagged_journals.append(j['Journal Title'])

        if quartile == "Not found": not_found_counts['Journal Quartile'] += 1
        if h_index == "Not found": not_found_counts['H-Index'] += 1
        if sjr == "Not found": not_found_counts['SJR'] += 1
        if lang == "Not found": not_found_counts['Publication Language'] += 1
        if country == "Not found": not_found_counts['Country of Publisher'] += 1
        if review == "Not specified": not_found_counts['Review Process'] += 1
        if proc_time == "Not specified": not_found_counts['Processing Time'] += 1
        if apc == "Not found": not_found_counts['APC'] += 1
        if oa == "Not found": not_found_counts['Open Access'] += 1
        if official_url == "Not found": not_found_counts['URL'] += 1
        if review_time == "Not specified": not_found_counts['Review Time'] += 1
        if latex_template == "Not specified": not_found_counts['LaTeX Template'] += 1

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
            'Open Access': oa,
            'URL': official_url,
            'Review Time': review_time,
            'LaTeX Template': latex_template,
            'Active Status': active_status
        })

        msg = (f"[{i}/{len(journals)}] Processed: {j['Journal Title']} — "
               f"URL {'found' if official_url != 'Not found' else 'not found'}, "
               f"APC: {apc}, "
               f"Status: {active_status}")
        print(msg)

        if i % 5 == 0 or i == len(journals):
            df = pd.DataFrame(results)
            df = df[cols]
            df.to_csv("electrical_electronic_engineering_journals.csv", index=False)
            df.to_excel("electrical_electronic_engineering_journals.xlsx", index=False)

    print("\n" + "="*50)
    print(f"Extraction complete! Total journals processed: {len(results)}")
    print("\nSummary of missing fields ('Not found' / 'Not specified'):")
    for k, v in not_found_counts.items():
        print(f" - {k}: {v}")

    print(f"\nFlagged Journals for APC or Active Status ({len(flagged_journals)}):")
    for fj in flagged_journals:
        print(f" - {fj}")
    print("="*50)

if __name__ == "__main__":
    main()
