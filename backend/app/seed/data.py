"""Demo seed data for ServeEasy, set around UTM Skudai.

Pure data: nothing here touches the database. Every row has a stable id derived
from a slug (uuid5), so the same slug always yields the same id. That is what
lets the seed runner upsert idempotently.

Names of colleges and landmarks are real UTM places. Every person, cafeteria
business, email address, phone number and payment reference is fictional.
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import quote_plus

from app.models.base import (
    BookingStatus,
    ListingCategory as Cat,
    ListingCondition as Cond,
    ListingStatus,
    MealSession,
    OrderStatus,
    ServiceCategory,
    UserRole,
)

_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://serveeasy.example/seed")
_BASE_TIME = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)
_TODAY = date(2026, 11, 11)

Row = dict[str, Any]


def uid(kind: str, slug: str) -> str:
    """Deterministic id: the same (kind, slug) always gives the same uuid string."""
    return str(uuid.uuid5(_NAMESPACE, f"{kind}:{slug}"))


def _img(label: str) -> str:
    return f"https://placehold.co/600x400?text={quote_plus(label)}"


def _at(hours: float) -> datetime:
    return _BASE_TIME + timedelta(hours=hours)


# --------------------------------------------------------------------------- users
USERS: list[Row] = []


def _user(slug, name, role, *, student_id=None, email=None, phone, hours=0.0) -> str:
    user_id = uid("user", slug)
    USERS.append(
        {
            "id": user_id,
            "name": name,
            "email": email or f"{slug}@graduate.utm.my",
            "email_verified": True,
            "image": _img(name.split()[0]),
            "student_id": student_id,
            "role": role,
            "phone": phone,
            "created_at": _at(hours),
            "updated_at": _at(hours),
        }
    )
    return user_id


S, F, P = UserRole.STUDENT, UserRole.FOOD_SELLER, UserRole.SERVICE_PROVIDER

# Students (KTR = Kolej Tun Razak, KTDI = Kolej Tun Dr. Ismail, KDSE = Kolej Datin Seri Endon,
# KTF = Kolej Tun Fatimah, KTHO = Kolej Tun Hussein Onn, KDOJ = Kolej Dato' Onn Jaafar)
aisyah = _user("aisyah.rahman", "Aisyah Rahman", S, student_id="A23CS0114", phone="+60 11-0000 0101")
haziq = _user("haziq.zulkifli", "Haziq Zulkifli", S, student_id="A22EE0231", phone="+60 11-0000 0102")
nurul = _user("nurul.izzati", "Nurul Izzati", S, student_id="A24BE0087", phone="+60 11-0000 0103")
farhan = _user("farhan.hakim", "Farhan Hakim", S, student_id="A23ME0345", phone="+60 11-0000 0104")
weijie = _user("tan.weijie", "Tan Wei Jie", S, student_id="A22CS0412", phone="+60 11-0000 0105")
priya = _user("priya.nair", "Priya Nair", S, student_id="A24SC0156", phone="+60 11-0000 0106")
daniel = _user("daniel.lim", "Daniel Lim", S, student_id="A21CE0278", phone="+60 11-0000 0107")
siti = _user("siti.aminah", "Siti Aminah", S, student_id="A23AR0063", phone="+60 11-0000 0108")

# Food sellers (external cafeterias, so no student id)
kakmin = _user("kakmin.kitchen", "Kak Min", F, email="kakmin.kitchen@serveeasy.example", phone="+60 11-0000 0201", hours=1)
paklah = _user("paklah.warung", "Pak Lah", F, email="paklah.warung@serveeasy.example", phone="+60 11-0000 0202", hours=1)
maksiti = _user("maksiti.dapur", "Mak Siti", F, email="maksiti.dapur@serveeasy.example", phone="+60 11-0000 0203", hours=1)
westerncorner = _user("western.corner", "Western Corner KTR", F, email="western.corner@serveeasy.example", phone="+60 11-0000 0204", hours=1)

# Service providers (students offering services, as per the PRD)
amir = _user("amir.syafiq", "Amir Syafiq", P, student_id="A22FC0190", phone="+60 11-0000 0301")
nadia = _user("nadia.kamal", "Nadia Kamal", P, student_id="A23FS0222", phone="+60 11-0000 0302")
jason = _user("jason.ong", "Jason Ong", P, student_id="A21EE0309", phone="+60 11-0000 0303")

# --------------------------------------------------------------- product listings
LISTINGS: list[Row] = []


def _listing(slug, seller, title, price, cond, cat, desc, *, status=ListingStatus.ACTIVE, hours=24.0):
    LISTINGS.append(
        {
            "id": uid("listing", slug),
            "seller_id": seller,
            "title": title,
            "description": desc,
            "price": Decimal(price),
            "condition": cond,
            "category": cat,
            "image": _img(title),
            "status": status,
            "created_at": _at(hours),
        }
    )


_listing("calc-fx570", aisyah, "Casio FX-570EX Scientific Calculator", "45.00", Cond.GOOD, Cat.ELECTRONICS,
         "Used for two semesters, all keys work. Cover included. Pickup at KTR lobby.", hours=24)
_listing("engmath-text", haziq, "Advanced Engineering Mathematics (Kreyszig)", "55.00", Cond.GOOD, Cat.BOOKS,
         "Some highlighting in chapters 1-6. Good for SEEE courses. Can meet at Perpustakaan Sultanah Zanariah.", hours=25)
_listing("c-prog-book", weijie, "C Programming: A Modern Approach", "38.00", Cond.LIKE_NEW, Cat.BOOKS,
         "Barely opened. Selling because I finished the course.", hours=26)
_listing("db-systems-book", aisyah, "Database System Concepts (7th ed.)", "60.00", Cond.GOOD, Cat.BOOKS,
         "Clean copy, no missing pages. Useful for SECD2523.", hours=27)
_listing("thermo-text", farhan, "Fundamentals of Thermodynamics", "50.00", Cond.FAIR, Cat.BOOKS,
         "Cover worn but all pages intact. Mechanical engineering students welcome.", hours=28)
_listing("study-lamp", nurul, "LED Study Lamp (USB)", "18.00", Cond.LIKE_NEW, Cat.ELECTRONICS,
         "Three brightness levels, clip-on. Works great on a hostel desk.", hours=29)
_listing("mini-fan", priya, "Rechargeable Mini Desk Fan", "22.00", Cond.GOOD, Cat.ELECTRONICS,
         "Battery lasts about 5 hours. Saved me through the KTDI heat.", hours=30)
_listing("laptop-stand", weijie, "Aluminium Laptop Stand", "30.00", Cond.LIKE_NEW, Cat.ELECTRONICS,
         "Foldable, fits up to 15.6 inch laptops.", hours=31)
_listing("monitor-24", daniel, "24-inch Dell Monitor (1080p)", "260.00", Cond.GOOD, Cat.ELECTRONICS,
         "HDMI and VGA. No dead pixels. Pickup at KTHO.", hours=32)
_listing("keyboard-mech", haziq, "Mechanical Keyboard (Blue Switch)", "85.00", Cond.GOOD, Cat.ELECTRONICS,
         "TKL layout, USB-C. A few shiny keycaps.", hours=33)
_listing("headphones", siti, "Wireless Headphones", "70.00", Cond.FAIR, Cat.ELECTRONICS,
         "Battery has slight degradation. Still gives about 10 hours.", status=ListingStatus.SOLD, hours=34)
_listing("study-desk", daniel, "Foldable Study Desk", "40.00", Cond.GOOD, Cat.FURNITURE,
         "Light and easy to move between colleges. Selling because I am moving to off-campus housing.", hours=35)
_listing("bookshelf", nurul, "Small 3-Tier Bookshelf", "35.00", Cond.GOOD, Cat.FURNITURE,
         "Fits in a KTR double room. Must collect yourself.", hours=36)
_listing("bean-bag", priya, "Bean Bag Chair", "55.00", Cond.FAIR, Cat.FURNITURE,
         "Cover washed, filling a bit flat.", hours=37)
_listing("baju-melayu", farhan, "Baju Melayu Set (Size L, Navy)", "60.00", Cond.LIKE_NEW, Cat.CLOTHING,
         "Worn once for a faculty event. Includes samping.", hours=38)
_listing("blazer", siti, "Black Blazer (Size M)", "45.00", Cond.GOOD, Cat.CLOTHING,
         "Good for presentations and interviews.", hours=39)
_listing("lab-coat", aisyah, "White Lab Coat (Size S)", "15.00", Cond.GOOD, Cat.CLOTHING,
         "Washed, no stains. Fits small to medium.", hours=40)
_listing("rice-cooker", nurul, "Mini Rice Cooker (0.6L)", "25.00", Cond.GOOD, Cat.KITCHEN,
         "Perfect for one person. Includes spatula.", hours=41)
_listing("kettle", haziq, "Electric Kettle 1L", "20.00", Cond.GOOD, Cat.KITCHEN,
         "Works well, new plug recently.", hours=42)
_listing("blender", priya, "Portable Blender", "28.00", Cond.LIKE_NEW, Cat.KITCHEN,
         "USB rechargeable. Great for smoothies in the hostel.", hours=43)
_listing("drawing-set", siti, "Architecture Drawing Set", "75.00", Cond.GOOD, Cat.STATIONERY,
         "T-square, set squares, scale ruler and technical pens. For architecture students.", hours=44)
_listing("a3-board", siti, "A3 Drawing Board", "40.00", Cond.GOOD, Cat.STATIONERY,
         "Slightly scratched but flat and usable.", hours=45)
_listing("badminton-racket", farhan, "Yonex Badminton Racket", "65.00", Cond.GOOD, Cat.SPORTS,
         "Restrung last month. Comes with a cover.", hours=46)
_listing("futsal-shoes", daniel, "Futsal Shoes (Size 42)", "48.00", Cond.FAIR, Cat.SPORTS,
         "Used for one semester of inter-college matches.", hours=47)
_listing("bicycle", weijie, "City Bicycle", "180.00", Cond.GOOD, Cat.OTHER,
         "Great for getting around campus. Basket and lock included.", hours=48)

# ------------------------------------------------------------ food items (menus)
FOOD_ITEMS: list[Row] = []
_ITEM_BY_SLUG: dict[str, Row] = {}

L, D = MealSession.LUNCH, MealSession.DINNER


def _food(slug, seller, name, price, session, *, available=True) -> None:
    row = {
        "id": uid("food", slug),
        "seller_id": seller,
        "name": name,
        "price": Decimal(price),
        "meal_session": session,
        "available": available,
        "image": _img(name),
    }
    FOOD_ITEMS.append(row)
    _ITEM_BY_SLUG[slug] = row


# Kak Min: Malay rice dishes
_food("km-nasi-ayam", kakmin, "Nasi Ayam Penyet", "8.50", L)
_food("km-nasi-lemak", kakmin, "Nasi Lemak Ayam Goreng", "7.50", L)
_food("km-nasi-kerabu", kakmin, "Nasi Kerabu", "9.00", L)
_food("km-sup-ayam", kakmin, "Nasi Sup Ayam", "8.00", D)
_food("km-ayam-masak-merah", kakmin, "Nasi Ayam Masak Merah", "8.50", D)
_food("km-teh-ais", kakmin, "Teh Ais", "2.00", L)

# Pak Lah: noodles
_food("pl-mee-rebus", paklah, "Mee Rebus", "6.50", L)
_food("pl-mee-goreng", paklah, "Mee Goreng Mamak", "7.00", L)
_food("pl-laksa", paklah, "Laksa Johor", "8.00", D)
_food("pl-kuey-teow", paklah, "Kuey Teow Goreng", "7.50", D)
_food("pl-bandung", paklah, "Air Bandung", "2.50", D, available=False)

# Mak Siti: home-style cooking
_food("ms-nasi-campur", maksiti, "Nasi Campur (3 lauk)", "9.50", L)
_food("ms-asam-pedas", maksiti, "Ikan Asam Pedas + Nasi", "10.00", L)
_food("ms-ayam-kicap", maksiti, "Ayam Masak Kicap + Nasi", "8.50", D)
_food("ms-sayur-lodeh", maksiti, "Sayur Lodeh Set", "7.50", D)

# Western Corner KTR
_food("wc-chicken-chop", westerncorner, "Chicken Chop", "11.90", L)
_food("wc-spaghetti", westerncorner, "Spaghetti Bolognese", "9.90", L)
_food("wc-fish-chips", westerncorner, "Fish and Chips", "12.50", D)
_food("wc-burger", westerncorner, "Beef Burger Set", "10.50", D)
_food("wc-lemon-tea", westerncorner, "Iced Lemon Tea", "3.00", D)

# ------------------------------------------------------------------- food orders
FOOD_ORDERS: list[Row] = []
ORDER_LINE_ITEMS: list[Row] = []

_PS = OrderStatus


def _order(slug, buyer, seller, lines, status, note, ref, *, hours) -> None:
    order_id = uid("order", slug)
    total = Decimal("0.00")
    for n, (item_slug, qty) in enumerate(lines, start=1):
        item = _ITEM_BY_SLUG[item_slug]
        assert item["seller_id"] == seller, f"{item_slug} does not belong to this seller"
        total += item["price"] * qty
        ORDER_LINE_ITEMS.append(
            {
                "id": uid("line", f"{slug}:{n}"),
                "order_id": order_id,
                "item_id": item["id"],
                "quantity": qty,
                "unit_price": item["price"],
            }
        )
    FOOD_ORDERS.append(
        {
            "id": order_id,
            "buyer_id": buyer,
            "seller_id": seller,
            "total": total,
            "pickup_note": note,
            "payment_ref": ref,
            "payment_proof": _img(f"Payment proof {ref}") if ref else None,
            "status": status,
            "created_at": _at(hours),
        }
    )


_order("o1", aisyah, kakmin, [("km-nasi-ayam", 1), ("km-teh-ais", 1)], _PS.COMPLETED,
       "Pickup at Kolej Tun Razak lobby, 12.30pm", "DUITNOW-20261103-0011", hours=72)
_order("o2", haziq, paklah, [("pl-mee-rebus", 2)], _PS.COMPLETED,
       "Pickup at KTDI main gate", "TNG-20261104-0207", hours=96)
_order("o3", nurul, maksiti, [("ms-nasi-campur", 1), ("ms-asam-pedas", 1)], _PS.READY,
       "Collect at Kolej Datin Seri Endon guardhouse", "DUITNOW-20261110-0033", hours=200)
_order("o4", weijie, westerncorner, [("wc-fish-chips", 1), ("wc-lemon-tea", 1)], _PS.CONFIRMED,
       "Dinner pickup at KTR cafe, 7pm", "DUITNOW-20261111-0048", hours=215)
_order("o5", priya, kakmin, [("km-sup-ayam", 2), ("km-ayam-masak-merah", 1)], _PS.PENDING,
       "Pickup at Kolej Tun Fatimah, 6.45pm", "TNG-20261111-0052", hours=217)
_order("o6", daniel, westerncorner, [("wc-chicken-chop", 1)], _PS.CANCELLED,
       "Cancelled: missed lunch cut-off", None, hours=190)

# ------------------------------------------------------------------ services
SERVICES: list[Row] = []


def _service(slug, provider, title, price, cat, desc) -> None:
    SERVICES.append(
        {
            "id": uid("service", slug),
            "provider_id": provider,
            "title": title,
            "description": desc,
            "price": Decimal(price),
            "category": cat,
        }
    )


SC = ServiceCategory
_service("print-bw", amir, "Black & White Printing (per page)", "0.10", SC.PRINTING,
         "A4 B&W printing from PDF. Pickup at Fakulti Komputeran. Minimum 10 pages.")
_service("print-colour", amir, "Colour Printing & Poster A3", "2.00", SC.PRINTING,
         "Colour A3 posters and project boards. Price is per sheet, ready in 1 day.")
_service("tailor-alter", nadia, "Clothing Alteration", "12.00", SC.TAILORING,
         "Hemming, taking in and letting out. Baju kurung, shirts, trousers.")
_service("tailor-baju", nadia, "Custom Baju Kurung", "85.00", SC.TAILORING,
         "Made to measure. Bring your own fabric. Takes about 2 weeks.")
_service("repair-laptop", jason, "Laptop Cleaning & Thermal Paste", "35.00", SC.REPAIR,
         "Fan cleaning and new thermal paste. Fixes overheating. Takes about 2 hours.")
_service("repair-phone", jason, "Phone Screen Replacement", "120.00", SC.REPAIR,
         "Screen swaps for popular models. Part cost included. Please confirm your model first.")
_service("repair-bike", jason, "Bicycle Tune-Up", "15.00", SC.REPAIR,
         "Brake adjustment, chain oiling and tyre check.")

# -------------------------------------------------------------- service bookings
SERVICE_BOOKINGS: list[Row] = []


def _booking(slug, student, service_slug, details, days_ahead, status, *, hours) -> None:
    SERVICE_BOOKINGS.append(
        {
            "id": uid("booking", slug),
            "student_id": student,
            "service_id": uid("service", service_slug),
            "details": details,
            "requested_date": _TODAY + timedelta(days=days_ahead),
            "status": status,
            "created_at": _at(hours),
        }
    )


BS = BookingStatus
_booking("b1", siti, "print-colour", "5 sheets of A3 colour for my studio board. PDF in chat.", 2, BS.ACCEPTED, hours=205)
_booking("b2", weijie, "repair-laptop", "Laptop gets very hot during compile. Lenovo ThinkPad.", 3, BS.PENDING, hours=212)
_booking("b3", aisyah, "tailor-alter", "Need a baju kurung hemmed by about 3 cm.", 5, BS.ACCEPTED, hours=210)
_booking("b4", farhan, "repair-bike", "Brakes feel loose.", -4, BS.COMPLETED, hours=100)
_booking("b5", priya, "repair-phone", "Cracked screen on a Samsung A54.", 4, BS.DECLINED, hours=208)

# ------------------------------------------------------------------- messages
MESSAGES: list[Row] = []


def _thread(slug, turns, start_hours) -> None:
    """turns is a list of (sender_id, receiver_id, text); each is 5 minutes after the last."""
    for n, (sender, receiver, text) in enumerate(turns, start=1):
        MESSAGES.append(
            {
                "id": uid("message", f"{slug}:{n}"),
                "sender_id": sender,
                "receiver_id": receiver,
                "content": text,
                "created_at": _at(start_hours) + timedelta(minutes=5 * n),
            }
        )


_thread(
    "calc-inquiry",
    [
        (weijie, aisyah, "Hi, is the Casio FX-570EX still available?"),
        (aisyah, weijie, "Yes it is! Still RM45."),
        (weijie, aisyah, "Can do RM40? I can collect at KTR lobby today."),
        (aisyah, weijie, "RM42 and we have a deal."),
        (weijie, aisyah, "Deal. See you at 5pm."),
    ],
    150,
)
_thread(
    "order-o5",
    [
        (priya, kakmin, "Hi Kak Min, I just sent the TNG payment for the sup ayam order."),
        (kakmin, priya, "Got it, will confirm the order shortly."),
        (priya, kakmin, "Thank you! Can I pick up at 6.45pm?"),
    ],
    217,
)
_thread(
    "booking-b2",
    [
        (weijie, jason, "Hi Jason, can you look at my laptop on Friday?"),
        (jason, weijie, "Sure, bring it to Kolej Tun Dr. Ismail cafe around 3pm."),
        (weijie, jason, "Perfect, thanks!"),
    ],
    213,
)
_thread(
    "monitor-inquiry",
    [
        (haziq, daniel, "Hello, does the Dell monitor come with an HDMI cable?"),
        (daniel, haziq, "Yes, HDMI cable and power cable both included."),
    ],
    160,
)

# ------------------------------------------------------------------- registry
# Parents first, so the seed runner can insert in this order without violating FKs.
TABLES: list[tuple[str, list[Row]]] = [
    ("users", USERS),
    ("product_listings", LISTINGS),
    ("food_items", FOOD_ITEMS),
    ("services", SERVICES),
    ("food_orders", FOOD_ORDERS),
    ("order_line_items", ORDER_LINE_ITEMS),
    ("service_bookings", SERVICE_BOOKINGS),
    ("messages", MESSAGES),
]


def summary() -> dict[str, int]:
    return {name: len(rows) for name, rows in TABLES}


if __name__ == "__main__":
    for name, count in summary().items():
        print(f"{name:20} {count}")
