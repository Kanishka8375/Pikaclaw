# PikaClaw

AI coding agent. Install and run in one command.

## Quick Start

```bash
pip install pikaclaw
pikaclaw
```

## Features

- **9 Specialized Agents**: Build, Plan, Review, Debug, Test, Security, Research, Darwin, Compact
- **20 Tools**: Read, Write, Edit, Bash, Grep, Glob, Git, WebSearch, WebFetch, TodoList, and more
- **Multi-Model Routing**: Ollama (local), Anthropic (Claude), OpenRouter (GLM-5, MiniMax M2.5)
- **Desktop App**: Native window with pywebview, React + Tailwind dark UI
- **HTTP Server**: FastAPI-based REST API
- **Security**: Secret sanitization, permission evaluation, file protection, audit logging
- **One-Command Install**: `pip install pikaclaw && pikaclaw`

## CLI Commands

```
pikaclaw          # Launch desktop app (or terminal if no pywebview)
pikaclaw chat     # Interactive terminal mode
pikaclaw doctor   # System health check
pikaclaw setup    # First-time setup wizard
pikaclaw serve    # Start HTTP API server
pikaclaw version  # Show version
pikaclaw init     # Create PIKACLAW.md in current directory
```

## Agent Permissions

| Agent | Write | Bash | Git | Spawn |
|-------|-------|------|-----|-------|
| Build ⚡ | ✅ | ✅ | ✅ | ✅ |
| Plan 📋 | ❌ | ❌ | ❌ | ❌ |
| Review 🔍 | ❌ | ✅ | ❌ | ❌ |
| Debug 🔧 | ✅ | ✅ | ✅ | ✅ |
| Test 🧪 | ✅ | ✅ | ✅ | ❌ |
| Security 🛡️ | ❌ | ✅ | ❌ | ❌ |
| Research 🌐 | ❌ | ❌ | ❌ | ❌ |

## License

MIT
