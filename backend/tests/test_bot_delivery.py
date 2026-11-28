import asyncio
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from telegram import InlineKeyboardMarkup, Update
from telegram.error import BadRequest

from app.bot.telegram_bot import _deliver


def _update_with_edit_error(error: BadRequest) -> tuple[Update, AsyncMock]:
    edit_message_text = AsyncMock(side_effect=error)
    query = SimpleNamespace(message=object(), edit_message_text=edit_message_text)
    update = cast(
        Update,
        SimpleNamespace(callback_query=query, effective_message=None),
    )
    return update, edit_message_text


def test_unchanged_callback_message_is_ignored():
    update, edit_message_text = _update_with_edit_error(
        BadRequest(
            "Message is not modified: specified new message content and reply markup "
            "are exactly the same as a current content and reply markup of the message"
        )
    )

    asyncio.run(_deliver(update, "same text", InlineKeyboardMarkup([]), edit=True))

    edit_message_text.assert_awaited_once()


def test_other_callback_edit_bad_requests_are_raised():
    update, _ = _update_with_edit_error(BadRequest("Message to edit not found"))

    with pytest.raises(BadRequest, match="Message to edit not found"):
        asyncio.run(_deliver(update, "new text", InlineKeyboardMarkup([]), edit=True))
