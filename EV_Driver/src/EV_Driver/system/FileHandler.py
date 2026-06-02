
class FileHandler:
    def __init__(self, filename: str):
        self.filename = filename


    def readFileLines(self) -> list:
        with open(self.filename, 'r', encoding='utf-8') as file:
            # Usamos una list comprehension para limpiar el '\n' de cada línea
            return [linea.rstrip('\n') for linea in file]
        
    def write(self, content: str) -> None:
        with open(self.filename, 'w', encoding='utf-8') as file:
            file.write(content)

    def writeList(self, lines: list) -> None:
        content = '\n'.join(lines)
        self.write(content)