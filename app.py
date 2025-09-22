from flask import Flask, request, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import io

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_domain(url):
    try:
        parsed = urlparse(url.strip())
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url or url.lower() in ["nan", "none", "null"]:
        return ""
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url
    return url

def check_anchors(backlink_page, expected_url):
    found_links = []
    expected_domain = get_domain(expected_url)
    noindex_status = "No"

    try:
        resp = requests.get(backlink_page, headers=headers, timeout=10)
        if resp.status_code != 200:
            return [{"result": f"Page not accessible ({resp.status_code})", "url": "", "anchor": "", "noindex": "No"}], 0
        soup = BeautifulSoup(resp.text, "html.parser")

        # Check meta robots
        meta_robots = soup.find("meta", attrs={"name": "robots"})
        if meta_robots and meta_robots.get("content"):
            content = meta_robots["content"].lower()
            if "noindex" in content:
                noindex_status = "Yes"
            else:
                noindex_status = "No"

        # Check anchors
        links = soup.find_all("a", href=True)
        for link in links:
            full_href = urljoin(backlink_page, link["href"])
            link_domain = get_domain(full_href)
            if expected_domain == link_domain:
                found_links.append({
                    "result": "Link Found",
                    "url": full_href,
                    "anchor": link.get_text(strip=True) if link.get_text(strip=True) else "N/A",
                    "noindex": noindex_status
                })

        if not found_links:
            return [{"result": "Link not found", "url": "", "anchor": "", "noindex": noindex_status}], 0
        return found_links, len(found_links)

    except requests.exceptions.Timeout:
        return [{"result": "Timeout – site too slow", "url": "", "anchor": "", "noindex": "No"}], 0
    except requests.exceptions.ConnectionError:
        return [{"result": "Connection blocked/refused", "url": "", "anchor": "", "noindex": "No"}], 0
    except Exception:
        return [{"result": "Unable to fetch page", "url": "", "anchor": "", "noindex": "No"}], 0


HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Backlink Checker</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f4f6f9;
      margin: 0;
      padding: 20px;
    }
    .container {
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      max-width: 1200px;
      margin: auto;
      box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    h2 {
      text-align: center;
      margin-bottom: 25px;
      color: #007BFF;
    }
    label {
      font-weight: bold;
      margin-bottom: 5px;
      display: block;
    }
    textarea, input, .file-input {
      width: 100%;
      padding: 12px;
      margin-bottom: 15px;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 14px;
    }
    button {
      width: 100%;
      padding: 12px;
      background: #007BFF;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 16px;
    }
    button:hover {
      background: #0056b3;
    }
    .table-wrapper {
      overflow-x: auto;
      margin-top: 25px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 700px;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
      font-size: 14px;
    }
    th {
      background: #007BFF;
      color: white;
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 1;
    }
    tr:nth-child(even) { background: #f9f9f9; }
    .download {
      margin-top: 20px;
      text-align: center;
    }
    @media (max-width: 768px) {
      textarea, input, .file-input, button {
        font-size: 14px;
      }
      th, td {
        font-size: 12px;
        padding: 8px;
      }
    }
  </style>
</head>
<body>
   <div class="container">
    <h2>Backlink Checker</h2>
    <form method="post" action="{{ url_for('check_backlinks') }}" enctype="multipart/form-data">
      <label>Backlink Page URLs (one per line):</label>
      <textarea name="backlinks" placeholder="https://example.com/article&#10;https://example2.com/page">{{ backlinks_text if backlinks_text else '' }}</textarea>
      
      <label>OR Upload Excel File (first column should contain backlink URLs):</label>
      <input type="file" name="file" class="file-input" accept=".xlsx,.xls">
      
      <label>Expected Target URL (only domain will be checked):</label>
      <input type="text" name="expected_url" placeholder="https://yourdomain.com/coach-course" value="{{ expected_url if expected_url else '' }}" required>
      
      <button type="submit">Check Backlinks</button>
    </form>

    {% if results %}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Backlink Page</th>
            <th>Expected Domain</th>
            <th>Total Found</th>
            <th>Status</th>
            <th>Found URL</th>
            <th>Anchor Text</th>
            <th>Noindex</th>
          </tr>
        </thead>
        <tbody>
          {% for res in results %}
            {% for link in res.links %}
              <tr>
                {% if loop.first %}
                  <td rowspan="{{res.count}}">{{ res.page }}</td>
                  <td rowspan="{{res.count}}">{{ res.expected }}</td>
                  <td rowspan="{{res.count}}">{{ res.count }}</td>
                {% endif %}
                <td>{{ link.result }}</td>
                <td>{{ link.url if link.url else "-" }}</td>
                <td>{{ link.anchor if link.anchor else "-" }}</td>
                <td>{{ link.noindex }}</td>  <!-- NEW -->
              </tr>
            {% endfor %}
          {% endfor %}
        </tbody>
      </table>
    </div>
    <div class="download">
      <form method="post" action="{{ url_for('download_excel') }}">
        <input type="hidden" name="expected_url" value="{{ expected_url }}">
        <input type="hidden" name="backlinks_text" value="{{ backlinks_text }}">
        <button type="submit"> Download Excel Report</button>
      </form>
    </div>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

@app.route("/check_backlinks", methods=["POST"])
def check_backlinks():
    backlinks_text = request.form.get("backlinks", "")
    expected_url = normalize_url(request.form.get("expected_url", "").strip())
    expected_domain = get_domain(expected_url)
    file = request.files.get("file")
    backlink_pages = []
    if backlinks_text.strip():
        backlink_pages.extend([normalize_url(line.strip()) for line in backlinks_text.splitlines() if line.strip()])
    if file and file.filename.endswith((".xlsx", ".xls")):
        try:
            df = pd.read_excel(file)
            excel_links = df.values.ravel().tolist()
            for link in excel_links:
                if pd.isna(link):
                    continue
                link = str(link).strip()
                if link.isdigit():
                    continue
                backlink_pages.append(normalize_url(link))
        except Exception as e:
            print("Excel read error:", str(e))
    results = []
    for page in backlink_pages:
        found_links, count = check_anchors(page, expected_url)
        results.append({
            "page": page,
            "expected": expected_domain,
            "count": count if count > 0 else 1,
            "links": found_links
        })
    app.config["last_results"] = results
    return render_template_string(HTML_FORM, results=results, expected_url=expected_url, backlinks_text=backlinks_text)

@app.route("/download_excel", methods=["POST"])
def download_excel():
    results = app.config.get("last_results", [])
    if not results:
        return "No results to export"
    rows = []
    for res in results:
        for link in res["links"]:
            rows.append({
                "Backlink Page": res["page"],
                "Expected Domain": res["expected"],
                "Total Found": res["count"],
                "Status": link["result"],
                "Found URL": link["url"],
                "Anchor Text": link["anchor"],
                "Noindex": link["noindex"]
            })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="backlink_report.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run()
