"""
Bilingual (Arabic/English) vocabulary used by the rule-based query engine:
business-term column aliases + intent keyword lists. No external API/model —
everything here is plain keyword/substring matching, tuned for a sales-style
analytics dataset (revenue, profit, quantity, region, category, product,
customer segment, date).
"""
from __future__ import annotations

import re

# --- Arabic text normalization -------------------------------------------------

_ARABIC_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْٰۖ-ۭ]")


def normalize_ar(text: str) -> str:
    """Lowercase (for any latin chars), strip diacritics, unify alef/ya/ta-marbuta
    variants, collapse whitespace — makes Arabic keyword matching far more robust
    against the spelling variation real users type."""
    text = text.strip().lower()
    text = _ARABIC_DIACRITICS.sub("", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize(text: str) -> str:
    """Normalize any input (Arabic or English) for matching."""
    return normalize_ar(text)


# --- Column business-term aliases ----------------------------------------------
# canonical_key -> list of keywords (English + normalized Arabic) that, if found
# as a substring of an actual column name (or vice-versa), identify that column.

COLUMN_ALIASES: dict[str, list[str]] = {
    "revenue": ["revenue", "sales", "income", "amount", "مبيعات", "ايراد", "دخل", "مبلغ"],
    "profit": ["profit", "margin", "earnings", "ربح", "ارباح", "هامش"],
    "quantity": ["quantity", "qty", "units", "count", "كميه", "عدد الوحدات"],
    "unit price": ["unit price", "price", "cost", "سعر", "تكلفه"],
    "region": ["region", "area", "city", "location", "منطقه", "مناطق", "مدينه", "مدن", "موقع"],
    "category": ["category", "type", "segment type", "فئه", "فئات", "تصنيف", "تصنيفات", "نوع", "انواع"],
    "product": ["product", "item", "sku", "منتج", "منتجات", "صنف", "اصناف"],
    "customer segment": ["customer segment", "segment", "channel", "شريحه", "شرائح", "قناه", "عميل"],
    "order date": ["order date", "date", "time", "month", "period", "تاريخ", "شهر", "شهور", "وقت", "فتره"],
    "order id": ["order id", "id", "order number", "رقم الطلب", "معرف"],
}

# --- Intent keyword lists (English + normalized Arabic) -----------------------

INTENT_KEYWORDS: dict[str, list[str]] = {
    "top_n": [
        "top", "highest", "best", "most", "biggest", "largest", "leading",
        "اعلى", "افضل", "اكثر", "اكبر",
    ],
    "bottom_n": [
        "bottom", "lowest", "worst", "least", "smallest", "weakest",
        "اقل", "اسوا", "الاقل", "اصغر", "ادنى",
    ],
    "why_decrease": [
        "why did", "why is", "why has", "decrease", "decline", "drop", "fall", "fell", "dropped", "declined", "down",
        "لماذا انخفض", "ليش قل", "ليش انخفض", "سبب انخفاض", "لماذا قل", "تراجع", "انخفض", "انخفاض", "هبوط",
    ],
    "why_increase": [
        "why did", "why is", "why has", "increase", "grow", "growth", "rise", "rose", "increased", "grew", "up", "improved",
        "لماذا ارتفع", "ليش زاد", "ليش ارتفع", "سبب ارتفاع", "لماذا زاد", "ارتفع", "ارتفاع", "زياده", "نمو", "زاد",
    ],
    "trend": [
        "trend", "over time", "monthly", "timeline", "trajectory", "progress",
        "اتجاه", "مع الوقت", "شهريا", "عبر الوقت", "تطور", "مسار",
    ],
    "compare": [
        "compare", "comparison", "versus", " vs ", "vs.", "difference between",
        "قارن", "مقارنه", "الفرق بين", "مقابل",
    ],
    "distribution": [
        "distribution", "breakdown", "split", "share", "percentage of", "proportion",
        "توزيع", "نسبه", "حصه", "تقسيم",
    ],
    "average": [
        "average", "avg", "mean", "typical",
        "متوسط", "معدل",
    ],
    "count": [
        "how many", "number of", "count of", "count",
        "كم عدد", "عدد", "كم مره",
    ],
    "total": [
        "total", "sum", "overall", "altogether", "in total", "grand total",
        "اجمالي", "مجموع", "الكلي", "كامل", "بالمجمل",
    ],
}

# Order matters when several intents tie on score — more specific first.
INTENT_PRIORITY = [
    "why_decrease", "why_increase", "compare", "top_n", "bottom_n",
    "trend", "distribution", "average", "count", "total",
]

# --- Data-value aliases (Arabic -> the English value it appears as in the data) ---
# Column values in the sample dataset are English (Riyadh, Electronics, ...), but a
# user typing a query in Arabic will name them in Arabic ("الرياض", "الكترونيات").
# This lets value-matching (e.g. for "compare") work in either language. Keys are
# matched after normalize_ar(), so spelling variants collapse automatically.
VALUE_ALIASES_AR_EN: dict[str, str] = {
    # regions / cities
    "الرياض": "Riyadh",
    "جده": "Jeddah",
    "الدمام": "Dammam",
    "مكه": "Makkah",
    "مكه المكرمه": "Makkah",
    "المدينه": "Madinah",
    "المدينه المنوره": "Madinah",
    # categories
    "الكترونيات": "Electronics",
    "إلكترونيات": "Electronics",
    "ملابس": "Clothing",
    "المنزل والمطبخ": "Home & Kitchen",
    "ادوات منزليه": "Home & Kitchen",
    "المطبخ": "Home & Kitchen",
    "تجميل": "Beauty",
    "مستحضرات تجميل": "Beauty",
    "رياضه": "Sports",
    # customer segments
    "تجزئه": "Retail",
    "جمله": "Wholesale",
    "اونلاين": "Online",
    "انترنت": "Online",
    "اون لاين": "Online",
}

MONTH_NAMES_AR = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "ابريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "اغسطس", 9: "سبتمبر", 10: "اكتوبر", 11: "نوفمبر", 12: "ديسمبر",
}
