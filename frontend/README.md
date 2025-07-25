# Human AI Services - Frontend

A SvelteKit application demonstrating human-AI interaction patterns for municipal services with advanced voice recording, transcription, and AI integration capabilities.

## Features

### Core Functionality
- **Voice Recording**: Browser-based audio recording with MediaRecorder API and multiple recording patterns
- **Real-time Transcription**: Audio-to-text conversion via Whisper API integration
- **Intent Analysis**: AI-powered intent recognition from voice input
- **Multi-language Support**: Dutch (default), English, and French with automatic detection
- **AI Chat Interface**: OpenAI-powered conversational AI for citizen services

### Two Concept Demonstrations
- **Concept 1**: Intent analysis workflow with dynamic form construction
- **Concept 2**: Voice recording with transcription and AI agent chat

### Technical Features
- **Session Management**: Persistent user sessions with localStorage
- **Error Handling**: Global error management with auto-dismiss
- **Inactivity Timer**: Automatic session cleanup and redirect
- **Development Tools**: API debugging and device testing interfaces

## Quick Start

```bash
# Install dependencies
pnpm install

# Set up environment (optional - defaults to localhost:8000)
echo "AI_API_ENDPOINT=http://localhost:8000" > .env

# Start development server
pnpm dev

# Build for production
pnpm build
```

## Tech Stack

- **SvelteKit** - Full-stack framework with file-based routing
- **Svelte 5** - Component framework with runes (`$state`, `$derived`, `$props`, `$effect`)
- **TypeScript** - Type safety throughout the application
- **Vite** - Build tool and development server
- **Amsterdam Design System** - Primary UI framework with custom sketchy styling
- **svelte-i18n** - Internationalization with SSR support
- **Patrick Hand Font** - Custom typography for sketchy aesthetic

## Project Structure

```
src/
├── app.d.ts          # SvelteKit type definitions
├── app.html          # HTML template
├── hooks.server.ts   # Server-side hooks for i18n
├── main.css          # Global CSS with Amsterdam Design System
├── routes/           # File-based routing
│   ├── +layout.svelte        # Root layout with i18n and error handling
│   ├── +page.svelte          # Homepage with concept selection
│   ├── 1/                    # Concept 1: Intent Analysis
│   │   ├── +page.svelte      # Intent analysis landing
│   │   ├── choose/           # Intent selection when confidence is low
│   │   ├── construct/[slug]/ # Dynamic form construction
│   │   ├── end/              # Completion page
│   │   └── feedback/         # Feedback collection
│   ├── 2/                    # Concept 2: Voice Recording
│   │   ├── +page.svelte      # Voice recording landing
│   │   ├── record/           # Recording with transcription
│   │   ├── agents-chat/      # AI agent chat interface
│   │   ├── end/              # Completion page
│   │   └── feedback/         # Feedback collection
│   ├── api/                  # API endpoints (5 endpoints)
│   │   ├── analyze/          # Audio analysis for intent
│   │   ├── chat/             # Chat interface
│   │   └── yap/              # Transcription endpoints
│   ├── test-devices/         # Microphone testing
│   └── test-endpoints/       # API testing interface
├── lib/
│   ├── components/   # 16 reusable Svelte components
│   │   ├── ButtonSketchy.svelte          # Main sketchy button
│   │   ├── SingleRecordingSection.svelte # Core recording component
│   │   ├── TranscriptionRecordingSection.svelte # Recording with transcription
│   │   ├── Header.svelte                 # App header with language selector
│   │   ├── ChatMessage.svelte            # Chat interface components
│   │   └── ... (11 more components)
│   ├── i18n/         # Internationalization (4 files)
│   │   ├── index.ts          # i18n configuration
│   │   ├── en.json           # English translations
│   │   ├── nl.json           # Dutch translations (default)
│   │   └── fr.json           # French translations
│   ├── stores/       # Svelte stores (5 stores)
│   │   ├── apiStore.ts       # API response storage
│   │   ├── sessionStore.ts   # Session management
│   │   ├── configStore.ts    # App configuration
│   │   ├── errorStore.ts     # Error handling
│   │   └── languageStore.ts  # Language switching
│   └── utils/        # Utility functions (2 files)
│       ├── apiHelpers.ts     # Centralized API communication
│       └── inactivityTimer.ts # Auto-redirect on inactivity
└── static/           # Static assets including custom SVG icons
```

## Development Commands

### Development
- `pnpm dev` - Start development server
- `pnpm dev -- --open` - Start development server and open in browser

### Build & Preview
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build

### Code Quality
- `pnpm check` - Run Svelte type checking
- `pnpm check:watch` - Run Svelte type checking in watch mode
- `pnpm lint` - Run Prettier and ESLint checks
- `pnpm format` - Format code with Prettier

## Backend Integration

The frontend integrates with the ai-assist FastAPI backend located at `../ai-assist/`. The backend provides:

- **OpenAI API Integration**: Chat completions and AI assistance
- **Whisper API**: Audio transcription capabilities
- **PostgreSQL Database**: Conversation history and session storage
- **Real-time Processing**: Session-based transcription with start/next patterns
- **Intent Recognition**: AI-powered analysis of user voice input

### API Endpoints Used
- `/api/analyze` - Audio analysis for intent recognition
- `/api/chat` - AI chat interface (supports JSON and FormData)
- `/api/yap` - Speech-to-text transcription
- `/api/yap/start` - Initialize transcription session
- `/api/yap/next` - Continue transcription session

## Architecture Highlights

### State Management
- **Reactive Stores**: 5 Svelte stores for persistent state management
- **localStorage Integration**: Session persistence across browser sessions
- **Global Error Handling**: Centralized error management with auto-dismiss

### Voice Interaction Patterns
- **Hold-to-Record**: Press and hold for recording
- **Toggle Recording**: Click to start/stop recording
- **Real-time Transcription**: Live audio-to-text conversion
- **Session-based Processing**: Continuous conversation context

### Accessibility & UX
- **Multi-language Support**: 3 languages with automatic detection
- **Responsive Design**: Mobile-first approach with Amsterdam Design System
- **Inactivity Management**: Auto-cleanup after 2 minutes of inactivity
- **Error Recovery**: Graceful error handling with user-friendly messages

### Development Features
- **API Debugging**: Built-in tools for API response inspection
- **Device Testing**: Microphone and audio device testing interface
- **Endpoint Testing**: Live API endpoint testing and validation
