# Chapter 4: Semantic Analysis

4 Semantic Analysis

In Chapter 2 we considered the topic of programming language syntax. In the current chapter we turn to the topic of semantics. Informally, syntax con- cerns the form of a valid program, while semantics concerns its meaning. Meaning is important for at least two reasons: it allows us to enforce rules (e.g., type con- sistency) that go beyond mere form, and it provides the information we need in order to generate an equivalent output program. It is conventional to say that the syntax of a language is precisely that portion of the language deﬁnition that can be described conveniently by a context-free grammar, while the semantics is that portion of the deﬁnition that cannot. This convention is useful in practice, though it does not always agree with intuition. When we require, for example, that the number of arguments contained in a call to a subroutine match the number of formal parameters in the subroutine deﬁni- tion, it is tempting to say that this requirement is a matter of syntax. After all, we can count arguments without knowing what they mean. Unfortunately, we can- not count them with context-free rules. Similarly, while it is possible to write a context-free grammar in which every function must contain at least one return statement, the required complexity makes this strategy very unattractive. In gen- eral, any rule that requires the compiler to compare things that are separated by long distances, or to count things that are not properly nested, ends up being a matter of semantics. Semantic rules are further divided into static and dynamic semantics, though again the line between the two is somewhat fuzzy. The compiler enforces static semantic rules at compile time. It generates code to enforce dynamic semantic rules at run time (or to call library routines that do so). Certain errors, such as division by zero, or attempting to index into an array with an out-of-bounds sub- script, cannot in general be caught at compile time, since they may occur only for certain input values, or certain behaviors of arbitrarily complex code. In special cases, a compiler may be able to tell that a certain error will always or never occur, regardless of run-time input. In these cases, the compiler can generate an error message at compile time, or refrain from generating code to perform the check at run time, as appropriate. Basic results from computability theory, however, tell us that no algorithm can make these predictions correctly for arbitrary programs:

there will inevitably be cases in which an error will always occur, but the compiler cannot tell, and must delay the error message until run time; there will also be cases in which an error can never occur, but the compiler cannot tell, and must incur the cost of unnecessary run-time checks. Both semantic analysis and intermediate code generation can be described in terms of annotation, or decoration of a parse tree or syntax tree. The annotations themselves are known as attributes. Numerous examples of static and dynamic semantic rules will appear in subsequent chapters. In this current chapter we focus primarily on the mechanisms a compiler uses to enforce the static rules. We will consider intermediate code generation (including the generation of code for dynamic semantic checks) in Chapter 15. In Section 4.1 we consider the role of the semantic analyzer in more detail, considering both the rules it needs to enforce and its relationship to other phases of compilation. Most of the rest of the chapter is then devoted to the subject of attribute grammars. Attribute grammars provide a formal framework for the decoration of a tree. This framework is a useful conceptual tool even in compilers that do not build a parse tree or syntax tree as an explicit data structure. We introduce the notion of an attribute grammar in Section 4.2. We then consider various ways in which such grammars can be applied in practice. Section 4.3 discusses the issue of attribute ﬂow, which constrains the order(s) in which nodes of a tree can be decorated. In practice, most compilers require decoration of the parse tree (or the evaluation of attributes that would reside in a parse tree if there were one) to occur in the process of an LL or LR parse. Section 4.4 presents action routines as an ad hoc mechanism for such “on-the-ﬂy” evaluation. In Section 4.5 (mostly on the companion site) we consider the management of space for parse tree attributes. Because they have to reﬂect the structure of the CFG, parse trees tend to be very complicated (recall the example in Figure 1.5). Once parsing is complete, we typically want to replace the parse tree with a syntax tree that reﬂects the input program in a more straightforward way (Figure 1.6). One particularly common compiler organization uses action routines during parsing solely for the purpose of constructing the syntax tree. The syntax tree is then decorated during a sepa- rate traversal, which can be formalized, if desired, with a separate attribute gram- mar. We consider the decoration of syntax trees in Section 4.6.

## 4.1 The Role of the Semantic Analyzer

Programming languages vary dramatically in their choice of semantic rules. Lisp dialects, for example, allow “mixed-mode” arithmetic on arbitrary numeric types, which they will automatically promote from integer to rational to ﬂoating-point or “bignum” (extended) precision, as required to maintain precision. Ada, by contract, assigns a speciﬁc type to every numeric variable, and requires the pro- grammer to convert among these explicitly when combining them in expressions.

Languages also vary in the extent to which they require their implementations to perform dynamic checks. At one extreme, C requires no checks at all, beyond those that come “free” with the hardware (e.g., division by zero, or attempted access to memory outside the bounds of the program). At the other extreme, Java takes great pains to check as many rules as possible, in part to ensure that an untrusted program cannot do anything to damage the memory or ﬁles of the machine on which it runs. The role of the semantic analyzer is to enforce all static semantic rules and to annotate the program with information needed by the in- termediate code generator. This information includes both clariﬁcations (this is ﬂoating-point addition, not integer; this is a reference to the global variable x) and requirements for dynamic semantic checks. In the typical compiler, analysis and intermediate code generation mark the end of front end computation. The exact division of labor between the front end and the back end, however, may vary from compiler to compiler: it can be hard to say exactly where analysis (ﬁguring out what the program means) ends and synthesis (expressing that meaning in some new form) begins (and as noted in Section 1.6 there may be a “middle end” in between). Many compilers also carry a program through more than one intermediate form. In one common orga- nization, described in more detail in Chapter 15, the semantic analyzer creates an annotated syntax tree, which the intermediate code generator then translates into a linear form reminiscent of the assembly language for some idealized ma- chine. After machine-independent code improvement, this linear form is then translated into yet another form, patterned more closely on the assembly lan- guage of the target machine. That form may undergo machine-speciﬁc code improvement. Compilers also vary in the extent to which semantic analysis and intermedi- ate code generation are interleaved with parsing. With fully separated phases, the parser passes a full parse tree on to the semantic analyzer, which converts it to a syntax tree, ﬁlls in the symbol table, performs semantic checks, and passes it on to the code generator. With fully interleaved phases, there may be no need to build either the parse tree or the syntax tree in its entirety: the parser can call semantic check and code generation routines on the ﬂy as it parses each expres- sion, statement, or subroutine of the source. We will focus on an organization in which construction of the syntax tree is interleaved with parsing (and the parse tree is not built), but semantic analysis occurs during a separate traversal of the syntax tree.

Dynamic Checks

Many compilers that generate code for dynamic checks provide the option of dis- abling them if desired. It is customary in some organizations to enable dynamic checks during program development and testing, and then disable them for pro- duction use, to increase execution speed. The wisdom of this practice is ques-

tionable: Tony Hoare, one of the key ﬁgures in programming language design,1 has likened the programmer who disables semantic checks to a sailing enthusiast who wears a life jacket when training on dry land, but removes it when going to sea [Hoa89, p. 198]. Errors may be less likely in production use than they are in testing, but the consequences of an undetected error are signiﬁcantly worse. Moreover, on modern processors it is often possible for dynamic checks to exe- cute in pipeline slots that would otherwise go unused, making them virtually free. On the other hand, some dynamic checks (e.g., ensuring that pointer arithmetic in C remains within the bounds of an array) are sufﬁciently expensive that they are rarely implemented.

Assertions

When reasoning about the correctness of their algorithms (or when formally proving properties of programs via axiomatic semantics) programmers fre- quently write logical assertions regarding the values of program data. Some pro- gramming languages make these assertions a part of the language syntax. The compiler then generates code to check the assertions at run time. An assertion EXAMPLE 4.1

Assertions in Java is a statement that a speciﬁed condition is expected to be true when execution reaches a certain point in the code. In Java one can write

DESIGN & IMPLEMENTATION

4.1 Dynamic semantic checks In the past, language theorists and researchers in programming methodology and software engineering tended to argue for more extensive semantic checks, while “real-world” programmers “voted with their feet” for languages like C and Fortran, which omitted those checks in the interest of execution speed. As computers have become more powerful, and as companies have come to ap- preciate the enormous costs of software maintenance, the “real-world” camp has become much more sympathetic to checking. Languages like Ada and Java have been designed from the outset with safety in mind, and languages like C and C++ have evolved (to the extent possible) toward increasingly strict deﬁ- nitions. In scripting languages, where many semantic checks are deferred until run time in order to avoid the need for explicit types and variable declarations, there has been a similar trend toward stricter rules. Perl, for example (one of the older scripting languages), will typically attempt to infer a possible mean- ing for expressions (e.g., 3 + "four") that newer languages (e.g., Python or Ruby) will ﬂag as run-time errors.

1 Among other things, C. A. R. Hoare (1934–) invented the quicksort algorithm and the case statement, contributed to the design of Algol W, and was one of the leaders in the development of axiomatic semantics. In the area of concurrent programming, he reﬁned and formalized the monitor construct (to be described in Section 13.4.1), and designed the CSP programming model and notation. He received the ACM Turing Award in 1980.

assert denominator != 0;

An AssertionError exception will be thrown if the semantic check fails at run time. ■ Some languages (e.g., Euclid, Eiffel, and Ada 2012) also provide explicit sup- port for invariants, preconditions, and postconditions. These are essentially struc- tured assertions. An invariant is expected to be true at all “clean points” of a given body of code. In Eiffel, the programmer can specify an invariant on the data in- side a class: the invariant will be checked, automatically, at the beginning and end of each of the class’s methods (subroutines). Similar invariants for loops are expected to be true before and after every iteration. Pre- and postconditions are expected to be true at the beginning and end of subroutines, respectively. In Eu- clid, a postcondition, speciﬁed once in the header of a subroutine, will be checked not only at the end of the subroutine’s text, but at every return statement as well. Many languages support assertions via standard library routines or macros. In EXAMPLE 4.2

Assertions in C C, for example, one can write

assert(denominator != 0);

If the assertion fails, the program will terminate abruptly with the message

myprog.c:42: failed assertion `denominator != 0'

The C manual requires assert to be implemented as a macro (or built into the compiler) so that it has access to the textual representation of its argument, and to the ﬁle name and line number on which the call appears. ■ Assertions, of course, could be used to cover the other three sorts of checks, but not as clearly or succinctly. Invariants, preconditions, and postconditions are a prominent part of the header of the code to which they apply, and can cover a potentially large number of places where an assertion would otherwise be re- quired. Euclid and Eiffel implementations allow the programmer to disable as- sertions and related constructs when desired, to eliminate their run-time cost.

Static Analysis

In general, compile-time algorithms that predict run-time behavior are known as static analysis. Such analysis is said to be precise if it allows the compiler to determine whether a given program will always follow the rules. Type checking, for example, is static and precise in languages like Ada and ML: the compiler ensures that no variable will ever be used at run time in a way that is inappropriate for its type. By contrast, languages like Lisp, Smalltalk, Python, and Ruby obtain greater ﬂexibility, while remaining completely type-safe, by accepting the run- time overhead of dynamic type checks. (We will cover type checking in more detail in Chapter 7.) Static analysis can also be useful when it isn’t precise. Compilers will often check what they can at compile time and then generate code to check the rest dynamically. In Java, for example, type checking is mostly static, but dynamically loaded classes and type casts may require run-time checks. In a similar vein, many

compilers perform extensive static analysis in an attempt to eliminate the need for dynamic checks on array subscripts, variant record tags, or potentially dangling pointers (to be discussed in Chapter 8). If we think of the omission of unnecessary dynamic checks as a performance optimization, it is natural to look for other ways in which static analysis may enable code improvement. We will consider this topic in more detail in Chap- ter 17. Examples include alias analysis, which determines when values can be safely cached in registers, computed “out of order,” or accessed by concurrent threads; escape analysis, which determines when all references to a value will be conﬁned to a given context, allowing the value to be allocated on the stack in- stead of the heap, or to be accessed without locks; and subtype analysis, which determines when a variable in an object-oriented language is guaranteed to have a certain subtype, so that its methods can be called without dynamic dispatch. An optimization is said to be unsafe if it may lead to incorrect code in certain programs. It is said to be speculative if it usually improves performance, but may degrade it in certain cases. A compiler is said to be conservative if it applies op- timizations only when it can guarantee that they will be both safe and effective. By contrast, an optimistic compiler may make liberal use of speculative optimiza- tions. It may also pursue unsafe optimizations by generating two versions of the code, with a dynamic check that chooses between them based on information not available at compile time. Examples of speculative optimization include nonbind- ing prefetches, which try to bring data into the cache before they are needed, and trace scheduling, which rearranges code in hopes of improving the performance of the processor pipeline and the instruction cache. To eliminate dynamic checks, language designers may choose to tighten se- mantic rules, banning programs for which conservative analysis fails. The ML type system, for example (Section 7.2.4), avoids the dynamic type checks of Lisp, but disallows certain useful programming idioms that Lisp supports. Similarly, the deﬁnite assignment rules of Java and C# (Section 6.1.3) allow the compiler to ensure that a variable is always given a value before it is used in an expression, but disallow certain programs that are legal (and correct) in C.

## 4.2 Attribute Grammars

In Chapter 2 we learned how to use a context-free grammar to specify the syntax of a programming language. Here, for example, is an LR (bottom-up) grammar EXAMPLE 4.3

Bottom-up CFG for constant expressions for arithmetic expressions composed of constants, with precedence and associa- tivity:2

2 The addition of semantic rules tends to make attribute grammars quite a bit more verbose than context-free grammars. For the sake of brevity, many of the examples in this chapter use very short symbol names: E instead of expr, TT instead of term tail.

E −→E + T

E −→E - T

E −→T

T −→T * F

T −→T / F

T −→F

F −→- F

F −→( E )

F −→const ■

This grammar will generate all properly formed constant expressions over the basic arithmetic operators, but it says nothing about their meaning. To tie these expressions to mathematical concepts (as opposed to, say, ﬂoor tile patterns or dance steps), we need additional notation. The most common is based on at- tributes. In our expression grammar, we can associate a val attribute with each EXAMPLE 4.4

Bottom-up AG for constant expressions E, T, F, and const in the grammar. The intent is that for any symbol S, S.val will be the meaning, as an arithmetic value, of the token string derived from S. We assume that the val of a const is provided to us by the scanner. We must then invent a set of rules for each production, to specify how the vals of different symbols are related. The resulting attribute grammar (AG) is shown in Figure 4.1. In this simple grammar, every production has a single rule. We shall see more complicated grammars later, in which productions can have several rules. The rules come in two forms. Those in productions 3, 6, 8, and 9 are known as copy rules; they specify that one attribute should be a copy of another. The other rules invoke semantic functions (sum, quotient, additive inverse, etc.). In this exam- ple, the semantic functions are all familiar arithmetic operations. In general, they can be arbitrarily complex functions speciﬁed by the language designer. Each se- mantic function takes an arbitrary number of arguments (each of which must be an attribute of a symbol in the current production—no global variables are al- lowed), and each computes a single result, which must likewise be assigned into an attribute of a symbol in the current production. When more than one sym- bol of a production has the same name, subscripts are used to distinguish them. These subscripts are solely for the beneﬁt of the semantic functions; they are not part of the context-free grammar itself. ■ In a strict deﬁnition of attribute grammars, copy rules and semantic function calls are the only two kinds of permissible rules. In our examples we use a  symbol to introduce each code fragment corresponding to a single rule. In prac- tice, it is common to allow rules to consist of small fragments of code in some well-deﬁned notation (e.g., the language in which a compiler is being written), so that simple semantic functions can be written out “in-line.” In this relaxed notation, the rule for the ﬁrst production in Figure 4.1 might be simply E1.val := E2.val + T.val. As another example, suppose we wanted to count the elements of a EXAMPLE 4.5

![Figure 4.1 A simple...](images/page_219_vector_215.png)
*Figure 4.1 A simple attribute grammar for constant expressions, using the standard arith- metic operations. Each semantic rule is introduced by a  sign.*

L −→id LT  L.c := 1 + LT.c LT −→, L  LT.c := L.c LT −→ϵ  LT.c := 0

Here the rule on the ﬁrst production sets the c (count) attribute of the left-hand side to one more than the count of the tail of the right-hand side. Like explicit semantic functions, in-line rules are not allowed to refer to any variables or at- tributes outside the current production. We will relax this restriction when we introduce action routines in Section 4.4. ■ Neither the notation for semantic functions (whether in-line or explicit) nor the types of the attributes themselves is intrinsic to the notion of an attribute grammar. The purpose of the grammar is simply to associate meaning with the nodes of a parse tree or syntax tree. Toward that end, we can use any notation and types whose meanings are already well deﬁned. In Examples 4.4 and 4.5, we associated numeric values with the symbols in a CFG—and thus with parse tree nodes—using semantic functions drawn from ordinary arithmetic. In a compiler or interpreter for a full programming language, the attributes of tree nodes might include

for an identiﬁer, a reference to information about it in the symbol table for an expression, its type for a statement or expression, a reference to corresponding code in the com- piler’s intermediate form for almost any construct, an indication of the ﬁle name, line, and column where the corresponding source code begins for any internal node, a list of semantic errors found in the subtree below

For purposes other than translation—e.g., in a theorem prover or machine- independent language deﬁnition—attributes might be drawn from the disciplines of denotational, operational, or axiomatic semantics. Interested readers can ﬁnd references in the Bibliographic Notes at the end of the chapter.

![Figure 4.2 Decoration of...](images/page_220_vector_351.png)
*Figure 4.2 Decoration of a parse tree for (1 + 3) * 2, using the attribute grammar of Figure 4.1. The val attributes of symbols are shown in boxes. Curving arrows show the attribute ﬂow, which is strictly upward in this case. Each box holds the output of a single semantic rule; the arrow(s) entering the box indicate the input(s) to the rule. At the second level of the tree, for example, the two arrows pointing into the box with the 8 represent application of the rule T1.val := product(T2.val, F.val). 4.3 Evaluating Attributes*

The process of evaluating attributes is called annotation or decoration of the parse tree. Figure 4.2 shows how to decorate the parse tree for the expression (1 + 3) EXAMPLE 4.6

Decoration of a parse tree * 2, using the AG of Figure 4.1. Once decoration is complete, the value of the overall expression can be found in the val attribute of the root of the tree. ■

Synthesized Attributes

The attribute grammar of Figure 4.1 is very simple. Each symbol has at most one attribute (the punctuation marks have none). Moreover, they are all so-called synthesized attributes: their values are calculated (synthesized) only in produc- tions in which their symbol appears on the left-hand side. For annotated parse trees like the one in Figure 4.2, this means that the attribute ﬂow—the pattern in which information moves from node to node—is entirely bottom-up.

An attribute grammar in which all attributes are synthesized is said to be S- attributed. The arguments to semantic functions in an S-attributed grammar are always attributes of symbols on the right-hand side of the current production, and the return value is always placed into an attribute of the left-hand side of the pro- duction. Tokens (terminals) often have intrinsic properties (e.g., the character- string representation of an identiﬁer or the value of a numeric constant); in a compiler these are synthesized attributes initialized by the scanner.

Inherited Attributes

In general, we can imagine (and will in fact have need of) attributes whose values are calculated when their symbol is on the right-hand side of the current produc- tion. Such attributes are said to be inherited. They allow contextual information to ﬂow into a symbol from above or from the side, so that the rules of that produc- tion can be enforced in different ways (or generate different values) depending on surrounding context. Symbol table information is commonly passed from sym- bol to symbol by means of inherited attributes. Inherited attributes of the root of the parse tree can also be used to represent the external environment (character- istics of the target machine, command-line arguments to the compiler, etc.). As a simple example of inherited attributes, consider the following fragment EXAMPLE 4.7

Top-down CFG and parse tree for subtraction of an LL(1) expression grammar (here covering only subtraction):

expr −→const expr tail expr tail −→- const expr tail | ϵ

For the expression 9 - 4 - 3, we obtain the following parse tree:

expr

9

expr_tail

expr_tail -

4

-

3 expr_tail

ϵ

■

If we want to create an attribute grammar that accumulates the value of the overall expression into the root of the tree, we have a problem: because subtrac- tion is left associative, we cannot summarize the right subtree of the root with a single numeric value. If we want to decorate the tree bottom-up, with an S- attributed grammar, we must be prepared to describe an arbitrary number of right operands in the attributes of the top-most expr tail node (see Exercise 4.4). This is indeed possible, but it defeats the purpose of the formalism: in effect, it requires us to embed the entire tree into the attributes of a single node, and do all the real work inside a single semantic function.

If, however, we are allowed to pass attribute values not only bottom-up but EXAMPLE 4.8

Decoration with left-to-right attribute ﬂow also left-to-right in the tree, then we can pass the 9 into the top-most expr tail node, where it can be combined (in proper left-associative fashion) with the 4. The resulting 5 can then be passed into the middle expr tail node, combined with the 3 to make 2, and then passed upward to the root:

expr

2

const

9

expr_tail

9 2

expr_tail -

4 const

5 2

-

2 2 3 const expr_tail

ϵ

■

To effect this style of decoration, we need the following attribute rules: EXAMPLE 4.9

Top-down AG for subtraction expr −→const expr tail  expr tail.st := const.val  expr.val := expr tail.val

expr tail1 −→- const expr tail2  expr tail2.st := expr tail1.st −const.val  expr tail1.val := expr tail2.val

expr tail −→ϵ  expr tail.val := expr tail.st

In each of the ﬁrst two productions, the ﬁrst rule serves to copy the left context (value of the expression so far) into a “subtotal” (st) attribute; the second rule copies the ﬁnal value from the right-most leaf back up to the root. In the expr tail nodes of the picture in Example 4.8, the left box holds the st attribute; the right holds val. ■ We can ﬂesh out the grammar fragment of Example 4.7 to produce a more EXAMPLE 4.10

Top-down AG for constant expressions complete expression grammar, as shown (with shorter symbol names) in Fig- ure 4.3. The underlying CFG for this grammar accepts the same language as the one in Figure 4.1, but where that one was SLR(1), this one is LL(1). Attribute ﬂow for a parse of (1 + 3) * 2, using the LL(1) grammar, appears in Figure 4.4. As in the grammar fragment of Example 4.9, the value of the left operand of each oper- ator is carried into the TT and FT productions by the st (subtotal) attribute. The relative complexity of the attribute ﬂow arises from the fact that operators are left associative, but the grammar cannot be left recursive: the left and right operands of a given operator are thus found in separate productions. Grammars to perform

![Figure 4.3 An attribute...](images/page_223_vector_365.png)
*Figure 4.3 An attribute grammar for constant expressions based on an LL(1) CFG. In this grammar several productions have two semantic rules.*

semantic analysis for practical languages generally require some non-S-attributed ﬂow. ■

Attribute Flow

Just as a context-free grammar does not specify how it should be parsed, an at- tribute grammar does not specify the order in which attribute rules should be invoked. Put another way, both notations are declarative: they deﬁne a set of valid trees, but they don’t say how to build or decorate them. Among other things, this means that the order in which attribute rules are listed for a given production is immaterial; attribute ﬂow may require them to execute in any order. If, in Fig- ure 4.3, we were to reverse the order in which the rules appear in productions 1, 2, 3, 5, 6, and/or 7 (listing the rule for symbol.val ﬁrst), it would be a purely cosmetic change; the grammar would not be altered. We say an attribute grammar is well deﬁned if its rules determine a unique set of values for the attributes of every possible parse tree. An attribute grammar is noncircular if it never leads to a parse tree in which there are cycles in the attribute ﬂow graph—that is, if no attribute, in any parse tree, ever depends (transitively)

![Figure 4.4 Decoration of...](images/page_224_vector_339.png)
*Figure 4.4 Decoration of a top-down parse tree for (1 + 3) * 2, using the AG of Figure 4.3. Curving arrows again indicate attribute ﬂow; the arrow(s) entering a given box represent the application of a single semantic rule. Flow in this case is no longer strictly bottom-up, but it is still left-to-right. At FT and TT nodes, the left box holds the st attribute; the right holds val.*

on itself. (A grammar can be circular and still be well deﬁned if attributes are guaranteed to converge to a unique value.) As a general rule, practical attribute grammars tend to be noncircular. An algorithm that decorates parse trees by invoking the rules of an attribute grammar in an order consistent with the tree’s attribute ﬂow is called a translation scheme. Perhaps the simplest scheme is one that makes repeated passes over a tree, invoking any semantic function whose arguments have all been deﬁned, and stopping when it completes a pass in which no values change. Such a scheme is said to be oblivious, in the sense that it exploits no special knowledge of either the parse tree or the grammar. It will halt only if the grammar is well deﬁned. Better performance, at least for noncircular grammars, may be achieved by a dynamic scheme that tailors the evaluation order to the structure of a given parse tree—for example, by constructing a topological sort of the attribute ﬂow graph and then invoking rules in an order consistent with the sort. The fastest translation schemes, however, tend to be static—based on an analy- sis of the structure of the attribute grammar itself, and then applied mechanically to any tree arising from the grammar. Like LL and LR parsers, linear-time static translation schemes can be devised only for certain restricted classes of gram-

mars. S-attributed grammars, such as the one in Figure 4.1, form the simplest such class. Because attribute ﬂow in an S-attributed grammar is strictly bottom- up, attributes can be evaluated by visiting the nodes of the parse tree in exactly the same order that those nodes are generated by an LR-family parser. In fact, the attributes can be evaluated on the ﬂy during a bottom-up parse, thereby inter- leaving parsing and semantic analysis (attribute evaluation). The attribute grammar of Figure 4.3 is a good bit messier than that of Fig- ure 4.1, but it is still L-attributed: its attributes can be evaluated by visiting the nodes of the parse tree in a single left-to-right, depth-ﬁrst traversal (the same or- der in which they are visited during a top-down parse—see Figure 4.4). If we say that an attribute A.s depends on an attribute B.t if B.t is ever passed to a semantic function that returns a value for A.s, then we can deﬁne L-attributed grammars more formally with the following two rules: (1) each synthesized attribute of a left-hand-side symbol depends only on that symbol’s own inherited attributes or on attributes (synthesized or inherited) of the production’s right-hand-side sym- bols, and (2) each inherited attribute of a right-hand-side symbol depends only on inherited attributes of the left-hand-side symbol or on attributes (synthesized or inherited) of symbols to its left in the right-hand side. Because L-attributed grammars permit rules that initialize attributes of the left-hand side of a production using attributes of symbols on the right-hand side, every S-attributed grammar is also an L-attributed grammar. The reverse is not the case: S-attributed grammars do not permit the initialization of at- tributes on the right-hand side, so there are L-attributed grammars that are not S-attributed. S-attributed attribute grammars are the most general class of attribute gram- mars for which evaluation can be implemented on the ﬂy during an LR parse. L-attributed grammars are the most general class for which evaluation can be im- plemented on the ﬂy during an LL parse. If we interleave semantic analysis (and possibly intermediate code generation) with parsing, then a bottom-up parser must in general be paired with an S-attributed translation scheme; a top-down parser must be paired with an L-attributed translation scheme. (Depending on the structure of the grammar, it is often possible for a bottom-up parser to ac- commodate some non-S-attributed attribute ﬂow; we consider this possibility in Section C 4.5.1.) If we choose to separate parsing and semantic analysis into sepa- rate passes, then the code that builds the parse tree or syntax tree must still use an S-attributed or L-attributed translation scheme (as appropriate), but the semantic analyzer can use a more powerful scheme if desired. There are certain tasks, such as the generation of code for “short-circuit” Boolean expressions (to be discussed in Sections 6.1.5 and 6.4.1), that are easiest to accomplish with a non-L-attributed scheme.

One-Pass Compilers

A compiler that interleaves semantic analysis and code generation with parsing is said to be a one-pass compiler.3 It is unclear whether interleaving semantic analysis with parsing makes a compiler simpler or more complex; it’s mainly a matter of taste. If intermediate code generation is interleaved with parsing, one need not build a syntax tree at all (unless of course the syntax tree is the intermediate code). Moreover, it is often possible to write the intermediate code to an output ﬁle on the ﬂy, rather than accumulating it in the attributes of the root of the parse tree. The resulting space savings were important for previous generations of computers, which had very small main memories. On the other hand, semantic analysis is easier to perform during a separate traversal of a syntax tree, because that tree reﬂects the program’s semantic structure better than the parse tree does, especially with a top-down parser, and because one has the option of traversing the tree in an order other than that chosen by the parser.

Building a Syntax Tree

If we choose not to interleave parsing and semantic analysis, we still need to add attribute rules to the context-free grammar, but they serve only to create the syn- tax tree—not to enforce semantic rules or generate code. Figures 4.5 and 4.6 EXAMPLE 4.11

Bottom-up and top-down AGs to build a syntax tree contain bottom-up and top-down attribute grammars, respectively, to build a syntax tree for constant expressions. The attributes in these grammars hold nei- ther numeric values nor target code fragments; instead they point to nodes of the syntax tree. Function make leaf returns a pointer to a newly allocated syntax tree node containing the value of a constant. Functions make un op and make bin op return pointers to newly allocated syntax tree nodes containing a unary or

DESIGN & IMPLEMENTATION

4.2 Forward references In Sections 3.3.3 and C 3.4.1 we noted that the scope rules of many languages require names to be declared before they are used, and provide special mech- anisms to introduce the forward references needed for recursive deﬁnitions. While these rules may help promote the creation of clear, maintainable code, an equally important motivation, at least historically, was to facilitate the con- struction of one-pass compilers. With increases in memory size, processing speed, and programmer expectations regarding the quality of code improve- ment, multipass compilers have become ubiquitous, and language designers have felt free (as, for example, in the class declarations of C++, Java, and C#) to abandon the requirement that declarations precede uses.

3 Most authors use the term one-pass only for compilers that translate all the way from source to target code in a single pass. Some authors insist only that intermediate code be generated in a single pass, and permit additional pass(es) to translate intermediate code to target code.

![Figure 4.5 Bottom-up (S-attributed)...](images/page_227_vector_311.png)
*Figure 4.5 Bottom-up (S-attributed) attribute grammar to construct a syntax tree. The symbol +/−is used (as it is on calculators) to indicate change of sign.*

binary operator, respectively, and pointers to the supplied operand(s). Figures 4.7 and 4.8 show stages in the decoration of parse trees for (1 + 3) * 2, using the grammars of Figures 4.5 and 4.6, respectively. Note that the ﬁnal syntax tree is the same in each case. ■

3CHECK YOUR UNDERSTANDING 1. What determines whether a language rule is a matter of syntax or of static semantics? 2. Why is it impossible to detect certain program errors at compile time, even though they can be detected at run time?

  3.
  What is an attribute grammar?
  4.
  What are programming assertions? What is their purpose?
  5.
  What is the difference between synthesized and inherited attributes?

  6.
  Give two examples of information that is typically passed through inherited
  attributes.

  7.
  What is attribute ﬂow?
  8.
  What is a one-pass compiler?

![Figure 4.6 Top-down (L-attributed)...](images/page_228_vector_431.png)
*Figure 4.6 Top-down (L-attributed) attribute grammar to construct a syntax tree. Here the st attribute, like the ptr attribute (and unlike the st attribute of Figure 4.3), is a pointer to a syntax tree node.*

  9.
  What does it mean for an attribute grammar to be S-attributed? L-attributed?
  Noncircular? What is the signiﬁcance of these grammar classes?

## 4.4 Action Routines

Just as there are automatic tools that will construct a parser for a given context- free grammar, there are automatic tools that will construct a semantic analyzer (attribute evaluator) for a given attribute grammar. Attribute evaluator gen-

E

*

T

F *

(d)

×

T

![Figure 4.7 Construction of...](images/page_229_vector_547.png)
*Figure 4.7 Construction of a syntax tree for (1 + 3) * 2 via decoration of a bottom-up parse tree, using the grammar of Figure 4.5. This ﬁgure reads from bottom to top. In diagram (a), the values of the constants 1 and 3 have been placed in new syntax tree leaves. Pointers to these leaves propagate up into the attributes of E and T. In (b), the pointers to these leaves become child pointers of a new internal + node. In (c) the pointer to this node propagates up into the attributes of T, and a new leaf is created for 2. Finally, in (d), the pointers from T and F become child pointers of a new internal × node, and a pointer to this node propagates up into the attributes of E.*

E

![Figure 4.8 Construction of...](images/page_230_vector_515.png)
*Figure 4.8 Construction of a syntax tree via decoration of a top-down parse tree, using the grammar of Figure 4.6. In the top diagram, (a), the value of the constant 1 has been placed in a new syntax tree leaf. A pointer to this leaf then propagates to the st attribute of TT. In (b), a second leaf has been created to hold the constant 3. Pointers to the two leaves then become child pointers of a new internal + node, a pointer to which propagates from the st attribute of the bottom-most TT, where it was created, all the way up and over to the st attribute of the top-most FT. In (c), a third leaf has been created for the constant 2. Pointers to this leaf and to the + node then become the children of a new × node, a pointer to which propagates from the st of the lower FT, where it was created, all the way to the root of the tree.*

erators have been used in syntax-based editors [RT88], incremental compil- ers [SDB84], web-page layout [MTAB13], and various aspects of programming language research. Most production compilers, however, use an ad hoc, hand- written translation scheme, interleaving parsing with the construction of a syntax tree and, in some cases, other aspects of semantic analysis or intermediate code generation. Because they evaluate the attributes of each production as it is parsed, they do not need to build the full parse tree. An ad hoc translation scheme that is interleaved with parsing takes the form of a set of action routines. An action routine is a semantic function that the pro- grammer (grammar writer) instructs the compiler to execute at a particular point in the parse. Most parser generators allow the programmer to specify action rou- tines. In an LL parser generator, an action routine can appear anywhere within a right-hand side. A routine at the beginning of a right-hand side will be called as soon as the parser predicts the production. A routine embedded in the middle of a right-hand side will be called as soon as the parser has matched (the yield of) the symbol to the left. The implementation mechanism is simple: when it predicts a production, the parser pushes all of the right-hand side onto the stack, including terminals (to be matched), nonterminals (to drive future predictions), and point- ers to action routines. When it ﬁnds a pointer to an action routine at the top of the parse stack, the parser simply calls it, passing (pointers to) the appropriate attributes as arguments. To make this process more concrete, consider again our LL(1) grammar for EXAMPLE 4.12

Top-down action routines to build a syntax tree constant expressions. Action routines to build a syntax tree while parsing this grammar appear in Figure 4.9. The only difference between this grammar and the one in Figure 4.6 is that the action routines (delimited here with curly braces) are embedded among the symbols of the right-hand sides; the work performed is the same. The ease with which the attribute grammar can be transformed into the grammar with action routines is due to the fact that the attribute grammar is L-attributed. If it required more complicated ﬂow, we would not be able to cast it as action routines. ■

DESIGN & IMPLEMENTATION

4.3 Attribute evaluators Automatic evaluators based on formal attribute grammars are popular in lan- guage research projects because they save developer time when the language deﬁnition changes. They are popular in syntax-based editors and incremental compilers because they save execution time: when a small change is made to a program, the evaluator may be able to “patch up” tree decorations signiﬁ- cantly faster than it could rebuild them from scratch. For the typical compiler, however, semantic analysis based on a formal attribute grammar is overkill: it has higher overhead than action routines, and doesn’t really save the compiler writer that much work.

![Figure 4.9 LL(1) grammar...](images/page_232_vector_232.png)
*Figure 4.9 LL(1) grammar with action routines to build a syntax tree.*

![Figure 4.10 Recursive descent...](images/page_232_vector_372.png)
*Figure 4.10 Recursive descent parsing with embedded “action routines.” Compare with the routine of the same name in Figure 2.17, and with productions 2 through 4 in Figure 4.9.*

As in ordinary parsing, there is a strong analogy between recursive descent and table-driven parsing with action routines. Figure 4.10 shows the term tail rou- EXAMPLE 4.13

Recursive descent and action routines tine from Figure 2.17, modiﬁed to do its part in constructing a syntax tree. The behavior of this routine mirrors that of productions 2 through 4 in Figure 4.9. The routine accepts as a parameter a pointer to the syntax tree fragment con- tained in the attribute grammar’s TT1. Then, given an upcoming + or - sym- bol on the input, it (1) calls add op to parse that symbol (returning a character string representation); (2) calls term to parse the attribute grammar’s T; (3) calls make bin op to create a new tree node; (4) passes that node to term tail, which parses the attribute grammar’s TT2; and (5) returns the result. ■

Bottom-Up Evaluation

In an LR parser generator, one cannot in general embed action routines at arbi- trary places in a right-hand side, since the parser does not in general know what production it is in until it has seen all or most of the yield. LR parser generators therefore permit action routines only in the portion (sufﬁx) of the right-hand

side in which the production being parsed can be identiﬁed unambiguously (this is known as the trailing part; the ambiguous preﬁx is the left corner). If the at- tribute ﬂow of the action routines is strictly bottom-up (as it is in an S-attributed attribute grammar), then execution at the end of right-hand sides is all that is needed. The attribute grammars of Figures 4.1 and 4.5, in fact, are essentially identical to the action routine versions. If the action routines are responsible for a signiﬁcant part of semantic analysis, however (as opposed to simply building a syntax tree), then they will often need contextual information in order to do their job. To obtain and use this information in an LR parse, they will need some (necessarily limited) access to inherited attributes or to information outside the current production. We consider this issue further in Section C 4.5.1.

## 4.5 Space Management for Attributes

Any attribute evaluation method requires space to hold the attributes of the gram- mar symbols. If we are building an explicit parse tree, then the obvious approach is to store attributes in the nodes of the tree themselves. If we are not building a parse tree, then we need to ﬁnd a way to keep track of the attributes for the sym- bols we have seen (or predicted) but not yet ﬁnished parsing. The details differ in bottom-up and top-down parsers. For a bottom-up parser with an S-attributed grammar, the obvious approach is to maintain an attribute stack that directly mirrors the parse stack: next to every state number on the parse stack is an attribute record for the symbol we shifted when we entered that state. Entries in the attribute stack are pushed and popped automatically by the parser driver; space managementis not an issue for the writer of action routines. Complications arise if we try to achieve the effect of inherited attributes, but these can be accommodated within the basic attribute-stack frame- work. For a top-down parser with an L-attributed grammar, we have two principal options. The ﬁrst option is automatic, but more complex than for bottom-up grammars. It still uses an attribute stack, but one that does not mirror the parse stack. The second option has lower space overhead, and saves time by “short- cutting” copy rules, but requires action routines to allocate and deallocate space for attributes explicitly. In both families of parsers, it is common for some of the contextual infor- mation for action routines to be kept in global variables. The symbol table in particular is usually global. Rather than pass its full contents through attributes from one production to the next, we pass an indication of the currently active scope. Lookups in the global table then use this scope information to obtain the right referencing environment.

![Figure 4.11 Context-free grammar...](images/page_234_vector_216.png)
*Figure 4.11 Context-free grammar for a calculator language with types and declarations. The intent is that every identiﬁer be declared before use, and that types not be mixed in com- putations.*

IN MORE DEPTH

We consider attribute space management in more detail on the companion site. Using bottom-up and top-down grammars for arithmetic expressions, we illus- trate automatic management for both bottom-up and top-down parsers, as well as the ad hoc option for top-down parsers.

## 4.6 Tree Grammars and Syntax Tree Decoration

In our discussion so far we have used attribute grammars solely to decorate parse trees. As we mentioned in the chapter introduction, attribute grammars can also be used to decorate syntax trees. If our compiler uses action routines simply to build a syntax tree, then the bulk of semantic analysis and intermediate code gen- eration will use the syntax tree as base. Figure 4.11 contains a bottom-up CFG for a calculator language with types and EXAMPLE 4.14

declarations. The grammar differs from that of Example 2.37 in three ways: (1) we allow declarations to be intermixed with statements, (2) we differentiate between integer and real constants (presumably the latter contain a decimal point), and (3) we require explicit conversions between integer and real operands. The intended semantics of our language requires that every identiﬁer be declared before it is used, and that types not be mixed in computations. ■ Extrapolating from the example in Figure 4.5, it is easy to add semantic func- EXAMPLE 4.15

Bottom-up CFG for calculator language with types

Syntax tree to average an integer and a real tions or action routines to the grammar of Figure 4.11 to construct a syntax tree for the calculator language (Exercise 4.21). The obvious structure for such a tree would represent expressions as we did in Figure 4.7, and would represent a pro- gram as a linked list of declarations and statements. As a concrete example, Fig- ure 4.12 contains the syntax tree for a simple program to print the average of an integer and a real. ■

![Figure 4.12 Syntax tree...](images/page_235_vector_306.png)
*Figure 4.12 Syntax tree for a simple calculator program.*

Much as a context-free grammar describes the possible structure of parse trees EXAMPLE 4.16

for a given programming language, we can use a tree grammar to represent the possible structure of syntax trees. As in a CFG, each production of a tree grammar represents a possible relationship between a parent and its children in the tree. The parent is the symbol on the left-hand side of the production; the children are the symbols on the right-hand side. The productions used in Figure 4.12 might look something like the following:

Tree grammar for the calculator language with types

program −→item

int decl : item −→id item

read : item −→id item

real decl : item −→id item

write : item −→expr item

null : item −→ϵ

‘÷’ : expr −→expr expr

‘+’ : expr −→expr expr

ﬂoat : expr −→expr

id : expr −→ϵ

real const : expr −→ϵ

Here the notation A : B on the left-hand side of a production means that A is one variant of B, and may appear anywhere a B is expected on a right-hand side. ■

![Figure 4.13 Classes of...](images/page_236_vector_185.png)
*Figure 4.13 Classes of nodes for the syntax tree attribute grammar of Figure 4.14. With the exception of name, all variants of a given class have all the class’s attributes.*

Tree grammars and context-free grammars differ in important ways. A context-free grammar is meant to deﬁne (generate) a language composed of strings of tokens, where each string is the fringe (yield) of a parse tree. Pars- ing is the process of ﬁnding a tree that has a given yield. A tree grammar, as we use it here, is meant to deﬁne (or generate) the trees themselves. We have no need for a notion of parsing: we can easily inspect a tree and determine whether (and how) it can be generated by the grammar. Our purpose in introducing tree gram- mars is to provide a framework for the decoration of syntax trees. Semantic rules attached to the productions of a tree grammar can be used to deﬁne the attribute ﬂow of a syntax tree in exactly the same way that semantic rules attached to the productions of a context-free grammar are used to deﬁne the attribute ﬂow of a parse tree. We will use a tree grammar in the remainder of this section to perform static semantic checking. In Chapter 15 we will show how additional semantic rules can be used to generate intermediate code. A complete tree attribute grammar for our calculator language with types can EXAMPLE 4.17

Tree AG for the calculator language with types be constructed using the node classes, variants, and attributes shown in Fig- ure 4.13. The grammar itself appears in Figure 4.14. Once decorated, the program node at the root of the syntax tree will contain a list, in a synthesized attribute, of all static semantic errors in the program. (The list will be empty if the pro- gram is free of such errors.) Each item or expr node has an inherited attribute symtab that contains a list, with types, of all identiﬁers declared to the left in the tree. Each item node also has an inherited attribute errors in that lists all static semantic errors found to its left in the tree, and a synthesized attribute errors out to propagate the ﬁnal error list back to the root. Each expr node has one synthe- sized attribute that indicates its type and another that contains a list of any static semantic errors found inside. Our handling of semantic errors illustrates a common technique. In order to continue looking for other errors, we must provide values for any attributes that would have been set in the absence of an error. To avoid cascading error mes- sages, we choose values for those attributes that will pass quietly through subse- quent checks. In this speciﬁc case we employ a pseudotype called error, which

![Figure 4.14 Attribute grammar...](images/page_237_vector_518.png)
*Figure 4.14 Attribute grammar to decorate an abstract syntax tree for the calculator lan- guage with types. We use square brackets to delimit error messages and pointed brackets to delimit symbol table entries. Juxtaposition indicates concatenation within error messages; the ‘+’ and ‘−’ operators indicate insertion and removal in lists. We assume that every node has been initialized by the scanner or by action routines in the parser to contain an indication of the location (line and column) at which the corresponding construct appears in the source (see Exercise 4.22). The ‘?’ symbol is used as a “wild card”; it matches any type. (continued)*

![Figure 4.14 (continued on...](images/page_238_vector_478.png)
*Figure 4.14 (continued on next page)*

we associate with any symbol table entry or expression for which we have already generated a message. Though it takes a bit of checking to verify the fact, our attribute grammar is noncircular and well deﬁned. No attribute is ever assigned a value more than once. (The helper routines at the end of Figure 4.14 should be thought of as macros, rather than semantic functions. For the sake of brevity we have passed them entire tree nodes as arguments. Each macro calculates the values of two dif- ferent attributes. Under a strict formulation of attribute grammars each macro

![Figure 4.14 (continued)...](images/page_239_vector_355.png)
*Figure 4.14 (continued)*

would be replaced by two separate semantic functions, one per calculated at- tribute.) ■ Figure 4.15 uses the grammar of Figure 4.14 to decorate the syntax tree of EXAMPLE 4.18

Decorating a tree with the AG of Example 4.17 Figure 4.12. The pattern of attribute ﬂow appears considerably messier than in previous examples in this chapter, but this is simply because type checking is more complicated than calculating constants or building a syntax tree. Symbol table information ﬂows along the chain of items and down into expr trees. The int decl and real decl nodes add new information; other nodes simply pass the table along. Type information is synthesized at id : expr leaves by looking up an identiﬁer’s name in the symbol table. The information then propagates upward within an expression tree, and is used to type-check operators and assignments (the latter don’t appear in this example). Error messages ﬂow along the chain of items via the errors in attributes, and then back to the root via the errors out attributes. Messages also ﬂow up out of expr trees. Wherever a type check is performed, the type attribute may be used to help create a new message to be appended to the growing message list. ■ In our example grammar we accumulate error messages into a synthesized at- tribute of the root of the syntax tree. In an ad hoc attribute evaluator we might be tempted to print these messages on the ﬂy as the errors are discovered. In prac-

![Figure 4.15 Decoration of...](images/page_240_vector_434.png)
*Figure 4.15 Decoration of the syntax tree of Figure 4.12, using the grammar of Figure 4.14. Location information, which we assume has been initialized in every node by the parser, con- tributes to error messages, but does not otherwise propagate through the tree.*

tice, however, particularly in a multipass compiler, it makes sense to buffer the messages, so they can be interleaved with messages produced by other phases of the compiler, and printed in program order at the end of compilation. One could convert our attribute grammar into executable code using an au- tomatic attribute evaluator generator. Alternatively, one could create an ad hoc evaluator in the form of mutually recursive subroutines (Exercise 4.20). In the lat- ter case attribute ﬂow would be explicit in the calling sequence of the routines. We could then choose if desired to keep the symbol table in global variables, rather than passing it from node to node through attributes. Most compilers employ the ad hoc approach.

3CHECK YOUR UNDERSTANDING 10. What is the difference between a semantic function and an action routine? 11. Why can’t action routines be placed at arbitrary locations within the right- hand side of productions in an LR CFG? 12. What patterns of attribute ﬂow can be captured easily with action routines?

* Some compilers perform all semantic checks and intermediate code genera-
  tion in action routines. Others use action routines to build a syntax tree and
  then perform semantic checks and intermediate code generation in separate
  traversals of the syntax tree. Discuss the tradeoffs between these two strate-
  gies.

* What sort of information do action routines typically keep in global variables,
  rather than in attributes?

* Describe the similarities and differences between context-free grammars and
  tree grammars.

* How can a semantic analyzer avoid the generation of cascading error mes-
  sages?

## 4.7 Summary and Concluding Remarks

This chapter has discussed the task of semantic analysis. We reviewed the sorts of language rules that can be classiﬁed as syntax, static semantics, and dynamic se- mantics, and discussed the issue of whether to generate code to perform dynamic semantic checks. We also considered the role that the semantic analyzer plays in a typical compiler. We noted that both the enforcement of static semantic rules and the generation of intermediate code can be cast in terms of annotation, or decoration, of a parse tree or syntax tree. We then presented attribute grammars as a formal framework for this decoration process. An attribute grammar associates attributes with each symbol in a context-free grammar or tree grammar, and attribute rules with each production. In a CFG, synthesized attributes are calculated only in productions in which their symbol appears on the left-hand side. The synthesized attributes of tokens are initialized by the scanner. Inherited attributes are calculated in productions in which their symbol appears within the right-hand side; they allow calculations in the subtree below a symbol to depend on the context in which the symbol appears. Inher- ited attributes of the start symbol (goal) can represent the external environment of the compiler. Strictly speaking, attribute grammars allow only copy rules (as- signments of one attribute to another) and simple calls to semantic functions, but we usually relax this restriction to allow more or less arbitrary code fragments in some existing programming language.

Just as context-free grammars can be categorized according to the parsing al- gorithm(s) that can use them, attribute grammars can be categorized according to the complexity of their pattern of attribute ﬂow. S-attributed grammars, in which all attributes are synthesized, can naturally be evaluated in a single bottom-up pass over a parse tree, in precisely the order the tree is discovered by an LR-family parser. L-attributed grammars, in which all attribute ﬂow is depth-ﬁrst left-to- right, can be evaluated in precisely the order that the parse tree is predicted and matched by an LL-family parser. Attribute grammars with more complex pat- terns of attribute ﬂow are not commonly used for the parse trees of production compilers, but are valuable for syntax-based editors, incremental compilers, and various other tools. While it is possible to construct automatic tools to analyze attribute ﬂow and decorate parse trees, most compilers rely on action routines, which the compiler writer embeds in the right-hand sides of productions to evaluate attribute rules at speciﬁc points in a parse. In an LL-family parser, action routines can be embed- ded at arbitrary points in a production’s right-hand side. In an LR-family parser, action routines must follow the production’s left corner. Space for attributes in a bottom-up compiler is naturally allocated in parallel with the parse stack, but this complicates the management of inherited attributes. Space for attributes in a top-down compiler can be allocated automatically, or managed explicitly by the writer of action routines. The automatic approach has the advantage of regularity, and is easier to maintain; the ad hoc approach is slightly faster and more ﬂexible. In a one-pass compiler, which interleaves scanning, parsing, semantic analysis, and code generation in a single traversal of its input, semantic functions or action routines are responsible for all of semantic analysis and code generation. More commonly, action routines simply build a syntax tree, which is then decorated during separate traversal(s) in subsequent pass(es). The code for these traversals is usually written by hand, in the form of mutually recursive subroutines, allowing the compiler to accommodate essentially arbitrary attribute ﬂow on the syntax tree. In subsequent chapters (6–10 in particular) we will consider a wide variety of programming language constructs. Rather than present the actual attribute grammars required to implement these constructs, we will describe their seman- tics informally, and give examples of the target code. We will return to attribute grammars in Chapter 15, when we consider the generation of intermediate code in more detail.

## 4.8 Exercises

4.1 Basic results from automata theory tell us that the language L = anbncn = ϵ, abc, aabbcc, aaabbbccc, ... is not context free. It can be captured, however, using an attribute grammar. Give an underlying CFG and a set of attribute rules that associates a Boolean attribute ok with the root R of each

![Figure 4.16 Natural syntax...](images/page_243_vector_243.png)
*Figure 4.16 Natural syntax tree for the Lisp expression (cdr ‚(a b c)).*

parse tree, such that R.ok = true if and only if the string corresponding to the fringe of the tree is in L.

4.2 Modify the grammar of Figure 2.25 so that it accepts only programs that contain at least one write statement. Make the same change in the solution to Exercise 2.17. Based on your experience, what do you think of the idea of using the CFG to enforce the rule that every function in C must contain at least one return statement?

## 4.3 Give two examples of reasonable semantic rules that cannot be checked at reasonable cost, either statically or by compiler-generated code at run time.

4.4 Write an S-attributed attribute grammar, based on the CFG of Example 4.7, that accumulates the value of the overall expression into the root of the tree. You will need to use dynamic memory allocation so that individual attributes can hold an arbitrary amount of information.

4.5 Lisp has the unusual property that its programs take the form of parenthe- sized lists. The natural syntax tree for a Lisp program is thus a tree of binary cells (known in Lisp as cons cells), where the ﬁrst child represents the ﬁrst element of the list and the second child represents the rest of the list. The syntax tree for (cdr ‚(a b c)) appears in Figure 4.16. (The notation ‚L is syntactic sugar for (quote L).) Extend the CFG of Exercise 2.18 to create an attribute grammar that will build such trees. When a parse tree has been fully decorated, the root should have an attribute v that refers to the syntax tree. You may assume that each atom has a synthesized attribute v that refers to a syntax tree node that holds information from the scanner. In your semantic functions, you may assume the availability of a cons function that takes two references as arguments and returns a reference to a new cons cell containing those references.

4.6 Refer back to the context-free grammar of Exercise 2.13. Add attribute rules to the grammar to accumulate into the root of the tree a count of the max- imum depth to which parentheses are nested in the program string. For example, given the string f1(a, f2(b * (c + (d - (e - f))))), the stmt at the root of the tree should have an attribute with a count of 3 (the paren- theses surrounding argument lists don’t count).

4.7 Suppose that we want to translate constant expressions into the postﬁx, or “reverse Polish” notation of logician Jan Łukasiewicz. Postﬁx notation does not require parentheses. It appears in stack-based languages such as Postscript, Forth, and the P-code and Java bytecode intermediate forms mentioned in Section 1.4. It also served, historically, as the input language of certain hand-held calculators made by Hewlett-Packard. When given a number, a postﬁx calculator would push the number onto an internal stack. When given an operator, it would pop the top two numbers from the stack, apply the operator, and push the result. The display would show the value at the top of the stack. To compute 2 × (15 −3)/4, for example, one would push 2 E 1 5 E 3 E - * 4 E / (here E is the “enter” key, used to end the string of digits that constitute a number). Using the underlying CFG of Figure 4.1, write an attribute grammar that will associate with the root of the parse tree a sequence of postﬁx calculator button pushes, seq, that will compute the arithmetic value of the tokens derived from that symbol. You may assume the existence of a function buttons(c) that returns a sequence of button pushes (ending with E on a postﬁx calculator) for the constant c. You may also assume the existence of a concatenation function for sequences of button pushes.

## 4.8 Repeat the previous exercise using the underlying CFG of Figure 4.3.

## 4.9 Consider the following grammar for reverse Polish arithmetic expressions:

E −→E E op | id

op −→+ | - | * | /

Assuming that each id has a synthesized attribute name of type string, and that each E and op has an attribute val of type string, write an attribute grammar that arranges for the val attribute of the root of the parse tree to contain a translation of the expression into conventional inﬁx notation. For example, if the leaves of the tree, left to right, were “A A B - * C /,” then the val ﬁeld of the root would be “( ( A * ( A - B ) ) / C ).” As an extra challenge, write a version of your attribute grammar that exploits the usual arithmetic precedence and associativity rules to use as few parentheses as possible.

4.10 To reduce the likelihood of typographic errors, the digits comprising most credit card numbers are designed to satisfy the so-called Luhn formula, stan- dardized by ANSI in the 1960s, and named for IBM mathematician Hans Peter Luhn. Starting at the right, we double every other digit (the second- to-last, fourth-to-last, etc.). If the doubled value is 10 or more, we add the

resulting digits. We then sum together all the digits. In any valid number the result will be a multiple of 10. For example, 1234 5678 9012 3456 becomes 2264 1658 9022 6416, which sums to 64, so this is not a valid number. If the last digit had been 2, however, the sum would have been 60, so the number would potentially be valid. Give an attribute grammar for strings of digits that accumulates into the root of the parse tree a Boolean value indicating whether the string is valid according to Luhn’s formula. Your grammar should accommodate strings of arbitrary length.

4.11 Consider the following CFG for ﬂoating-point constants, without exponen- tial notation. (Note that this exercise is somewhat artiﬁcial: the language in question is regular, and would be handled by the scanner of a typical com- piler.)

C −→digits . digits

digits −→digit more digits

more digits −→digits | ϵ

digit −→0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

Augment this grammar with attribute rules that will accumulate the value of the constant into a val attribute of the root of the parse tree. Your answer should be S-attributed.

4.12 One potential criticism of the obvious solution to the previous problem is that the values in internal nodes of the parse tree do not reﬂect the value, in context, of the fringe below them. Create an alternative solution that addresses this criticism. More speciﬁcally, create your grammar in such a way that the val of an internal node is the sum of the vals of its chil- dren. Illustrate your solution by drawing the parse tree and attribute ﬂow for 12.34. (Hint: You will probably want a different underlying CFG, and non-L-attributed ﬂow.)

## 4.13 Consider the following attribute grammar for variable declarations, based on the CFG of Exercise 2.11:

decl −→ID decl tail  decl.t := decl tail.t  decl tail.in tab := insert (decl.in tab, ID.n, decl tail.t)  decl.out tab := decl tail.out tab decl tail −→, decl  decl tail.t := decl.t  decl.in tab := decl tail.in tab  decl tail.out tab := decl.out tab decl tail −→: ID ;  decl tail.t := ID.n  decl tail.out tab := decl tail.in tab

Show a parse tree for the string A, B : C;. Then, using arrows and textual description, specify the attribute ﬂow required to fully decorate the tree. (Hint: Note that the grammar is not L-attributed.)

4.14 A CFG-based attribute evaluator capable of handling non-L-attributed at- tribute ﬂow needs to take a parse tree as input. Explain how to build a parse tree automatically during a top-down or bottom-up parse (i.e., without ex- plicit action routines).

## 4.15 Building on Example 4.13, modify the remainder of the recursive descent parser of Figure 2.17 to build syntax trees for programs in the calculator language.

4.16 Write an LL(1) grammar with action routines and automatic attribute space management that generates the reverse Polish translation described in Ex- ercise 4.7. 4.17 (a) Write a context-free grammar for polynomials in x. Add semantic func- tions to produce an attribute grammar that will accumulate the poly- nomial’s derivative (as a string) in a synthesized attribute of the root of the parse tree. (b) Replace your semantic functions with action routines that can be eval- uated during parsing. 4.18 (a) Write a context-free grammar for case or switch statements in the style of Pascal or C. Add semantic functions to ensure that the same label does not appear on two different arms of the construct. (b) Replace your semantic functions with action routines that can be eval- uated during parsing.

## 4.19 Write an algorithm to determine whether the rules of an arbitrary attribute grammar are noncircular. (Your algorithm will require exponential time in the worst case [JOR75].)

4.20 Rewrite the attribute grammar of Figure 4.14 in the form of an ad hoc tree traversal consisting of mutually recursive subroutines in your favorite pro- gramming language. Keep the symbol table in a global variable, rather than passing it through arguments.

## 4.21 Write an attribute grammar based on the CFG of Figure 4.11 that will build a syntax tree with the structure described in Figure 4.14.

4.22 Augment the attribute grammar of Figure 4.5, Figure 4.6, or Exercise 4.21 to initialize a synthesized attribute in every syntax tree node that indicates the location (line and column) at which the corresponding construct appears in the source program. You may assume that the scanner initializes the location of every token.

4.23 Modify the CFG and attribute grammar of Figures 4.11 and 4.14 to permit mixed integer and real expressions, without the need for float and trunc. You will want to add an annotation to any node that must be coerced to the opposite type, so that the code generator will know to generate code to do

so. Be sure to think carefully about your coercion rules. In the expression my_int + my_real, for example, how will you know whether to coerce the integer to be a real, or to coerce the real to be an integer?

## 4.24 Explain the need for the A : B notation on the left-hand sides of produc- tions in a tree grammar. Why isn’t similar notation required for context-free grammars?

4.25 A potential objection to the tree attribute grammar of Example 4.17 is that it repeatedly copies the entire symbol table from one node to another. In this particular tiny language, it is easy to see that the referencing environment never shrinks: the symbol table changes only with the addition of new iden- tiﬁers. Exploiting this observation, show how to modify the pseudocode of Figure 4.14 so that it copies only pointers, rather than the entire symbol table.

4.26 Your solution to the previous exercise probably doesn’t generalize to lan- guages with nontrivial scoping rules. Explain how an AG such as that in Figure 4.14 might be modiﬁed to use a global symbol table similar to the one described in Section C 3.4.1. Among other things, you should consider nested scopes, the hiding of names in outer scopes, and the requirement (not enforced by the table of Section C 3.4.1) that variables be declared be- fore they are used.

4.27–4.31 In More Depth.

## 4.9 Explorations

4.32 One of the most inﬂuential applications of attribute grammars was the Cor- nell Synthesizer Generator [Rep84, RT88]. Learn how the Generator used attribute grammars not only for incremental update of semantic informa- tion in a program under edit, but also for automatic creation of language based editors from formal language speciﬁcations. How general is this tech- nique? What applications might it have beyond syntax-directed editing of computer programs?

4.33 The attribute grammars used in this chapter are all quite simple. Most are S- or L-attributed. All are noncircular. Are there any practical uses for more complex attribute grammars? How about automatic attribute eval- uators? Using the Bibliographic Notes as a starting point, conduct a survey of attribute evaluation techniques. Where is the line between practical tech- niques and intellectual curiosities?

4.34 The ﬁrst validated Ada implementation was the Ada/Ed interpreter from New York University [DGAFS+80]. The interpreter was written in the set- based language SETL [SDDS86] using a denotational semantics deﬁnition of Ada. Learn about the Ada/Ed project, SETL, and denotational semantics. Discuss how the use of a formal deﬁnition aided the development process.

Also discuss the limitations of Ada/Ed, and expand on the potential role of formal semantics in language design, development, and prototype imple- mentation.

4.35 Version 5 of the Scheme language manual [KCR+98] included a formal def- inition of Scheme in denotational semantics. How long is this deﬁnition, compared to the more conventional deﬁnition in English? How readable is it? What do the length and the level of readability say about Scheme? About denotational semantics? (For more on denotational semantics, see the texts of Stoy [Sto77] or Gordon [Gor79].) Version 6 of the manual [SDF+07] switched to operational semantics. How does this compare to the denotational version? Why do you suppose the standards committee made the change? (For more information, see the paper by Matthews and Findler [MF08].)

4.36–4.37 In More Depth.

## 4.10 Bibliographic Notes

Much of the early theory of attribute grammars was developed by Knuth [Knu68]. Lewis, Rosenkrantz, and Stearns [LRS74] introduced the notion of an L- attributed grammar. Watt [Wat77] showed how to use marker symbols to em- ulate inherited attributes in a bottom-up parser. Jazayeri, Ogden, and Rounds [JOR75] showed that exponential time may be required in the worst case to dec- orate a parse tree with arbitrary attribute ﬂow. Articles by Courcelle [Cou84] and Engelfriet [Eng84] survey the theory and practice of attribute evaluation. Language-based program editing based on attribute grammars was pioneered by the Synthesizer Generator [RT88] (a follow-on to the language-speciﬁc Cor- nell Program Synthesizer [TR81]) of Reps and Teitelbaum. Magpie [SDB84] was an early incremental compiler, again based on attribute grammars. Meyerovich et al. [MTAB13] have recently used attribute grammars to parallelize a variety of tree-traversal tasks—notably for web page rendering and GPU-accelerated ani- mation. Action routines to implement many language features can be found in the texts of Fischer et al. or Appel [App97]. Further notes on attribute grammars can be found in the texts of Cooper and Torczon [CT04, pp. 171–188] or Aho et al. [ALSU07, Chap. 5]. Marcotty, Ledgard, and Bochmann [MLB76] provide an early survey of formal notations for programming language semantics. More detailed but still somewhat dated treatment can be found in the texts of Winskel [Win93] and Slonneger and Kurtz [SK95]. Nipkow and Klein cover the topic from a modern and mathe- matically rigorous perspective, integrating their text with an executable theorem- proving system [NK15]. The seminal paper on axiomatic semantics is by Hoare [Hoa69]. An excellent book on the subject is Gries’s The Science of Programming [Gri81]. The seminal paper on denotational semantics is by Scott and Strachey [SS71]. Early texts on the subject include those of Stoy [Sto77] and Gordon [Gor79].

