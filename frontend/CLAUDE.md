# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Svelte 5 Usage
Read https://svelte.dev/llms-small.txt for correct Svelte 5 usage patterns and syntax.

## Project Structure
Add /src directory to context when working on this project.

This frontend is part of a larger human-ai-services-experiments repository containing:
- `/frontend/` - This SvelteKit application
- `/ai-assist/` - FastAPI backend service with OpenAI integration
- `/stadstuin/` - Additional project components

The ai-assist backend provides:
- OpenAI API integration
- Audio transcription capabilities
- Database connectivity (PostgreSQL)
- FastAPI endpoints for AI services

## Common Development Commands

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

### Package Management
- Uses `pnpm` as package manager (note: pnpm-lock.yaml present)

## Architecture Overview

### SvelteKit Application
- Built with SvelteKit and Svelte 5
- Uses file-based routing in `/src/routes/`
- TypeScript support enabled
- Vite as build tool

### Key Application Features
- **Multi-concept Demo**: Routes for different concepts (`/1`, `/2`)
- **Audio Recording**: Voice recording functionality with MediaRecorder API
- **Mock Transcription**: Server-side transcription endpoint with mock responses
- **Amsterdam Design System**: Uses Amsterdam Design System components and styling

### Route Structure
- `/` - Home page with navigation links
- `/1` - Concept 1 page
- `/2` - Concept 2 main page
- `/2/record` - Audio recording interface
- `/2/record/transcribe` - API endpoint for transcription (POST)

### Component Architecture
- **Header**: Logo and navigation component
- **MainMessage**: Reusable message display component
- **ButtonSketchy**: Custom styled button component
- **CalloutBubble**: Message bubble component
- **SingleRecordingSection**: Recording-specific UI component

### State Management
- Uses Svelte 5 runes (`$state`, `$derived`, `$props`)
- Recording state handled in-component with reactive variables
- Utility functions in `/src/lib/utils/recording.js` for recording logic

### API Integration
- Mock transcription service at `/2/record/transcribe`
- FormData handling for audio file uploads
- Currently returns hardcoded Dutch transcription responses
- Additional API endpoints at `/api/analyze` and `/api/chat`
- Integration with backend ai-assist service for real AI capabilities

### Styling Approach
- Component-scoped CSS in `.svelte` files
- Amsterdam Design System CSS classes
- Responsive design with mobile breakpoints
- Custom SVG icons in `/static/images/`

## Important Development Notes

### Svelte 5 Patterns
- Use `$state()` for reactive variables
- Use `$derived()` for computed values
- Use `$props()` for component props
- Use `{@render children()}` for slot content

### Recording Implementation
- Uses browser MediaRecorder API
- Audio chunks collected and converted to Blob
- Transcription via POST to `/2/record/transcribe`
- Mock responses currently implemented

### Design System Integration
- Amsterdam Design System components available
- Typography and color tokens from design system
- Consistent spacing and layout patterns
- Design system assets, CSS, React components, and icons installed
- Tokens for consistent theming across components

## Backend Integration
The frontend integrates with the ai-assist FastAPI backend:
- Audio transcription via Whisper API
- OpenAI chat completions
- Database storage for conversation history
- Real-time AI assistance capabilities

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.