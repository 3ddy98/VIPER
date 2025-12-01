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
- **Adaptive Plan Execution:** AI agents can reevaluate and modify plans after each step based on execution results. Supports automatic error recovery, early completion, and dynamic plan updates with full transparency and user control.
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

There are two ways to install VIPER:

#### Option 1: Global CLI Installation (Recommended)

Install VIPER as a global command-line tool using `pipx`:

1.  Clone the repository:
    ```bash
    git clone https://github.com/3ddy98/VIPER.git
    cd VIPER
    ```

2.  Install with pipx (recommended for CLI tools):
    ```bash
    pipx install .
    ```

    Or using pip:
    ```bash
    pip install .
    ```

3.  Run VIPER from anywhere:
    ```bash
    VIPER                    # Run in current directory
    VIPER --dir ~/projects   # Run in specified directory
    VIPER --version          # Show version
    ```

#### Option 2: Development Installation

For development or running directly from source:

1.  Clone the repository:
    ```bash
    git clone https://github.com/3ddy98/VIPER.git
    cd VIPER
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run from the project directory:
    ```bash
    python main.py
    ```

### Configuration

1.  Create a `.env` file in the VIPER installation directory.
2.  Add your API keys to the `.env` file:
    ```
    API_KEY=your-primary-api-key
    OPEN_ROUTER_API_KEY=your-openrouter-api-key
    GOOGLE_SEARCH_API_KEY=your-google-search-api-key
    ```
    **Note:** Only add the API keys you need. The system will skip prompts for keys found in `.env` during first-time setup.

3.  Run VIPER for the first time:
    ```bash
    VIPER                    # If using global installation
    # OR
    python main.py           # If running from source
    ```
    The application will generate the default `data/config.json` file in the VIPER installation directory and guide you through any remaining setup.

4.  Optionally, you can customize settings by editing `data/config.json` or using the `/config` command.

**Important Notes:**
- **Security:** API keys are stored exclusively in `.env` and are never written to `config.json`. The `.env` file is ignored by git, so your keys will never be committed to version control.
- **Data Persistence:** VIPER stores all configuration, conversations, and agents in the installation directory. This means your settings and data persist across all working directories. Use `VIPER --dir /path/to/project` to change your current working directory for file operations.

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

## Adaptive Plan Execution

VIPER features an advanced **adaptive plan execution** system that allows AI agents to intelligently modify their plans in real-time based on execution results.

### How It Works

1. **Initial Plan Creation**: The AI creates a multi-step plan to accomplish a task
2. **Step-by-Step Execution**: Each step is executed sequentially
3. **Reevaluation**: After each step (success or failure), the AI analyzes the results
4. **Decision Making**: The AI can:
   - **CONTINUE** - Proceed with the existing plan
   - **UPDATE_PLAN** - Modify the plan (add/remove/change steps)
   - **COMPLETE** - Mark plan as finished early if goals are achieved
   - **ABORT** - Stop execution due to unrecoverable errors

### Benefits

- **Error Recovery**: Automatically handles failures by creating recovery plans
- **Adaptive Planning**: Plans evolve based on actual results rather than assumptions
- **Efficiency**: Completes early when goals are achieved without running unnecessary steps
- **Transparency**: Visual diffs show exactly what changes the AI proposes
- **User Control**: All plan updates require user confirmation before execution

### Example: Automatic Recovery

```
Initial Plan: Load and process data
Step 1: Read data.csv → FAILED (file not found)

AI proposes recovery plan:
Step 1: Create sample data.csv
Step 2: Read data.csv
Step 3: Process data

User confirms → Execution continues with recovery plan
```

### Visual Feedback

When plans are updated, VIPER displays a color-coded diff showing:
- ✓ Added steps (green)
- ✗ Removed steps (red)
- ~ Modified steps (yellow)
- = Unchanged steps (gray)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.