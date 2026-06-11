import os

class FileHandler:
    def __init__(self, filename: str):
        self.filename = filename


    def readFileLines(self) -> list:
        if not self.exists():
            return []
        
        with open(self.filename, 'r', encoding='utf-8') as file:
            return [linea.rstrip('\n') for linea in file]
        
    def write(self, content: str) -> None:
        with open(self.filename, 'w', encoding='utf-8') as file:
            file.write(content)

    def writeList(self, lines: list) -> None:
        content = '\n'.join(lines)
        self.write(content)

    def exists(self) -> bool:
        return os.path.exists(self.filename)

    def delete(self) -> None:
        if self.exists():
            os.remove(self.filename)