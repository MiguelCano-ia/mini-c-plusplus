from mcontext import Context
from rich import print
from mdot import MakeDot
from tabulate import tabulate
from mchecker import *

"""
    print("optional arguments:")
    print("-h, --help             show this help message and exit")
    print("-l, --lex              Store output of lexer")
    print("-a, --AST              Display AST")
    print("-D, --dot              Generate AST graph as DOT format")
    print("-p, --png              Generate AST graph as png format")
    print("--sym                  Dump the symbol table") #the Checker one
    print("-R, --exec             Execute the generated program")
"""
def menu():
    print("\t\t\t\n ################################ Miguel Cano and Nicolas Vega MiniC++ Compiler ################################  \n")
    print("usage: mc.py [-h] [-l] [-a] [-D] [-p] [--sym] [-R] input\n")

    print("Compiler for MiniC++ programs\n")

    print("positional arguments:")
    print("input MiniC++            program file to compile\n")

    print("optional arguments:")
    print("-h, --help             show this help message and exit")
    print("-l, --lex              display tokens from lexer")
    print("-a, --AST              Display AST")
    print("-D, --dot              Generate AST graph as DOT format")
    print("-p, --png              Generate AST graph as png format")
    print("--sym                  Dump the symbol table")
    print("-R, --exec             Execute the generated program")

def main(argv):
    if len(argv) == 2:
        menu()
        raise SystemExit()

    print("\t\t\t\n ################################ Miguel Cano and Nicolas Vega MiniC++ Compiler ################################  \n")
    ctxt = Context()
    if len(argv) > 2:
        source = ""
        with open(argv[2]) as file:
            source = file.read()
        ctxt.parse(source)
        if not ctxt.have_errors:
            if argv[1] in ["-h","--help"]:
                menu()
                #raise SystemExit()
            elif argv[1] in ["-l","--lex"]:
                print("\n\n\t\t********** TOKENS ********** \n\n")
                tokens = ctxt.lexer.tokenize(source)
                table=[["Type","Value","At line"]]
                for tok in tokens:
                    row=[]
                    row.append(tok.type)
                    row.append(tok.value)
                    row.append(tok.lineno)
                    table.append(row)
                print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
            elif argv[1] in ["-a","--AST"]:
                print("\n\n\t\t********** AST ********** \n\n")
                print(ctxt.ast)
            elif argv[1] in ["-D","--dot"]:
                print("\n\n DOT LANGUAGE \n")
                dot = MakeDot()
                for expr in ctxt.ast.stmts:
                    expr.accept(dot)
                dot.generate_dot()
                print(dot)
            elif argv[1] in ["-p","--png"]:
                print("\n\n PNG FILE CREATED \n")
                dot = MakeDot()
                for expr in ctxt.ast.stmts:
                    expr.accept(dot)
                dot.generate_dot_png()
            elif argv[1] in ["--sym"]:
                print("\n\n\t\t********** Tabla de Símbolos ********** \n")
                ctxt.check()
                if not ctxt.have_errors:
                    for scope_info in ctxt.symtab:
                        print(f"Scope ({scope_info.type}): {scope_info.name}")
                        table = []
                        for var_name, var_info in scope_info.symbols.items():
                            if isinstance(var_info, dict) and var_info.get('kind') == 'constructor':
                                params = ', '.join([param.var_type for param in var_info['params']])
                                constructor_signature = f"constructor ({params})"
                                table.append([var_name, constructor_signature])
                            elif isinstance(var_info, dict):
                                var_type = var_info['type']
                                table.append([var_name, var_type])
                            elif isinstance(var_info, str):
                                var_type = var_info
                                table.append([var_name, var_type])
                            elif isinstance(var_info, FuncDecl):
                                params = ', '.join([param.var_type for param in var_info.params])
                                return_type = var_info.return_type
                                func_signature = f"function ({params}) -> {return_type}"
                                table.append([var_name, func_signature])
                            elif isinstance(var_info, ClassDecl):
                                super_class = var_info.super_class if var_info.super_class else 'None'
                                class_info = f"class (super: {super_class})"
                                table.append([var_name, class_info])
                            else:
                                table.append([var_name, str(type(var_info))])
                        if table:
                            print(tabulate(table, headers=["Nombre", "Tipo"], tablefmt="fancy_grid"))
                        else:
                            print("(Sin símbolos en este scope)")
                else:
                    print("No se pudo generar la tabla de símbolos debido a errores en el análisis.")


            elif argv[1] in ["-R", "--exec"]:
                print("\n CHECKER + INTERPRETER \n")
                ctxt.run()
            else:
                print("Not defined action")
                op = int(input("Do you need help? 1:yes/2:no :: "))
                if op == 1:
                    menu()
    else:
        try:
            while True:
                source = input("mc > ") #This one works for very simple one line stuff, but the environments of neither Checker or Interpret work properly.
                ctxt.parse(source)
                if ctxt.have_errors: continue
                for stmt in ctxt.ast.decl:
                    ctxt.ast = stmt
                    ctxt.run()

        except EOFError:
            pass

if __name__ == "__main__":
    from sys import argv
    main(argv)