import unittest
from lexer import Lexer

class TestMiniCLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_keywords(self):
        result = list(self.lexer.tokenize('int float if else while return'))
        tokens = [token.type for token in result]
        expected = ['INT', 'FLOAT', 'IF', 'ELSE', 'WHILE', 'RETURN']
        self.assertEqual(tokens, expected)

    def test_identifiers(self):
        result = list(self.lexer.tokenize('variable1 variable2 _variable'))
        tokens = [token.type for token in result]
        expected = ['IDENT', 'IDENT', 'IDENT']
        self.assertEqual(tokens, expected)

    def test_operators(self):
        result = list(self.lexer.tokenize('== != && || < > <= >='))
        tokens = [token.type for token in result]
        expected = ['EQ', 'NE', 'AND', 'OR', 'LT', 'GT', 'LE', 'GE']
        self.assertEqual(tokens, expected)

    def test_literals(self):
        result = list(self.lexer.tokenize('123 3.14 true false "hello"'))
        tokens = [token.type for token in result]
        expected = ['INTLIT', 'FLOATLIT', 'BOOLIT', 'BOOLIT', 'STRINGLIT']
        self.assertEqual(tokens, expected)

    def test_class_declaration(self):
        code = '''
        class Persona {
            int edad;
            float altura;
            string nombre;
        };
        '''
        result = list(self.lexer.tokenize(code))
        tokens = [token.type for token in result if token.type]
        expected = ['CLASS', 'IDENT', '{', 'INT', 'IDENT', ';', 'FLOAT', 'IDENT', ';', 'IDENT', 'IDENT', ';', '}', ';']
        self.assertEqual(tokens, expected)

    def test_while_if_declaration(self):
        code = '''
            int edad = 0;
            int limite = 110;
            
            while (edad < limite) {
                if (edad % 2 == 0) {
                    edad++;
                    continue;
                }
        
                if (edad >= 100) {
                    break;
                }
        
                edad++;
            }
        '''
        expected_tokens = [
            'INT', 'IDENT', '=', 'INTLIT', ';',
            'INT', 'IDENT', '=', 'INTLIT', ';',
            'WHILE', '(', 'IDENT', 'LT', 'IDENT', ')', '{',
            'IF', '(', 'IDENT', '%', 'INTLIT', 'EQ', 'INTLIT', ')', '{',
            'IDENT', 'INCREMENT', ';',
            'CONTINUE', ';',
            '}',
            'IF', '(', 'IDENT', 'GE', 'INTLIT', ')', '{',
            'BREAK', ';',
            '}',
            'IDENT', 'INCREMENT', ';',
            '}'
        ]

        result = list(self.lexer.tokenize(code))
        tokens = [token.type if token.type else token.value for token in result]
        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    unittest.main()
