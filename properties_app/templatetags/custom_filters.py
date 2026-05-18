from django import template

register = template.Library()

@register.filter(name='indian_rupee')
def indian_rupee(value):
    """
    Converts a number into Indian Rupee format (e.g., 10,00,000).
    """
    try:
        if value is None:
            return "0"
        value = int(float(value))
    except (ValueError, TypeError):
        return value
    
    is_negative = value < 0
    value = abs(value)
    
    value_str = str(value)
    if len(value_str) <= 3:
        formatted = value_str
    else:
        last_three = value_str[-3:]
        other_digits = value_str[:-3]
        
        parts = []
        while len(other_digits) > 2:
            parts.insert(0, other_digits[-2:])
            other_digits = other_digits[:-2]
        
        if other_digits:
            parts.insert(0, other_digits)
            
        formatted = ','.join(parts) + ',' + last_three
        
    if is_negative:
        return "-" + formatted
    return formatted

def _get_two_digits_words(n):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if n < 20:
        return ones[n]
    else:
        return tens[n // 10] + (" " + ones[n % 10] if (n % 10 != 0) else "")

@register.filter(name='indian_words')
def indian_words(value):
    """
    Converts a number into English words using the Indian numbering system.
    """
    try:
        if value is None:
            return ""
        num = int(float(value))
    except (ValueError, TypeError):
        return ""
        
    if num == 0:
        return "Zero"
        
    is_negative = num < 0
    num = abs(num)
    
    parts = []
    
    crores = num // 10000000
    num = num % 10000000
    
    lakhs = num // 100000
    num = num % 100000
    
    thousands = num // 1000
    num = num % 1000
    
    hundreds = num // 100
    num = num % 100
    
    if crores > 0:
        parts.append(_get_two_digits_words(crores) + " Crore")
    if lakhs > 0:
        parts.append(_get_two_digits_words(lakhs) + " Lakh")
    if thousands > 0:
        parts.append(_get_two_digits_words(thousands) + " Thousand")
    if hundreds > 0:
        parts.append(_get_two_digits_words(hundreds) + " Hundred")
    if num > 0:
        parts.append(_get_two_digits_words(num))
        
    words = " ".join(parts).strip()
    if is_negative:
        return "Minus " + words
    return words
