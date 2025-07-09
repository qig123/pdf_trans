# A.2 Utility Functions

A

## Appendix

A.1 Interpreters

We provide interpreters for each of the source languages LInt, LVar, … in the files interp-Lint.rkt, interp-Lvar.rkt, and so on. The interpreters for the inter- mediate languages CVar and CIf are in interp-Cvar.rkt and interp-C1.rkt. The interpreters for CTup, CFun, pseudo-x86, and x86 are in the interp.rkt file.

A.2 Utility Functions

The utility functions described in this section are in the utilities.rkt file of the support code.

interp-tests This function runs the compiler passes and the interpreters on each of the specified tests to check whether each pass is correct. The interp-tests function has the following parameters:

name (a string) A name to identify the compiler. typechecker A function of exactly one argument that either raises an error using the error function when it encounters a type error, or returns #f when it encounters a type error. If there is no type error, the type checker returns the program. passes A list with one entry per pass. An entry is a list consisting of four things:

* a string giving the name of the pass;
* the function that implements the pass (a translator from AST to AST);
* a function that implements the interpreter (a function from AST to result
  value) for the output language; and,
* a type checker for the output language. Type checkers for all the L and C
  languages are provided in the support code. For example, the type checkers
  for LVar and CVar are in type-check-Lvar.rkt and type-check-Cvar.rkt.
  The type checker entry is optional. The support code does not provide type
  checkers for the x86 languages.
  source-interp An interpreter for the source language. The interpreters from
  appendix A.1 make a good choice.
  test-family (a string) For example, "var" or "cond".

