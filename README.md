# VIPER

**A developer-focused, terminal-based AI chat interface.**

VIPER (Viper Is a Python-based Extensible repl) is a highly modular and extensible AI assistant for your command-line workflows. It supports custom tools, conversation management, and a rich, configurable UI. It's designed for power users who want a tailored AI experience directly in their terminal.

---

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Command System](#command-system)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Conversation Management:** Start new conversations, save and continue existing ones, list all conversations, search by title or content, and delete conversations.
- **Rich Terminal UI:** Styled menus, tables, and panels, streaming AI responses with live markdown rendering, syntax highlighting for JSON, and interactive prompts.
- **Advanced AI & Tool Integration:** Dynamically loads and integrates custom tools from the `tools/` directory. The AI can create and execute multi-step plans using the available tools.
- **Configurable Execution:** Control tool usage with settings for automatic execution of destructive or non-destructive actions.
- **Token Management:** Accurately tracks conversation token count to manage the context window effectively.
- **Persistent Configuration:** Settings are saved to `data/config.json` and loaded on startup.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- An API key for your chosen AI model (e.g., OpenAI, Gemini)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/VIPER.git
    cd VIPER
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root of the project.
2.  Add your API key to the `.env` file:
    ```
    API_KEY=your-api-key
    ```
3.  Run the application for the first time to generate the default `data/config.json` file.
4.  Optionally, you can customize the configuration by editing `data/config.json`.

---

## Usage

Run the application:

```bash
python main.py
```

---

## Command System

VIPER uses a slash command system for navigation and control:

- `/help`: Show available commands.
- `/new`: Start a new conversation.
- `/switch <id>`: Switch to a different conversation.
- `/list`: List all conversations.
- `/search <query>`: Search conversations.
- `/delete <id>`: Delete a conversation.
- `/config`: Open the configuration menu to manage settings.
- `/tools`: List all available tools and their descriptions.
- `/exit`: Exit the application.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.