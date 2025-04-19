from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate



model = OllamaLLM(model="llama3.2")

template = """
You will be provided with a user's question and a set of relevant problems and their answers. Your job is to find the answer associated with the most relevant problem and provide that answer *verbatim* to the user. Do not generate any additional text or explanations.

Here are the relevant problems and their answers: {problems}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def chat_with_model(question: str):
    from services.vector import retriever
    problems = retriever.invoke(question)
    print(problems)
    result = chain.invoke({"problems": problems, "question": question})
    return result