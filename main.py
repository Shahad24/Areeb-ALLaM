from fastapi import FastAPI, Request
from general_question import run_interactive_story, eval_yes_no_question, critical_thinking_general, eval_critical_thinking_general
from fastapi.responses import StreamingResponse
import asyncio
from science_question import run_interactive_science_stroy, eval_first_question, generate_keywords_from_story, critical_thinking_science, eval_critical_thinking_science


# =========================================================================================================


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# =========================================================================================================


@app.get("/general_question")
async def general_question(child_name: str, child_age: int, selected_story: int):
    #return run_interactive_story(child_name, child_age, selected_story)
    return StreamingResponse(run_interactive_story(child_name, child_age, selected_story), media_type="text/event-stream")


@app.get("/general_eval_first_question")
async def general_eval_first_question(child_name: str, child_age: int, story: str, child_response: str, question: str):
    #return run_interactive_story(child_name, child_age, selected_story)
    #return eval_yes_no_question(child_age, story, child_response, question)
    return StreamingResponse(eval_yes_no_question(child_name, child_age, story, child_response, question), media_type="text/event-stream")


@app.get("/general_eval_third_question")
async def general_eval_third_question(child_name: str, child_age: int, story: str, generated_problem: str, child_answer: str):
    #return run_interactive_story(child_name, child_age, selected_story)
    return StreamingResponse(eval_critical_thinking_general(child_name, child_age, story, generated_problem, child_answer), media_type="text/event-stream")


@app.get("/general_critical_thinking")
def general_critical_thinking(child_name: str, child_age: int, story: str):

    return critical_thinking_general(child_name, child_age, story)

# =========================================================================================================


@app.get("/science_third_level_evaluation_response")
async def science_eval_first_question(child_name: str, child_age: int, generated_problem: str, child_answer: str):
    #return run_interactive_story(child_name, child_age, selected_story)
    return StreamingResponse(eval_critical_thinking_science(child_name, child_age, generated_problem, child_answer), media_type="text/event-stream")


@app.get("/critical_thinking_science")
def science_critical_thinking(child_name: str, child_age: int, story: str):

    return critical_thinking_science(child_name, child_age, story)


@app.get("/generate_keywords_from_story")
def generate_keyword(story: str, child_name: str):
    #return run_interactive_story(child_name, child_age, selected_story)
    return generate_keywords_from_story(story, child_name)


@app.get("/science_eval_first_question")
async def science_eval_first_question(child_name: str, child_age: int, question: str, retrieved_text: str, child_answer: str):
    #return run_interactive_story(child_name, child_age, selected_story)
    #return eval_first_question(child_name, child_age, question, retrieved_text, child_answer)
    return StreamingResponse(eval_first_question(child_name, child_age, question, retrieved_text, child_answer), media_type="text/event-stream")


@app.get("/science_question")
async def science_question(child_name: str, child_age: int, selected_story: int):
    #return run_interactive_story(child_name, child_age, selected_story)
    return StreamingResponse(run_interactive_science_stroy(child_name, child_age, selected_story), media_type="text/event-stream")

# =========================================================================================================

