"""Vercel Flask entry point (recognized as app/app.py by Vercel)."""

from app.bootstrap import create_initialized_app

app = create_initialized_app()
