"""The ServeEasy Telegram bot.

The bot answers questions about the marketplace by reading the same Neon
database the API reads. It only ever runs SELECTs: every transaction on its
engine is opened as read-only (see `app.bot.queries`).

The bot is started and stopped by the FastAPI lifespan in `app.main`, so
`uvicorn app.main:app` is enough to have it online.
"""

from __future__ import annotations

import asyncio
import html
import logging
from decimal import Decimal
from typing import Any, Callable

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.bot.queries import (
    PAGE_SIZE,
    bot_session,
    find_cafeteria,
    find_shop,
    get_listing,
    get_menu,
    get_service,
    get_shop,
    list_cafeterias,
    list_shops,
    search_listings,
    search_services,
)
from app.models.base import ListingCategory, ServiceCategory
from app.schemas import ListingOut, ServiceOut

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "<b>ServeEasy bot</b>\n"
    "Browse the UTM marketplace without opening the app.\n\n"
    "<b>Commands</b>\n"
    "/listings <i>[text]</i> — items for sale (newest first)\n"
    "/services <i>[text]</i> — services offered by students\n"
    "/search <i>&lt;text&gt;</i> — items and services at once\n"
    "/cafeterias — food sellers\n"
    "/menu <i>&lt;cafeteria&gt;</i> — a cafeteria's lunch and dinner menu\n"
    "/shops — student enterprises\n"
    "/shop <i>&lt;name&gt;</i> — a shop and what it sells\n\n"
    "Just type a word to search everything. Buttons below the results filter "
    "by category and price."
)

# Price shortcuts offered under a list of results.
PRICE_STEPS = ("10", "25", "50", "100")

# The categories a result list can be filtered by.
_LISTING_CATEGORIES = tuple(c.value for c in ListingCategory)
_SERVICE_CATEGORIES = tuple(c.value for c in ServiceCategory)


# ------------------------------------------------------------------ helpers


def _esc(value: Any) -> str:
    """Escape text for Telegram's HTML parse mode."""
    return html.escape(str(value if value is not None else ""))


def _money(value: Decimal) -> str:
    return f"RM {value:.2f}"


def _label(value: Any) -> str:
    """`daily_essentials` becomes `daily essentials`."""
    raw = getattr(value, "value", value)
    return str(raw).replace("_", " ")


def _truncate(text: str, limit: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _cb(kind: str, page: int, cat: str, maxp: str, q: str) -> str:
    """Build callback data. Telegram allows 64 bytes, so the query is clipped."""
    clean = (q or "").replace(":", " ").replace("\n", " ")[:30]
    return f"{kind}:{page}:{cat}:{maxp}:{clean}"


def _split_cb(data: str) -> list[str]:
    """Split callback data back into its fields, padding what is missing."""
    parts = data.split(":", 4)
    parts += [""] * (5 - len(parts))
    # The query is the last field and may hold anything but a colon.
    parts[4] = parts[4].replace(":", " ").strip()
    return parts


# ----------------------------------------------------------------- rendering


def _listing_card(listing: ListingOut) -> str:
    lines = [
        f"<b>{_esc(listing.title)}</b>",
        f"{_money(listing.price)} · {_label(listing.condition)} · {_label(listing.category)}",
    ]
    if listing.spot:
        lines.append(f"📍 {_esc(listing.spot)}")
    seller = listing.seller.name
    if listing.seller.faculty:
        seller = f"{seller} ({listing.seller.faculty})"
    lines.append(f"Seller: {_esc(seller)}")
    if listing.shop:
        lines.append(f"Shop: {_esc(listing.shop.name)}")
    return "\n".join(lines)


def _service_card(service: ServiceOut) -> str:
    unit = f" / {_esc(service.unit)}" if service.unit else ""
    lines = [
        f"<b>{_esc(service.title)}</b>",
        f"{_money(service.price)}{unit} · {_label(service.category)}",
    ]
    if service.spot:
        lines.append(f"📍 {_esc(service.spot)}")
    provider = service.provider.name
    if service.provider.faculty:
        provider = f"{provider} ({service.provider.faculty})"
    lines.append(f"Provider: {_esc(provider)}")
    if service.shop:
        lines.append(f"Shop: {_esc(service.shop.name)}")
    return "\n".join(lines)


def _listing_detail(listing: ListingOut) -> str:
    body = [_listing_card(listing)]
    if listing.description:
        body.append(_truncate(listing.description, 900))
    return "\n\n".join(body)


def _service_detail(service: ServiceOut) -> str:
    body = [_service_card(service)]
    if service.description:
        body.append(_truncate(service.description, 900))
    return "\n\n".join(body)


def _grid(
    buttons: list[InlineKeyboardButton], per_row: int = 3
) -> list[list[InlineKeyboardButton]]:
    return [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]


def _filter_rows(
    kind: str,
    categories: tuple[str, ...],
    cat: str,
    maxp: str,
    q: str,
) -> list[list[InlineKeyboardButton]]:
    """Category buttons, price buttons and a way back to everything."""
    rows: list[list[InlineKeyboardButton]] = []
    cat_buttons = [InlineKeyboardButton("All", callback_data=_cb(kind, 0, "", maxp, q))]
    cat_buttons += [
        InlineKeyboardButton(_label(c), callback_data=_cb(kind, 0, c, maxp, q)) for c in categories
    ]
    rows += _grid(cat_buttons)
    price_buttons = [InlineKeyboardButton("Any price", callback_data=_cb(kind, 0, cat, "", q))]
    price_buttons += [
        InlineKeyboardButton(f"≤ RM {p}", callback_data=_cb(kind, 0, cat, p, q))
        for p in PRICE_STEPS
    ]
    rows.append(price_buttons)
    return rows


def _nav_row(
    kind: str, page: int, has_next: bool, cat: str, maxp: str, q: str
) -> list[InlineKeyboardButton]:
    buttons = []
    if page > 0:
        buttons.append(
            InlineKeyboardButton("◀ Previous", callback_data=_cb(kind, page - 1, cat, maxp, q))
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton("Next ▶", callback_data=_cb(kind, page + 1, cat, maxp, q))
        )
    return buttons


# -------------------------------------------------------------------- fetching


def _fetch_page(func: Callable, page: int, **kwargs) -> list:
    """Run one page of a search. The extra row tells us if a next page exists."""
    with bot_session() as session:
        return func(
            session,
            limit=PAGE_SIZE + 1,
            offset=page * PAGE_SIZE,
            **kwargs,
        )


def _fetch_one(func: Callable, **kwargs):
    with bot_session() as session:
        return func(session, **kwargs)


# -------------------------------------------------------------------- handlers


async def _deliver(update: Update, text: str, keyboard: InlineKeyboardMarkup, edit: bool) -> None:
    query = update.callback_query
    if edit and query is not None and query.message is not None:
        try:
            await query.edit_message_text(
                text, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        except BadRequest as exc:
            if "Message is not modified" not in str(exc):
                raise
            logger.debug("Skipped editing an unchanged Telegram message")
        return
    message = update.effective_message
    if message is not None:
        await message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


async def _cmd_listings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = " ".join(context.args).strip() or None
    await _show_listings(update, q=q)


async def _cmd_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = " ".join(context.args).strip() or None
    await _show_services(update, q=q)


async def _cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = " ".join(context.args).strip()
    if not q:
        await update.effective_message.reply_text(
            "What should I look for? Try /search calculator", parse_mode=ParseMode.HTML
        )
        return
    await _show_listings(update, q=q)
    await _show_services(update, q=q)


async def _cmd_cafeterias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cafeterias = await asyncio.to_thread(
        _fetch_page, lambda session, **kw: list_cafeterias(session), 0
    )
    if not cafeterias:
        await update.effective_message.reply_text("No cafeterias yet.")
        return
    lines = ["<b>Food sellers</b>"]
    lines += [f"• {_esc(c.name)}" for c in cafeterias]
    lines.append("\nUse /menu &lt;name&gt; to see a menu.")
    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def _cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args).strip()
    if not name:
        await update.effective_message.reply_text(
            "Which cafeteria? Try /menu &lt;name&gt;", parse_mode=ParseMode.HTML
        )
        return
    menu = await asyncio.to_thread(_fetch_menu, name)
    if menu is None:
        await update.effective_message.reply_text(
            f"No cafeteria called <b>{_esc(name)}</b>. Use /cafeterias to see the list.",
            parse_mode=ParseMode.HTML,
        )
        return
    lines = [f"<b>{_esc(menu.cafeteria.name)}</b>"]
    if not menu.items:
        lines.append("No items on the menu right now.")
    current = None
    for item in menu.items:
        if item.meal_session != current:
            current = item.meal_session
            lines.append(f"\n<u>{_label(current).title()}</u>")
        lines.append(f"• {_esc(item.name)} — {_money(item.price)}")
    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def _cmd_shops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    shops = await asyncio.to_thread(_fetch_page, lambda session, **kw: list_shops(session), 0)
    if not shops:
        await update.effective_message.reply_text("No shops yet.")
        return
    lines = ["<b>Student enterprises</b>"]
    for shop in shops:
        lines.append(f"• <b>{_esc(shop.name)}</b> — {_esc(shop.location)}")
        if shop.description:
            lines.append(f"  {_truncate(shop.description, 120)}")
    lines.append("\nUse /shop &lt;name&gt; for the full profile.")
    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def _cmd_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = " ".join(context.args).strip()
    if not name:
        await update.effective_message.reply_text(
            "Which shop? Try /shop &lt;name&gt;", parse_mode=ParseMode.HTML
        )
        return
    detail = await asyncio.to_thread(_fetch_shop, name)
    if detail is None:
        await update.effective_message.reply_text(
            f"No shop called <b>{_esc(name)}</b>. Use /shops to see the list.",
            parse_mode=ParseMode.HTML,
        )
        return
    lines = [f"<b>{_esc(detail.name)}</b>"]
    if detail.description:
        lines.append(_truncate(detail.description, 400))
    if detail.location:
        lines.append(f"📍 {_esc(detail.location)}")
    if detail.hours:
        lines.append(f"🕒 {_esc(detail.hours)}")
    if detail.owner:
        lines.append(f"Owner: {_esc(detail.owner.name)}")
    if detail.listings:
        lines.append("\n<u>Items</u>")
        for listing in detail.listings[:PAGE_SIZE]:
            lines.append(f"• {_esc(listing.title)} — {_money(listing.price)}")
    if detail.services:
        lines.append("\n<u>Services</u>")
        for service in detail.services[:PAGE_SIZE]:
            lines.append(f"• {_esc(service.title)} — {_money(service.price)}")
    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def _on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A plain message is treated as a search for both items and services."""
    text = (update.effective_message.text or "").strip()
    if not text or text.startswith("/"):
        # A command Telegram did not recognise; the command menu has the real list.
        return
    await _show_listings(update, q=text)
    await _show_services(update, q=text)


async def _show_listings(
    update: Update,
    *,
    q: str | None = None,
    category: ListingCategory | None = None,
    max_price: Decimal | None = None,
    page: int = 0,
    edit: bool = False,
) -> None:
    rows = await asyncio.to_thread(
        _fetch_page,
        search_listings,
        page,
        q=q,
        category=category,
        max_price=max_price,
    )
    shown = rows[:PAGE_SIZE]
    has_next = len(rows) > PAGE_SIZE
    cat = category.value if category else ""
    maxp = str(int(max_price)) if max_price is not None else ""

    if not shown:
        text = f"No items found{f' for “{_esc(q)}”' if q else ''}."
        keyboard = InlineKeyboardMarkup(
            _filter_rows("lp", _LISTING_CATEGORIES, cat, maxp, q or "")
        )
        await _deliver(update, text, keyboard, edit)
        return

    header = "<b>Items for sale</b>"
    if q:
        header += f" — “{_esc(q)}”"
    body = "\n\n".join(_listing_card(row) for row in shown)
    text = f"{header}\n\n{body}"

    buttons = [
        [
            InlineKeyboardButton(
                _truncate(f"{row.title} · {_money(row.price)}", 40),
                callback_data=f"ld:{row.id}",
            )
        ]
        for row in shown
    ]
    buttons += _filter_rows("lp", _LISTING_CATEGORIES, cat, maxp, q or "")
    nav = _nav_row("lp", page, has_next, cat, maxp, q or "")
    if nav:
        buttons.append(nav)
    await _deliver(update, text, InlineKeyboardMarkup(buttons), edit)


async def _show_services(
    update: Update,
    *,
    q: str | None = None,
    category: ServiceCategory | None = None,
    max_price: Decimal | None = None,
    page: int = 0,
    edit: bool = False,
) -> None:
    rows = await asyncio.to_thread(
        _fetch_page,
        search_services,
        page,
        q=q,
        category=category,
        max_price=max_price,
    )
    shown = rows[:PAGE_SIZE]
    has_next = len(rows) > PAGE_SIZE
    cat = category.value if category else ""
    maxp = str(int(max_price)) if max_price is not None else ""

    if not shown:
        text = f"No services found{f' for “{_esc(q)}”' if q else ''}."
        keyboard = InlineKeyboardMarkup(
            _filter_rows("sp", _SERVICE_CATEGORIES, cat, maxp, q or "")
        )
        await _deliver(update, text, keyboard, edit)
        return

    header = "<b>Services</b>"
    if q:
        header += f" — “{_esc(q)}”"
    body = "\n\n".join(_service_card(row) for row in shown)
    text = f"{header}\n\n{body}"

    buttons = [
        [
            InlineKeyboardButton(
                _truncate(f"{row.title} · {_money(row.price)}", 40),
                callback_data=f"sd:{row.id}",
            )
        ]
        for row in shown
    ]
    buttons += _filter_rows("sp", _SERVICE_CATEGORIES, cat, maxp, q or "")
    nav = _nav_row("sp", page, has_next, cat, maxp, q or "")
    if nav:
        buttons.append(nav)
    await _deliver(update, text, InlineKeyboardMarkup(buttons), edit)


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    try:
        await query.answer()
    except TelegramError:
        # The spinner is a nicety; the answer should still be sent without it.
        logger.debug("Could not answer the callback query", exc_info=True)
    data = query.data or ""

    if data.startswith("lp:"):
        _, page, cat, maxp, q = _split_cb(data)
        await _show_listings(
            update,
            q=q or None,
            category=ListingCategory(cat) if cat else None,
            max_price=Decimal(maxp) if maxp else None,
            page=int(page or 0),
            edit=True,
        )
        return

    if data.startswith("sp:"):
        _, page, cat, maxp, q = _split_cb(data)
        await _show_services(
            update,
            q=q or None,
            category=ServiceCategory(cat) if cat else None,
            max_price=Decimal(maxp) if maxp else None,
            page=int(page or 0),
            edit=True,
        )
        return

    if data.startswith("ld:"):
        listing = await asyncio.to_thread(_fetch_one, get_listing, listing_id=data[3:])
        if listing is None:
            await query.message.reply_text("That item is gone.")
            return
        await _reply_with_photo(query.message, _listing_detail(listing), listing.image)
        return

    if data.startswith("sd:"):
        service = await asyncio.to_thread(_fetch_one, get_service, service_id=data[3:])
        if service is None:
            await query.message.reply_text("That service is gone.")
            return
        await _reply_with_photo(query.message, _service_detail(service), service.image)


async def _reply_with_photo(message, text: str, photo: str | None) -> None:
    """Send the picture with the description, falling back to text only."""
    if photo and photo.startswith(("http://", "https://")):
        try:
            await message.reply_photo(photo=photo, caption=text, parse_mode=ParseMode.HTML)
            return
        except TelegramError:
            logger.warning("Could not send the photo %s", photo, exc_info=True)
    await message.reply_text(text, parse_mode=ParseMode.HTML)


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Telegram bot error", exc_info=context.error)
    message = getattr(update, "effective_message", None)
    if message is not None:
        try:
            await message.reply_text("Something went wrong on my side. Please try again.")
        except TelegramError:
            pass


# --------------------------------------------------------------- thread helpers


def _fetch_menu(name: str):
    with bot_session() as session:
        cafeteria = find_cafeteria(session, name)
        if cafeteria is None:
            return None
        return get_menu(session, cafeteria.id)


def _fetch_shop(name: str):
    with bot_session() as session:
        shop = find_shop(session, name)
        if shop is None:
            return None
        return get_shop(session, shop.id)


# ------------------------------------------------------------------ lifecycle


async def _post_init(application: Application) -> None:
    """Publish the command menu in Telegram."""
    await application.bot.set_my_commands(
        [
            BotCommand("listings", "Browse items for sale"),
            BotCommand("services", "Browse services"),
            BotCommand("search", "Search items and services"),
            BotCommand("cafeterias", "List the food sellers"),
            BotCommand("menu", "See a cafeteria's menu"),
            BotCommand("shops", "List the student enterprises"),
            BotCommand("shop", "See a shop and what it sells"),
            BotCommand("help", "How to use this bot"),
        ]
    )


def _register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", _cmd_start))
    application.add_handler(CommandHandler("help", _cmd_help))
    application.add_handler(CommandHandler("listings", _cmd_listings))
    application.add_handler(CommandHandler("services", _cmd_services))
    application.add_handler(CommandHandler("search", _cmd_search))
    application.add_handler(CommandHandler("cafeterias", _cmd_cafeterias))
    application.add_handler(CommandHandler("menu", _cmd_menu))
    application.add_handler(CommandHandler("shops", _cmd_shops))
    application.add_handler(CommandHandler("shop", _cmd_shop))
    application.add_handler(CallbackQueryHandler(_on_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _on_text))
    application.add_error_handler(_on_error)


async def start_bot(token: str) -> Application:
    """Build the bot and start polling Telegram."""
    application = Application.builder().token(token).build()
    _register_handlers(application)
    await application.initialize()
    # Application.initialize() does not run post_init (only run_polling does),
    # so the command menu is published here.
    try:
        await _post_init(application)
    except TelegramError:
        logger.warning("Could not publish the Telegram command menu", exc_info=True)
    await application.start()
    await application.updater.start_polling(bootstrap_retries=3)
    logger.info("Telegram bot is polling")
    return application


async def stop_bot(application: Application) -> None:
    """Stop polling and release the Telegram session."""
    await application.stop()
    # The updater has to stop before the application can shut down.
    await application.updater.stop()
    await application.shutdown()
    logger.info("Telegram bot stopped")
