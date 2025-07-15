# Human AI Services - Frontend

A SvelteKit application demonstrating human-AI interaction patterns with voice recording and transcription capabilities.

## Features

- **Voice Recording**: Browser-based audio recording with MediaRecorder API
- **AI Transcription**: Audio-to-text conversion via backend integration
- **Multi-concept Demo**: Different interaction patterns across `/1` and `/2` routes

## Quick Start

```bash
# Install dependencies
pnpm install

# Set up environment
echo "AI_API_ENDPOINT=http://localhost:8000" > .env

# Start development server
pnpm dev

# Build for production
pnpm build
```

## Tech Stack

- **SvelteKit** - Full-stack framework
- **Svelte 5** - Component framework with runes
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Amsterdam Design System** - UI components

## Project Structure

```
src/
├── routes/           # File-based routing
│   ├── 1/           # Concept 1 demo
│   ├── 2/           # Concept 2 with recording
│   └── api/         # API endpoints
├── lib/
│   ├── components/  # Reusable Svelte components
│   └── utils/       # Utility functions
└── app.html         # HTML template
```

## Development Commands

- `pnpm dev` - Development server
- `pnpm check` - Type checking
- `pnpm lint` - Code linting
- `pnpm format` - Code formatting

## Backend Integration

Please run the API at `../ai-assist/` for this to work. Includes:
- OpenAI API integration
- Audio transcription
- Database storage

