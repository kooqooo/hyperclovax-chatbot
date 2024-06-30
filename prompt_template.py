from typing import List, Tuple, Union

class Prompt:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def __repr__(self):
        return f"Message(role='{self.role}', content='{self.content}')"

    def render(self, context):
        return self.content.format(**context)
    
class Prompts:
    def __init__(self):
        self.messages = []

    def validate_role(self, role: str):
        assert role in ["system", "user", "assistant"], "Role must be 'system', 'user', or 'assistant'"

    def add_message(self, role: str, content: str):
        self.validate_role(role)
        self.messages.append(Prompt(role, content))

    def add_messages(self, messages: Union[List[Union[List, Tuple]], Tuple[Union[List, Tuple]]]):
        for message in messages:
            self.validate_role(message[0])
            self.messages.append(Prompt(message[0], message[1]))

    @classmethod
    def from_message(cls, message: Union[List, Tuple]):
        instance = cls()
        instance.add_message(message[0], message[1])
        return instance

    @classmethod
    def from_messages(cls, messages: Union[List[Union[List, Tuple]], Tuple[Union[List, Tuple]]]):
        instance = cls()
        for message in messages:
            instance.add_message(message[0], message[1])
        return instance

    def render(self, context: dict):
        for message in self.messages:
            message.content = message.render(context)
    
    def to_dict(self) -> List[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in self.messages]
    
    def __add__(self, other):
        self.messages.extend(other.messages)
        return self

    def __repr__(self):
        return f"MessageList(messages={self.messages})"

    def __str__(self):
        return str(self.to_dict())


if __name__ == "__main__":
    # Example usage
    messages = Prompts.from_messages(
        [
            ("system", "You are a helpful assistant"),
            ("user", "Tell me a joke about {topic}")
        ]
    )
    other_messages = Prompts.from_messages(
        [
            ("system", "더하기 연산자 테스트"),
            ("user", "이게 보인다면 성공입니다."),
            ("assistant", "__add__ 메서드를 사용했습니다.")
        ]
    )
    messages += other_messages

    messages.add_message("system", "add_mesage 테스트")
    messages.add_messages(
        [
            ("user", "add_messages 테스트"),
            ("assistant", "add_messages 테스트2")
        ]
    )
    messages.render({"topic": "cats"})

    def pretty_print(messages: List[dict[str, str]]):
        role_width = max(len(message["role"]) for message in messages) + 2
        content_width = max(len(message["content"]) for message in messages) + 2
        for message in messages:
            print(message["role"].ljust(role_width) + message["content"].ljust(content_width))

    pretty_print(messages.to_dict())