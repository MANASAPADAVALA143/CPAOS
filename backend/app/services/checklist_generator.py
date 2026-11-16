"""Country + entity onboarding checklists (spec Task 6)."""

from __future__ import annotations

INDIA_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("PAN Card", "Permanent Account Number card", True),
            ("Aadhaar Card", "12-digit UID card", True),
            ("Passport/Voter ID", "Any one government photo ID", False),
        ],
        "Tax": [
            ("Form 16", "TDS certificate from employer", True),
            ("AIS/26AS", "Annual Information Statement from IT portal", True),
            ("Previous ITR", "Last 2 years filed returns", False),
            ("Salary Slips", "Last 3 months salary slips", False),
        ],
        "Financial": [
            ("Bank Statements", "Last 12 months all accounts", True),
            ("Investment Proofs", "Mutual funds, FD, shares, PPF", False),
            ("Rental Income Docs", "Rental agreement if rental income", False),
        ],
    },
    "sole_proprietor": {
        "Identity": [
            ("PAN Card", "Proprietor PAN card", True),
            ("Aadhaar Card", "Proprietor Aadhaar", True),
        ],
        "Business": [
            ("GST Certificate", "GST registration if registered", False),
            ("MSME Certificate", "Udyam registration if applicable", False),
            ("Trade License", "Municipal trade license", False),
        ],
        "Tax": [
            ("Previous ITR", "Last 2 years ITR-3 or ITR-4", True),
            ("TDS Returns", "24Q/26Q if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("Purchase Invoices", "Sample vendor invoices", False),
        ],
    },
    "partnership": {
        "Identity": [
            ("Partnership Deed", "Registered partnership deed", True),
            ("PAN Card", "Firm PAN card", True),
            ("Partners PAN", "All partners PAN cards", True),
            ("Partners Aadhaar", "All partners Aadhaar", True),
        ],
        "Business": [
            ("GST Certificate", "GST registration certificate", True),
            ("MSME Certificate", "If registered", False),
        ],
        "Tax": [
            ("Previous ITR", "Firm ITR + partners ITR last 2 years", True),
            ("TDS Returns", "If TDS deducted", False),
        ],
        "Financial": [
            ("Capital Accounts", "Partners capital account statements", True),
            ("Bank Statements", "All firm accounts 12 months", True),
            ("P&L Statement", "Last 2 years", True),
            ("Balance Sheet", "Last 2 years", True),
        ],
    },
    "llp": {
        "Identity": [
            ("LLP Agreement", "Registered LLP agreement", True),
            ("COI", "Certificate of Incorporation", True),
            ("PAN Card", "LLP PAN card", True),
            ("Partners PAN", "All designated partners PAN", True),
            ("DPIN", "Designated Partner Identification Number", True),
        ],
        "Business": [
            ("GST Certificate", "GST registration certificate", True),
            ("MSME Certificate", "If registered", False),
        ],
        "Tax": [
            ("Previous ITR", "LLP ITR-5 last 2 years", True),
            ("TDS Returns", "Last 4 quarters", True),
        ],
        "Financial": [
            ("Audited Accounts", "Last 2 years P&L + BS", True),
            ("Bank Statements", "All accounts 12 months", True),
            ("Annual Return", "Form 11 filed with MCA", False),
        ],
    },
    "private_limited": {
        "Identity": [
            ("COI", "Certificate of Incorporation", True),
            ("MOA & AOA", "Memorandum and Articles of Association", True),
            ("PAN Card", "Company PAN card", True),
            ("Board Resolution", "Authorising the CA firm", True),
            ("DIN", "Directors DIN numbers", True),
        ],
        "Business": [
            ("GST Certificate", "GST registration certificate", True),
            ("MSME Certificate", "Udyam registration if applicable", False),
            ("Shops & Est License", "Municipal licence if applicable", False),
            ("IEC Code", "Import Export Code if applicable", False),
        ],
        "Tax": [
            ("Previous ITR", "Company ITR-6 last 2 years", True),
            ("TDS Returns", "24Q/26Q last 4 quarters", True),
            ("Advance Tax Challan", "BSR code challans if paid", False),
        ],
        "Financial": [
            ("Audited Accounts", "Last 2 years P&L + Balance Sheet", True),
            ("Bank Statements", "All accounts 12 months", True),
            ("Loan Statements", "All existing loan accounts", False),
            ("Fixed Asset Register", "If available", False),
            ("Debtors/Creditors List", "Ageing as of last year end", False),
        ],
        "GST": [
            ("GST Returns", "Last 12 months GSTR-1 and GSTR-3B", True),
            ("GST Reconciliation", "Books vs GST portal reconciliation", False),
            ("E-way Bills", "Sample if applicable", False),
        ],
    },
}

UAE_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("Passport Copy", "Valid passport all pages", True),
            ("Emirates ID", "Valid Emirates ID front and back", True),
            ("Visa Copy", "UAE resident visa", True),
        ],
        "Financial": [
            ("Bank Statements", "UAE and overseas accounts 12 months", True),
            ("Rental Income Docs", "Tenancy contract if rental income", False),
        ],
    },
    "sole_proprietor": {
        "Identity": [
            ("Trade License", "Valid trade license", True),
            ("Owner Passport", "Passport copy", True),
            ("Owner Emirates ID", "Valid Emirates ID", True),
        ],
        "Tax": [
            ("VAT Registration", "TRN certificate if VAT registered", False),
            ("CT Registration", "Corporate Tax registration mandatory post June 2023", True),
        ],
        "Financial": [
            ("Bank Statements", "All business accounts 12 months", True),
        ],
    },
    "private_limited": {
        "Identity": [
            ("Trade License", "Valid trade license", True),
            ("MOA", "Memorandum of Association", True),
            ("Passport Copies", "All shareholders and directors", True),
            ("Emirates ID", "All UAE resident directors", True),
            ("POA", "Power of attorney if applicable", False),
            ("Ownership Certificate", "Share certificate or ownership structure", True),
        ],
        "Tax": [
            ("VAT Registration", "TRN certificate", True),
            ("VAT Returns", "Last 12 months VAT returns", True),
            ("CT Registration", "Corporate Tax registration", True),
            ("Economic Substance", "ESR notification if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Audited Accounts", "Last 2 years if available", False),
            ("Contracts", "Major client or supplier contracts", False),
            ("Fixed Asset Register", "If applicable", False),
        ],
    },
    "partnership": {
        "Identity": [
            ("Trade License", "Valid trade license listing all partners", True),
            ("Partnership Agreement", "Signed partnership agreement or MOA", True),
            ("Partners Passports", "Passport copies of all partners", True),
            ("Partners Emirates ID", "Emirates ID of all UAE resident partners", True),
        ],
        "Tax": [
            ("VAT Registration", "TRN certificate if VAT registered", False),
            ("VAT Returns", "Last 12 months if VAT registered", False),
            ("CT Registration", "Corporate Tax registration", True),
        ],
        "Financial": [
            ("Bank Statements", "All partnership accounts 12 months", True),
            ("Profit Sharing Schedule", "Partner capital and profit split", True),
            ("Financial Statements", "Last 2 years if available", False),
        ],
    },
    "llp": {
        "Identity": [
            ("Free Zone License", "Valid free zone license (e.g. DMCC, DIFC, ADGM)", True),
            ("Certificate of Incorporation", "Free zone registration certificate", True),
            ("Articles of Association", "Constitutional documents", True),
            ("Register of Members", "Members and shareholding register", True),
            ("UBO Declaration", "Ultimate Beneficial Owner register", True),
            ("Members Passports", "Passport copies of all members and managers", True),
        ],
        "Tax": [
            ("CT Registration", "Corporate Tax registration", True),
            ("Qualifying Free Zone Assessment", "QFZP status if claiming 0% rate", False),
            ("VAT Registration", "TRN certificate if VAT registered", False),
            ("VAT Returns", "Last 12 months if VAT registered", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Audited Accounts", "Last 2 years (required by most free zones)", True),
            ("Lease Agreement", "Free zone office or flexi-desk lease", False),
        ],
    },
}

UK_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("Passport or Driving Licence", "Valid UK or foreign passport", True),
            ("Proof of Address", "Utility bill or bank statement last 3 months", True),
            ("NI Number", "National Insurance number", True),
            ("UTR Number", "Unique Taxpayer Reference from HMRC", True),
        ],
        "Tax": [
            ("SA302", "Last 2 years self-assessment tax calculations", True),
            ("P60", "Last 2 years P60 if employed", False),
            ("P11D", "Benefits in kind form if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "Personal and business accounts 12 months", True),
            ("Dividend Vouchers", "If director of a limited company", False),
        ],
    },
    "sole_trader": {
        "Identity": [
            ("Passport or Driving Licence", "Valid photo ID", True),
            ("Proof of Address", "Utility bill last 3 months", True),
            ("UTR Number", "HMRC Unique Taxpayer Reference", True),
        ],
        "Business": [
            ("VAT Registration", "VAT number if VAT registered", False),
        ],
        "Tax": [
            ("Previous SA Returns", "Last 2 years self-assessment returns", True),
            ("CIS Statement", "If in construction industry", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("Invoices", "Sales and purchase invoices current year", False),
        ],
    },
    "private_limited": {
        "Identity": [
            ("Certificate of Incorporation", "Companies House certificate", True),
            ("Memorandum and Articles", "M&A from Companies House", True),
            ("Company UTR", "HMRC corporation tax UTR", True),
            ("Director ID", "All directors passport and proof of address", True),
            ("Companies House Number", "CRN from incorporation", True),
        ],
        "Business": [
            ("VAT Registration", "VAT certificate if registered", False),
            ("PAYE Reference", "Employer PAYE reference if staff employed", False),
        ],
        "Tax": [
            ("Previous CT600", "Last 2 years corporation tax returns", True),
            ("Previous Filed Accounts", "Last 2 years accounts", True),
            ("PAYE RTI Records", "If payroll exists", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Loan Agreements", "All business loans", False),
            ("Lease Agreements", "Office or equipment leases", False),
            ("Aged Debtors List", "Debtors list as at year end", False),
        ],
    },
    "llp": {
        "Identity": [
            ("LLP Agreement", "Registered LLP agreement", True),
            ("Certificate of Incorporation", "Companies House certificate", True),
            ("Members ID", "All members passport and address proof", True),
            ("UTR", "HMRC UTR for the LLP", True),
        ],
        "Tax": [
            ("Previous SA800", "Last 2 years LLP partnership returns", True),
            ("Members SA Returns", "Each members personal return", True),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Capital Accounts", "Members capital accounts", True),
        ],
    },
}

US_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("SSN or ITIN", "Social Security Number or ITIN", True),
            ("Government ID", "Drivers license or passport", True),
            ("Prior Year Return", "Last 2 years 1040 returns", True),
        ],
        "Tax": [
            ("W-2 Forms", "From all employers for the year", True),
            ("1099 Forms", "All 1099s received NEC INT DIV etc", True),
            ("K-1 Forms", "If partner or shareholder in pass-through entity", False),
            ("1095-A or B or C", "Health coverage forms", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Investment Statements", "1099-B brokerage statements", False),
            ("Mortgage Interest", "1098 form", False),
            ("Charitable Contributions", "Receipts over $250", False),
        ],
    },
    "sole_proprietor": {
        "Identity": [
            ("SSN or ITIN or EIN", "Tax ID number", True),
            ("Government ID", "Drivers license or passport", True),
            ("DBA Filing", "Doing Business As registration if applicable", False),
        ],
        "Tax": [
            ("Prior Year Return", "Last 2 years 1040 and Schedule C", True),
            ("Sales Tax Returns", "If registered for state sales tax", False),
            ("Estimated Tax Payments", "1040-ES payment records", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("P&L Statement", "YTD income and expense report", True),
            ("Mileage Log", "If claiming vehicle deduction", False),
        ],
    },
    "llc": {
        "Identity": [
            ("EIN", "Employer Identification Number from IRS", True),
            ("Articles of Organization", "State-filed formation document", True),
            ("Operating Agreement", "LLC operating agreement", True),
            ("Members SSN or ITIN", "All members tax IDs", True),
        ],
        "Tax": [
            ("Prior Year Return", "Last 2 years 1065 partnership or 1120-S S-corp", True),
            ("K-1 Distribution", "Prior year K-1 for each member", True),
            ("Sales Tax Returns", "State filing if applicable", False),
            ("Payroll Returns", "941 quarterly returns if employees", False),
        ],
        "Financial": [
            ("Bank Statements", "All business accounts 12 months", True),
            ("P&L Statement", "Current and prior year", True),
            ("Balance Sheet", "As of year end", True),
            ("Loan Agreements", "Business loans and lines of credit", False),
            ("Fixed Assets", "Asset register with dates and cost", False),
        ],
    },
    "s_corp": {
        "Identity": [
            ("EIN", "Employer Identification Number", True),
            ("Articles of Incorporation", "State-filed document", True),
            ("Bylaws", "Corporate bylaws", True),
            ("S-Corp Election", "IRS Form 2553", True),
            ("Shareholders ID", "All shareholders SSN or ITIN", True),
        ],
        "Tax": [
            ("Prior Year 1120-S", "Last 2 years S-Corp return", True),
            ("Prior K-1s", "All shareholders K-1 forms", True),
            ("Payroll Returns", "941 and W-3 filings", True),
            ("W-2s Issued", "W-2s to shareholder-employees", True),
        ],
        "Financial": [
            ("P&L Statement", "Current year and prior year", True),
            ("Balance Sheet", "As of year end", True),
            ("Bank Statements", "All accounts 12 months", True),
            ("Shareholder Loans", "Any loans to or from shareholders", False),
        ],
    },
    "c_corp": {
        "Identity": [
            ("EIN", "Employer Identification Number", True),
            ("Articles of Incorporation", "State-filed document", True),
            ("Bylaws", "Corporate bylaws", True),
            ("Stock Register", "Shareholder register and cap table", True),
        ],
        "Tax": [
            ("Prior Year 1120", "Last 2 years C-Corp return", True),
            ("Payroll Returns", "941 940 and W-3 filings", True),
            ("State Returns", "State income tax returns", True),
            ("R&D Credit", "Form 6765 if claiming R&D credit", False),
        ],
        "Financial": [
            ("P&L Statement", "Current and prior year", True),
            ("Balance Sheet", "As of year end", True),
            ("Bank Statements", "All accounts 12 months", True),
            ("Audited or Reviewed Accounts", "If available", False),
        ],
    },
}

SINGAPORE_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("NRIC or Passport", "NRIC for citizens/PRs, passport and work pass for foreigners", True),
            ("Proof of Address", "Utility bill or bank statement last 3 months", False),
        ],
        "Tax": [
            ("Notice of Assessment", "Last 2 years IRAS NOA", True),
            ("IR8A", "Employer income statement if not auto-included", False),
            ("Previous Form B1", "Last 2 years individual tax returns", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("CPF Statement", "CPF contribution history", False),
            ("Rental Income Docs", "Tenancy agreements if rental income", False),
            ("Investment Statements", "Dividends and overseas income", False),
        ],
    },
    "sole_proprietor": {
        "Identity": [
            ("ACRA Business Profile", "BizFile business profile", True),
            ("Owner NRIC or Passport", "Sole proprietor ID", True),
        ],
        "Tax": [
            ("Previous Form B", "Last 2 years IRAS Form B", True),
            ("Notice of Assessment", "Last 2 years IRAS NOA", True),
            ("GST Registration", "If GST registered over $1M turnover", False),
            ("GST Returns", "Last 12 months if registered", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("Income and Expense Records", "Current year sales and purchase records", True),
            ("MediSave Contributions", "Self-employed MediSave payment records", True),
        ],
    },
    "private_limited": {
        "Identity": [
            ("ACRA BizFile", "Company profile from ACRA", True),
            ("M&A", "Memorandum and Articles of Association", True),
            ("Directors NRIC or Passport", "All directors", True),
            ("Shareholders NRIC or Passport", "All shareholders", True),
        ],
        "Tax": [
            ("Previous C-S or C Forms", "Last 2 years IRAS filings", True),
            ("GST Registration", "If GST registered over $1M turnover", False),
            ("GST Returns", "Last 12 months if registered", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Audited Accounts", "If required over $10M revenue", False),
            ("CPF Contribution", "CPF e-submission report", True),
        ],
    },
}

AUSTRALIA_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("Driver Licence or Passport", "Valid photo ID", True),
            ("TFN", "Tax File Number", True),
            ("myGov Access", "ATO linked myGov access or prefill report", False),
        ],
        "Tax": [
            ("Income Statement", "PAYG income statement from employer(s)", True),
            ("Previous Tax Returns", "Last 2 years individual returns and NOAs", True),
            ("Private Health Insurance Statement", "If held during the year", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Investment Statements", "Shares, dividends, managed funds", False),
            ("Rental Property Docs", "Rental statements and expenses if applicable", False),
            ("Work Expense Receipts", "Deductible work-related expenses", False),
        ],
    },
    "sole_trader": {
        "Identity": [
            ("Driver Licence or Passport", "Valid photo ID", True),
            ("TFN", "Individual Tax File Number", True),
            ("ABN Registration", "Australian Business Number confirmation", True),
        ],
        "Tax": [
            ("BAS Statements", "Business Activity Statements last 4 quarters", True),
            ("Previous Tax Returns", "Last 2 years returns with business schedule", True),
            ("GST Registration", "If turnover over $75K", False),
            ("PAYG Instalments", "Instalment notices if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("Income and Expense Records", "Current year invoices and receipts", True),
            ("Vehicle Logbook", "If claiming motor vehicle expenses", False),
        ],
    },
    "partnership": {
        "Identity": [
            ("Partnership Agreement", "Signed partnership agreement", True),
            ("ABN Registration", "Partnership ABN confirmation", True),
            ("Partnership TFN", "Tax File Number for the partnership", True),
            ("Partners ID", "Photo ID and TFN for each partner", True),
        ],
        "Tax": [
            ("BAS Statements", "Business Activity Statements last 4 quarters", True),
            ("Previous Partnership Returns", "Last 2 years partnership tax returns", True),
            ("GST Registration", "If turnover over $75K", False),
        ],
        "Financial": [
            ("Bank Statements", "All partnership accounts 12 months", True),
            ("Profit Distribution", "Partner profit and capital split", True),
            ("Payroll Summary", "STP finalisation if employees", False),
        ],
    },
    "private_limited": {
        "Identity": [
            ("ASIC Registration", "Certificate of registration and current extract", True),
            ("Company Constitution", "Constitution or replaceable rules confirmation", True),
            ("ABN Registration", "Company ABN confirmation", True),
            ("Company TFN", "Tax File Number for the company", True),
            ("Directors ID", "Director IDs and photo ID for all directors", True),
            ("Share Register", "Members and shareholding register", True),
        ],
        "Tax": [
            ("BAS Statements", "Business Activity Statements last 4 quarters", True),
            ("Previous Company Returns", "Last 2 years company tax returns", True),
            ("GST Registration", "If turnover over $75K", False),
            ("Payroll Summary", "STP finalisation and super contributions", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Financial Statements", "Last 2 years P&L and balance sheet", True),
            ("Division 7A Loans", "Shareholder loan agreements if any", False),
            ("Fixed Asset Register", "Depreciation schedule", False),
        ],
    },
    "trust": {
        "Identity": [
            ("Trust Deed", "Signed trust deed and any variations", True),
            ("Trustee Details", "ID for individual trustees or ASIC extract for corporate trustee", True),
            ("ABN Registration", "Trust ABN confirmation", True),
            ("Trust TFN", "Tax File Number for the trust", True),
        ],
        "Tax": [
            ("Previous Trust Returns", "Last 2 years trust tax returns", True),
            ("Distribution Resolutions", "Trustee resolutions for the year", True),
            ("BAS Statements", "If registered for GST", False),
        ],
        "Financial": [
            ("Bank Statements", "All trust accounts 12 months", True),
            ("Financial Statements", "Last 2 years", True),
        ],
        "SMSF": [
            ("SMSF Trust Deed", "If the trust is a self-managed super fund", False),
            ("SMSF Annual Return", "Last 2 years SMSF annual returns", False),
            ("SMSF Audit Report", "Independent auditor report", False),
            ("Member Statements", "Member balances and contributions", False),
            ("Investment Strategy", "Current documented investment strategy", False),
        ],
    },
}

OTHER_CHECKLISTS = {
    "individual": {
        "Identity": [
            ("Passport", "Valid passport bio page", True),
            ("Proof of Address", "Utility bill or bank statement last 3 months", True),
            ("Tax ID", "Local taxpayer identification number", True),
        ],
        "Tax": [
            ("Previous Tax Returns", "Last 2 years filed returns", False),
            ("Income Statements", "Employer or payer income statements", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
        ],
    },
    "sole_proprietor": {
        "Identity": [
            ("Owner Passport", "Valid passport bio page", True),
            ("Proof of Address", "Utility bill or bank statement last 3 months", True),
            ("Business Registration", "Local business or trade registration", True),
            ("Tax ID", "Business or personal taxpayer number", True),
        ],
        "Tax": [
            ("Previous Tax Returns", "Last 2 years filed returns", True),
            ("Indirect Tax Registration", "VAT/GST/sales tax registration if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "Business account 12 months", True),
            ("Income and Expense Records", "Current year sales and purchases", False),
        ],
    },
    "partnership": {
        "Identity": [
            ("Partnership Agreement", "Signed partnership deed or agreement", True),
            ("Business Registration", "Local registration certificate", True),
            ("Partners Passports", "Passport copies of all partners", True),
            ("Tax ID", "Partnership taxpayer number", True),
        ],
        "Tax": [
            ("Previous Tax Returns", "Last 2 years partnership returns", True),
            ("Indirect Tax Registration", "VAT/GST/sales tax registration if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Financial Statements", "Last 2 years if available", False),
        ],
    },
    "private_limited": {
        "Identity": [
            ("Certificate of Incorporation", "Company registration certificate", True),
            ("Constitutional Documents", "Articles, bylaws or memorandum", True),
            ("Register of Shareholders", "Shareholders and ownership percentages", True),
            ("Directors Passports", "Passport copies of all directors", True),
            ("UBO Declaration", "Ultimate beneficial owners", True),
            ("Tax ID", "Company taxpayer number", True),
        ],
        "Tax": [
            ("Previous Tax Returns", "Last 2 years corporate returns", True),
            ("Indirect Tax Registration", "VAT/GST/sales tax registration if applicable", False),
        ],
        "Financial": [
            ("Bank Statements", "All accounts 12 months", True),
            ("Financial Statements", "Last 2 years P&L and balance sheet", True),
            ("Board Resolution", "Authorising the firm to act", False),
        ],
    },
}

COUNTRY_MAP = {
    "India": INDIA_CHECKLISTS,
    "UAE": UAE_CHECKLISTS,
    "UK": UK_CHECKLISTS,
    "US": US_CHECKLISTS,
    "Singapore": SINGAPORE_CHECKLISTS,
    "Australia": AUSTRALIA_CHECKLISTS,
    "Other": OTHER_CHECKLISTS,
}

ENTITY_ALIASES = {
    "UK": {"sole_proprietor": "sole_trader"},
    "US": {"private_limited": "c_corp", "partnership": "llc", "llp": "llc"},
    "UAE": {"sole_trader": "sole_proprietor"},
    "Singapore": {"sole_trader": "sole_proprietor"},
    "Australia": {"sole_proprietor": "sole_trader", "public_limited": "private_limited"},
    "Other": {"sole_trader": "sole_proprietor", "llp": "partnership", "llc": "private_limited"},
}


def generate_checklist(country: str, entity_type: str, services: list) -> list[dict]:
    country_map = COUNTRY_MAP.get(country, OTHER_CHECKLISTS)
    aliases = ENTITY_ALIASES.get(country, {})
    resolved = aliases.get(entity_type, entity_type)
    entity_docs = (
        country_map.get(resolved)
        or country_map.get("private_limited")
        or next(iter(country_map.values()))
    )
    items: list[dict] = []
    order = 1
    services_lower = [str(s).lower() for s in (services or [])]
    for category, docs in entity_docs.items():
        if category in ("GST", "VAT") and category.lower() not in services_lower:
            continue
        for name, description, required in docs:
            items.append(
                {
                    "category": category,
                    "item_name": name,
                    "description": description,
                    "is_required": required,
                    "display_order": order,
                }
            )
            order += 1
    return items
