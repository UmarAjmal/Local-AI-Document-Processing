import re

def extract_fields(text, doc_class):
    """
    Extracts structured fields using robust Python Regex that handles
    different naming variations and formatting inside the document text.
    """
    fields = {"class": doc_class}
    
    if doc_class == "Invoice":
        # Matches: "Invoice # 123", "INV: 123", "Invoice Number: 123"
        inv_match = re.search(r"(?:invoice|inv)\s*(?:number|#|no\.?)?[\s:]*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        # Matches typical date formats (YYYY-MM-DD, DD/MM/YYYY)
        date_match = re.search(r"(\d{2,4}[-/.]\d{2}[-/.]\d{2,4})", text)
        # First word after company/vendor or assume standard placement
        company_match = re.search(r"(?:company|vendor|from)[\s:]*([A-Za-z0-9\s]+)", text, re.IGNORECASE)
        # Matches: "Total Amount: $350.50", "Amount Due: 350.50"
        amount_match = re.search(r"(?:total(?: amount)?|amount due|balance due)[\s:\$]*([\d,]+\.?\d*)", text, re.IGNORECASE)
        
        fields["invoice_number"] = inv_match.group(1).strip() if inv_match else None
        fields["date"] = date_match.group(1).strip() if date_match else None
        fields["company"] = company_match.group(1).strip() if company_match else None
        fields["total_amount"] = float(amount_match.group(1).replace(',', '')) if amount_match else None
        
    elif doc_class == "Resume":
        name_match = re.search(r"(?:name)[\s:]*([A-Za-z\s]+)", text, re.IGNORECASE)
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        exp_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)", text, re.IGNORECASE)
        
        fields["name"] = name_match.group(1).strip() if name_match else None
        fields["email"] = email_match.group(0).strip() if email_match else None
        fields["phone"] = phone_match.group(0).strip() if phone_match else None
        fields["experience_years"] = int(exp_match.group(1)) if exp_match else None
        
    elif doc_class == "Utility Bill":
        acc_match = re.search(r"(?:account|acc)\s*(?:number|#|no\.?)?[\s:]*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        date_match = re.search(r"(\d{2,4}[-/.]\d{2}[-/.]\d{2,4})", text)
        usage_match = re.search(r"(?:usage|consumption)[\s:]*([\d,]+\.?\d*)\s*(?:kwh)?", text, re.IGNORECASE)
        amount_match = re.search(r"(?:amount|amount due|total|balance)[\s:\$]*([\d,]+\.?\d*)", text, re.IGNORECASE)
        
        fields["account_number"] = acc_match.group(1).strip() if acc_match else None
        fields["date"] = date_match.group(1).strip() if date_match else None
        fields["usage_kwh"] = float(usage_match.group(1).replace(',', '')) if usage_match else None
        fields["amount_due"] = float(amount_match.group(1).replace(',', '')) if amount_match else None
        
    return fields
