## B

### Language Design and Language

### **Implementation**

Throughout this text, we have had occasion to remark on the many connections between language design and language implementation. Some of the more direct connections have been highlighted in separate sidebars. We list those sidebars here.

**Chapter 1: Introduction**

1.1 Introduction 10 1.2 Compiled and interpreted languages 18 1.3 The early success of Pascal 22 1.4 Powerful development environments 25

**Chapter 2: Programming Language Syntax**

2.1 Contextual keywords 46 2.2 Formatting restrictions 48 2.3 Nested comments 55 2.4 Recognizing multiple kinds of token 63 2.5 Longest possible tokens 64 2.6 The dangling else 81 2.7 Recursive descent and table-driven LL parsing 86

**Chapter 3: Names, Scopes, and Bindings**

3.1 Binding time 117 3.2 Recursion in Fortran 119 3.3 Mutual recursion 131 3.4 Redeclarations 134 3.5 Modules and separate compilation 140 3.6 Dynamic scoping 143 3.7 Pointers in C and Fortran 146 3.8 User-deﬁned operators in OCaml 149 3.9 Binding rules and extent 156 3.10 Functions and function objects 161

3.11 Generics as macros 163 3.12 Separate compilation C*·*41

**Chapter 4: Semantic Analysis**

4.1 Dynamic semantic checks 182 4.2 Forward references 193 4.3 Attribute evaluators 198

**Chapter 5: Target Machine Architecture**

5.2 The processor/memory gap C*·*62 5.3 How much is a megabyte? C*·*66 5.4 Delayed branch instructions C*·*90 5.5 Delayed load instructions C*·*92 5.6 In-line subroutines C*·*97 5.1 Pseudo-assembly notation 218

**Chapter 6: Control Flow**

6.1 Implementing the reference model 232 6.2 Safety versus performance 241 6.3 Evaluation order 242 6.4 Cleaning up continuations 250 6.5 Short-circuit evaluation 255 6.6 Case statements 259 6.7 Numerical imprecision 264 6.8 for loops 267 6.9 “True” iterators and iterator objects 270 6.10 Normal-order evaluation 282 6.11 Nondeterminacy and fairness C*·*114

**Chapter 7: Type Systems**

7.1 Systems programming 299 7.2 Dynamic typing 300 7.3 Multilingual character sets 306 7.4 Decimal types 307 7.5 Multiple sizes of integers 309 7.6 Nonconverting casts 319 7.7 Type classes for overloaded functions in Haskell 329 7.8 Uniﬁcation 331 7.9 Generics in ML 334 7.10 Overloading and polymorphism 336 7.11 Why erasure? C*·*127

**Chapter 8: Composite Types**

8.13 The placement of variant ﬁelds C*·*141 8.3 Is [ ] an operator? 361 8.4 Array layout 370 8.5 Lower bounds on array indices 373 8.6 Implementation of pointers 378 8.7 Stack smashing 385 8.8 Pointers and arrays 386 8.9 Garbage collection 390 8.10 What exactly is garbage? 393 8.11 Reference counts versus tracing 396 8.12 car and cdr 399

**Chapter 9: Subroutines and Control Abstraction**

9.8 Lexical nesting and displays C*·*164 9.9 Leveraging pc = r15 C*·*169 9.10 Executing code in the stack C*·*176 9.1 Hints and directives 420 9.2 In-lining and modularity 421 9.3 Parameter modes 424 9.11 Call by name C*·*181 9.12 Call by need C*·*182 9.4 Structured exceptions 446 9.5 setjmp 449 9.6 Threads and coroutines 452 9.7 Coroutine stacks 453

**Chapter 10: Data Abstraction and Object Orientation**

10.1 What goes in a class declaration? 476 10.2 Containers/collections 484 10.3 The value/reference tradeoff 498 10.4 Initialization and assignment 501 10.5 Initialization of “expanded” objects 502 10.6 Reverse assignment 511 10.7 The fragile base class problem 512 10.8 The cost of multiple inheritance C*·*197

**Chapter 11: Functional Languages**

11.1 Iteration in functional programs 546 11.2 Equality and ordering in SML and Haskell 554 11.3 Type Equivalence in OCaml 560 11.4 Lazy evaluation 570 11.5 Monads 575 11.6 Higher-order functions 577 11.7 Side effects and compilation 582

**Chapter 12: Logic Languages**

12.1 Homoiconic languages 608 12.2 Reﬂection 611 12.3 Implementing logic 613 12.4 Alternative search strategies 614

**Chapter 13: Concurrency**

13.1 What, exactly, is a processor? 632 13.2 Hardware and software communication 636 13.3 Task-parallel and data-parallel computing 643 13.4 Counterintuitive implementation 646 13.5 Monitor signal semantics 672 13.6 The nested monitor problem 673 13.7 Conditional critical regions 674 13.8 Condition variables in Java 677 13.9 Side-effect freedom and implicit synchronization 685 13.10 The semantic impact of implementation issues C*·*241 13.11 Emulation and efﬁciency C*·*243 13.12 Parameters to remote procedures C*·*250

**Chapter 14: Scripting Languages**

14.1 Compiling interpreted languages 702 14.2 Canonical implementations 703 14.3 Built-in commands in the shell 707 14.4 Magic numbers 712 14.5 JavaScript and Java 736 14.6 How far can you trust a script? 737 14.14 W3C and WHATWG C*·*260 14.7 Thinking about dynamic scoping 742 14.8 The grep command and the birth of Unix tools 744 14.9 Automata for regular expressions 746 14.10 Compiling regular expressions 749 14.11 Typeglobs in Perl 754 14.12 Executable class declarations 763 14.13 Worse Is Better 764

**Chapter 15: Building a Runnable Program**

15.1 Postscript 783 15.2 Type checking for separate compilation 799

**Chapter 16: Run-Time Program Management**

16.1 Run-time systems 808 16.2 Optimizing stack-based IF 812 16.3 Veriﬁcation of class ﬁles and bytecode 820

16.7 Assuming a just-in-time compiler C*·*287 16.8 References and pointers C*·*290 16.4 Emulation and interpretation 830 16.5 Creating a sandbox via binary rewriting 835 16.6 DWARF 846

**Chapter 17: Code Improvement**

17.1 Peephole optimization C*·*303 17.2 Basic blocks C*·*304 17.3 Common subexpressions C*·*309 17.4 Pointer analysis C*·*310 17.5 Loop invariants C*·*324 17.6 Control ﬂow analysis C*·*325

