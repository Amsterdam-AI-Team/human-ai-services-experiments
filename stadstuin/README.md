# Stadstuin Project

A full-stack application with a Next.js frontend and Python Flask backend, built with TypeScript and modern web technologies.

## Project Structure

```
.
├── backend/               # Python Flask backend
│   ├── app.py             # Main application entry point
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   └── utils/         # Utility functions
│   ├── package.json       # Frontend dependencies
│   └── tailwind.config.js # Tailwind CSS configuration
├── .gitignore
└── package.json           # Monorepo configuration
```

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.8+
- pip
- virtualenv (recommended for Python development)

## Getting Started

### Monorepo Setup

1. Install Node.js dependencies for the root project:
   ```bash
   npm install
   ```

### Backend Development

1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your environment variables:
   ```
   OPENAI_API_KEY=
    OPENAI_API_URL=
    DALLE_URL=
    DALLE_KEY=
   ```

4. Start the backend server:
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5000`

### Frontend Development

1. From the project root, start the Next.js development server:
   ```bash
   npm run dev:frontend
   ```
   The frontend will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev:frontend` - Start the Next.js development server
- `npm run dev:backend` - Start the Python backend server
- `npm run build` - Build the Next.js application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint

## Tech Stack

- **Frontend**:
  - Next.js 14
  - React 18
  - TypeScript
  - Tailwind CSS
  - Axios for API requests

- **Backend**:
  - Python 3.8+
  - Flask
  - RESTful API

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file in the frontend directory with:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

4. Start the frontend development server:
```bash
npm run dev
```
The frontend will run on `http://localhost:3000`

## Running the Application

1. Start the backend server first:
```bash
cd backend
python app.py
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`. The frontend communicates with the backend through the API running on `http://localhost:5000`.

## Features

- Users can submit wishes for their ideal city garden
- Wishes are combined into a prompt for image generation
- Uses Azure OpenAI's DALL-E 3 model to generate images
- Responsive design that works on both desktop and mobile
- Real-time validation and error handling
- Toast notifications for user feedback

## Development

### Backend API Endpoints

- `POST /build_prompt`: Combines wishes into a prompt for image generation
- `POST /generate_image`: Generates an image using Azure OpenAI's DALL-E 3 model

### Frontend Components

- `WishInput`: Form for submitting wishes
- `WishBubbleList`: Displays submitted wishes
- Main page layout with image generation functionality
