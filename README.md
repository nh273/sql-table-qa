# SQL Chinook QA
## Installation

1. Install Python 3.11.9 using pyenv:
    ```shell
    pyenv install 3.11.9
    ```

2. Set Python 3.11.9 as the global version:
    ```shell
    pyenv local 3.11.9
    ```
3. Install poetry:
    ```shell
    curl -sSL https://install.python-poetry.org | python3 -
    ```
4. Install dependencies using poetry:
    ```shell
    poetry install
    ```
5. Adding configs
   1. Copy config file template into local config:
   ```
   cp configs/env.example configs/local.env
   ```
   2. Replace placeholder values with your own API keys

## Usage

1. Run the interactive chat interface (Streamlit app):
    ```shell
    poetry run python streamlit run app/app.py
    ```

2. To interact with experiments in `notebooks/` directory:
   - launch Jupyter:
    ```shell
    poetry run jupyter lab
    ```
    - Open your web browser and go to `http://localhost:8888`.

3. Interact with the MLflow experiment log:
   - launch Mlflow local UI:
    ```shell
    poetry run mlflow ui
    ```
    - Open your web browser and go to `http://127.0.0.1:5000`.
    - Use the MLflow UI to explore and interact with the experiment log.
    - This is a very truncated MLFlow experiment log to save of space, intended only to demonstrate what a log might look like

## Evaluation
I used gpt-4 over the UI as well as hand-generated 2 sets of evaluation questions:
- [./data/evaluation_dataset.csv](./data/evaluation_dataset.csv) contains short questions that can be answered factually from the dataset and the  corresponding answers. It also contains the SQL query to generate those answers and the tables required, to evaluate intermediate steps as needed.
- [./data/unanswerable_dataset.csv](./data/unanswerable_dataset.csv) contains questions that cannot be answered factually from the dataset, and a reasonable, polite answer that a model might use to inform the user as such.

I used gpt-3.5-turbo for both inference and evaluation, to save on cost. I find the gpt-3.5 evaluations to be quite satisfactory.

Check out the notebooks [notebooks/experiment-naive-langchain-prod.ipynb](notebooks/experiment-naive-langchain-prod.ipynb) and [notebooks/experiment-naive-langchain-qa.ipynb](notebooks/experiment-naive-langchain-qa.ipynb) and/or the 2 included mlflow runs to inspect the evaluation output.

## Approaches
(to check out each approach/version, first run `git fetch --all --tags --prune` to fetch all tags locally)

### 1. Naive chat interface with SQL executor
`git checkout tags/v2.1 -b <branch_name>`
This is a really simple approach: basically an UI that connects to OpenAI API with a system prompt that tells the bot its role as an SQL expert and instruct it to send back an SQL query that will answer the question.<br>

Then whenever the bot sends back a message with backtick, we parse it into an editable SQL field and the user can manually run it. The bot will then interpret the answer.<br>

Even though this approach technically violates the letter of the assignment (not per se a function, having a human in the loop), it actually works really well.<br>

![naive-qa-demo](./assets/demo-1.gif)

### 2. OpenAI Assistant API
`git checkout test-open-ai-assistant`
This approach uses the OpenAI Assistant API with these added benefits:
- It will intelligently manage chat history context
- Most of the time it can directly give an answer, and then we can request it to explain itself and examine the SQL

![agent-qa-demo](./assets/demo-2.gif)

However, it still has some issues and bugs, which is why I did not use this as my main submission:
- I did not have time to refactor the assistant into its own class, so the generation code and UI code is co-mingled
- Sometimes for unknown reasons the Assistant will scramble the message chat history

### Aborted approaches
#### Langchain pipeline
`git checkout tags/v1.1 -b <branch_name>`
This will generate and run SQL query. It is quite successful (see MLFlow), which I suspect is because Chinook DB has been around for so long that GPT-3.5 probably have seen a lot of examples of queries on Chinook in its training data. But this does not generally ask clarification questions very well.

#### Griptape agent
Tried this agent-oriented library based on some Reddit recommendations but it never made it past the initial prototype stage. The agent keeps getting stuck on hallucinated table names.

## Further improvements / TODOs
1. Evaluate the OpenAI agent approach on the whole dataset.
2. The naive approaches worked really well, so I did not do too much prompt tuning. But I suspected that this is basically because many Chinook queries have been included in OpenAI's training data. It would be interesting to test on a more obscure dataset.
3. The project in general is quite coupled with OpenAI's models.
   1. This is mainly because many existing libraries like `langchain` and `mlflow` (evaluators) have pre-built components that are integrated with OpenAI.
   2. However, for real life, it might be good to create more custom components that are able to plug into other foundational models
4. I would have built a Docker image to more easily run the interactive app. I have something going but Poetry doesn't like me.

## License

This project is licensed under the [MIT License](LICENSE).