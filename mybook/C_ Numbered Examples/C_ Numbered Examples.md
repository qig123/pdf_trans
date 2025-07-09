# C: Numbered Examples

**C** **Numbered Examples**

**Chapter 1: Introduction**

## 1.25 Interpreting the syntax tree 33 1.26 GCD program assembly code 34 1.27 GCD program optimization 36

## 1.1 GCD program in x86 machine language 5 1.2 GCD program in x86 assembler 5

**Chapter 2: Programming Language Syntax**

The Art of Language Design

The Programming Language Spectrum

## 2.1 Syntax of Arabic numerals 43

## 1.3 Classiﬁcation of programming languages 11 1.4 GCD function in C 13 1.5 GCD function in OCaml 13 1.6 GCD rules in Prolog 13

Specifying Syntax: Regular Expressions and Context-Free Grammars

2.2 Lexical structure of C11 45 2.3 Syntax of numeric constants 46 2.4 Syntactic nesting in expressions 48 2.5 Extended BNF (EBNF) 49 2.6 Derivation of slope * x + intercept 50 2.7 Parse trees for slope * x + intercept 51 2.8 Expression grammar with precedence and associativity 52

Why Study Programming Languages?

Compilation and Interpretation

1.7 Pure compilation 17 1.8 Pure interpretation 17 1.9 Mixing compilation and interpretation 18 1.10 Preprocessing 19 1.11 Library routines and linking 19 1.12 Post-compilation assembly 20 1.13 The C preprocessor 20 1.14 Source-to-source translation 20 1.15 Bootstrapping 21 1.16 Compiling interpreted languages 23 1.17 Dynamic and just-in-time compilation 23 1.18 Microcode (ﬁrmware) 24

Scanning

2.9 Tokens for a calculator language 54 2.10 An ad hoc scanner for calculator tokens 54 2.11 Finite automaton for a calculator scanner 55 2.12 Constructing an NFA for a given regular expression 58 2.13 NFA for* d****(** .*d*** |*** d*.** )*** d****** 59 2.14 DFA for* d****(** .*d*** |*** d*.** )*** d****** 60 2.15 Minimal DFA for* d****(** .*d*** |*** d*.** )*** d****** 60 2.16 Nested case statement automaton 62 2.17 The nontrivial preﬁx problem 64 2.18 Look-ahead in Fortran scanning 64 2.19 Table-driven scanning 65

Programming Environments

An Overview of Compilation

1.19 Phases of compilation and interpretation 26 1.20 GCD program in C 28 1.21 GCD program tokens 28 1.22 Context-free grammar and parsing 28 1.23 GCD program parse tree 29 1.24 GCD program abstract syntax tree 33

Parsing

## 2.20 Top-down and bottom-up parsing 70 2.21 Bounding space with a bottom-up grammar 72

2.60 0*n*1*n* is not a regular language C*·*19 2.61 Separation of grammar classes C*·*20 2.62 Separation of language classes C*·*20

2.22 Top-down grammar for a calculator language 73 2.23 Recursive descent parser for the calcula- tor language 75 2.24 Recursive descent parse of a “sum and average” program 75 2.25 Left recursion 79 2.26 Common preﬁxes 79 2.27 Eliminating left recursion 80 2.28 Left factoring 80 2.29 Parsing a “dangling else” 80 2.30 “Dangling else” program bug 81 2.31 End markers for structured statements 81 2.32 The need for elsif 82 2.33 Driver and table for top-down parsing 82 2.34 Table-driven parse of the “sum and average” program 83 2.35 Predict sets for the calculator language 84 2.36 Derivation of an id list 90 2.37 Bottom-up grammar for the calculator language 90 2.38 Bottom-up parse of the “sum and average” program 91 2.39 CFSM for the bottom-up calculator grammar 95 2.40 Epsilon productions in the bottom-up calculator grammar 95 2.41 CFSM with epsilon productions 101 2.42 A syntax error in C 102 2.43 Syntax error in C (reprise) C*·*1 2.44 The problem with panic mode C*·*1 2.45 Phrase-level recovery in recursive descent C*·*2 2.46 Cascading syntax errors C*·*3 2.47 Reducing cascading errors with context- speciﬁc look-ahead C*·*4 2.48 Recursive descent with full phrase-level recovery C*·*4 2.49 Exceptions in a recursive descent parser C*·*5 2.50 Error production for “; else” C*·*6 2.51 Insertion-only repair in FMQ C*·*8 2.52 FMQ with deletions C*·*8 2.53 Panic mode in yacc/bison C*·*11 2.54 Panic mode with statement terminators C*·*11 2.55 Phrase-level recovery in yacc/bison C*·*11

**Chapter 3: Names, Scopes, and Bindings**

The Notion of Binding Time

Object Lifetime and Storage Management

## 3.1 Static allocation of local variables 119 3.2 Layout of the run-time stack 120 3.3 External fragmentation in the heap 122

Scope Rules

3.4 Static variables in C 127 3.5 Nested scopes 128 3.6 Static chains 130 3.7 A “gotcha” in declare-before-use 131 3.8 Whole-block scope in C# 132 3.9 “Local if written” in Python 132 3.10 Declaration order in Scheme 132 3.11 Declarations vs deﬁnitions in C 133 3.12 Inner declarations in C 134 3.13 Pseudorandom numbers as a motivation for modules 136 3.14 Pseudorandom number generator in C++ 137 3.15 Module as “manager” for a type 138 3.16 A pseudorandom number generator type 140 3.17 Modules and classes in a large application 142 3.18 Static vs dynamic scoping 143 3.19 Run-time errors with dynamic scoping 144

Implementing Scope

## 3.45 The LeBlanc-Cook symbol table C*·*27 3.46 Symbol table for a sample program C*·*28 3.47 A-list lookup in Lisp C*·*31 3.48 Central reference table C*·*33 3.49 A-list closures C*·*33

The Meaning of Names within a Scope

3.20 Aliasing with parameters 146 3.21 Aliases and code improvement 146 3.22 Overloaded enumeration constants in Ada 147 3.23 Resolving ambiguous overloads 147 3.24 Overloading in C++ 148 3.25 Operator overloading in Ada 148 3.26 Operator overloading in C++ 148 3.27 Inﬁx operators in Haskell 149 3.28 Overloading with type classes 149 3.29 Printing objects of multiple types 150

Theoretical Foundations

2.56 Formal DFA for* d*** *****(** .*d* |* d*.** )*** d*** *** C*·*14 2.57 Reconstructing a regular expression for the decimal string DFA C*·*15 2.58 A regular language with a large minimal DFA C*·*16 2.59 Exponential DFA blow-up C*·*16

Action Routines

The Binding of Referencing Environments

3.30 Deep and shallow binding 152 3.31 Binding rules with static scoping 154 3.32 Returning a ﬁrst-class subroutine in Scheme 156 3.33 An object closure in Java 157 3.34 Delegates in C# 158 3.35 Delegates and unlimited extent 158 3.36 Function objects in C++ 158 3.37 A lambda expression in C# 159 3.38 Variety of lambda syntax 159 3.39 A simple lambda expression in C++11 160 3.40 Variable capture in C++ lambda expres- sions 161 3.41 Lambda expressions in Java 8 162

## 4.12 Top-down action routines to build a syntax tree 198 4.13 Recursive descent and action routines 199

Space Management for Attributes

4.19 Stack trace for bottom-up parse, with action routines C*·*45 4.20 Finding inherited attributes in “buried” records C*·*46 4.21 Grammar fragment requiring context C*·*47 4.22 Semantic hooks for context C*·*47 4.23 Semantic hooks that break an LR CFG C*·*48 4.24 Action routines in the trailing part C*·*49 4.25 Left factoring in lieu of semantic hooks C*·*49 4.26 Operation of an LL attribute stack C*·*50 4.27 Ad hoc management of a semantic stack C*·*53 4.28 Processing lists with an attribute stack C*·*54 4.29 Processing lists with a semantic stack C*·*55

Macro Expansion

## 3.42 A simple assembly macro 162 3.43 Preprocessor macros in C 163 3.44 “Gotchas” in C macros 163

Tree Grammars and Syntax Tree Decoration

Separate Compilation

4.14 Bottom-up CFG for calculator language with types 201 4.15 Syntax tree to average an integer and a real 201 4.16 Tree grammar for the calculator language with types 201 4.17 Tree AG for the calculator language with types 203 4.18 Decorating a tree with the AG of Example 4.17 206

## 3.50 Namespaces in C++ C*·*39 3.51 Using names from another namespace C*·*39 3.52 Packages in Java C*·*40 3.53 Using names from another package C*·*40 3.54 Multipart package names C*·*41

**Chapter 4: Semantic Analysis**

The Role of the Semantic Analyzer

## 4.1 Assertions in Java 182 4.2 Assertions in C 183

**Chapter 5: Target Machine Architecture**

The Memory Hierarchy

Attribute Grammars

## 5.1 Memory hierarchy stats C*·*61

## 4.3 Bottom-up CFG for constant expressions 184 4.4 Bottom-up AG for constant expressions 185 4.5 Top-down AG to count the elements of a list 185

Data Representation

## 5.2 Big- and little-endian C*·*63 5.3 Hexadecimal numbers C*·*65 5.4 Two’s complement C*·*66 5.5 Overﬂow in two’s complement addition C*·*66 5.6 Biased exponents C*·*68 5.7 IEEE ﬂoating-point C*·*68

Evaluating Attributes

4.6 Decoration of a parse tree 187 4.7 Top-down CFG and parse tree for subtraction 188 4.8 Decoration with left-to-right attribute ﬂow 188 4.9 Top-down AG for subtraction 189 4.10 Top-down AG for constant expressions 189 4.11 Bottom-up and top-down AGs to build a syntax tree 193

Instruction Set Architecture (ISA)

## 5.8 An if statement in x86 assembler C*·*72 5.9 Compare and test instructions C*·*73 5.10 Conditional move C*·*73

Architecture and Implementation

## 6.34 Short-circuited expressions 243 6.35 Saving time with short-circuiting 243 6.36 Short-circuit pointer chasing 244 6.37 Short-circuiting and other errors 244 6.38 Optional short-circuiting 245

## 5.11 The x86 ISA C*·*80 5.12 The ARM ISA C*·*81 5.13 x86 and ARM register sets C*·*82

Compiling for Modern Processors

Structured and Unstructured Flow

5.14 Performance* ̸*= clock rate C*·*88 5.15 Filling a load delay slot C*·*91 5.16 Renaming registers for scheduling C*·*92 5.17 Register allocation for a simple loop C*·*93 5.18 Register allocation and instruction scheduling C*·*95

6.39 Control ﬂow with gotos in Fortran 246 6.40 Escaping a nested subroutine 247 6.41 Structured nonlocal transfers 248 6.42 Error checking with status codes 249 6.43 A simple Ruby continuation 250 6.44 Continuation reuse and unlimited extent 251

**Chapter 6: Control Flow**

Sequencing

Expression Evaluation

## 6.45 Side effects in a random number generator 252

6.1 A typical function call 225 6.2 Typical operators 225 6.3 Cambridge Polish (preﬁx) notation 225 6.4 Juxtaposition in ML 225 6.5 Mixﬁx notation in Smalltalk 226 6.6 Conditional expressions 226 6.7 A complicated Fortran expression 226 6.8 Precedence in four inﬂuential languages 227 6.9 A “gotcha” in Pascal precedence 227 6.10 Common rules for associativity 227 6.11 User-deﬁned precedence and associativ- ity in Haskell 228 6.12 L-values and r-values 230 6.13 L-values in C 230 6.14 L-values in C++ 231 6.15 Variables as values and references 231 6.16 Wrapper classes 232 6.17 Boxing in Java 5 and C# 232 6.18 Expression orientation in Algol 68 233 6.19 A “gotcha” in C conditions 234 6.20 Updating assignments 234 6.21 Side effects and updates 235 6.22 Assignment operators 235 6.23 Preﬁx and postﬁx inc/dec 235 6.24 Advantages of postﬁx inc/dec 236 6.25 Simple multiway assignment 236 6.26 Advantages of multiway assignment 236 6.27 Programs outlawed by deﬁnite assign- ment 239 6.28 Indeterminate ordering 240 6.29 A value that depends on ordering 241 6.30 An optimization that depends on ordering 241 6.31 Optimization and mathematical “laws” 242 6.32 Overﬂow and arithmetic “identities” 243 6.33 Reordering and numerical stability 243

Selection

6.46 Selection in Algol 60 253 6.47 elsif/elif 253 6.48 cond in Lisp 253 6.49 Code generation for a Boolean condition 254 6.50 Code generation for short-circuiting 255 6.51 Short-circuit creation of a Boolean value 255 6.52 case statements and nested ifs 256 6.53 Translation of nested ifs 257 6.54 Jump tables 257 6.55 Fall-through in C switch statements 260

Iteration

6.56 Fortran 90 do loop 262 6.57 Modula-2 for loop 262 6.58 Obvious translation of a for loop 262 6.59 for loop translation with test at the bottom 263 6.60 for loop translation with an iteration count 263 6.61 A “gotcha” in the naive loop translation 263 6.62 Changing the index in a for loop 265 6.63 Inspecting the index after a for loop 265 6.64 Combination (for) loop in C 267 6.65 C for loop with a local index 268 6.66 Simple iterator in Python 268 6.67 Python iterator for tree enumeration 269 6.68 Java iterator for tree enumeration 270 6.69 Iteration in C++11 270 6.70 Passing the “loop body” to an iterator in Scheme 272 6.71 Iteration with blocks in Smalltalk 272 6.72 Iterating with procs in Ruby 273 6.73 Imitating iterators in C 274

6.89 Simple generator in Icon C*·*107 6.90 A generator inside an expression C*·*107 6.91 Generating in search of success C*·*108 6.92 Backtracking with multiple generators C*·*108 6.74 while loop in Algol-W 275 6.75 Post-test loop in Pascal and Modula 275 6.76 Post-test loop in C 275 6.77 break statement in C 276 6.78 Exiting a nested loop in Ada 276 6.79 Exiting a nested loop in Perl 276

## 7.13 Emulating distinguished enum values in Java 309 7.14 Subranges in Pascal 309 7.15 Subranges in Ada 310 7.16 Space requirements of subrange type 310

Type Checking

7.17 Trivial differences in type 313 7.18 Other minor differences in type 313 7.19 The problem with structural equivalence 314 7.20 Alias types 314 7.21 Semantically equivalent alias types 315 7.22 Semantically distinct alias types 315 7.23 Derived types and subtypes in Ada 315 7.24 Name vs structural equivalence 316 7.25 Contexts that expect a given type 316 7.26 Type conversions in Ada 317 7.27 Type conversions in C 318 7.28 Unchecked conversions in Ada 319 7.29 Conversions and nonconverting casts in C++ 319 7.30 Coercion in C 320 7.31 Coercion vs overloading of addends 322 7.32 Java container of Object 323 7.33 Inference of subrange types 324 7.34 Type inference for sets 325 7.35 var declarations in C# 325 7.36 Avoiding messy declarations 325 7.37 decltype in C++11 326 7.38 Fibonacci function in OCaml 327 7.39 Checking with explicit types 327 7.40 Expression types 328 7.41 Type inconsistency 328 7.42 Polymorphic functions 329 7.43 A simple instance of uniﬁcation 330

Recursion

6.80 A “naturally iterative” problem 278 6.81 A “naturally recursive” problem 278 6.82 Implementing problems “the other way” 278 6.83 Iterative implementation of tail recursion 279 6.84 By-hand creation of tail-recursive code 279 6.85 Naive recursive Fibonacci function 280 6.86 Linear iterative Fibonacci function 281 6.87 Efﬁcient tail-recursive Fibonacci function 281 6.88 Lazy evaluation of an inﬁnite data structure 283 6.93 Avoiding asymmetry with non- determinism C*·*110 6.94 Selection with guarded commands C*·*110 6.95 Looping with guarded commands C*·*111 6.96 Nondeterministic message receipt C*·*112 6.97 Nondeterministic server in SR C*·*112 6.98 Naive (unfair) implementation of non- determinism C*·*113 6.99 “Gotcha” in round-robin implementation of nondeterminism C*·*113

**Chapter 7: Type Systems**

## 7.1 Operations that leverage type informa- tion 297 7.2 Errors captured by type information 297 7.3 Types as a source of “may alias” informa- tion 298

Parametric Polymorphism

7.44 Finding the minimum in OCaml or Haskell 331 7.45 Implicit polymorphism in Scheme 332 7.46 Duck typing in Ruby 332 7.47 Generic min function in Ada 333 7.48 Generic queues in C++ 333 7.49 Generic parameters 333 7.50 with constraints in Ada 336 7.51 Generic sorting routine in Java 336 7.52 Generic sorting routine in C# 337 7.53 Generic sorting routine in C++ 337 7.54 Generic class instance in C++ 338 7.55 Generic subroutine instance in Ada 338 7.56 Implicit instantiation in C++ 338 7.58 Generic arbiter class in C++ C*·*119

Overview

7.4 void (trivial) type 303 7.5 Making do without void 303 7.6 Option types in OCaml 303 7.7 Option types in Swift 304 7.8 Aggregates in Ada 304 7.9 Enumerations in Pascal 307 7.10 Enumerations as constants 308 7.11 Converting to and from enumeration type 308 7.12 Distinguished values for enums 308

7.59 Template function bodies moved to a .c ﬁle C*·*121 7.60 extern templates in C++11 C*·*122 7.61 Instantiation-time errors in C++ tem- plates C*·*122 7.62 Generic Arbiter class in Java C*·*124 7.63 Wildcards and bounds on Java generic parameters C*·*125 7.64 Type erasure and implicit casts C*·*126 7.65 Unchecked warnings in Java C*·*127 7.66 Java generics and built-in types C*·*127 7.67 Sharing generic implementations in C# C*·*128 7.68 C# generics and built-in types C*·*128 7.69 Generic Arbiter class in C# C*·*128 7.70 Contravariance in the Arbiter interface C*·*128 7.71 Covariance C*·*130 7.72 Chooser as a delegate C*·*130

8.17 Array slice operations 362 8.18 Local arrays of dynamic shape in C 365 8.19 Stack allocation of elaborated arrays 365 8.20 Elaborated arrays in Fortran 90 366 8.21 Dynamic strings in Java and C# 367 8.22 Row-major vs column-major array layout 368 8.23 Array layout and cache performance 368 8.24 Contiguous vs row-pointer array layout 370 8.25 Indexing a contiguous array 371 8.26 Static and dynamic portions of an array index 372 8.27 Indexing complex structures 373 8.28 Indexing a row-pointer array 374

Strings

## 8.29 Character escapes in C and C++ 375 8.30 char* assignment in C 376

Equality Testing and Assignment

Sets

## 7.57 Equality testing in Scheme 340

## 8.31 Set types in Pascal 376 8.32 Emulating a set with a map in Go 377

**Chapter 8: Composite Types**

Records (Structures)

Pointers and Recursive Types

8.1 A C struct 352 8.2 Accessing record ﬁelds 352 8.3 Nested records 352 8.4 OCaml records and tuples 353 8.5 Memory layout for a record type 353 8.6 Nested records as values 354 8.7 Nested records as references 354 8.8 Layout of packed types 354 8.9 Assignment and comparison of records 355 8.10 Minimizing holes by sorting ﬁelds 356 8.11 A union in C 357 8.12 Motivation for variant records 358 8.59 Nested structs and unions in tradi- tional C C*·*136 8.60 A variant record in Pascal C*·*137 8.61 Anonymous unions in C11 and C++11 C*·*137 8.62 Breaking type safety with unions C*·*138 8.63 Type-safe unions in OCaml C*·*139 8.64 Ada variants and tags (discriminants) C*·*140 8.65 A discriminated subtype in Ada C*·*141 8.66 Discriminated array in Ada C*·*141 8.67 Derived types as an alternative to unions C*·*142

8.33 Tree type in OCaml 379 8.34 Tree type in Lisp 379 8.35 Mutually recursive types in OCaml 380 8.36 Tree types in Ada and C 382 8.37 Allocating heap nodes 382 8.38 Object-oriented allocation of heap nodes 382 8.39 Pointer-based tree 382 8.40 Pointer dereferencing 382 8.41 Implicit dereferencing in Ada 383 8.42 Pointer dereferencing in OCaml 383 8.43 Assignment in Lisp 384 8.44 Array names and pointers in C 384 8.45 Pointer comparison and subtraction in C 386 8.46 Pointer and array declarations in C 386 8.47 Arrays as parameters in C 387 8.48 sizeof in C 387 8.49 Explicit storage reclamation 388 8.50 Dangling reference to a stack variable in C++ 388 8.51 Dangling reference to a heap variable in C++ 388 8.68 Dangling reference detection with tombstones C*·*144 8.69 Dangling reference detection with locks and keys C*·*146 8.52 Reference counts and circular structures 391 8.53 Heap tracing with pointer reversal 394

Arrays

## 8.13 Array declarations 359 8.14 Multidimensional arrays 360 8.15 Multidimensional vs built-up arrays 360 8.16 Arrays of arrays in C 361

Lists

9.14 const parameters in C 426 9.15 Reference parameters in C++ 428 9.16 References as aliases in C++ 428 9.17 Simplifying code with an in-line alias 428 9.18 Returning a reference from a function 429 9.19 R-value references in C++11 430 9.20 Subroutines as parameters in Ada 431 9.21 First-class subroutines in Scheme 431 9.22 First-class subroutines in OCaml 432 9.23 Subroutine pointers in C and C++ 432 9.64 Jensen’s device C*·*180 9.24 Default parameters in Ada 433 9.25 Named parameters in Ada 435 9.26 Self-documentation with named parame- ters 436 9.27 Variable number of arguments in C 436 9.28 Variable number of arguments in Java 437 9.29 Variable number of arguments in C# 438 9.30 return statement 438 9.31 Incremental computation of a return value 438 9.32 Explicitly named return values in Go 439 9.33 Multivalue returns 439

8.54 Lists in ML and Lisp 398 8.55 List notation 399 8.56 Basic list operations in Lisp 400 8.57 Basic list operations in OCaml 400 8.58 List comprehensions 400 8.70 Files as a built-in type C*·*150 8.71 The open operation C*·*150 8.72 The close operation C*·*150 8.73 Formatted output in Fortran C*·*152 8.74 Labeled formats C*·*152 8.75 Printing to standard output C*·*153 8.76 Formatted output in Ada C*·*153 8.77 Overloaded put routines C*·*154 8.78 Formatted output in C C*·*154 8.79 Text in format strings C*·*155 8.80 Formatted input in C C*·*155 8.81 Formatted output in C++ C*·*156 8.82 Stream manipulators C*·*157 8.83 Array output in C++ C*·*157 8.84 Changing default format C*·*158

**Chapter 9: Subroutines and Control** **Abstraction**

Exception Handling

Review of Stack Layout

9.34 ON conditions in PL/I 441 9.35 A simple try block in C++ 441 9.36 Nested try blocks 442 9.37 Propagation of an exception out of a called routine 442 9.38 What is an exception? 444 9.39 Parameterized exceptions 444 9.40 Multiple handlers in C++ 445 9.41 Exception handler in OCaml 446 9.42 finally clause in Python 447 9.43 Stacked exception handlers 447 9.44 Multiple exceptions per handler 447 9.45 setjmp and longjmp in C 449

## 9.1 Layout of run-time stack (reprise) 412 9.2 Offsets from frame pointer 412 9.3 Static and dynamic links 412 9.4 Visibility of nested routines 413

Calling Sequences

9.5 A typical calling sequence 415 9.56 Nonlocal access using a display C*·*163 9.57 LLVM/ARM stack layout C*·*167 9.58 LLVM/ARM calling sequence C*·*170 9.59 gcc/x86-32 stack layout C*·*172 9.60 gcc/x86-32 calling sequence C*·*172 9.61 Subroutine closure trampoline C*·*174 9.62 The x86-64 red zone C*·*175 9.63 Register windows on the SPARC C*·*177 9.6 Requesting an inline subroutine 419 9.7 In-lining and recursion 420

Coroutines

9.46 Explicit interleaving of concurrent computations 451 9.47 Interleaving coroutines 451 9.48 Cactus stacks 453 9.49 Switching coroutines 455 9.65 Coroutine-based iterator invocation C*·*183 9.66 Coroutine-based iterator implementation C*·*183 9.67 Iterator usage in C# C*·*184 9.68 Implementation of C# iterators C*·*185 9.69 Sequential simulation of a complex physical system C*·*187

Parameter Passing

9.8 Inﬁx operators 422 9.9 Control abstraction in Lisp and Smalltalk 422 9.10 Passing an argument to a subroutine 423 9.11 Value and reference parameters 423 9.12 Call by value/result 424 9.13 Emulating call-by-reference in C 424

Initialization and Finalization

9.70 Initialization of a coroutine-based trafﬁc simulation C*·*187 9.71 Traversing a street segment in the trafﬁc simulation C*·*188 9.72 Scheduling a coroutine for future execution C*·*188 9.73 Queueing cars at a trafﬁc light C*·*188 9.74 Waiting at a light C*·*189 9.75 Sleeping in anticipation of future execu- tion C*·*189

10.25 Naming constructors in Eiffel 496 10.26 Metaclasses in Smalltalk 497 10.27 Declarations and constructors in C++ 498 10.28 Copy constructors 499 10.29 Temporary objects 499 10.30 Return value optimization 500 10.31 Eiffel constructors and expanded objects 501 10.32 Speciﬁcation of base class constructor arguments 502 10.33 Speciﬁcation of member constructor arguments 502 10.34 Constructor forwarding 503 10.35 Invocation of base class constructor in Java 503 10.36 Reclaiming space with destructors 504

Events

9.50 Signal trampoline 457 9.51 An event handler in C# 459 9.52 An anonymous delegate handler 459 9.53 An event handler in Java 460 9.54 An anonymous inner class handler 460 9.55 Handling an event with a lambda expression 460

Dynamic Method Binding

10.37 Derived class objects in a base class context 505 10.38 Static and dynamic method binding 506 10.39 The need for dynamic binding 507 10.40 Virtual methods in C++ and C# 508 10.41 Class-wide types in Ada 95 508 10.42 Abstract methods in Java and C# 508 10.43 Abstract methods in C++ 509 10.44 Vtables 509 10.45 Implementation of a virtual method call 509 10.46 Implementation of single inheritance 510 10.47 Casts in C++ 511 10.48 Reverse assignment in Eiffel and C# 511 10.49 Virtual methods in an object closure 513 10.50 Encapsulating arguments 514

**Chapter 10: Data Abstraction and Object** **Orientation**

Object-Oriented Programming

10.1 list_node class in C++ 473 10.2 list class that uses list_node 473 10.3 Declaration of in-line (expanded) objects 475 10.4 Constructor arguments 475 10.5 Method declaration without deﬁnition 476 10.6 Separate method deﬁnition 477 10.7 property and indexer methods in C# 477 10.8 queue class derived from list 478 10.9 Hiding members of a base class 479 10.10 Redeﬁning a method in a derived class 479 10.11 Accessing base class members 480 10.12 Renaming methods in Eiffel 480 10.13 A queue that* contains* a list 480 10.14 Base class for general-purpose lists 481 10.15 The problem with type-speciﬁc exten- sions 482 10.16 How do you name an unknown type? 483 10.17 Generic lists in C++ 483

Mix-In Inheritance

10.51 The motivation for interfaces 516 10.52 Mixing interfaces into a derived class 516 10.53 Compile-time implementation of mix-in inheritance 517 10.54 Use of default methods 520 10.55 Implementation of default methods 520 10.56 Deriving from two base classes 521 10.57 Deriving from two base classes (reprise) C*·*194 10.58 (Nonrepeated) multiple inheritance C*·*194 10.59 Method invocation with multiple inheri- tance C*·*195 10.60 this correction C*·*196 10.61 Methods found in more than one base class C*·*197 10.62 Overriding an ambiguous method C*·*197 10.63 Repeated multiple inheritance C*·*198 10.64 Shared inheritance in C++ C*·*199

Encapsulation and Inheritance

10.18 Data hiding in Ada 486 10.19 The hidden this parameter 487 10.20 Hiding inherited methods 488 10.21 protected base class in C++ 488 10.22 Inner classes in Java 490 10.23 List and queue abstractions in Ada 2005 491 10.24 Extension methods in C# 494

## 10.65 Replicated inheritance in Eiffel C*·*199 10.66 Using replicated inheritance C*·*200 10.67 Overriding methods with shared inheri- tance C*·*201 10.68 Implementation of shared inheritance C*·*201

11.28 A recursive nested function (reprise of Example 7.38) 555 11.29 Polymorphic list operators 555 11.30 List notation 556 11.31 Array notation 556 11.32 Strings as character arrays 557 11.33 Tuple notation 557 11.34 Record notation 557 11.35 Mutable ﬁelds 558 11.36 References 558 11.37 Variants as enumerations 558 11.38 Variants as unions 558 11.39 Recursive variants 559 11.40 Pattern matching of parameters 559 11.41 Pattern matching in local declarations 560 11.42 The match construct 560 11.43 Guards 561 11.44 The as keyword 561 11.45 The function keyword 561 11.46 Run-time pattern matching 562 11.47 Coverage of patterns 562 11.48 Pattern matching against a tuple returned from a function 562 11.49 An if without an else 563 11.50 Insertion sort in OCaml 563 11.51 A simple exception 564 11.52 An exception with arguments 564 11.53 Catching an exception 564 11.54 Simulating a DFA in OCaml 565

Object-Oriented Programming Revisited

10.69 Operations as messages in Smalltalk C*·*204 10.70 Mixﬁx messages C*·*204 10.71 Selection as an ifTrue: ifFalse: message C*·*205 10.72 Iterating with messages C*·*205 10.73 Blocks as closures C*·*206 10.74 Logical looping with messages C*·*206 10.75 Deﬁning control abstractions C*·*206 10.76 Recursion in Smalltalk C*·*207

**Chapter 11: Functional Languages**

Historical Origins

Functional Programming Concepts

A Bit of Scheme

11.1 The read-eval-print loop 539 11.2 Signiﬁcance of parentheses 540 11.3 Quoting 540 11.4 Dynamic typing 540 11.5 Type predicates 541 11.6 Liberal syntax for symbols 541 11.7 lambda expressions 541 11.8 Function evaluation 542 11.9 if expressions 542 11.10 Nested scopes with let 542 11.11 Global bindings with define 543 11.12 Basic list operations 543 11.13 List search functions 544 11.14 Searching association lists 545 11.15 Multiway conditional expressions 545 11.16 Assignment 545 11.17 Sequencing 545 11.18 Iteration 546 11.19 Evaluating data as code 547 11.20 Simulating a DFA in Scheme 548

Evaluation Order Revisited

11.55 Applicative and normal-order evaluation 567 11.56 Normal-order avoidance of unnecessary work 568 11.57 Avoiding work with lazy evaluation 570 11.58 Stream-based program execution 571 11.59 Interactive I/O with streams 572 11.60 Pseudorandom numbers in Haskell 572 11.61 The state of the IO monad 574 11.62 Functional composition of actions 574 11.63 Streams and the I/O monad 575

Higher-Order Functions

11.64 map function in Scheme 576 11.65 Folding (reduction) in Scheme 576 11.66 Folding in OCaml 576 11.67 Combining higher-order functions 576 11.68 Partial application with currying 577 11.69 General-purpose curry function 577 11.70 Tuples as OCaml function arguments 578 11.71 Optional parentheses on singleton arguments 578

A Bit of OCaml

11.21 Interacting with the interpreter 551 11.22 Function call syntax 551 11.23 Function values 552 11.24 unit type 552 11.25 “Physical” and “structural” comparison 553 11.26 Outermost declarations 554 11.27 Nested declarations 555

12.16 Backtracking and instantiation 599 12.17 Order of rule evaluation 600 12.18 Inﬁnite regression 600 12.19 Tic-tac-toe in Prolog 600 12.20 The cut 604 12.21 *\*+ and its implementation 605 12.22 Pruning unwanted answers with the cut 605 12.23 Using the cut for selection 605 12.24 Looping with fail 605 12.25 Looping with an unbounded generator 606 12.26 Character input with get 607 12.27 Prolog programs as data 607 12.28 Modifying the Prolog database 608 12.29 Tic-tac-toe (full game) 608 12.30 The functor predicate 608 12.31 Creating terms at run time 610 12.32 Pursuing a dynamic goal 611 12.33 Custom database perusal 611 12.34 Predicates as mathematical objects 612 12.39 Propositions C*·*226 12.40 Different ways to say things C*·*226 12.41 Conversion to clausal form C*·*227 12.42 Conversion to Prolog C*·*228 12.43 Disjunctive left-hand side C*·*228 12.44 Empty left-hand side C*·*229 12.45 Theorem proving as a search for contradiction C*·*229 12.46 Skolem constants C*·*230 12.47 Skolem functions C*·*230 12.48 Limitations of Skolemization C*·*230

11.72 Simple curried function in OCaml 578 11.73 Shorthand notation for currying 579 11.74 Building fold_left in OCaml 579 11.75 Currying in OCaml vs Scheme 580 11.76 Declarative (nonconstructive) function deﬁnition 580 11.77 Functions as mappings C*·*212 11.78 Functions as sets C*·*212 11.79 Functions as powerset elements C*·*213 11.80 Function spaces C*·*213 11.81 Higher-order functions as sets C*·*213 11.82 Curried functions as sets C*·*213 11.83 Juxtaposition as function application C*·*214 11.84 Lambda calculus syntax C*·*214 11.85 Binding parameters with* λ* C*·*214 11.86 Free variables C*·*215 11.87 Naming functions for future reference C*·*215 11.88 Evaluation rules C*·*215 11.89 Delta reduction for arithmetic C*·*215 11.90 Eta reduction C*·*216 11.91 Reduction to simplest form C*·*216 11.92 Nonterminating applicative-order reduc- tion C*·*217 11.93 Booleans and conditionals C*·*218 11.94 Beta abstraction for recursion C*·*218 11.95 The ﬁxed-point combinator** Y** C*·*218 11.96 Lambda calculus list operators C*·*219 11.97 List operator identities C*·*219 11.98 Nesting of lambda expressions C*·*221 11.99 Paired arguments and currying C*·*221

Functional Programming in Perspective

Logic Programming in Perspective

**Chapter 12: Logic Languages**

## 12.35 Sorting incredibly slowly 613 12.36 Quicksort in Prolog 614 12.37 Negation as failure 615 12.38 Negation and instantiation 616

Logic Programming Concepts

## 12.1 Horn clauses 592 12.2 Resolution 592 12.3 Uniﬁcation 592

**Chapter 13: Concurrency**

Background and Motivation

Prolog

## 13.1 Independent tasks in C# 626 13.2 A simple race condition 626 13.3 Multithreaded web browser 627 13.4 Dispatch loop web browser 628 13.5 The cache coherence problem 632

12.4 Atoms, variables, scope, and type 593 12.5 Structures and predicates 593 12.6 Facts and rules 593 12.7 Queries 594 12.8 Resolution in Prolog 595 12.9 Uniﬁcation in Prolog and ML 595 12.10 Equality and uniﬁcation 595 12.11 Uniﬁcation without instantiation 596 12.12 List notation in Prolog 596 12.13 Functions, predicates, and two-way rules 597 12.14 Arithmetic and the is predicate 597 12.15 Search tree exploration 598

Concurrent Programming Fundamentals

## 13.6 General form of co-begin 638 13.7 Co-begin in OpenMP 639 13.8 A parallel loop in OpenMP 639 13.9 A parallel loop in C# 639 13.10 Forall in Fortran 95 640

13.57 Datagram messages in Java C*·*238 13.58 Connection-based messages in Java C*·*238 13.59 Three main options for send semantics C*·*240 13.60 Buffering-dependent deadlock C*·*241 13.61 Acknowledgments C*·*242 13.62 Bounded buffer in Ada 83 C*·*245 13.63 Timeout and distributed termination C*·*246 13.64 Bounded buffer in Go C*·*246 13.65 Bounded buffer in Erlang C*·*247 13.66 Peeking at messages in Erlang C*·*247 13.67 An RPC server system C*·*251

13.11 Reduction in OpenMP 641 13.12 Elaborated tasks in Ada 641 13.13 Co-begin vs fork/join 642 13.14 Task types in Ada 642 13.15 Thread creation in Java 2 643 13.16 Thread creation in C# 644 13.17 Thread pools in Java 5 645 13.18 Spawn and sync in Cilk 645 13.19 Modeling subroutines with fork/join 646 13.20 Multiplexing threads on processes 647 13.21 Cooperative multithreading on a unipro- cessor 648 13.22 A race condition in preemptive multi- threading 650 13.23 Disabling signals during context switch 651

**Chapter 14: Scripting Languages**

What Is a Scripting Language?

## 14.1 Trivial programs in conventional and scripting languages 702 14.2 Coercion in Perl 703

Implementing Synchronization

13.24 The basic test and set lock 654 13.25 Test-and-test and set 654 13.26 Barriers in ﬁnite element analysis 655 13.27 The “sense-reversing” barrier 656 13.28 Java 7 phasers 656 13.29 Atomic update with CAS 657 13.30 The M&S queue 658 13.31 Write buffers and consistency 659 13.32 Distributed consistency 661 13.33 Using volatile to avoid a data race 662 13.34 Scheduling threads on processes 663 13.35 A race condition in thread scheduling 664 13.36 A “spin-then-yield” lock 665 13.37 The bounded buffer problem 666 13.38 Semaphore implementation 667 13.39 Bounded buffer with semaphores 668

Problem Domains

14.3 “Wildcards” and “globbing” 706 14.4 For loops in the shell 706 14.5 A whole loop on one line 706 14.6 Conditional tests in the shell 707 14.7 Pipes 708 14.8 Output redirection 708 14.9 Redirection of stderr and stdout 708 14.10 Heredocs (in-line input) 709 14.11 Problematic spaces in ﬁle names 709 14.12 Single and double quotes 709 14.13 Subshells 709 14.14 Brace-quoted blocks in the shell 710 14.15 Pattern-based list generation 710 14.16 User-deﬁned shell functions 710 14.17 The #! convention in script ﬁles 711 14.18 Extracting HTML headers with sed 713 14.19 One-line scripts in sed 713 14.20 Extracting HTML headers with awk 714 14.21 Fields in awk 715 14.22 Capitalizing a title in awk 715 14.23 Extracting HTML headers with Perl 716 14.24 “Force quit” script in Perl 718 14.25 “Force quit” script in Python 720 14.26 Method call syntax in Ruby 722 14.27 “Force quit” script in Ruby 722 14.28 Numbering lines with Emacs Lisp 725

Language-Level Constructs

13.40 Bounded buffer monitor 670 13.41 How to wait for a signal (hint or absolute) 671 13.42 Original CCR syntax 674 13.43 synchronized statement in Java 676 13.44 notify as hint in Java 676 13.45 Lock variables in Java 5 677 13.46 Multiple Conditions in Java 5 678 13.47 A simple atomic block 680 13.48 Bounded buffer with transactions 680 13.49 Translation of an atomic block 681 13.50 future construct in Multilisp 684 13.51 Futures in C# 684 13.52 Futures in C++11 685 13.53 Naming processes, ports, and entries C*·*235 13.54 entry calls in Ada C*·*235 13.55 Channels in Go C*·*236 13.56 Remote invocation in Go C*·*237

Scripting the World Wide Web

## 14.29 Remote monitoring with a CGI script 728 14.30 Adder web form with a CGI script 728 14.31 Remote monitoring with a PHP script 731 14.32 A fragmented PHP script 731

14.74 Inheritance in Perl 759 14.75 Inheritance via use base 759 14.76 Prototypes in JavaScript 760 14.77 Overriding instance methods in JavaScript 761 14.78 Inheritance in JavaScript 761 14.79 Constructors in Python and Ruby 762 14.80 Naming class members in Python and Ruby 762

14.33 Adder web form with a PHP script 732 14.34 Self-posting Adder web form 732 14.35 Adder web form in JavaScript 734 14.36 Embedding an applet in a web page 735 14.81 Content versus presentation in HTML C*·*258 14.82 Well-formed XHTML C*·*259 14.83 XHTML to display a favorite quote C*·*261 14.84 XPath names for XHTML elements C*·*262 14.85 Creating a reference list with XSLT C*·*262

**Chapter 15: Building a Runnable Program**

Innovative Features

Back-End Compiler Structure

14.37 Scoping rules in Python 740 14.38 Superassignment in R 740 14.39 Static and dynamic scoping in Perl 741 14.40 Accessing globals in Perl 742 14.41 Basic operations in POSIX REs 744 14.42 Extra quantiﬁers in POSIX REs 744 14.43 Zero-length assertions 744 14.44 Character classes 744 14.45 The dot (.) character 745 14.46 Negation and quoting in character classes 745 14.47 Predeﬁned POSIX character classes 745 14.48 RE matching in Perl 745 14.49 Negating a match in Perl 746 14.50 RE substitution in Perl 746 14.51 Trailing modiﬁers on RE matches 746 14.52 Greedy and minimal matching 748 14.53 Minimal matching of HTML headers 748 14.54 Variable interpolation in extended REs 748 14.55 Variable capture in extended REs 749 14.56 Backreferences in extended REs 750 14.57 Dissecting a ﬂoating-point literal 750 14.58 Implicit capture of preﬁx, match, and sufﬁx 750 14.59 Coercion in Ruby and Perl 751 14.60 Coercion and context in Perl 751 14.61 Explicit conversion in Ruby 752 14.62 Perl arrays 753 14.63 Perl hashes 753 14.64 Arrays and hashes in Python and Ruby 754 14.65 Array access methods in Ruby 755 14.66 Tuples in Python 755 14.67 Sets in Python 755 14.68 Conﬂated types in PHP, Tcl, and JavaScript 755 14.69 Multidimensional arrays in Python and other languages 755 14.70 Scalar and list context in Perl 756 14.71 Using wantarray to determine calling context 757 14.72 A simple class in Perl 757 14.73 Invoking methods in Perl 758

## 15.1 Phases of compilation 776 15.2 GCD program abstract syntax tree (reprise) 776

Intermediate Forms

## 15.3 Intermediate forms in Figure 15.1 781 15.19 GCD program in GIMPLE C*·*273 15.20 An RTL insn sequence C*·*276 15.4 Computing Heron’s formula 783

Code Generation

## 15.5 Simpler compiler structure 784 15.6 An attribute grammar for code genera- tion 785 15.7 Stack-based register allocation 787 15.8 GCD program target code 788

Address Space Organization

## 15.9 Linux address space layout 792

Assembly

15.10 Assembly as a ﬁnal compiler pass 792 15.11 Direct generation of object code 794 15.12 Compressing nops 794 15.13 Relative and absolute branches 794 15.14 Pseudoinstructions 795 15.15 Assembler directives 795 15.16 Encoding of addresses in object ﬁles 796

Linking

15.17 Static linking 798 15.18 Checksumming headers for consistency 799 15.21 PIC under x86/Linux C*·*280 15.22 PC-relative addressing on the x86 C*·*282 15.23 Dynamic linking in Linux on the x86 C*·*282

**Chapter 16: Run-Time Program** **Management**

**Chapter 17: Code Improvement**

Virtual Machines

17.1 Code improvement phases C*·*299 17.2 Elimination of redundant loads and stores C*·*301 17.3 Constant folding C*·*301 17.4 Constant propagation C*·*301 17.5 Common subexpression elimination C*·*302 17.6 Copy propagation C*·*302 17.7 Strength reduction C*·*302 17.8 Elimination of useless instructions C*·*303 17.9 Exploitation of the instruction set C*·*303 17.10 The combinations subroutine C*·*305 17.11 Syntax tree and naive control ﬂow graph C*·*305 17.12 Result of local redundancy elimination C*·*310 17.13 Conversion to SSA form C*·*313 17.14 Global value numbering C*·*313 17.15 Data ﬂow equations for available expressions C*·*317 17.16 Fixed point for available expressions C*·*317 17.17 Result of global common subexpression elimination C*·*318 17.18 Edge splitting transformations C*·*319 17.19 Data ﬂow equations for live variables C*·*321 17.20 Fixed point for live variables C*·*321 17.21 Data ﬂow equations for reaching deﬁnitions C*·*324 17.22 Result of hoisting loop invariants C*·*325 17.23 Induction variable strength reduction C*·*325 17.24 Induction variable elimination C*·*326 17.25 Result of induction variable optimization C*·*326 17.26 Remaining pipeline delays C*·*329 17.27 Value dependence DAG C*·*329 17.28 Result of instruction scheduling C*·*331 17.29 Result of loop unrolling C*·*332 17.30 Result of software pipelining C*·*333 17.31 Loop interchange C*·*337 17.32 Loop tiling (blocking) C*·*337 17.33 Loop distribution C*·*339 17.34 Loop fusion C*·*339 17.35 Obtaining a perfect loop nest C*·*339 17.36 Loop-carried dependences C*·*340 17.37 Loop reversal and interchange C*·*341 17.38 Loop skewing C*·*341 17.39 Coarse-grain parallelization C*·*343 17.40 Strip mining C*·*343 17.41 Live ranges of virtual registers C*·*344 17.42 Register coloring C*·*344 17.43 Optimized combinations subroutine C*·*346

## 16.2 Constants for “Hello, world” 813 16.3 Bytecode for a list insert operation 818 16.39 Generics in the CLI and JVM C*·*291 16.40 CIL for a list insert operation C*·*292

Late Binding of Machine Code

16.4 When is in-lining safe? 824 16.5 Speculative optimization 825 16.6 Dynamic compilation in the CLR 826 16.7 Dynamic compilation in CMU Common Lisp 827 16.8 Compilation of Perl 827 16.9 The Mac 68K emulator 829 16.10 The Transmeta Crusoe processor 829 16.11 Static binary translation 830 16.12 Dynamic binary translation 830 16.13 Mixed interpretation and translation 830 16.14 Transparent dynamic translation 831 16.15 Translation and virtualization 831 16.16 The Dynamo dynamic optimizer 831 16.17 The ATOM binary rewriter 833

Inspection/Introspection

16.18 Finding the concrete type of a reference variable 837 16.19 What* not* to do with reﬂection 838 16.20 Java class-naming conventions 838 16.21 Getting information on a particular class 839 16.22 Listing the methods of a Java class 839 16.23 Calling a method with reﬂection 840 16.24 Reﬂection facilities in Ruby 841 16.25 User-deﬁned annotations in Java 842 16.26 User-deﬁned annotations in C# 842 16.27 javadoc 842 16.28 Intercomponent communication 843 16.29 Attributes for LINQ 843 16.30 The Java Modeling Language 844 16.31 Java annotation processors 845 16.32 Setting a breakpoint 847 16.33 Hardware breakpoints 847 16.34 Setting a watchpoint 847 16.35 Statistical sampling 848 16.36 Call graph proﬁling 848 16.37 Finding basic blocks with low IPC 849 16.38 Haswell performance counters 849

