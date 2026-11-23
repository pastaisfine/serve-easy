"""Demo seed data for ServeEasy, set around UTM Skudai.

Pure data: nothing here touches the database. Every row has a stable id derived
from a slug (uuid5), so the same slug always yields the same id. That is what
lets the seed runner upsert idempotently.

What is real and what is made up:
- Real: UTM place names, and the details of The Cube (supplied by the project owner:
  a student-run dessert and shaved ice shop, location, hours and menu highlights).
- Fictional: every person (including The Cube's owner account), the other shops,
  cafeteria businesses, emails, phone numbers and payment references.
- Photos are Unsplash images that the frontend already uses (allowed in its
  next.config.ts). They are matched to categories by hand and not all are exact fits.
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import quote_plus

from app.seed import photos
from app.seed.catalog_listings import LISTING_ROWS
from app.seed.catalog_services import SERVICE_ROWS
from app.seed.photo_groups import listing_group, service_group
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
    """Text placeholder, used where no suitable photo exists (avatars, menu items, shop logos).

    PNG, not placehold.co's default SVG, because next/image refuses SVG by default.
    """
    return f"https://placehold.co/600x400/png?text={quote_plus(label)}"


def _photo(photo_id: str, width: int = 600) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?w={width}&q=75&auto=format&fit=crop"


_FOOD_PHOTO = "1567620905732-2d1ec7ab7445"
def _at(hours: float) -> datetime:
    return _BASE_TIME + timedelta(hours=hours)


# --------------------------------------------------------------------------- users
USERS: list[Row] = []


def _user(slug, name, role, *, student_id=None, faculty=None, email=None, phone, image=None, hours=0.0) -> str:
    user_id = uid("user", slug)
    USERS.append(
        {
            "id": user_id,
            "name": name,
            "email": email or f"{slug}@graduate.utm.my",
            "email_verified": True,
            "image": image or _img(name.split()[0]),
            "student_id": student_id,
            "role": role,
            "phone": phone,
            "faculty": faculty,
            "created_at": _at(hours),
            "updated_at": _at(hours),
        }
    )
    return user_id


S, F, P = UserRole.STUDENT, UserRole.FOOD_SELLER, UserRole.SERVICE_PROVIDER

COMPUTING = "Faculty of Computing"
ELECTRICAL = "Faculty of Electrical Engineering"
MECHANICAL = "Faculty of Mechanical Engineering"
CIVIL = "Faculty of Civil Engineering"
BUILT_ENV = "Faculty of Built Environment and Surveying"
SCIENCE = "Faculty of Science"

# Students (KTR = Kolej Tun Razak, KTDI = Kolej Tun Dr. Ismail, KDSE = Kolej Datin Seri Endon,
# KTF = Kolej Tun Fatimah, KTHO = Kolej Tun Hussein Onn, KDOJ = Kolej Dato' Onn Jaafar)
aisyah = _user("aisyah.rahman", "Aisyah Rahman", S, student_id="A23CS0114", faculty=COMPUTING, phone="+60 11-0000 0101")
haziq = _user("haziq.zulkifli", "Haziq Zulkifli", S, student_id="A22EE0231", faculty=ELECTRICAL, phone="+60 11-0000 0102")
nurul = _user("nurul.izzati", "Nurul Izzati", S, student_id="A24BE0087", faculty=BUILT_ENV, phone="+60 11-0000 0103")
farhan = _user("farhan.hakim", "Farhan Hakim", S, student_id="A23ME0345", faculty=MECHANICAL, phone="+60 11-0000 0104")
weijie = _user("tan.weijie", "Tan Wei Jie", S, student_id="A22CS0412", faculty=COMPUTING, phone="+60 11-0000 0105")
priya = _user("priya.nair", "Priya Nair", S, student_id="A24SC0156", faculty=SCIENCE, phone="+60 11-0000 0106")
daniel = _user("daniel.lim", "Daniel Lim", S, student_id="A21CE0278", faculty=CIVIL, phone="+60 11-0000 0107")
siti = _user("siti.aminah", "Siti Aminah", S, student_id="A23AR0063", faculty=BUILT_ENV, phone="+60 11-0000 0108")

# Food sellers (external cafeterias, so no student id or faculty)
kakmin = _user("kakmin.kitchen", "Kak Min", F, email="kakmin.kitchen@serveeasy.example", phone="+60 11-0000 0201", image=_photo(_FOOD_PHOTO), hours=1)
paklah = _user("paklah.warung", "Pak Lah", F, email="paklah.warung@serveeasy.example", phone="+60 11-0000 0202", image=_photo(_FOOD_PHOTO), hours=1)
maksiti = _user("maksiti.dapur", "Mak Siti", F, email="maksiti.dapur@serveeasy.example", phone="+60 11-0000 0203", image=_photo(_FOOD_PHOTO), hours=1)
westerncorner = _user("western.corner", "Western Corner KTR", F, email="western.corner@serveeasy.example", phone="+60 11-0000 0204", image=_photo(_FOOD_PHOTO), hours=1)

# Service providers (students offering services, as per the PRD)
amir = _user("amir.syafiq", "Amir Syafiq", P, student_id="A22FC0190", faculty=COMPUTING, phone="+60 11-0000 0301")
nadia = _user("nadia.kamal", "Nadia Kamal", P, student_id="A23FS0222", faculty=SCIENCE, phone="+60 11-0000 0302")
jason = _user("jason.ong", "Jason Ong", P, student_id="A21EE0309", faculty=ELECTRICAL, phone="+60 11-0000 0303")
hafiz = _user("hafiz.roslan", "Hafiz Roslan", P, student_id="A23ME0271", faculty=MECHANICAL, phone="+60 11-0000 0304")
kavitha = _user("kavitha.raj", "Kavitha Raj", P, student_id="A24SC0099", faculty=SCIENCE, phone="+60 11-0000 0305")

# Owner account for The Cube's shop profile. The person is fictional: replace with the real owner.
zaid = _user("zaid.rahim", "Zaid Rahim", S, student_id="A22EE0118", faculty=ELECTRICAL, phone="+60 11-0000 0401")

# ----------------------------------------------- more sellers and service providers
# Fictional people. College codes: KTR, KTDI, KDSE, KTF, KTHO, KDOJ, KRP (Kolej Rahman Putra).
_COLLEGE: dict[str, str] = {
    aisyah: "KTR", haziq: "KTDI", nurul: "KDSE", farhan: "KTHO", weijie: "KRP", priya: "KTF",
    daniel: "KTHO", siti: "KDOJ", amir: "KRP", nadia: "KDSE", jason: "KTDI", hafiz: "KRP", kavitha: "KTF",
}
_FACULTY_CODE = {COMPUTING: "CS", ELECTRICAL: "EE", MECHANICAL: "ME", CIVIL: "CE", BUILT_ENV: "BE", SCIENCE: "SC"}
_extra_counter = 0


def _extra(slug, name, role, faculty, college) -> str:
    global _extra_counter
    _extra_counter += 1
    n = _extra_counter
    user_id = _user(
        slug, name, role,
        student_id=f"A2{n % 4 + 1}{_FACULTY_CODE[faculty]}{500 + n:04d}",
        faculty=faculty, phone=f"+60 11-0000 {500 + n:04d}", hours=0.5,
    )
    _COLLEGE[user_id] = college
    return user_id


# Extra students who sell listings
_EXTRA_SELLERS = [
    _extra("amirah.yusof", "Amirah Yusof", S, COMPUTING, "KDSE"),
    _extra("ravi.kumar", "Ravi Kumar", S, MECHANICAL, "KTDI"),
    _extra("lim.meiling", "Lim Mei Ling", S, SCIENCE, "KTF"),
    _extra("irfan.azmi", "Irfan Azmi", S, ELECTRICAL, "KTR"),
    _extra("sarah.tan", "Sarah Tan", S, BUILT_ENV, "KDSE"),
    _extra("zulhilmi.hamid", "Zulhilmi Hamid", S, CIVIL, "KTHO"),
    _extra("fatin.najwa", "Fatin Najwa", S, COMPUTING, "KTF"),
    _extra("kevin.chong", "Kevin Chong", S, ELECTRICAL, "KTDI"),
    _extra("aina.sofea", "Aina Sofea", S, SCIENCE, "KDSE"),
    _extra("hakim.ismail", "Hakim Ismail", S, MECHANICAL, "KTR"),
    _extra("devi.pillai", "Devi Pillai", S, CIVIL, "KTF"),
    _extra("shafiq.rosli", "Shafiq Rosli", S, COMPUTING, "KRP"),
]
SELLERS = [aisyah, haziq, nurul, farhan, weijie, priya, daniel, siti, *_EXTRA_SELLERS]

# Extra students who offer services
hanis = _extra("hanis.zainal", "Hanis Zainal", P, COMPUTING, "KTR")
brandon = _extra("brandon.lee", "Brandon Lee", P, BUILT_ENV, "KDOJ")
salmah = _extra("salmah.ibrahim", "Salmah Ibrahim", P, BUILT_ENV, "KTF")
meiyee = _extra("mei.yee", "Mei Yee Ong", P, SCIENCE, "KDSE")
syafiq = _extra("syafiq.hamzah", "Syafiq Hamzah", P, ELECTRICAL, "KTDI")
arvind = _extra("arvind.menon", "Arvind Menon", P, ELECTRICAL, "KTHO")
khairul = _extra("khairul.anuar", "Khairul Anuar", P, MECHANICAL, "KTR")
zarif = _extra("zarif.daud", "Zarif Daud", P, CIVIL, "KRP")
liyana = _extra("liyana.kasim", "Liyana Kasim", P, SCIENCE, "KTF")
farah = _extra("farah.diyana", "Farah Diyana", P, COMPUTING, "KDSE")
adam = _extra("adam.harun", "Adam Harun", P, SCIENCE, "KTDI")
wenhui = _extra("wen.hui", "Wong Wen Hui", P, COMPUTING, "KTR")
ikmal = _extra("ikmal.hisham", "Ikmal Hisham", P, ELECTRICAL, "KTHO")
sharmila = _extra("sharmila.devi", "Sharmila Devi", P, SCIENCE, "KTF")
danial = _extra("danial.aiman", "Danial Aiman", P, MECHANICAL, "KDOJ")
nabila = _extra("nabila.safiya", "Nabila Safiya", P, BUILT_ENV, "KDSE")
junkai = _extra("jun.kai", "Chew Jun Kai", P, COMPUTING, "KRP")
alia = _extra("alia.mansor", "Alia Mansor", P, COMPUTING, "KDSE")
raj = _extra("raj.singh", "Raj Singh", P, COMPUTING, "KTR")
nick = _extra("nick.tan", "Nicholas Tan", P, ELECTRICAL, "KTDI")
huda = _extra("huda.rahim", "Huda Rahim", P, SCIENCE, "KTF")
firdaus = _extra("firdaus.salleh", "Firdaus Salleh", P, BUILT_ENV, "KDOJ")
sue = _extra("sue.ling", "Sue Ling Chan", P, COMPUTING, "KTF")
imran = _extra("imran.kadir", "Imran Kadir", P, MECHANICAL, "KTHO")
balqis = _extra("balqis.aziz", "Balqis Aziz", P, CIVIL, "KDSE")

# Meet-up spots: where this person would hand over an item or do a service.
_COLLEGE_SPOTS = {
    "KTR": ["Kolej Tun Razak lobby", "Kolej Tun Razak cafe"],
    "KTDI": ["Kolej Tun Dr. Ismail cafe", "Kolej Tun Dr. Ismail guardhouse"],
    "KDSE": ["Kolej Datin Seri Endon guardhouse", "Kolej Datin Seri Endon lobby"],
    "KTF": ["Kolej Tun Fatimah lobby", "Kolej Tun Fatimah cafe"],
    "KTHO": ["Kolej Tun Hussein Onn lobby", "Kolej Tun Hussein Onn cafe"],
    "KDOJ": ["Kolej Dato' Onn Jaafar lobby", "Kolej Dato' Onn Jaafar cafe"],
    "KRP": ["Kolej Rahman Putra common room", "Kolej Rahman Putra lobby"],
}
_FACULTY_SPOT = {
    COMPUTING: "Fakulti Komputeran lobby",
    ELECTRICAL: "Fakulti Kejuruteraan Elektrik lobby",
    MECHANICAL: "Fakulti Kejuruteraan Mekanikal lobby",
    CIVIL: "Fakulti Kejuruteraan Awam lobby",
    BUILT_ENV: "Fakulti Alam Bina lobby",
    SCIENCE: "Fakulti Sains lobby",
}
_FACULTY_OF = {u["id"]: u["faculty"] for u in USERS}


def _spots_for(user_id: str) -> list[str]:
    college = _COLLEGE_SPOTS[_COLLEGE[user_id]]
    return [college[0], _FACULTY_SPOT[_FACULTY_OF[user_id]], "PSZ Library, main entrance", college[1], "Arked Meranti"]


# ------------------------------------------------------------------------- shops
SHOPS: list[Row] = []


def _shop(slug, owner, name, description, location, hours) -> str:
    shop_id = uid("shop", slug)
    SHOPS.append(
        {
            "id": shop_id,
            "owner_id": owner,
            "name": name,
            "description": description,
            "logo": _img(name),  # no real logos yet
            "location": location,
            "hours": hours,
            "created_at": _at(2),
        }
    )
    return shop_id


# Real details supplied by the project owner. Instagram handle not provided, so not stored.
the_cube = _shop(
    "the-cube",
    zaid,
    "The Cube",
    "Student-run dessert and shaved ice shop, run by UTM engineering students. "
    "Menu highlights: shaved ice (snow ice) in various flavours, tea eggs, and "
    "shao xian cao (herbal jelly).",
    "Lot 6, Student Mall, UTM Johor Bahru (Skudai) Campus, Johor",
    "7:00 PM - 11:30 PM, daily",
)
# Fictional demo shops whose services appear on their shop pages.
amir_print = _shop(
    "amir-print-corner",
    amir,
    "Amir Print Corner",
    "Quick, cheap printing for assignments, posters and project boards. Run by a Computing student.",
    "Fakulti Komputeran lobby, UTM Skudai",
    "Mon-Fri, 10:00 AM - 6:00 PM",
)
nadia_stitches = _shop(
    "nadia-stitches",
    nadia,
    "Nadia's Stitches",
    "Alterations and made-to-measure baju kurung by a student tailor.",
    "Kolej Datin Seri Endon, UTM Skudai",
    "Weekdays after 4:00 PM, weekends by appointment",
)

# --------------------------------------------------------------- product listings
# Unsplash photo ids, hand-matched to what each shows. Where no exact photo exists, the closest fit is used.
PH: dict[str, str] = {
    "books_a": "1512820790803-83ca734da794", "books_b": "1495446815901-a7297e633e8d",
    "books_c": "1544947950-fa07a98d237f", "bookstack": "1497633762265-9d179a990aa6",
    "notebook": "1544717305-2782549b5136", "stationery": "1456735190827-d1262f71b8a3",
    "deskwork": "1434030216411-0b793f4b4173", "mouse": "1527864550417-7fd91fc51a46",
    "keyboard": "1587829741301-dc798b83add3", "headphones": "1583394838336-acd977736f90",
    "phone": "1511707171634-5f897ff02aa9", "laptop": "1517336714731-489689fd1ca8",
    "desk": "1593642632559-0c6d3fc62b89", "camera": "1526170375885-4d8ecf77b99f",
    "watch": "1612817159949-195b6eb9e31a", "solder": "1558618666-fcd25c85cd64",
    "elec_a": "1588508065123-287b28e013da", "elec_b": "1505740420928-5e560c06d30e",
    "tee_badge": "1618354691373-d851c5c3a990", "tee_print": "1583743814966-8936f5b7be1a",
    "clothes": "1523381210434-271e8be1f52b", "sportswear": "1515886657613-9f3515b0c78f",
    "sneaker": "1491553895911-0055eca6402d", "backpack": "1553062407-98eeb64c6a62",
    "cooking": "1556909114-f6e7ad7d3136", "kitchen": "1509042239860-f550ce710b93",
    "racket": "1515886657613-9f3515b0c78f", "ball": "1515886657613-9f3515b0c78f",  # no racket/ball photo yet
    "weights": "1517836357463-d25dfeac3438", "yoga": "1571019613454-1cb2f99b2d8b",
    "guitar": "1510915361894-db8b60106cb1", "paint": "1513364776144-60967b0f800f",
    "other": "1485955900006-10f4d324d411", "food": _FOOD_PHOTO,
    "tutor": "1522202176988-66273c2fd55f", "haircut_a": "1599351431202-1e0f0137899a",
    "haircut_b": "1585747860715-2ba37e788b70", "haircut_c": "1621605815971-fbc98d665033",
}

LISTINGS: list[Row] = []
_SOLD = {"headphones", "mouse-gaming", "canvas-shoes", "ticket-sportsday", "chess-set"}

for _i, (_slug, _title, _price, _cond, _cat, _desc, _ph) in enumerate(LISTING_ROWS):
    _seller = SELLERS[(_i * 7) % len(SELLERS)]  # 7 is coprime to 20 sellers, so this spreads evenly
    _spots = _spots_for(_seller)
    LISTINGS.append(
        {
            "id": uid("listing", _slug),
            "seller_id": _seller,
            "title": _title,
            "description": _desc,
            "price": Decimal(_price),
            "condition": Cond(_cond),
            "category": Cat(_cat),
            "image": photos.pick(listing_group(_slug, _cat)) or _photo(PH[_ph]),
            "spot": _spots[(_i // 3) % len(_spots)],
            "status": ListingStatus.SOLD if _slug in _SOLD else ListingStatus.ACTIVE,
            "shop_id": None,
            "created_at": _at(24 + _i * 0.4),
        }
    )

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


FOOD_PROVIDERS: list[Row] = [
    {
        "id": uid("meal-provider", "jojoe-kopitiam"),
        "name": "JojoeKopitiam",
        "image": _photo(_FOOD_PHOTO),
        "is_active": True,
    },
    {
        "id": uid("meal-provider", "fen-jie"),
        "name": "芬姐",
        "image": _photo(_FOOD_PHOTO),
        "is_active": True,
    },
    {
        "id": uid("meal-provider", "ji-bao"),
        "name": "吉宝",
        "image": _photo(_FOOD_PHOTO),
        "is_active": True,
    },
]
_MEAL_PROVIDER_ID = {provider["name"]: provider["id"] for provider in FOOD_PROVIDERS}


def _sample_food(slug, provider_name, name, price, session) -> None:
    FOOD_ITEMS.append(
        {
            "id": uid("food", slug),
            "seller_id": None,
            "provider_id": _MEAL_PROVIDER_ID[provider_name],
            "name": name,
            "price": Decimal(price),
            "meal_session": session,
            "available": True,
            "image": None,
            "is_demo": True,
        }
    )


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

# ------------------------------------------------------- prototype meal menus
_sample_food("jojoe-l-nasi-lemak", "JojoeKopitiam", "Nasi Lemak Ayam", "8.00", L)
_sample_food("jojoe-l-chicken-rice", "JojoeKopitiam", "Hainanese Chicken Rice", "8.50", L)
_sample_food("jojoe-l-mee-goreng", "JojoeKopitiam", "Mee Goreng Mamak", "7.00", L)
_sample_food("jojoe-d-ayam-penyet", "JojoeKopitiam", "Nasi Ayam Penyet", "9.00", D)
_sample_food("jojoe-d-char-kuey-teow", "JojoeKopitiam", "Char Kuey Teow", "8.50", D)

_sample_food("fenjie-l-curry-chicken", "芬姐", "Curry Chicken Rice", "8.50", L)
_sample_food("fenjie-l-nasi-campur", "芬姐", "Nasi Campur", "9.00", L)
_sample_food("fenjie-l-mee-hoon", "芬姐", "Fried Mee Hoon", "7.50", L)
_sample_food("fenjie-d-asam-pedas", "芬姐", "Asam Pedas Set", "10.00", D)
_sample_food("fenjie-d-curry-noodles", "芬姐", "Curry Noodles", "8.50", D)

_sample_food("jibao-l-chicken-chop", "吉宝", "Chicken Chop Rice", "12.00", L)
_sample_food("jibao-l-spaghetti", "吉宝", "Spaghetti Bolognese", "10.00", L)
_sample_food("jibao-l-egg-mayo", "吉宝", "Egg Mayo Sandwich", "6.00", L)
_sample_food("jibao-d-burger", "吉宝", "Beef Burger Set", "11.00", D)
_sample_food("jibao-d-carbonara", "吉宝", "Chicken Carbonara", "12.00", D)

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

_PINNED = {  # slug -> (provider, shop)
    "print-bw": (amir, amir_print), "print-colour": (amir, amir_print), "print-binding": (amir, amir_print),
    "tailor-alter": (nadia, nadia_stitches), "tailor-baju": (nadia, nadia_stitches),
    "repair-laptop": (jason, None), "repair-phone": (jason, None), "repair-bike": (jason, None),
    "groom-haircut": (hafiz, None), "tutor-calculus": (kavitha, None), "tutor-programming": (amir, None),
    "design-poster": (amir, None), "web-dev": (amir, None), "photo-graduation": (hafiz, None),
    "video-edit": (jason, None),
}
# (slug prefixes) -> providers who realistically offer that kind of service; used in rotation.
_POOLS: list[tuple[tuple[str, ...], list[str]]] = [
    (("tutor-physics", "tutor-chem", "tutor-organic", "tutor-biology", "tutor-stats", "tutor-linear",
      "tutor-diffeq"), [kavitha, adam, sharmila]),
    (("tutor-statics", "tutor-thermo", "tutor-circuits", "tutor-digital", "tutor-fluid", "tutor-engdrawing",
      "tutor-autocad", "tutor-solidworks", "tutor-matlab"), [ikmal, danial, khairul]),
    (("tutor-dsa", "tutor-python", "tutor-java", "tutor-cpp", "tutor-web", "tutor-sql", "tutor-excel",
      "tutor-spss"), [wenhui, junkai, farah]),
    (("tutor-",), [nabila, kavitha, adam, sharmila]),
    (("design-",), [alia, sue, firdaus]),
    (("photo-", "video-", "audio-"), [nick, imran, huda]),
    (("music-", "event-"), [huda, imran, balqis]),
    (("dev-",), [raj, sue, nick]),
    (("errand-",), [balqis, imran, firdaus, huda, raj]),
]
_CATEGORY_POOLS: dict[str, list[str]] = {
    "printing": [amir, hanis, brandon],
    "tailoring": [nadia, salmah, meiyee],
    "repair": [jason, syafiq, arvind, khairul],
    "grooming": [hafiz, zarif, liyana, farah],
}
_pool_counter: dict[Any, int] = {}


def _provider_for(slug: str, category: str) -> str:
    if category in _CATEGORY_POOLS:
        members = _CATEGORY_POOLS[category]
        k = _pool_counter.get(category, 0)
        _pool_counter[category] = k + 1
        return members[k % len(members)]
    for n, (prefixes, members) in enumerate(_POOLS):
        if slug.startswith(prefixes):
            k = _pool_counter.get(n, 0)
            _pool_counter[n] = k + 1
            return members[k % len(members)]
    raise ValueError(f"no provider pool for {slug}")


for _i, (_slug, _title, _price, _cat, _desc, _unit, _ph) in enumerate(SERVICE_ROWS):
    _provider, _shop = _PINNED.get(_slug) or (_provider_for(_slug, _cat), None)
    _spots = _spots_for(_provider)
    SERVICES.append(
        {
            "id": uid("service", _slug),
            "provider_id": _provider,
            "title": _title,
            "description": _desc,
            "price": Decimal(_price),
            "category": ServiceCategory(_cat),
            "unit": _unit,
            "image": photos.pick(service_group(_slug, _cat)) or _photo(PH[_ph]),
            "spot": "Online (chat to arrange)" if "(online)" in _desc else _spots[(_i // 2) % len(_spots)],
            "shop_id": _shop,
            "created_at": _at(20 + _i * 0.3),
        }
    )

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
_booking("b6", nurul, "print-binding", "2 copies of my final report, 80 pages, spiral binding.", 6, BS.PENDING, hours=214)
_booking("b7", haziq, "tutor-calculus", "Need help with multiple integrals before the mid-sem test.", 1, BS.ACCEPTED, hours=211)
_booking("b8", daniel, "photo-graduation", "Graduation portraits at Dewan Sultan Iskandar.", 12, BS.PENDING, hours=216)
_booking("b9", priya, "design-poster", "Poster for the Science Club open day.", -2, BS.COMPLETED, hours=120)
_booking("b10", weijie, "tutor-programming", "Help with a Java OOP assignment.", 2, BS.CANCELLED, hours=213)

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
    "powerbank-inquiry",
    [
        (haziq, priya, "Hello, does the 10000mAh power bank come with a cable?"),
        (priya, haziq, "Yes, a USB-C cable is included."),
    ],
    160,
)

# ------------------------------------------------------------------- registry
# Parents first, so the seed runner can insert in this order without violating FKs.
TABLES: list[tuple[str, list[Row]]] = [
    ("users", USERS),
    ("food_providers", FOOD_PROVIDERS),
    ("food_provider_staff", []),
    ("shops", SHOPS),
    ("product_listings", LISTINGS),
    ("product_orders", []),
    ("food_items", FOOD_ITEMS),
    ("food_delivery_batches", []),
    ("services", SERVICES),
    ("food_orders", FOOD_ORDERS),
    ("order_line_items", ORDER_LINE_ITEMS),
    ("service_bookings", SERVICE_BOOKINGS),
    ("messages", MESSAGES),
    ("notifications", []),
]


def summary() -> dict[str, int]:
    return {name: len(rows) for name, rows in TABLES}


if __name__ == "__main__":
    for name, count in summary().items():
        print(f"{name:20} {count}")
