def classify_document(text):
    # Convert all text to lower case so it is easier to match words
    text_lower = text.lower()
    
    # If the document has no text, return Unclassifiable
    if not text.strip(): 
        return 'Unclassifiable'
        
    # We will score each document type based on how many weighted keywords we find
    scores = {'Invoice': 0.0, 'Resume': 0.0, 'Utility Bill': 0.0}
    
    # Dictionaries with words and their power (weight). 
    # Generic words get less points, highly specific words get more points.
    invoice_keywords = {
        'invoice': 3, 'bill': 2, 'balance due': 3, 'amount due': 3, 'gross total': 2,
        'subtotal': 2, 'tax': 1, 'payment terms': 2, 'vendor': 2, 'remit to': 2, 
        'inv:': 3, 'net payable': 2, 'paid via': 1
    }
    
    resume_keywords = {
        'resume': 4, 'curriculum vitae': 4, 'cv': 3, 'employment history': 3, 
        'work experience': 2, 'education': 1, 'skills': 1, 'certifications': 2,
        'objective': 0.5, 'summary': 0.5, 'projects': 0.5
    }
    
    utility_keywords = {
        'kwh': 3, 'meter no': 4, 'meter number': 3, 'energy charge': 3, 'kilowatt': 3, 
        'utility': 2, 'electricity': 2, 'gas charges': 4, 'gas consumed': 4, 'mmbtu': 4,
        'water': 2, 'account id': 4, 'account number': 2, 'consumer no': 4, 
        'billing month': 3, 'billing period': 2, 'service address': 2, 'consumption': 2,
        'sngpl': 5, 'ssgc': 5, 'lesco': 5, 'k-electric': 5
    }
    
    # Add up scores for Invoice
    for kw, weight in invoice_keywords.items(): 
        if kw in text_lower: 
            scores['Invoice'] += weight
            
    # Add up scores for Resume        
    for kw, weight in resume_keywords.items(): 
        if kw in text_lower: 
            scores['Resume'] += weight
            
    # Add up scores for Utility Bill
    for kw, weight in utility_keywords.items(): 
        if kw in text_lower: 
            scores['Utility Bill'] += weight
        
    # Find the document type that got the highest score
    max_class = max(scores, key=scores.get)
    
    # If the highest score is less than 4 points, it is probably just a general document (like a system design)
    if scores[max_class] < 4.0: 
        return 'Other'
        
    return max_class
