##Backlink Checker Tool
A simple web-based **Backlink Checker** built with **Python (Flask)** that allows users to upload backlink files or mapping files (Excel/CSV) and verify:
Whether backlinks exist on given pages  
- Anchor text matches  
- Link URLs are correct  
- Index / Noindex status of the page   
The tool also supports exporting results to **Excel reports**.

##Features
- Upload **Backlink URLs** (Excel or text input)  
- Crawl and analyze backlink pages  
- Extract:
  - Found URL  
  - Anchor Text  
  - Index / Noindex status  
- Compare results with expected mapping file  
- Responsive **Bootstrap-based UI**  
- Export results to **Excel**  

##Installation
1. Clone this repo:

   ```bash
   git clone https://github.com/yourusername/backlink-checker.git
   cd backlink-checker
2. Install dependencies: pip install -r requirements.txt
3. Run the Flask app: python app.py
4. Open in browser: http://localhost:5000

##Tech Stack
1. Python 3.x
2. Flask
3. Requests / BeautifulSoup (for scraping)
4. Pandas / Openpyxl (for Excel handling)
5. Bootstrap 5 (for frontend UI)


