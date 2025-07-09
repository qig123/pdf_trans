# C: Numbered Examples

## **C**

## **Numbered Examples**

**Chapter 1: Introduction**

1.1
GCD program in x86 machine language
5
1.2
GCD program in x86 assembler
5

The Art of Language Design

The Programming Language Spectrum

1.3
Classiﬁcation of programming languages
11
1.4
GCD function in C
13
1.5
GCD function in OCaml
13
1.6
GCD rules in Prolog
13

Why Study Programming Languages?

Compilation and Interpretation

1.7
Pure compilation
17
1.8
Pure interpretation
17
1.9
Mixing compilation and interpretation
18
1.10
Preprocessing
19
1.11
Library routines and linking
19
1.12
Post-compilation assembly
20
1.13
The C preprocessor
20
1.14
Source-to-source translation
20
1.15
Bootstrapping
21
1.16
Compiling interpreted languages
23
1.17
Dynamic and just-in-time compilation
23
1.18
Microcode (ﬁrmware)
24

Programming Environments

An Overview of Compilation

1.19
Phases of compilation and interpretation
26
1.20
GCD program in C
28
1.21
GCD program tokens
28
1.22
Context-free grammar and parsing
28
1.23
GCD program parse tree
29
1.24
GCD program abstract syntax tree
33

1.25
Interpreting the syntax tree
33
1.26
GCD program assembly code
34
1.27
GCD program optimization
36

**Chapter 2: Programming Language Syntax**

2.1
Syntax of Arabic numerals
43

Specifying Syntax: Regular Expressions and Context-Free
Grammars

```
2.2
Lexical structure of C11
45
2.3
Syntax of numeric constants
46
2.4
Syntactic nesting in expressions
48
2.5
Extended BNF (EBNF)
49
2.6
Derivation of slope * x + intercept
50
2.7
Parse trees for slope * x + intercept
51
2.8
Expression grammar with precedence
and associativity
52
```

Scanning

```
2.9
Tokens for a calculator language
54
2.10
An ad hoc scanner for calculator tokens
54
2.11
Finite automaton for a calculator scanner
55
2.12
Constructing an NFA for a given regular
expression
58
2.13
NFA for d*( .d | d. ) d*
59
2.14
DFA for d*( .d | d. ) d*
60
2.15
Minimal DFA for d*( .d | d. ) d*
60
2.16
Nested case statement automaton
62
2.17
The nontrivial preﬁx problem
64
2.18
Look-ahead in Fortran scanning
64
2.19
Table-driven scanning
65
```

Parsing

2.20
Top-down and bottom-up parsing
70
2.21
Bounding space with a bottom-up
grammar
72

The Memory Hierarchy

5.1
Memory hierarchy stats
C*·*61

Data Representation

5.2
Big- and little-endian
C*·*63
5.3
Hexadecimal numbers
C*·*65
5.4
Two’s complement
C*·*66
5.5
Overﬂow in two’s complement addition
C*·*66
5.6
Biased exponents
C*·*68
5.7
IEEE ﬂoating-point
C*·*68

Instruction Set Architecture (ISA)

```
5.8
An if statement in x86 assembler
C·72
5.9
Compare and test instructions
C·73
5.10
Conditional move
C·73
```

