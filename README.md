<p align="center">
  <img src="./assets/game.gif" alt="Game Demo" width="80%" height="auto">
</p>



# Steve HarvAI

<div style="display: flex; justify-content: space-between;">
    <img src="https://variety.com/wp-content/uploads/2020/07/154639_7306-e1718819031196.jpg" alt="Steve HarvAI" width="48%">
    <img src="./assets/image-1.png" alt="Steve HarvAI" width="48%">
</div>

This is a simple implementation of a "20 Questions" game that I built to showcase the capabilities of multi-agent interaction. The name "Steve HarvAI" is an homage to the famous (and hilarious) Steve Harvey, who hosted the popular game show "Let's Make a Deal."

## Project Structure
```
.
├── agents.py          # Contains the agent definitions
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

## Things To Think About

### What main steps will there be?
I think that it is natural that step of the interaction should be one turn of the game.
This means that a single step would entail:
- The guesser generates a question
- The guesser picks a topic proposal (optionally)
- The host validates the topic proposal (optionally)
- The host answers the question (if the guesser has not guessed the topic)

### How Will We Get the Agents to Interact?
The agents will be two separate entities with clearly defined boundaries to prevent accidental knowledge leakage. Both entities will share information through messages. Every external message to the agent will arrive as a `UserMessage`. These messages are then stored in the agent's message history, and the agent will use that history to generate its new output through an LLM call. Message history is essentially a conversation history or a "memory" of an agent.

In general, I follow the ReAct framework: agents are reasoning and then acting.

### What Context Does Each Agent Have?
Each agent will have the following context:
- The appropriate system message.
- The current step of the game (especially important for the Guesser, who needs to be aware of the steps left).
- The conversation history between the agents.
Additionally, the Host also knows about the topic.

### What Pieces Could You Keep Static at First to Simplify Things?
What helped me initially simplify things:
- Keep system prompts short and laconic to avoid inducing unwanted, complex behavior early on.
- Use a simple, constant topic for early development and debugging (I chose 'Dog').
- Use a lightweight, reliable model (I chose `gpt-4o-mini`).
- Use a response format to ensure that the output space of the agents is constrained and more deterministic.

### How Do You Want to Handle Errors and Other Issues?
Since my script is quite simple, I assume there will be no errors during the API calls. However, in my professional work, I noticed that errors do happen, so I:
- Retry the API calls a couple of times.
- Have a fallback model in case the API completely fails (e.g., different API provider, different model, model without images, etc.).
- Use a lightweight, local model to approximate the output that I'd get from the LLM.
  
The rest of the logic is quite reliable, mostly due to the use of structured responses from the API.

### Reliability
Once I implemented a rough version of the game, I noticed that the flow of the game and the behavior of the agents were not always correct. This is why I decided to implement a `reasoning` field in the tools. This allowed me to "debug" the agents by checking what they are reasoning about and hence understand if they "know what they are supposed to know." This is how I realized that I swapped `SYSTEM_PROMPT_HOST` and `SYSTEM_PROMPT_GUESSER` in the code.

The reasoning also serves as a Chain of Thought (CoT) prompting technique (note that the `reasoning` field always comes as the first attribute of the tool's `BaseModel`, ensuring that CoT is triggered BEFORE generating the rest of the output).

### Evaluation
A simple evaluation I implemented is running the game multiple times and counting the number of wins and losses.
```bash
python parallel_game.py --num_games 100
```
It is a simple evaluation but already serves as a good baseline. It allows me to have a rough idea of which categories are easier or harder for the Guesser (obviously in my case, animals, plants, and mountains are easier to guess than people or landmarks). I can quickly find out the average win rate, etc.

However, there are several other aspects that evaluation should capture:
- We are in a multi-agent setting, so the agents influence each other. How do we determine whether the Guesser regressing does not simply come from Host improving? We need joint, but also individual evaluation metrics from which we could create one global evaluation metric (similar to Generative Adversarial Networks or popular Self-Play AIs).
- How do we benchmark against human players?

We can vary the difficulty of the game by broadening or narrowing the category of the topic. I decided to go for all the tangible, real-world objects. However, once we start introducing abstract concepts, the game ought to get much harder for both the Guesser and the Host (to understand the topic and provide good answers).

### Testability
I parallelized the game so that we can run multiple games in parallel.
```bash
python parallel_games.py --num_games 5
```
Each game run has its own unique UUID and produces a color-coded log that can be investigated after the run.

This UUID could be directly linked to the version of the system prompt so that we could investigate the influence of the system prompts on the behavior of the agents.

At scale, I would probably write a lightweight experiment managing framework that would use WandB or something similar, allowing me to quickly analyze and inspect the results.

### Be Sure to Note Where the Agents Get Stuck
Sometimes the Guesser performs a "breadth-first search" of the topic space, which takes many turns. For example, the Host chose the topic `Eiffel Tower`. Instead of asking `Is this building in Europe?` to quickly narrow down the search space, the Guesser asks questions like `Is this building a museum?`, `An art gallery?`, `A historical landmark?`, etc. Additional prompting would help here to make the Guesser more strategic. Also, the Guesser has a conviction, that if a topic is not a "living thing", it cannot be a historical person, like Cleopatra, while the Hosts shares the opposite conviction. Some more prompting would help.

Also, I struggle with the variety of topics that the Host generates. Even though I tried hard to nudge it toward diverse topics (high temperature, specific prompts, adding a random seed to break the potential prompt caching) and it helped to some degree, I still see repetitions in the topics.

### How Did You Resolve Some of the Issues You Encountered?
- I added a `reasoning` field to the tools, which helps me understand what the agents are reasoning about.
- I tinkered with the system prompts to nudge the agents toward "good behavior" (e.g., asking good questions).
- Initially, I restricted the category of questions to animals only, which helped me with debugging.
- I implemented several improvements for generating more diverse topics.

### Which Issues Are Still Outstanding? How Might You Solve Them If You Had More Time?
I managed to reach a working solution quite quickly, and I am pretty happy with the result. Probably, more prompt engineering could help, but I would quickly hit diminishing returns. While I am very happy with the Host's behavior, the quality of the Guesser might improve if we used majority voting between multiple guesses either from the same model or several different models combined (e.g., GPT-4, Sonnet, etc.).

Also, I'd take more time to figure out why the generated topics are not diverse and try to fix it! Additionally, I could not make the Guesser more aggressive in proposing topics, even when it's unsure about the answer.

### What Future Work Would You Explore, Perhaps Beyond Prompt Engineering?
I wonder how better models (o1-preview or o1-mini) would perform. Due to their latency and costs, I haven't tested them. Also, I would try to encourage the Guesser to use its time more strategically. An idea would be to make it explore the "depth" of the problem for the first couple of turns, but then closer to the end, really focus on trying to guess the topic. What would definitely help is for the Guesser to have experience playing multiple games in the past so it can use that experience to inform its strategy for future games.
