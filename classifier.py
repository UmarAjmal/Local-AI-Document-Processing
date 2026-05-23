def classify_document(text):
    # Convert all text to lower case so it is easier to match words
    text_lower = text.lower()
    
    # If the document has no text, return Unclassifiable
    if not text.strip(): 
        return 'Unclassifiable'
        
    # We will score each document type based on how many keywords we find
    scores = {'Invoice': 0, 'Resume': 0, 'Utility Bill': 0}
    
    # Lists of words that usually appear in these types of documents
    invoice_keywords = ['invoice', 'bill', 'subtotal', 'tax', 'balance due', 'payment terms', 'due date', 'vendor', 'remit to', 'amount due', 'total amount', 'inv:', 'net payable', 'gross total', 'paid via']
    resume_keywords = ['resume', 'curriculum vitae', 'cv', 'experience', 'education', 'skills', 'objective', 'summary', 'projects', 'employment history', 'certifications']
    utility_keywords = ['utility', 'electricity', 'gas', 'water', 'kwh', 'meter number', 'account number', 'billing period', 'energy charge', 'consumption', 'service address', 'kilowatt']
    
    # Count how many invoice keywords are in the text
    for kw in invoice_keywords: 
        if kw in text_lower: 
            scores['Invoice'] += 1
            
    # Count how many resume keywords are in the text        
    for kw in resume_keywords: 
        if kw in text_lower: 
            scores['Resume'] += 1
            
    # Count how many utility keywords are in the text
    for kw in utility_keywords: 
        if kw in text_lower: 
            scores['Utility Bill'] += 1
        
    # Find the document type that got the highest score
    max_class = max(scores, key=scores.get)
    
    # If the highest score is less than 2, it is probably something else
    if scores[max_class] < 2: 
        return 'Other'
        
    return max_class
