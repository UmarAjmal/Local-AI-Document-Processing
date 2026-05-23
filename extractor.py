import re

def extract_fields(text, doc_class):
    # Store the document type in our result dictionary
    fields = {'class': doc_class}
    
    # Remove extra spaces or new lines to make the text clean
    clean_text = re.sub(r'\s+', ' ', text)
    
    # Break text into separate lines and remove empty ones
    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 3]
    
    # Find all possible dates anywhere in the text using a generic pattern
    all_dates = re.findall(r'\b(?:\d{1,2}[-/.]\s*[A-Za-z]{3,9}\s*[-/.]\d{2,4}|\d{2,4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b', clean_text)
    all_dates = [d for d in all_dates if len(d) >= 6]
    
    # Find anything that looks like money anywhere in the document
    all_money = re.findall(r'(?:Rs\.?|PKR|USD|EUR|GBP|CAD|\$|€|£)?\s*([\d,]+\.\d{1,2}|[\d,]+)\b', clean_text)
    money_floats = []
    
    # Convert all found money completely into simple numbers
    for m in all_money:
        try: 
            money_floats.append(float(m.replace(',', '')))
        except: 
            pass
    
    # Look at the top few lines of the document to find company names
    top_text = " ".join(lines[:5]) if len(lines) >= 5 else " ".join(lines)
    
    # Fallback plan. If we cannot find a company name, we take the top non generic line
    fallback_company = None
    for line in lines[:5]:
        line_clean = line.strip().upper()
        # Ignore basic titles like LOGO or INVOICE
        if line_clean not in ["LOGO", "INVOICE", "BILL", "RECEIPT", "STATEMENT"] and len(line_clean) > 3:
            fallback_company = line
            break
            
    # Rules if the document is an Invoice
    if doc_class == 'Invoice':
        # Search anywhere for words like INV followed by a number
        inv_match = re.search(r'(?:invoice|inv|ref|bill|receipt|#|no\.?|order)\s*[:.\-]?\s*([A-Za-z0-9\-]{4,20})', clean_text, re.IGNORECASE)
        fields['invoice_number'] = inv_match.group(1).strip() if inv_match else None
        
        # Pick the first date we found
        fields['date'] = all_dates[0] if all_dates else None
        
        # Search the top block for words like LTD or LLC and save company
        comp_match = re.search(r'\b([A-Z][A-Za-z0-9\-&\s]+(?:LTD|LLC|INC|CORP|PHARMACY|CLINIC|STORE|SERVICES|SYSTEMS?))\b', top_text, re.IGNORECASE)
        fields['company'] = comp_match.group(1).strip() if comp_match else fallback_company
        
        # Rule of math. The biggest number in an invoice is usually the Total Amount
        fields['total_amount'] = max(money_floats) if money_floats else None


    # Rules if the document is a Resume
    elif doc_class == 'Resume':
        # Look for the word Name and grab the words after it
        name_match = re.search(r'(?:name)[\s:\-]*([A-Za-z\s]{3,40}?)(?:\s*(?:email|phone|address|education|experience|objective|$))', clean_text, re.IGNORECASE)
        if name_match:
            fields['name'] = name_match.group(1).strip()
        else:
            # If no clear Name field, take the first short line at the top
            for l in lines[:10]:
                if len(l.split()) <= 4 and not re.search(r'(resume|cv|summary|profile|email|phone)', l, re.IGNORECASE):
                    fields['name'] = l
                    break

        # Check for any valid email address
        email_match = re.search(r'\b[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+\b', clean_text)
        fields['email'] = email_match.group(0).strip() if email_match else None
        
        # Check for a phone number layout
        phone_match = re.search(r'(?:(?:\+|00)\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}', clean_text)
        fields['phone'] = phone_match.group(0).strip() if phone_match else None
        
        # Check for numbers placed near the word experience
        exp_match = re.search(r'(\d+)\s*(?:\+|to|and)?\s*(?:years?|yrs?|yr).{0,30}(?:experience|skills|working|development|proficient)', clean_text, re.IGNORECASE)
        fields['experience_years'] = int(exp_match.group(1)) if exp_match else None
        
    # Rules if the document is a Utility Bill
    elif doc_class == 'Utility Bill':
        # Search for words ending with account, and grab the number
        acc_match = re.search(r'(?:account|acc(?:t)?|customer|ref|meter)\s*(?:number|num|#|no\.?|id)?\s*[:.\-]?\s*([A-Z0-9\-]{5,20})', clean_text, re.IGNORECASE)
        fields['account_number'] = acc_match.group(1).strip() if acc_match else None
        
        # Grab the first date inside the bill
        fields['date'] = all_dates[0] if all_dates else None
        
        # Grab the number that comes before kwh or units
        usage_match = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:kwh|units|units consumed|reading)\b', clean_text, re.IGNORECASE)
        try: 
            fields['usage_kwh'] = float(usage_match.group(1).replace(',', '')) if usage_match else None
        except: 
            fields['usage_kwh'] = None
        
        # Rule of math again. The highest money found relates to the bill amount due
        fields['amount_due'] = max(money_floats) if money_floats else None
            
    return fields
