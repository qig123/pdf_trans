# Chapter 4: Semantic Analysis

## **4**

## **Semantic Analysis**

```
In Chapter 2 we considered the topic of programming language syntax.
In the current chapter we turn to the topic of semantics. Informally, syntax con-
cerns the form of a valid program, while semantics concerns its meaning. Meaning
is important for at least two reasons: it allows us to enforce rules (e.g., type con-
sistency) that go beyond mere form, and it provides the information we need in
order to generate an equivalent output program.
It is conventional to say that the syntax of a language is precisely that portion
of the language deﬁnition that can be described conveniently by a context-free
grammar, while the semantics is that portion of the deﬁnition that cannot. This
convention is useful in practice, though it does not always agree with intuition.
When we require, for example, that the number of arguments contained in a call
to a subroutine match the number of formal parameters in the subroutine deﬁni-
tion, it is tempting to say that this requirement is a matter of syntax. After all, we
can count arguments without knowing what they mean. Unfortunately, we can-
not count them with context-free rules. Similarly, while it is possible to write a
context-free grammar in which every function must contain at least one return
statement, the required complexity makes this strategy very unattractive. In gen-
eral, any rule that requires the compiler to compare things that are separated by
long distances, or to count things that are not properly nested, ends up being a
matter of semantics.
Semantic rules are further divided into static and dynamic semantics, though
again the line between the two is somewhat fuzzy. The compiler enforces static
semantic rules at compile time. It generates code to enforce dynamic semantic
rules at run time (or to call library routines that do so). Certain errors, such as
division by zero, or attempting to index into an array with an out-of-bounds sub-
script, cannot in general be caught at compile time, since they may occur only for
certain input values, or certain behaviors of arbitrarily complex code. In special
cases, a compiler may be able to tell that a certain error will always or never occur,
regardless of run-time input. In these cases, the compiler can generate an error
message at compile time, or refrain from generating code to perform the check at
run time, as appropriate. Basic results from computability theory, however, tell
us that no algorithm can make these predictions correctly for arbitrary programs:
```

**179**

Programming languages vary dramatically in their choice of semantic rules. Lisp
dialects, for example, allow “mixed-mode” arithmetic on arbitrary numeric types,
which they will automatically promote from integer to rational to ﬂoating-point
or “bignum” (extended) precision, as required to maintain precision. Ada, by
contract, assigns a speciﬁc type to every numeric variable, and requires the pro-
grammer to convert among these explicitly when combining them in expressions.

Assertions in Java
is a statement that a speciﬁed condition is expected to be true when execution
reaches a certain point in the code. In Java one can write

**DESIGN & IMPLEMENTATION**

```
4.1 Dynamic semantic checks
In the past, language theorists and researchers in programming methodology
and software engineering tended to argue for more extensive semantic checks,
while “real-world” programmers “voted with their feet” for languages like C
and Fortran, which omitted those checks in the interest of execution speed. As
computers have become more powerful, and as companies have come to ap-
preciate the enormous costs of software maintenance, the “real-world” camp
has become much more sympathetic to checking. Languages like Ada and Java
have been designed from the outset with safety in mind, and languages like C
and C++ have evolved (to the extent possible) toward increasingly strict deﬁ-
nitions. In scripting languages, where many semantic checks are deferred until
run time in order to avoid the need for explicit types and variable declarations,
there has been a similar trend toward stricter rules. Perl, for example (one of
the older scripting languages), will typically attempt to infer a possible mean-
ing for expressions (e.g., 3 + "four") that newer languages (e.g., Python or
Ruby) will ﬂag as run-time errors.
```

```
1
Among other things, C. A. R. Hoare (1934–) invented the quicksort algorithm and the case
statement, contributed to the design of Algol W, and was one of the leaders in the development
of axiomatic semantics. In the area of concurrent programming, he reﬁned and formalized the
monitor construct (to be described in Section 13.4.1), and designed the CSP programming model
and notation. He received the ACM Turing Award in 1980.
```

**Static Analysis**

In general, compile-time algorithms that predict run-time behavior are known
as* static analysis*. Such analysis is said to be* precise* if it allows the compiler to
determine whether a given program will always follow the rules. Type checking,
for example, is static and precise in languages like Ada and ML: the compiler
ensures that no variable will ever be used at run time in a way that is inappropriate
for its type. By contrast, languages like Lisp, Smalltalk, Python, and Ruby obtain
greater ﬂexibility, while remaining completely type-safe, by accepting the run-
time overhead of dynamic type checks. (We will cover type checking in more
detail in Chapter 7.)
Static analysis can also be useful when it isn’t precise. Compilers will often
check what they can at compile time and then generate code to check the rest
dynamically. In Java, for example, type checking is mostly static, but dynamically
loaded classes and type casts may require run-time checks. In a similar vein, many

This grammar will generate all properly formed constant expressions over the
basic arithmetic operators, but it says nothing about their meaning. To tie these
expressions to mathematical concepts (as opposed to, say, ﬂoor tile patterns or
dance steps), we need additional notation. The most common is based on* at-*
*tributes*. In our expression grammar, we can associate a val attribute with each
**EXAMPLE** 4.4

```
Bottom-up AG for
constant expressions
E, T, F, and const in the grammar. The intent is that for any symbol S, S.val
will be the meaning, as an arithmetic value, of the token string derived from S.
We assume that the val of a const is provided to us by the scanner. We must
then invent a set of rules for each production, to specify how the vals of different
symbols are related. The resulting attribute grammar (AG) is shown in Figure 4.1.
In this simple grammar, every production has a single rule. We shall see more
complicated grammars later, in which productions can have several rules. The
rules come in two forms. Those in productions 3, 6, 8, and 9 are known as copy
rules; they specify that one attribute should be a copy of another. The other rules
invoke semantic functions (sum, quotient, additive inverse, etc.). In this exam-
ple, the semantic functions are all familiar arithmetic operations. In general, they
can be arbitrarily complex functions speciﬁed by the language designer. Each se-
mantic function takes an arbitrary number of arguments (each of which must be
an attribute of a symbol in the current production—no global variables are al-
lowed), and each computes a single result, which must likewise be assigned into
an attribute of a symbol in the current production. When more than one sym-
bol of a production has the same name, subscripts are used to distinguish them.
These subscripts are solely for the beneﬁt of the semantic functions; they are not
part of the context-free grammar itself.
■
In a strict deﬁnition of attribute grammars, copy rules and semantic function
calls are the only two kinds of permissible rules. In our examples we use a 
symbol to introduce each code fragment corresponding to a single rule. In prac-
tice, it is common to allow rules to consist of small fragments of code in some
well-deﬁned notation (e.g., the language in which a compiler is being written),
so that simple semantic functions can be written out “in-line.” In this relaxed
notation, the rule for the ﬁrst production in Figure 4.1 might be simply E1.val :=
E2.val + T.val. As another example, suppose we wanted to count the elements of a
EXAMPLE 4.5
```

Top-down AG to count the
elements of a list
comma-separated list:

for an identiﬁer, a reference to information about it in the symbol table
for an expression, its type
for a statement or expression, a reference to corresponding code in the com-
piler’s intermediate form
for almost any construct, an indication of the ﬁle name, line, and column
where the corresponding source code begins
for any internal node, a list of semantic errors found in the subtree below

For purposes other than translation—e.g., in a theorem prover or machine-
independent language deﬁnition—attributes might be drawn from the disciplines
of* denotational*,* operational*, or* axiomatic* semantics. Interested readers can ﬁnd
references in the Bibliographic Notes at the end of the chapter.

const

+

4

4

1

1

1

1

3

3

3

2

2


![Figure 4.2 Decoration of...](images/page_220_vector_351.png)
*Figure 4.2 Decoration of a parse tree for (1 + 3) * 2, using the attribute grammar of Figure 4.1. The val attributes of symbols are shown in boxes. Curving arrows show the attribute ﬂow, which is strictly upward in this case. Each box holds the output of a single semantic rule; the arrow(s) entering the box indicate the input(s) to the rule. At the second level of the tree, for example, the two arrows pointing into the box with the 8 represent application of the rule T1.val := product(T2.val, F.val). 4.3 Evaluating Attributes*

```
The process of evaluating attributes is called annotation or decoration of the parse
tree. Figure 4.2 shows how to decorate the parse tree for the expression (1 + 3)
EXAMPLE 4.6
```

```
Decoration of a parse tree
* 2, using the AG of Figure 4.1. Once decoration is complete, the value of the
overall expression can be found in the val attribute of the root of the tree.
■
```

**Synthesized Attributes**

The attribute grammar of Figure 4.1 is very simple. Each symbol has at most one
attribute (the punctuation marks have none). Moreover, they are all so-called
*synthesized attributes*: their values are calculated (synthesized) only in produc-
tions in which their symbol appears on the left-hand side. For annotated parse
trees like the one in Figure 4.2, this means that the* attribute ﬂow*—the pattern in
which information moves from node to node—is entirely bottom-up.

*TT*

*E*

*FT*

*F*

const

*FT*

*TT*
+

*ϵ*
*ϵ*

*ϵ*

*ϵ*

*ϵ*


![Figure 4.4 Decoration of...](images/page_224_vector_339.png)
*Figure 4.4 Decoration of a top-down parse tree for (1 + 3) * 2, using the AG of Figure 4.3. Curving arrows again indicate attribute ﬂow; the arrow(s) entering a given box represent the application of a single semantic rule. Flow in this case is no longer strictly bottom-up, but it is still left-to-right. At FT and TT nodes, the left box holds the st attribute; the right holds val.*

on itself. (A grammar can be circular and still be well deﬁned if attributes are
guaranteed to converge to a unique value.) As a general rule, practical attribute
grammars tend to be noncircular.
An algorithm that decorates parse trees by invoking the rules of an attribute
grammar in an order consistent with the tree’s attribute ﬂow is called a* translation*
*scheme*. Perhaps the simplest scheme is one that makes repeated passes over a
tree, invoking any semantic function whose arguments have all been deﬁned, and
stopping when it completes a pass in which no values change. Such a scheme is
said to be* oblivious*, in the sense that it exploits no special knowledge of either the
parse tree or the grammar. It will halt only if the grammar is well deﬁned. Better
performance, at least for noncircular grammars, may be achieved by a* dynamic*
scheme that tailors the evaluation order to the structure of a given parse tree—for
example, by constructing a topological sort of the attribute ﬂow graph and then
invoking rules in an order consistent with the sort.
The fastest translation schemes, however, tend to be* static*—based on an analy-
sis of the structure of the attribute grammar itself, and then applied mechanically
to any tree arising from the grammar. Like LL and LR parsers, linear-time static
translation schemes can be devised only for certain restricted classes of gram-

+

+


![Figure 4.8 Construction of...](images/page_230_vector_515.png)
*Figure 4.8 Construction of a syntax tree via decoration of a top-down parse tree, using the grammar of Figure 4.6. In the top diagram, (a), the value of the constant 1 has been placed in a new syntax tree leaf. A pointer to this leaf then propagates to the st attribute of TT. In (b), a second leaf has been created to hold the constant 3. Pointers to the two leaves then become child pointers of a new internal + node, a pointer to which propagates from the st attribute of the bottom-most TT, where it was created, all the way up and over to the st attribute of the top-most FT. In (c), a third leaf has been created for the constant 2. Pointers to this leaf and to the + node then become the children of a new × node, a pointer to which propagates from the st of the lower FT, where it was created, all the way to the root of the tree.*

