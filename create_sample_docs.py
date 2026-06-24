import pymupdf

docs = [
    ('company_a_report.pdf', '''Company A Annual Report 2025

FINANCIAL HIGHLIGHTS
Revenue: 500 million dollars, up 12 percent year over year
Net Profit: 75 million dollars, profit margin of 15 percent
R&D Spending: 40 million dollars, representing 8 percent of revenue
Total Employees: 5000

BUSINESS OVERVIEW
Company A operates in the software services sector, focusing on cloud computing and AI solutions. The company expanded into 3 new international markets this year.

RISKS
Increased competition from larger players and currency fluctuation risk in international markets.'''),
    ('company_b_report.pdf', '''Company B Annual Report 2025

FINANCIAL HIGHLIGHTS
Revenue: 800 million dollars, up 8 percent year over year
Net Profit: 96 million dollars, profit margin of 12 percent
R&D Spending: 96 million dollars, representing 12 percent of revenue
Total Employees: 9000

BUSINESS OVERVIEW
Company B operates in the financial technology sector, providing payment processing and lending solutions. The company acquired 2 smaller startups this year.

RISKS
Regulatory risk due to financial sector compliance requirements and cybersecurity threats.''')
]

for filename, content in docs:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), content, fontsize=11)
    doc.save(filename)
    print(f"Created {filename}")