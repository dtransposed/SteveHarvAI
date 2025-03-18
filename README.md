<p align="center">
  <img src="./assets/game.gif" alt="Game Demo" width="80%" height="auto">
</p>



# Steve HarvAI

<div style="display: flex; justify-content: space-between;">
    <img src="https://variety.com/wp-content/uploads/2020/07/154639_7306-e1718819031196.jpg" alt="Steve HarvAI" width="48%">
    <img src="./assets/image-1.png" alt="Steve HarvAI" width="48%">
</div>

This is a simple implementation of a "20 Questions" game that I built to showcase the capabilities of multi-agent interaction. The name "Steve HarvAI" is an homage to the famous (and hilarious) Steve Harvey, who hosted the popular game show "Family Feud."

## Project Structure
```
.
├── agents.py          # Imported from openai-agents package
├── custom_agents.py   # Contains the custom agent implementations for the game
├── config.py          # Contains configuration settings such as the model type
├── game.py            # Contains the game logic (main script)
├── messages.py        # Contains the message objects
├── prompts.py         # Contains the system prompts for the agents
├── tools.py           # Contains the tools that the agents can use
├── utils.py           # Contains utility functions
├── README.md          # This file
├── assets             # Contains assets
├── pyproject.toml     # Contains project metadata and dependencies
└── parallel_game.py   # Contains the script for running multiple games in parallel (see game.py for details)
```

## Setup
```bash
# Create a virtual environment and install dependencies
uv venv && source .venv/bin/activate  
uv sync
```
Also, do not forget to set the `OPENAI_API_KEY` environment variable to your API key.

## Running

Whenever you run the game, it will create a new log file in the `game_logs` directory.
This way, you can either inspect the game progress in your terminal (with pretty coloring for easier reading)
or you can open the log file in a text editor to inspect the full run.

### Run One Game
```bash
# Run the game
python game.py
# You can also run the game with a specific topic for the Guesser to guess
python game.py --topic "Sam Altman"
```

### Run Multiple Games in Parallel
```bash
# Run multiple games in parallel
# This will clear the logs directory before running (to avoid clutter) and run 20 games in parallel
python parallel_game.py \
--num_games 20 \ # Number of games to run in parallel
--clear_logs \ # Clear the logs directory before running; just for convenience (default: True)
```

The output will be a summary of all the games:
```bash
Games played: 40
Wins: 19
Losses: 21
Topics guessed correctly: ['Eiffel Tower', 'Eiffel Tower', 'Pyramids of Giza', 'The Great Wall of China', 'Eiffel Tower', 'Pyramids of Giza', 'Blender', 'The Great Wall of China', 'Kangaroo', 'Puzzle', 'Eiffel Tower', 'Eiffel Tower', 'Great Wall of China', 'Eiffel Tower', 'Machu Picchu', 'Kilimanjaro', 'The Great Wall of China', 'Taj Mahal', 'The Great Wall of China']
Topics not guessed: ['Pyramids', 'Eiffel Tower', 'Chocolate Cake', 'Eiffel Tower', 'Eiffel Tower', 'Cleopatra', 'Taj Mahal', 'Model Airplane', 'Sundial', 'Eiffel Tower', 'Taco', 'Pyramid', 'Volcano', 'Pyramids', 'Kilimanjaro', 'Parthenon', 'Pyramids', 'Lighthouse', 'Pyramids', 'Eiffel Tower', 'Pyramids']
```

## Model Configuration

The project currently uses the following OpenAI models as configured in `config.py`:
- `gpt-4o-mini` for the Guesser agent 
- `gpt-4o-mini` for the Host agent
- `o3-mini` for the Topic Proposal agent

We'd rather use `o3-mini` for all agents, but it takes more time to create a conversation with it.

You can modify this configuration file to use different OpenAI models if desired.
