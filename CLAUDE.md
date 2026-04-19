# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**gutwise** — a FODMAP Menu Analyzer for IBS management. Users upload a food/menu photo and the app uses Claude's vision model to assess how IBS-friendly each dish is.

## Running the App

```bash
# Set API key (or use .env file)
export ANTHROPIC_API_KEY=your_key_here

# Start server
python server.py
# Accessible at http://localhost:5050
```

Dependencies (install manually if missing): `anthropic`, `flask`, `python-dotenv`

## Architecture

**Two files form the entire application:**

- [server.py](server.py) — Flask backend. Serves the HTML frontend and exposes one analysis endpoint: `POST /analyze`. Receives `{image: base64string, media_type: string}`, calls Claude Sonnet 4.6 with a structured FODMAP-analysis prompt, returns structured JSON.
- [ibs-fodmap-analyzer.html](ibs-fodmap-analyzer.html) — Single-page frontend. Handles file upload/drag-drop, converts images to base64, calls `/analyze`, and renders results.

**Request flow:**
1. User uploads image in browser
2. JS converts to base64 and POSTs to `/analyze`
3. Flask forwards to Claude vision API with a FODMAP-scoring prompt
4. Claude returns structured JSON (dish name, 0–100 score, rating, ingredients, modification tips)
5. Frontend renders score ring, color-coded badge, ingredient tags, and tips

**Claude API usage:** `claude-sonnet-4-6`, max 1000 tokens, expects JSON in the response content. The prompt in `server.py` instructs the model to output a specific JSON schema — changes to the response schema must be reflected in both the backend parsing and the frontend rendering logic.
