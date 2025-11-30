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
- **Specialized Agents:** Create and manage specialized AI agents with different models and capabilities via the `/agents` command. Agents can delegate tasks to each other and automatically use tools when supported.
- **OpenRouter Integration:** Native support for OpenRouter's tool calling format, enabling agents to use any OpenRouter-compatible model with automatic tool support detection.
- **Secure Configuration:** API keys are stored exclusively in `.env` file and never committed to version control. Configuration files are safe to share.
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
2.  Add your API keys to the `.env` file:
    ```
    API_KEY=your-primary-api-key
    OPEN_ROUTER_API_KEY=your-openrouter-api-key
    GOOGLE_SEARCH_API_KEY=your-google-search-api-key
    ```
    **Note:** Only add the API keys you need. The system will skip prompts for keys found in `.env` during first-time setup.
3.  Run the application for the first time:
    ```bash
    python main.py
    ```
    The application will generate the default `data/config.json` file and guide you through any remaining setup.
4.  Optionally, you can customize settings by editing `data/config.json` or using the `/config` command.

**Security Note:** API keys are stored exclusively in `.env` and are never written to `config.json`. The `.env` file is ignored by git, so your keys will never be committed to version control.

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
- `/agents`: Create, list, modify, and delete specialized AI agents.
- `/exit`: Exit the application.

## Agent System

VIPER supports creating specialized AI agents that can be invoked by the primary AI or by other agents. Each agent has its own model configuration and can use tools when the model supports them.

### Creating an Agent

Use the `/agents` command and select "Create new agent" to:
1. Name your agent
2. Provide a description of its purpose
3. Select a model from OpenRouter's available models
4. Configure optional site URL and name for OpenRouter tracking

### Agent Tool Support

VIPER automatically detects whether an agent's model supports tool calling by querying the OpenRouter API:
- **Models with tool support** (e.g., GPT-4, Claude, Qwen3): Can use all available VIPER tools
- **Models without tool support** (e.g., Qwen2.5): Will respond with text only, tools automatically disabled

### Using Agents

The primary AI can invoke agents using the `AGENTS` tool:
```
Please use the Coder agent to help me write a Python function for sorting a list.
```

Agents can also invoke other agents, enabling complex multi-agent workflows.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.