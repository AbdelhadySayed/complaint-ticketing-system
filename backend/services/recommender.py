from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from services.vector import retriever


model = OllamaLLM(model="llama3.2")

template = """
You are a customer ticket support AI Assistant and your job is only to instruct users on how to solve their problems.
this is not a chat but only a reply.
ensure the customer that there will be an employee replying to him as well soon.

Here are some relevant problems and how to handle them: {problems}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def chat_with_model(question: str):

    
    problems = retriever.invoke(question)
    result = chain.invoke({"problems": problems, "question": question})
    print(result)
    return result