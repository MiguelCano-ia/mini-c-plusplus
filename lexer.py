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
        VOID, BOOL, INT, FLOAT, STRING , IF, ELSE, WHILE,
        RETURN, CONTINUE, SIZE, NEW, CLASS, PRINTF,
        THIS, SUPER, PRIVATE, PUBLIC, BREAK, TRUE, FALSE,
        FOR,

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

    @_(r'/\*([^*]|\*+[^*/])*\*+/')
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
    IDENT['true'] = TRUE
    IDENT['false'] = FALSE
    IDENT['string'] = STRING
    IDENT['for'] = FOR

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