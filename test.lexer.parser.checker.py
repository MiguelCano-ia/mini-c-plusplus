import io
import sys
from lexer import *
from parser import *
from myAST import *
from rich import print
from mchecker import *
from mdot import *
import os
from myInterpreter import *

def select_script():
    try:
        # Lista de directorios disponibles
        directories = ['scripts', 'errors']
        print("Available directories:")
        for i, directory in enumerate(directories, start=1):
            print(f"{i}. {directory}")
        print("Select a directory:")
        dir_choice = int(input())
        if dir_choice > 0 and dir_choice <= len(directories):
            selected_dir = directories[dir_choice - 1]
            dir_path = f'./{selected_dir}'
        else:
            print("[red]Invalid directory option.")
            return None

        # Verificar si el directorio existe
        if not os.path.exists(dir_path):
            print(f"[red] Directory {dir_path} not found.")
            return None

        files = os.listdir(dir_path)
        if not files:
            print("No files found in the selected directory.")
            return None
        else:
            print(f"Available scripts in '{selected_dir}':")
            for i, file in enumerate(files, start=1):
                print(f"{i}. {file}")
            print("Select a script to parse:")
            script_choice = int(input())
            if script_choice > 0 and script_choice <= len(files):
                with open(f"{dir_path}/{files[script_choice - 1]}", 'r') as f:
                    data = f.read()
                return data
            else:
                print("[red]Invalid script option.")
                return None
    except FileNotFoundError:
        print(f"[red] Directory {dir_path} not found.")
        return None
    except Exception as e:
        print(f"[red] Error: {e}")
        return None

def tryParser():
    data = select_script()
    if data:
        lexer = Lexer()
        parser = Parser()
        tokens = lexer.tokenize(data)
        
        print("Tokens:")
        for token in tokens:
            print(token) 
            
        tokens = lexer.tokenize(data)
        ast = parser.parse(tokens)
        
        print("\nAST:")
        print(ast)
        
        dot = MakeDot()
        for expr in ast.stmts:
            expr.accept(dot)
        dot.generate_dot()
        dot.generate_dot_png()
        
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        
        if analyzer.errors:
            for error in analyzer.errors:
                print(error)
        else:
            print("Análisis semántico completado sin errores.")
            print("Executing program...")
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            try:
                interpreterContext = {}
                interpreter = Interpreter(interpreterContext,analyzer)
                interpreter.interpret(ast)
                sys.stdout = sys.__stdout__
                outputContent = output_buffer.getvalue()
                print(f'Execution output:')
                print(f"{outputContent}")
                return outputContent
            except Exception as e:
              sys.stdout = sys.__stdout__
              print(f"[red]Error: {e}")
              return None
            finally:
              output_buffer.close()
    else:
        print("[red]No script selected or an error occurred.")

if __name__ == "__main__":
    tryParser()
