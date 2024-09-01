#mclex
#Lexer for MiniC++ language
#Nicolas Vega and Miguel Cano

import sly
from rich import print

class Lexer(sly.Lexer):
    #Tokens List

    tokens = {
        #Keywords
        VOID, BOOL, INT, FLOAT, IF, ELSE, WHILE,
        RETURN, CONTINUE, SIZE, NEW, CLASS, PRINTF,
        THIS, SUPER, PRIVATE, PUBLIC,

        #Operators
        AND, OR, NOT,
        EQ, NE, GE, GT, LE, LT,

        #Literals
        INTLIT, FLOATLIT, BOOLIT, STRINGLIT, IDENT,
    }

    #Simbols and simple literals
    literals = '+-*/%=().,;{}[]<>!'

    #Ignore spaces and tabs
    ignore = ' \t'

    #Ignore comments of one line
    @_(r'//.*')
    def ignore_comment(self, t):
        pass

    #Ignore comments of multiple lines
    @_(r'/\*(.|\n)*?\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    #Ignore jump lines and count lines

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

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
    IDENT['continue'] = CONTINUE
    IDENT['size'] = SIZE
    IDENT['new'] = NEW
    IDENT['class'] = CLASS
    IDENT['printf'] = PRINTF
    IDENT['this'] = THIS
    IDENT['super'] = SUPER
    IDENT['private'] = PRIVATE
    IDENT['public'] = PUBLIC

    @_(r'\d+')
    def INTLIT(self, t):
        t.value = int(t.value)
        return t

    @_(r'\d+\.\d+')
    def FLOATLIT(self, t):
        t.value = float(t.value)
        return t

    @_(r'true|false')
    def BOOLIT(self, t):
        t.value = True if t.value == 'true' else False
        return t

    @_(r'"([^\\"]|\\.)*"')
    def STRINGLIT(self, t):
        t.value = t.value[1:-1] #Remove quotes
        return t

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

    def error(self, t):
        print(f'Error: Illegal character {t.value[0]}')
        self.index += 1

def print_tokens():
    l = Lexer()
    d = '''
    void main(void) {
        // Esto es un comentario
        int i = 12;
        float pi = 3.1415;
        if (i == 12) {
            printf("Hola clase\n");
        }
        
        while (i < 20) {
            printf("i = %d\n", i);
            i = i++;
        }
        
        return 0;
    }
'''

    for tok in l.tokenize(d):
        print(tok)

if __name__ == '__main__':
    print_tokens()



