# 距離フェーズ
import distance

class Template:
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
        pass
    
    def function1(self):
        print(self.b)
        pass

def main():
    template = Template(1, 2)
    print(template.a)
    template.function1()

if __name__ == "__main__":
    main()
    pass
