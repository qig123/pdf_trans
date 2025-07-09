# Chapter 3: Names, Scopes, and Bindings

3 Names, Scopes, and Bindings

Early languages such as Fortran, Algol, and Lisp were termed “high level” because their syntax and semantics were signiﬁcantly more abstract—farther from the hardware—than those of the assembly languages they were intended to supplant. Abstraction made it possible to write programs that would run well on a wide variety of machines. It also made programs signiﬁcantly easier for hu- man beings to understand. While machine independence remains important, it is primarily ease of programming that continues to drive the design of modern languages. This chapter is the ﬁrst of six to address core issues in language de- sign. (The others are Chapters 6 through 10.) Much of the current discussion will revolve around the notion of names. A name is a mnemonic character string used to represent something else. Names in most languages are identiﬁers (alphanumeric tokens), though certain other symbols, such as + or :=, can also be names. Names allow us to refer to variables, constants, operations, types, and so on using symbolic identiﬁers rather than low-level concepts like addresses. Names are also essential in the context of a second meaning of the word abstraction. In this second meaning, abstraction is a process by which the programmer associates a name with a potentially compli- cated program fragment, which can then be thought of in terms of its purpose or function, rather than in terms of how that function is achieved. By hiding irrel- evant details, abstraction reduces conceptual complexity, making it possible for the programmer to focus on a manageable subset of the program text at any par- ticular time. Subroutines are control abstractions: they allow the programmer to hide arbitrarily complicated code behind a simple interface. Classes are data ab- stractions: they allow the programmer to hide data representation details behind a (comparatively) simple set of operations. We will look at severalmajor issues related to names. Section 3.1 introduces the notion of binding time, which refers not only to the binding of a name to the thing it represents, but also in general to the notion of resolving any design decision in a language implementation. Section 3.2 outlines the various mechanisms used to allocate and deallocate storage space for objects, and distinguishes between

the lifetime of an object and the lifetime of a binding of a name to that object.1 Most name-to-object bindings are usable only within a limited region of a given high-level program. Section 3.3 explores the scope rules that deﬁne this region; Section 3.4 (mostly on the companion site) considers their implementation. The complete set of bindings in effect at a given point in a program is known as the current referencing environment. Section 3.5 discusses aliasing, in which more than one name may refer to a given object in a given scope, and overloading, in which a name may refer to more than one object in a given scope, depending on the context of the reference. Section 3.6 expands on the notion of scope rules by considering the ways in which a referencing environment may be bound to a subroutine that is passed as a parameter, returned from a function, or stored in a variable. Section 3.7 discusses macro expansion, which can introduce new names via textual substitution, sometimes in ways that are at odds with the rest of the language. Finally, Section 3.8 (mostly on the companion site) discusses separate compilation.

3.1 The Notion of Binding Time

A binding is an association between two things, such as a name and the thing it names. Binding time is the time at which a binding is created or, more generally, the time at which any implementation decision is made (we can think of this as binding an answer to a question). There are many different times at which decisions may be bound:

Language design time: In most languages, the control-ﬂow constructs, the set of fundamental (primitive) types, the available constructors for creating complex types, and many other aspects of language semantics are chosen when the lan- guage is designed. Language implementation time: Most language manuals leave a variety of issues to the discretion of the language implementor. Typical (though by no means universal) examples include the precision (number of bits) of the fundamental types, the coupling of I/O to the operating system’s notion of ﬁles, and the organization and maximum sizes of the stack and heap. Program writing time: Programmers, of course, choose algorithms, data struc- tures, and names. Compile time: Compilers choose the mapping of high-level constructs to ma- chine code, including the layout of statically deﬁned data in memory.

1 For want of a better term, we will use the term “object” throughout Chapters 3–9 to refer to anything that might have a name: variables, constants, types, subroutines, modules, and oth- ers. In many modern languages “object” has a more formal meaning, which we will consider in Chapter 10.

Link time: Since most compilers support separate compilation—compiling dif- ferent modules of a program at different times—and depend on the availability of a library of standard subroutines, a program is usually not complete until the various modules are joined together by a linker. The linker chooses the overall layout of the modules with respect to one another, and resolves inter- module references. When a name in one module refers to an object in another module, the binding between the two is not ﬁnalized until link time. Load time: Load time refers to the point at which the operating system loads the program into memory so that it can run. In primitive operating systems, the choice of machine addresses for objects within the program was not ﬁnalized until load time. Most modern operating systems distinguish between virtual and physical addresses. Virtual addresses are chosen at link time; physical ad- dresses can actually change at run time. The processor’s memory management hardware translates virtual addresses into physical addresses during each indi- vidual instruction at run time. Run time: Run time is actually a very broad term that covers the entire span from the beginning to the end of execution. Bindings of values to variables occur at run time, as do a host of other decisions that vary from language to language. Run time subsumes program start-up time, module entry time, elaboration time (the point at which a declaration is ﬁrst “seen”), subroutine call time, block entry time, and expression evaluation time/statement execution.

The terms static and dynamic are generally used to refer to things bound before run time and at run time, respectively. Clearly “static” is a coarse term. So is “dynamic.” Compiler-based language implementations tend to be more efﬁcient than interpreter-based implementations because they make earlier decisions. For ex- ample, a compiler analyzes the syntax and semantics of global variable declara- tions once, before the program ever runs. It decides on a layout for those variables in memory and generates efﬁcient code to access them wherever they appear in the program. A pure interpreter, by contrast, must analyze the declarations every time the program begins execution. In the worst case, an interpreter may reana- lyze the local declarations within a subroutine each time that subroutine is called. If a call appears in a deeply nested loop, the savings achieved by a compiler that is able to analyze the declarations only once may be very large. As we shall see in

DESIGN & IMPLEMENTATION

3.1 Binding time It is difﬁcult to overemphasize the importance of binding times in the design and implementation of programming languages. In general, early binding times are associated with greater efﬁciency, while later binding times are as- sociated with greater ﬂexibility. The tension between these goals provides a recurring theme for later chapters of this book.

the following section, a compiler will not usually be able to predict the address of a local variable at compile time, since space for the variable will be allocated dy- namically on a stack, but it can arrange for the variable to appear at a ﬁxed offset from the location pointed to by a certain register at run time. Some languages are difﬁcult to compile because their semantics require funda- mental decisions to be postponed until run time, generally in order to increase the ﬂexibility or expressiveness of the language. Most scripting languages, for exam- ple, delay all type checking until run time. References to objects of arbitrary types (classes) can be assigned into arbitrary named variables, as long as the program never ends up applying an operator to (invoking a method of) an object that is not prepared to handle it. This form of polymorphism—applicability to objects or expressions of multiple types—allows the programmer to write unusually ﬂexi- ble and general-purpose code. We will mention polymorphism again in several future sections, including 7.1.2, 7.3, 10.1.1, and 14.4.4.

3.2 Object Lifetime and Storage Management

In any discussion of names and bindings, it is important to distinguish between names and the objects to which they refer, and to identify several key events:

Creation and destruction of objects Creation and destruction of bindings Deactivation and reactivation of bindings that may be temporarily unusable References to variables, subroutines, types, and so on, all of which use bindings

The period of time between the creation and the destruction of a name-to- object binding is called the binding’s lifetime. Similarly, the time between the creation and destruction of an object is the object’s lifetime. These lifetimes need not necessarily coincide. In particular, an object may retain its value and the po- tential to be accessed even when a given name can no longer be used to access it. When a variable is passed to a subroutine by reference, for example (as it typically is in Fortran or with ‘&’ parameters in C++), the binding between the parame- ter name and the variable that was passed has a lifetime shorter than that of the variable itself. It is also possible, though generally a sign of a program bug, for a name-to-object binding to have a lifetime longer than that of the object. This can happen, for example, if an object created via the C++ new operator is passed as a & parameter and then deallocated (delete-ed) before the subroutine returns. A binding to an object that is no longer live is called a dangling reference. Dangling references will be discussed further in Sections 3.6 and 8.5.2. Object lifetimes generally correspond to one of three principal storage alloca- tion mechanisms, used to manage the object’s space:

* Static objects are given an absolute address that is retained throughout the
  program’s execution.

* Stack objects are allocated and deallocated in last-in, ﬁrst-out order, usually in
  conjunction with subroutine calls and returns.
* Heap objects may be allocated and deallocated at arbitrary times. They require
  a more general (and expensive) storage management algorithm.

3.2.1 Static Allocation

Global variables are the obvious example of static objects, but not the only one. The instructions that constitute a program’s machine code can also be thought of as statically allocated objects. We shall see examples in Section 3.3.1 of vari- ables that are local to a single subroutine, but retain their values from one invo- cation to the next; their space is statically allocated. Numeric and string-valued constant literals are also statically allocated, for statements such as A = B/14.7 or printf("hello, world\n"). (Small constants are often stored within the instruction itself; larger ones are assigned a separate location.) Finally, most compilers produce a variety of tables that are used by run-time support routines for debugging, dynamic type checking, garbage collection, exception handling, and other purposes; these are also statically allocated. Statically allocated ob- jects whose value should not change during program execution (e.g., instructions, constants, and certain run-time tables) are often allocated in protected, read-only memory, so that any inadvertent attempt to write to them will cause a processor interrupt, allowing the operating system to announce a run-time error. Logically speaking, local variables are created when their subroutine is called, and destroyed when it returns. If the subroutine is called repeatedly, each invo- cation is said to create and destroy a separate instance of each local variable. It is not always the case, however, that a language implementation must perform work at run time corresponding to these create and destroy operations. Recursion was EXAMPLE 3.1

Static allocation of local variables not originally supported in Fortran (it was added in Fortran 90). As a result, there can never be more than one invocation of a subroutine active in an older Fortran program at any given time, and a compiler may choose to use static allocation for local variables, effectively arranging for the variables of different invocations to share the same locations, and thereby avoiding any run-time overhead for cre- ation and destruction. ■

DESIGN & IMPLEMENTATION

3.2 Recursion in Fortran The lack of recursion in (pre-Fortran 90) Fortran is generally attributed to the expense of stack manipulation on the IBM 704, on which the language was ﬁrst implemented. Many (perhaps most) Fortran implementations choose to use a stack for local variables, but because the language deﬁnition permits the use of static allocation instead, Fortran programmers were denied the beneﬁts of language-supported recursion for over 30 years.

In many languages a named constant is required to have a value that can be determined at compile time. Usually the expression that speciﬁes the constant’s value is permitted to include only other known constants and built-in functions and arithmetic operators. Named constants of this sort, together with constant literals, are sometimes called manifest constants or compile-time constants. Mani- fest constants can always be allocated statically, even if they are local to a recursive subroutine: multiple instances can share the same location. In other languages (e.g., C and Ada), constants are simply variables that cannot be changed after elaboration (initialization) time. Their values, though unchang- ing, can sometimes depend on other values that are not known until run time. Such elaboration-time constants, when local to a recursive subroutine, must be allocated on the stack. C# distinguishes between compile-time and elaboration- time constants using the const and readonly keywords, respectively.

3.2.2 Stack-Based Allocation

If a language permits recursion, static allocation of local variables is no longer an option, since the number of instances of a variable that may need to exist at the same time is conceptually unbounded. Fortunately, the natural nesting of sub- routine calls makes it easy to allocate space for locals on a stack. A simpliﬁed EXAMPLE 3.2

Layout of the run-time stack picture of a typical stack appears in Figure 3.1. Each instance of a subroutine at run time has its own frame (also called an activation record) on the stack, contain- ing arguments and return values, local variables, temporaries, and bookkeeping information. Temporaries are typically intermediate values produced in complex calculations. Bookkeeping information typically includes the subroutine’s return address, a reference to the stack frame of the caller (also called the dynamic link), saved values of registers needed by both the caller and the callee, and various other values that we will study later. Arguments to be passed to subsequent routines lie at the top of the frame, where the callee can easily ﬁnd them. The organization of the remaining information is implementation-dependent: it varies from one language, machine, and compiler to another. ■ Maintenance of the stack is the responsibility of the subroutine calling se- quence—the code executed by the caller immediately before and after the call— and of the prologue (code executed at the beginning) and epilogue (code executed at the end) of the subroutine itself. Sometimes the term “calling sequence” is used to refer to the combined operations of the caller, the prologue, and the epilogue. We will study calling sequences in more detail in Section 9.2. While the location of a stack frame cannot be predicted at compile time (the compiler cannot in general tell what other frames may already be on the stack), the offsets of objects within a frame usually can be statically determined. More- over, the compiler can arrange (in the calling sequence or prologue) for a par- ticular register, known as the frame pointer to always point to a known location within the frame of the current subroutine. Code that needs to access a local vari- able within the current frame, or an argument near the top of the calling frame,

![Figure 3.1 Stack-based allocation...](images/page_154_vector_345.png)
*Figure 3.1 Stack-based allocation of space for subroutines. We assume here that subroutines have been called as shown in the upper right. In particular, B has called itself once, recursively, before calling C. If D returns and C calls E, E’s frame (activation record) will occupy the same space previously used for D’s frame. At any given time, the stack pointer (sp) register points to the ﬁrst unused location on the stack (or the last used location on some machines), and the frame pointer (fp) register points to a known location within the frame of the current subroutine. The relative order of ﬁelds within a frame may vary from machine to machine and compiler to compiler.*

can do so by adding a predetermined offset to the value in the frame pointer. As we discuss in Section C 5.3.1, almost every processor provides a displacement addressing mechanism that allows this addition to be speciﬁed implicitly as part of an ordinary load or store instruction. The stack grows “downward” toward lower addresses in most language implementations. Some machines provide spe- cial push and pop instructions that assume this direction of growth. Local vari- ables, temporaries, and bookkeeping information typically have negative offsets from the frame pointer. Arguments and returns typically have positive offsets; they reside in the caller’s frame. Even in a language without recursion, it can be advantageous to use a stack for local variables, rather than allocating them statically. In most programs the pat- tern of potential calls among subroutines does not permit all of those subroutines to be active at the same time. As a result, the total space needed for local vari- ables of currently active subroutines is seldom as large as the total space across all

![Figure 3.2 Fragmentation. The...](images/page_155_vector_163.png)
*Figure 3.2 Fragmentation. The shaded blocks are in use; the clear blocks are free. Cross- hatched space at the ends of in-use blocks represents internal fragmentation. The discontiguous free blocks indicate external fragmentation. While there is more than enough total free space remaining to satisfy an allocation request of the illustrated size, no single remaining block is large enough.*

subroutines, active or not. A stack may therefore require substantially less mem- ory at run time than would be required for static allocation.

3.2.3 Heap-Based Allocation

A heap is a region of storage in which subblocks can be allocated and deallocated at arbitrary times.2 Heaps are required for the dynamically allocated pieces of linked data structures, and for objects such as fully general character strings, lists, and sets, whose size may change as a result of an assignment statement or other update operation. There are many possible strategies to manage space in a heap. We review the major alternatives here; details can be found in any data-structures textbook. The principal concerns are speed and space, and as usual there are tradeoffs between them. Space concerns can be further subdivided into issues of internal and ex- ternal fragmentation. Internal fragmentation occurs when a storage-management algorithm allocates a block that is larger than required to hold a given object; the extra space is then unused. External fragmentation occurs when the blocks that EXAMPLE 3.3

External fragmentation in the heap have been assigned to active objects are scattered through the heap in such a way that the remaining, unused space is composed of multiple blocks: there may be quite a lot of free space, but no one piece of it may be large enough to satisfy some future request (see Figure 3.2). ■ Many storage-management algorithms maintain a single linked list—the free list—of heap blocks not currently in use. Initially the list consists of a single block comprising the entire heap. At each allocation request the algorithm searches the list for a block of appropriate size. With a ﬁrst ﬁt algorithm we select the ﬁrst block on the list that is large enough to satisfy the request. With a best ﬁt algorithm we search the entire list to ﬁnd the smallest block that is large enough to satisfy the

2 Unfortunately, the term “heap” is also used for the common tree-based implementation of a priority queue. These two uses of the term have nothing to do with one another.

request. In either case, if the chosen block is signiﬁcantly larger than required, then we divide it into two and return the unneeded portion to the free list as a smaller block. (If the unneeded portion is below some minimum threshold in size, we may leave it in the allocated block as internal fragmentation.) When a block is deallocated and returned to the free list, we check to see whether either or both of the physically adjacent blocks are free; if so, we coalesce them. Intuitively, one would expect a best ﬁt algorithm to do a better job of reserving large blocks for large requests. At the same time, it has higher allocation cost than a ﬁrst ﬁt algorithm, because it must always search the entire list, and it tends to result in a larger number of very small “left-over” blocks. Which approach—ﬁrst ﬁt or best ﬁt—results in lower external fragmentation depends on the distribution of size requests. In any algorithm that maintains a single free list, the cost of allocation is lin- ear in the number of free blocks. To reduce this cost to a constant, some stor- age management algorithms maintain separate free lists for blocks of different sizes. Each request is rounded up to the next standard size (at the cost of inter- nal fragmentation) and allocated from the appropriate list. In effect, the heap is divided into “pools,” one for each standard size. The division may be static or dynamic. Two common mechanisms for dynamic pool adjustment are known as the buddy system and the Fibonacci heap. In the buddy system, the standard block sizes are powers of two. If a block of size 2k is needed, but none is available, a block of size 2k+1 is split in two. One of the halves is used to satisfy the request; the other is placed on the kth free list. When a block is deallocated, it is coa- lesced with its “buddy”—the other half of the split that created it—if that buddy is free. Fibonacci heaps are similar, but use Fibonacci numbers for the standard sizes, instead of powers of two. The algorithm is slightly more complex, but leads to slightly lower internal fragmentation, because the Fibonacci sequence grows more slowly than 2k. The problem with external fragmentation is that the ability of the heap to sat- isfy requests may degrade over time. Multiple free lists may help, by clustering small blocks in relatively close physical proximity, but they do not eliminate the problem. It is always possible to devise a sequence of requests that cannot be satisﬁed, even though the total space required is less than the size of the heap. If memory is partitioned among size pools statically, one need only exceed the maxi- mum number of requests of a given size. If pools are dynamically readjusted, one can “checkerboard” the heap by allocating a large number of small blocks and then deallocating every other one, in order of physical address, leaving an alter- nating pattern of small free and allocated blocks. To eliminate external fragmen- tation, we must be prepared to compact the heap, by moving already-allocated blocks. This task is complicated by the need to ﬁnd and update all outstanding references to a block that is being moved. We will discuss compaction further in Section 8.5.3.

3.2.4 Garbage Collection

Allocation of heap-based objects is always triggered by some speciﬁc operation in a program: instantiating an object, appending to the end of a list, assigning a long value into a previously short string, and so on. Deallocation is also explicit in some languages (e.g., C, C++, and Rust). As we shall see in Section 8.5, however, many languages specify that objects are to be deallocated implicitly when it is no longer possible to reach them from any program variable. The run-time library for such a language must then provide a garbage collection mechanism to identify and reclaim unreachable objects. Most functional and scripting languages require garbage collection, as do many more recent imperative languages, including Java and C#. The traditional arguments in favor of explicit deallocation are implementa- tion simplicity and execution speed. Even naive implementations of automatic garbage collection add signiﬁcant complexity to the implementation of a lan- guage with a rich type system, and even the most sophisticated garbage collector can consume nontrivial amounts of time in certain programs. If the programmer can correctly identify the end of an object’s lifetime, without too much run-time bookkeeping, the result is likely to be faster execution. The argument in favor of automatic garbage collection, however, is compel- ling: manual deallocation errors are among the most common and costly bugs in real-world programs. If an object is deallocated too soon, the program may follow a dangling reference, accessing memory now used by another object. If an object is not deallocated at the end of its lifetime, then the program may “leak memory,” eventually running out of heap space. Deallocation errors are notoriously difﬁ- cult to identify and ﬁx. Over time, many language designers and programmers have come to consider automatic garbage collection an essential language feature. Garbage-collection algorithms have improved, reducing their run-time overhead; language implementations have become more complex in general, reducing the marginal complexity of automatic collection; and leading-edge applications have become larger and more complex, making the beneﬁts of automatic collection ever more compelling.

3CHECK YOUR UNDERSTANDING 1. What is binding time? 2. Explain the distinction between decisions that are bound statically and those that are bound dynamically. 3. What is the advantage of binding things as early as possible? What is the advantage of delaying bindings? 4. Explain the distinction between the lifetime of a name-to-object binding and its visibility.

  5.
  What determines whether an object is allocated statically, on the stack, or in
  the heap?
  6.
  List the objects and information commonly found in a stack frame.

  7.
  What is a frame pointer? What is it used for?
  8.
  What is a calling sequence?

  9.
  What are internal and external fragmentation?
* What is garbage collection?

* What is a dangling reference?

3.3 Scope Rules

The textual region of the program in which a binding is active is its scope. In most modern languages, the scope of a binding is determined statically, that is, at compile time. In C, for example, we introduce a new scope upon entry to a subroutine. We create bindings for local objects and deactivate bindings for global objects that are hidden (made invisible) by local objects of the same name. On subroutine exit, we destroy bindings for local variables and reactivate bindings for any global objects that were hidden. These manipulations of bindings may at ﬁrst glance appear to be run-time operations, but they do not require the execution of any code: the portions of the program in which a binding is active are completely determined at compile time. We can look at a C program and know which names refer to which objects at which points in the program based on purely textual rules. For this reason, C is said to be statically scoped (some authors say lexically scoped 3). Other languages, including APL, Snobol, Tcl, and early dialects of Lisp, are dynamically scoped: their bindings depend on the ﬂow of execution at run time. We will examine static and dynamic scoping in more detail in Sections 3.3.1 and 3.3.6. In addition to talking about the “scope of a binding,” we sometimes use the word “scope” as a noun all by itself, without a speciﬁc binding in mind. Infor- mally, a scope is a program region of maximal size in which no bindings change (or at least none are destroyed—more on this in Section 3.3.3). Typically, a scope is the body of a module, class, subroutine, or structured control-ﬂow statement, sometimes called a block. In C family languages it would be delimited with {...} braces.

3 Lexical scope is actually a better term than static scope, because scope rules based on nesting can be enforced at run time instead of compile time if desired. In fact, in Common Lisp and Scheme it is possible to pass the unevaluated text of a subroutine declaration into some other subroutine as a parameter, and then use the text to create a lexically nested declaration at run time.

Algol 68 and Ada use the term elaboration to refer to the process by which declarations become active when control ﬁrst enters a scope. Elaboration entails the creation of bindings. In many languages, it also entails the allocation of stack space for local objects, and possibly the assignment of initial values. In Ada it can entail a host of other things, including the execution of error-checking or heap-space-allocating code, the propagation of exceptions, and the creation of concurrently executing tasks (to be discussed in Chapter 13). At any given point in a program’s execution, the set of active bindings is called the current referencing environment. The set is principally determined by static or dynamic scope rules. We shall see that a referencing environment generally corresponds to a sequence of scopes that can be examined (in order) to ﬁnd the current binding for a given name. In some cases, referencing environments also depend on what are (in a con- fusing use of terminology) called binding rules. Speciﬁcally, when a reference to a subroutine S is stored in a variable, passed as a parameter to another subroutine, or returned as a function value, one needs to determine when the referencing en- vironment for S is chosen—that is, when the binding between the reference to S and the referencing environment of S is made. The two principal options are deep binding, in which the choice is made when the reference is ﬁrst created, and shallow binding, in which the choice is made when the reference is ﬁnally used. We will examine these options in more detail in Section 3.6.

3.3.1 Static Scoping

In a language with static (lexical) scoping, the bindings between names and ob- jects can be determined at compile time by examining the text of the program, without consideration of the ﬂow of control at run time. Typically, the “current” binding for a given name is found in the matching declaration whose block most closely surrounds a given point in the program, though as we shall see there are many variants on this basic theme. The simplest static scope rule is probably that of early versions of Basic, in which there was only a single, global scope. In fact, there were only a few hundred possible names, each of which consisted of a letter optionally followed by a digit. There were no explicit declarations; variables were declared implicitly by virtue of being used. Scope rules are somewhat more complex in (pre-Fortran 90) Fortran, though not much more. Fortran distinguishes between global and local variables. The scope of a local variable is limited to the subroutine in which it appears; it is not visible elsewhere. Variable declarations are optional. If a variable is not declared, it is assumed to be local to the current subroutine and to be of type integer if its name begins with the letters I–N, or real otherwise. (Different conventions for implicit declarations can be speciﬁed by the programmer. In Fortran 90 and its successors, the programmer can also turn off implicit declarations, so that use of an undeclared variable becomes a compile-time error.)

![Figure 3.3 C code...](images/page_160_vector_200.png)
*Figure 3.3 C code to illustrate the use of static variables.*

Semantically, the lifetime of a local Fortran variable (both the object itself and the name-to-object binding) encompasses a single execution of the variable’s sub- routine. Programmers can override this rule by using an explicit save statement. (Similar mechanisms appear in many other languages: in C one declares the vari- able static; in Algol one declares it own.) A save-ed (static, own) variable has a lifetime that encompasses the entire execution of the program. Instead of a log- ically separate object for every invocation of the subroutine, the compiler creates a single object that retains its value from one invocation of the subroutine to the next. (The name-to-variable binding, of course, is inactive when the subroutine is not executing, because the name is out of scope.) As an example of the use of static variables, consider the code in Figure 3.3. EXAMPLE 3.4

Static variables in C The subroutine label_name can be used to generate a series of distinct character- string names: L1, L2, .... A compiler might use these names in its assembly language output. ■

3.3.2 Nested Subroutines

The ability to nest subroutines inside each other, introduced in Algol 60, is a fea- ture of many subsequent languages, including Ada, ML, Common Lisp, Python, Scheme, Swift, and (to a limited extent) Fortran 90. Other languages, including C and its descendants, allow classes or other scopes to nest. Just as the local variables of a Fortran subroutine are not visible to other subroutines, any constants, types, variables, or subroutines declared within a scope are not visible outside that scope in Algol-family languages. More formally, Algol-style nesting gives rise to the clos- est nested scope rule for bindings from names to objects: a name that is introduced in a declaration is known in the scope in which it is declared, and in each inter- nally nested scope, unless it is hidden by another declaration of the same name in one or more nested scopes. To ﬁnd the object corresponding to a given use of a name, we look for a declaration with that name in the current, innermost scope. If there is one, it deﬁnes the active binding for the name. Otherwise, we look for a declaration in the immediately surrounding scope. We continue outward,

examining successively surrounding scopes, until we reach the outer nesting level of the program, where global objects are declared. If no declaration is found at any level, then the program is in error. Many languages provide a collection of built-in, or predeﬁned objects, such as I/O routines, mathematical functions, and in some cases types such as integer and char. It is common to consider these to be declared in an extra, invisible, outermost scope, which surrounds the scope in which global objects are declared. The search for bindings described in the previous paragraph terminates at this ex- tra, outermost scope, if it exists, rather than at the scope in which global objects are declared. This outermost scope convention makes it possible for a program- mer to deﬁne a global object whose name is the same as that of some predeﬁned object (whose “declaration” is thereby hidden, making it invisible). An example of nested scopes appears in Figure 3.4.4 In this example, procedure EXAMPLE 3.5

Nested scopes P2 is called only by P1, and need not be visible outside. It is therefore declared inside P1, limiting its scope (its region of visibility) to the portion of the program shown here. In a similar fashion, P4 is visible only within P1, P3 is visible only within P2, and F1 is visible only within P4. Under the standard rules for nested scopes, F1 could call P2 and P4 could call F1, but P2 could not call F1. Though they are hidden from the rest of the program, nested subroutines are able to access the parameters and local variables (and other local objects) of the surrounding scope(s). In our example, P3 can name (and modify) A1, X, and A2, in addition to A3. Because P1 and F1 both declare local variables named X, the inner declaration hides the outer one within a portion of its scope. Uses of X in F1 refer to the inner X; uses of X in other regions of the code refer to the outer X. ■

A name-to-object binding that is hidden by a nested declaration of the same name is said to have a hole in its scope. In some languages, the object whose name is hidden is simply inaccessible in the nested scope (unless it has more than one name). In others, the programmer can access the outer meaning of a name by applying a qualiﬁer or scope resolution operator. In Ada, for example, a name may be preﬁxed by the name of the scope in which it is declared, using syntax that resembles the speciﬁcation of ﬁelds in a record. My_proc.X, for example, refers to the declaration of X in subroutine My_proc, regardless of whether some other X has been declared in a lexically closer scope. In C++, which does not allow subroutines to nest, ::X refers to a global declaration of X, regardless of whether the current subroutine also has an X.5

Access to Nonlocal Objects

We have already seen (Section 3.2.2) that the compiler can arrange for a frame pointer register to point to the frame of the currently executing subroutine at run

4 This code is not contrived; it was extracted from an implementation (originally in Pascal) of the FMQ error repair algorithm described in Section C 2.3.5.

5 The C++ :: operator is also used to name members (ﬁelds or methods) of a base class that are hidden by members of a derived class; we will consider this use in Section 10.2.2.

![Figure 3.4 Example of...](images/page_162_vector_393.png)
*Figure 3.4 Example of nested subroutines, shown in pseudocode. Vertical bars indicate the scope of each name, for a language in which declarations are visible throughout their subroutine. Note the hole in the scope of the outer X.*

time. Using this register as a base for displacement (register plus offset) address- ing, target code can access objects within the current subroutine. But what about objects in lexically surrounding subroutines? To ﬁnd these we need a way to ﬁnd the frames corresponding to those scopes at run time. Since a nested subroutine may call a routine in an outer scope, the order of stack frames at run time may not necessarily correspond to the order of lexical nesting. Nonetheless, we can be sure that there is some frame for the surrounding scope already in the stack, since the current subroutine could not have been called unless it was visible, and it could not have been visible unless the surrounding scope was active. (It is actually pos- sible in some languages to save a reference to a nested subroutine, and then call it when the surrounding scope is no longer active. We defer this possibility to Section 3.6.2.) The simplest way in which to ﬁnd the frames of surrounding scopes is to main- tain a static link in each frame that points to the “parent” frame: the frame of the

![Figure 3.5 Static chains....](images/page_163_vector_287.png)
*Figure 3.5 Static chains. Subroutines A, B, C, D, and E are nested as shown on the left. If the sequence of nested calls at run time is A, E, B, D, and C, then the static links in the stack will look as shown on the right. The code for subroutine C can ﬁnd local objects at known offsets from the frame pointer. It can ﬁnd local objects of the surrounding scope, B, by dereferencing its static chain once and then applying an offset. It can ﬁnd local objects in B’s surrounding scope, A, by dereferencing its static chain twice and then applying an offset.*

most recent invocation of the lexically surrounding subroutine. If a subroutine is declared at the outermost nesting level of the program, then its frame will have a null static link at run time. If a subroutine is nested k levels deep, then its frame’s static link, and those of its parent, grandparent, and so on, will form a static chain of length k at run time. To ﬁnd a variable or parameter declared j subroutine scopes outward, target code at run time can dereference the static chain j times, and then add the appropriate offset. Static chains are illustrated in Figure 3.5. We EXAMPLE 3.6

Static chains will discuss the code required to maintain them in Section 9.2. ■

3.3.3 Declaration Order

In our discussion so far we have glossed over an important subtlety: suppose an object x is declared somewhere within block B. Does the scope of x include the portion of B before the declaration, and if so can x actually be used in that portion of the code? Put another way, can an expression E refer to any name declared in the current scope, or only to names that are declared before E in the scope? Several early languages, including Algol 60 and Lisp, required that all declara- tions appear at the beginning of their scope. One might at ﬁrst think that this rule

would avoid the questions in the preceding paragraph, but it does not, because declarations may refer to one another.6 In an apparent attempt to simplify the implementation of the compiler, Pas- EXAMPLE 3.7

A “gotcha” in declare-before-use cal modiﬁed the requirement to say that names must be declared before they are used. There are special mechanisms to accommodate recursive types and sub- routines, but in general, a forward reference (an attempt to use a name before its declaration) is a static semantic error. At the same time, however, Pascal retained the notion that the scope of a declaration is the entire surrounding block. Taken together, whole-block scope and declare-before-use rules can interact in surpris- ing ways:

  1.
  const N = 10;
  2.
  ...
  3.
  procedure foo;
  4.
  const
  5.
  M = N;
  (* static semantic error! *)
  6.
  ...
  7.
  N = 20;
  (* local constant declaration; hides the outer N *)

Pascal says that the second declaration of N covers all of foo, so the semantic analyzer should complain on line 5 that N is being used before its declaration. The error has the potential to be highly confusing, particularly if the programmer meant to use the outer N:

```
const N = 10;
...
procedure foo;
const
M = N;
(* static semantic error! *)
var
A : array [1..M] of integer;
N : real;
(* hiding declaration *)
```

Here the pair of messages “N used before declaration” and “N is not a constant” are almost certainly not helpful.

DESIGN & IMPLEMENTATION

3.3 Mutual recursion Some Algol 60 compilers were known to process the declarations of a scope in program order. This strategy had the unfortunate effect of implicitly outlawing mutually recursive subroutines and types, something the language designers clearly did not intend [Atk73].

6 We saw an example of mutually recursive subroutines in the recursive descent parsing of Sec- tion 2.3.1. Mutually recursive types frequently arise in linked data structures, where nodes of two types may need to point to each other.

In order to determine the validity of any declaration that appears to use a name from a surrounding scope, a Pascal compiler must scan the remainder of the scope’s declarations to see if the name is hidden. To avoid this complication, most Pascal successors (and some dialects of Pascal itself) specify that the scope of an identiﬁer is not the entire block in which it is declared (excluding holes), but rather the portion of that block from the declaration to the end (again excluding holes). If our program fragment had been written in Ada, for example, or in C, C++, or Java, no semantic errors would be reported. The declaration of M would refer to the ﬁrst (outer) declaration of N. ■ C++ and Java further relax the rules by dispensing with the deﬁne-before-use requirement in many cases. In both languages, members of a class (including those that are not deﬁned until later in the program text) are visible inside all of the class’s methods. In Java, classes themselves can be declared in any order. Interestingly, while C# echos Java in requiring declaration before use for local EXAMPLE 3.8

Whole-block scope in C# variables (but not for classes and members), it returns to the Pascal notion of whole-block scope. Thus the following is invalid in C#:

class A { const int N = 10; void foo() { const int M = N; // uses inner N before it is declared const int N = 20; ■

Perhaps the simplest approach to declaration order, from a conceptual point of view, is that of Modula-3, which says that the scope of a declaration is the en- tire block in which it appears (minus any holes created by nested declarations), and that the order of declarations doesn’t matter. The principal objection to this approach is that programmers may ﬁnd it counterintuitive to use a local variable before it is declared. Python takes the “whole block” scope rule one step further EXAMPLE 3.9

“Local if written” in Python by dispensing with variable declarations altogether. In their place it adopts the unusual convention that the local variables of subroutine S are precisely those variables that are written by some statement in the (static) body of S. If S is nested inside of T, and the name x appears on the left-hand side of assignment statements in both S and T, then the x’s are distinct: there is one in S and one in T. Non-local variables are read-only unless explicitly imported (using Python’s global statement). We will consider these conventions in more detail in Sec- tion 14.4.1, as part of a general discussion of scoping in scripting languages. ■ In the interest of ﬂexibility, modern Lisp dialects tend to provide several op- EXAMPLE 3.10

Declaration order in Scheme tions for declaration order. In Scheme, for example, the letrec and let* con- structs deﬁne scopes with, respectively, whole-block and declaration-to-end-of- block semantics. The most frequently used construct, let, provides yet another option:

```
(let ((A 1))
; outer scope, with A defined to be 1
(let ((A 2)
; inner scope, with A defined to be 2
(B A))
;
and B defined to be A
B))
; return the value of B
```

Here the nested declarations of A and B don’t take effect until after the end of the declaration list. Thus when B is deﬁned, the redeﬁnition of A has not yet taken effect. B is deﬁned to be the outer A, and the code as a whole returns 1. ■

Declarations and Deﬁnitions

Recursive types and subroutines introduce a problem for languages that require names to be declared before they can be used: how can two declarations each appear before the other? C and C++ handle the problem by distinguishing be- tween the declaration of an object and its deﬁnition. A declaration introduces a name and indicates its scope, but may omit certain implementation details. A deﬁnition describes the object in sufﬁcient detail for the compiler to determine its implementation. If a declaration is not complete enough to be a deﬁnition, then a separate deﬁnition must appear somewhere else in the scope. In C we can EXAMPLE 3.11

Declarations vs deﬁnitions in C write

```
struct manager;
/* declaration only */
struct employee {
struct manager *boss;
struct employee *next_employee;
...
};
struct manager {
/* definition */
struct employee *first_employee;
...
};
```

and

```
void list_tail(follow_set fs);
/* declaration only */
void list(follow_set fs)
{
switch (input_token) {
case id : match(id); list_tail(fs);
...
}
void list_tail(follow_set fs)
/* definition */
{
switch (input_token) {
case comma : match(comma); list(fs);
...
}
```

The initial declaration of manager needed only to introduce a name: since point- ers are generally all the same size, the compiler can determine the implementa- tion of employee without knowing any manager details. The initial declaration of list_tail, however, must include the return type and parameter list, so the compiler can tell that the call in list is correct. ■

Nested Blocks

In many languages, including Algol 60, C89, and Ada, local variables can be de- clared not only at the beginning of any subroutine, but also at the top of any begin... end ({...}) block. Other languages, including Algol 68, C, and all of C’s descendants, are even more ﬂexible, allowing declarations wherever a state- ment may appear. In most languages a nested declaration hides any outer dec- laration with the same name (Java and C# make it a static semantic error if the outer declaration is local to the current subroutine).

DESIGN & IMPLEMENTATION

3.4 Redeclarations Some languages, particularly those that are intended for interactive use, permit the programmer to redeclare an object: to create a new binding for a given name in a given scope. Interactive programmers commonly use redeclarations to experiment with alternative implementations or to ﬁx bugs during early development. In most interactive languages, the new meaning of the name replaces the old in all contexts. In ML dialects, however, the old meaning of the name may remain accessible to functions that were elaborated before the name was redeclared. This design choice can sometimes be counterintuitive. Here’s an example in OCaml (the lines beginning with # are user input; the others are printed by the interpreter):

```
# let x = 1;;
val x : int = 1
# let f y = x + y;;
val f : int -> int = <fun>
# let x = 2;;
val x : int = 2
# f 3;;
- : int = 4
```

The second line of user input deﬁnes f to be a function of one argument (y) that returns the sum of that argument and the previously deﬁned value x. When we redeﬁne x to be 2, however, the function does not notice: it still returns y plus 1. This behavior reﬂects the fact that OCaml is usually com- piled, bit by bit on the ﬂy, rather than interpreted. When x is redeﬁned, f has already been compiled into a form (bytecode or machine code) that ac- cesses the old meaning of x directly. By comparison, a language like Scheme, which is lexically scoped but usually interpreted, stores the bindings for names in known locations. Programs always access the meanings of names indirectly through those locations: if the meaning of a name changes, all accesses to the name will use the new meaning.

Variables declared in nested blocks can be very useful, as for example in the EXAMPLE 3.12

Inner declarations in C following C code:

```
{
int temp = a;
a = b;
b = temp;
}
```

Keeping the declaration of temp lexically adjacent to the code that uses it makes the program easier to read, and eliminates any possibility that this code will in- terfere with another variable named temp. ■ No run-time work is needed to allocate or deallocate space for variables de- clared in nested blocks; their space can be included in the total space for local variables allocated in the subroutine prologue and deallocated in the epilogue. Exercise 3.9 considers how to minimize the total space required.

3CHECK YOUR UNDERSTANDING 12. What do we mean by the scope of a name-to-object binding?

* Describe the difference between static and dynamic scoping.
* What is elaboration?

* What is a referencing environment?
* Explain the closest nested scope rule.
* What is the purpose of a scope resolution operator?

* What is a static chain? What is it used for?
* What are forward references? Why are they prohibited or restricted in many
  programming languages?
* Explain the difference between a declaration and a deﬁnition. Why is the dis-
  tinction important?

3.3.4 Modules

An important challenge in the construction of any large body of software is to divide the effort among programmers in such a way that work can proceed on multiple fronts simultaneously. This modularization of effort depends critically on the notion of information hiding, which makes objects and algorithms invisi- ble, whenever possible, to portions of the system that do not need them. Properly modularized code reduces the “cognitive load” on the programmer by minimiz- ing the amount of information required to understand any given portion of the

system. In a well-designed program the interfaces among modules are as “nar- row” (i.e., simple) as possible, and any design decision that is likely to change is hidden inside a single module. Information hiding is crucial for software maintenance (bug ﬁxes and en- hancement), which tends to signiﬁcantly outweigh the cost of initial development for most commercial software. In addition to reducing cognitive load, hiding re- duces the risk of name conﬂicts: with fewer visible names, there is less chance that a newly introduced name will be the same as one already in use. It also safe- guards the integrity of data abstractions: any attempt to access an object outside of the module to which it belongs will cause the compiler to issue an “undeﬁned symbol” error message. Finally, it helps to compartmentalize run-time errors: if a variable takes on an unexpected value, we can generally be sure that the code that modiﬁed it is in the variable’s scope.

Encapsulating Data and Subroutines

Unfortunately, the information hiding provided by nested subroutines is limited to objects whose lifetime is the same as that of the subroutine in which they are hidden. When control returns from a subroutine, its local variables will no longer be live: their values will be discarded. We have seen a partial solution to this problem in the form of the save statement in Fortran and the static and own variables of C and Algol. Static variables allow a subroutine to have “memory”—to retain information from one invocation to the next—while protecting that memory from acciden- tal access or modiﬁcation by other parts of the program. Put another way, static variables allow programmers to build single-subroutine abstractions. Unfortu- nately, they do not allow the construction of abstractions whose interface needs to consist of more than one subroutine. Consider, for example, a simple pseudo- EXAMPLE 3.13

Pseudorandom numbers as a motivation for modules random number generator. In addition to the main rand_int routine, we might want a set_seed routine that primes the generator for a speciﬁc pseudorandom sequence (e.g., for deterministic testing). We should like to make the state of the generator, which determines the next pseudorandom number, visible to both rand_int and set_seed, but hide it from the rest of the program. We can achieve this goal in many languages through use of a module construct. ■

Modules as Abstractions

A module allows a collection of objects—subroutines, variables, types, and so on—to be encapsulated in such a way that (1) objects inside are visible to each other, but (2) objects on the inside may not be visible on the outside unless they are exported, and (3) objects on the outside may not be visible on the inside un- less they are imported. Import and export conventions vary signiﬁcantly from one language to another, but in all cases, only the visibility of objects is affected; modules do not affect the lifetime of the objects they contain.

![Figure 3.6 Pseudorandom number...](images/page_170_vector_221.png)
*Figure 3.6 Pseudorandom number generator module in C++. Uses the linear congruential method, with a default seed taken from the current time of day. While there exist much better (more random) generators, this one is simple, and acceptable for many purposes.*

Modules were one of the principal language innovations of the late 1970s and early 1980s; they appeared in Clu7 (which called them clusters), Modula (1, 2, and 3), Turing, and Ada 83, among others. In more modern form, they also appear in Haskell, C++, Java, C#, and all the major scripting languages. Several languages, including Ada, Java, and Perl, use the term package instead of module. Others, including C++, C#, and PHP, use namespace. Modules can be emulated to some degree through use of the separate compilation facilities of C; we discuss this possibility in Section C 3.8. As an example of the use of modules, consider the pseudorandom number EXAMPLE 3.14

Pseudorandom number generator in C++ generator shown in Figure 3.6. As discussed in Sidebar 3.5, this module (names- pace) would typically be placed in its own ﬁle, and then imported wherever it is needed in a C++ program. Bindings of names made inside the namespace may be partially or totally hid- den (inactive) on the outside—but not destroyed. In C++, where namespaces can appear only at the outermost level of lexical nesting, integer seed would retain its value throughout the execution of the program, even though it is visible only to set_seed and rand_int. Outside the rand_mod namespace, C++ allows set_seed and rand_int to be accessed as rand_mod::set_seed and rand_mod::rand_int. The seed variable could also be accessed as rand_mod::seed, but this is probably not a good idea, and the need for the rand_mod preﬁx means it’s unlikely to happen by accident.

7 Barbara Liskov (1939–), the principal designer of Clu, is one of the leading ﬁgures in the history of abstraction mechanisms. A faculty member at MIT since 1971, she was also the principal de- signer of the Argus programming language, which combined language and database technology to improve the reliability and programmability of distributed systems. She received the ACM Turing Award in 2008.

The need for the preﬁx can be eliminated, on a name-by-name basis, with a using directive:

```
using rand_mod::rand_int;
...
int r = rand_int();
```

Alternatively, the full set of names declared in a namespace can be made available at once:

```
using namespace rand_mod;
...
set_seed(12345);
int r = rand_int();
```

Unfortunately, such wholesale exposure of a module’s names increases both the likelihood of conﬂict with names in the importing context and the likelihood that objects like seed, which are logically private to the module, will be accessed accidentally. ■

Imports and Exports

Some languages allow the programmer to specify that names exported from mod- ules be usable only in restricted ways. Variables may be exported read-only, for example, or types may be exported opaquely, meaning that variables of that type may be declared, passed as arguments to the module’s subroutines, and possibly compared or assigned to one another, but not manipulated in any other way. Modules into which names must be explicitly imported are said to be closed scopes. By extension, modules that do not require imports are said to be open scopes. Imports serve to document the program: they increase modularity by requiring a module to specify the ways in which it depends on the rest of the pro- gram. They also reduce name conﬂicts by refraining from importing anything that isn’t needed. Modules are closed in Modula (1, 2, and 3) and Haskell. C++ is representative of an increasingly common option, in which names are auto- matically exported, but are available on the outside only when qualiﬁed with the module name—unless they are explicitly “imported” by another scope (e.g., with the C++ using directive), at which point they are available unqualiﬁed. This op- tion, which we might call selectively open modules, also appears in Ada, Java, C#, and Python, among others.

Modules as Managers

Modules facilitate the construction of abstractions by allowing data to be made private to the subroutines that use them. When used as in Figure 3.6, however, each module deﬁnes a single abstraction. Continuing our previous example, there EXAMPLE 3.15

Module as “manager” for a type are times when it may be desirable to have more than one pseudorandom num- ber generator. When debugging a game, for example, we might want to obtain deterministic (repeatable) behavior in one particular game module (a particular

![Figure 3.7 Manager module...](images/page_172_vector_309.png)
*Figure 3.7 Manager module for pseudorandom numbers in C++.*

character, perhaps), regardless of uses of pseudorandom numbers elsewhere in the program. If we want to have several generators, we can make our namespace a “manager” for instances of a generator type, which is then exported from the module, as shown in Figure 3.7. The manager idiom requires additional subrou- tines to create/initialize and possibly destroy generator instances, and it requires that every subroutine (set_seed, rand_int, create) take an extra parameter, to specify the generator in question. Given the declarations in Figure 3.7, we could create and use an arbitrary num- ber of generators:

```
using rand_mgr::generator;
generator *g1 = rand_mgr::create();
generator *g2 = rand_mgr::create();
...
using rand_mgr::rand_int;
int r1 = rand_int(g1);
int r2 = rand_int(g2);
```

In more complex programs, it may make sense for a module to export several related types, instances of which can then be passed to its subroutines. ■

3.3.5 Module Types and Classes

An alternative solution to the multiple instance problem appeared in Eu- clid, which treated each module as a type, rather than a simple encapsulation

construct. Given a module type, the programmer could declare an arbitrary number of similar module objects. As it turns out, the classes of modern object- oriented languages are an extension of module types. Access to a module instance typically looks like access to an object, and we can illustrate the ideas in any object-oriented language. For our C++ pseudorandom number example, the EXAMPLE 3.16

A pseudorandom number generator type syntax

```
generator *g = rand_mgr::create();
...
int r = rand_int(g);
```

might be replaced by

```
rand_gen *g = new rand_gen();
...
int r = g->rand_int();
```

where the rand_gen class is declared as in Figure 3.8. Module types or classes allow the programmer to think of the rand_int routine as “belonging to” the generator, rather than as a separate entity to which the generator must be passed

DESIGN & IMPLEMENTATION

3.5 Modules and separate compilation One of the hallmarks of a good abstraction is that it tends to be useful in multi- ple contexts. To facilitate code reuse, many languages make modules the basis of separate compilation. Modula-2 actually provided two different kinds of modules: one (external modules) for separate compilation, the other (internal modules) for textual nesting within a larger scope. Experience with these op- tions eventually led Niklaus Wirth, the designer of Modula-2, to conclude that external modules were by far the more useful variety; he omitted the internal version from his subsequent language, Oberon. Many would argue, however, that internal modules ﬁnd their real utility only when extended with instan- tiation and inheritance. Indeed, as noted near the end of this section, many object-oriented languages provide both modules and classes. The former sup- port separate compilation and serve to minimize name conﬂicts; the latter are for data abstraction. To facilitate separate compilation, modules in many languages (Modula-2 and Oberon among them) can be divided into a declaration part (header) and an implementation part (body), each of which occupies a separate ﬁle. Code that uses the exports of a given module can be compiled as soon as the header exists; it is not dependent on the body. In particular, work on the bodies of cooperating modules can proceed concurrently once the headers exist. We will return to the subjects of separate compilation and code reuse in Sections C 3.8 and 10.1, respectively.

![Figure 3.8 Pseudorandom number...](images/page_174_vector_222.png)
*Figure 3.8 Pseudorandom number generator class in C++.*

as an argument. Conceptually, there is a dedicated rand_int routine for every generator (rand_gen object). In practice, of course, it would be highly wasteful to create multiple copies of the code. As we shall see in Chapter 10, rand_gen instances really share a single pair of set_seed and rand_int routines, and the compiler arranges for a pointer to the relevant instance to be passed to the routine as an extra, hidden parameter. The implementation turns out to be very similar to that of Figure 3.7, but the programmer need not think of it that way. ■

Object Orientation

The difference between module types and classes is a powerful pair of features found together in the latter but not the former—namely, inheritance and dynamic method dispatch.8 Inheritance allows new classes to be deﬁned as extensions or reﬁnements of existing classes. Dynamic method dispatch allows a reﬁned class to override the deﬁnition of an operation in its parent class, and for the choice among deﬁnitions to be made at run time, on the basis of whether a particular object belongs to the child class or merely to the parent. Inheritance facilitates a programming style in which all or most operations are thought of as belonging to objects, and in which new objects can inherit many of their operations from existing objects, without the need to rewrite code. Classes have their roots in Simula-67, and were further developed in Smalltalk. They ap- pear in many modern languages, including Eiffel, OCaml, C++, Java, C#, and sev- eral scripting languages, notably Python and Ruby. Inheritance mechanisms can also be found in certain languages that are not usually considered object-oriented, including Modula-3, Ada 95, and Oberon. We will examine inheritance, dynamic dispatch, and their impact on scope rules in Chapter 10 and in Section 14.4.4.

8 A few languages—notablymembers of the ML family—havemodule types with inheritance—but still without dynamic method dispatch. Modules in most languages are missing both features.

Module types and classes (ignoring issues related to inheritance) require only simple changes to the scope rules deﬁned for modules in Section 3.3.4. Every instance A of a module type or class (e.g., every rand_gen) has a separate copy of the module or class’s variables. These variables are then visible when executing one of A’s operations. They may also be indirectly visible to the operations of some other instance B if A is passed as a parameter to one of those operations. This rule makes it possible in most object-oriented languages to construct binary (or more-ary) operations that can manipulate the variables (ﬁelds) of more than one instance of a class.

Modules Containing Classes

While there is a clear progression from modules to module types to classes, it is not necessarily the case that classes are an adequate replacement for modules in all cases. Suppose we are developing an interactive “ﬁrst person” game. Class EXAMPLE 3.17

Modules and classes in a large application hierarchies may be just what we need to represent characters, possessions, build- ings, goals, and a host of other data abstractions. At the same time, especially on a project with a large team of programmers, we will probably want to divide the functionality of the game into large-scale subsystems such as graphics and ren- dering, physics, and strategy. These subsystems are really not data abstractions, and we probably don’t want the option to create multiple instances of them. They are naturally captured with traditional modules, particularly if those modules are designed for separate compilation (Section 3.8). Recognizing the need for both multi-instance abstractions and functional subdivision, many languages, includ- ing C++, Java, C#, Python, and Ruby, provide separate class and module mecha- nisms. ■

3.3.6 Dynamic Scoping

In a language with dynamic scoping, the bindings between names and objects depend on the ﬂow of control at run time, and in particular on the order in which subroutines are called. In comparison to the static scope rules discussed in the previous section, dynamic scope rules are generally quite simple: the “current” binding for a given name is the one encountered most recently during execution, and not yet destroyed by returning from its scope. Languages with dynamic scoping include APL, Snobol, Tcl, TEX (the type- setting language with which this book was created), and early dialects of Lisp [MAE+65, Moo78, TM81] and Perl.9 Because the ﬂow of control cannot in gen- eral be predicted in advance, the bindings between names and objects in a lan- guage with dynamic scoping cannot in general be determined by a compiler. As a

9 Scheme and Common Lisp are statically scoped, though the latter allows the programmer to specify dynamic scoping for individual variables. Static scoping was added to Perl in version 5; the programmer now chooses static or dynamic scoping explicitly in each variable declaration. (We consider this choice in more detail in Section 14.4.1.)

![Figure 3.9 Static versus...](images/page_176_vector_239.png)
*Figure 3.9 Static versus dynamic scoping. Program output depends on both scope rules and, in the case of dynamic scoping, a value read at run time.*

result, many semantic rules in a language with dynamic scoping become a matter of dynamic semantics rather than static semantics. Type checking in expressions and argument checking in subroutine calls, for example, must in general be de- ferred until run time. To accommodate all these checks, languages with dynamic scoping tend to be interpreted, rather than compiled. Consider the program in Figure 3.9. If static scoping is in effect, this program EXAMPLE 3.18

Static vs dynamic scoping prints a 1. If dynamic scoping is in effect, the output depends on the value read at line 8 at run time: if the input is positive, the program prints a 2; otherwise it prints a 1. Why the difference? At issue is whether the assignment to the variable n at line 3 refers to the global variable declared at line 1 or to the local variable declared at line 5. Static scope rules require that the reference resolve to the closest lexically enclosing declaration, namely the global n. Procedure ﬁrst changes n to 1, and line 12 prints this value. Dynamic scope rules, on the other hand, require that we choose the most recent, active binding for n at run time.

DESIGN & IMPLEMENTATION

3.6 Dynamic scoping It is not entirely clear whether the use of dynamic scoping in Lisp and other early interpreted languages was deliberate or accidental. One reason to think that it may have been deliberate is that it makes it very easy for an interpreter to look up the meaning of a name: all that is required is a stack of declarations (we examine this stack more closely in Section C 3.4.2). Unfortunately, this simple implementation has a very high run-time cost, and experience indicates that dynamic scoping makes programs harder to understand. The modern consen- sus seems to be that dynamic scoping is usually a bad idea (see Exercise 3.17 and Exploration 3.36 for two exceptions).

We create a binding for n when we enter the main program. We create another when and if we enter procedure second. When we execute the assignment state- ment at line 3, the n to which we are referring will depend on whether we entered ﬁrst through second or directly from the main program. If we entered through second, we will assign the value 1 to second’s local n. If we entered from the main program, we will assign the value 1 to the global n. In either case, the write at line 12 will refer to the global n, since second’s local n will be destroyed, along with its binding, when control returns to the main program. ■ With dynamic scoping, errors associated with the referencing environment EXAMPLE 3.19

Run-time errors with dynamic scoping may not be detected until run time. In Figure 3.10, for example, the declara- tion of local variable max score in procedure foo accidentally redeﬁnes a global variable used by function scaled score, which is then called from foo. Since the global max score is an integer, while the local max score is a ﬂoating-point num- ber, dynamic semantic checks in at least some languages will result in a type clash message at run time. If the local max score had been an integer, no error would have been detected, but the program would almost certainly have produced in- correct results. This sort of error can be very hard to ﬁnd. ■

3.4 Implementing Scope

To keep track of the names in a statically scoped program, a compiler relies on a data abstraction called a symbol table. In essence, the symbol table is a dictionary: it maps names to the information the compiler knows about them. The most ba- sic operations are to insert a new mapping (a name-to-object binding) or to look up the information that is already present for a given name. Static scope rules add complexity by allowing a given name to correspond to differentobjects—and thus to different information—in different parts of the program. Most variations on static scoping can be handled by augmenting a basic dictionary-style symbol table with enter scope and leave scope operations to keep track of visibility. Nothing is ever deleted from the table; the entire structure is retained throughout compi- lation, and then saved for use by debuggers or run-time reﬂection (type lookup) mechanisms. In a language with dynamic scoping, an interpreter (or the output of a com- piler) must perform operations analogous to symbol table insert and lookup at run time. In principle, any organization used for a symbol table in a compiler could be used to track name-to-object bindings in an interpreter, and vice versa. In practice, implementations of dynamic scoping tend to adopt one of two spe- ciﬁc organizations: an association list or a central reference table.

IN MORE DEPTH

A symbol table with visibility support can be implemented in several different ways. One appealing approach, due to LeBlanc and Cook [CL83], is described on the companion site, along with both association lists and central reference tables.

![Figure 3.10 The problem...](images/page_178_vector_212.png)
*Figure 3.10 The problem with dynamic scoping. Procedure scaled score probably does not do what the programmer intended when dynamic scope rules allow procedure foo to change the meaning of max score.*

An association list (or A-list for short) is simply a list of name/value pairs. When used to implement dynamic scoping it functions as a stack: new declara- tions are pushed as they are encountered, and popped at the end of the scope in which they appeared. Bindings are found by searching down the list from the top. A central reference table avoids the need for linear-time search by maintaining an explicit mapping from names to their current meanings. Lookup is faster, but scope entry and exit are somewhat more complex, and it becomes substantially more difﬁcult to save a referencing environment for future use (we discuss this issue further in Section 3.6.1).

3.5 The Meaning of Names within a Scope

So far in our discussion of naming and scopes we have assumed that there is a one-to-one mapping between names and visible objects at any given point in a program. This need not be the case. Two or more names that refer to the same object at the same point in the program are said to be aliases. A name that can refer to more than one object at a given point in the program is said to be overloaded. Overloading is in turn related to the more general subject of polymorphism, which allows a subroutine or other program fragment to behave in different ways depending on the types of its arguments.

3.5.1 Aliases

Simple examples of aliases occur in the variant records and unions of many pro- gramming languages (we will discuss these features detail in Section C 8.1.3).

They also arise naturally in programs that make use of pointer-based data struc- tures. A more subtle way to create aliases in many languages is to pass a variable EXAMPLE 3.20

Aliasing with parameters by reference to a subroutine that also accesses that variable directly. Consider the following code in C++:

```
double sum, sum_of_squares;
...
void accumulate(double& x) {
// x is passed by reference
sum += x;
sum_of_squares += x * x;
}
```

If we pass sum as an argument to accumulate, then sum and x will be aliases for one another inside the called routine, and the program will probably not do what the programmer intended. ■ As a general rule, aliases tend to make programs more confusing than they otherwise would be. They also make it much more difﬁcult for a compiler to perform certain important code improvements. Consider the following EXAMPLE 3.21

Aliases and code improvement C code:

```
int a, b, *p, *q;
...
a = *p;
/* read from the variable referred to by p */
*q = 3;
/* assign to the variable referred to by q */
b = *p;
/* read from the variable referred to by p */
```

DESIGN & IMPLEMENTATION

3.7 Pointers in C and Fortran The tendency of pointers to introduce aliases is one of the reasons why For- tran compilers tended, historically, to produce faster code than C compilers: pointers are heavily used in C, but missing from Fortran 77 and its predeces- sors. It is only in recent years that sophisticated alias analysis algorithms have allowed C compilers to rival their Fortran counterparts in speed of generated code. Pointer analysis is sufﬁciently important that the designers of the C99 standard decided to add a new keyword to the language. The restrict qual- iﬁer, when attached to a pointer declaration, is an assertion on the part of the programmer that the object to which the pointer refers has no alias in the cur- rent scope. It is the programmer’s responsibility to ensure that the assertion is correct; the compiler need not attempt to check it. C99 also introduced strict aliasing. This allows the compiler to assume that pointers of different types will never refer to the same location in memory. Most compilers provide a command-line option to disable optimizations that exploit this rule; other- wise (poorly written) legacy programs may behave incorrectly when compiled at higher optimization levels.

![Figure 3.11 Overloading of...](images/page_180_vector_198.png)
*Figure 3.11 Overloading of enumeration constants in Ada.*

The initial assignment to a will, on most machines, require that *p be loaded into a register. Since accessing memory is expensive, the compiler will want to hang on to the loaded value and reuse it in the assignment to b. It will be unable to do so, however, unless it can verify that p and q cannot refer to the same object—that is, that *p and *q are not aliases. While compile-time veriﬁcation of this sort is possible in many common cases, in general it’s undecidable. ■

3.5.2 Overloading

Most programming languages provide at least a limited form of overloading. In C, for example, the plus sign (+) is used to name several different functions, in- cluding signed and unsigned integer and ﬂoating-point addition. Most program- mers don’t worry about the distinction between these two functions—both are based on the same mathematical concept, after all—but they take arguments of different types and perform very different operations on the underlying bits. A EXAMPLE 3.22

Overloaded enumeration constants in Ada slightly more sophisticated form of overloading appears in the enumeration con- stants of Ada. In Figure 3.11, the constants oct and dec refer either to months or to numeric bases, depending on the context in which they appear. ■ Within the symbol table of a compiler, overloading must be handled (resolved) by arranging for the lookup routine to return a list of possible meanings for the requested name. The semantic analyzer must then choose from among the ele- ments of the list based on context. When the context is not sufﬁcient to decide, as in the call to print in Figure 3.11, then the semantic analyzer must announce an error. Most languages that allow overloaded enumeration constants allow the EXAMPLE 3.23

Resolving ambiguous overloads programmer to provide appropriate context explicitly. In Ada, for example, one can say

print(month'(oct));

In Modula-3 and C#, every use of an enumeration constant must be preﬁxed with a type name, even when there is no chance of ambiguity:

![Figure 3.12 Simple example...](images/page_181_vector_245.png)
*Figure 3.12 Simple example of overloading in C++. In each case the compiler can tell which function is intended by the number and types of arguments.*

```
mo := month.dec;
(* Modula-3 *)
```

```
pb = print_base.oct;
// C#
```

In C, one cannot overload enumeration constants at all; every constant visible in a given scope must be distinct. C++11 introduced new syntax to give the program- mer control over this behavior: enum constants must be distinct; enum class constants must be qualiﬁed with the class name (e.g., month::oct). ■ Both Ada and C++ have elaborate facilities for overloading subroutine names. EXAMPLE 3.24

Overloading in C++ Many of the C++ facilities carry over to Java and C#. A given name may refer to an arbitrary number of subroutines in the same scope, so long as the subrou- tines differ in the number or types of their arguments. C++ examples appear in Figure 3.12. ■

Redeﬁning Built-in Operators

Many languages also allow the built-in arithmetic operators (+, -, *, etc.) to be overloaded with user-deﬁned functions. Ada, C++, and C# do this by deﬁning EXAMPLE 3.25

Operator overloading in Ada alternative preﬁx forms of each operator, and deﬁning the usual inﬁx forms to be abbreviations (or “syntactic sugar”) for the preﬁx forms. In Ada, A + B is short for "+"(A, B). If "+" (the preﬁx form) is overloaded, then + (the inﬁx form) will work for the new types as well. It must be possible to resolve the overloading (determine which + is intended) from the types of A and B. ■ Fortran 90 provides a special interface construct that can be used to associate an operator with some named binary function. In C++ and C#, EXAMPLE 3.26

Operator overloading in C++ which are object-oriented, A + B may be short for either operator+(A, B) or A.operator+(B). In the latter case, A is an instance of a class (module type) that deﬁnes an operator+ function. In C++ one might say

```
class complex {
double real, imaginary;
...
public:
complex operator+(complex other) {
return complex(real + other.real, imaginary + other.imaginary);
}
...
};
...
complex A, B, C;
...
C = A + B;
// uses user-defined operator+
```

C# syntax is similar. ■ In Haskell, user-deﬁned inﬁx operators are simply functions whose names EXAMPLE 3.27

Inﬁx operators in Haskell consist of non-alphanumeric characters:

let a @@ b = a * 2 + b

Here we have deﬁned a 2-argument operator named @@. We could also have de- clared it with the usual preﬁx notation, in which case we would have needed to enclose the name in parentheses:

let (@@) a b = a * 2 + b

Either way, both 3 @@ 4 and (@@) 3 4 will evaluate to 10. (An arbitrary function can also be used as inﬁx operator in Haskell by enclosing its name in backquotes. With an appropriate deﬁnition, gcd 8 12 and 8 `gcd` 12 will both evaluate to 4.) Unlike most languages, Haskell allows the programmer to specify both the as- sociativity and the precedence of user-deﬁned operators. We will return to this subject in Section 6.1.1. ■ Both operators and ordinary functions can be overloaded in Haskell, using a EXAMPLE 3.28

Overloading with type classes mechanism known as type classes. Among the simplest of these is the class Eq, declared in the standard library as

DESIGN & IMPLEMENTATION

3.8 User-deﬁned operators in OCaml OCaml does not support overloading, but it does allow the user to create new operators, whose names—as in Haskell—consist of non-alphanumeric char- acters. Each such name must begin with the name of one of the built-in op- erators, from which the new operator inherits its syntactic role (preﬁx, inﬁx, or postﬁx) and precedence. So, for example,+.is used for ﬂoating-point addi- tion; +/ is used for “bignum” (arbitrary precision) integer addition.

```
class Eq a, where
(==) :: a -> a -> Bool
```

This declaration establishes Eq as the set of types that provide an == operator. Any instance of ==, for some particular type a, must take two arguments (each of type a) and return a Boolean result. In other words, == is an overloaded operator, supported by all types of class Eq; each such type must provide its own equality deﬁnition. The deﬁnition for integers, again from the standard library, looks like this:

```
instance Eq Integer where
x == y = x `integerEq` y
```

Here integerEq is the built-in, non-overloaded integer equality operator. ■ Type classes can build upon themselves. The Haskell Ord class, for example, encompasses all Eq types that also support the operators <, >, <=, and >=. The Num class (simplifying a bit) encompasses all Eq types that also support addition, subtraction, and multiplication. In addition to making overloading a bit more explicit than it is in most languages, type classes make it possible to specify that certain polymorphic functions can be used only when their arguments are of a type that supports some particular overloaded function (for more on this subject, see Sidebar 7.7).

Related Concepts

When considering function and subroutine calls, it is important to distinguish overloading from the related concepts of coercion and polymorphism. All three can be used, in certain circumstances, to pass arguments of multiple types to (or return values of multiple types from) what appears to be a single named routine. The syntactic similarity, however, hides signiﬁcant differences in semantics and pragmatics. Coercion, which we will cover in more detail in Section 7.2.2, is the process by which a compiler automatically converts a value of one type into a value of another type when that second type is required by the surrounding context. Poly- morphism, which we will consider in Sections 7.1.2, 7.3, 10.1.1, and 14.4.4, allows a single subroutine to accept arguments of multiple types. Consider a print routine designed to display its argument on the standard out- EXAMPLE 3.29

Printing objects of multiple types put stream, and suppose that we wish to be able to display objects of multiple types. With overloading, we might write a separate print routine for each type of interest. Then when it sees a call to print(my object), the compiler would choose the appropriate routine based on the type of my object. Now suppose we already have a print routine that accepts a ﬂoating-point ar- gument. With coercion, we might be able to print integers by passing them to this existing routine, rather than writing a new one. When it sees a call to print(my integer), the compiler would coerce (convert) the argument automati- cally to ﬂoating-point type prior to the call.

Finally, suppose we have a language in which many types support a to string operation that will generate a character-string representation of an object of that type. We might then be able to write a polymorphic print routine that accepts an argument of any type for which to string is deﬁned. The to string operation might itself be polymorphic, built in, or simply overloaded; in any of these cases, print could call it and output the result. ■ In short, overloading allows the programmerto give the same name to multiple objects, and to disambiguate (resolve) them based on context—for subroutines, on the number or types of arguments. Coercion allows the compiler to perform an automatic type conversion to make an argument conform to the expected type of some existing routine. Polymorphism allows a single routine to accept argu- ments of multiple types, provided that it attempts to use them only in ways that their types support.

3CHECK YOUR UNDERSTANDING 21. Explain the importance of information hiding.

* What is an opaque export?
* Why might it be useful to distinguish between the header and the body of a
  module?
* What does it mean for a scope to be closed?

* Explain the distinction between “modules as managers” and “modules as
  types.”

* How do classes differ from modules?
* Why might it be useful to have modules and classes in the same language?

* Why does the use of dynamic scoping imply the need for run-time type check-
  ing?

* Explain the purpose of a compiler’s symbol table.
* What are aliases? Why are they considered a problem in language design and
  implementation?
* Explain the value of the restrict qualiﬁer in C.

* What is overloading? How does it differ from coercion and polymorphism?
* What are type classes in Haskell? What purpose do they serve?

3.6 The Binding of Referencing Environments

We have seen in Section 3.3 how scope rules determine the referencing environ- ment of a given statement in a program. Static scope rules specify that the refer- encing environment depends on the lexical nesting of program blocks in which names are declared. Dynamic scope rules specify that the referencing environ- ment depends on the order in which declarations are encountered at run time. An additional issue that we have not yet considered arises in languages that allow one to create a reference to a subroutine—for example, by passing it as a parame- ter. When should scope rules be applied to such a subroutine: when the reference is ﬁrst created, or when the routine is ﬁnally called? The answer is particularly im- portant for languages with dynamic scoping, though we shall see that it matters even in languages with static scoping. A dynamic scoping example appears as pseudocode in Figure 3.13. Procedure EXAMPLE 3.30

Deep and shallow binding print selected records is assumed to be a general-purpose routine that knows how to traverse the records in a database, regardless of whether they represent people, sprockets, or salads. It takes as parameters a database, a predicate to make print/don’t print decisions, and a subroutine that knows how to format the data in the records of this particular database. We have hypothesized that procedure print person uses the value of nonlocal variable line length to calculate the num- ber and width of columns in its output. In a language with dynamic scoping, it is natural for procedure print selected records to declare and initialize this variable locally, knowing that code inside print routine will pick it up if needed. For this coding technique to work, the referencing environment of print routine must not be created until the routine is actually called by print selected records. This late binding of the referencing environment of a subroutine that has been passed as a parameter is known as shallow binding. It is usually the default in languages with dynamic scoping. For function older than threshold, by contrast, shallow binding may not work well. If, for example, procedure print selected records happens to have a local variable named threshold, then the variable set by the main program to inﬂu- ence the behavior of older than threshold will not be visible when the function is ﬁnally called, and the predicate will be unlikely to work correctly. In such a situation, the code that originally passes the function as a parameter has a par- ticular referencing environment (the current one) in mind; it does not want the routine to be called in any other environment. It therefore makes sense to bind the environment at the time the routine is ﬁrst passed as a parameter, and then restore that environment when the routine is ﬁnally called. That is, we arrange for older than threshold to see, when it is eventually called, the same referencing environment it would have seen if it had been called at the point where the refer- ence was created. This early binding of the referencing environment is known as deep binding. It is almost always the default in languages with static scoping, and is sometimes available as an option with dynamic scoping as well. ■

![Figure 3.13 Program (in...](images/page_186_vector_431.png)
*Figure 3.13 Program (in pseudocode) to illustrate the importance of binding rules. One might argue that deep binding is appropriate for the environment of function older than threshold (for access to threshold), while shallow binding is appropriate for the environment of procedure print person (for access to line length).*

3.6.1 Subroutine Closures

Deep binding is implemented by creating an explicit representation of a refer- encing environment (generally the one in which the subroutine would execute if called at the present time) and bundling it together with a reference to the subroutine. The bundle as a whole is referred to as a closure. Usually the sub- routine itself can be represented in the closure by a pointer to its code. In a lan- guage with dynamic scoping, the representation of the referencing environment depends on whether the language implementation uses an association list or a

![Figure 3.14 Deep binding...](images/page_187_vector_225.png)
*Figure 3.14 Deep binding in Python. At right is a conceptual view of the run-time stack. Referencing environments captured in closures are shown as dashed boxes and arrows. When B is called via formal parameter P, two instances of I exist. Because the closure for P was created in the initial invocation of A, B’s static link (solid arrow) points to the frame of that earlier invocation. B uses that invocation’s instance of I in its print statement, and the output is a 1.*

central reference table for run-time lookup of names; we consider these alterna- tives at the end of Section C 3.4.2. In early dialects of Lisp, which used dynamic scoping, deep binding was avail- able via the built-in primitive function, which took a function as its argument and returned a closure whose referencing environment was the one in which the function would have executed if called at that moment in time. The closure could then be passed as a parameter to another function. If and when it was eventually called, it would execute in the saved environment. (Closures work slightly differ- ently from “bare” functions in most Lisp dialects: they must be called by passing them to the built-in primitives funcall or apply.) At ﬁrst glance, one might be tempted to think that the binding time of refer- encing environments would not matter in a language with static scoping. After all, the meaning of a statically scoped name depends on its lexical nesting, not on the ﬂow of execution, and this nesting is the same whether it is captured at the time a subroutine is passed as a parameter or at the time the subroutine is called. The catch is that a running program may have more than one instance of an ob- ject that is declared within a recursive subroutine. A closure in a language with static scoping captures the current instance of every object, at the time the closure is created. When the closure’s subroutine is called, it will ﬁnd these captured in- stances, even if newer instances have subsequently been created by recursive calls. One could imagine combining static scoping with shallow binding [VF82], but the combination does not seem to make much sense, and does not appear to have been adopted in any language. Figure 3.14 contains a Python program that illus- EXAMPLE 3.31

Binding rules with static scoping trates the impact of binding rules in the presence of static scoping. This program prints a 1. With shallow binding it would print a 2. ■

It should be noted that binding rules matter with static scoping only when accessing objects that are neither local nor global, but are deﬁned at some inter- mediate level of nesting. If an object is local to the currently executing subroutine, then it does not matter whether the subroutine was called directly or through a closure; in either case local objects will have been created when the subroutine started running. If an object is global, there will never be more than one instance, since the main body of the program is not recursive. Binding rules are therefore irrelevant in languages like C, which has no nested subroutines, or Modula-2, which allows only outermost subroutines to be passed as parameters, thus ensur- ing that any variable deﬁned outside the subroutine is global. (Binding rules are also irrelevant in languages like PL/I and Ada 83, which do not permit subroutines to be passed as parameters at all.) Suppose then that we have a language with static scoping in which nested sub- routines can be passed as parameters, with deep binding. To represent a closure for subroutine S, we can simply save a pointer to S’s code together with the static link that S would use if it were called right now, in the current environment. When S is ﬁnally called, we temporarily restore the saved static link, rather than creating a new one. When S follows its static chain to access a nonlocal object, it will ﬁnd the object instance that was current at the time the closure was created. This instance may not have the value it had at the time the closure was created, but its identity, at least, will reﬂect the intent of the closure’s creator.

3.6.2 First-Class Values and Unlimited Extent

In general, a value in a programming language is said to have ﬁrst-class status if it can be passed as a parameter, returned from a subroutine, or assigned into a variable. Simple types such as integers and characters are ﬁrst-class values in most programming languages. By contrast, a “second-class” value can be passed as a parameter, but not returned from a subroutine or assigned into a variable, and a “third-class” value cannot even be passed as a parameter. As we shall see in Section 9.3.2, labels (in languages that have them) are usually third-class val- ues, but they are second-class values in Algol. Subroutines display the most vari- ation. They are ﬁrst-class values in all functional programming languages and most scripting languages. They are also ﬁrst-class values in C# and, with some restrictions, in several other imperative languages, including Fortran, Modula-2 and -3, Ada 95, C, and C++.10 They are second-class values in most other imper- ative languages, and third-class values in Ada 83. Our discussion of binding so far has considered only second-class subroutines. First-class subroutines in a language with nested scopes introduce an additional level of complexity: they raise the possibility that a reference to a subroutine may

10 Some authors would say that ﬁrst-class status requires anonymous function deﬁnitions—lambda expressions—that can be embedded in other expressions. C#, several scripting languages, and all functional languages meet this requirement, but many imperative languages do not.

outlive the execution of the scope in which that routine was declared. Consider EXAMPLE 3.32

Returning a ﬁrst-class subroutine in Scheme the following example in Scheme:

  1.
  (define plus-x
  2.
  (lambda (x)
  3.
  (lambda (y) (+ x y))))
  4.
  ...
  5.
  (let ((f (plus-x 2)))
  6.
  (f 3))
  ; returns 5

Here the let construct on line 5 declares a new function, f, which is the result of calling plus-x with argument 2. Function plus-x is deﬁned at line 1. It returns the (unnamed) function declared at line 3. But that function refers to parameter x of plus-x. When f is called at line 6, its referencing environment will include the x in plus-x, despite the fact that plus-x has already returned (see Figure 3.15). Somehow we must ensure that x remains available. ■ If local objects were destroyed (and their space reclaimed) at the end of each scope’s execution, then the referencing environment captured in a long-lived clo- sure might become full of dangling references. To avoid this problem, most func- tional languages specify that local objects have unlimited extent: their lifetimes continue indeﬁnitely. Their space can be reclaimed only when the garbage col- lection system is able to prove that they will never be used again. Local objects (other than own/static variables) in most imperative languages have limited ex- tent: they are destroyed at the end of their scope’s execution. (C# and Smalltalk are exceptions to the rule, as are most scripting languages.) Space for local ob- jects with limited extent can be allocated on a stack. Space for local objects with unlimited extent must generally be allocated on a heap. Given the desire to maintain stack-based allocation for the local variables of subroutines, imperative languages with ﬁrst-class subroutines must generally adopt alternative mechanisms to avoid the dangling reference problem for clo- sures. C and (pre-Fortran 90) Fortran, of course, do not have nested subrou- tines. Modula-2 allows references to be created only to outermost subroutines (outermost routines are ﬁrst-class values; nested routines are third-class values). Modula-3 allows nested subroutines to be passed as parameters, but only outer-

DESIGN & IMPLEMENTATION

3.9 Binding rules and extent Binding mechanisms and the notion of extent are closely tied to implementa- tion issues. A-lists make it easy to build closures (Section C 3.4.2), but so do the non-nested subroutines of C and the rule against passing nonglobal sub- routines as parameters in Modula-2. In a similar vein, the lack of ﬁrst-class subroutines in many imperative languages reﬂects in large part the desire to avoid heap allocation, which would be needed for local variables with unlim- ited extent.

![Figure 3.15 The need...](images/page_190_vector_150.png)
*Figure 3.15 The need for unlimited extent. When function plus-x is called in Example 3.32, it returns (left side of the ﬁgure) a closure containing an anonymous function. The referencing environment of that function encompasses both plus-x and main—including the local variables of plus-x itself. When the anonymous function is subsequently called (right side of the ﬁgure), it must be able to access variables in the closure’s environment—in particular, the x inside plus-x—despite the fact that plus-x is no longer active.*

most routines to be returned or stored in variables (outermost routines are ﬁrst- class values; nested routines are second-class values). Ada 95 allows a nested rou- tine to be returned, but only if the scope in which it was declared is the same as, or larger than, the scope of the declared return type. This containment rule, while more conservative than strictly necessary (it forbids the Ada equivalent of Figure 3.14), makes it impossible to propagate a subroutine reference to a portion of the program in which the routine’s referencing environment is not active.

3.6.3 Object Closures

As noted in Section 3.6.1, the referencing environment in a closure will be non- trivial only when passing a nested subroutine. This means that the implementa- tion of ﬁrst-class subroutines is trivial in a language without nested subroutines. At the same time, it means that a programmer working in such a language is missing a useful feature: the ability to pass a subroutine with context. In object- oriented languages, there is an alternative way to achieve a similar effect: we can encapsulate our subroutine as a method of a simple object, and let the object’s ﬁelds hold context for the method. In Java we might write the equivalent of Ex- EXAMPLE 3.33

An object closure in Java ample 3.32 as follows:

```
interface IntFunc {
public int call(int i);
}
class PlusX implements IntFunc {
final int x;
PlusX(int n) { x = n; }
public int call(int i) { return i + x; }
}
...
IntFunc f = new PlusX(2);
System.out.println(f.call(3));
// prints 5
```

Here the interface IntFunc deﬁnes a static type for objects enclosing a function from integers to integers. Class PlusX is a concrete implementation of this type, and can be instantiated for any integer constant x. Where the Scheme code in Example 3.32 captured x in the subroutine closure returned by (plus-x 2), the Java code here captures x in the object closure returned by new PlusX(2). ■ An object that plays the role of a function and its referencing environment may variously be called an object closure, a function object, or a functor. (This is unrelated to use of the term functor in Prolog, ML, or Haskell.) In C#, a ﬁrst-class EXAMPLE 3.34

Delegates in C# subroutine is an instance of a delegate type:

delegate int IntFunc(int i);

This type can be instantiated for any subroutine that matches the speciﬁed argu- ment and return types. That subroutine may be static, or it may be a method of some object:

```
static int Plus2(int i)
return i + 2;
...
IntFunc f = new IntFunc(Plus2);
Console.WriteLine(f(3));
// prints 5
```

class PlusX int x; public PlusX(int n) x = n; public int call(int i) return i + x; ... IntFunc g = new IntFunc(new PlusX(2).call); Console.WriteLine(g(3)); // prints 5 ■

Remarkably, though C# does not permit subroutines to nest in the general EXAMPLE 3.35

Delegates and unlimited extent case, it does allow delegates to be instantiated in-line from anonymous (unnamed) methods. These allow us to mimic the code of Example 3.32:

```
static IntFunc PlusY(int y) {
return delegate(int i) { return i + y; };
}
...
IntFunc h = PlusY(2);
```

Here y has unlimited extent! The compiler arranges to allocate it in the heap, and to refer to it indirectly through a hidden pointer, included in the closure. This implementation incurs the cost of dynamic storage allocation (and eventual garbage collection) only when it is needed; local variables remain in the stack in the common case. ■ Object closures are sufﬁciently important that some languages support them with special syntax. In C++, an object of a class that overrides operator() can EXAMPLE 3.36

Function objects in C++ be called as if it were a function:

```
class int_func {
public:
virtual int operator()(int i) = 0;
};
class plus_x : public int_func {
const int x;
public:
plus_x(int n) : x(n) { }
virtual int operator()(int i) { return i + x; }
};
...
plus_x f(2);
cout << f(3) << "\n";
// prints 5
```

Object f could also be passed to any function that expected a parameter of class int_func. ■

3.6.4 Lambda Expressions

In most of our examples so far, closures have corresponded to subroutines that were declared—and named—in the usual way. In the Scheme code of Exam- ple 3.32, however, we saw an anonymous function—a lambda expression. Simi- larly, in Example 3.35, we saw an anonymous delegate in C#. That example can EXAMPLE 3.37

A lambda expression in C# be made even simpler using C#’s lambda syntax:

```
static IntFunc PlusY(int y) {
return i => i + y;
}
```

Here the keyword delegate of Example 3.35 has been replaced by an => sign that separates the anonymous function’s parameter list (in this case, just i) from its body (the expression i + y). In a function with more than one parameter, the parameter list would be parenthesized; in a longer, more complicated function, the body could be a code block, with one or more explicit return statements. ■

The term “lambda expression” comes from the lambda calculus, a formal no- tation for functional programming that we will consider in more detail in Chap- ter 11. As one might expect, lambda syntax varies quite a bit from one language EXAMPLE 3.38

Variety of lambda syntax to another:

```
(lambda (i j) (> i j) i j)
; Scheme
```

```
(int i, int j) => i > j ? i : j
// C#
```

```
fun i j -> if i > j then i else j
(* OCaml *)
```

```
->(i, j){ i > j ? i : j }
# Ruby
```

Each of these expressions evaluates to the larger of two parameters.

In Scheme and OCaml, which are predominately functional languages, a lambda expression simply is a function, and can be called in the same way as any other function:

```
; Scheme:
((lambda (i j) (> i j) i j) 5 8)
; evaluates to 8
```

```
(* OCaml: *)
(fun i j -> if i > j then i else j) 5 8
(* likewise *)
```

In Ruby, which is predominately imperative, a lambda expression must be called explicitly:

print ->(i, j){ i > j ? i : j }.call(5, 8)

In C#, the expression must be assigned into a variable (or passed into a parameter) before it can be invoked:

```
Func<int, int, int> m = (i, j) => i > j ? i : j;
Console.WriteLine(m.Invoke(5, 8));
```

Here Func<int, int, int> is how one names the type of a function taking two integer parameters and returning an integer result. ■ In functional programming languages, lambda expressions make it easy to ma- nipulate functions as values—to combine them in various ways to create new functions on the ﬂy. This sort of manipulation is less common in imperative lan- guages, but even there, lambda expressions can help encourage code reuse and generality. One particularly common idiom is the callback—a subroutine, passed into a library, that allows the library to “call back” into the main program when appropriate. Examples of callbacks include a comparison operator passed into a sorting routine, a predicate used to ﬁlter elements of a collection, or a handler to be called in response to some future event (see Section 9.6.2). With the increasing popularity of ﬁrst-class subroutines, lambda expressions have even made their way into C++, where the lack of garbage collection and the emphasis on stack-based allocation make it particularly difﬁcult to solve the problem of variable capture. The adopted solution, in keeping with the nature of the language, stresses efﬁciency and expressiveness more than run-time safety. In the simple case, no capture of nonlocal variables is required. If V is a vector EXAMPLE 3.39

A simple lambda expression in C++11 of integers, the following will print all elements less than 50:

```
for_each(V.begin(), V.end(),
[](int e){ if (e < 50) cout << e << " "; }
);
```

Here for_each is a standard library routine that applies its third parameter—a function—to every element of a collection in the range speciﬁed by its ﬁrst two

parameters. In our example, the function is denoted by a lambda expression, introduced by the empty square brackets. The compiler turns the lambda expres- sion into an anonymous function, which is then passed to for_each via C++’s usual mechanism—a simple pointer to the code. ■ Suppose, however, that we wanted to print all elements less than k, where k is EXAMPLE 3.40

Variable capture in C++ lambda expressions a variable outside the scope of the lambda expression. We now have two options in C++:

[=](int e){ if (e < k) cout << e << " "; }

[&](int e){ if (e < k) cout << e << " "; }

Both of these cause the compiler to create an object closure (a function object in C++), which could be passed to (and called from) for_each in the same way as an ordinary function. The difference between the two options is that [=] ar- ranges for a copy of each captured variable to be placed in the object closure; [&] arranges for a reference to be placed there instead. The programmer must choose between these options. Copying can be expensive for large objects, and any changes to the object made after the closure is created will not be seen by the code of the lambda expression when it ﬁnally executes. References allow changes to be seen, but will lead to undeﬁned (and presumably incorrect) behavior if the closure’s lifetime exceeds that of the captured object: C++ does not have un- limited extent. In particularly complex situations, the programmer can specify capture on an object-by-object basis:

[j, &k](int e){ ... // capture j's value and a reference to k, // so they can be used in here ■

DESIGN & IMPLEMENTATION

3.10 Functions and function objects The astute reader may be wondering: In Example 3.40, how does for_each manage to “do the right thing” with two different implementations of its third parameter? After all, sometimes that parameter is implemented as a simple pointer; other times it is a pointer to an object with an operator(), which re- quires a different kind of call. The answer is that for_each is a generic routine (a template in C++). The compiler generates customized implementations of for_each on demand. We will discuss generics in more detail in Section 7.3.1. In some situations, it may be difﬁcult to use generics to distinguish among “function-like” parameters. As an alternative, C++ provides a standard function class, with constructors that allow it to be instantiated from a func- tion, a function pointer, a function object, or a manually created object closure. Something like for_each could then be written as an ordinary (nongeneric) subroutine whose third parameter was a object of class function. In any given call, the compiler would coerce the provided argument to be a function object.

Lambda expressions appear in Java 8 as well, but in a restricted form. In situa- tions where they might be useful, Java has traditionally relied on an idiom known as a functional interface. The Arrays.sort routine, for example, expects a pa- EXAMPLE 3.41

Lambda expressions in Java 8 rameter of type Comparator. To sort an array of personnel records by age, we would (traditionally) have written

```
class AgeComparator implements Comparator<Person> {
public int compare(Person p1, Person p2) {
return Integer.compare(p1.age, p2.age);
}
}
Person[] People = ...
...
Arrays.sort(People, new AgeComparator());
```

Signiﬁcantly, Comparator has only a single abstract method: the compare rou- tine provided by our AgeComparator class. With lambda expressions in Java 8, we can omit the declaration of AgeComparator and simply write

Arrays.sort(People, (p1, p2) -> Integer.compare(p1.age, p2.age));

The key to the simpler syntax is that Comparator is a functional interface, and thus has only a single abstract method. When a variable or formal parameter is declared to be of some functional interface type, Java 8 allows a lambda ex- pression whose parameter and return types match those of the interface’s single method to be assigned into the variable or passed as the parameter. In effect, the compiler uses the lambda expression to create an instance of an anonymous class that implements the interface. ■ As it turns out, coercion to functional interface types is the only use of lambda expressions in Java. In particular, lambda expressions have no types of their own: they are not really objects, and cannot be directly manipulated. Their behav- ior with respect to variable capture is entirely determined by the usual rules for nested classes. We will consider these rules in more detail in Section 10.2.3; for now, sufﬁce it to note that Java, like C++, does not support unlimited extent.

3.7 Macro Expansion

Prior to the development of high-level programming languages, assembly lan- guage programmers could ﬁnd themselves writing highly repetitive code. To ease the burden, many assemblers provided sophisticated macro expansion facilities. Consider the task of loading an element of a two-dimensional array from memory EXAMPLE 3.42

A simple assembly macro into a register. As we shall see in Section 8.2.3, this operation can easily require

half a dozen instructions, with details depending on the hardware instruction set; the size of the array elements; and whether the indices are constants, values in memory, or values in registers. In many early assemblers, one could deﬁne a macro that would replace an expression like ld2d(target reg, array name, row, col- umn, row size, element size) with the appropriate multi-instruction sequence. In a numeric program containing hundreds or thousands of array access operations, this macro could prove extremely useful. ■ When C was created in the early 1970s, it was natural to include a macro pre- EXAMPLE 3.43

Preprocessor macros in C processing facility:

```
#define LINE_LEN 80
#define DIVIDES(a,n) (!((n) % (a)))
/* true iff n has zero remainder modulo a */
#define SWAP(a,b) {int t = (a); (a) = (b); (b) = t;}
#define MAX(a,b) ((a) > (b) ? (a) : (b))
```

Macros like LINE_LEN avoided the need (in early versions of C) to support named constants in the language itself. Perhaps more important, parameterized macros like DIVIDES, MAX, and SWAP were much more efﬁcient than equivalent C func- tions. They avoided the overhead of the subroutine call mechanism (including register saves and restores), and the code they generated could be integrated into any code improvements that the compiler was able to effect in the code surround- ing the call. ■ Unfortunately, C macros suffer from severallimitations, all of which stem from EXAMPLE 3.44

“Gotchas” in C macros the fact that they are implementedby textual substitution, and are not understood by the rest of the compiler. Put another way, they provide a naming and binding mechanism that is separate from—and often at odds with—the rest of the pro- gramming language. In the deﬁnition of DIVIDES, the parentheses around the occurrences of a and n are essential. Without them, DIVIDES(y + z, x) would be replaced by (!(x % y + z)), which is the same as (!((x % y) + z)), according to the rules of prece- dence. In a similar vein, SWAP may behave unexpectedly if the programmer writes SWAP(x, t): textual substitution of arguments allows the macro’s declaration of t to capture the t that was passed. MAX(x++, y++) may also behave unexpect- edly, since the increment side effects will happen more than once. Unfortunately,

DESIGN & IMPLEMENTATION

3.11 Generics as macros In some sense, the ability to import names into an ordinary module provides a primitive sort of generic facility. A stack module that imports its element type, for example, can be inserted (with a text editor) into any context in which the appropriate type name has been declared, and will produce a “customized” stack for that context when compiled. Early versions of C++ formalized this mechanism by using macros to implement templates. Later versions of C++ have made templates (generics) a fully supported language feature, giving them much of the ﬂavor of hygienic macros. (More on templates and on template metaprogramming can be found in Section C 7.3.2.)

in standard C we cannot avoid the extra side effects by assigning the parameters into temporary variables: a C macro that “returns” a value must be an expression, and declarations are one of many language constructs that cannot appear inside (see also Exercise 3.23). ■ Modern languages and compilers have, for the most part, abandoned macros as an anachronism. Named constants are type-safe and easy to implement, and in-line subroutines (to be discussed in Section 9.2.4) provide almost all the per- formance of parameterized macros without their limitations. A few languages (notably Scheme and Common Lisp) take an alternative approach, and integrate macros into the language in a safe and consistent way. So-called hygienic macros implicitly encapsulate their arguments, avoiding unexpected interactions with as- sociativity and precedence. They rename variables when necessary to avoid the capture problem, and they can be used in any expression context. Unlike subrou- tines, however, they are expanded during semantic analysis, making them gen- erally unsuitable for unbounded recursion. Their appeal is that, like all macros, they take unevaluated arguments, which they evaluate lazily on demand. Among other things, this means that they preserve the multiple side effect “gotcha” of our MAX example. Delayed evaluation was a bug in this context, but can sometimes be a feature. We will return to it in Sections 6.1.5 (short-circuit Boolean eval- uation), 9.3.2 (call-by-name parameters), and 11.5 (normal-order evaluation in functional programming languages).

3CHECK YOUR UNDERSTANDING 34. Describe the difference between deep and shallow binding of referencing en- vironments. 35. Why are binding rules particularly important for languages with dynamic scoping? 36. What are ﬁrst-class subroutines? What languages support them? 37. What is a subroutine closure? What is it used for? How is it implemented?

* What is an object closure? How is it related to a subroutine closure?
* Describe how the delegates of C# extend and unify both subroutine and object
  closures.
* Explain the distinction between limited and unlimited extent of objects in a
  local scope.
* What is a lambda expression? How does the support for lambda expressions in
  functional languages compare to that of C# or Ruby? To that of C++ or Java?

* What are macros? What was the motivation for including them in C? What
  problems may they cause?

3.8 Separate Compilation

Since most large programs are constructed and tested incrementally, and since the compilation of a very large program can be a multihour operation, any language designed to support large programs must provide for separate compilation.

IN MORE DEPTH

On the companion site we consider the relationship between modules and sepa- rate compilation. Because they are designed for encapsulation and provide a nar- row interface, modules are the natural choice for the “compilation units” of many programming languages. The separate module headers and bodies of Modula-3 and Ada, for example, are explicitly intended for separate compilation, and reﬂect experience gained with more primitive facilities in other languages. C and C++, by contrast, must maintain backward compatibility with mechanisms designed in the early 1970s. Modern versions of C and C++ include a namespace mechanism that provides module-like data hiding, but names must still be declared before they are used in every compilation unit, and the mechanisms used to accom- modate this rule are purely a matter of convention. Java and C# break with the C tradition by requiring the compiler to infer header information automatically from separately compiled class deﬁnitions; no header ﬁles are required.

## 3.9 Summary and Concluding Remarks

This chapter has addressed the subject of names, and the binding of names to ob- jects (in a broad sense of the word). We began with a general discussion of the notion of binding time—the time at which a name is associated with a particular object or, more generally, the time at which an answer is associated with any open question in language or program design or implementation. We deﬁned the no- tion of lifetime for both objects and name-to-object bindings, and noted that they need not be the same. We then introduced the three principal storage allocation mechanisms—static, stack, and heap—used to manage space for objects. In Section 3.3 we described how the binding of names to objects is governed by scope rules. In some languages, scope rules are dynamic: the meaning of a name is found in the most recently entered scope that contains a declaration and that has not yet been exited. In most modern languages, however, scope rules are static, or lexical: the meaning of a name is found in the closest lexically surrounding scope that contains a declaration. We found that lexical scope rules vary in important but sometimes subtle ways from one language to another. We considered what sorts of scopes are allowed to nest, whether scopes are open or closed, whether the scope of a name encompasses the entire block in which it is declared, and whether

a name must be declared before it is used. We explored the implementation of scope rules in Section 3.4. In Section 3.5 we examined several ways in which bindings relate to one an- other. Aliases arise when two or more names in a given scope are bound to the same object. Overloading arises when one name is bound to multiple objects. We noted that while behavior reminiscent of overloading can sometimes be achieved through coercion or polymorphism, the underlying mechanisms are really very different. In Section 3.6 we considered the question of when to bind a referencing environment to a subroutine that is passed as a parameter, returned from a func- tion, or stored in a variable. Our discussion touched on the notions of closures and lambda expressions, both of which will appear repeatedly in later chapters. In Sections 3.7 and 3.8 we considered macros and separate compilation. Some of the more complicated aspects of lexical scoping illustrate the evolu- tion of language support for data abstraction, a subject to which we will return in Chapter 10. We began by describing the own or static variables of languages like Fortran, Algol 60, and C, which allow a variable that is local to a subroutine to retain its value from one invocation to the next. We then noted that simple modules can be seen as a way to make long-lived objects local to a group of sub- routines, in such a way that they are not visible to other parts of the program. By selectively exporting names, a module may serve as the “manager” for one or more abstract data types. At the next level of complexity, we noted that some languages treat modules as types, allowing the programmer to create an arbitrary number of instances of the abstraction deﬁned by a module. Finally, we noted that object-oriented languages extend the module-as-type approach (as well as the notion of lexical scope) by providing an inheritance mechanism that allows new abstractions (classes) to be deﬁned as extensions or reﬁnements of existing classes. Among the topics considered in this chapter, we saw several examples of useful features (recursion, static scoping, forward references, ﬁrst-class subroutines, un- limited extent) that have been omitted from certain languages because of concern for their implementation complexity or run-time cost. We also saw an example of a feature (the private part of a module speciﬁcation) introduced expressly to facilitate a language’s implementation, and another (separate compilation in C) whose design was clearly intended to mirror a particular implementation. In sev- eral additional aspects of language design (late vs early binding, static vs dynamic scoping, support for coercions and conversions, toleration of pointers and other aliases), we saw that implementation issues play a major role. In a similar vein, apparently simple language rules can have surprising implica- tions. In Section 3.3.3, for example, we considered the interaction of whole-block scope with the requirement that names be declared before they can be used. Like the do loop syntax and white space rules of Fortran (Section 2.2.2) or the if... then ... else syntax of Pascal (Section 2.3.2), poorly chosen scoping rules can make program analysis difﬁcult not only for the compiler, but for human beings as well. In future chapters we shall see several additional examples of features that are both confusing and hard to compile. Of course, semantic utility and ease of

implementation do not always go together. Many easy-to-compile features (e.g., goto statements) are of questionable value at best. We will also see several ex- amples of highly useful and (conceptually) simple features, such as garbage col- lection (Section 8.5.3) and uniﬁcation (Sections 7.2.4, C 7.3.2, and 12.2.1), whose implementations are quite complex.

## 3.10 Exercises

3.1 Indicate the binding time (when the language is designed, when the pro- gram is linked, when the program begins execution, etc.) for each of the following decisions in your favorite programming language and implemen- tation. Explain any answers you think are open to interpretation.

The number of built-in functions (math, type queries, etc.) The variable declaration that corresponds to a particular variable refer- ence (use) The maximum length allowed for a constant (literal) character string The referencing environment for a subroutine that is passed as a pa- rameter The address of a particular library routine The total amount of space occupied by program code and data

3.2 In Fortran 77, local variables were typically allocated statically. In Algol and its descendants (e.g., Ada and C), they are typically allocated in the stack. In Lisp they are typically allocated at least partially in the heap. What accounts for these differences? Give an example of a program in Ada or C that would not work correctly if local variables were allocated statically. Give an example of a program in Scheme or Common Lisp that would not work correctly if local variables were allocated on the stack.

3.3 Give two examples in which it might make sense to delay the binding of an implementation decision, even though sufﬁcient information exists to bind it early.

3.4 Give three concrete examples drawn from programming languages with which you are familiar in which a variable is live but not in scope.

3.5 Consider the following pseudocode:

  1.
  procedure main()
  2.
  a : integer := 1
  3.
  b : integer := 2

  4.
  procedure middle()
  5.
  b : integer := a

  6.
  procedure inner()
  7.
  print a, b

  8.
  a : integer := 3

  9.
  –– body of middle
  10.
  inner()
  11.
  print a, b

  12.
  –– body of main
  13.
  middle()
  14.
  print a, b

Suppose this was code for a language with the declaration-order rules of C (but with nested subroutines)—that is, names must be declared before use, and the scope of a name extends from its declaration through the end of the block. At each print statement, indicate which declarations of a and b are in the referencing environment. What does the program print (or will the compiler identify static semantic errors)? Repeat the exercise for the declaration-order rules of C# (names must be declared before use, but the scope of a name is the entire block in which it is declared) and of Modula-3 (names can be declared in any order, and their scope is the entire block in which they are declared).

3.6 Consider the following pseudocode, assuming nested subroutines and static scope:

procedure main() g : integer

procedure B(a : integer) x : integer

procedure A(n : integer) g := n

procedure R(m : integer) write integer(x) x /:= 2 –– integer division if x > 1 R(m + 1) else A(m)

–– body of B x := a × a R(1)

–– body of main B(3) write integer(g)

(a) What does this program print?

![Figure 3.16 List management...](images/page_202_vector_397.png)
*Figure 3.16 List management routines for Exercise 3.7.*

(b) Show the frames on the stack when A has just been called. For each frame, show the static and dynamic links. (c) Explain how A ﬁnds g.

3.7 As part of the development team at MumbleTech.com, Janet has written a list manipulation library for C that contains, among other things, the code in Figure 3.16.

(a) Accustomed to Java, new team member Brad includes the following code in the main loop of his program:

```
list_node* L = 0;
while (more_widgets()) {
L = insert(next_widget(), L);
}
L = reverse(L);
```

Sadly, after running for a while, Brad’s program always runs out of memory and crashes. Explain what’s going wrong. (b) After Janet patiently explains the problem to him, Brad gives it another try:

```
list_node* L = 0;
while (more_widgets()) {
L = insert(next_widget(), L);
}
list_node* T = reverse(L);
delete_list(L);
L = T;
```

This seems to solve the insufﬁcient memory problem, but where the program used to produce correct results (before running out of mem- ory), now its output is strangely corrupted, and Brad goes back to Janet for advice. What will she tell him this time?

3.8 Rewrite Figures 3.6 and 3.7 in C. You will need to use separate compilation for name hiding.

3.9 Consider the following fragment of code in C:

```
{
int a, b, c;
...
{
int d, e;
...
{
int f;
...
}
...
}
...
{
int g, h, i;
...
}
...
}
```

(a) Assume that each integer variable occupies four bytes. How much total space is required for the variables in this code? (b) Describe an algorithm that a compiler could use to assign stack frame offsets to the variables of arbitrary nested blocks, in a way that mini- mizes the total space required.

3.10 Consider the design of a Fortran 77 compiler that uses static allocation for the local variables of subroutines. Expanding on the solution to the pre- vious question, describe an algorithm to minimize the total space required for these variables. You may ﬁnd it helpful to construct a call graph data

structure in which each node represents a subroutine, and each directed arc indicates that the subroutine at the tail may sometimes call the subroutine at the head.

3.11 Consider the following pseudocode:

procedure P(A, B : real) X : real

procedure Q(B, C : real) Y : real . . .

procedure R(A, C : real) Z : real . . . –– (*) . . .

Assuming static scope, what is the referencing environment at the location marked by (*)?

3.12 Write a simple program in Scheme that displays three different behaviors, depending on whether we use let, let*, or letrec to declare a given set of names. (Hint: To make good use of letrec, you will probably want your names to be functions [lambda expressions].)

3.13 Consider the following program in Scheme:

```
(define A
(lambda()
(let* ((x 2)
(C (lambda (P)
(let ((x 4))
(P))))
(D (lambda ()
x))
(B (lambda ()
(let ((x 3))
(C D)))))
(B))))
```

What does this program print? What would it print if Scheme used dynamic scoping and shallow binding? Dynamic scoping and deep binding? Explain your answers.

3.14 Consider the following pseudocode:

x : integer –– global

procedure set x(n : integer) x := n

procedure print x() write integer(x)

procedure ﬁrst() set x(1) print x()

procedure second() x : integer set x(2) print x()

set x(0) ﬁrst() print x() second() print x()

What does this program print if the language uses static scoping? What does it print with dynamic scoping? Why?

3.15 The principal argument in favor of dynamic scoping is that it facilitates the customization of subroutines. Suppose, for example, that we have a library routine print integer that is capable of printing its argument in any of several bases (decimal, binary, hexadecimal, etc.). Suppose further that we want the routine to use decimal notation most of the time, and to use other bases only in a few special cases: we do not want to have to specify a base explicitly on each individual call. We can achieve this result with dynamic scoping by having print integer obtain its base from a nonlocal variable print base. We can establish the default behavior by declaring a variable print base and setting its value to 10 in a scope encountered early in execution. Then, any time we want to change the base temporarily, we can write

begin –– nested block print base : integer := 16 –– use hexadecimal print integer(n)

The problem with this argument is that there are usually other ways to achieve the same effect, without dynamic scoping. Describe at least two for the print integer example.

3.16 As noted in Section 3.6.3, C# has unusually sophisticated support for ﬁrst- class subroutines. Among other things, it allows delegates to be instantiated from anonymous nested methods, and gives local variables and parameters unlimited extent when they may be needed by such a delegate. Consider the implications of these features in the following C# program:

```
using System;
public delegate int UnaryOp(int n);
// type declaration: UnaryOp is a function from ints to ints
```

```
public class Foo {
static int a = 2;
static UnaryOp b(int c) {
int d = a + c;
Console.WriteLine(d);
return delegate(int n) { return c + n; };
}
public static void Main(string[] args) {
Console.WriteLine(b(3)(4));
}
}
```

What does this program print? Which of a, b, c, and d, if any, is likely to be statically allocated? Which could be allocated on the stack? Which would need to be allocated in the heap? Explain.

3.17 If you are familiar with structured exception handling, as provided in Ada, C++, Java, C#, ML, Python, or Ruby, consider how this mechanism relates to the issue of scoping. Conventionally, a raise or throw statement is thought of as referring to an exception, which it passes as a parameter to a handler-ﬁnding library routine. In each of the languages mentioned, the exception itself must be declared in some surrounding scope, and is sub- ject to the usual static scope rules. Describe an alternative point of view, in which the raise or throw is actually a reference to a handler, to which it transfers control directly. Assuming this point of view, what are the scope rules for handlers? Are these rules consistent with the rest of the language? Explain. (For further information on exceptions, see Section 9.4.)

3.18 Consider the following pseudocode:

x : integer –– global

procedure set x(n : integer) x := n

procedure print x() write integer(x)

procedure foo(S, P : function; n : integer) x : integer := 5 if n in {1, 3} set x(n) else S(n)

if n in {1, 2} print x() else P

set x(0); foo(set x, print x, 1); print x() set x(0); foo(set x, print x, 2); print x() set x(0); foo(set x, print x, 3); print x() set x(0); foo(set x, print x, 4); print x()

Assume that the language uses dynamic scoping. What does the program print if the language uses shallow binding? What does it print with deep binding? Why?

3.19 Consider the following pseudocode:

x : integer := 1 y : integer := 2

procedure add() x := x + y

procedure second(P : procedure) x : integer := 2 P()

procedure ﬁrst y : integer := 3 second(add)

ﬁrst() write integer(x) (a) What does this program print if the language uses static scoping? (b) What does it print if the language uses dynamic scoping with deep bind- ing? (c) What does it print if the language uses dynamic scoping with shallow binding?

3.20 Consider mathematical operations in a language like C++, which supports both overloading and coercion. In many cases, it may make sense to pro- vide multiple, overloaded versions of a function, one for each numeric type or combination of types. In other cases, we might use a single version— probably deﬁned for double-precision ﬂoating point arguments—and rely on coercion to allow that function to be used for other numeric types (e.g., integers). Give an example in which overloading is clearly the preferable approach. Give another in which coercion is almost certainly better.

3.21 In a language that supports operator overloading, build support for ration- al numbers. Each number should be represented internally as a (numera- tor, denominator) pair in simplest form, with a positive denominator. Your

code should support unary negation and the four standard arithmetic oper- ators. For extra credit, create a conversion routine that accepts two ﬂoating- point parameters—a value and a error bound—and returns the simplest (smallest denominator) rational number within the given error bound of the given value.

3.22 In an imperative language with lambda expressions (e.g., C#, Ruby, C++, or Java), write the following higher-level functions. (A higher-level function, as we shall see in Chapter 11, takes other functions as argument and/or returns a function as a result.)

compose(g, f)—returns a function h such that h(x) == g(f(x)). map(f, L)—given a function f and a list L returns a list M such that the ith element of M is f(e), where e is the ith element of L. filter(L, P)—given a list L and a predicate (Boolean-returning function) P, returns a list containing all and only those elements of L for which P is true.

Ideally, your code should work for any argument or list element type.

3.23 Can you write a macro in standard C that “returns” the greatest common divisor of a pair of arguments, without calling a subroutine? Why or why not? 3.24–3.31 In More Depth.

## 3.11 Explorations

3.32 Experiment with naming rules in your favorite programming language. Read the manual, and write and compile some test programs. Does the language use lexical or dynamic scoping? Can scopes nest? Are they open or closed? Does the scope of a name encompass the entire block in which it is declared, or only the portion after the declaration? How does one declare mutually recursive types or subroutines? Can subroutines be passed as pa- rameters, returned from functions, or stored in variables? If so, when are referencing environments bound?

3.33 List the keywords (reserved words) of one or more programming languages. List the predeﬁned identiﬁers. (Recall that every keyword is a separate to- ken. An identiﬁer cannot have the same spelling as a keyword.) What cri- teria do you think were used to decide which names should be keywords and which should be predeﬁned identiﬁers? Do you agree with the choices? Why or why not?

3.34 If you have experience with a language like C, C++, or Rust, in which dy- namically allocated space must be manually reclaimed, describe your ex- perience with dangling references or memory leaks. How often do these

bugs arise? How do you ﬁnd them? How much effort does it take? Learn about open-source or commercial tools for ﬁnding storage bugs (Valgrind is a popular open-source example). Do such tools weaken the argument for automatic garbage collection?

3.35 A few languages—notably Euclid and Turing, make every subroutine a closed scope, and require it to explicitly import any nonlocal names it uses. The import lists can be thought of as explicit, mandatory documentation of a part of the subroutine interface that is usually implicit. The use of import lists also makes it easy for Euclid and Turing to prohibit passing a variable, by reference, to a subroutine that also accesses that variable directly, thereby avoiding the errors alluded to in Example 3.20. In programs you have written, how hard would it have been to document every use of a nonlocal variable? Would the effort be worth the improve- ment in the quality of documentation and error rates?

3.36 We learned in Section 3.3.6 that modern languages have generally aban- doned dynamic scoping. One place it can still be found is in the so-called environment variables of the Unix programming environment. If you are not familiar with these, read the manual page for your favorite shell (com- mand interpreter—ksh/bash, csh/tcsh, etc.) to learn how these behave. Explain why the usual alternatives to dynamic scoping (default parameters and static variables) are not appropriate in this case.

3.37 Compare the mechanisms for overloading of enumeration names in Ada and in Modula-3 or C# (Section 3.5.2). One might argue that the (histor- ically more recent) Modula-3/C# approach moves responsibility from the compiler to the programmer: it requires even an unambiguous use of an enumeration constant to be annotated with its type. Why do you think this approach was chosen by the language designers? Do you agree with the choice? Why or why not?

3.38 Learn about tied variables in Perl. These allow the programmer to asso- ciate an ordinary variable with an (object-oriented) object in such a way that operations on the variable are automatically interpreted as method in- vocations on the object. As an example, suppose we write tie $my_var, "my_class";. The interpreter will create a new object of class my_class, which it will associate with scalar variable $my_var. For purposes of dis- cussion, call that object O. Now, any attempt to read the value of $my_var will be interpreted as a call to method O->FETCH(). Similarly, the assign- ment $my_var = value will be interpreted as a call to O->STORE(value). Array, hash, and ﬁlehandle variables, which support a larger set of built-in operations, provide access to a larger set of methods when tied. Compare Perl’s tying mechanism to the operator overloading of C++. Which features of each language can be convenientlyemulated by the other?

3.39 Do you think coercion is a good idea? Why or why not?

3.40 The syntax for lambda expressions in Ruby evolved over time, with the re- sult that there are now four ways to pass a block into a method as a closure:

by placing it after the end of the argument list (in which case it become an extra, ﬁnal parameter); by passing it to Proc.new; or, within the argument list, by preﬁxing it with the keyword lambda or by writing it in -> lambda notation. Investigate these options. Which came ﬁrst? Which came later? What are their comparative advantages? Are their any minor differences in their behavior?

3.41 Lambda expressions were a late addition to the Java programming language: they were strongly resisted for many years. Research the controversy sur- rounding them. Where do your sympathies lie? What alternative proposals were rejected? Do you ﬁnd any of them appealing?

3.42 Give three examples of features that are not provided in some language with which you are familiar, but that are common in other languages. Why do you think these features are missing? Would they complicate the implemen- tation of the language? If so, would the complication (in your judgment) be justiﬁed?

3.43–3.47 In More Depth.

## 3.12 Bibliographic Notes

This chapter has traced the evolution of naming and scoping mechanisms through a very large number of languages, including Fortran (several versions), Basic, Algol 60 and 68, Pascal, Simula, C and C++, Euclid, Turing, Modula (1, 2, and 3), Ada (83 and 95), Oberon, Eiffel, Perl, Tcl, Python, Ruby, Rust, Java, and C#. Bibliographic references for all of these can be found in Appendix A. Both modules and objects trace their roots to Simula, which was developed by Dahl, Nygaard, Myhrhaug, and others at the Norwegian Computing Center in the mid-1960s. (Simula I was implemented in 1964; descriptions in this book pertain to Simula 67.) The encapsulation mechanisms of Simula were reﬁned in the 1970s by the developers of Clu, Modula, Euclid, and related languages. Other Simula innovations—inheritance and dynamic method binding in particular— provided the inspiration for Smalltalk, the original and arguably purest of the object-oriented languages. Modern object-oriented languages, including Eiffel, C++, Java, C#, Python, and Ruby, represent to a large extent a reintegration of the evolutionary lines of encapsulation on the one hand and inheritance and dynamic method binding on the other. The notion of information hiding originates in Parnas’s classic paper, “On the Criteria to be Used in Decomposing Systems into Modules” [Par72]. Compara- tive discussions of naming, scoping, and abstraction mechanisms can be found, among other places, in Liskov et al.’s discussion of Clu [LSAS77], Liskov and Gut- tag’s text [LG86, Chap. 4], the Ada Rationale [IBFW91, Chaps. 9–12], Harbison’s text on Modula-3 [Har92, Chaps. 8–9], Wirth’s early work on modules [Wir80], and his later discussion of Modula and Oberon [Wir88a, Wir07]. Further infor- mation on object-oriented languages can be found in Chapter 10.

For a detailed discussion of overloading and polymorphism, see the survey by Cardelli and Wegner [CW85]. Cailliau [Cai82] provides a lighthearted discus- sion of many of the scoping pitfalls noted in Section 3.3.3. Abelson and Suss- man [AS96, p. 11n] attribute the term “syntactic sugar” to Peter Landin. Lambda expressions for C++ are described in the paper of Järvi and Free- man [JF10]. Lambda expressions for Java were developed under JSR 335 of the Java Community Process (documentation at jcp.org).

