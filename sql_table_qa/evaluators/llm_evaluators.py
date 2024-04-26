from mlflow.metrics.genai import answer_correctness, answer_relevance

EVAL_MODEL = "openai:/gpt-3.5-turbo-0125"
openai_correctness_evaluator = answer_correctness(
    model=EVAL_MODEL
)
openai_relevance_evaluator = answer_relevance(
    model=EVAL_MODEL
)
