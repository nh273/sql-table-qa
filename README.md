# Project Name

## Installation

1. Install Python 3.11.9 using pyenv:
    ```shell
    pyenv install 3.11.9
    ```

2. Set Python 3.11.9 as the global version:
    ```shell
    pyenv local 3.11.9
    ```

3. Install dependencies using poetry:
    ```shell
    poetry install
    ```

## Usage

1. Run the interactive chat interface (Streamlit app):
    ```shell
    poetry run streamlit run app/app.py
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

## Approaches

## Further improvements

## License

This project is licensed under the [MIT License](LICENSE).