# Chapter 6: Control Flow

## **6**

## **Control Flow**

**Having considered the mechanisms that a compiler uses** to enforce se-
mantic rules (Chapter 4) and the characteristics of the target machines for which
compilers must generate code (Chapter 5), we now return to core issues in lan-
guage design. Speciﬁcally, we turn in this chapter to the issue of* control ﬂow* or
*ordering* in program execution. Ordering is fundamental to most models of com-
puting. It determines what should be done ﬁrst, what second, and so forth, to
accomplish some desired task. We can organize the language mechanisms used to
specify ordering into several categories:

```
1. Sequencing: Statements are to be executed (or expressions evaluated) in a cer-
tain speciﬁed order—usually the order in which they appear in the program
text.
2. Selection: Depending on some run-time condition, a choice is to be made
among two or more statements or expressions. The most common selection
constructs are if and case (switch) statements. Selection is also sometimes
referred to as alternation.
3. Iteration: A given fragment of code is to be executed repeatedly, either a cer-
tain number of times, or until a certain run-time condition is true. Iteration
constructs include for/do, while, and repeat loops.
4. Procedural abstraction: A potentially complex collection of control constructs
(a subroutine) is encapsulated in a way that allows it to be treated as a single
unit, usually subject to parameterization.
5. Recursion: An expression is deﬁned in terms of (simpler versions of) itself, ei-
ther directly or indirectly; the computational model requires a stack on which
to save information about partially evaluated instances of the expression. Re-
cursion is usually deﬁned by means of self-referential subroutines.
6. Concurrency: Two or more program fragments are to be executed/evaluated
“at the same time,” either in parallel on separate processors, or interleaved on
a single processor in a way that achieves the same effect.
7. Exception handling and speculation: A program fragment is executed optimisti-
cally, on the assumption that some expected condition will be true. If that con-
```

**223**

Operators are typically simpler, taking only one or two arguments, and dispensing
**EXAMPLE** 6.2

Typical operators
with the parentheses and commas:

```
a + b
- c
```

```
As we saw in Section 3.5.2, some languages deﬁne their operators as syntactic
sugar for more “normal”-looking functions. In Ada, for example, a + b is short
for "+"(a, b); in C++, a + b is short for a.operator+(b) or operator+(a,
b) (whichever is deﬁned).
■
In general, a language may specify that function calls (operator invocations)
employ preﬁx, inﬁx, or postﬁx notation.
These terms indicate, respectively,
whether the function name appears before, among, or after its several arguments:
```

preﬁx:
*op* a b
or
*op* (a, b)
or
(*op* a b)
inﬁx:
a* op* b
postﬁx:
a b* op*

Most imperative languages use inﬁx notation for binary operators and preﬁx
notation for unary operators and (with parentheses around the arguments) other
functions. Lisp uses preﬁx notation for all functions, but with the third of the
**EXAMPLE** 6.3

Cambridge Polish (preﬁx)
notation
variants above: in what is known as* Cambridge Polish*1 notation, it places the
function name* inside* the parentheses:

```
(* (+ 1 3) 2)
; that would be (1 + 3) * 2 in infix
(append a b c my_list)
■
```

ML-family languages dispense with the parentheses altogether, except when
**EXAMPLE** 6.4

Juxtaposition in ML
they are required for disambiguation:

```
max (2 + 3) 4;;
=⇒5
■
```

**1**
Preﬁx notation was popularized by Polish logicians of the early 20th century; Lisp-like parenthe-
sized syntax was ﬁrst employed (for noncomputational purposes) by philosopher W. V. Quine of
Harvard University (Cambridge, MA).

or

**2**
Most authors use the term “inﬁx” only for binary operators. Multiword operators may be called
“mixﬁx,” or left unnamed.

```
, (sequencing)
```


![Figure 6.1 Operator precedence...](images/page_261_vector_480.png)
*Figure 6.1 Operator precedence levels in Fortran, Pascal, C, and Ada. The operators at the top of the ﬁgure group most tightly.*

```
4**(3**2); the language syntax does not allow the unparenthesized form. In
languages that allow assignments inside expressions (an option we will consider
more in Section 6.1.2), assignment associates right-to-left. Thus in C, a = b =
a + c assigns a + c into b and then assigns the same value into a.
■
Haskell is unusual in allowing the programmer to specify both the associativity
EXAMPLE 6.11
```

```
User-deﬁned precedence
and associativity in Haskell
and the precedence of user-deﬁned operators. The predeﬁned ^ operator, for ex-
```

