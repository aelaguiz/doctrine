# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Make Real is a Next.js application that transforms hand-drawn wireframes into working HTML prototypes using AI. Built on the tldraw SDK, it allows users to draw UI mockups on a canvas and generate interactive HTML/CSS/JavaScript implementations via OpenAI, Anthropic, or Google AI models.

Live at: https://makereal.tldraw.com

## Development Commands

```bash
yarn install    # Install dependencies
yarn dev        # Dev server on http://localhost:3000
yarn build      # Production build
yarn start      # Production server
yarn lint       # Lint code
```

No test suite exists in this project. TypeScript strict mode is disabled (`strict: false` in tsconfig.json).

## Architecture

### Core Flow

1. User draws wireframes on tldraw canvas
2. Selected shapes captured as JPEG (max 1000px) via `editor.toImage()`
3. Image + prompts sent to AI provider API routes
4. Streamed HTML response parsed for `<!DOCTYPE html>` ... `</html>` boundaries
5. Generated HTML rendered in PreviewShape iframe (900x900 default)
6. Completed HTML uploaded to Vercel Postgres via `uploadLink()`

### Host-Based Routing

`middleware.ts` rewrites all requests based on hostname:
- `makereal.tldraw.link` → `/makereal.tldraw.link/...` (shared link viewer)
- Everything else → `/makereal.tldraw.com/...` (main app)

This means the actual app code lives under `app/makereal.tldraw.com/` and link viewing under `app/makereal.tldraw.link/`.

### Key Components

**useMakeReal Hook** (`app/hooks/useMakeReal.ts`)
- Main orchestration: validates keys, captures image, creates PreviewShape, streams response
- Supports **"all" provider mode** (`settings.provider === 'all'`) that runs OpenAI, Anthropic, and Google in parallel via `Promise.allSettled`, creating labeled previews for each
- Iterative refinement: when previous PreviewShapes are selected, their HTML is passed to the AI
- Error handling categorizes errors (rate limit, auth, model access, token limit, network) into user-friendly toasts

**PreviewShape** (`app/PreviewShape/PreviewShape.tsx`)
- Custom tldraw shape rendering generated HTML in an iframe
- Streams HTML in real-time via `parts` prop updates during generation
- Supports interaction mode (double-click), copy HTML/URL, open in new window

**Settings System** (`app/lib/settings.tsx`)
- `MIGRATION_VERSION = 13` — increment when changing settings schema
- Settings persisted in localStorage as `makereal_settings_2`, version as `makereal_version`
- Migration runs in `InsideTldrawContext` on mount (`app/makereal.tldraw.com/page.tsx`)
- Default models after latest migration: `gpt-5`, `claude-sonnet-4-6`, `gemini-3-pro-preview`
- Supports per-provider custom prompts (`prompts.openai`, `prompts.anthropic`, `prompts.google`)

**Prompt Engineering** (`app/prompt.ts`)
- Current production prompt: `NOVEMBER_19_2025`
- Legacy prompts preserved: `LEGACY_SYSTEM_PROMPT`, `IMPROVED_ORIGINAL`
- Additional prompt markdown files in `prompts/` directory at repo root (per-provider variants, scratchpad)

### API Routes

All under `app/makereal.tldraw.com/api/`, accepting `{ apiKey, messages, model, systemPrompt }` and streaming text responses. `maxDuration: 60` seconds, `force-dynamic`.

**OpenAI** (`api/openai/route.ts`)
- gpt-5 models use `openai.responses('gpt-5')` with `temperature: 0` (no seed)
- Other models use `temperature: 0, seed: 42`

**Anthropic** (`api/anthropic/route.ts`)
- `claude-3-7-sonnet-20250219 (thinking)`: extended thinking with `budgetTokens: 12000`, `temperature: 0, seed: 42`
- `claude-3-7-sonnet-20250219`: `temperature: 0, seed: 42`
- All other models: no temperature/seed set (API defaults)

**Google** (`api/google/route.ts`)
- All models: `temperature: 0, seed: 42`

**Replit** (`api/replit/route.ts`)
- Not an AI route — exports generated HTML to a new Repl via Replit's external claims API
- Uses `process.env.REPLIT_CLAIMS_KEY`

### Message Construction

**getMessages** (`app/lib/getMessages.ts`)
- Builds multimodal message array: canvas image → optional text → previous HTML (for iterations)
- Previous preview screenshots are commented out — only previous HTML code is passed
- Text extraction (`getTextFromSelectedShapes`) is also currently commented out in `useMakeReal.ts`

## Code Patterns

### Adding a New AI Provider

1. Add provider config to `PROVIDERS` array in `app/lib/settings.tsx`
2. Create API route at `app/makereal.tldraw.com/api/<provider-id>/route.ts` using Vercel AI SDK's `streamText`
3. Add `case` in the `switch (provider)` block in `useMakeReal.ts`

### Modifying Prompts

1. Create new prompt constant in `app/prompt.ts` (must export `{ system: string, user: (sourceCode: string) => string }`)
2. Update references in `app/lib/settings.tsx` (defaults and migration)
3. Increment `MIGRATION_VERSION` to push prompt update to existing users

### Settings Migrations

1. Increment `MIGRATION_VERSION` in `app/lib/settings.tsx`
2. Add `if (version < NEW_VERSION) { ... }` block in `applySettingsMigrations`

### Adding New Models

Update the `models` array for the relevant provider in `app/lib/settings.tsx`. Optionally add a migration to set it as the default for existing users.

## Environment Variables

Users primarily configure API keys via the in-app Settings UI. Server-side env vars:

- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` — optional server defaults
- `REPLIT_CLAIMS_KEY` — for Replit export feature
- `NEXT_PUBLIC_GA4_MEASUREMENT_ID` — Google Analytics
- Vercel Postgres credentials — for link sharing (`uploadLink`)

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Canvas**: tldraw 4.x
- **AI SDKs**: Vercel AI SDK (`ai`) with `@ai-sdk/openai`, `@ai-sdk/anthropic`, `@ai-sdk/google`
- **Styling**: Tailwind CSS
- **State**: tldraw atoms (`app/lib/settings.tsx`)
- **Storage**: Vercel Postgres (link uploads), localStorage (settings/canvas)
