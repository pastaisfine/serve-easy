"""Which Unsplash search each seed row's photo comes from.

One search per *group* (not per row): rows in a group share the search's top
results and rotate through them. `fetch_photos.py` runs the searches and caches
them in `photo_cache.json`; this module only decides which group a row is in.
"""

import re

# group -> Unsplash search query. Order is the fetch order.
GROUPS: dict[str, str] = {
    # --- items: books and stationery
    "textbooks": "university textbooks stack",
    "notes": "handwritten lecture notes notebook",
    "calculator": "scientific calculator",
    "drafting": "drawing compass",
    "usb_drive": "usb flash drive",
    "stationery": "stationery pens notebooks desk",
    # --- items: electronics
    "mouse": "computer mouse",
    "keyboard": "computer keyboard",
    "headphones": "headphones",
    "powerbank": "power bank",
    "charger_cable": "charging cable usb",
    "usb_hub": "usb hub laptop adapter",
    "laptop_stand": "laptop stand",
    "phone_tripod": "phone tripod",
    "speaker": "bluetooth speaker",
    "smartwatch": "smartwatch",
    "desk_lamp": "desk lamp",
    "hard_drive": "external hard drive",
    "electronics_kit": "arduino breadboard electronics",
    # --- items: clothing
    "tshirt": "t-shirt",
    "hoodie": "hoodie",
    "sneakers": "sneakers shoes",
    "backpack": "backpack",
    "wristwatch": "wristwatch",
    "accessories": "umbrella cap tie",
    "malay_clothing": "baju kurung malay traditional",
    "formal_wear": "blazer formal shirt",
    "lab_coat": "lab coat science",
    # --- items: kitchen, sports, hobbies
    "kitchen_appliance": "small kitchen appliances",
    "lunchbox": "lunch box",
    "water_bottle": "water bottle",
    "badminton": "badminton racket shuttlecock",
    "basketball": "basketball",
    "football": "soccer ball",
    "tennis": "tennis racket balls",
    "gym": "gym dumbbells resistance bands",
    "board_game": "board game",
    "guitar": "acoustic guitar ukulele",
    "paint": "paint brushes art supplies",
    "camera": "film camera",
    "collectibles": "collectible figures toys",
    # --- items: tickets, snacks, daily essentials
    "event_ticket": "event tickets",
    "instant_noodles": "instant noodles",
    "coffee": "instant coffee",
    "cookies": "cookies chocolate brownies",
    "toiletries": "toiletries shampoo soap",
    "detergent": "laundry detergent",
    # --- services
    "binding": "book binding",
    "print_poster": "poster printing banner",
    "print_docs": "printing documents printer",
    "sewing": "sewing machine tailor",
    "laptop_repair": "laptop repair",
    "phone_repair": "phone screen repair",
    "bike_repair": "bicycle repair",
    "solder_repair": "soldering electronics repair",
    "repair_misc": "watch repair",
    "haircut": "barber haircut",
    "makeup": "makeup artist",
    "massage": "shoulder massage",
    "tutor_math": "math tutoring whiteboard",
    "tutor_science": "chemistry lab students",
    "tutor_eng": "engineering students blueprint",
    "tutor_code": "coding laptop programming",
    "tutor_lang": "language class learning",
    "tutor_writing": "student writing essay",
    "design_graphic": "graphic design",
    "photography": "photographer camera",
    "videography": "video editing",
    "podcast": "podcast microphone",
    "web_dev": "web design laptop",
    "coding": "software developer code",
    "laundry": "laundry folding clothes",
    "cleaning": "cleaning room",
    "delivery": "grocery shopping delivery",
    "carpool": "car ride friends",
    "typing": "typing laptop keyboard hands",
    "event_help": "event emcee microphone",
    "rental_gear": "projector speaker camera",
}

# First match wins. Matched against the row slug.
_LISTING_RULES: list[tuple[str, str]] = [
    (r"^(past-papers|papers-|civil-notes|digital-logic-notes|thermo-revision|biochem-notes)", "notes"),
    (r"^calc-", "calculator"),
    (r"^(drawing-set|a3-board|eng-drawing-kit|tech-pens|scale-ruler|tracing-paper|geometry-set)", "drafting"),
    (r"^flash-", "usb_drive"),
    (r"^mouse-", "mouse"),
    (r"^keyboard-", "keyboard"),
    (r"^(headphones|earphones-wired|earbuds-tws)", "headphones"),
    (r"^powerbank-", "powerbank"),
    (r"^(laptop-charger|phone-charger|cable-|extension-|travel-adapter)", "charger_cable"),
    (r"^(adapter-|usb-hub|card-reader)", "usb_hub"),
    (r"^(laptop-stand|cooling-pad)", "laptop_stand"),
    (r"^(phone-holder|tripod-phone|ring-light|webcam)", "phone_tripod"),
    (r"^speaker-", "speaker"),
    (r"^(smartwatch|fitness-band)", "smartwatch"),
    (r"^(study-lamp|mini-fan)", "desk_lamp"),
    (r"^(hdd-|ssd-)", "hard_drive"),
    (r"^(arduino|breadboard|raspberry|multimeter|soldering)", "electronics_kit"),
    (r"^(faculty-tee|tee-|jersey)", "tshirt"),
    (r"^(hoodie|windbreaker|denim|sports-set)", "hoodie"),
    (r"^(running-shoes|futsal-shoes|canvas-shoes|sandals)", "sneakers"),
    (r"^(backpack|sling-bag|tote-bag)", "backpack"),
    (r"^watch-analog", "wristwatch"),
    (r"^(cap$|umbrella|lanyard|necktie)", "accessories"),
    (r"^(baju-|tudung)", "malay_clothing"),
    (r"^(blazer|formal-|grad-sash)", "formal_wear"),
    (r"^(lab-coat|safety-goggles)", "lab_coat"),
    (r"^(rice-cooker|egg-boiler|sandwich|mini-pan|knife-small|kettle|blender|coffee-dripper)", "kitchen_appliance"),
    (r"^(lunchbox|noodle-bowl|microwave|jar-set|cutlery|plate-bowl)", "lunchbox"),
    (r"^(water-bottle|thermos|tumbler|ice-tray|reusable-cup|mug-set|shaker)", "water_bottle"),
    (r"^(badminton|shuttlecocks)", "badminton"),
    (r"^basketball", "basketball"),
    (r"^(football|futsal-ball|takraw|frisbee)", "football"),
    (r"^(tennis|pingpong)", "tennis"),
    (r"^(yoga|resistance|dumbbells|hand-grips|gym-|skipping|knee|ankle|cycling|sports-towel|swim)", "gym"),
    (r"^(board-game|monopoly|jenga|catan|chess|rubiks|uno|playing-cards)", "board_game"),
    (r"^(guitar|ukulele|harmonica)", "guitar"),
    (r"^(art-supplies|watercolour|brush-set|clay-kit|sketchbook|colour-pencils)", "paint"),
    (r"^(camera-|instant-camera)", "camera"),
    (r"^(trading|figure|crochet|handmade|resin)", "collectibles"),
    (r"^(ticket-|workshop-pass|voucher-)", "event_ticket"),
    (r"^noodles-box", "instant_noodles"),
    (r"^coffee-sachets", "coffee"),
    (r"^(baked-cookies|brownies|kuih|protein-bars|chocolates)", "cookies"),
    (r"^(toiletry|tissue|hand-sanitiser|first-aid|laundry-bag)", "toiletries"),
    (r"^(detergent|fabric-softener)", "detergent"),
]
# Used when no rule matches, keyed by the row's category.
_LISTING_DEFAULT = {"books": "textbooks", "stationery": "stationery"}

_SERVICE_RULES: list[tuple[str, str]] = [
    (r"^(print-binding|spiral-bind|hardcover-thesis)", "binding"),
    (r"^(print-colour|poster-a3|banner-print|sticker-print|namecard-print|lanyard-print|foamboard|plot-a1|photo-print|mug-print|tshirt-print)", "print_poster"),
    (r"^repair-(phone|tablet|charge-port)", "phone_repair"),
    (r"^repair-(bike|puncture|brake)", "bike_repair"),
    (r"^repair-(earphone|headphone|cable|circuit|solder|fan)", "solder_repair"),
    (r"^repair-(shoe|watch|glasses|umbrella)", "repair_misc"),
    (r"^groom-(makeup|grad-makeup|hijab|henna|nail|manicure|pedicure|facial|threading|braid|dye)", "makeup"),
    (r"^groom-(scalp|shoulder)", "massage"),
    (r"^tutor-(calculus|stats|linear|diffeq|econ|accounting)", "tutor_math"),
    (r"^tutor-(physics|chem|organic|biology)", "tutor_science"),
    (r"^tutor-(statics|thermo|circuits|digital|fluid|engdrawing|autocad|solidworks|matlab)", "tutor_eng"),
    (r"^tutor-(programming|dsa|python|java|cpp|web|sql|excel|spss)", "tutor_code"),
    (r"^tutor-(english|muet|bm|arabic|mandarin|japanese)", "tutor_lang"),
    (r"^tutor-(writing|proofread|presentation|interview|study|group)", "tutor_writing"),
    (r"^music-", "guitar"),
    (r"^(design-|errand-(calligraphy|poster-sci|data-viz))", "design_graphic"),
    (r"^(photo-|photo-graduation)", "photography"),
    (r"^(video-|errand-stream)", "videography"),
    (r"^audio-", "podcast"),
    (r"^dev-(arduino|pcb)", "electronics_kit"),
    (r"^(web-dev|dev-wordpress|dev-figma)", "web_dev"),
    (r"^dev-", "coding"),
    (r"^errand-(sound|cameras|tripod-rent|projector)", "rental_gear"),
    (r"^errand-(laundry|ironing)", "laundry"),
    (r"^errand-(cleaning|packing)", "cleaning"),
    (r"^errand-(grocery|parcel|food)", "delivery"),
    (r"^errand-carpool", "carpool"),
    (r"^errand-(typing|transcribe|translate|linkedin|coverletter|notes|research|referencing|labreport|mailmerge|qr|mc-bm|queue)", "typing"),
    (r"^(errand-|event-)", "event_help"),
]
_SERVICE_DEFAULT = {
    "printing": "print_docs",
    "tailoring": "sewing",
    "repair": "laptop_repair",
    "grooming": "haircut",
}


def _match(rules: list[tuple[str, str]], slug: str) -> str | None:
    for pattern, group in rules:
        if re.match(pattern, slug):
            return group
    return None


def listing_group(slug: str, category: str) -> str:
    group = _match(_LISTING_RULES, slug) or _LISTING_DEFAULT.get(category)
    if group is None:
        raise ValueError(f"no photo group for listing {slug!r} ({category})")
    return group


def service_group(slug: str, category: str) -> str:
    group = _match(_SERVICE_RULES, slug) or _SERVICE_DEFAULT.get(category)
    if group is None:
        raise ValueError(f"no photo group for service {slug!r} ({category})")
    return group
