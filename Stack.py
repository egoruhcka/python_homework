from typing import Any

class StackIsEmpty(Exception):
    pass

class Stack:
    def __init__(self):
        self.__stack = []

    @property
    def items(self) -> list:
        return self.__stack
    
    def push(self, value: Any) -> None:
        self.__stack.append(value)

    def pop(self) -> Any:
        if not self.__stack:
            raise StackIsEmpty

        res = self.__stack[-1]
        del self.__stack[-1]
        return res
    
    def __len__(self) -> int:
        return len(self.__stack)
    
    def __str__(self) -> str:
        elem = ", ".join(map(str, self.__stack))
        return f"Stack({elem})"
    
    def __repr__(self) -> str:
        elem = ", ".join(map(repr, self.__stack))
        return f"Stack([{elem}])"
    
    def __iter__(self) -> Any:
        for i in self.__stack:
            yield i
    
    def __contains__(self, value: Any) -> bool:
        return value in self.__stack
    
    def __getitem__(self, index: int) -> Any:
        return self.__stack[index]
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__stack.clear()
        return False
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Stack):
            return NotImplemented
        return self.items == other.items
        
