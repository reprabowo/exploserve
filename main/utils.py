import requests
from bs4 import BeautifulSoup
import re
from difflib import SequenceMatcher

def fetch_sinta_scores(sinta_id, local_name = None, threshold = 0.8):
    """
    Given a SINTA ID, fetch the corresponding profile page from SINTA
    and return a tuple (first_score, second_score) where:
      - first_score is the text of the first element with class "pr-num"
      - second_score is the text of the second element with class "pr-num"
    If an element is not found, its value will be None.
    """
    url = f"https://sinta.kemdikbud.go.id/authors/profile/{sinta_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error fetching SINTA page:", e)
        return None, None, None, None, "", False

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1) Get the first two scores by class="pr-num"
    pr_elements = soup.find_all(class_="pr-num")
    
    first_score = pr_elements[0].get_text(strip=True) if len(pr_elements) >= 1 else None
    second_score = pr_elements[1].get_text(strip=True) if len(pr_elements) >= 2 else None

    # 2) Get the third and fourth scores from the table row 4, col 2/3
    third_score, fourth_score = None, None
    table = soup.find('table')  # or be more specific if there are multiple tables

    if table:
        rows = table.find_all('tr')
        # Check if row 5 exists (index 4)
        if len(rows) >= 5:
            cells = rows[4].find_all('td')  # tr[4] => index 3
            if len(cells) >= 3:
                # td[2] => cells[1], td[3] => cells[2]
                third_score = cells[1].get_text(strip=True)
                fourth_score = cells[2].get_text(strip=True)

    # scrape the “official” name in <h3><a>…</a></h3>
    sinta_name = ""
    h3 = soup.find("h3")
    if h3:
        a = h3.find("a")
        sinta_name = a.get_text(strip=True) if a else h3.get_text(strip=True)

    # fuzzy compare
    name_match = False
    if local_name and sinta_name:
        ratio = SequenceMatcher(
            None,
            local_name.lower().strip(),
            sinta_name.lower().strip()
        ).ratio()
        name_match = (ratio >= threshold)

    return first_score, second_score, third_score, fourth_score, sinta_name, name_match

# Example usage in the Django shell:
if __name__ == "__main__":
    score, score3, scoresc, scorego = fetch_sinta_scores("6491")
    print("First Score:", score)
    print("Second Score:", score3)
    print("Third Score:", scoresc)
    print("Fourth Score:", scorego)

def fetch_sinta_inst_scores(sinta_id):
    """
    Given a SINTA ID, fetch the corresponding profile page from SINTA
    and return a tuple (first_score, second_score) where:
      - first_score is the text of the first element with class "pr-num"
      - second_score is the text of the second element with class "pr-num"
    If an element is not found, its value will be None.
    """
    url = f"https://sinta.kemdikbud.go.id/affiliations/profile/{sinta_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error fetching SINTA page:", e)
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1) Get the first two scores by class="pr-num"
    pr_elements = soup.find_all(class_="pr-num")
    
    first_inst_score = pr_elements[0].get_text(strip=True) if len(pr_elements) >= 1 else None
    second_inst_score = pr_elements[1].get_text(strip=True) if len(pr_elements) >= 2 else None

    return first_inst_score, second_inst_score

def fetch_sinta_ps_scores(inst_sinta_id, inst_pt_id, ps_sinta_id):
    """
    Fetch SINTA Score Overall and 3Yr for a specific Program Studi
    from SINTA department page using institutional IDs.
    """
    url = f"https://sinta.kemdikbud.go.id/affiliations/departments/{inst_sinta_id}/{inst_pt_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error fetching SINTA page:", e)
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select("div.row.d-item")

    for row in rows:
        sinta_id_div = row.select_one("div.tbl-content-meta-num")
        if not sinta_id_div:
            continue

        try:
            current_ps_id = int(sinta_id_div.get_text(strip=True))
        except ValueError:
            continue

        if current_ps_id == int(ps_sinta_id):
            overall_span = row.select_one("span.profile-id.text-warning")
            score3yr_span = row.select_one("span.profile-id.text-success")

            def extract_last_number(text):
                match = re.search(r"(\d[\d.,]*)\s*$", text)
                return match.group(1).replace('.', '').replace(',', '.') if match else None

            first_ps_score = extract_last_number(overall_span.get_text()) if overall_span else None
            second_ps_score = extract_last_number(score3yr_span.get_text()) if score3yr_span else None

            return first_ps_score, second_ps_score

    return None, None
