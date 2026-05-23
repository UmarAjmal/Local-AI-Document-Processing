def classify_document(text):
    """
    Classifies a document using a keyword-density scoring system.
    This ensures we identify the document by its actual overall content, 
    not just one word or the filename.
    """
    text_lower = text.lower()
    
    if not text.strip():
        return "Unclassifiable"
        
    # Define vocabulary sets for each document type
    scores = {
        "Invoice": 0,
        "Resume": 0,
        "Utility Bill": 0
    }
    
    invoice_keywords = ['invoice', 'bill to', 'amount due', 'total amount', 'subtotal', 'tax', 'balance due', 'payment terms', 'due date', 'vendor']
    resume_keywords = ['resume', 'curriculum vitae', 'cv', 'experience', 'education', 'skills', 'objective', 'summary', 'projects', 'employment history', 'profile']
    utility_keywords = ['utility', 'electricity', 'gas', 'water', 'kwh', 'meter number', 'account number', 'billing period', 'energy charge', 'consumption']
    
    # Calculate score based on how many keywords match
    for kw in invoice_keywords:
        if kw in text_lower: scores["Invoice"] += 1
        
    for kw in resume_keywords:
        if kw in text_lower: scores["Resume"] += 1
        
    for kw in utility_keywords:
        if kw in text_lower: scores["Utility Bill"] += 1
        
    # Get the class with the highest score
    max_class = max(scores, key=scores.get)
    
    # If no significant keywords found at all, fallback to Other
    if scores[max_class] == 0:
        return "Other"
        
    return max_class
