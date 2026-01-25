from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.common import get_param, reply_to_message, restricted


def _build_update(
    text: str = "/cities", reply_to_message_id: int | None = None, user_id: int = 1
):
    reply_to_message = (
        SimpleNamespace(message_id=reply_to_message_id)
        if reply_to_message_id is not None
        else None
    )
    message = SimpleNamespace(
        text=text,
        chat_id=123,
        message_id=50,
        reply_to_message=reply_to_message,
    )
    return SimpleNamespace(
        effective_message=message,
        effective_chat=SimpleNamespace(id=999),
        effective_user=SimpleNamespace(id=user_id),
    )


def test_get_param_strips_command_and_bot_suffix():
    update = _build_update(text="/cities@helpukraine Berlin ")
    assert get_param(update, "/cities") == "berlin"


@pytest.mark.anyio
async def test_reply_to_message_replies_and_deletes():
    update = _build_update(reply_to_message_id=321)
    bot = SimpleNamespace(
        send_message=AsyncMock(),
        delete_message=AsyncMock(),
    )
    context = SimpleNamespace(bot=bot)

    await reply_to_message(update, context, "hello", disable_web_page_preview=False)

    bot.send_message.assert_awaited_once_with(
        chat_id=123,
        reply_to_message_id=321,
        text="hello",
        disable_web_page_preview=False,
    )
    bot.delete_message.assert_awaited_once_with(chat_id=123, message_id=50)


@pytest.mark.anyio
async def test_restricted_allows_admins(monkeypatch):
    called = False

    @restricted
    async def sample(update, context):
        nonlocal called
        called = True

    async def fake_get_chat_administrators(chat_id: int):
        return [SimpleNamespace(user=SimpleNamespace(id=7))]

    update = _build_update(user_id=7)
    bot = SimpleNamespace(get_chat_administrators=fake_get_chat_administrators)
    context = SimpleNamespace(bot=bot)

    await sample(update, context)

    assert called is True


@pytest.mark.anyio
async def test_restricted_blocks_non_admins(monkeypatch):
    called = False

    @restricted
    async def sample(update, context):
        nonlocal called
        called = True

    async def fake_get_chat_administrators(chat_id: int):
        return [SimpleNamespace(user=SimpleNamespace(id=99))]

    update = _build_update(user_id=1)
    bot = SimpleNamespace(get_chat_administrators=fake_get_chat_administrators)
    context = SimpleNamespace(bot=bot)

    await sample(update, context)

    assert called is False
