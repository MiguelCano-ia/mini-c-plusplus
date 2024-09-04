#mclex
#Lexer for MiniC++ language
#Nicolas Vega and Miguel Cano

import os
import sly
from rich import print

class Lexer(sly.Lexer):
    #Tokens List
    tokens = {
        #Keywords
        VOID, BOOL, INT, FLOAT, IF, ELSE, WHILE,
        RETURN, CONTINUE, SIZE, NEW, CLASS, PRINTF,
        THIS, SUPER, PRIVATE, PUBLIC, BREAK,

        #Operators
        AND, OR, NOT,
        EQ, NE, GE, GT, LE, LT,
        INCREMENT, DECREMENT,

        #Literals
        INTLIT, FLOATLIT, BOOLIT, STRINGLIT, IDENT,
    }

    #Simbols and simple literals
    literals = '+-*/%=().,:;{}[]<>!'

    #Ignore spaces and tabs
    ignore = ' \t'

    # Ignore jump lines and count lines
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # Ignore comments
    @_(r'//.*\n')
    def ignore_cppcomment(self, t):
        self.lineno += 1

    @_(r'/\*(.|\n)*\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\d+\.\d+')
    def FLOATLIT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INTLIT(self, t):
        t.value = int(t.value)
        return t

    @_(r'true|false')
    def BOOLIT(self, t):
        t.value = True if t.value == 'true' else False
        return t

    @_(r'"([^\\"]|\\.)*"')
    def STRINGLIT(self, t):
        t.value = t.value[1:-1]  # Remove quotes
        return t

    #Define tokens
    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENT['void'] = VOID
    IDENT['bool'] = BOOL
    IDENT['int'] = INT
    IDENT['float'] = FLOAT
    IDENT['if'] = IF
    IDENT['else'] = ELSE
    IDENT['while'] = WHILE
    IDENT['return'] = RETURN
    IDENT['break'] = BREAK
    IDENT['continue'] = CONTINUE
    IDENT['size'] = SIZE
    IDENT['new'] = NEW
    IDENT['class'] = CLASS
    IDENT['printf'] = PRINTF
    IDENT['this'] = THIS
    IDENT['super'] = SUPER
    IDENT['private'] = PRIVATE
    IDENT['public'] = PUBLIC

    #Relational Operators
    EQ = r'=='
    NE = r'!='
    GE = r'>='
    GT = r'>'
    LE = r'<='
    LT = r'<'
    AND = r'&&'
    OR = r'\|\|'
    NOT = r'!'
    INCREMENT = r'\+\+'
    DECREMENT = r'\-\-'

    def error(self, t):
        print(f'Error: Illegal character {t.value[0]}')
        self.index += 1

def list_scripts(path = 'scripts'):
    scripts = []
    for file in os.listdir(path):
        if file.endswith('.cpp'):
            scripts.append(file)
    return scripts

def test_script(lexer, name, path = 'scripts'):
    script_path = os.path.join(path, name)
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            script = f.read()
            print(f'Running script {name}')
            for tok in lexer.tokenize(script):
                print(tok)
            print('\n')
    else:
        print(f'Script {name} not found')

if __name__ == '__main__':
    lexer = Lexer()
    scripts = list_scripts()

    if not scripts:
        print("No C++ scripts found in the 'scripts' directory.")
    else:
        print('Aviable scripts:')
        for i,script in enumerate(scripts,1):
            print(f"{i}. {script}")
        print('\n')

        choice = input(f"Select a script to test (1-{len(scripts)}): ")

        if choice.isdigit():
            choice = int(choice)
            if choice > 0 and choice <= len(scripts):
                test_script(lexer, scripts[choice-1])
            else:
                print("Invalid choice")





