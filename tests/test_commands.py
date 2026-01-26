from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from telegram.ext import Application

os.environ.setdefault("APP_NAME", "TESTING")
os.environ.setdefault("TOKEN", "123:TESTTOKEN")

from src import commands
from src.config import PINNED_JOB, SOCIAL_JOB

TOKEN = "123:TESTTOKEN"


def _build_context(job_queue=None, bot=None, job=None):
    return SimpleNamespace(job_queue=job_queue, bot=bot, job=job)


def _build_update(chat_id: int = 1):
    message = SimpleNamespace(chat_id=chat_id, message_id=10)
    return SimpleNamespace(effective_message=message)


def test_register_returns_commands():
    application = Application.builder().token(TOKEN).build()

    command_list = commands.register(application)

    assert any(cmd.command == "cities" for cmd in command_list)
    assert any(handler.callback == commands.help_command for handler in application.handlers[0])


class DummyJobQueue:
    def __init__(self):
        self.jobs = {}
        self.run_calls = 0

    def get_jobs_by_name(self, name: str):
        return self.jobs.get(name, [])

    def run_repeating(
        self, callback, interval, first=0, chat_id=None, name=None, data=None
    ):
        self.run_calls += 1
        job = SimpleNamespace(
            enabled=True,
            chat_id=chat_id,
            name=name,
            data=data,
            callback=callback,
        )
        self.jobs.setdefault(name, []).append(job)
        return job


@pytest.mark.anyio
async def test_reminder_creates_jobs_when_none_exist():
    job_queue = DummyJobQueue()
    bot = SimpleNamespace(send_message=AsyncMock())
    context = _build_context(job_queue=job_queue, bot=bot)
    update = _build_update(chat_id=42)

    await commands.reminder(update, context)

    expected_names = {
        f"{PINNED_JOB}-42",
        f"{SOCIAL_JOB}-42",
    }
    assert expected_names.issubset(job_queue.jobs.keys())
    assert bot.send_message.await_count == 2


@pytest.mark.anyio
async def test_reminder_reenables_existing_jobs():
    pinned_job = SimpleNamespace(enabled=False)
    social_job = SimpleNamespace(enabled=False)

    class PreloadedJobQueue(DummyJobQueue):
        def __init__(self):
            super().__init__()
            self.jobs = {
                f"{PINNED_JOB}-1": [pinned_job],
                f"{SOCIAL_JOB}-1": [social_job],
            }

    job_queue = PreloadedJobQueue()
    bot = SimpleNamespace(send_message=AsyncMock())
    context = _build_context(job_queue=job_queue, bot=bot)
    update = _build_update(chat_id=1)

    await commands.reminder(update, context)

    assert pinned_job.enabled is True
    assert social_job.enabled is True
    assert job_queue.run_calls == 0


@pytest.mark.anyio
async def test_send_pinned_reminder_forwards_if_pinned_exists():
    pinned_message = SimpleNamespace(message_id=7)
    chat = SimpleNamespace(pinned_message=pinned_message)
    bot = SimpleNamespace(
        get_chat=AsyncMock(return_value=chat),
        forward_message=AsyncMock(),
        send_message=AsyncMock(),
    )
    context = _build_context(
        bot=bot,
        job=SimpleNamespace(chat_id=55),
    )

    await commands.send_pinned_reminder(context)

    bot.forward_message.assert_awaited_once_with(
        chat_id=55, from_chat_id=55, message_id=7
    )
    bot.send_message.assert_not_awaited()


@pytest.mark.anyio
async def test_send_pinned_reminder_sends_text_if_no_pinned():
    chat = SimpleNamespace(pinned_message=None)
    bot = SimpleNamespace(
        get_chat=AsyncMock(return_value=chat),
        forward_message=AsyncMock(),
        send_message=AsyncMock(),
    )
    context = _build_context(
        bot=bot,
        job=SimpleNamespace(chat_id=77),
    )

    await commands.send_pinned_reminder(context)

    bot.send_message.assert_awaited_once()


@pytest.mark.anyio
async def test_send_social_reminder_uses_guidebook(monkeypatch):
    expected = "social results"
    monkeypatch.setattr(commands.guidebook, "get_results", lambda **_: expected)
    bot = SimpleNamespace(send_message=AsyncMock())
    context = _build_context(bot=bot, job=SimpleNamespace(chat_id=88))

    await commands.send_social_reminder(context)

    bot.send_message.assert_awaited_once_with(
        chat_id=88, text=expected, disable_web_page_preview=True
    )
