class Student(object):
    def __init__(self, name = 'Lee', age = 20, score = 'a'):
        self.name = name
        self.age = age
        self.score = score
        self.__dict__ = {
            'name': self.name,
            'age': self.age,
            'score': self.score
        }
    
def student2dict(obj):
    return {
        'name': obj.name,
        'age': obj.age,
        'score': obj.score
    }