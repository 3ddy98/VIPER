# VIPER

An advanced, tool-augmented conversation manager with a beautiful terminal UI, built with the Rich Python library and a highly modular architecture.

## Features

✨ **Conversation Management**
- 🆕 Start new conversations (auto-titled from first message)
- 💾 Save and continue existing conversations
- 📋 List all conversations with details
- 🔍 Search conversations by title or content
- 🗑️ Delete conversations
- 🔄 Simple numeric IDs (1, 2, 3...) for easy reference

✨ **Rich Terminal UI**
- Beautiful styled menus, tables, and panels
- Streaming AI responses with live markdown rendering
- Structured JSON output with syntax highlighting
- Color-coded and animated UI elements
- Interactive prompts and confirmations

✨ **Advanced AI & Tool Integration**
- **Tool Support:** Dynamically loads and integrates custom tools from the `tools/` directory.
- **Planning Engine:** The AI can create and execute multi-step plans using the available tools.
- **Configurable Execution:** Control tool usage with settings for automatic execution of destructive or non-destructive actions.
- **Token Management:** Accurately tracks conversation token count to manage the context window effectively.

✨ **Slash Command System**
- `/help` - Show available commands
- `/new` - Start a new conversation
- `/switch <id>` - Switch to a different conversation
- `/list` - List all conversations
- `/search <query>` - Search conversations
- `/delete <id>` - Delete a conversation
- `/config` - Open the configuration menu to manage settings
- `/tools` - List all available tools and their descriptions
- `/exit` - Exit the application

✨ **Persistent Configuration**
- Settings changed in the `/config` menu are saved to `data/config.json` and loaded on startup.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python chat_manager.py
```

## Project Structure

```
SEBESKYGPT/
├── data/
│   └── config.json            # Persisted user configuration
├── modules/                    # Core application modules
│   ├── __init__.py            # Package initialization
│   ├── banner.py              # ASCII art banner
│   ├── commands.py            # Slash command handling
│   ├── config.py              # Default configuration constants
│   ├── config_persistence.py  # Saves and loads configuration
│   ├── conversation_manager.py # Conversation and AI logic
│   ├── renderer.py            # Rich UI rendering functions
│   ├── token_manager.py       # Manages conversation token counting
│   └── tool_manager.py        # Loads and executes tools
├── tools/                      # Directory for custom tools
│   └── README.md              # Documentation for creating tools
├── chat_manager.py            # Main application entry point
├── conversations.json         # Stored conversation history
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Module Architecture

Our modular architecture separates concerns into distinct, well-defined modules:

---

#### **`conversation_manager.py`** - Core Logic Layer
**Purpose:** The central orchestrator of the application. It manages the conversation flow, interacts with the AI, and coordinates with other modules like the `ToolManager` and `TokenManager`.
**Contains:** `ConversationManager` class, AI response streaming, tool/plan execution logic, and conversation CRUD operations.

---

#### **`tool_manager.py`** - Tool Integration Layer
**Purpose:** Dynamically loads, validates, and executes tools from the `tools/` directory. It provides the AI with tool specifications and handles the safe execution of tool methods.
**Contains:** `ToolManager` class, dynamic module loading, tool specification generation, and method execution with safety checks.

---

#### **`commands.py`** - Command Layer
**Purpose:** Handles all user-facing slash commands. It parses user input and calls the appropriate functions in other modules. It also manages the interactive configuration menu.
**Contains:** `handle_command()` and `show_config_menu()` functions, command parsing, and validation logic.

---

#### **`renderer.py`** - Presentation Layer
**Purpose:** Responsible for all UI output using the `rich` library. It ensures a consistent and beautiful user interface.
**Contains:** Functions for displaying tables, markdown, JSON, banners, plans, and status bars (`render_json_response`, `show_conversations_table`, etc.).

---

#### **`config.py`** - Default Configuration
**Purpose:** Provides the default, fallback configuration for the application. These are the initial settings used if no `data/config.json` exists.
**Contains:** `CLIENT_CONFIG`, `TOOL_CONFIG`, `UI_CONFIG`, `SYSTEM_PROMPT`, and other default constants.

---

#### **`config_persistence.py`** - Configuration Persistence
**Purpose:** Handles saving the user's settings from the `/config` menu to a JSON file, so they persist across sessions.
**Contains:** `save_config()` and `load_config()` (implicitly used) functions for JSON serialization.

---

#### **`token_manager.py`** - Tokenization Layer
**Purpose:** Provides accurate token counting for conversations. This is crucial for managing the AI's context window and preventing errors.
**Contains:** `TokenManager` class, using the `tiktoken` library to count tokens based on the selected model.

---

#### **`banner.py`** - Display Utility
**Purpose:** A simple utility module that returns the ASCII art banner for display by the `renderer` module.
**Contains:** `get_banner()` function.
