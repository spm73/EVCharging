class CPId:
    def __init__(self):
        self.id = ''
        
    def set_id(self, id: str):
        self.id = id
        
    def get_id(self) -> str:
        return self.id
    
    def has_id(self) -> bool:
        return bool(self.id)