""" Author: @kooqooo
[Reference]
- https://api.python.langchain.com/en/latest/prompts/langchain_core.prompts.prompt.PromptTemplate.html#langchain_core.prompts.prompt.PromptTemplate
- https://python.langchain.com/v0.2/docs/concepts/#prompt-templates
"""


from pprint import pprint
from pyprnt import prnt
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")
print(type(prompt_template))
prnt(prompt_template.dict())

result = prompt_template.invoke({"topic": "cats"})
print(type(result))
prnt(result.dict())

print("="*80)

from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "Tell me a joke about {topic}")
])
print(type(prompt_template))
prnt(prompt_template.dict())

result = prompt_template.invoke({"topic": "cats"})
print(type(result))
prnt(result.dict())
