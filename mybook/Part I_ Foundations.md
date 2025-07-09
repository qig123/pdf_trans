# Part I: Foundations

## **I**

## **Foundations**

A central premise of* Programming Language Pragmatics* is that language design and implemen-
tation are intimately connected; it’s hard to study one without the other.
The bulk of the text—Parts II and III—is organized around topics in language design,
but with detailed coverage throughout of the many ways in which design decisions have been
shaped by implementation concerns.
The ﬁrst ﬁve chapters—Part I—set the stage by covering foundational material in both
design and implementation. Chapter 1 motivates the study of programming languages, in-
troduces the major language families, and provides an overview of the compilation process.
Chapter 3 covers the high-level structure of programs, with an emphasis on* names*, the* bind-*
*ing* of names to objects, and the* scope rules* that govern which bindings are active at any given
time. In the process it touches on storage management; subroutines, modules, and classes;
polymorphism; and separate compilation.
Chapters 2, 4, and 5 are more implementation oriented. They provide the background
needed to understand the implementation issues mentioned in Parts II and III. Chapter 2
discusses the* syntax*, or textual structure, of programs. It introduces* regular expressions* and
*context-free grammars*, which designers use to describe program syntax, together with the* scan-*
*ning* and* parsing* algorithms that a compiler or interpreter uses to recognize that syntax. Given
an understanding of syntax, Chapter 4 explains how a compiler (or interpreter) determines
the* semantics*, or meaning of a program. The discussion is organized around the notion of* at-*
*tribute grammars*, which serve to map a program onto something else that has meaning, such
as mathematics or some other existing language. Finally, Chapter 5 (entirely on the companion
site) provides an overview of assembly-level computer architecture, focusing on the features of
modern microprocessors most relevant to compilers. Programmers who understand these fea-
tures have a better chance not only of understanding why the languages they use were designed
the way they were, but also of using those languages as fully and effectively as possible.

This page intentionally left blank

```
55 89 e5 53
83 ec 04 83
e4 f0 e8 31
00 00 00 89
c3 e8 2a 00
00 00 39 c3
74 10 8d b6
00 00 00 00
39 c3 7e 13
29 c3 39 c3
75 f6 89 1c
24 e8 6e 00
00 00 8b 5d
fc c9 c3 29
d8 eb eb 90
■
```

### As people began to write larger programs, it quickly became apparent that a

### less error-prone notation was required. Assembly languages were invented to al-

### low operations to be expressed with mnemonic abbreviations. Our GCD program

**EXAMPLE** 1.2
GCD program in x86
assembler
### looks like this in x86 assembly language:

```
pushl
%ebp
movl
%esp, %ebp
pushl
%ebx
subl
$4, %esp
andl
$-16, %esp
call
getint
movl
%eax, %ebx
call
getint
cmpl
%eax, %ebx
je
C
A:
cmpl
%eax, %ebx
```

```
jle
D
subl
%eax, %ebx
B:
cmpl
%eax, %ebx
jne
A
C:
movl
%ebx, (%esp)
call
putint
movl
-4(%ebp), %ebx
leave
ret
D:
subl
%ebx, %eax
jmp
B
■
```

### **5**

```
The proposition gcd(a, b, g) is true if (1) a, b, and g are all equal; (2) a is greater
than b and there exists a number c such that c is a - b and gcd(c, b, g) is true; or
(3) a is less than b and there exists a number c such that c is b - a and gcd(c, a,
g) is true. To compute the gcd of a given pair of numbers, search for a number g (and
various numbers c) for which these rules allow one to prove that gcd(a, b, g) is true.
```

```
A Prolog version of this algorithm appears at the bottom of Figure 1.2. It may be
easier to understand if one reads “if” for :- and “and” for commas.
■
It should be emphasized that the distinctions among language families are not
clear-cut. The division between the von Neumann and object-oriented languages,
for example, is often very fuzzy, and many scripting languages are also object-
oriented. Most of the functional and logic languages include some imperative
features, and several recent imperative languages have added functional features.
The descriptions above are meant to capture the general ﬂavor of the families,
without providing formal deﬁnitions.
Imperative languages—von Neumann and object-oriented—receive the bulk
of the attention in this book. Many issues cut across family lines, however, and
the interested reader will discover much that is applicable to alternative compu-
tational models in most chapters of the book. Chapters 11 through 14 contain
additional material on functional, logic, concurrent, and scripting languages.
```

Output

Unlike a compiler, an interpreter stays around for the execution of the appli-
cation. In fact, the interpreter is the locus of control during that execution. In
effect, the interpreter implements a virtual machine whose “machine language”
is the high-level programming language. The interpreter reads statements in that
language more or less one at a time, executing them as it goes along.
■
In general, interpretation leads to greater ﬂexibility and better diagnostics (er-
ror messages) than does compilation. Because the source code is being executed
directly, the interpreter can include an excellent source-level debugger. It can also
cope with languages in which fundamental characteristics of the program, such as
the sizes and types of variables, or even which names refer to which variables, can
depend on the input data. Some language features are almost impossible to im-
plement without interpretation: in Lisp and Prolog, for example, a program can
write new pieces of itself and execute them on the ﬂy. (Several scripting languages
also provide this capability.) Delaying decisions about program implementation
until run time is known as* late binding*; we will discuss it at greater length in
Section 3.1.

Assembly language

Source program

Compiler

■

A surprising number of compilers generate output in some high-level
**EXAMPLE** 1.14

Source-to-source
translation
language—commonly C or some simpliﬁed version of the input language.
Such* source-to-source* translation is particularly common in research languages
and during the early stages of language development. One famous example was
AT&T’s original compiler for C++. This was indeed a true compiler, though
it generated C instead of assembler: it performed a complete analysis of the
syntax and semantics of the C++ source program, and with very few excep-

Token stream

Parse tree

Abstract syntax tree or
other intermediate form

Scanner (lexical analysis)

Program input

Program output

Parser (syntax analysis)

Semantic analysis and
intermediate code generation

Tree-walk routines

Symbol table

Front
end


![Figure 1.4 Phases of...](images/page_60_vector_505.png)
*Figure 1.4 Phases of interpretation. The front end is essentially the same as that of a compiler. The ﬁnal phase “executes” the intermediate form, typically using a set of mutually recursive subroutines that walk the syntax tree.*

for more than one machine (target language), and so that the back end may be
shared by compilers for more than one source language. In some implementa-
tions the front end and the back end may be separated by a “middle end” that
is responsible for language- and machine-independent code improvement. Prior

}
{
*block-item-list_opt*

*block-item-list*

*function-definition*

*translation-unit*

int

int

*declaration-specifiers_opt*

*direct-declarator*

*declarator*

*block-item*

*block-item*

*declaration-specifiers_opt*

*declaration*

*compound-statement*

ident(main)

ident(i)

1

*postfix-expression*
13

### **A**

### **B**

1

)
(
*postfix-expression*

*argument-expression-list_opt*
1
ident(getint)

ident(j)
*postfix-expression*
13

)
(
*postfix-expression*

*argument-expression-list_opt*
1
ident(getint)

*id_list_tail*

*id_list_tail*

*id_list_tail*

id

, id

;

*id_list*
*id_list_tail*

*id_list_tail*

*id_list_tail*

*id_list_tail*


![Figure 2.14 Top-down (left)...](images/page_104_vector_502.png)
*Figure 2.14 Top-down (left) and bottom-up parsing (right) of the input string A, B, C;. Grammar appears at lower left.*

```
to peek at the upcoming token (a comma), which allows it to choose between the
two possible expansions for id list tail. It then matches the comma and the id
and moves down into the next id list tail. In a similar, recursive fashion, the top-
down parser works down the tree, left-to-right, predicting and expanding nodes
and tracing out a left-most derivation of the fringe of the tree.
```

