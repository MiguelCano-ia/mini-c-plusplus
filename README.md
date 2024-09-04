# MiniC++ Lexer

## Descripción

Este proyecto es un lexer para un subconjunto del lenguaje C++, llamado MiniC++, desarrollado por Nicolás Vega y Miguel Cano. El lexer está escrito en Python utilizando la librería `sly` y se encarga de analizar y tokenizar el código fuente escrito en MiniC++.

## Características

- **Soporte de palabras clave**: Reconoce palabras clave como `void`, `int`, `float`, `if`, `else`, `while`, `return`, `class`, `public`, `private`, `new`, entre otras.
- **Soporte de operadores**: Identifica operadores relacionales (`==`, `!=`, `>=`, `<=`, `>`, `<`), lógicos (`&&`, `||`, `!`), y de incremento y decremento (`++`, `--`).
- **Literales**: Tokeniza literales enteros, flotantes, booleanos y cadenas de texto.
- **Identificadores**: Reconoce identificadores de variables y funciones.
- **Comentarios**: Ignora comentarios de una línea (`// ...`) y de múltiples líneas (`/* ... */`).
- **Soporte para pruebas unitarias**: Permite ejecutar scripts de prueba en C++ para validar el comportamiento del lexer.

## Estructura del Proyecto

- **`lexer.py`**: Contiene la implementación principal del lexer.
- **`scripts/`**: Carpeta donde se almacenan los scripts de prueba en C++.
- **`test_lexer.py`**: Script para ejecutar las pruebas unitarias del lexer utilizando los scripts de la carpeta `scripts`.

## Requisitos

- **Python 3.6 o superior**
- **Librería `sly`**: Se utiliza para la implementación del lexer.
- **Librería `rich`**: Se utiliza para la impresión formateada en la terminal.

## Instalación

1. Clona este repositorio en tu máquina local.
   ```bash
   git clone https://github.com/usuario/minicpp-lexer.git

2. Navega al directorio del proyecto