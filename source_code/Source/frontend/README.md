# Multi-Domain Agentic RAG — Web Client Frontend

[![Next.js: 14](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.dot.js&logoColor=white)](https://nextjs.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg?logo=tailwind_css&logoColor=white)](https://tailwindcss.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)

The interactive web client application for the **Multi-Domain Agentic RAG Platform**, engineered with Next.js 14 App Router, TypeScript, and TailwindCSS. It provides real-time WebSocket state streaming, live reasoning telemetry badges, KaTeX mathematical formula rendering, and 1-click Google Workspace export.

---

## 🌟 Key Features

1. **Real-Time WebSocket State Synchronization:**
   - Connects to `/api/ws/chat/{session_id}` for bidirectional streaming.
   - Dynamically visualizes LangGraph execution steps as live badges (`[Router: Computer Science]` $\rightarrow$ `[Hybrid Search: bge-m3 + BM25]` $\rightarrow$ `[Grader: Pass]` $\rightarrow$ `[Generator: Qwen2.5 7B]`).
2. **Academic Markdown & LaTeX Formula Rendering:**
   - Native integration with `react-markdown`, `remark-math`, and `rehype-katex` for instantaneous rendering of inline and block mathematical formulas.
   - Syntax-highlighted code blocks with copy-to-clipboard functionality.
3. **Multi-Domain Repository Selector:**
   - Dedicated UI panel for toggling between the 8 specialized knowledge domains (CS, Electronics, Math, Physics, Agriculture, Economics, Law, Medicine).
   - Document upload and indexing progress indicators.
4. **Research Workspace & Scientific Console:**
   - Real-time token generation throughput counter (tokens/s).
   - Direct 1-click export of synthesized reports to Google Docs and Google Sheets via OAuth2.

---

## 📁 Frontend Project Structure

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout & font configurations
│   │   ├── page.tsx            # Main chat interface & workspace
│   │   ├── login/              # Authentication & JWT sign-in
│   │   └── globals.css         # Tailwind global styles
│   ├── components/             # Reusable UI components
│   │   ├── ChatStream.tsx      # WebSocket chat message & token streaming
│   │   ├── ReasoningBadge.tsx  # Dynamic node state visualization badges
│   │   ├── DomainSelector.tsx  # Multi-domain knowledge base switcher
│   │   ├── LatexRenderer.tsx   # KaTeX mathematical equation parser
│   │   └── ExportModal.tsx     # Google Workspace export controller
│   ├── hooks/                  # Custom React hooks
│   │   └── useWebSocketChat.ts # WebSocket lifecycle, reconnection & state buffer
│   └── lib/                    # API client helpers & utility functions
├── public/                     # Static assets & brand icons
├── Dockerfile                  # Container build specification
├── package.json                # Node dependencies & build scripts
├── tailwind.config.ts          # TailwindCSS styling configuration
└── tsconfig.json               # TypeScript compiler rules
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Node.js 18.17+ or Node.js 20+
- Running backend instance (default: `http://localhost:8000`)

### 2. Configuration
Copy the sample environment configuration:
```bash
cp .env.local.example .env.local
```
Ensure `.env.local` points to the FastAPI backend:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Installation & Run
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm run start
```
Access the client interface at `http://localhost:3000`.

---

## 🐳 Docker Deployment

The frontend is containerized using a multi-stage Dockerfile:
```bash
docker build -t agentic-frontend .
docker run -p 3000:3000 agentic-frontend
```
Or launched seamlessly as part of the complete stack via root `docker-compose.yml`.
