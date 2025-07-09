# Chapter 6: Control Flow

6 Control Flow

Having considered the mechanisms that a compiler uses to enforce se- mantic rules (Chapter 4) and the characteristics of the target machines for which compilers must generate code (Chapter 5), we now return to core issues in lan- guage design. Speciﬁcally, we turn in this chapter to the issue of control ﬂow or ordering in program execution. Ordering is fundamental to most models of com- puting. It determines what should be done ﬁrst, what second, and so forth, to accomplish some desired task. We can organize the language mechanisms used to specify ordering into several categories:

* Sequencing: Statements are to be executed (or expressions evaluated) in a cer-
  tain speciﬁed order—usually the order in which they appear in the program
  text.
* Selection: Depending on some run-time condition, a choice is to be made
  among two or more statements or expressions. The most common selection
  constructs are if and case (switch) statements. Selection is also sometimes
  referred to as alternation.
* Iteration: A given fragment of code is to be executed repeatedly, either a cer-
  tain number of times, or until a certain run-time condition is true. Iteration
  constructs include for/do, while, and repeat loops.
* Procedural abstraction: A potentially complex collection of control constructs
  (a subroutine) is encapsulated in a way that allows it to be treated as a single
  unit, usually subject to parameterization.
* Recursion: An expression is deﬁned in terms of (simpler versions of) itself, ei-
  ther directly or indirectly; the computational model requires a stack on which
  to save information about partially evaluated instances of the expression. Re-
  cursion is usually deﬁned by means of self-referential subroutines.
* Concurrency: Two or more program fragments are to be executed/evaluated
  “at the same time,” either in parallel on separate processors, or interleaved on
  a single processor in a way that achieves the same effect.
* Exception handling and speculation: A program fragment is executed optimisti-
  cally, on the assumption that some expected condition will be true. If that con-

dition turns out to be false, execution branches to a handler that executes in place of the remainder of the protected fragment (in the case of exception han- dling), or in place of the entire protected fragment (in the case of speculation). For speculation, the language implementation must be able to undo, or “roll back,” any visible effects of the protected code. 8. Nondeterminacy: The ordering or choice among statements or expressions is deliberately left unspeciﬁed, implying that any alternative will lead to correct results. Some languages require the choice to be random, or fair, in some for- mal sense of the word.

Though the syntactic and semantic details vary from language to language, these categories cover all of the control-ﬂow constructs and mechanisms found in most programming languages. A programmer who thinks in terms of these categories, rather than the syntax of some particular language, will ﬁnd it easy to learn new languages, evaluate the tradeoffs among languages, and design and reason about algorithms in a language-independent way. Subroutines are the subject of Chapter 9. Concurrency is the subject of Chap- ter 13. Exception handling and speculation are discussed in those chapters as well, in Sections 9.4 and 13.4.4. The bulk of the current chapter (Sections 6.3 through 6.7) is devoted to the ﬁve remaining categories. We begin in Section 6.1 by considering the evaluation of expressions—the building blocks on which all higher-level ordering is based. We consider the syntactic form of expressions, the precedence and associativity of operators, the order of evaluation of operands, and the semantics of the assignment statement. We focus in particular on the distinction between variables that hold a value and variables that hold a reference to a value; this distinction will play an important role many times in future chap- ters. In Section 6.2 we consider the difference between structured and unstructured (goto-based) control ﬂow. The relative importance of different categories of control ﬂow varies signif- icantly among the different classes of programming languages. Sequencing is central to imperative (von Neumann and object-oriented) languages, but plays a relatively minor role in functional languages, which emphasize the evaluation of expressions, de-emphasizing or eliminating statements (e.g., assignments) that affect program output in any way other than through the return of a value. Sim- ilarly, functional languages make heavy use of recursion, while imperative lan- guages tend to emphasize iteration. Logic languages tend to de-emphasize or hide the issue of control ﬂow entirely: The programmer simply speciﬁes a set of infer- ence rules; the language implementation must ﬁnd an order in which to apply those rules that will allow it to deduce values that satisfy some desired property.

6.1 Expression Evaluation

An expression generally consists of either a simple object (e.g., a literal constant, or a named variable or constant) or an operator or function applied to a col-

lection of operands or arguments, each of which in turn is an expression. It is conventional to use the term operator for built-in functions that use special, simple syntax, and to use the term operand for an argument of an operator. In EXAMPLE 6.1

A typical function call most imperative languages, function calls consist of a function name followed by a parenthesized, comma-separated list of arguments, as in

my_func(A, B, C) ■

Operators are typically simpler, taking only one or two arguments, and dispensing EXAMPLE 6.2

Typical operators with the parentheses and commas:

```
a + b
- c
```

As we saw in Section 3.5.2, some languages deﬁne their operators as syntactic sugar for more “normal”-looking functions. In Ada, for example, a + b is short for "+"(a, b); in C++, a + b is short for a.operator+(b) or operator+(a, b) (whichever is deﬁned). ■ In general, a language may specify that function calls (operator invocations) employ preﬁx, inﬁx, or postﬁx notation. These terms indicate, respectively, whether the function name appears before, among, or after its several arguments:

preﬁx: op a b or op (a, b) or (op a b) inﬁx: a op b postﬁx: a b op

Most imperative languages use inﬁx notation for binary operators and preﬁx notation for unary operators and (with parentheses around the arguments) other functions. Lisp uses preﬁx notation for all functions, but with the third of the EXAMPLE 6.3

Cambridge Polish (preﬁx) notation variants above: in what is known as Cambridge Polish1 notation, it places the function name inside the parentheses:

(* (+ 1 3) 2) ; that would be (1 + 3) * 2 in infix (append a b c my_list) ■

ML-family languages dispense with the parentheses altogether, except when EXAMPLE 6.4

Juxtaposition in ML they are required for disambiguation:

max (2 + 3) 4;; =⇒5 ■

1 Preﬁx notation was popularized by Polish logicians of the early 20th century; Lisp-like parenthe- sized syntax was ﬁrst employed (for noncomputational purposes) by philosopher W. V. Quine of Harvard University (Cambridge, MA).

A few languages, notably ML and the R scripting language, allow the user to create new inﬁx operators. Smalltalk uses inﬁx notation for all functions (which it calls messages), both built-in and user-deﬁned. The following Smalltalk state- EXAMPLE 6.5

Mixﬁx notation in Smalltalk ment sends a “displayOn: at:” message to graphical object myBox, with ar- guments myScreen and 100@50 (a pixel location). It corresponds to what other languages would call the invocation of the “displayOn: at:” function with ar- guments myBox, myScreen, and 100@50.

myBox displayOn: myScreen at: 100@50 ■

This sort of multiword inﬁx notation occurs occasionally in other languages as EXAMPLE 6.6

Conditional expressions well.2 In Algol one can say

a := if b <> 0 then a/b else 0;

Here “if... then ... else” is a three-operand inﬁx operator. The equivalent op- erator in C is written “... ? ... : ...”:

a = b != 0 ? a/b : 0; ■

Postﬁx notation is used for most functions in Postscript, Forth, the input lan- guage of certain hand-held calculators, and the intermediate code of some com- pilers. Postﬁx appears in a few places in other languages as well. Examples in- clude the pointer dereferencing operator (^) of Pascal and the post-increment and decrement operators (++ and --) of C and its descendants.

6.1.1 Precedence and Associativity

Most languages provide a rich set of built-in arithmetic and logical operators. When written in inﬁx notation, without parentheses, these operators lead to am- biguity as to what is an operand of what. In Fortran, for example, which uses ** EXAMPLE 6.7

A complicated Fortran expression for exponentiation, how should we parse a + b * c**d**e/f? Should this be grouped as

((((a + b) * c)**d)**e)/f

or

a + (((b * c)**d)**(e/f))

or

2 Most authors use the term “inﬁx” only for binary operators. Multiword operators may be called “mixﬁx,” or left unnamed.

a + ((b * (c**(d**e)))/f)

or yet some other option? (In Fortran, the answer is the last of the options shown.) ■ In any given language, the choice among alternative evaluation orders depends on the precedence and associativity of operators, concepts we introduced in Sec- tion 2.1.3. Issues of precedence and associativity do not arise in preﬁx or postﬁx notation. Precedence rules specify that certain operators, in the absence of parentheses, group “more tightly” than other operators. In most languages multiplication and EXAMPLE 6.8

Precedence in four inﬂuential languages division group more tightly than addition and subtraction, so 2 + 3 × 4 is 14 and not 20. Details vary widely from one language to another, however. Figure 6.1 shows the levels of precedence for several well-known languages. ■ The precedence structure of C (and, with minor variations, of its descendants, C++, Java, and C#) is substantially richer than that of most other languages. It is, in fact, richer than shown in Figure 6.1, because several additional constructs, including type casts, function calls, array subscripting, and record ﬁeld selection, are classiﬁed as operators in C. It is probably fair to say that most C program- mers do not remember all of their language’s precedence levels. The intent of the language designers was presumably to ensure that “the right thing” will usu- ally happen when parentheses are not used to force a particular evaluation order. Rather than count on this, however, the wise programmer will consult the manual or add parentheses. It is also probably fair to say that the relatively ﬂat precedence hierarchy of Pas- EXAMPLE 6.9

A “gotcha” in Pascal precedence cal was a mistake. Novice Pascal programmers would frequently write conditions like

if A < B and C < D then (* ouch *)

Unless A, B, C, and D were all of type Boolean, which is unlikely, this code would result in a static semantic error, since the rules of precedence cause it to group as A < (B and C) < D. (And even if all four operands were of type Boolean, the result was almost certain to be something other than what the programmer intended.) Most languages avoid this problem by giving arithmetic operators higher prece- dence than relational (comparison) operators, which in turn have higher prece- dence than the logical operators. Notable exceptions include APL and Smalltalk, in which all operators are of equal precedence; parentheses must be used to specify grouping. ■ Associativity rules specify whether sequences of operators of equal precedence EXAMPLE 6.10

Common rules for associativity group to the right or to the left. Conventions here are somewhat more uniform across languages, but still display some variety. The basic arithmetic operators almost always associate left-to-right, so 9 - 3 - 2 is 4 and not 8. In Fortran, as noted above, the exponentiation operator (**) follows standard mathematical convention, and associates right-to-left, so 4**3**2 is 262144 and not 4096. In Ada, exponentiation does not associate: one must write either (4**3)**2 or

![Figure 6.1 Operator precedence...](images/page_261_vector_480.png)
*Figure 6.1 Operator precedence levels in Fortran, Pascal, C, and Ada. The operators at the top of the ﬁgure group most tightly.*

4**(3**2); the language syntax does not allow the unparenthesized form. In languages that allow assignments inside expressions (an option we will consider more in Section 6.1.2), assignment associates right-to-left. Thus in C, a = b = a + c assigns a + c into b and then assigns the same value into a. ■ Haskell is unusual in allowing the programmer to specify both the associativity EXAMPLE 6.11

User-deﬁned precedence and associativity in Haskell and the precedence of user-deﬁned operators. The predeﬁned ^ operator, for ex-

ample, which indicates integer exponentiation, is declared in the standard library (and could be redeﬁned by the programmer) as

infixr 8 ^

Here infixr means “right associative inﬁx operator,” so 4 ^ 3 ^ 2 groups as 4 ^ (3 ^ 2) rather than as (4 ^ 3) ^ 2. The similar infixl and infix dec- larations specify left associativity and nonassociativity, respectively. Precedence levels run from 0 (loosest) to 9 (tightest). If no “ﬁxity” declaration is provided, newly deﬁned operators are left associative by default, and group at level 9. Func- tion application (speciﬁed simply via juxtaposition in Haskell) groups tightest of all—effectively at level 10. ■ Because the rules for precedence and associativity vary so much from one lan- guage to another, a programmer who works in several languages is wise to make liberal use of parentheses.

6.1.2 Assignments

In a purely functional language, expressions are the building blocks of programs, and computation consists entirely of expression evaluation. The effect of any individual expression on the overall computation is limited to the value that ex- pression provides to its surrounding context. Complex computations employ re- cursion to generate a potentially unbounded number of values, expressions, and contexts. In an imperative language, by contrast, computation typically consists of an ordered series of changes to the values of variables in memory. Assignments pro- vide the principal means by which to make the changes. Each assignment takes a pair of arguments: a value and a reference to a variable into which the value should be placed. In general, a programming language construct is said to have a side effect if it inﬂuences subsequent computation (and ultimately program output) in any way other than by returning a value for use in the surrounding context. Assignment is perhaps the most fundamental side effect: while the evaluation of an assignment may sometimes yield a value, what we really care about is the fact that it changes the value of a variable, thereby inﬂuencing the result of any later computation in which the variable appears. Many imperative languages distinguish between expressions, which always pro- duce a value, and may or may not have side effects, and statements, which are ex- ecuted solely for their side effects, and return no useful value. Given the centrality of assignment, imperative programming is sometimes described as “computing by means of side effects.” At the opposite extreme, purely functional languages have no side effects. As a result, the value of an expression in such a language depends only on the referenc- ing environment in which the expression is evaluated, not on the time at which

the evaluation occurs. If an expression yields a certain value at one point in time, it is guaranteed to yield the same value at any point in time. In fancier terms, expressions in a purely functional language are said to be referentially transparent. Haskell and Miranda are purely functional. Many other languages are mixed: ML and Lisp are mostly functional, but make assignment available to program- mers who want it. C#, Python, and Ruby are mostly imperative, but provide a variety of features (ﬁrst-class functions, polymorphism, functional values and aggregates, garbage collection, unlimited extent) that allow them to be used in a largely functional style. We will return to functional programming, and the features it requires, in several future sections, including 6.2.2, 6.6, 7.3, 8.5.3, 8.6, and all of Chapter 11.

References and Values

On the surface, assignment appears to be a very straightforward operation. Be- low the surface, however, there are some subtle but important differences in the semantics of assignment in different imperative languages. These differences are often invisible, because they do not affect the behavior of simple programs. They have a major impact, however, on programs that use pointers, and will be ex- plored in further detail in Section 8.5. We provide an introduction to the issues here. Consider the following assignments in C: EXAMPLE 6.12

L-values and r-values d = a; a = b + c;

In the ﬁrst statement, the right-hand side of the assignment refers to the value of a, which we wish to place into d. In the second statement, the left-hand side refers to the location of a, where we want to put the sum of b and c. Both interpretations—value and location—are possible because a variable in C (as in many other languages) is a named container for a value. We sometimes say that languages like C use a value model of variables. Because of their use on the left- hand side of assignment statements, expressions that denote locations are referred to as l-values. Expressions that denote values (possibly the value stored in a loca- tion) are referred to as r-values. Under a value model of variables, a given expres- sion can be either an l-value or an r-value, depending on the context in which it appears. ■ Of course, not all expressions can be l-values, because not all values have a location, and not all names are variables. In most languages it makes no sense to EXAMPLE 6.13

L-values in C say 2 + 3 = a, or even a = 2 + 3, if a is the name of a constant. By the same token, not all l-values are simple names; both l-values and r-values can be complicated expressions. In C one may write

(f(a)+3)->b[c] = 2;

In this expression f(a) returns a pointer to some element of an array of pointers to structures (records). The assignment places the value 2 into the c-th element

![Figure 6.2 The value...](images/page_264_vector_163.png)
*Figure 6.2 The value (left) and reference (right) models of variables. Under the reference model, it becomes important to distinguish between variables that refer to the same object and variables that refer to different objects whose values happen (at the moment) to be equal.*

of ﬁeld b of the structure pointed at by the third array element after the one to which f’s return value points. ■ In C++ it is even possible for a function to return a reference to a structure, EXAMPLE 6.14

L-values in C++ rather than a pointer to it, allowing one to write

g(a).b[c] = 2; ■

We will consider references further in Section 9.3.1. A language can make the distinction between l-values and r-values more ex- plicit by employing a reference model of variables. Languages that do this include Algol 68, Clu, Lisp/Scheme, ML, and Smalltalk. In these languages, a variable is not a named container for a value; rather, it is a named reference to a value. The EXAMPLE 6.15

Variables as values and references following fragment of code is syntactically valid in both Pascal and Clu:

```
b := 2;
c := b;
a := b + c;
```

A Pascal programmer might describe this code by saying: “We put the value 2 in b and then copy it into c. We then read these values, add them together, and place the resulting 4 in a.” The Clu programmer would say: “We let b refer to 2 and then let c refer to it also. We then pass these references to the + operator, and let a refer to the result, namely 4.” These two ways of thinking are illustrated in Figure 6.2. With a value model of variables, any integer variable can contain the value 2. With a reference model of variables, there is (at least conceptually) only one 2—a sort of Platonic Ideal— to which any variable can refer. The practical effect is the same in this example, because integers are immutable: the value of 2 never changes, so we can’t tell the difference between two copies of the number 2 and two references to “the” number 2. ■ In a language that uses the reference model, every variable is an l-value. When it appears in a context that expects an r-value, it must be dereferenced to obtain the value to which it refers. In most languages with a reference model (including Clu), the dereference is implicit and automatic. In ML, the programmer must use

an explicit dereference operator, denoted with a preﬁx exclamation point. We will revisit ML pointers in Section 8.5.1. The difference between the value and reference models of variables becomes particularly important (speciﬁcally, it can affect program output and behavior) if the values to which variables refer can change “in place,” as they do in many programs with linked data structures, or if it is possible for variables to refer to different objects that happen to have the “same” value. In this latter case it be- comes important to distinguish between variables that refer to the same object and variables that refer to different objects whose values happen (at the moment) to be equal. (Lisp, as we shall see in Sections 7.4 and 11.3.3, provides more than one notion of equality, to accommodate this distinction.) We will discuss the value and reference models of variables further in Section 8.5. Java uses a value model for built-in types and a reference model for user- deﬁned types (classes). C# and Eiffel allow the programmer to choose between the value and reference models for each individual user-deﬁned type. A C# class is a reference type; a struct is a value type.

Boxing

A drawback of using a value model for built-in types is that they can’t be passed uniformly to methods that expect class-typed parameters. Early versions of Java EXAMPLE 6.16

Wrapper classes required the programmer to “wrap” objects of built-in types inside corresponding predeﬁned class types in order to insert them in standard container (collection) classes:

```
import java.util.Hashtable;
...
Hashtable ht = new Hashtable();
...
Integer N = new Integer(13);
// Integer is a "wrapper" class
ht.put(N, new Integer(31));
Integer M = (Integer) ht.get(N);
int m = M.intValue();
```

The wrapper class was needed here because Hashtable expects a parameter of object type, and an int is not an object. ■

DESIGN & IMPLEMENTATION

6.1 Implementing the reference model It is tempting to assume that the reference model of variables is inherently more expensive than the value model, since a naive implementation would require a level of indirection on every access. As we shall see in Section 8.5.1, however, most compilers for languages with a reference model use multiple copies of immutable objects for the sake of efﬁciency, achieving exactly the same performance for simple types that they would with a value model.

C# and more recent versions of Java perform automatic boxing and unboxing EXAMPLE 6.17

Boxing in Java 5 and C# operations that avoid the wrapper syntax in many cases:

```
ht.put(13, 31);
int m = (Integer) ht.get(13);
```

Here the Java compiler creates hidden Integer objects to hold the values 13 and 31, so they may be passed to put as references. The Integer cast on the return value is still needed, to make sure that the hash table entry for 13 is really an integer and not, say, a ﬂoating-point number or string. Generics, which we will consider in Section 7.3.1, allow the programmer to declare a table containing only integers. In Java, this would eliminate the need to cast the return value. In C#, it would eliminate the need for boxing. ■

Orthogonality

A common design goal is to make the various features of a language as orthogonal as possible. Orthogonality means that features can be used in any combination, the combinations all make sense, and the meaning of a given feature is consistent, regardless of the other features with which it is combined. Algol 68 was one of the ﬁrst languages to make orthogonality a principal design goal, and in fact few languages since have given the goal such weight. Among other things, Algol 68 is said to be expression-oriented: it has no separate notion of statement. Arbitrary expressions can appear in contexts that would call for a statement in many other languages, and constructs that are considered to be statements in other languages can appear within expressions. The following, for EXAMPLE 6.18

Expression orientation in Algol 68 example, is valid in Algol 68:

```
begin
a := if b < c then d else e;
a := begin f(b); g(c) end;
g(d);
2 + 3
end
```

Here the value of the if... then ... else construct is either the value of its then part or the value of its else part, depending on the value of the condition. The value of the “statement list” on the right-hand side of the second assignment is the value of its ﬁnal “statement,” namely the return value of g(c). There is no need to distinguish between procedures and functions, because every subroutine call returns a value. The value returned by g(d) is discarded in this example. Finally, the value of the code fragment as a whole is 5, the sum of 2 and 3. ■ C takes an intermediate approach. It distinguishes between statements and ex- pressions, but one of the classes of statement is an “expression statement,” which computes the value of an expression and then throws it away; in effect, this allows an expression to appear in any context that would require a statement in most other languages. Unfortunately, as we noted in Section 3.7, the reverse is not the

case: statements cannot in general be used in an expression context. C provides special expression forms for selection and sequencing. Algol 60 deﬁnes if... then ... else as both a statement and an expression. Both Algol 68 and C allow assignments within expressions. The value of an assignment is simply the value of its right-hand side. Where most of the descen- dants of Algol 60 use the := token to represent assignment, C follows Fortran in simply using =. It uses == to represent a test for equality (Fortran uses .eq.). Moreover, in any context that expects a Boolean value, C accepts anything that EXAMPLE 6.19

A “gotcha” in C conditions can be coerced to be an integer. It interprets zero as false; any other value is true.3 As a result, both of the following constructs are valid—common—in C:

```
if (a == b) {
/* do the following if a equals b */
...
```

```
if (a = b) {
/* assign b into a and then do
the following if the result is nonzero */
...
```

Programmers who are accustomed to Ada or some other language in which = is the equality test frequently write the second form above when the ﬁrst is what is intended. This sort of bug can be very hard to ﬁnd. ■ Though it provides a true Boolean type (bool), C++ shares the problem of C, because it provides automatic coercions from numeric, pointer, and enumeration types. Java and C# eliminate the problem by disallowing integers in Boolean con- texts. The assignment operator is still =, and the equality test is still ==, but the statement if (a = b) ... will generate a compile-time type clash error unless a and b are both of Boolean type.

Combination Assignment Operators

Because they rely so heavily on side effects, imperative programs must frequently update a variable. It is thus common in many languages to see statements like EXAMPLE 6.20

Updating assignments a = a + 1;

or, worse,

b.c[3].d = b.c[3].d * e;

Such statements are not only cumbersome to write and to read (we must examine both sides of the assignment carefully to see if they really are the same), they also

3 Historically, C lacked a separate Boolean type. C99 added _Bool, but it’s really just a 1-bit integer.

result in redundant address calculations (or at least extra work to eliminate the redundancy in the code improvement phase of compilation). ■ If the address calculation has a side effect, then we may need to write a pair of EXAMPLE 6.21

Side effects and updates statements instead. Consider the following code in C:

```
void update(int A[], int index_fn(int n)) {
int i, j;
/* calculate i */
...
j = index_fn(i);
A[j] = A[j] + 1;
}
```

Here we cannot safely write

A[index_fn(i)] = A[index_fn(i)] + 1;

We have to introduce the temporary variable j because we don’t know whether index_fn has a side effect or not. If it is being used, for example, to keep a log of elements that have been updated, then we shall want to make sure that update calls it only once. ■ To eliminate the clutter and compile- or run-time cost of redundant address calculations, and to avoid the issue of repeated side effects, many languages, be- ginning with Algol 68, and including C and its descendants, provide so-called assignment operators to update a variable. Using assignment operators, the state- EXAMPLE 6.22

Assignment operators ments in Example 6.20 can be written as follows:

```
a += 1;
b.c[3].d *= e;
```

and the two assignments in the update function can be replaced with

A[index_fn(i)] += 1;

In addition to being aesthetically cleaner, the assignment operator form guaran- tees that the address calculation and any side effects happen only once. ■ As shown in Figure 6.1, C provides 10 different assignment operators, one for each of its binary arithmetic and bit-wise operators. C also provides preﬁx and EXAMPLE 6.23

Preﬁx and postﬁx inc/dec postﬁx increment and decrement operations. These allow even simpler code in update:

A[index_fn(i)]++;

or

++A[index_fn(i)];

More signiﬁcantly, increment and decrement operators provide elegant syntax for code that uses an index or a pointer to traverse an array:

```
A[--i] = b;
*p++ = *q++;
```

When preﬁxed to an expression, the ++ or -- operator increments or decrements its operand before providing a value to the surrounding context. In the postﬁx form, ++ or -- updates its operand after providing a value. If i is 3 and p and q point to the initial elements of a pair of arrays, then b will be assigned into A[2] (not A[3]), and the second assignment will copy the initial elements of the arrays (not the second elements). ■ The preﬁx forms of ++ and -- are syntactic sugar for += and -=. We could EXAMPLE 6.24

Advantages of postﬁx inc/dec have written

A[i -= 1] = b;

above. The postﬁx forms are not syntactic sugar. To obtain an effect similar to the second statement above we would need an auxiliary variable and a lot of extra notation:

*(t = p, p += 1, t) = *(t = q, q += 1, t); ■

Both the assignment operators (+=, -=) and the increment and decrement op- erators (++, --) do “the right thing” when applied to pointers in C (assuming those pointers point into an array). If p points to element i of an array, where each element occupies n bytes (including any bytes required for alignment, as discussed in Section C 5.1), then p += 3 points to element i + 3, 3n bytes later in memory. We will discuss pointers and arrays in C in more detail in Section 8.5.1.

Multiway Assignment

We have already seen that the right associativity of assignment (in languages that allow assignment in expressions) allows one to write things like a = b = c. In EXAMPLE 6.25

Simple multiway assignment several languages, including Clu, ML, Perl, Python, and Ruby, it is also possible to write

a, b = c, d;

Here the comma in the right-hand side is not the sequencing operator of C. Rather, it serves to deﬁne an expression, or tuple, consisting of multiple r-values. The comma operator on the left-hand side produces a tuple of l-values. The effect of the assignment is to copy c into a and d into b.4 ■ While we could just as easily have written EXAMPLE 6.26

Advantages of multiway assignment

4 The syntax shown here is for Perl, Python, and Ruby. Clu uses := for assignment. ML requires parentheses around each tuple.

a = c; b = d;

the multiway (tuple) assignment allows us to write things like

```
a, b = b, a;
(* swap a and b *)
```

which would otherwise require auxiliary variables. Moreover, multiway assign- ment allows functions to return tuples, as well as single values:

a, b, c = foo(d, e, f);

This notation eliminates the asymmetry (nonorthogonality) of functions in most programming languages, which allow an arbitrary number of arguments, but only a single return. ■

3CHECK YOUR UNDERSTANDING 1. Name eight major categories of control-ﬂow mechanisms. 2. What distinguishes operators from other sorts of functions?

  3.
  Explain the difference between preﬁx, inﬁx, and postﬁx notation. What is
  Cambridge Polish notation? Name two programming languages that use post-
  ﬁx notation.
  4.
  Why don’t issues of associativity and precedence arise in Postscript or Forth?

  5.
  What does it mean for an expression to be referentially transparent?
  6.
  What is the difference between a value model of variables and a reference
  model of variables? Why is the distinction important?
  7.
  What is an l-value? An r-value?

  8.
  Why is the distinction between mutable and immutable values important in
  the implementation of a language with a reference model of variables?
  9.
  Deﬁne orthogonality in the context of programming language design.
* What is the difference between a statement and an expression? What does it
  mean for a language to be expression-oriented?
* What are the advantages of updating a variable with an assignment operator,
  rather than with a regular assignment in which the variable appears on both
  the left- and right-hand sides?

6.1.3 Initialization

Because they already provide a construct (the assignment statement) to set the value of a variable, imperative languages do not always provide a means of spec- ifying an initial value for a variable in its declaration. There are several reasons, however, why such initial values may be useful:

* As suggested in Figure 3.3, a static variable that is local to a subroutine needs
  an initial value in order to be useful.
* For any statically allocated variable, an initial value that is speciﬁed in the dec-
  laration can be preallocated in global memory by the compiler, avoiding the
  cost of assigning an initial value at run time.
* Accidental use of an uninitialized variable is one of the most common pro-
  gramming errors. One of the easiest ways to prevent such errors (or at least
  ensure that erroneous behavior is repeatable) is to give every variable a value
  when it is ﬁrst declared.

Most languages allow variables of built-in types to be initialized in their dec- larations. A more complete and orthogonal approach to initialization requires a notation for aggregates: built-up structured values of user-deﬁned composite types. Aggregates can be found in several languages, including C, C++, Ada, For- tran 90, and ML; we will discuss them further in Section 7.1.3. It should be emphasized that initialization saves time only for variables that are statically allocated. Variables allocated in the stack or heap at run time must be initialized at run time.5 It is also worth noting that the problem of using an uninitialized variable occurs not only after elaboration, but also as a result of any operation that destroys a variable’s value without providing a new one. Two of the most common such operations are explicit deallocation of an object referenced through a pointer and modiﬁcation of the tag of a variant record. We will consider these operations further in Sections 8.5 and C 8.1.3, respectively. If a variable is not given an initial value explicitly in its declaration, the lan- guage may specify a default value. In C, for example, statically allocated variables for which the programmer does not provide an initial value are guaranteed to be represented in memory as if they had been initialized to zero. For most types on most machines, this is a string of zero bits, allowing the language implementation to exploit the fact that most operating systems (for security reasons) ﬁll newly allocated memory with zeros. Zero-initialization applies recursively to the sub- components of variables of user-deﬁned composite types. Java and C# provide a similar guarantee for the ﬁelds of all class-typed objects, not just those that are statically allocated. Most scripting languages provide a default initial value for all variables, of all types, regardless of scope or lifetime.

5 For variables that are accessed indirectly (e.g., in languages that employ a reference model of variables), a compiler can often reduce the cost of initializing a stack or heap variable by placing the initial value in static memory, and only creating the pointer to it at elaboration time.

Dynamic Checks

Instead of giving every uninitialized variable a default value, a language or imple- mentation can choose to deﬁne the use of an uninitialized variable as a dynamic semantic error, and can catch these errors at run time. The advantage of the se- mantic checks is that they will often identify a program bug that is masked or made more subtle by the presence of a default value. With appropriate hardware support, uninitialized variable checks can even be as cheap as default values, at least for certain types. In particular, a compiler that relies on the IEEE standard for ﬂoating-point arithmetic can ﬁll uninitialized ﬂoating-point numbers with a signaling NaN value, as discussed in Section C 5.2.2. Any attempt to use such a value in a computation will result in a hardware interrupt, which the language implementation may catch (with a little help from the operating system), and use to trigger a semantic error message. For most types on most machines, unfortunately, the costs of catching all uses of an uninitialized variable at run time are considerably higher. If every possible bit pattern of the variable’s representation in memory designates some legitimate value (and this is often the case), then extra space must be allocated somewhere to hold an initialized/uninitialized ﬂag. This ﬂag must be set to “uninitialized” at elaboration time and to “initialized” at assignment time. It must also be checked (by extra code) at every use, or at least at every use that the code improver is unable to prove is redundant.

Deﬁnite Assignment

For local variables of methods, Java and C# deﬁne a notion of deﬁnite assignment that precludes the use of uninitialized variables. This notion is based on the con- trol ﬂow of the program, and can be statically checked by the compiler. Roughly EXAMPLE 6.27

Programs outlawed by deﬁnite assignment speaking, every possible control path to an expression must assign a value to every variable in that expression. This is a conservative rule; it can sometimes prohibit programs that would never actually use an uninitialized variable. In Java:

```
int i;
int j = 3;
...
if (j > 0) {
i = 2;
}
...
// no assignments to j in here
if (j > 0) {
System.out.println(i);
// error: "i might not have been initialized"
}
```

While a human being might reason that i will be used only when it has previously been given a value, such determinations are undecidable in the general case, and the compiler does not attempt them. ■

Constructors

Many object-oriented languages (Java and C# among them) allow the program- mer to deﬁne types for which initialization of dynamically allocated variables occurs automatically, even when no initial value is speciﬁed in the declaration. Some—notably C++—also distinguish carefully between initialization and as- signment. Initialization is interpreted as a call to a constructor function for the variable’s type, with the initial value as an argument. In the absence of coercion, assignment is interpreted as a call to the type’s assignment operator or, if none has been deﬁned, as a simple bit-wise copy of the value on the assignment’s right- hand side. The distinction between initialization and assignment is particularly important for user-deﬁned abstract data types that perform their own storage management. A typical example occurs in variable-length character strings. An assignment to such a string must generally deallocate the space consumed by the old value of the string before allocating space for the new value. An initialization of the string must simply allocate space. Initialization with a nontrivial value is generally cheaper than default initialization followed by assignment, because it avoids deallocation of the space allocated for the default value. We will return to this issue in Section 10.3.2. Neither Java nor C# distinguishes between initialization and assignment: an initial value can be given in a declaration, but this is the same as an immedi- ate subsequent assignment. Java uses a reference model for all variables of user- deﬁned object types, and provides for automatic storage reclamation, so assign- ment never copies values. C# allows the programmer to specify a value model when desired (in which case assignment does copy values), but otherwise mirrors Java.

6.1.4 Ordering within Expressions

While precedence and associativity rules deﬁne the order in which binary inﬁx operators are applied within an expression, they do not specify the order in which the operands of a given operator are evaluated. For example, in the expression EXAMPLE 6.28

Indeterminate ordering a - f(b) - c * d

we know from associativity that f(b) will be subtracted from a before perform- ing the second subtraction, and we know from precedence that the right operand of that second subtraction will be the result of c * d, rather than merely c, but without additional information we do not know whether a - f(b) will be evalu- ated before or after c * d. Similarly, in a subroutine call with multiple arguments

f(a, g(b), h(c))

we do not know the order in which the arguments will be evaluated. ■ There are two main reasons why the order can be important:

* Side effects: If f(b) may modify d, then the value of a - f(b) - c * d will
  EXAMPLE 6.29

A value that depends on ordering depend on whether the ﬁrst subtraction or the multiplication is performed ﬁrst. Similarly, if g(b) may modify a and/or c, then the values passed to f(a, g(b), h(c)) will depend on the order in which the arguments are eval- uated. ■ 2. Code improvement: The order of evaluation of subexpressions has an impact on both register allocation and instruction scheduling. In the expression a * b EXAMPLE 6.30

An optimization that depends on ordering + f(c), it is probably desirable to call f before evaluating a * b, because the product, if calculated ﬁrst, would need to be saved during the call to f, and f might want to use all the registers in which it might easily be saved. In a similar vein, consider the sequence

```
a := B[i];
c := a * 2 + d * 3;
```

On an in-order processor, it is probably desirable to evaluate d * 3 before eval- uating a * 2, because the previous statement, a := B[i], will need to load a value from memory. Because loads are slow, if the processor attempts to use the value of a in the next instruction (or even the next few instructions on many machines), it will have to wait. If it does something unrelated instead (i.e., evaluate d * 3), then the load can proceed in parallel with other compu- tation. ■

Because of the importance of code improvement, most language manuals say that the order of evaluation of operands and arguments is undeﬁned. (Java and C# are unusual in this regard: they require left-to-right evaluation.) In the ab- sence of an enforced order, the compiler can choose whatever order is likely to result in faster code.

DESIGN & IMPLEMENTATION

6.2 Safety versus performance A recurring theme in any comparison between C++ and Java is the latter’s will- ingness to accept additional run-time cost in order to obtain cleaner semantics or increased reliability. Deﬁnite assignment is one example: it may force the programmer to perform “unnecessary” initializations on certain code paths, but in so doing it avoids the many subtle errors that can arise from missing initialization in other languages. Similarly, the Java speciﬁcation mandates au- tomatic garbage collection, and its reference model of user-deﬁnedtypes forces most objects to be allocated in the heap. As we shall see in future chapters, Java also requires both dynamic binding of all method invocations and run-time checks for out-of-bounds array references, type clashes, and other dynamic semantic errors. Clever compilers can reduce or eliminate the cost of these requirements in certain common cases, but for the most part the Java design reﬂects an evolutionary shift away from performance as the overriding design goal.

Applying Mathematical Identities

Some language implementations (e.g., for dialects of Fortran) allow the compiler to rearrange expressions involving operators whose mathematical abstractions are commutative, associative, and/or distributive, in order to generate faster code. Consider the following Fortran fragment: EXAMPLE 6.31

Optimization and mathematical “laws” a = b + c d = c + e + b

Some compilers will rearrange this as

```
a = b + c
d = b + c + e
```

They can then recognize the common subexpression in the ﬁrst and second state- ments, and generate code equivalent to

```
a = b + c
d = a + e
```

Similarly,

```
a = b/c/d
e = f/d/c
```

may be rearranged as

t = c * d a = b/t e = f/t ■

Unfortunately, while mathematical arithmetic obeys a variety of commuta- tive, associative, and distributive laws, computer arithmetic is not as orderly. The

DESIGN & IMPLEMENTATION

6.3 Evaluation order Expression evaluation presents a difﬁcult tradeoff between semantics and im- plementation. To limit surprises, most language deﬁnitions require the com- piler, if it ever reorders expressions, to respect any ordering imposed by paren- theses. The programmer can therefore use parentheses to prevent the applica- tion of arithmetic “identities” when desired. No similar guarantee exists with respect to the order of evaluation of operands and arguments. It is therefore unwise to write expressions in which a side effect of evaluating one operand or argument can affect the value of another. As we shall see in Section 6.3, some languages, notably Euclid and Turing, outlaw such side effects.

problem is that numbers in a computer are of limited precision. Suppose a, b, EXAMPLE 6.32

Overﬂow and arithmetic “identities” and c are all integers between two billion and three billion. With 32-bit arith- metic, the expression b - c + d can be evaluated safely left-to-right (232 is a little less than 4.3 billion). If the compiler attempts to reorganize this expression as b + d - c, however (e.g., in order to delay its use of c), then arithmetic overﬂow will occur. Despite our intuition from math, this reorganization is unsafe. ■ Many languages, including Pascal and most of its descendants, provide dy- namic semantic checks to detect arithmetic overﬂow. In some implementations these checks can be disabled to eliminate their run-time overhead. In C and C++, the effect of arithmetic overﬂow is implementation-dependent. In Java, it is well deﬁned: the language deﬁnition speciﬁes the size of all numeric types, and re- quires two’s complement integer and IEEE ﬂoating-point arithmetic. In C#, the programmer can explicitly request the presence or absence of checks by tagging an expression or statement with the checked or unchecked keyword. In a com- pletely different vein, Scheme, Common Lisp, and several scripting languages place no a priori limit on the size of integers; space is allocated to hold extra-large values on demand. Even in the absence of overﬂow, the limited precision of ﬂoating-point arith- metic can cause different arrangements of the “same” expression to produce sig- niﬁcantly different results, invisibly. Single-precision IEEE ﬂoating-point num- EXAMPLE 6.33

Reordering and numerical stability bers devote one bit to the sign, eight bits to the exponent (power of two), and 23 bits to the mantissa. Under this representation, a + b is guaranteed to result in a loss of information if | log2(a/b)| > 23. Thus if b = -c, then a + b + c may appear to be zero, instead of a, if the magnitude of a is small, while the magnitudes of b and c are large. In a similar vein, a number like 0.1 cannot be represented precisely, because its binary representation is a “repeating decimal”:

0.0001001001.... For certain values of x, (0.1 + x) * 10.0 and 1.0 + (x * 10.0) can differ by as much as 25%, even when 0.1 and x are of the same mag- nitude. ■

6.1.5 Short-Circuit Evaluation

Boolean expressions provide a special and important opportunity for code im- provement and increased readability. Consider the expression (a < b) and EXAMPLE 6.34

Short-circuited expressions (b < c). If a is greater than b, there is really no point in checking to see whether b is less than c; we know the overall expression must be false. Similarly, in the expression (a > b) or (b > c), if a is indeed greater than b there is no point in checking to see whether b is greater than c; we know the overall expression must be true. A compiler that performs short-circuit evaluation of Boolean expressions will generate code that skips the second half of both of these computations when the overall value can be determined from the ﬁrst half. ■ Short-circuit evaluation can save signiﬁcant amounts of time in certain situa- EXAMPLE 6.35

Saving time with short-circuiting tions:

if (very_unlikely_condition && very_expensive_function()) ... ■

But time is not the only consideration, or even the most important. Short- EXAMPLE 6.36

Short-circuit pointer chasing circuiting changes the semantics of Boolean expressions. In C, for example, one can use the following code to search for an element in a list:

```
p = my_list;
while (p && p->key != val)
p = p->next;
```

C short-circuits its && and || operators, and uses zero for both null and false, so p->key will be accessed if and only if p is non-null. The syntactically similar code in Pascal does not work, because Pascal does not short-circuit and and or:

```
p := my_list;
while (p <> nil) and (p^.key <> val) do
(* ouch! *)
p := p^.next;
```

Here both of the <> relations will be evaluated before and-ing their results to- gether. At the end of an unsuccessful search, p will be nil, and the attempt to access p^.key will be a run-time (dynamic semantic) error, which the compiler may or may not have generated code to catch. To avoid this situation, the Pascal programmer must introduce an auxiliary Boolean variable and an extra level of nesting:

p := my_list; still_searching := true; while still_searching do if p = nil then still_searching := false else if p^.key = val then still_searching := false else p := p^.next; ■

Short-circuit evaluation can also be used to avoid out-of-bound subscripts: EXAMPLE 6.37

Short-circuiting and other errors const int MAX = 10; int A[MAX]; /* indices from 0 to 9 */ ... if (i >= 0 && i < MAX && A[i] > foo) ...

division by zero:

if (d == 0 || n/d < threshold) ...

and various other errors. ■

There are situations, however, in which short circuiting may not be appropri- ate. In particular, if expressions E1 and E2 both have side effects, we may want the conjunction E1 and E2 (and likewise E1 or E2) to evaluate both halves (Ex- ercise 6.12). To accommodate such situations while still allowing short-circuit evaluation in scenarios like those of Examples 6.35 through 6.37, a few languages include both regular and short-circuit Boolean operators. In Ada, for example, EXAMPLE 6.38

Optional short-circuiting the regular Boolean operators are and and or; the short-circuit versions are the two-word combinations and then and or else:

```
found_it := p /= null and then p.key = val;
...
if d = 0.0 or else n/d < threshold then ...
```

(Ada uses /= for “not equal.”) In C, the bit-wise & and | operators can be used as non-short-circuiting alternatives to && and || when their arguments are logical (zero or one) values. ■ If we think of and and or as binary operators, short circuiting can be consid- ered an example of delayed or lazy evaluation: the operands are “passed” uneval- uated. Internally, the operator evaluates the ﬁrst operand in any case, the second only when needed. In a language like Algol 68, which allows arbitrary control ﬂow constructs to be used inside expressions, conditional evaluation can be speciﬁed explicitly with if... then ... else; see Exercise 6.13. When used to determine the ﬂow of control in a selection or iteration con- struct, short-circuit Boolean expressions do not really have to calculate a Boolean value; they simply have to ensure that control takes the proper path in any given situation. We will look more closely at the generation of code for short-circuit expressions in Section 6.4.1.

3CHECK YOUR UNDERSTANDING 12. Given the ability to assign a value into a variable, why is it useful to be able to specify an initial value?

* What are aggregates? Why are they useful?
* Explain the notion of deﬁnite assignment in Java and C#.

* Why is it generally expensive to catch all uses of uninitialized variables at run
  time?

* Why is it impossible to catch all uses of uninitialized variables at compile time?
* Why do most languages leave unspeciﬁed the order in which the arguments
  of an operator or function are evaluated?
* What is short-circuit Boolean evaluation? Why is it useful?

6.2 Structured and Unstructured Flow

Control ﬂow in assembly languages is achieved by means of conditional and un- conditional jumps (branches). Early versions of Fortran mimicked the low-level EXAMPLE 6.39

Control ﬂow with gotos in Fortran approach by relying heavily on goto statements for most nonprocedural control ﬂow:

```
if (A .lt. B) goto 10
! ".lt." means "<"
...
10
```

The 10 on the bottom line is a statement label. Goto statements also featured prominently in other early imperative languages. ■ Beginning in the late 1960s, largely in response to an article by Edsger Dijk- stra [Dij68b],6 language designers hotly debated the merits and evils of gotos. It seems fair to say the detractors won. Ada and C# allow gotos only in limited contexts. Modula (1, 2, and 3), Clu, Eiffel, Java, and most of the scripting lan- guages do not allow them at all. Fortran 90 and C++ allow them primarily for compatibility with their predecessor languages. (Java reserves the token goto as a keyword, to make it easier for a Java compiler to produce good error messages when a programmer uses a C++ goto by mistake.) The abandonment of gotos was part of a larger “revolution” in software en- gineering known as structured programming. Structured programming was the “hot trend” of the 1970s, in much the same way that object-oriented program- ming was the trend of the 1990s. Structured programming emphasizes top-down design (i.e., progressive reﬁnement), modularization of code, structured types (records, sets, pointers, multidimensional arrays), descriptive variable and con- stant names, and extensive commenting conventions. The developers of struc- tured programming were able to demonstrate that within a subroutine, almost any well-designed imperative algorithm can be elegantly expressed with only se- quencing, selection, and iteration. Instead of labels, structured languages rely on the boundaries of lexically nested constructs as the targets of branching control. Many of the structured control-ﬂow constructs familiar to modern program- mers were pioneered by Algol 60. These include the if... then ... else con- struct and both enumeration (for) and logically (while) controlled loops. The modern case (switch) statement was introduced by Wirth and Hoare in Al- gol W [WH66] as an alternative to the more unstructured computed goto and switch constructs of Fortran and Algol 60, respectively. (The switch statement of C bears a closer resemblance to the Algol W case statement than to the Algol 60 switch.)

6 Edsger W. Dijkstra (1930–2002) developed much of the logical foundation of our modern un- derstanding of concurrency. He was also responsible, among many other contributions, for the semaphores of Section 13.3.5 and for much of the practical development of structured program- ming. He received the ACM Turing Award in 1972.

6.2.1 Structured Alternatives to goto

Once the principal structured constructs had been deﬁned, most of the contro- versy surrounding gotos revolved around a small number of special cases, each of which was eventually addressed in structured ways. Where once a goto might have been used to jump to the end of the current subroutine, most modern lan- guages provide an explicit return statement. Where once a goto might have been used to escape from the middle of a loop, most modern languages provide a break or exit statement for this purpose. (Some languages also provide a state- ment that will skip the remainder of the current iteration only: continue in C; cycle in Fortran 90; next in Perl.) More signiﬁcantly, several languages allow a program to return from a nested chain of subroutine calls in a single opera- tion, and many provide a way to raise an exception that propagates out to some surrounding context. Both of these capabilities might once have been attempted with (nonlocal) gotos.

Multilevel Returns

Returns and (local) gotos allow control to return from the current subroutine. On occasion it may make sense to return from a surrounding routine. Imagine, for EXAMPLE 6.40

Escaping a nested subroutine example, that we are searching for an item matching some desired pattern within a collection of ﬁles. The search routine might invoke several nested routines, or a single routine multiple times, once for each place in which to search. In such a situation certain historic languages, including Algol 60, PL/I, and Pascal, permit- ted a goto to branch to a lexically visible label outside the current subroutine:

```
function search(key : string) : string;
var rtn : string;
...
procedure search_file(fname : string);
...
begin
...
for ... (* iterate over lines *)
...
if found(key, line) then begin
rtn := line;
goto 100;
end;
...
end;
...
begin (* search *)
...
```

for ... (* iterate over files *) ... search_file(fname); ... 100: return rtn; end; ■

In the event of a nonlocal goto, the language implementation must guarantee to repair the run-time stack of subroutine call information. This repair operation is known as unwinding. It requires not only that the implementation deallocate the stack frames of any subroutines from which we have escaped, but also that it perform any bookkeeping operations, such as restoration of register contents, that would have been performed when returning from those routines. As a more structured alternative to the nonlocal goto, Common Lisp provides a return-from statement that names the lexically surrounding function or block from which to return, and also supplies a return value (eliminating the need for the artiﬁcial rtn variable in Example 6.40). But what if search_file were not nested inside of search? We might, for example, wish to call it from routines that search ﬁles in different orders. Algol 60, Algol 68, and PL/I allowed labels to be passed as parameters, so a dynamically nested subroutine could perform a goto to a caller-deﬁned location. Common EXAMPLE 6.41

Structured nonlocal transfers Lisp again provides a more structured alternative, also available in Ruby. In either language an expression can be surrounded with a catch block, whose value can be provided by any dynamically nested routine that executes a matching throw. In Ruby we might write

```
def searchFile(fname, pattern)
file = File.open(fname)
file.each {|line|
throw :found, line if line =~ /#{pattern}/
}
end
```

```
match = catch :found do
searchFile("f1", key)
searchFile("f2", key)
searchFile("f3", key)
"not found\n"
# default value for catch,
end
# if control gets this far
print match
```

Here the throw expression speciﬁes a tag, which must appear in a matching catch, together with a value (line) to be returned as the value of the catch. (The if clause attached to the throw performs a regular-expression pattern match, looking for pattern within line. We will consider pattern matching in more detail in Section 14.4.2.) ■

Errors and Other Exceptions

The notion of a multilevel return assumes that the callee knows what the caller expects, and can return an appropriate value. In a related and arguably more common situation, a deeply nested block or subroutine may discover that it is unable to proceed with its usual function, and moreover lacks the contextual in- formation it would need to recover in any graceful way. Eiffel formalizes this notion by saying that every software component has a contract—a speciﬁcation of the function it performs. A component that is unable to fulﬁll its contract is said to fail. Rather than return in the normal way, it must arrange for control to “back out” to some context in which the program is able to recover. Conditions that require a program to “back out” are usually called exceptions. We mentioned an example in Section C 2.3.5, where we considered phrase-level recovery from syntax errors in a recursive descent parser. The most straightforward but generally least satisfactory way to cope with ex- EXAMPLE 6.42

Error checking with status codes ceptions is to use auxiliary Boolean variables within a subroutine (if still_ok then ...) and to return status codes from calls:

status := my_proc(args); if status = ok then ... ■

The auxiliary Booleans can be eliminated by using a nonlocal goto or multilevel return, but the caller to which we return must still inspect status codes explic- itly. As a structured alternative, many modern languages provide an exception- handling mechanism for convenient, nonlocal recovery from exceptions. We will discuss exception handling in more detail in Section 9.4. Typically the program- mer appends a block of code called a handler to any computation in which an exception may arise. The job of the handler is to take whatever remedial action is required to recover from the exception. If the protected computation completes in the normal fashion, execution of the handler is skipped. Multilevel returns and structured exceptions have strong similarities. Both in- volve a control transfer from some inner, nested context back to an outer context, unwinding the stack on the way. The distinction lies in where the computing oc- curs. In a multilevel return the inner context has all the information it needs. It completes its computation, generating a return value if appropriate, and transfers to the outer context in a way that requires no post-processing. At an exception, by contrast, the inner context cannot complete its work—it cannot fulﬁll its con- tract. It performs an “abnormal” return, triggering execution of the handler. Common Lisp and Ruby provide mechanisms for both multilevel returns and exceptions, but this dual support is relatively rare. Most languages support only exceptions; programmers implement multilevel returns by writing a trivial han- dler. In an unfortunate overloading of terminology, the names catch and throw, which Common Lisp and Ruby use for multilevel returns, are used for exceptions in several other languages.

6.2.2 Continuations

The notion of nonlocal gotos that unwind the stack can be generalized by deﬁn- ing what are known as continuations. In low-level terms, a continuation con- sists of a code address, a referencing environment that should be established (or restored) when jumping to that address, and a reference to another continua- tion that represents what to do in the event of a subsequent subroutine return. (The chain of return continuations constitutes a backtrace of the run-time stack.) In higher-level terms, a continuation is an abstraction that captures a context in which execution might continue. Continuations are fundamental to deno- tational semantics. They also appear as ﬁrst-class values in several programming languages (notably Scheme and Ruby), allowing the programmer to deﬁne new control-ﬂow constructs. Continuation support in Scheme takes the form of a function named call- with-current-continuation, often abbreviated call/cc. This function takes a single argument f , which is itself a function of one argument. Call/cc calls f , passing as argument a continuation c that captures the current program counter, referencing environment, and stack backtrace. The continuation is implemented as a closure, indistinguishable from the closures used to represent subroutines passed as parameters. At any point in the future, f can call c, passing it a value, v. The call will “return” v into c’s captured context, as if it had been returned by the original call to call/cc. Ruby support is similar: EXAMPLE 6.43

A simple Ruby continuation def foo(i, c) printf "start %d; ", i if i < 3 then foo(i+1, c) else c.call(i) end printf "end %d; ", i end

```
v = callcc { |d| foo(1, d) }
printf "got %d\n", v
```

Here the parameter to callcc is a block—roughly, a lambda expression. The block’s parameter is the continuation c, which its body passes, together with the

DESIGN & IMPLEMENTATION

6.4 Cleaning up continuations The implementation of continuations in Scheme and Ruby is surprisingly straightforward. Because local variables have unlimited extent in both lan- guages, activation records must in general be allocated on the heap. As a re- sult, explicit deallocation of frames in the current context is neither required nor appropriate when jumping through a continuation: if those frames are no longer accessible, they will eventually be reclaimed by the standard garbage collector (more on this in Section 8.5.3).

number 1, to subroutine foo. The subroutine then calls itself twice recursively before executing c.call(i). Finally, the call method jumps into the context captured by c, making i (that is, 3) appear to have been returned by callcc. The ﬁnal program output is start 1; start 2; start 3; got 3. ■ In this simple example, the jump into the continuation behaved much as an exception would, popping out of a series of nested calls. But continuations can do much more. Like other closures, they can be saved in variables, returned from EXAMPLE 6.44

Continuation reuse and unlimited extent subroutines, or called repeatedly, even after control has returned out of the con- text in which they were created (this means that they require unlimited extent; see Section 3.6). Consider the following more subtle example:

```
def here
return callcc { |a| return a }
end
```

```
def bar(i)
printf "start %d; ", i
b = if i < 3 then bar(i+1) else here end
printf "end %d; ", i
return b
end
```

```
n = 3
c = bar(1)
n -= 1
puts
# print newline
if n > 0 then c.call(c) end
puts "done"
```

This code performs three nested calls to bar, returning a continuation created by function here in the middle of the innermost call. Using that continuation, we can jump back into the nested calls of bar—in fact, we can do so repeatedly. Note that while c’s captured referencing environment remains the same each time, the value of n can change. The ﬁnal program output is

start 1; start 2; start 3; end 3; end 2; end 1; end 3; end 2; end 1; end 3; end 2; end 1; done ■

Call/cc sufﬁces to build a wide variety of control abstractions, including gotos, midloop exits, multilevel returns, exceptions, iterators (Section 6.5.3), call-by-name parameters (Section 9.3.1), and coroutines (Section 9.5). It even subsumes the notion of returning from a subroutine, though it seldom replaces it in practice. Used in a disciplined way, continuations make a language surpris- ingly extensible. At the same time, they allow the undisciplined programmer to construct completely inscrutable programs.

6.3 Sequencing

Like assignment, sequencing is central to imperative programming. It is the prin- cipal means of controlling the order in which side effects (e.g., assignments) oc- cur: when one statement follows another in the program text, the ﬁrst statement executes before the second. In most imperative languages, lists of statements can be enclosed with begin... end or { ... } delimiters and then used in any context in which a single statement is expected. Such a delimited list is usually called a compound statement. A compound statement optionally preceded by a set of declarations is sometimes called a block. In languages like Algol 68, which blur or eliminate the distinction between statements and expressions, the value of a statement (expression) list is the value of its ﬁnal element. In Common Lisp, the programmer can choose to return the value of the ﬁrst element, the second, or the last. Of course, sequencing is a useless operation unless the subexpressions that do not play a part in the return value have side effects. The various sequencing constructs in Lisp are used only in program fragments that do not conform to a purely functional programming model. Even in imperative languages, there is debate as to the value of certain kinds of side effects. In Euclid and Turing, for example, functions (i.e., subroutines that return values, and that therefore can appear within expressions) are not permitted to have side effects. Among other things, side-effect freedom ensures that a Euclid or Turing function, like its counterpart in mathematics, is always idempotent: if called repeatedly with the same set of arguments, it will always return the same value, and the number of consecutive calls (after the ﬁrst) will not affect the results of subsequent execution. In addition, side-effect freedom for functions means that the value of a subexpression will never depend on whether that subexpression is evaluated before or after calling a function in some other subexpression. These properties make it easier for a programmer or theorem-proving system to reason about program behavior. They also simplify code improvement, for example by permitting the safe rearrangement of expressions. Unfortunately, there are some situations in which side effects in functions are EXAMPLE 6.45

Side effects in a random number generator highly desirable. We saw one example in the label name function of Figure 3.3. Another arises in the typical interface to a pseudorandom number generator:

procedure srand(seed : integer) –– Initialize internal tables. –– The pseudorandom generator will return a different –– sequence of values for each different value of seed.

function rand() : integer –– No arguments; returns a new “random” number.

Obviously rand needs to have a side effect, so that it will return a different value each time it is called. One could always recast it as a procedure with a reference parameter:

procedure rand(ref n : integer)

but most programmers would ﬁnd this less appealing. Ada strikes a compromise: it allows side effects in functions in the form of changes to static or global vari- ables, but does not allow a function to modify its parameters. ■

6.4 Selection

Selection statements in most imperative languages employ some variant of the EXAMPLE 6.46

Selection in Algol 60 if... then ... else notation introduced in Algol 60:

if condition then statement else if condition then statement else if condition then statement ... else statement ■

As we saw in Section 2.3.2, languages differ in the details of the syntax. In Algol 60 and Pascal both the then clause and the else clause were deﬁned to contain a single statement (this could of course be a begin... end compound statement). To avoid grammatical ambiguity, Algol 60 required that the statement after the then begin with something other than if (begin is ﬁne). Pascal eliminated this restriction in favor of a “disambiguating rule” that associated an else with the closest unmatched then. Algol 68, Fortran 77, and more modern languages avoid the ambiguity by allowing a statement list to follow either then or else, with a terminating keyword at the end of the construct. To keep terminators from piling up at the end of nested if statements, most EXAMPLE 6.47

elsif/elif languages with terminators provide a special elsif or elif keyword. In Ruby, one writes

if a == b then ... elsif a == c then ... elsif a == d then ... else ... end ■

In Lisp, the equivalent construct is EXAMPLE 6.48

cond in Lisp (cond ((= A B) (...))

```
((= A C)
(...))
((= A D)
(...))
(T
(...)))
```

Here cond takes as arguments a sequence of pairs. In each pair the ﬁrst ele- ment is a condition; the second is an expression to be returned as the value of the overall construct if the condition evaluates to T (T means “true” in most Lisp dialects). ■

6.4.1 Short-Circuited Conditions

While the condition in an if... then ... else statement is a Boolean expression, there is usually no need for evaluation of that expression to result in a Boolean value in a register. Most machines provide conditional branch instructions that capture simple comparisons. Put another way, the purpose of the Boolean expres- sion in a selection statement is not to compute a value to be stored, but to cause control to branch to various locations. This observation allows us to generate particularly efﬁcient code (called jump code) for expressions that are amenable to the short-circuit evaluation of Section 6.1.5. Jump code is applicable not only to selection statements such as if... then ... else, but to logically controlled loops as well; we will consider the latter in Section 6.5.5. In the usual process of code generation, a synthesized attribute of the root of an expression subtree acquires the name of a register into which the value of the expression will be computed at run time. The surrounding context then uses this register name when generating code that uses the expression. In jump code, inherited attributes of the root inform it of the addresses to which control should branch if the expression is true or false, respectively. Suppose, for example, that we are generating code for the following source: EXAMPLE 6.49

Code generation for a Boolean condition if ((A > B) and (C > D)) or (E ̸= F) then then clause else else clause

In a language without short-circuit evaluation, the output code would look some- thing like this:

r1 := A –– load r2 := B r1 := r1 > r2 r2 := C r3 := D

r2 := r2 > r3 r1 := r1 & r2 r2 := E r3 := F r2 := r2 ̸= r3 r1 := r1 | r2 if r1 = 0 goto L2 L1: then clause –– (label not actually used) goto L3 L2: else clause L3:

The root of the subtree for ((A > B) and (C > D)) or (E ̸= F) would name r1 as the register containing the expression value. ■ In jump code, by contrast, the inherited attributes of the condition’s root EXAMPLE 6.50

Code generation for short-circuiting would indicate that control should “fall through” to L1 if the condition is true, or branch to L2 if the condition is false. Output code would then look something like this:

r1 := A r2 := B if r1 <= r2 goto L4 r1 := C r2 := D if r1 > r2 goto L1 L4: r1 := E r2 := F if r1 = r2 goto L2 L1: then clause goto L3 L2: else clause L3:

Here the value of the Boolean condition is never explicitly placed into a register. Rather it is implicit in the ﬂow of control. Moreover for most values of A, B, C, D, and E, the execution path through the jump code is shorter and therefore faster (assuming good branch prediction) than the straight-line code that calculates the value of every subexpression. ■

DESIGN & IMPLEMENTATION

6.5 Short-circuit evaluation Short-circuit evaluation is one of those happy cases in programming language design where a clever language feature yields both more useful semantics and a faster implementation than existing alternatives. Other at least arguable exam- ples include case statements, local scopes for for loop indices (Section 6.5.1), and Ada-style parameter modes (Section 9.3.1).

If the value of a short-circuited expression is needed explicitly, it can of course EXAMPLE 6.51

Short-circuit creation of a Boolean value be generated, while still using jump code for efﬁciency. The Ada fragment

found_it := p /= null and then p.key = val;

is equivalent to

```
if p /= null and then p.key = val then
found_it := true;
else
found_it := false;
end if;
```

and can be translated as

r1 := p if r1 = 0 goto L1 r2 := r1→key if r2 ̸= val goto L1 r1 := 1 goto L2 L1: r1 := 0 L2: found it := r1

The astute reader will notice that the ﬁrst goto L1 can be replaced by goto L2, since r1 already contains a zero in this case. The code improvement phase of the compiler will notice this also, and make the change. It is easier to ﬁx this sort of thing in the code improver than it is to generate the better version of the code in the ﬁrst place. The code improver has to be able to recognize jumps to redundant instructions for other reasons anyway; there is no point in building special cases into the short-circuit evaluation routines. ■

6.4.2 Case/Switch Statements

The case statements of Algol W and its descendants provide alternative syntax EXAMPLE 6.52

case statements and nested ifs for a special case of nested if... then ... else. When each condition compares the same expression to a different compile-time constant, then the following code (written here in Ada)

i := ... -- potentially complicated expression if i = 1 then clause A elsif i = 2 or i = 7 then clause B elsif i in 3..5 then clause C elsif i = 10 then clause D else clause E end if;

can be rewritten as

case ... -- potentially complicated expression is when 1 => clause A when 2 | 7 => clause B when 3..5 => clause C when 10 => clause D when others => clause E end case;

The elided code fragments (clause A, clause B, etc.) after the arrows are called the arms of the case statement. The lists of constants in front of the arrows are case statement labels. The constants in the label lists must be disjoint, and must be of a type compatible with the tested (“controlling”) expression. Most languages allow this type to be anything whose values are discrete: integers, characters, enumera- tions, and subranges of the same. C# and (recent versions of) Java allow strings as well. ■ The case statement version of the code above is certainly less verbose than the if... then ... else version, but syntactic elegance is not the principal motivation for providing a case statement in a programming language. The principal mo- tivation is to facilitate the generation of efﬁcient target code. The if... then ... EXAMPLE 6.53

Translation of nested ifs else statement is most naturally translated as follows:

r1 := . . . –– calculate controlling expression if r1 ̸= 1 goto L1 clause A goto L6 L1: if r1 = 2 goto L2 if r1 ̸= 7 goto L3 L2: clause B goto L6 L3: if r1 < 3 goto L4 if r1 > 5 goto L4 clause C goto L6 L4: if r1 ̸= 10 goto L5 clause D goto L6 L5: clause E L6: ■

Rather than test its controlling expression sequentially against a series of pos- sible values, the case statement is meant to compute an address to which it jumps in a single instruction. The general form of the anticipated target code appears EXAMPLE 6.54

Jump tables in Figure 6.3. The elided calculation at label L6 can take any of several forms. The most common of these simply indexes into an array, as shown in Figure 6.4.

![Figure 6.3 General form...](images/page_291_vector_256.png)
*Figure 6.3 General form of target code generated for a ﬁve-arm case statement.*

![Figure 6.4 Jump table...](images/page_291_vector_484.png)
*Figure 6.4 Jump table to control branching in a case statement. This code replaces the last three lines of Figure 6.3.*

The “code” at label T in that ﬁgure is in fact an array of addresses, known as a jump table. It contains one entry for each integer between the lowest and highest values, inclusive, found among the case statement labels. The code at L6 checks to make sure that the controlling expression is within the bounds of the array (if not, we should execute the others arm of the case statement). It then fetches the corresponding entry from the table and branches to it. ■

Alternative Implementations

A jump table is fast: it begins executing the correct arm of the case statement in constant time, regardless of the value of the controlling expression. It is also space efﬁcient when the overall set of case statement labels is dense and does not contain large ranges. It can consume an extraordinarily large amount of space, however, if the set of labels is nondense, or includes large value ranges. Alter- native methods to compute the address to which to branch include sequential testing, hashing, and binary search. Sequential testing (as in an if... then ... else statement) is the method of choice if the total number of case statement labels is small. It chooses an arm in O(n) time, where n is the number of labels. A hash table is attractive if the set of label values is large, but has many missing values and no large ranges. With an appropriate hash function it will choose the right arm in O(1) time. Unfortunately, a hash table, like a jump table, requires a separate entry for each possible value of the controlling tested expression, making it unsuitable for statements with large value ranges. Binary search can accommo- date ranges easily. It chooses an arm in O(log n) time. To generate good code for all possible case statements, a compiler needs to be prepared to use a variety of strategies. During compilation it can generate code for the various arms of the case statement as it ﬁnds them, while simultaneously building up an internal data structure to describe the label set. Once it has seen all the arms, it can decide which form of target code to generate. For the sake of simplicity, most compilers employ only some of the possible implementations. Some use binary search in lieu of hashing. Some generate only jump tables; oth- ers only that plus sequential testing. Users of less sophisticated compilers may need to restructure their case statements if the generated code turns out to be unexpectedly large or slow.

Syntax and Label Semantics

As with if... then ... else statements, the syntactic details of case statements vary from language to language. Different languages use different punctuation to delimit labels and arms. More signiﬁcantly, languages differ in whether they permit label ranges, whether they permit (or require) a default (others) clause, and in how they handle a value that fails to match any label at run time. In some languages (e.g., Modula), it is a dynamic semantic error for the con- trolling expression to have a value that does not appear in the label lists. Ada

DESIGN & IMPLEMENTATION

6.6 Case statements Case statements are one of the clearest examples of language design driven by implementation. Their primary reason for existence is to facilitate the gener- ation of jump tables. Ranges in label lists (not permitted in Pascal or C) may reduce efﬁciency slightly, but binary search is still dramatically faster than the equivalent series of ifs.

requires the labels to cover all possible values in the domain of the controlling expression’s type; if the type has a very large number of values, then this cover- age must be accomplished using ranges or an others clause. In some languages, notably C and Fortran 90, it is not an error for the tested expression to evaluate to a missing value. Rather, the entire construct has no effect when the value is missing.

The C switch Statement

C’s syntax for case (switch) statements (retained by C++ and Java) is unusual in several respects:

switch (... /* controlling expression */) { case 1: clause A break; case 2: case 7: clause B break; case 3: case 4: case 5: clause C break; case 10: clause D break; default: clause E break; }

Here each possible value for the tested expression must have its own label within the switch; ranges are not allowed. In fact, lists of labels are not al- lowed, but the effect of lists can be achieved by allowing a label (such as 2, 3, and 4 above) to have an empty arm that simply “falls through” into the code for the subsequent label. Because of the provision for fall-through, an explicit break statement must be used to get out of the switch at the end of an arm, rather than falling through into the next. There are rare circumstances in which the ability to EXAMPLE 6.55

Fall-through in C switch statements fall through is convenient:

letter_case = lower; switch (c) { ... case 'A' : letter_case = upper; /* FALL THROUGH! */ case 'a' : ... break; ... } ■

Most of the time, however, the need to insert a break at the end of each arm— and the compiler’s willingness to accept arms without breaks, silently—is a recipe for unexpected and difﬁcult-to-diagnose bugs. C# retains the familiar C syntax, including multiple consecutive labels, but requires every nonempty arm to end with a break, goto, continue, or return.

3CHECK YOUR UNDERSTANDING 19. List the principal uses of goto, and the structured alternatives to each.

* Explain the distinction between exceptions and multilevel returns.
* What are continuations? What other language features do they subsume?

* Why is sequencing a comparatively unimportant form of control ﬂow in Lisp?
* Explain why it may sometimes be useful for a function to have side effects.
* Describe the jump code implementation of short-circuit Boolean evaluation.

* Why do imperative languages commonly provide a case or switch statement
  in addition to if... then ... else?
* Describe three different search strategies that might be employed in the im-
  plementation of a case statement, and the circumstances in which each
  would be desirable.

* Explain the use of break to terminate the arms of a C switch statement, and
  the behavior that arises if a break is accidentally omitted.

6.5 Iteration

Iteration and recursion are the two mechanisms that allow a computer to per- form similar operations repeatedly. Without at least one of these mechanisms, the running time of a program (and hence the amount of work it can do and the amount of space it can use) would be a linear function of the size of the program text. In a very real sense, it is iteration and recursion that make computers useful for more than ﬁxed-size tasks. In this section we focus on iteration. Recursion is the subject of Section 6.6. Programmers in imperative languages tend to use iteration more than they use recursion (recursion is more common in functional languages). In most lan- guages, iteration takes the form of loops. Like the statements in a sequence, the it- erations of a loop are generally executed for their side effects: their modiﬁcations of variables. Loops come in two principal varieties, which differ in the mecha- nisms used to determine how many times to iterate. An enumeration-controlled loop is executed once for every value in a given ﬁnite set; the number of iterations is known before the ﬁrst iteration begins. A logically controlled loop is executed

until some Boolean condition (which must generally depend on values altered in the loop) changes value. Most (though not all) languages provide separate con- structs for these two varieties of loop.

6.5.1 Enumeration-Controlled Loops

Enumeration-controlled iteration originated with the do loop of Fortran I. Sim- ilar mechanisms have been adopted in some form by almost every subsequent language, but syntax and semantics vary widely. Even Fortran’s own loop has evolved considerably over time. The modern Fortran version looks something EXAMPLE 6.56

Fortran 90 do loop like this:

```
do i = 1, 10, 2
...
enddo
```

Variable i is called the index of the loop. The expressions that follow the equals sign are i’s initial value, its bound, and the step size. With the values shown here, the body of the loop (the statements between the loop header and the enddo de- limiter) will execute ﬁve times, with i set to 1, 3, ..., 9 in successive iterations. ■

Many other languages provide similar functionality. In Modula-2 one would EXAMPLE 6.57

Modula-2 for loop say

```
FOR i := first TO last BY step DO
...
END
```

By choosing different values of first, last, and step, we could arrange to iter- ate over an arbitrary arithmetic sequence of integers, namely i = first, first + step, ..., first + ⌊(last −first)/step⌋× step. ■ Following the lead of Clu, many modern languages allow enumeration- controlled loops to iterate over much more general ﬁnite sets—the nodes of a tree, for example, or the elements of a collection. We consider these more general iterators in Section 6.5.3. For the moment we focus on arithmetic sequences. For the sake of simplicity, we use the name “for loop” as a general term, even for languages that use a different keyword.

Code Generation for for Loops

Naively, the loop of Example 6.57 can be translated as EXAMPLE 6.58

Obvious translation of a for loop r1 := ﬁrst r2 := step r3 := last L1: if r1 > r3 goto L2 . . . –– loop body; use r1 for i r1 := r1 + r2 goto L1 L2: ■

A slightly better if less straightforward translation is EXAMPLE 6.59

for loop translation with test at the bottom r1 := ﬁrst r2 := step r3 := last goto L2 L1: . . . –– loop body; use r1 for i r1 := r1 + r2 L2: if r1 ≤r3 goto L1

This version is likely to be faster, because each iteration contains a single con- ditional branch, rather than a conditional branch at the top and an uncondi- tional branch at the bottom. (We will consider yet another version in Exer- cise C 17.4.) ■ Note that both of these translations employ a loop-ending test that is funda- mentally directional: as shown, they assume that all the realized values of i will be smaller than last. If the loop goes “the other direction”—that is, if first > last, and step < 0—then we will need to use the inverse test to end the loop. To allow the compiler to make the right choice, many languages restrict the generality of their arithmetic sequences. Commonly, step is required to be a compile-time constant. Ada actually limits the choices to ±1. Several languages, including both Ada and Pascal, require special syntax for loops that iterate “backward” (for i in reverse 10..1 in Ada; for i := 10 downto 1 in Pascal). Obviously, one can generate code that checks the sign of step at run time, and chooses a test accordingly. The obvious translations, however, are either time or space inefﬁcient. An arguably more attractive approach, adopted by many EXAMPLE 6.60

for loop translation with an iteration count Fortran compilers, is to precompute the number of iterations, place this iteration count in a register, decrement the register at the end of each iteration, and branch back to the top of the loop if the count is not yet zero:

r1 := ﬁrst r2 := step r3 := max(⌊(last −ﬁrst + step)/step⌋, 0) –– iteration count –– NB: this calculation may require several instructions. –– It is guaranteed to result in a value within the precision of the machine, –– but we may have to be careful to avoid overﬂow during its calculation. if r3 ≤0 goto L2 L1: . . . –– loop body; use r1 for i r1 := r1 + r2 r3 := r3 −1 if r3 > 0 goto L1 i := r1 L2: ■

The use of the iteration count avoids the need to test the sign of step within the loop. Assuming we have been suitably careful in precomputing the count, it EXAMPLE 6.61

A “gotcha” in the naive loop translation also avoids a problem we glossed over in the naive translations of Examples 6.58

and 6.59: If last is near the maximum value representable by integers on our machine, naively adding step to the ﬁnal legitimate value of i may result in arith- metic overﬂow. The “wrapped” number may then appear to be smaller (much smaller!) than last, and we may have translated perfectly good source code into an inﬁnite loop. ■ Some processors, including the Power family, PA-RISC, and most CISC ma- chines, can decrement the iteration count, test it against zero, and conditionally branch, all in a single instruction. For many loops this results in very efﬁcient code.

Semantic Complications

The astute reader may have noticed that use of an iteration count is fundamen- tally dependent on being able to predict the number of iterations before the loop begins to execute. While this prediction is possible in many languages, including Fortran and Ada, it is not possible in others, notably C and its descendants. The difference stems largely from the following question: is the for loop construct only for iteration, or is it simply meant to make enumeration easy? If the lan- guage insists on enumeration, then an iteration count works ﬁne. If enumeration is only one possible purpose for the loop—more speciﬁcally, if the number of iter- ations or the sequence of index values may change as a result of executing the ﬁrst few iterations—then we may need to use a more general implementation, along the lines of Example 6.59, modiﬁed if necessary to handle dynamic discovery of the direction of the terminating test.

DESIGN & IMPLEMENTATION

6.7 Numerical imprecision Among its many changes to the do loop of Fortran IV, Fortran 77 allowed the index, bounds, and step size of the loop to be ﬂoating-point numbers, not just integers. Interestingly, this feature was taken back out of the language in Fortran 90. The problem with real-number sequences is that limited precision can cause comparisons (e.g., between the index and the bound) to produce unexpected or even implementation-dependent results when the values are close to one another. Should

for x := 1.0 to 2.0 by 1.0 / 3.0

execute three iterations or four? It depends on whether 1.0 / 3.0 is rounded up or down. The Fortran 90 designers appear to have decided that such ambiguity is philosophically inconsistent with the idea of ﬁnite enumeration. The pro- grammer who wants to iterate over ﬂoating-point values must use an explicit comparison in a pretest or post-test loop (Section 6.5.5).

The choice between requiring and (merely) enabling enumeration manifests itself in several speciﬁc questions:

* Can control enter or leave the loop in any way other than through the enumer-
  ation mechanism?
* What happens if the loop body modiﬁes variables that were used to compute
  the end-of-loop bound?
* What happens if the loop body modiﬁes the index variable itself?
* Can the program read the index variable after the loop has completed, and if
  so, what will its value be?

Questions (1) and (2) are relatively easy to resolve. Most languages allow a break/exit statement to leave a for loop early. Fortran IV allowed a goto to jump into a loop, but this was generally regarded as a language ﬂaw; Fortran 77 and most other languages prohibit such jumps. Similarly, most languages (but not C; see Section 6.5.2) specify that the bound is computed only once, before the ﬁrst iteration, and kept in a temporary location. Subsequent changes to variables used to compute the bound have no effect on how many times the loop iterates. Questions (3) and (4) are more difﬁcult. Suppose we write (in no particular EXAMPLE 6.62

Changing the index in a for loop language)

for i := 1 to 10 by 2 ... if i = 3 i := 6

What should happen at the end of the i=3 iteration? Should the next iteration have i = 5 (the next element of the arithmetic sequence speciﬁed in the loop header), i = 8 (2 more than 6), or even conceivably i = 7 (the next value of the sequence after 6)? One can imagine reasonable arguments for each of these options. To avoid the need to choose, many languages prohibit changes to the loop index within the body of the loop. Fortran makes the prohibition a mat- ter of programmer discipline: the implementation is not required to catch an erroneous update. Pascal provided an elaborate set of conservative rules [Int90, Sec. 6.8.3.9] that allowed the compiler to catch all possible updates. These rules were complicated by the fact that the index variable was declared outside the loop; it might be visible to subroutines called from the loop even if it was not passed as a parameter. ■ If control escapes the loop with a break/exit, the natural value for the in- EXAMPLE 6.63

Inspecting the index after a for loop dex would seem to be the one that was current at the time of the escape. For “normal” termination, on the other hand, the natural value would seem to be the ﬁrst one that exceeds the loop bound. Certainly that is the value that will be produced by the implementation of Example 6.59. Unfortunately, as we noted in Example 6.60, the “next” value for some loops may be outside the range of integer precision. For other loops, it may be semantically invalid:

c : ’a’..’z’ –– character subrange ... for c := ’a’ to ’z’ do ... –– what comes after ’z’?

Requiring the post-loop value to always be the index of the ﬁnal iteration is unattractive from an implementation perspective: it would force us to replace Example 6.59 with a translation that has an extra branch instruction in every it- eration:

r1 := ’a’ r2 := ’z’ if r1 > r2 goto L3 –– Code improver may remove this test, –– since ’a’ and ’z’ are constants. L1: . . . –– loop body; use r1 for i if r1 = r2 goto L2 r1 := r1 + 1 goto L1 L2: i := r1 L3:

Of course, the compiler must generate this sort of code in any event (or use an iteration count) if arithmetic overﬂow may interfere with testing the terminating condition. To permit the compiler to use the fastest correct implementation in all cases, several languages, including Fortran 90 and Pascal, say that the value of the index is undeﬁned after the end of the loop. ■ An attractive solution to both the index modiﬁcation problem and the post- loop value problem was pioneered by Algol W and Algol 68, and subsequently adopted by Ada, Modula 3, and many other languages. In these, the header of the loop is considered to contain a declaration of the index. Its type is inferred from the bounds of the loop, and its scope is the loop’s body. Because the index is not visible outside the loop, its value is not an issue. Of course, the programmer must not give the index the same name as any variable that must be accessed within the loop, but this is a strictly local issue: it has no ramiﬁcations outside the loop.

6.5.2 Combination Loops

Algol 60 provided a single loop construct that subsumed the properties of more modern enumeration and logically controlled loops. It allowed the programmer to specify an arbitrary number of “enumerators,” each of which could be a single value, a range of values similar to those of modern enumeration-controlled loops, or an expression with a terminating condition. Common Lisp provides an even more powerful facility, with four separate sets of clauses, to initialize index vari- ables (of which there may be an arbitrary number), test for loop termination (in any of several ways), evaluate body expressions, and clean up at loop termination.

A much simpler form of combination loop appears in C and its successors. Semantically, the C for loop is logically controlled. It was designed, however, to make enumeration easy. Our Modula-2 example EXAMPLE 6.64

Combination (for) loop in C FOR i := first TO last BY step DO ... END

would usually be written in C as

```
for (i = first; i <= last; i += step) {
...
}
```

With caveats for a few special cases, C deﬁnes this to be equivalent to

{ i = first; while (i <= last) { ... i += step; } ■ }

This deﬁnition means that it is the programmer’s responsibility to worry about the effect of overﬂow on testing of the terminating condition. It also means that both the index and any variables contained in the terminating condition can be modiﬁed by the body of the loop, or by subroutines it calls, and these changes will affect the loop control. This, too, is the programmer’s responsibility. Any of the three clauses in the for loop header can be null (the condition is considered true if missing). Alternatively, a clause can consist of a sequence of comma-separated expressions. The advantage of the C for loop over its while loop equivalent is compactness and clarity. In particular, all of the code affecting

DESIGN & IMPLEMENTATION

6.8 for loops Modern for loops reﬂect the impact of both semantic and implementation challenges. Semantic challenges include changes to loop indices or bounds from within the loop, the scope of the index variable (and its value, if any, out- side the loop), and gotos that enter or leave the loop. Implementation chal- lenges include the imprecision of ﬂoating-point values, the direction of the bottom-of-loop test, and overﬂow at the end of the iteration range. The “com- bination loops” of C (Section 6.5.2) move responsibility for these challenges out of the compiler and into the application program.

the ﬂow of control is localized within the header. In the while loop, one must read both the top and the bottom of the loop to know what is going on. While the logical iteration semantics of the C for loop eliminate any ambigu- ity about the value of the index variable after the end of the loop, it may still be convenient to make the index local to the body of the loop, by declaring it in the header’s initialization clause. In Example 6.64, variable i must be declared in the surrounding scope. If we instead write EXAMPLE 6.65

C for loop with a local index for (int i = first; i <= last; i += step) { ... }

then i will not be visible outside. It will still, however, be vulnerable to (deliberate or accidental) modiﬁcation within the loop. ■

6.5.3 Iterators

In all of the examples we have seen so far (with the possible exception of the com- bination loops of Algol 60, Common Lisp, or C), a for loop iterates over the ele- ments of an arithmetic sequence. In general, however, we may wish to iterate over the elements of any well-deﬁned set (what are often called collections, or instances of a container class, in object-oriented code). Clu introduced an elegant iterator mechanism (also found in Python, Ruby, and C#) to do precisely that. Euclid and several more recent languages, notably C++, Java, and Ada 2012, deﬁne a stan- dard interface for iterator objects (sometimes called enumerators) that are equally easy to use, but not as easy to write. Icon, conversely, provides a generalization of iterators, known as generators, that combines enumeration with backtracking search.7

True Iterators

Clu, Python, Ruby, and C# allow any container abstraction to provide an iterator that enumerates its items. The iterator resembles a subroutine that is permitted to contain yield statements, each of which produces a loop index value. For loops are then designed to incorporate a call to an iterator. The Modula-2 fragment EXAMPLE 6.66

Simple iterator in Python FOR i := first TO last BY step DO ... END

would be written as follows in Python:

7 Unfortunately, terminology is not consistent across languages. Euclid uses the term “generator” for what are called “iterator objects” here. Python uses it for what are called “true iterators” here.

![Figure 6.5 Python iterator...](images/page_302_vector_244.png)
*Figure 6.5 Python iterator for preorder enumeration of the nodes of a binary tree. Because Python is dynamically typed, this code will work for any data that support the operations needed by insert, lookup, and so on (probably just <). In a statically typed language, the BinTree class would need to be generic.*

```
for i in range(first, last, step):
...
```

Here range is a built-in iterator that yields the integers from first to first + ⌊(last −first)/step⌋× step in increments of step. ■ When called, the iterator calculates the ﬁrst index value of the loop, which it returns to the main program by executing a yield statement. The yield be- haves like return, except that when control transfers back to the iterator after completion of the ﬁrst iteration of the loop, the iterator continues where it last left off—not at the beginning of its code. When the iterator has no more elements to yield it simply returns (without a value), thereby terminating the loop. In effect, an iterator is a separate thread of control, with its own program counter, whose execution is interleaved with that of the for loop to which it sup- plies index values.8 The iteration mechanism serves to “decouple” the algorithm required to enumerate elements from the code that uses those elements. The range iterator is predeﬁned in Python. As a more illustrative example, EXAMPLE 6.67

Python iterator for tree enumeration consider the preorder enumeration of values stored in a binary tree. A Python iterator for this task appears in Figure 6.5. Invoked from the header of a for loop, it yields the value in the root node (if any) for the ﬁrst iteration and then calls itself recursively, twice, to enumerate values in the left and right subtrees. ■

8 Because iterators are interleaved with loops in a very regular way, they can be implemented more easily (and cheaply) than fully general threads. We will consider implementation options further in Section C 9.5.3.

Iterator Objects

As realized in most imperative languages, iteration involves both a special form of for loop and a mechanism to enumerate values for the loop. These concepts can be separated. Euclid, C++, Java, and Ada 2012 all provide enumeration- controlled loops reminiscent of those of Python. They have no yield statement, however, and no separate thread-like context to enumerate values; rather, an it- erator is an ordinary object (in the object-oriented sense of the word) that pro- vides methods for initialization, generation of the next index value, and testing for completion. Between calls, the state of the iterator must be kept in the object’s data members. Figure 6.6 contains the Java equivalent of the BinTree class of Figure 6.5. EXAMPLE 6.68

Java iterator for tree enumeration Given this code, we can write

```
BinTree<Integer> myTree = ...
...
for (Integer i : myTree) {
System.out.println(i);
}
```

The loop here is syntactic sugar for

```
for (Iterator<Integer> it = myTree.iterator(); it.hasNext();) {
Integer i = it.next();
System.out.println(i);
}
```

The expression following the colon in the more concise version of the loop must be an object that supports the standard Iterable interface. This interface in- cludes an iterator() method that returns an Iterator object. ■ C++ takes a related but somewhat different approach. With appropriate deﬁ- EXAMPLE 6.69

Iteration in C++11 nitions, the Java for loop of the previous example could be written as follows in C++11:

```
tree_node* my_tree = ...
...
for (int n : *my_tree) {
cout << n << "\n";
}
```

DESIGN & IMPLEMENTATION

6.9 “True” iterators and iterator objects While the iterator library mechanisms of C++ and Java are highly useful, it is worth emphasizing that they are not the functional equivalents of “true” iterators, as found in Clu, Python, Ruby, and C#. Their key limitation is the need to maintain all intermediate state in the form of explicit data structures, rather than in the program counter and local variables of a resumable execu- tion context.

![Figure 6.6 Java code...](images/page_304_vector_408.png)
*Figure 6.6 Java code for preorder enumeration of the nodes of a binary tree. The nested TreeIterator class uses an explicit Stack object (borrowed from the standard library) to keep track of subtrees whose nodes have yet to be enumerated. Java generics, speciﬁed as <T> type arguments for BinTree, Stack, Iterator, and Iterable, allow next to return an object of the appropriate type, rather than the undifferentiated Object. The remove method is part of the Iterator interface, and must therefore be provided, if only as a placeholder.*

This loop is syntactic sugar for

```
for (tree_node::iterator it = my_tree->begin();
it != my_tree->end(); ++it) {
int n = *it;
cout << n << "\n";
}
```

Where a Java iterator has methods to produce successive elements of a collection on demand (and to indicate when there are no more), a C++ iterator is designed

to act as a special kind of pointer. Support routines in the standard library lever- age the language’s unusually ﬂexible operator overloading and reference mecha- nisms to redeﬁne comparison (!=), increment (++), dereference (*), and so on in a way that makes iterating over the elements of a collection look very much like using pointer arithmetic to traverse a conventional array (“Pointers and Arrays in C,” Section 8.5.1). As in the Java example, iterator it encapsulates all the state needed to ﬁnd successive elements of the collection, and to determine when there are no more. To obtain the current element, we “dereference” the iterator, using the * or -> operators. The initial value of the iterator is produced by a collection’s begin method. To advance to the following element, we use the increment (++) opera- tor. The end method returns a special iterator that “points beyond the end” of the collection. The increment (++) operator must return a reference that tests equal to this special iterator when the collection has been exhausted. ■ Code to implement our C++ tree iterator is somewhat messier than the Java version of Figure 6.6, due to operator overloading, the value model of variables (which requires explicit references and pointers), and the lack of garbage collec- tion. We leave the details to Exercise 6.19.

Iterating with First-Class Functions

In functional languages, the ability to specify a function “in line” facilitates a pro- gramming idiom in which the body of a loop is written as a function, with the loop index as an argument. This function is then passed as the ﬁnal argument to an iterator, which is itself a function. In Scheme we might write EXAMPLE 6.70

Passing the “loop body” to an iterator in Scheme (define uptoby (lambda (low high step f) (if (<= low high) (begin (f low) (uptoby (+ low step) high step f)) '())))

We could then sum the ﬁrst 50 odd numbers as follows:

(let ((sum 0)) (uptoby 1 100 2 (lambda (i) (set! sum (+ sum i)))) sum) =⇒2500

Here the body of the loop, (set! sum (+ sum i)), is an assignment. The =⇒ symbol (not a part of Scheme) is used here to mean “evaluates to.” ■ Smalltalk, which we consider in Section C 10.7.1, supports a similar idiom: EXAMPLE 6.71

Iteration with blocks in Smalltalk sum <- 0. 1 to: 100 by: 2 do: [:i | sum <- sum + i]

Like a lambda expression in Scheme, a square-bracketed block in Smalltalk creates a ﬁrst-class function, which we then pass as argument to the to: by: do: iterator. The iterator calls the function repeatedly, passing successive values of the index variable i as argument. ■ Iterators in Ruby are also similar, with functional semantics but syntax remi- niscent of Python or C#. Our uptoby iterator in Ruby could be written as follows: EXAMPLE 6.72

Iterating with procs in Ruby def uptoby(first, last, inc) while first <= last do yield first first += inc end end ... sum = 0 uptoby(1, 100, 2) { |i| sum += i } puts sum =⇒2500

This code is deﬁned as syntactic sugar for

```
def uptoby(first, last, inc, block)
while first <= last do
block.call(first)
first += inc
end
end
...
sum = 0
uptoby(1, 100, 2, Proc.new { |i| sum += i })
puts sum
```

When a block, delimited by braces or do... end, follows the parameter list of a function invocation, Ruby passes a closure representing the block (a “proc”) as an implicit extra argument to the function. Within the body of the function, yield is deﬁned as a call to the function’s last parameter, which must be a proc, and need not be explicitly declared. For added convenience, all of Ruby’s collection objects (arrays, ranges, map- pings, and sets) support a method named each that will invoke a block for every element of the collection. To sum the ﬁrst 100 integers (without the step size of 2), we could say

sum = 0 (1..100).each { |i| sum += i } puts sum =⇒5050

This code serves as the deﬁnition of conventional for-loop syntax, which is fur- ther syntactic sugar:

```
sum = 0
for i in (1..100) do
sum += i
end
puts sum
```

In Lisp and Scheme, one can deﬁne similar syntactic sugar using continuations (Section 6.2.2) and lazy evaluation (Section 6.6.2); we consider this possibility in Exercises 6.34 and 6.35. ■

Iterating without Iterators

In a language with neither true iterators nor iterator objects, we can still decou- EXAMPLE 6.73

Imitating iterators in C ple the enumeration of a collection from actual use of the elements by adopting appropriate programming conventions. In C, for example, we might deﬁne a tree_iter type and associated functions that could be used in a loop as follows:

```
bin_tree *my_tree;
tree_iter ti;
...
for (ti_create(my_tree, &ti); !ti_done(ti); ti_next(&ti)) {
bin_tree *n = ti_val(ti);
...
}
ti_delete(&ti);
```

There are two principal differences between this code and the more structured al- ternatives: (1) the syntax of the loop is a good bit less elegant (and arguably more prone to accidental errors), and (2) the code for the iterator is simply a type and some associated functions—C provides no abstraction mechanism to group them together as a module or a class. By providing a standard interface for iterator ab- stractions, object-oriented languages facilitate the design of higher-order mech- anisms that manipulate whole collections: sorting them, merging them, ﬁnding their intersection or difference, and so on. We leave the C code for tree_iter and the various ti_ functions to Exercise 6.20. ■

6.5.4 Generators in Icon

Icon generalizes the concept of iterators, providing a generator mechanism that causes any expression in which it is embedded to enumerate multiple values on demand.

IN MORE DEPTH

We consider Icon generators in more detail on the companion site. The language’s enumeration-controlled loop, the every loop, can contain not only a generator,

but any expression that contains a generator. Generators can also be used in con- structs like if statements, which will execute their nested code if any generated value makes the condition true, automatically searching through all the possi- bilities. When generators are nested, Icon explores all possible combinations of generated values, and will even backtrack where necessary to undo unsuccessful control-ﬂow branches or assignments.

6.5.5 Logically Controlled Loops

In comparison to enumeration-controlled loops, logically controlled loops have many fewer semantic subtleties. The only real question to be answered is where within the body of the loop the terminating condition is tested. By far the most common approach is to test the condition before each iteration. The familiar EXAMPLE 6.74

while loop in Algol-W while loop syntax for this was introduced in Algol-W:

while condition do statement

To allow the body of the loop to be a statement list, most modern languages use an explicit concluding keyword (e.g., end), or bracket the body with delimiters (e.g., { ...}). A few languages (notably Python) indicate the body with an extra level of indentation. ■

Post-test Loops

Occasionally it is handy to be able to test the terminating condition at the bottom of a loop. Pascal introduced special syntax for this case, which was retained in Modula but dropped in Ada. A post-test loop allows us, for example, to write EXAMPLE 6.75

Post-test loop in Pascal and Modula repeat readln(line) until line[1] = '$';

instead of

```
readln(line);
while line[1] <> '$' do
readln(line);
```

The difference between these constructs is particularly important when the body of the loop is longer. Note that the body of a post-test loop is always executed at least once. ■ C provides a post-test loop whose condition works “the other direction” (i.e., EXAMPLE 6.76

Post-test loop in C “while” instead of “until”):

```
do {
line = read_line(stdin);
} while (line[0] != '$');
```

■

Mid-test Loops

Finally, as we noted in Section 6.2.1, it is sometimes appropriate to test the ter- minating condition in the middle of a loop. In many languages this “mid-test” can be accomplished with a special statement nested inside a conditional: exit in Ada, break in C, last in Perl. In Section 6.4.2 we saw a somewhat unusual use EXAMPLE 6.77

break statement in C of break to leave a C switch statement. More conventionally, C also uses break to exit the closest for, while, or do loop:

```
for (;;) {
line = read_line(stdin);
if (all_blanks(line)) break;
consume_line(line);
}
```

Here the missing condition in the for loop header is assumed to always be true. (C programmers have traditionally preferred this syntax to the equivalent while (1), presumably because it was faster in certain early C compilers.) ■ In some languages, an exit statement takes an optional loop-name argument EXAMPLE 6.78

Exiting a nested loop in Ada that allows control to escape a nested loop. In Ada we might write

outer: loop get_line(line, length); for i in 1..length loop exit outer when line(i) = '$'; consume_char(line(i)); end loop; end loop outer; ■

In Perl this would be EXAMPLE 6.79

Exiting a nested loop in Perl outer: while (<>) { # iterate over lines of input foreach $c (split //) { # iterate over remaining chars last outer if ($c =~ '\$'); # exit main loop if we see a $ sign consume_char($c); } } ■

Java extends the C/C++ break statement in a similar fashion, with optional labels on loops.

3CHECK YOUR UNDERSTANDING 28. Describe three subtleties in the implementation of enumeration-controlled loops. 29. Why do most languagesnot allow the bounds or increment of an enumeration- controlled loop to be ﬂoating-point numbers?

* Why do many languages require the step size of an enumeration-controlled
  loop to be a compile-time constant?
* Describe the “iteration count” loop implementation. What problem(s) does
  it solve?
* What are the advantages of making an index variable local to the loop it con-
  trols?

* Does C have enumeration-controlled loops? Explain.
* What is a collection (a container instance)?
* Explain the difference between true iterators and iterator objects.

* Cite two advantages of iterator objects over the use of programming conven-
  tions in a language like C.

* Describe the approach to iteration typically employed in languages with ﬁrst-
  class functions.
* Give an example in which a mid-test loop results in more elegant code than
  does a pretest or post-test loop.

6.6 Recursion

Unlike the control-ﬂow mechanisms discussed so far, recursion requires no spe- cial syntax. In any language that provides subroutines (particularly functions), all that is required is to permit functions to call themselves, or to call other functions that then call them back in turn. Most programmers learn in a data structures class that recursion and (logically controlled) iteration provide equally powerful means of computing functions: any iterative algorithm can be rewritten, auto- matically, as a recursive algorithm, and vice versa. We will compare iteration and recursion in more detail in the ﬁrst subsection below. In the following subsection we will consider the possibility of passing unevaluated expressions into a func- tion. While usually inadvisable, due to implementation cost, this technique will sometimes allow us to write elegant code for functions that are only deﬁned on a subset of the possible inputs, or that explore logically inﬁnite data structures.

6.6.1 Iteration and Recursion

As we noted in Section 3.2, Fortran 77 and certain other languages do not permit recursion. A few functional languages do not permit iteration. Most modern languages, however, provide both mechanisms. Iteration is in some sense the more “natural” of the two in imperative languages, because it is based on the repeated modiﬁcation of variables. Recursion is the more natural of the two in

functional languages, because it does not change variables. In the ﬁnal analysis, which to use in which circumstance is mainly a matter of taste. To compute a EXAMPLE 6.80

A “naturally iterative” problem sum,



1≤i≤10 f (i)

it seems natural to use iteration. In C one would say

typedef int (*int_func) (int); int summation(int_func f, int low, int high) { /* assume low <= high */ int total = 0; int i; for (i = low; i <= high; i++) { total += f(i); // (C will automatically dereference // a function pointer when we attempt to call it.) } return total; } ■

To compute a value deﬁned by a recurrence, EXAMPLE 6.81

A “naturally recursive” problem gcd(a, b) (positive integers, a, b) ≡

⎧ ⎨

a if a = b gcd(a−b, b) if a > b gcd(a, b−a) if b > a

⎩

recursion may seem more natural:

int gcd(int a, int b) { /* assume a, b > 0 */ if (a == b) return a; else if (a > b) return gcd(a-b, b); else return gcd(a, b-a); } ■

In both these cases, the choice could go the other way: EXAMPLE 6.82

Implementing problems “the other way” typedef int (*int_func) (int); int summation(int_func f, int low, int high) { /* assume low <= high */ if (low == high) return f(low); else return f(low) + summation(f, low+1, high); }

int gcd(int a, int b) { /* assume a, b > 0 */ while (a != b) { if (a > b) a = a-b; else b = b-a; } return a; } ■

Tail Recursion

It is sometimes argued that iteration is more efﬁcient than recursion. It is more accurate to say that naive implementation of iteration is usually more efﬁcient than naive implementation of recursion. In the examples above, the iterative im- plementations of summation and greatest divisors will be more efﬁcient than the recursive implementations if the latter make real subroutine calls that allocate space on a run-time stack for local variables and bookkeeping information. An “optimizing” compiler, however, particularly one designed for a functional lan- guage, will often be able to generate excellent code for recursive functions. It is particularly likely to do so for tail-recursive functions such as gcd above. A tail-recursive function is one in which additional computation never follows a re- cursive call: the return value is simply whatever the recursive call returns. For such functions, dynamically allocated stack space is unnecessary: the compiler can reuse the space belonging to the current iteration when it makes the recursive call. In effect, a good compiler will recast the recursive gcd function above as EXAMPLE 6.83

Iterative implementation of tail recursion follows:

int gcd(int a, int b) { /* assume a, b > 0 */ start: if (a == b) return a; else if (a > b) { a = a-b; goto start; } else { b = b-a; goto start; } } ■

Even for functions that are not tail-recursive, automatic, often simple trans- formations can produce tail-recursive code. The general case of the transforma- tion employs conversion to what is known as continuation-passing style [FWH01, Chaps. 7–8]. In effect, a recursive function can always avoid doing any work after returning from a recursive call by passing that work into the recursive call, in the form of a continuation. Some speciﬁc transformations (not based on continuation passing) are often employed by skilled users of functional languages. Consider, for example, the EXAMPLE 6.84

By-hand creation of tail-recursive code recursive summation function above, written here in Scheme:

```
(define summation
(lambda (f low high)
(if (= low high)
(f low)
; then part
(+ (f low) (summation f (+ low 1) high)))))
; else part
```

Recall that Scheme, like all Lisp dialects, uses Cambridge Polish notation for ex- pressions. The lambda keyword is used to introduce a function. As recursive calls return, our code calculates the sum from “right to left”: from high down to low. If the programmer (or compiler) recognizes that addition is associative, we can rewrite the code in a tail-recursive form:

```
(define summation
(lambda (f low high subtotal)
(if (= low high)
(+ subtotal (f low))
(summation f (+ low 1) high (+ subtotal (f low))))))
```

Here the subtotal parameter accumulates the sum from left to right, passing it into the recursive calls. Because it is tail recursive, this function can be translated into machine code that does not allocate stack space for recursive calls. Of course, the programmer won’t want to pass an explicit subtotal parameter to the initial call, so we hide it (the parameter) in an auxiliary, “helper” function:

```
(define summation
(lambda (f low high)
(letrec ((sum-helper
(lambda (low subtotal)
(let ((new_subtotal (+ subtotal (f low))))
(if (= low high)
new_subtotal
(sum-helper (+ low 1) new_subtotal))))))
(sum-helper low 0))))
```

The let construct in Scheme serves to introduce a nested scope in which local names (e.g., new_subtotal) can be deﬁned. The letrec construct permits the deﬁnition of recursive functions (e.g., sum-helper). ■

Thinking Recursively

Detractors of functional programming sometimes argue, incorrectly, that recur- sion leads to algorithmically inferior programs. Fibonacci numbers, for example, EXAMPLE 6.85

Naive recursive Fibonacci function are deﬁned by the mathematical recurrence

Fn (non-negative integer n) ≡  1 if n = 0 or n = 1 Fn−1 + Fn−2 otherwise

The naive way to implement this recurrence in Scheme is

(define fib (lambda (n) (cond ((= n 0) 1) ((= n 1) 1) (#t (+ (fib (- n 1)) (fib (- n 2))))))) ; #t means 'true' in Scheme ■

Unfortunately, this algorithm takes exponential time, when linear time is possi- ble.9 In C, one might write EXAMPLE 6.86

Linear iterative Fibonacci function int fib(int n) { int f1 = 1; int f2 = 1; int i; for (i = 2; i <= n; i++) { int temp = f1 + f2; f1 = f2; f2 = temp; } return f2; } ■

One can write this iterative algorithm in Scheme: the language includes (non- functional) iterative features. It is probably better, however, to draw inspiration EXAMPLE 6.87

Efﬁcient tail-recursive Fibonacci function from the tail-recursive version of the summation example above, and write the following O(n) recursive function:

```
(define fib
(lambda (n)
(letrec ((fib-helper
(lambda (f1 f2 i)
(if (= i n)
f2
(fib-helper f2 (+ f1 f2) (+ i 1))))))
(fib-helper 0 1 0))))
```

For a programmer accustomed to writing in a functional style, this code is per- fectly natural. One might argue that it isn’t “really” recursive; it simply casts an iterative algorithm in a tail-recursive form, and this argument has some merit. Despite the algorithmic similarity, however, there is an important difference be- tween the iterative algorithm in C and the tail-recursive algorithm in Scheme: the latter has no side effects. Each recursive call of the fib-helper function creates a new scope, containing new variables. The language implementation may be able to reuse the space occupied by previous instances of the same scope, but it guarantees that this optimization will never introduce bugs. ■

9 Actually, one can do substantially better than linear time using algorithms based on binary matrix multiplication or closest-integer rounding of continuous functions, but these approaches suffer from high constant-factor costs or problems with numeric precision. For most purposes the linear-time algorithm is a reasonable choice.

6.6.2 Applicative- and Normal-Order Evaluation

Throughout the discussion so far we have assumed implicitly that arguments are evaluated before passing them to a subroutine. This need not be the case. It is possible to pass a representation of the unevaluated arguments to the subroutine instead, and to evaluate them only when (if) the value is actually needed. The for- mer option (evaluating before the call) is known as applicative-order evaluation; the latter (evaluating only when the value is actually needed) is known as normal- order evaluation. Normal-order evaluation is what naturally occurs in macros (Section 3.7). It also occurs in short-circuit Boolean evaluation (Section 6.1.5), call-by-name parameters (to be discussed in Section 9.3.1), and certain functional languages (to be discussed in Section 11.5). Algol 60 uses normal-order evaluation by default for user-deﬁned functions (applicative order is also available). This choice was presumably made to mimic the behavior of macros (Section 3.7). Most programmers in 1960 wrote mainly in assembler, and were accustomed to macro facilities. Because the parameter- passing mechanisms of Algol 60 are part of the language, rather than textual ab- breviations, problems like misinterpreted precedence or naming conﬂicts do not arise. Side effects, however, are still very much an issue. We will discuss Algol 60 parameters in more detail in Section 9.3.1.

Lazy Evaluation

From the points of view of clarity and efﬁciency, applicative-order evaluation is generally preferable to normal-order evaluation. It is therefore natural for it to be employed in most languages. In some circumstances, however, normal-order evaluation can actually lead to faster code, or to code that works when applicative- order evaluation would lead to a run-time error. In both cases, what matters is that normal-order evaluation will sometimes not evaluate an argument at all, if its value is never actually needed. Scheme provides for optional normal-order

DESIGN & IMPLEMENTATION

6.10 Normal-order evaluation Normal-order evaluation is one of many examples we have seen where ar- guably desirable semantics have been dismissed by language designers because of fear of implementation cost. Other examples in this chapter include side- effect freedom (which allows normal order to be implemented via lazy evalu- ation), iterators (Section 6.5.3), and nondeterminacy (Section 6.7). As noted in Sidebar 6.2, however, there has been a tendency over time to trade a bit of speed for cleaner semantics and increased reliability. Within the functional programming community, Haskell and its predecessor Miranda are entirely side-effect free, and use normal-order (lazy) evaluation for all parameters.

evaluation in the form of built-in functions called delay and force.10 These functions provide an implementation of lazy evaluation. In the absence of side effects, lazy evaluation has the same semantics as normal-order evaluation, but the implementation keeps track of which expressions have already been evaluated, so it can reuse their values if they are needed more than once in a given referencing environment. A delayed expression is sometimes called a promise. The mechanism used to keep track of which promises have already been evaluated is sometimes called memoization.11 Because applicative-order evaluation is the default in Scheme, the programmer must use special syntax not only to pass an unevaluated argument, but also to use it. In Algol 60, subroutine headers indicate which arguments are to be passed which way; the point of call and the uses of parameters within sub- routines look the same in either case. One important use of lazy evaluation is to create so-called inﬁnite or lazy data structures, which are “ﬂeshed out” on demand. The following example, adapted EXAMPLE 6.88

Lazy evaluation of an inﬁnite data structure from version 5 of the Scheme manual [KCR+98, p. 28], creates a “list” of all the natural numbers:

```
(define naturals
(letrec ((next (lambda (n) (cons n (delay (next (+ n 1)))))))
(next 1)))
(define head car)
(define tail (lambda (stream) (force (cdr stream))))
```

Here cons can be thought of, roughly, as a concatenation operator. Car returns the head of a list; cdr returns everything but the head. Given these deﬁnitions, we can access as many natural numbers as we want:

(head naturals) =⇒1 (head (tail naturals)) =⇒2 (head (tail (tail naturals))) =⇒3

The list will occupy only as much space as we have actually explored. More elab- orate lazy data structures (e.g., trees) can be valuable in combinatorial search problems, in which a clever algorithm may explore only the “interesting” parts of a potentially enormous search space. ■

6.7 Nondeterminacy

Our ﬁnal category of control ﬂow is nondeterminacy. A nondeterministic con- struct is one in which the choice between alternatives (i.e., between control paths)

10 More precisely, delay is a special form, rather than a function. Its argument is passed to it un- evaluated.

11 Within the functional programming community, the term “lazy evaluation” is often used for any implementation that declines to evaluate unneeded function parameters; this includes both naive implementations of normal-order evaluation and the memoizing mechanism described here.

is deliberately unspeciﬁed. We have already seen examples of nondeterminacy in the evaluation of expressions (Section 6.1.4): in most languages, operator or subroutine arguments may be evaluated in any order. Some languages, notably Algol 68 and various concurrent languages, provide more extensive nondetermin- istic mechanisms, which cover statements as well.

IN MORE DEPTH

Further discussion of nondeterminism can be found on the companion site. Ab- sent a nondeterministic construct, the author of a code fragment in which order does not matter must choose some arbitrary (artiﬁcial) order. Such a choice can make it more difﬁcult to construct a formal correctness proof. Some language designers have also argued that it is inelegant. The most compelling uses for non- determinacy arise in concurrent programs, where imposing an arbitrary choice on the order in which a thread interacts with its peers may cause the system as a whole to deadlock. For such programs one may need to ensure that the choice among nondeterministic alternatives is fair in some formal sense.

3CHECK YOUR UNDERSTANDING 39. What is a tail-recursive function? Why is tail recursion important? 40. Explain the difference between applicative- and normal-order evaluation of expressions. Under what circumstances is each desirable? 41. What is lazy evaluation? What are promises? What is memoization?

* Give two reasons why lazy evaluation may be desirable.
* Name a language in which parameters are always evaluated lazily.

* Give two reasons why a programmer might sometimes want control ﬂow to
  be nondeterministic.

## 6.8 Summary and Concluding Remarks

In this chapter we introduced the principal forms of control ﬂow found in pro- gramming languages: sequencing, selection, iteration, procedural abstraction, recursion, concurrency, exception handling and speculation, and nondetermi- nacy. Sequencing speciﬁes that certain operations are to occur in order, one after the other. Selection expresses a choice among two or more control-ﬂow alter- natives. Iteration and recursion are the two ways to execute operations repeat- edly. Recursion deﬁnes an operation in terms of simpler instances of itself; it depends on procedural abstraction. Iteration repeats an operation for its side

effect(s). Sequencing and iteration are fundamental to imperative programming. Recursion is fundamental to functional programming. Nondeterminacy allows the programmer to leave certain aspects of control ﬂow deliberately unspeciﬁed. We touched on concurrency only brieﬂy; it will be the subject of Chapter 13. Procedural abstractions (subroutines) are the subject of Chapter 9. Exception handling and speculation will be covered in Sections 9.4 and 13.4.4. Our survey of control-ﬂow mechanisms was preceded by a discussion of ex- pression evaluation. We considered the distinction between l-values and r-values, and between the value model of variables, in which a variable is a named con- tainer for data, and the reference model of variables, in which a variable is a ref- erence to a data object. We considered issues of precedence, associativity, and ordering within expressions. We examined short-circuit Boolean evaluation and its implementation via jump code, both as a semantic issue that affects the cor- rectness of expressions whose subparts are not always well deﬁned, and as an implementation issue that affects the time required to evaluate complex Boolean expressions. In our survey we encountered many examples of control-ﬂow constructs whose syntax and semantics have evolved considerably over time. An important early example was the phasing out of goto-based control ﬂow and the emergence of a consensus on structured alternatives. While convenience and readability are difﬁcult to quantify, most programmers would agree that the control-ﬂow con- structs of a language like Ada are a dramatic improvement over those of, say, Fortran IV. Examples of features in Ada that are speciﬁcally designed to rectify control-ﬂow problems in earlier languages include explicit terminators (end if, end loop, etc.) for structured constructs; elsif clauses; label ranges and default (others) clauses in case statements; implicit declaration of for loop indices as read-only local variables; explicit return statements; multilevel loop exit state- ments; and exceptions. The evolution of constructs has been driven by many goals, including ease of programming, semantic elegance, ease of implementation, and run-time ef- ﬁciency. In some cases these goals have proved complementary. We have seen for example that short-circuit evaluation leads both to faster code and (in many cases) to cleaner semantics. In a similar vein, the introduction of a new local scope for the index variable of an enumeration-controlled loop avoids both the semantic problem of the value of the index after the loop and (to some extent) the implementation problem of potential overﬂow. In other cases improvements in language semantics have been considered worth a small cost in run-time efﬁciency. We saw this in the development of iterators: like many forms of abstraction, they add a modest amount of run-time cost in many cases (e.g., in comparison to explicitly embedding the implementa- tion of the enumerated collection in the control ﬂow of the loop), but with a large pay-back in modularity, clarity, and opportunities for code reuse. In a similar vein, the developers of Java would argue that for many applications the portabil- ity and safety provided by extensive semantic checking, standard-format numeric types, and so on are far more important than speed.

In several cases, advances in compiler technology or in the simple willingness of designers to build more complex compilers have made it possible to incorpo- rate features once considered too expensive. Label ranges in Ada case statements require that the compiler be prepared to generate code employing binary search. In-line functions in C++ eliminate the need to choose between the inefﬁciency of tiny functions and the messy semantics of macros. Exceptions (as we shall see in Section 9.4.3) can be implemented in such a way that they incur no cost in the common case (when they do not occur), but the implementation is quite tricky. Iterators, boxing, generics (Section 7.3.1), and ﬁrst-class functions are likewise rather tricky, but are increasingly found in mainstream imperative languages. Some implementation techniques (e.g., rearranging expressions to uncover common subexpressions, or avoiding the evaluation of guards in a nondeter- ministic construct once an acceptable choice has been found) are sufﬁciently im- portant to justify a modest burden on the programmer (e.g., adding parentheses where necessary to avoid overﬂow or ensure numeric stability, or ensuring that expressions in guards are side-effect-free). Other semantically useful mechanisms (e.g., lazy evaluation, continuations, or truly random nondeterminacy) are usu- ally considered complex or expensive enough to be worthwhile only in special circumstances (if at all). In comparatively primitive languages, we can often obtain some of the beneﬁts of missing features through programming conventions. In early dialects of For- tran, for example, we can limit the use of gotos to patterns that mimic the control ﬂow of more modern languages. In languages without short-circuit evaluation, we can write nested selection statements. In languages without iterators, we can write sets of subroutines that provide equivalent functionality.

## 6.9 Exercises

6.1 We noted in Section 6.1.1 that most binary arithmetic operators are left- associative in most programming languages. In Section 6.1.4, however, we also noted that most compilers are free to evaluate the operands of a binary operator in either order. Are these statements contradictory? Why or why not?

6.2 As noted in Figure 6.1, Fortran and Pascal give unary and binary minus the same level of precedence. Is this likely to lead to nonintuitive evaluations of certain expressions? Why or why not?

6.3 In Example 6.9 we described a common error in Pascal programs caused by the fact that and and or have precedence comparable to that of the arith- metic operators. Show how a similar problem can arise in the stream-based I/O of C++ (described in Section C 8.7.3). (Hint: Consider the precedence of << and >>, and the operators that appear below them in the C column of Figure 6.1.)

6.4 Translate the following expression into postﬁx and preﬁx notation:

[−b + sqrt(b × b −4 × a × c)]/(2 × a)

Do you need a special symbol for unary negation?

6.5 In Lisp, most of the arithmetic operators are deﬁned to take two or more arguments, rather than strictly two. Thus (* 2 3 4 5) evaluates to 120, and (- 16 9 4) evaluates to 3. Show that parentheses are necessary to dis- ambiguate arithmetic expressions in Lisp (in other words, give an example of an expression whose meaning is unclear when parentheses are removed). In Section 6.1.1 we claimed that issues of precedence and associativity do not arise with preﬁx or postﬁx notation. Reword this claim to make explicit the hidden assumption.

6.6 Example 6.33 claims that “For certain values of x, (0.1 + x) * 10.0 and 1.0 + (x * 10.0) can differ by as much as 25%, even when 0.1 and x are of the same magnitude.” Verify this claim. (Warning: If you’re us- ing an x86 processor, be aware that ﬂoating-point calculations [even on single-precision variables] are performed internally with 80 bits of preci- sion. Roundoff errors will appear only when intermediate results are stored out to memory [with limited precision] and read back in again.)

6.7 Is &(&i) ever valid in C? Explain.

6.8 Languages that employ a reference model of variables also tend to employ automatic garbage collection. Is this more than a coincidence? Explain.

6.9 In Section 6.1.2 (“Orthogonality”), we noted that C uses = for assignment and == for equality testing. The language designers state: “Since assignment is about twice as frequent as equality testing in typical C programs, it’s ap- propriate that the operator be half as long” [KR88, p. 17]. What do you think of this rationale?

6.10 Consider a language implementation in which we wish to catch every use of an uninitialized variable. In Section 6.1.3 we noted that for types in which every possible bit pattern represents a valid value, extra space must be used to hold an initialized/uninitialized ﬂag. Dynamic checks in such a system can be expensive, largely because of the address calculations needed to ac- cess the ﬂags. We can reduce the cost in the common case by having the compiler generate code to automatically initialize every variable with a dis- tinguished sentinel value. If at some point we ﬁnd that a variable’s value is different from the sentinel, then that variable must have been initialized. If its value is the sentinel, we must double-check the ﬂag. Describe a plausible allocation strategy for initialization ﬂags, and show the assembly language sequences that would be required for dynamic checks, with and without the use of sentinels.

6.11 Write an attribute grammar, based on the following context-free grammar, that accumulates jump code for Boolean expressions (with short-circuiting)

into a synthesized attribute code of condition, and then uses this attribute to generate code for if statements.

stmt −→if condition then stmt else stmt

−→other stmt condition −→c term | condition or c term c term −→c factor | c term and c factor c factor −→ident relation ident | ( condition ) | not ( condition ) relation −→< | <= | = | <> | > | >=

You may assume that the code attribute has already been initialized for other stmt and ident nodes. (For hints, see Fischer et al.’s compiler book [FCL10, Sec. 14.1.4].)

6.12 Describe a plausible scenario in which a programmer might wish to avoid short-circuit evaluation of a Boolean expression.

6.13 Neither Algol 60 nor Algol 68 employs short-circuit evaluation for Boolean expressions. In both languages, however, an if... then ... else construct can be used as an expression. Show how to use if... then ... else to achieve the effect of short-circuit evaluation.

6.14 Consider the following expression in C: a/b > 0 && b/a > 0. What will be the result of evaluating this expression when a is zero? What will be the result when b is zero? Would it make sense to try to design a language in which this expression is guaranteed to evaluate to false when either a or b (but not both) is zero? Explain your answer.

6.15 As noted in Section 6.4.2, languages vary in how they handle the situation in which the controlling expression in a case statement does not appear among the labels on the arms. C and Fortran 90 say the statement has no effect. Pascal and Modula say it results in a dynamic semantic error. Ada says that the labels must cover all possible values for the type of the expres- sion, so the question of a missing value can never arise at run time. What are the tradeoffs among these alternatives? Which do you prefer? Why?

6.16 The equivalence of for and while loops, mentioned in Example 6.64, is not precise. Give an example in which it breaks down. Hint: think about the continue statement.

6.17 Write the equivalent of Figure 6.5 in C# or Ruby. Write a second version that performs an in-order enumeration, rather than preorder.

6.18 Revise the algorithm of Figure 6.6 so that it performs an in-order enumera- tion, rather than preorder.

6.19 Write a C++ preorder iterator to supply tree nodes to the loop in Exam- ple 6.69. You will need to know (or learn) how to use pointers, references, inner classes, and operator overloading in C++. For the sake of (relative) simplicity, you may assume that the data in a tree node is always an int; this will save you the need to use generics. You may want to use the stack abstraction from the C++ standard library.

6.20 Write code for the tree_iter type (struct) and the ti_create, ti_done, ti_next, ti_val, and ti_delete functions employed in Example 6.73.

6.21 Write, in C#, Python, or Ruby, an iterator that yields (a) all permutations of the integers 1 . . n (b) all combinations of k integers from the range 1 . . n (0 ≤k ≤n).

You may represent your permutations and combinations using either a list or an array.

6.22 Use iterators to construct a program that outputs (in some order) all struc- turally distinct binary trees of n nodes. Two trees are considered structurally distinct if they have different numbers of nodes or if their left or right sub- trees are structurally distinct. There are, for example, ﬁve structurally dis- tinct trees of three nodes:

These are most easily output in “dotted parenthesized form”:

```
(((.).).)
((.(.)).)
((.).(.))
(.((.).))
(.(.(.)))
```

(Hint: Think recursively! If you need help, see Section 2.2 of the text by Finkel [Fin96].)

6.23 Build true iterators in Java using threads. (This requires knowledge of ma- terial in Chapter 13.) Make your solution as clean and as general as possible. In particular, you should provide the standard Iterator or IEnumerable interface, for use with extended for loops, but the programmer should not have to write these. Instead, he or she should write a class with an Iterate method, which should in turn be able to call a Yield method, which you should also provide. Evaluate the cost of your solution. How much more expensive is it than standard Java iterator objects?

6.24 In an expression-orientedlanguage such as Algol 68 or Lisp, a while loop (a do loop in Lisp) has a value as an expression. How do you think this value should be determined? (How is it determined in Algol 68 and Lisp?) Is the value a useless artifact of expression orientation, or are there reasonable programs in which it might actually be used? What do you think should happen if the condition on the loop is such that the body is never executed?

6.25 Consider a mid-test loop, here written in C, that looks for blank lines in its input:

```
for (;;) {
line = read_line();
if (all_blanks(line)) break;
consume_line(line);
}
```

Show how you might accomplish the same task using a while or do (repeat) loop, if mid-test loops were not available. (Hint: One alterna- tive duplicates part of the code; another introduces a Boolean ﬂag variable.) How do these alternatives compare to the mid-test version?

6.26 Rubin [Rub87] used the following example (rewritten here in C) to argue in favor of a goto statement:

```
int first_zero_row = -1;
/* none */
int i, j;
for (i = 0; i < n; i++) {
for (j = 0; j < n; j++) {
if (A[i][j]) goto next;
}
first_zero_row = i;
break;
next: ;
}
```

The intent of the code is to ﬁnd the ﬁrst all-zero row, if any, of an n × n matrix. Do you ﬁnd the example convincing? Is there a good structured alternative in C? In any language?

6.27 Bentley [Ben00, Chap. 4] provides the following informal description of binary search:

We are to determine whether the sorted array X[1..N] contains the element T.... Binary search solves the problem by keeping track of a range within the array in which T must be if it is anywhere in the array. Initially, the range is the entire array. The range is shrunk by comparing its middle element to T and discarding half the range. The process continues until T is discovered in the array or until the range in which it must lie is known to be empty.

Write code for binary search in your favorite imperative programming lan- guage. What loop construct(s) did you ﬁnd to be most useful? NB: when he asked more than a hundred professional programmers to solve this prob- lem, Bentley found that only about 10% got it right the ﬁrst time, without testing.

6.28 A loop invariant is a condition that is guaranteed to be true at a given point within the body of a loop on every iteration. Loop invariants play a major role in axiomatic semantics, a formal reasoning system used to prove prop- erties of programs. In a less formal way, programmers who identify (and write down!) the invariants for their loops are more likely to write correct code. Show the loop invariant(s) for your solution to the preceding exercise.

(Hint: You will ﬁnd the distinction between < and ≤[or between > and ≥] to be crucial.)

6.29 If you have taken a course in automata theory or recursive function theory, explain why while loops are strictly more powerful than for loops. (If you haven’t had such a course, skip this question!) Note that we’re referring here to Ada-style for loops, not C-style.

6.30 Show how to calculate the number of iterations of a general Fortran 90- style do loop. Your code should be written in an assembler-like notation, and should be guaranteed to work for all valid bounds and step sizes. Be careful of overﬂow! (Hint: While the bounds and step size of the loop can be either positive or negative, you can safely use an unsigned integer for the iteration count.)

6.31 Write a tail-recursive function in Scheme or ML to compute n factorial (n! =  1≤i≤n i = 1 × 2 × · · · × n). (Hint: You will probably want to deﬁne a “helper” function, as discussed in Section 6.6.1.)

6.32 Is it possible to write a tail-recursive version of the classic quicksort algo- rithm? Why or why not?

6.33 Give an example in C in which an in-line subroutine may be signiﬁcantly faster than a functionally equivalent macro. Give another example in which the macro is likely to be faster. (Hint: Think about applicative vs normal- order evaluation of arguments.)

6.34 Use lazy evaluation (delay and force) to implement iterator objects in Scheme. More speciﬁcally, let an iterator be either the null list or a pair consisting of an element and a promise which when forced will return an iterator. Give code for an uptoby function that returns an iterator, and a for-iter function that accepts as arguments a one-argument function and an iterator. These should allow you to evaluate such expressions as

(for-iter (lambda (e) (display e) (newline)) (uptoby 10 50 3))

Note that unlike the standard Scheme for-each, for-iter should not re- quire the existence of a list containing the elements over which to iterate; the intrinsic space required for (for-iter f (uptoby 1 n 1)) should be only O(1), rather than O(n). 6.35 (Difﬁcult) Use call-with-current-continuation (call/cc) to imple- ment the following structured nonlocal control transfers in Scheme. (This requires knowledge of material in Chapter 11.) You will probably want to consult a Scheme manual for documentation not only on call/cc, but on define-syntax and dynamic-wind as well. (a) Multilevel returns. Model your syntax after the catch and throw of Common Lisp. (b) True iterators. In a style reminiscent of Exercise 6.34, let an iterator be a function which when call/cc-ed will return either a null list or a pair

consisting of an element and an iterator. As in that previous exercise, your implementation should support expressions like

(for-iter (lambda (e) (display e) (newline)) (uptoby 10 50 3))

Where the implementation of uptoby in Exercise 6.34 required the use of delay and force, however, you should provide an iterator macro (a Scheme special form) and a yield function that allows uptoby to look like an ordinary tail-recursive function with an embedded yield:

```
(define uptoby
(iterator (low high step)
(letrec ((helper (lambda (next)
(if (> next high) '()
(begin
; else clause
(yield next)
(helper (+ next step)))))))
(helper low))))
```

6.36–6.40 In More Depth.

## 6.10 Explorations

6.41 Loop unrolling (described in Exercise C 5.21 and Section C 17.7.1) is a code transformation that replicates the body of a loop and reduces the number of iterations, thereby decreasing loop overhead and increasing opportuni- ties to improve the performance of the processor pipeline by reordering in- structions. Unrolling is traditionally implemented by the code improve- ment phase of a compiler. It can be implemented at source level, however, if we are faced with the prospect of “hand optimizing” time-critical code on a system whose compiler is not up to the task. Unfortunately, if we replicate the body of a loop k times, we must deal with the possibility that the original number of loop iterations, n, may not be a multiple of k. Writing in C, and letting k = 4, we might transform the main loop of Exercise C 5.21 from

```
i = 0;
do {
sum += A[i]; squares += A[i] * A[i]; i++;
} while (i < N);
```

to

```
i = 0;
j = N/4;
do {
sum += A[i]; squares += A[i] * A[i]; i++;
sum += A[i]; squares += A[i] * A[i]; i++;
sum += A[i]; squares += A[i] * A[i]; i++;
sum += A[i]; squares += A[i] * A[i]; i++;
} while (--j > 0);
do {
sum += A[i]; squares += A[i] * A[i]; i++;
} while (i < N);
```

In 1983, Tom Duff of Lucasﬁlm realized that code of this sort can be “simpliﬁed” in C by interleaving a switch statement and a loop. The result is rather startling, but perfectly valid C. It’s known in programming folklore as “Duff’s device”:

```
i = 0; j = (N+3)/4;
switch (N%4) {
case 0: do{ sum += A[i]; squares += A[i] * A[i]; i++;
case 3:
sum += A[i]; squares += A[i] * A[i]; i++;
case 2:
sum += A[i]; squares += A[i] * A[i]; i++;
case 1:
sum += A[i]; squares += A[i] * A[i]; i++;
} while (--j > 0);
}
```

Duff announced his discovery with “a combination of pride and revulsion.” He noted that “Many people... have said that the worst feature of C is that switches don’t break automatically before each case label. This code forms some sort of argument in that debate, but I’m not sure whether it’s for or against.” What do you think? Is it reasonable to interleave a loop and a switch in this way? Should a programming language permit it? Is automatic fall-through ever a good idea?

6.42 Using your favorite language and compiler, investigate the order of evalu- ation of subroutine parameters. Are they usually evaluated left-to-right or right-to-left? Are they ever evaluated in the other order? (Can you be sure?) Write a program in which the order makes a difference in the results of the computation.

6.43 Consider the different approaches to arithmetic overﬂow adopted by Pascal, C, Java, C#, and Common Lisp, as described in Section 6.1.4. Speculate as to the differences in language design goals that might have caused the designers to adopt the approaches they did.

6.44 Learn more about container classes and the design patterns (structured pro- gramming idioms) they support. Explore the similarities and differences among the standard container libraries of C++, Java, and C#. Which of these libraries do you ﬁnd the most appealing? Why?

6.45 In Examples 6.43 and 6.72 we suggested that a Ruby proc (a block, passed to a function as an implicit extra argument) was “roughly” equivalent to a lambda expression. As it turns out, Ruby has both procs and lambda expressions, and they’re almost—but not quite—the same. Learn about the details, and the history of their development. In what situations will a proc and a lambda behave differently, and why?

6.46 One of the most popular idioms for large-scale systems is the so-called vis- itor pattern. It has several uses, one of which resembles the “iterating with ﬁrst-class functions” idiom of Examples 6.70 and 6.71. Brieﬂy, elements of a container class provide an accept method that expects as argument an object that implements the visitor interface. This interface in turn has a method named visit that expects an argument of element type. To iter- ate over a collection, we implement the “loop body” in the visit method of a visitor object. This object constitutes a closure of the sort described in Section 3.6.3. Any information that visit needs (beyond the identify of the “loop index” element) can be encapsulated in the object’s ﬁelds. An itera- tor method for the collection passes the visitor object to the accept method of each element. Each element in turn calls the visit method of the visitor object, passing itself as argument. Learn more about the visitor pattern. Use it to implement iterators for a collection—preorder, inorder, and postorder traversals of a binary tree, for example. How do visitors compare with equivalent iterator-based code? Do they add new functionality? What else are visitors good for, in addition to iteration? 6.47–6.50 In More Depth.

## 6.11 Bibliographic Notes

Many of the issues discussed in this chapter feature prominently in papers on the history of programming languages. Pointers to several such papers can be found in the Bibliographic Notes for Chapter 1. Fifteen papers comparing Ada, C, and Pascal can be found in the collection edited by Feuer and Gehani [FG84]. References for individual languages can be found in Appendix A. Niklaus Wirth has been responsible for a series of inﬂuential languages over a 30-year period, including Pascal [Wir71], its predecessor Algol W [WH66], and the successors Modula [Wir77b], Modula-2 [Wir85b], and Oberon [Wir88b]. The case statement of Algol W is due to Hoare [Hoa81]. Bernstein [Ber85] considers a variety of alternative implementations for case, including multi- level versions appropriate for label sets consisting of several dense “clusters” of values. Guarded commands (Section C 6.7) are due to Dijkstra [Dij75]. Duff’s device (Exploration 6.41) was originally posted to netnews, an early on-line dis- cussion group system, in May of 1984. The original posting appears to have been

lost, but Duff’s commentary on it can be found at many Internet sites, including www.lysator.liu.se/c/duffs-device.html. Debate over the supposed merits or evils of the goto statement dates from at least the early 1960s, but became a good bit more heated in the wake of a 1968 article by Dijkstra (“Go To Statement Considered Harmful” [Dij68b]). The struc- tured programming movement of the 1970s took its name from the text of Dahl, Dijkstra, and Hoare [DDH72]. A dissenting letter by Rubin in 1987 (“ ‘GOTO Considered Harmful’ Considered Harmful” [Rub87]; Exercise 6.26) elicited a ﬂurry of responses. What has been called the “reference model of variables” in this chapter is called the “object model” in Clu; Liskov and Guttag describe it in Sections 2.3 and 2.4.2 of their text on abstraction and speciﬁcation [LG86]. Clu iterators are described in an article by Liskov et al. [LSAS77], and in Chapter 6 of the Liskov and Guttag text. Icon generators are discussed in Chapters 11 and 14 of the text by Gris- wold and Griswold [GG96]. Ruby blocks, procs, and iterators are discussed in Chapter 4 of the text by Thomas et al. [TFH13]. The tree-enumeration algo- rithm of Exercise 6.22 was originally presented (without iterators) by Solomon and Finkel [SF80]. Several texts discuss the use of invariants (Exercise 6.28) as a tool for writing correct programs. Particularly noteworthy are the works of Dijkstra [Dij76] and Gries [Gri81]. Kernighan and Plauger provide a more informal discussion of the art of writing good programs [KP78]. The Blizzard [SFL+94] and Shasta [SG96] systems for software distributed shared memory (S-DSM) make use of sentinels (Exercise 6.10). We will discuss S-DSM in Section 13.2.1. Michaelson [Mic89, Chap. 8] provides an accessible formal treatment of applicative-order, normal-order, and lazy evaluation. The concept of memoiza- tion is originally due to Michie [Mic68]. Friedman, Wand, and Haynes provide an excellent discussion of continuation-passing style [FWH01, Chaps. 7–8].

