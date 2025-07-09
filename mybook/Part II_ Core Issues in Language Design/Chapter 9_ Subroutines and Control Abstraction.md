# Chapter 9: Subroutines and Control Abstraction

## **9**

## **Subroutines and Control Abstraction**

**In the introduction to Chapter 3,** we deﬁned* abstraction* as a process by
which the programmer can associate a name with a potentially complicated pro-
gram fragment, which can then be thought of in terms of its purpose or function,
rather than in terms of its implementation. We sometimes distinguish between
*control abstraction*, in which the principal purpose of the abstraction is to perform
a well-deﬁned operation, and* data abstraction*, in which the principal purpose of
the abstraction is to represent information.1 We will consider data abstraction in
more detail in Chapter 10.
Subroutines are the principal mechanism for control abstraction in most pro-
gramming languages. A subroutine performs its operation on behalf of a* caller*,
who waits for the subroutine to ﬁnish before continuing execution. Most sub-
routines are parameterized: the caller passes arguments that inﬂuence the sub-
routine’s behavior, or provide it with data on which to operate. Arguments are
also called* actual parameters*. They are mapped to the subroutine’s* formal pa-*
*rameters* at the time a call occurs. A subroutine that returns a value is usually
called a* function*. A subroutine that does not return a value is usually called a* pro-*
*cedure*. Statically typed languages typically require a declaration for every called
subroutine, so the compiler can verify, for example, that every call passes the right
number and types of arguments.
As noted in Section 3.2.2, the storage consumed by parameters and local vari-
ables can in most languages be allocated on a stack. We therefore begin this chap-
ter, in Section 9.1, by reviewing the layout of the stack. We then turn in Section 9.2
to the* calling sequences* that serve to maintain this layout. In the process, we revisit
the use of static chains to access nonlocal variables in nested subroutines, and con-
sider (on the companion site) an alternative mechanism, known as a* display*, that
serves a similar purpose. We also consider subroutine inlining and the represen-
tation of closures. To illustrate some of the possible implementation alternatives,
we present (again on the companion site) case studies of the LLVM compiler for

**1**
The distinction betweencontrol and data abstraction is somewhat fuzzy, because the latter usually
encapsulates not only information but also the operations that access and modify that informa-
tion. Put another way, most data abstractions include control abstraction.

**411**

Offsets from frame pointer
time, then the object is placed in a variable-size area at the top of the frame; its
address and dope vector (descriptor) are stored in the ﬁxed-size portion of the
frame, at a statically known offset from the frame pointer (Figure 8.7). If there
are no variable-size objects, then every object within the frame has a statically
known offset from the stack pointer, and the implementation may dispense with
the frame pointer, freeing up a register for other use. If the size of an argument is
not known at compile time, then the argument may be placed in a variable-size
portion of the frame* below* the other arguments, with its address and dope vector
at known offsets from the frame pointer. Alternatively, the caller may simply pass
a temporary address and dope vector, counting on the called routine to copy the
argument into the variable-size area at the top of the frame.
■
In a language with nested subroutines and static scoping (e.g., Ada, Common
**EXAMPLE** 9.3

Static and dynamic links
Lisp, ML, Scheme, or Swift), objects that lie in surrounding subroutines, and

D

B

E

A

Dynamic
links

Static
links


![Figure 9.1 Example of...](images/page_446_vector_295.png)
*Figure 9.1 Example of subroutine nesting, taken from Figure 3.5. Within B, C, and D, all ﬁve routines are visible. Within A and E, routines A, B, and E are visible, but C and D are not. Given the calling sequence A, E, B, D, C, in that order, frames will be allocated on the stack as shown at right, with the indicated static and dynamic links.*

that are thus neither local nor global, can be found by maintaining a* static chain*
(Figure 9.1). Each stack frame contains a reference to the frame of the lexically
surrounding subroutine. This reference is called the* static link*. By analogy, the
saved value of the frame pointer, which will be restored on subroutine return, is
called the* dynamic link*. The static and dynamic links may or may not be the same,
depending on whether the current routine was called by its lexically surrounding
routine, or by some other routine nested in that surrounding routine.
■
Whether or not a subroutine is called directly by the lexically surrounding rou-
tine, we can be sure that the surrounding routine is active; there is no other way
that the current routine could have been visible, allowing it to be called. Consider,
**EXAMPLE** 9.4

Visibility of nested routines
for example, the subroutine nesting shown in Figure 9.1. If subroutine D is called
directly from B, then clearly B’s frame will already be on the stack. How else
could D be called? It is not visible in A or E, because it is nested inside of B. A
moment’s thought makes clear that it is only when control enters B (placing B’s
frame on the stack) that D comes into view. It can therefore be called by C, or
by any other routine (not shown) that is nested inside C or D, but only because
these are also within B.
■

Finally, the caller

**1.** moves the return value to wherever it is needed
**2.** restores caller-saves registers if needed
■

**Special-Case Optimizations**

Many parts of the calling sequence, prologue, and epilogue can be omitted in
common cases. If the hardware passes the return address in a register, then a* leaf*
*routine* (a subroutine that makes no additional calls before returning)2 can simply

**2**
A leaf routine is so named because it is a leaf of the* subroutine call graph*, a data structure men-
tioned in Exercise 3.10.

9.5.2** Transfer**

To transfer from one coroutine to another, the run-time system must change the
program counter (PC), the stack, and the contents of the processor’s registers.
These changes are encapsulated in the transfer operation: one coroutine calls

