15
Building a Runnable Program
As noted in Section 1.6, the various phases of compilation are commonly
grouped into a front end responsible for the analysis of source code, a back end
responsible for the synthesis of target code, and often a “middle end” responsible
for language- and machine-independent code improvement. Chapters 2 and 4
discussed the work of the front end, culminating in the construction of a syntax
tree. The current chapter turns to the work of the back end, and speciﬁcally to
code generation, assembly, and linking. We will continue with code improvement
in Chapter 17.
In Chapters 6 through 10, we often discussed the code that a compiler would
generate to implement various language features. Now we will look at how the
compiler produces that code from a syntax tree, and how it combines the out-
put of multiple compilations to produce a runnable program. We begin in Sec-
tion 15.1 with a more detailed overview of the work of program synthesis than
was possible in Chapter 1. We focus in particular on one of several plausible ways
of dividing that work into phases. In Section 15.2 we then consider the many
possible forms of intermediate code passed between these phases. On the com-
panion site we provide a bit more detail on two concrete examples—the GIMPLE
and RTL formats used by the GNU compilers. We will consider two additional
intermediate forms in Chapter 16: Java bytecode and the Common Intermedi-
ate Language (CIL) used by Microsoft and other implementors of the Common
Language Infrastructure.
In Section 15.3 we discuss the generation of assembly code from an abstract
syntax tree, using attribute grammars as a formal framework. In Section 15.4 we
discuss the internal organization of binary object ﬁles and the layout of programs
in memory. Section 15.5 describes assembly. Section 15.6 considers linking.
15.1
Back-End Compiler Structure
As we noted in Chapter 4, there is less uniformity in back-end compiler structure
than there is in front-end structure. Even such unconventional compilers as text
775
776
Chapter 15 Building a Runnable Program
processors, source-to-source translators, and VLSI layout tools must scan, parse,
and analyze the semantics of their input. When it comes to the back end, however,
even compilers for the same language on the same machine can have very different
internal structure.
As we shall see in Section 15.2, different compilers may use different interme-
diate forms to represent a program internally. They may also differ dramatically
in the forms of code improvement they perform. A simple compiler, or one de-
signed for speed of compilation rather than speed of target code execution (e.g.,
a “just-in-time” compiler) may not do much improvement at all. A just-in-time
or “load-and-go” compiler (one that compiles and then executes a program as a
single high-level operation, without writing the target code to a ﬁle) may not use
a separate linker. In some compilers, much or all of the code generator may be
written automatically by a tool (a “code generator generator”) that takes a formal
description of the target machine as input.
15.1.1 A Plausible Set of Phases


![Figure 15.1 illustrates a...](images/page_809_caption_Figure%2015.1%20illustrates%20a%20plausible%20seven-phase%20structure%20for%20a%20conventional%20com-%20EXAMPLE%2015.1.png)
*Figure 15.1 illustrates a plausible seven-phase structure for a conventional com- EXAMPLE 15.1*

Phases of compilation
piler. The ﬁrst three phases (scanning, parsing, and semantic analysis) are lan-
guage dependent; the last two (target code generation and machine-speciﬁc code
improvement) are machine dependent, and the middle two (intermediate code
generation and machine-independent code improvement) are (to ﬁrst approxi-
mation) dependent on neither the language nor the machine. The scanner and
parser drive a set of action routines that build a syntax tree. The semantic analyzer
traverses the tree, performing all static semantic checks and initializing various at-
tributes (mainly symbol table pointers and indications of the need for dynamic
checks) of use to the back end.
■
While certain code improvements can be performed on syntax trees, a less hi-
erarchical representation of the program makes most code improvement easier.
Our example compiler therefore includes an explicit phase for intermediate code
generation. The code generator begins by grouping the nodes of the tree into
basic blocks, each of which consists of a maximal-length set of operations that
should execute sequentially at run time, with no branches in or out. It then cre-
ates a control ﬂow graph in which the nodes are basic blocks and the arcs represent
interblock control ﬂow. Within each basic block, operations are represented as
instructions for an idealized machine with an unlimited number of registers. We
will call these virtual registers. By allocating a new one for every computed value,
the compiler can avoid creating artiﬁcial connections between otherwise inde-
pendent computations too early in the compilation process.
In Example 1.20 we used a simple greatest common divisor (GCD) program
EXAMPLE 15.2
GCD program abstract
syntax tree (reprise)
to illustrate the phases of compilation. The syntax tree for this program appeared
in Figure 1.6; it is reproduced here (in slightly altered form) as Figure 15.2. A cor-
responding control ﬂow graph appears in Figure 15.3. We will discuss techniques
to generate this graph in Section 15.3 and Exercise 15.6. Additional examples of
control ﬂow graphs will appear in Chapter 17.
■
15.1 Back-End Compiler Structure
777
Character stream
Scanner (lexical analysis)
Token stream
Parser (syntax analysis)
Parse tree
Semantic analysis
Abstract syntax tree
with annotations
Front end
Back end
Intermediate
code generation
Flow graph with pseudo-
instructions in basic blocks
Machine-independent
code improvement
Modified flow graph
Target code generation
Machine-
dependent
(Almost) assembly language
Machine-specific
code improvement
Real assembly language


![Figure 15.1 A plausible...](images/page_810_caption_Figure%2015.1%20A%20plausible%20set%20of%20compiler%20phases.%20Here%20we%20have%20shown%20a%20sharper%20separation%20between%20sema.png)
*Figure 15.1 A plausible set of compiler phases. Here we have shown a sharper separation between semantic analysis and intermediate code generation than we considered in Chapter 1 (see Figure 1.3). Machine-independent code improvement employs an intermediate form that resembles the assembly language for an idealized machine with an unlimited number of reg- isters. Machine-speciﬁc code improvement—register allocation and instruction scheduling in particular—employs the assembly language of the target machine. The dashed line shows a common “break point” between the front end and back end of a two-pass compiler. In some implementations, machine-independent code improvement may be located in a separate “middle end” pass.*

The machine-independent code improvement phase of compilation performs
a variety of transformations on the control ﬂow graph. It modiﬁes the instruction
sequence within each basic block to eliminate redundant loads, stores, and arith-
metic computations; this is local code improvement. It also identiﬁes and removes
a variety of redundancies across the boundaries between basic blocks within a
subroutine; this is global code improvement. As an example of the latter, an ex-
pression whose value is computed immediately before an if statement need not
be recomputed within the code that follows the else. Likewise an expression that
appears within the body of a loop need only be evaluated once if its value will not
change in subsequent iterations. Some global improvements change the number
of basic blocks and/or the arcs among them.
778
Chapter 15 Building a Runnable Program
program
:=
:=
while
call
(5)
call
(6)
call
null
(3)
null
(4)
(5)
(3)
null
=/
if
null
Index
Symbol
Type
(5)
(6)
>
:=
:=
void
int
getint
putint
i
j
type
type
func : (1) → (2)
func : (2) → (1)
(2)
(2)
1
2
3
4
5
6
null
null
(5)
(6)
(5)
(6)
−
−
(5)
(6)
(6)
(5)


![Figure 15.2 Syntax tree...](images/page_811_caption_Figure%2015.2%20Syntax%20tree%20and%20symbol%20table%20for%20the%20GCD%20program.%20The%20only%20difference%20from%20Figure%201.6%20is.png)
*Figure 15.2 Syntax tree and symbol table for the GCD program. The only difference from Figure 1.6 is the addition of explicit null nodes to indicate empty argument lists and to terminate statement lists.*

It is worth noting that “global” code improvement typically considers only the
current subroutine, not the program as a whole. Much recent research in com-
piler technology has been aimed at “truly global” techniques, known as inter-
procedural code improvement. Since programmers are generally unwilling to give
up separate compilation (recompiling hundreds of thousands of lines of code is a
very time-consuming operation), a practical interprocedural code improver must
do much of its work at link time. One of the (many) challenges to be overcome
is to develop a division of labor and an intermediate representation that allow the
compiler to do as much work as possible during (separate) compilation, but leave
enough of the details undecided that the link-time code improver is able to do its
job.
Following machine-independent code improvement, the next phase of com-
pilation is target code generation. This phase strings the basic blocks together
into a linear program, translating each block into the instruction set of the target
machine and generating branch instructions (or “fall-throughs”) that correspond
to the arcs of the control ﬂow graph. The output of this phase differs from real
assembly language primarily in its continued reliance on virtual registers. So long
as the pseudoinstructions of the intermediate form are reasonably close to those
of the target machine, this phase of compilation, though tedious, is more or less
straightforward.
15.1 Back-End Compiler Structure
779
call getint
i := rv
call getint
j := rv
Start
v13 := i
a1 := v13
call putint
F
v1 := i
v2 := j
v3 := v1 =/ v2
test v3
T
End
v4 := i
v5 := j
v6 := v4 > v5
test v6
T
F
v7 := i
v8 := j
v9 := v7 − v 8
i := v9
v10 := j
v11 := i
v12 := v10 − v11
j := v12
null


![Figure 15.3 Control ﬂow...](images/page_812_caption_Figure%2015.3%20Control%20%EF%AC%82ow%20graph%20for%20the%20GCD%20program.%20Code%20within%20basic%20blocks%20is%20shown%20in%20the%20pseudo-a.png)
*Figure 15.3 Control ﬂow graph for the GCD program. Code within basic blocks is shown in the pseudo-assembly notation introduced in Sidebar 5.1, with a different virtual register (here named v1. . . v13) for every computed value. Registers a1 and rv are used to pass values to and from subroutines.*

To reduce programmer effort and increase the ease with which a compiler can
be ported to a new target machine, target code generators are sometimes gen-
erated automatically from a formal description of the machine. Automatically
generated code generators all rely on some sort of pattern-matching algorithm to
replace sequences of intermediate code instructions with equivalent sequences of
target machine instructions. References to several such algorithms can be found
in the Bibliographic Notes at the end of this chapter; details are beyond the scope
of this book.
780
Chapter 15 Building a Runnable Program
The ﬁnal phase of our example compiler structure consists of register alloca-
tion and instruction scheduling, both of which can be thought of as machine-
speciﬁc code improvement. Register allocation requires that we map the unlim-
ited virtual registers employed in earlier phases onto the bounded set of architec-
tural registers available in the target machine. If there aren’t enough architectural
registers to go around, we may need to generate additional loads and stores to
multiplex a given architectural register among two or more virtual registers. In-
struction scheduling (described in Sections C 5.5 and C 17.6) consists of reorder-
ing the instructions of each basic block in an attempt to ﬁll the pipeline(s) of the
target machine.
15.1.2 Phases and Passes
In Section 1.6 we deﬁned a pass of compilation as a phase or sequence of phases
that is serialized with respect to the rest of compilation: it does not start until
previous phases have completed, and it ﬁnishes before any subsequent phases
start. If desired, a pass may be written as a separate program, reading its input
from a ﬁle and writing its output to a ﬁle. Two-pass compilers are particularly
common. They may be divided between semantic analysis and intermediate code
generation or between intermediate code generation and machine-independent
code improvement. In either case, the ﬁrst pass is commonly referred to as the
“front end” and the second pass as the “back end.”
Like most compilers, our example generates symbolic assembly language as
its output (a few compilers, including those written by IBM for the Power family,
generate binary machine code directly). The assembler (not shown in Figure 15.1)
behaves as an extra pass, assigning addresses to fragments of data and code, and
translating symbolic operations into their binary encodings. In most cases, the
input to the compiler will have consisted of source code for a single compilation
unit. After assembly, the output will need to be linked to other fragments of the
application, and to various preexisting subroutine libraries. Some of the work of
linking may be delayed until load time (immediately prior to program execution)
or even until run time (during program execution). We will discuss assembly and
linking in Sections 15.5 through 15.7.
15.2
Intermediate Forms
An intermediate form (IF) provides the connection between phases of machine-
independent code improvement, and continues to represent the program during
the various back-end phases.
IFs can be classiﬁed in terms of their level, or degree of machine dependence.
High-level IFs are often based on trees or directed acyclic graphs (DAGs) that
directly capture the hierarchical structure of modern programming languages.
15.2 Intermediate Forms
781
A high-level IF facilitates certain kinds of machine-independent code improve-
ment, incremental program updates (e.g., in a language-based editor), and direct
interpretation (most interpreters employ a tree-based internal IF). Because the
permissible structure of a tree can be described formally by a set of productions
(as described in Section 4.6), manipulations of tree-based forms can be written as
attribute grammars.
The most common medium-level IFs employ three-address instructions for a
simple idealized machine, typically one with an unlimited number of registers.
Often the instructions are embedded in a control ﬂow graph. Since the typical
instruction speciﬁes two operands, an operator, and a destination, three-address
instructions are sometimes called quadruples. Low-level IFs usually resemble the
assembly language of some particular target machine, most often the physical
machine on which the target code will execute.
Different compilers use different IFs. Many compilers use more than one IF
internally, though in the common two-pass organization one of these is distin-
guished as “the” intermediate form by virtue of being the externally visible con-
nection between the front end and the back end. In the example of Section 15.1.1,
EXAMPLE 15.3
Intermediate forms in
Figure 15.1
the syntax trees passed from semantic analysis to intermediate code generation
constitute a high-level IF. Control ﬂow graphs containing pseudo-assembly lan-
guage (passed in and out of machine-independent code improvement) are a
medium-level IF. The assembly language of the target machine (initially with
virtual registers; later with architectural registers) serves as a low-level IF.
The distinction between “high-,” “medium-,” and “low-level” IFs is of course
somewhat arbitrary: the plausible design space is very large, with a nearly contin-
uous spectrum from abstract to machine-dependent.
■
Compilers that have back ends for several different target architectures tend to
do as much work as possible on a high- or medium-level IF, so that the machine-
independent parts of the code improver can be shared by different back ends. By
contrast, some (but not all) compilers that generate code for a single architecture
perform most code improvement on a comparatively low-level IF, closely mod-
eled after the assembly language of the target machine.
In a multilanguage compiler family, an IF that is independent of both source
language and target machine allows a software vendor who wishes to sell compil-
ers for n languages on m machines to build just n front ends and m back ends,
rather than n × m integrated compilers. Even in a single-language compiler fam-
ily, a common, possibly language-dependent IF simpliﬁes the task of porting to
a new machine by isolating the code that needs to be changed. In a rich pro-
gram development environment, there may be a variety of tools in addition to the
passes of the compiler that understand and operate on the IF. Examples include
editors, assemblers, linkers, debuggers, pretty-printers, and version-management
software. In a language system capable of interprocedural (whole-program) code
improvement, separately compiled modules and libraries may be compiled only
to the IF, rather than the target language, leaving the ﬁnal stages of compilation
to the linker.
782
Chapter 15 Building a Runnable Program
To be stored in a ﬁle, an IF requires a linear representation. Sequences of three-
address instructions are naturally linear. Tree-based IFs can be linearized via or-
dered traversal. Structures like control ﬂow graphs can be linearized by replacing
pointers with indices relative to the beginning of the ﬁle.
15.2.1 GIMPLE and RTL
Many readers will be familiar with the gcc compilers. Distributed as open source
by the Free Software Foundation, gcc is used very widely in both academia and
industry. The standard distribution includes front ends for C, C++, Objective-
C, Ada, Fortran, Go, and Java. Front ends for additional languages, including
Cobol, Modula-2 and 3, Pascal and PL/I, are separately available. The C compiler
is the original, and the one most widely used (gcc originally stood for “GNU C
compiler”). There are back ends for dozens of processor architectures, including
all commercially signiﬁcant options. There are also GNU implementations, not
based on gcc, for some two dozen additional languages.
IN MORE DEPTH
Gcc has three main IFs. Most of the (language-speciﬁc) front ends employ, in-
ternally, some variant of a high-level syntax tree form known as GENERIC. Early
phases of machine-independent code improvement use a somewhat lower-level
tree form known as GIMPLE (still a high-level IF). Later phases use a linear form
known as RTL (register transfer language). RTL is a medium-level IF, but a bit
higher level than most: it overlays a control ﬂow graph on of a sequence of pseu-
doinstructions. RTL was, for many years, the principal IF for gcc. GIMPLE was
introduced in 2005 as a more suitable form for machine-independent code im-
provement. We consider GIMPLE and RTL in more detail on the companion
site.
15.2.2 Stack-Based Intermediate Forms
In situations where simplicity and brevity are paramount, designers often turn to
stack-based languages. Operations in a such a language pop arguments from—
and push results to—a common implicit stack. The lack of named operands
means that a stack-based language can be very compact. In certain HP calcu-
lators (Exercise 4.7), stack-based expression evaluation serves to minimize the
number of keystrokes required to enter equations. For embedded devices and
printers, stack-based evaluation in Forth and Postscript serves to reduce memory
and bandwidth requirements, respectively (see Sidebar 15.1).
Medium-levelstack-based intermediate languages are similarly attractive when
passing code from a compiler to an interpreter or virtual machine. Forty years
15.2 Intermediate Forms
783
ago, P-code (Example 1.15) made it easy to port Pascal to new machines, and
helped to speed the language’s adoption. Today, the compactness of Java bytecode
helps minimize the download time for applets. Common Intermediate Language
(CIL), the analogue of Java bytecode for .NET and other implementations of the
Common Language Infrastructure (CLI), is similarly compact and machine inde-
pendent. As of 2015, .NET runs only on the x86 and ARM, but the open-source
Mono CLI is available for all the major instruction sets. We will consider Java
bytecode and CIL in some detail in Chapter 16.
Unfortunately, stack-based IF is not well suited to many code improvement
techniques: it limits the ability to eliminate redundancy or improve pipeline per-
formance by reordering calculations. For this reason, languages like Java bytecode
and CIL tend to be used mainly as an external format, not as a representation for
code within a compiler.
In many cases, stack-based code for an expression will occupy fewer bytes, but
specify more instructions, than corresponding three-address code. As a concrete
EXAMPLE 15.4
Computing Heron’s
formula
example, consider Heron’s formula to compute the area of a triangle given the
lengths of its sides, a, b, and c:
A =

s(s −a)(s −b)(s −c),
where
s = a + b + c
2


![Figure 15.4 compares bytecode...](images/page_816_caption_Figure%2015.4%20compares%20bytecode%20and%20three-address%20versions%20of%20this%20formula.%20Each%20line%20represents%20a%20sin.png)
*Figure 15.4 compares bytecode and three-address versions of this formula. Each line represents a single instruction. If we assume that a, b, c, and s are all among the ﬁrst few local variables of the current subroutine, both the Java Virtual Ma- chine (JVM) and the CLI will be able to move them to or from the stack with single-byte instructions. Consequently, the second-to-last instruction in the left column is the only one that needs more than a single byte (it takes three: one for*

DESIGN & IMPLEMENTATION
15.1 Postscript
One of the most pervasive uses of stack-based languages today occurs in doc-
ument preparation. Many document compilers (TEX, Microsoft Word, etc.)
generate Postscript or the related Portable Document Format (PDF) as their
target language. (Most document compilers employ some special-purpose in-
termediate language as well, and have multiple back ends, so they can generate
multiple target languages.)
Postscript is stack-based. It is portable, compact, and easy to generate. It
is also written in ASCII, so it can be read (albeit with some difﬁculty) by hu-
man beings. Postscript interpreters are embedded in most professional-quality
printers. Issues of code improvement are relatively unimportant: most of the
time required for printing is consumed by network delays, mechanical paper
transport, and data manipulations embedded in (optimized) library routines;
interpretation time is seldom a bottleneck. Compactness on the other hand is
crucial, because it contributes to network delays.
784
Chapter 15 Building a Runnable Program
push a
r2 := a
push b
r3 := b
push c
r4 := c
add
r1 := r2 + r3
add
r1 := r1 + r4
push 2
r1 := r1 / 2
–– s
divide
pop s
push s
push s
r2 := r1 −r2
–– s −a
push a
subtract
push s
r3 := r1 −r3
–– s −b
push b
subtract
push s
r4 := r1 −r4
–– s −c
push c
subtract
multiply
r3 := r3 × r4
multiply
r2 := r2 × r3
multiply
r1 := r1 × r2
push sqrt
call sqrt
call


![Figure 15.4 Stack-based versus...](images/page_817_caption_Figure%2015.4%20Stack-based%20versus%20three-address%20IF.%20Shown%20are%20two%20versions%20of%20code%20to%20compute%20the%20area%20.png)
*Figure 15.4 Stack-based versus three-address IF. Shown are two versions of code to compute the area of a triangle using Heron’s formula. At left is a stylized version of Java bytecode or CLI Common Intermediate Language. At right is corresponding pseudo-assembler for a machine with three-address instructions. The bytecode requires a larger number of instructions, but occupies less space.*

the push operation and two to specify the sqrt routine). This gives us a total of
23 instructions in 25 bytes.
By contrast, three-address code for the same formula keeps a, b, c, and s in
registers, and requires only 13 instructions. Unfortunately, in typical notation
each instruction but the last will be four bytes in length (the last will be eight),
and our 13 instructions will occupy 56 bytes.
■
15.3
Code Generation
The back-end structure of Figure 15.1 is too complex to present in any detail in a
EXAMPLE 15.5
Simpler compiler structure
single chapter. To limit the scope of our discussion, we will content ourselves in
this chapter with producing correct but naive code. This choice will allow us to
consider a signiﬁcantly simpler middle and back end. Starting with the structure
of Figure 15.1, we drop the machine-independent code improver and then merge
intermediate and target code generation into a single phase. This merged phase
15.3 Code Generation
785
Character stream
Scanner (lexical analysis)
Token stream
Parser (syntax analysis)
Parse tree
Semantic analysis
Abstract syntax tree
with annotations
Front end
Back end
Naive register allocation
Syntax tree with
additional annotations
Target code generation
Assembly language


![Figure 15.5 A simpler,...](images/page_818_caption_Figure%2015.5%20A%20simpler%2C%20nonoptimizing%20compiler%20structure%2C%20assumed%20in%20Section%2015.3.%20The%20target%20code%20ge.png)
*Figure 15.5 A simpler, nonoptimizing compiler structure, assumed in Section 15.3. The target code generation phase closely resembles the intermediate code generation phase of Figure 15.1.*

generates pure, linear assembly language; because we are not performing code
improvements that alter the program’s control ﬂow, there is no need to represent
that ﬂow explicitly in a control ﬂow graph. We also adopt a much simpler register
allocation algorithm, which can operate directly on the syntax tree prior to code
generation, eliminating the need for virtual registers and the subsequent mapping
onto architectural registers. Finally, we drop instruction scheduling. The result-
ing compiler structure appears in Figure 15.5. Its code generation phase closely
resembles the intermediate code generation of Figure 15.1.
■
15.3.1 An Attribute Grammar Example
Like semantic analysis, intermediate code generation can be formalized in terms
of an attribute grammar, though it is most commonly implemented via hand-
written ad hoc traversal of a syntax tree. We present an attribute grammar here
for the sake of clarity.
In Figure 1.7, we presented naive x86 assembly language for the GCD pro-
gram. We will use our attribute grammar example to generate a similar version
here, but for a RISC-like machine, and in pseudo-assembly notation. Because this
notation is now meant to represent target code, rather than medium- or low-level
intermediate code, we will assume a ﬁxed, limited register set reminiscent of real
machines. We will reserve several registers (a1, a2, sp, rv) for special purposes;
others (r1 . . rk) will be available for temporary values and expression evaluation.
Figure 15.6 contains a fragment of our attribute grammar. To save space, we
EXAMPLE 15.6
An attribute grammar for
code generation
have shown only those productions that actually appear in Figure 15.2. As in
786
Chapter 15 Building a Runnable Program
reg names : array [0..k−1] of register name := [“r1”, “r2”, . . . , “rk”]
–– ordered set of temporaries
program −→stmt
 stmt.next free reg := 0
 program.code := [“main:”] + stmt.code + [“goto exit”]
while : stmt1 −→expr stmt2 stmt3
 expr.next free reg := stmt2.next free reg := stmt3.next free reg := stmt1.next free reg
 L1 := new label(); L2 := new label()
stmt1.code := [“goto” L1] + [L2 “:”] + stmt2.code + [L1 “:”] + expr.code
+ [“if” expr.reg “goto” L2] + stmt3.code
if : stmt1 −→expr stmt2 stmt3 stmt4
 expr.next free reg := stmt2.next free reg := stmt3.next free reg := stmt4.next free reg :=
stmt1.next free reg
 L1 := new label(); L2 := new label()
stmt1.code := expr.code + [“if” expr.reg “goto” L1] + stmt3.code + [“goto” L2]
+ [L1 “:”] + stmt2.code + [L2 “:”] + stmt4.code
assign : stmt1 −→id expr stmt2
 expr.next free reg := stmt2.next free reg := stmt1.next free reg
 stmt1.code := expr.code + [id.stp→name “:=” expr.reg] + stmt2.code
read : stmt1 −→id1 id2 stmt2
 stmt1.code := [“a1 := &” id1.stp→name]
–– ﬁle
+ [“call” if id2.stp→type = int then “readint” else . . . ]
+ [id2.stp→name “:= rv”] + stmt2.code
write : stmt1 −→id expr stmt2
 expr.next free reg := stmt2.next free reg := stmt1.next free reg
 stmt1.code := [“a1 := &” id.stp→name]
–– ﬁle
+ [“a2 :=” expr.reg]
–– value
+ [“call” if id.stp→type = int then “writeint” else . . . ] + stmt2.code
writeln : stmt1 −→id stmt2
 stmt1.code := [“a1 := &” id.stp→name] + [“call writeln”] + stmt2.code
null : stmt −→ϵ
 stmt.code := null
‘<>’ : expr1 −→expr2 expr3
 handle op(expr1, expr2, expr3, “̸=”)
‘>’ : expr1 −→expr2 expr3
 handle op(expr1, expr2, expr3, “>”)
‘−’ : expr1 −→expr2 expr3
 handle op(expr1, expr2, expr3, “−”)
id : expr −→ϵ
 expr.reg := reg names[expr.next free reg mod k]
 expr.code := [expr.reg “:=” expr.stp→name]


![Figure 15.6 Attribute grammar...](images/page_819_caption_Figure%2015.6%20Attribute%20grammar%20to%20generate%20code%20from%20a%20syntax%20tree.%20Square%20brackets%20delimit%20individua.png)
*Figure 15.6 Attribute grammar to generate code from a syntax tree. Square brackets delimit individual target instructions. Juxtaposition indicates concatenation within instructions; the ‘+’ operator indicates concatenation of instruction lists. The handle op macro is used in three of the attribute rules. (continued)*

15.3 Code Generation
787
macro handle op(ref result, L operand, R operand, op : syntax tree node)
result.reg := L operand.reg
L operand.next free reg := result.next free reg
R operand.next free reg := result.next free reg + 1
if R operand.next free reg < k
spill code := restore code := null
else
spill code := [“*sp :=” reg names[R operand.next free reg mod k]]
+ [“sp := sp −4”]
restore code := [“sp := sp + 4”]
+ [reg names[R operand.next free reg mod k] “:= *sp”]
result.code := L operand.code + spill code + R operand.code
+ [result.reg “:=” L operand.reg op R operand.reg] + restore code


![Figure 15.6 (continued)...](images/page_820_caption_Figure%2015.6%20%28continued%29.png)
*Figure 15.6 (continued)*

Chapter 4, notation like while : stmt on the left-hand side of a production in-
dicates that a while node in the syntax tree is one of several kinds of stmt node;
it may serve as the stmt in the right-hand side of its parent production. In our
attribute grammar fragment, program, expr, and stmt all have a synthesized at-
tribute code that contains a sequence of instructions. Program has an inherited
attribute name of type string, obtained from the compiler command line. Id has
a synthesized attribute stp that points to the symbol table entry for the identi-
ﬁer. Expr has a synthesized attribute reg that indicates the register that will hold
the value of the computed expression at run time. Expr and stmt have an inher-
ited attribute next free reg that indicates the next register (in an ordered set of
temporaries) that is available for use (i.e., that will hold no useful value at run
time) immediately before evaluation of a given expression or statement. (For
simplicity, we will be managing registers as if they were a stack; more on this in
Section 15.3.2.)
■
Because we use a symbol table in our example, and because symbol tables lie
outside the formal attribute grammar framework, we must augment our attribute
grammar with some extra code for storage management. Speciﬁcally, prior to
evaluating the attribute rules of Figure 15.6, we must traverse the symbol table in
order to calculate stack-frame offsets for local variables and parameters (two of
which—i and j—occur in the GCD program) and in order to generate assembler
directives to allocate space for global variables (of which our program has none).
Storage allocation and other assembler directives will be discussed in more detail
in Section 15.5.
15.3.2 Register Allocation
Evaluation of the rules of the attribute grammar itself consists of two main tasks.
In each subtree we ﬁrst determine the registers that will be used to hold various
quantities at run time; then we generate code. Our naive register allocation strat-
EXAMPLE 15.7
Stack-based register
allocation
788
Chapter 15 Building a Runnable Program
egy uses the next free reg inherited attribute to manage registers r1. . . rk as an
expression evaluation stack. To calculate the value of (a + b) × (c −(d / e)), for
example, we would generate the following:
r1 := a
–– push a
r2 := b
–– push b
r1 := r1 + r2
–– add
r2 := c
–– push c
r3 := d
–– push d
r4 := e
–– push e
r3 := r3 / r4
–– divide
r2 := r2 −r3
–– subtract
r1 := r1 × r2
–– multiply
Allocation of the next register on the “stack” occurs in the production id :
expr −→ϵ, where we use expr.next free reg to index into reg names, the ar-
ray of temporary register names, and in macro handle op, where we increment
next free reg to make this register unavailable during evaluation of the right-
hand operand. There is no need to “pop” the “register stack” explicitly; this hap-
pens automatically when the attribute evaluator returns to a parent node and uses
the parent’s (unmodiﬁed) next free reg attribute. In our example grammar, left-
hand operands are the only constructs that tie up a register during the evaluation
of anything else. In a more complete grammar, other long-term uses of registers
would probably occur in constructs like for loops (for the step size, index, and
bound).
In a particularly complicated fragment of code it is possible to run out of ar-
chitectural registers. In this case we must spill one or more registers to memory.
Our naive register allocator pushes a register onto the program’s subroutine call
stack, reuses the register for another purpose, and then pops the saved value back
into the register before it is needed again. In effect, architectural registers hold the
top k elements of an expression evaluation stack of effectively unlimited size.
■
It should be emphasized that our register allocation algorithm, while correct,
makes very poor use of machine resources. We have made no attempt to reor-
ganize expressions to minimize the number of registers used, or to keep com-
monly used variables in registers over extended periods of time (avoiding loads
and stores). If we were generating medium-levelintermediate code, instead of tar-
get code, we would employ virtual registers, rather than architectural ones, and
would allocate a new one every time we needed it, never reusing one to hold a dif-
ferent value. Mapping of virtual registers to architectural registers would occur
much later in the compilation process.
Target code for the GCD program appears in Figure 15.7. The ﬁrst few lines are
EXAMPLE 15.8
GCD program target code
generated during symbol table traversal, prior to attribute evaluation. Attribute
program.name might be passed to the assembler, to tell it the name of the ﬁle
into which to place the runnable program. A real compiler would probably also
generate assembler directives to embed symbol-table information in the target
program. As in Figure 1.7, the quality of our code is very poor. We will investigate
15.3 Code Generation
789
–– ﬁrst few lines generated during symbol table traversal
.data
–– begin static data
i:
.word 0
–– reserve one word to hold i
j:
.word 0
–– reserve one word to hold j
.text
–– begin text (code)
–– remaining lines accumulated into program.code
main:
a1 := &input –– “input” and “output” are ﬁle control blocks
–– located in a library, to be found by the linker
call readint
–– “readint”, “writeint”, and “writeln” are library subroutines
i := rv
a1 := &input
call readint
j := rv
goto L1
L2: r1 := i
–– body of while loop
r2 := j
r1 := r1 > r2
if r1 goto L3
r1 := j
–– “else” part
r2 := i
r1 := r1 −r2
j := r1
goto L4
L3: r1 := i
–– “then” part
r2 := j
r1 := r1 −r2
i := r1
L4:
L1: r1 := i
–– test terminating condition
r2 := j
r1 := r1 ̸= r2
if r1 goto L2
a1 := &output
r1 := i
a2 := r1
call writeint
a1 := &output
call writeln
goto exit
–– return to operating system


![Figure 15.7 Target code...](images/page_822_caption_Figure%2015.7%20Target%20code%20for%20the%20GCD%20program%2C%20generated%20from%20the%20syntax%20tree%20of%20Figure%2015.2%2C%20using%20th.png)
*Figure 15.7 Target code for the GCD program, generated from the syntax tree of Figure 15.2, using the attribute grammar of Figure 15.6.*

790
Chapter 15 Building a Runnable Program
techniques to improve it in Chapter 17. In the remaining sections of the current
chapter we will consider assembly and linking.
■
3CHECK YOUR UNDERSTANDING
1.
What is a code generator generator? Why might it be useful?
2.
What is a basic block? A control ﬂow graph?
3.
What are virtual registers? What purpose do they serve?
4.
What is the difference between local and global code improvement?
5.
What is register spilling?
6.
Explain what is meant by the “level” of an intermediate form (IF). What are
the comparative advantages and disadvantages of high-, medium-, and low-
level IFs?
7.
What is the IF most commonly used in Ada compilers?
8.
Name two advantages of a stack-based IF. Name one disadvantage.
9.
Explain the rationale for basing a family of compilers (several languages, sev-
eral target machines) on a single IF.
10. Why might a compiler employ more than one IF?
11. Outline some of the major design alternatives for back-end compiler organi-
zation and structure.
12. What is sometimes called the “middle end” of a compiler?
13. Why is management of a limited set of physical registers usually deferred until
late in the compilation process?
15.4
Address Space Organization
Assemblers, linkers, and loaders typically operate on a pair of related ﬁle formats:
relocatable object code and executable object code. Relocatable object code is ac-
ceptable as input to a linker; multiple ﬁles in this format can be combined to
create an executable program. Executable object code is acceptable as input to a
loader: it can be brought into memory and run. A relocatable object ﬁle includes
the following descriptive information:
Import table: Identiﬁes instructions that refer to named locations whose ad-
dresses are unknown, but are presumed to lie in other ﬁles yet to be linked
to this one.
15.4 Address Space Organization
791
Relocation table: Identiﬁes instructions that refer to locations within the current
ﬁle, but that must be modiﬁed at link time to reﬂect the offset of the current
ﬁle within the ﬁnal, executable program.
Export table: Lists the names and addresses of locations in the current ﬁle that
may be referred to in other ﬁles.
Imported and exported names are known as external symbols.
An executable object ﬁle is distinguished by the fact that it contains no refer-
ences to external symbols (at least if statically linked—more on this below). It
also deﬁnes a starting address for execution. An executable ﬁle may or may not
be relocatable, depending on whether it contains the tables above.
Details of object ﬁle structure vary from one operating system to another. Typ-
ically, however, an object ﬁle is divided into several sections, each of which is
handled differently by the linker, loader, or operating system. The ﬁrst section
includes the import, export, and relocation tables, together with an indication of
how much space will be required by the program for noninitialized static data.
Other sections commonly include code (instructions), read-only data (constants,
jump tables for case statements, etc.), initialized but writable static data, and
symbol table and layout information saved by the compiler. The initial descrip-
tive section is used by the linker and loader. The symbol table section is used
by debuggers and performance proﬁlers (Sections 16.3.2 and 16.3.3). Neither
of these tables is usually brought into memory at run time; neither is needed by
most running programs (an exception occurs in the case of programs that employ
reﬂection mechanisms [Section 16.3.1] to examine their own type structure).
In its runnable (loaded) form, a program is typically organized into several
segments. On some machines (e.g., the 80286 or PA-RISC), segments were visible
to the assembly language programmer, and could be named explicitly in instruc-
tions. More commonly on modern machines, segments are simply subsets of
the address space that the operating system manages in different ways. Some of
them—code, constants, and initialized data in particular—correspond to sections
of the object ﬁle. Code and constants are usually read-only, and are often com-
bined in a single segment; the operating system arranges to receive an interrupt
if the program attempts to modify them. (In response to such an interrupt it will
most likely print an error message and terminate the program.) Initialized data
are writable. At load time, the operating system either reads code, constants, and
initialized data from disk, or arranges to read them in at run time, in response to
“invalid access” (page fault) interrupts or dynamic linking requests.
In addition to code, constants, and initialized data, the typical running pro-
gram has several additional segments:
Uninitialized data: May be allocated at load time or on demand in response to
page faults. Usually zero-ﬁlled, both to provide repeatable symptoms for pro-
grams that erroneously read data they have not yet written, and to enhance
security on multiuser systems, by preventing a program from reading the con-
tents of pages written by previous users.
792
Chapter 15 Building a Runnable Program
Stack: May be allocated in some ﬁxed amount at load time. More commonly, is
given a small initial size, and is then extended automatically by the operating
system in response to (faulting) accesses beyond the current segment end.
Heap: Like stack, may be allocated in some ﬁxed amount at load time. More
commonly, is given a small initial size, and is then extended in response to
explicit requests (via system call) from heap-management library routines.
Files: In many systems, library routines allow a program to map a ﬁle into mem-
ory. The map routine interacts with the operating system to create a new seg-
ment for the ﬁle, and returns the address of the beginning of the segment. The
contents of the segment are usually fetched from disk on demand, in response
to page faults.
Dynamic libraries: Modern operating systems typically arrange for most pro-
grams to share a single copy of the code for popular libraries (Section C 15.7).
From the point of view of an individual process, each such library tends to oc-
cupy a pair of segments: one for the shared code, one for linkage information
and for a private copy of any writable data the library may need.
The layout of these segments for a contemporary 32-bit Linux system on the
EXAMPLE 15.9
Linux address space layout
x86 appears in Figure 15.8. Relative placements and addresses may be different
for other operating systems and machines.
■
15.5
Assembly
Some compilers translate source ﬁles directly into object ﬁles acceptable to the
linker. More commonly, they generate assembly language that must subsequently
be processed by an assembler to create an object ﬁle.
In our examples we have consistently employed a symbolic (textual) notation
for code. Within a compiler, the representation would not be textual, but it would
still be symbolic, most likely consisting of records and linked lists. To translate this
symbolic representation into executable code, we must
1. Replace opcodes and operands with their machine language encodings.
2. Replace uses of symbolic names with actual addresses.
These are the principal tasks of an assembler.
In the early days of computing, most programmers wrote in assembly lan-
guage. To simplify the more tedious and repetitive aspects of assembly program-
ming, assemblers often provided extensive macro expansion facilities. With the
ubiquity of modern high-level languages, such programmer-centric features have
largely disappeared. Almost all assembly language programs today are written by
compilers.
When passing assembly language directly from the compiler to the assembler, it
EXAMPLE 15.10
Assembly as a ﬁnal
compiler pass
makes sense to use some internal (records and linked lists) representation. At the
15.5 Assembly
793
Kernel address space
(inaccessible to
user programs)
0xc0000000
Stack
In early Unix systems with very limited memory,
the stack grew downward from the bottom of the
text segment; the number 0x08048000 is a legacy
of these systems. The sections marked “Shared li-
braries and memory-mapped ﬁles” typically com-
prise multiple segments with varying permissions
and addresses. (Modern Linux systems randomize
the choice of addresses to discourage malware.) The
top quarter of the address space belongs to the ker-
nel. Just over 1 MB of space is left unmapped at the
bottom of the address space to help catch program
bugs in which small integer values are accidentally
used as pointers.
Shared libraries and
memory-mapped files
Heap
Uninitialized data
Initialized data
Read-only code
(“text”) and constants
0x08048000
Shared libraries and
memory-mapped files
0x00110000


![Figure 15.8 Layout of...](images/page_826_caption_Figure%2015.8%20Layout%20of%2032-bit%20process%20address%20space%20in%20x86%20Linux%20%28not%20to%20scale%29.%20Double%20lines%20separat.png)
*Figure 15.8 Layout of 32-bit process address space in x86 Linux (not to scale). Double lines separate regions with potentially different access permissions.*

same time, we must provide a textual front end to accommodate the occasional
need for human input:
Source program
Assembler source
Assembler source
Compiler
Internal data structures
Assembler front end
Assembler back end
Object code
794
Chapter 15 Building a Runnable Program
The assembler front end simply translates textual source into internal symbolic
form. By sharing the assembler back end, the compiler and assembler front end
avoid duplication of effort. For debugging purposes, the compiler will generally
have an option to dump a textual representation of the code it passes to the as-
sembler.
■
An alternative organization has the compiler generate object code directly:
EXAMPLE 15.11
Direct generation of object
code
Source program
Assembler source
Compiler
Assembler
Disassembler
Object code
Assembler source
This organization gives the compiler a bit more ﬂexibility: operations nor-
mally performed by an assembler (e.g., assignment of addresses to variables) can
be performed earlier if desired. Because there is no separate assembly pass, the
overall translation to object code may be slightly faster. The stand-alone assem-
bler can be relatively simple. If it is used only for small, special-purpose code
fragments, it probably doesn’t need to perform instruction scheduling or other
machine-speciﬁc code improvement. Using a disassembler instead of an assem-
bly language dump from the compiler ensures that what the programmer sees
corresponds precisely to what is in the object ﬁle. If the compiler uses a fancier
assembler as a back end, then any program modiﬁcations effected by the assem-
bler will not be visible in the assembly language dumped by the compiler.
■
15.5.1 Emitting Instructions
The most basic task of the assembler is to translate symbolic representations of
instructions into binary form. In some assemblers this is an entirely straight-
forward task, because there is a one-to-one correspondence between mnemonic
operations and instruction op-codes. Many assemblers, however, make minor
changes to their input in order to improve performance or to extend the instruc-
tion set in ways that make the assembly language easier for human beings to read.
The GNU assembler, gas, is among the more conservative, but even it takes a few
liberties. For example, some compilers generate nop instructions to cache-align
EXAMPLE 15.12
Compressing nops
certain basic blocks (e.g., function prologues). To reduce the number of cycles
these consume, gas will combine multiple consecutive nops into multibyte in-
structions that have no effect. (On the x86, there are 2-, 4-, and 7-byte variants of
the lea instruction that can be used to move a register into itself.)
■
15.5 Assembly
795
For jumps to nearby addresses, gas uses an instruction variant that speciﬁes
EXAMPLE 15.13
Relative and absolute
branches
an offset from the pc. For jumps to distant addresses (or to addresses not known
until link time), it uses a longer variant that speciﬁes an absolute address. A few
x86 instructions (not typically generated by modern compilers) don’t have the
longer variant. For these, some assemblerswill reverse the sense of the conditional
test to hop over an unconditional jump. Gas simply fails to handle them.
■
At the more aggressive end of the spectrum, SGI’s assembler for the MIPS
EXAMPLE 15.14
Pseudoinstructions
instruction set provides a large number of pseudoinstructions that translate into
different real instructions depending on their arguments, or that correspond to
multi-instruction sequences. For example, there are two integer add instructions
on the MIPS: one of them adds two registers; the other adds a register and a con-
stant. The assembler provides a single pseudoinstruction, which it translates into
the appropriate variant. In a similar vein, the assembler provides a pseudoinstruc-
tion to load an arbitrary constant into a register. Since all instructions are 32 bits
long, this pseudoinstruction must be translated into a pair of real instructions
when the constant won’t ﬁt in 16 bits. Some pseudoinstructions may generate
even longer sequences. Integer division can take as many as 11 real instructions,
to check for errors and to move the quotient from a temporary location into the
desired register.
■
In effect, the SGI assembler implements a “cleaned-up” variant of the real ma-
chine. In addition to providing pseudoinstructions, it reorganizes instructions to
hide the existence of delayed branches (Section C 5.5.1) and to improve the ex-
pected performance of the processor pipeline. This reorganization constitutes a
ﬁnal pass of instruction scheduling (Sections C 5.5.1 and C 17.6). Though the job
could be handled by the compiler, the existence of pseudoinstructions like the in-
teger division example argues strongly for doing it in the assembler. In addition
to having two branch delays that might be ﬁlled by neighboring instructions, the
expanded division sequence can be used as a source of instructions to ﬁll nearby
branch, load, or functional unit delays.
In addition to translating from symbolic to binary instruction representations,
EXAMPLE 15.15
Assembler directives
most assemblers respond to a variety of directives. Gas provides more than 100 of
these. A few examples follow.
Segment switching: The .text directive indicates that subsequent instructions
and data should be placed in the code (text) segment. The .data directive
indicates that subsequent instructions and data should be placed in the initial-
ized data segment. (It is possible, though uncommon, to put instructions in
the data segment, or data in the code segment.) The .space n directive indi-
cates that n bytes of space should be reserved in the uninitialized data segment.
(This latter directive is usually preceded by a label.)
Data generation: The .byte, .hword, .word, .float, and .double directives
each take a sequence of arguments, which they place in successive locations
in the current segment of the output program. They differ in the types of
operands. The related.ascii directive takes a single character string as argu-
ment, which it places in consecutive bytes.
796
Chapter 15 Building a Runnable Program
Symbol identiﬁcation: The.globl name directive indicates that name should be
entered into the table of exported symbols.
Alignment: The.align n directive causes the subsequent output to be aligned at
an address evenly divisible by 2n.
■
15.5.2 Assigning Addresses to Names
Like compilers, assemblers commonly work in several phases. If the input is tex-
tual, an initial phase scans and parses the input, and builds an internal represen-
tation. In the most common organization there are two additional phases. The
ﬁrst identiﬁes all internal and external (imported) symbols, assigning locations to
the internal ones. This phase is complicated by the fact that the length of some in-
structions (on a CISC machine) or the number of real instructions produced by a
pseudoinstruction (on a RISC machine) may depend on the number of signiﬁcant
bits in an address. Given values for symbols, the ﬁnal phase produces object code.
Within the object ﬁle, any symbol mentioned in a .globl directive must ap-
pear in the table of exported symbols, with an entry that indicates the symbol’s
address. Any symbol referred to in a directive or an instruction, but not deﬁned
in the input program, must appear in the table of imported symbols, with an en-
try that identiﬁes all places in the code at which such references occur. Finally,
any instruction or datum whose value depends on the placement of the current
ﬁle within the address space of a running program must be listed in the relocation
table.
Historically, assemblers distinguished between absolute and relocatable words
EXAMPLE 15.16
Encoding of addresses in
object ﬁles
in an object ﬁle. Absolute words were known at assembly time; they did not need
to be changed by the linker. Examples include constants and register–register
instructions. A relocatable word, in contrast, needed to be modiﬁed by adding to
it the address within the ﬁnal program of the code or data segment of the object
ﬁle in which it appeared. A CISC jump instruction, for example, might consist
of a 1-byte jmp opcode followed by a 4-byte target address. For a local target,
the address bytes in the object ﬁle would contain the symbol’s offset within the
ﬁle. The linker would ﬁnalize the address by adding the address of the ﬁle’s code
segment in the ﬁnal version of the program.
On modern machines, this single form of relocation no longer sufﬁces. Ad-
dresses are encoded into instructions in many different ways, and these encodings
must be reﬂected in the relocation table and the import table. On a 32-bit ARM
processor, for example, an unconditional branch (b) instruction has a 24-bit off-
set ﬁeld. The processor left-shifts this ﬁeld by two bits, sign-extends it, and then
adds it to the address of the branch instruction itself to obtain the target address.1
1
The size of the offset implies that branches on ARM are limited to jumps of ≤32 MB in either
direction. If the linker discovers that a target is farther away than that, it must generate “veneer”
code that loads the target address into r12 (which is reserved for this purpose) and then performs
and indirect branch.
15.6 Linking
797
To relocate such an instruction, the linker must add the address of the target code
segment and the offset within it of the target instruction, subtract the address
of the current code segment and the offset within it of the branch instruction,
perform a two-bit right arithmetic shift, and truncate the result to 24 bits. In a
similar vein, a 32-bit load on ARM requires a two-instruction sequence analogous
to that of Example 15.14; if the loaded quantity is relocatable, the linker must re-
calculate the 16-bit operands of both instructions. Modern assemblers and object
ﬁle formats reﬂect this diversity of relocation modes.
■
15.6
Linking
Most language implementations—certainly all that are intended for the construc-
tion of large programs—support separate compilation: fragments of the program
can be compiled and assembled more or less independently. After compilation,
these fragments (known as compilation units) are “glued together” by a linker.
In many languages and environments, the programmer explicitly divides the pro-
gram into modules or ﬁles, each of which is separately compiled. More integrated
environments may abandon the notion of a ﬁle in favor of a database of subrou-
tines, each of which is separately compiled.
The task of a linker is to join together compilation units. A static linker does
its work prior to program execution, producing an executable object ﬁle. A dy-
namic linker (described in Section C 15.7) does its work after the (ﬁrst part of the)
program has been brought into memory for execution.
Each to-be-linked compilation unit must be a relocatable object ﬁle. Typically,
some ﬁles will have been produced by compiling fragments of the application
being constructed, while others will be preexisting library packages needed by
the application. Since most programs make use of libraries, even a “one-ﬁle”
application typically needs to be linked.
Linking involves two subtasks: relocation and the resolution of external ref-
erences. Some authors refer to relocation as loading, and call the entire “joining
together” process “link-loading.” Other authors (including the current one) use
“loading” to refer to the process of bringing an executable object ﬁle into memory
for execution. On very simple machines, or on machines with very simple oper-
ating systems, loading entails relocation. More commonly, the operating system
uses virtual memory to give every program the impression that it starts at some
standard address. In many systems loading also entails a certain amount of link-
ing (Section C 15.7).
798
Chapter 15 Building a Runnable Program
Relocatable object files
Executable object file
Code
 
…
A
B
Imports
 
M
 
M
Imports
 
X
 
r1 := &M (2300)
1800
800
500
300
 
call M (2300)
Exports
 
M
Exports
 
X
 
…
Relocation
Relocation
 
r1 := &L (1800)
900
2300
3000
 
r2 := Y (3900)
Code
 
…
Code
 
…
 
r3 := X (3300)
800
300
500
L:
 
r1 := &L (1000)
 
r1 := &M
1000
400
1500
1600
M:
 
r2 := Y (400)
 
call M
 
r3 := X
Data
L:
X:
M:
Data
Data
X:
Y:
Y:


![Figure 15.9 Linking relocatable...](images/page_831_caption_Figure%2015.9%20Linking%20relocatable%20object%20%EF%AC%81les%20A%20and%20B%20to%20make%20an%20executable%20object%20%EF%AC%81le.%20For%20simplicity.png)
*Figure 15.9 Linking relocatable object ﬁles A and B to make an executable object ﬁle. For simplicity of presentation, A’s code section has been placed at offset 0, with B’s code section immediately after, at offset 800 (addresses increase down the page). To allow the operating system to establish different protections for the code and data segments, A’s data section has been placed at the next page boundary (offset 3000), with B’s data section immediately after (offset 3500). External references to M and X have been set to use the appropriate addresses. Internal references to L and Y have been updated by adding in the starting addresses of B’s code and data sections, respectively.*

15.6.1 Relocation and Name Resolution
Each relocatable object ﬁle contains the information required for linking: the
import, export, and relocation tables. A static linker uses this information in a
two-phase process analogous to that described for assemblers in Section 15.5. In
the ﬁrst phase, the linker gathers all of the compilation units together, chooses an
order for them in memory, and notes the address at which each will consequently
lie. In the second phase, the linker processes each unit, replacing unresolved exter-
nal references with appropriate addresses, and modifying instructions that need
to be relocated to reﬂect the addresses of their units. These phases are illustrated
EXAMPLE 15.17
Static linking
pictorially in Figure 15.9. Addresses and offsets are assumed to be written in hex-
adecimal notation, with a page size of 4K (100016) bytes.
■
Libraries present a bit of a challenge. Many consist of hundreds of separately
compiled program fragments, most of which will not be needed by any particular
15.6 Linking
799
application. Rather than link the entire library into every application, the linker
needs to search the library to identify the fragments that are referenced from the
main program. If these refer to additional fragments, then those must be included
also, recursively. Many systems support a special library format for relocatable
object ﬁles. A library in this format may contain an arbitrary number of code and
data sections, together with an index that maps symbol names to the sections in
which they appear.
15.6.2 Type Checking
Within a compilation unit, the compiler enforces static semantic rules. Across the
boundaries between units, it uses module headers to enforce the rules pertaining
to external references. In effect, the header for module M makes a set of promises
regarding M’s interface to its users. When compiling the body of M, the compiler
ensures that those promises are kept. Imagine what could happen, however, if
we compiled the body of M, and then changed the numbers and types of param-
eters for some of the subroutines in its header ﬁle before compiling some user
module U. If both compilations succeed, then M and U will have very differ-
ent notions of how to interpret the parameters passed between them; while they
may still link together, chaos is likely to ensue at run time. To prevent this sort of
problem, we must ensure whenever M and U are linked together that both were
compiled using the same version of M’s header.
In most module-based languages, the following technique sufﬁces.
When
compiling the body of module M we create a dummy symbol whose name
uniquely characterizes the contents of M’s header. When compiling the body
of U we create a reference to the dummy symbol. An attempt to link M and U
together will succeed only if they agree on the name of the symbol.
One way to create the symbol name that characterizes M is to use a textual
EXAMPLE 15.18
Checksumming headers
for consistency
representation of the time of the most recent modiﬁcation of M’s header. Because
ﬁles may be moved across machines, however (e.g., to deliver source ﬁles to geo-
graphically distributed customers), modiﬁcation times are problematic: clocks
on different machines may be poorly synchronized, and ﬁle copy operations often
DESIGN & IMPLEMENTATION
15.2 Type checking for separate compilation
The encoding of type information in symbol names works well in C++, but is
too strict for use in C: it would outlaw programming tricks that, while ques-
tionable, are permitted by the language deﬁnition. Symbol-name encoding is
facilitated in C++ by the use of structural equivalence for types. In princi-
ple, one could use it in a language with name equivalence, but given that such
languages generally have well-structured modules, it is simpler just to use a
checksum of the header.
800
Chapter 15 Building a Runnable Program
change the modiﬁcation time. A better candidate is a checksum of the header ﬁle:
essentially the output of a hash function that uses the entire text of the ﬁle as key.
It is possible in theory for two different but valid ﬁles to have the same checksum,
but with a good choice of hash function the odds of this error are exceedingly
small.
■
The checksum strategy does require that we know when we’re using a mod-
ule header. Unfortunately, as described in Section C 3.8, we don’t know this in C
and C++: headers in these languages are simply a programming convention, sup-
ported by the textual inclusion mechanism of the language’s preprocessor. Most
implementations of C do not enforce consistency of interfaces at link time; in-
stead, programmers rely on conﬁguration management tools (e.g., Unix’s make)
to recompile ﬁles when necessary. Such tools are typically driven by ﬁle modiﬁ-
cation times.
Most implementations of C++ adopt a different approach, sometimes called
name mangling. The name of each imported or exported symbol in an object
ﬁle is created by concatenating the corresponding name from the program source
with a representation of its type. For an object, the type consists of the class name
and a terse encoding of its structure. For a function, it consists of an encoding
of the types of the arguments and the return value. For complicated objects or
functions of many arguments, the resulting names can be very long. If the linker
limits symbols to some too-small maximum length, the type information can be
compressed by hashing, at some small loss in security [SF88].
One problem with any technique based on ﬁle modiﬁcation times or check-
sums is that a trivial change to a header ﬁle (e.g., modiﬁcation of a comment,
or deﬁnition of a new constant not needed by existing users of the interface) can
prevent ﬁles from linking correctly. A similar problem occurs with conﬁguration
management tools: a trivial change may cause the tool to recompile ﬁles unnec-
essarily. A few programming environments address this issue by tracking changes
at a granularity smaller than the compilation unit [Tic86]. Most just live with the
need to recompile.
15.7
Dynamic Linking
On a multiuser system, it is common for several instances of a program (e.g.,
an editor or web browser) to be executing simultaneously. It would be highly
wasteful to allocate space in memory for a separate, identical copy of the code of
such a program for every running instance. Many operating systems therefore
keep track of the programs that are running, and set up memory mapping tables
so that all instances of the same program share the same read-only copy of the
program’s code segment. Each instance receives its own writable copy of the data
segment. Code segment sharing can save enormous amounts of space. It does not
work, however, for instances of programs that are similar but not identical.
Many sets of programs, while not identical, have large amounts of library code
in common—for example to manage a graphical user interface. If every appli-
15.7 Dynamic Linking
801
cation has its own copy of the library, then large amounts of memory may be
wasted. Moreover, if programs are statically linked, then much larger amounts
of disk space may be wasted on nearly identical copies of the library in separate
executable object ﬁles.
IN MORE DEPTH
In the early 1990s, most operating system vendors adopted dynamic linking in or-
der to save space in memory and on disk. We consider this option in more detail
on the companion site. Each dynamically linked library resides in its own code
and data segments. Every program instance that uses a given library has a pri-
vate copy of the library’s data segment, but shares a single system-wide read-only
copy of the library’s code segment. These segments may be linked to the remain-
der of the code when the program is loaded into memory, or they may be linked
incrementally on demand, during execution. In addition to saving space, dy-
namic linking allows a programmer or system administrator to install backward-
compatible updates to a library without rebuilding all existing executable object
ﬁles: the next time it runs, each program will obtain the new version of the library
automatically.
3CHECK YOUR UNDERSTANDING
14. What are the distinguishing characteristics of a relocatable object ﬁle? An ex-
ecutable object ﬁle?
15. Why do operating systems typically zero-ﬁll pages used for uninitialized data?
16. List four tasks commonly performed by an assembler.
17. Summarize the comparative advantages of assembly language and object code
as the output of a compiler.
18. Give three examples of pseudoinstructions and three examples of directives that
an assembler might be likely to provide.
19. Why might an assembler perform its own ﬁnal pass of instruction scheduling?
20. Explain the distinction between absolute and relocatable words in an object
ﬁle. Why is the notion of “relocatability” more complicated than it used to
be?
21. What is the difference between linking and loading?
22. What are the principal tasks of a linker?
23. How can a linker enforce type checking across compilation units?
24. What is the motivation for dynamic linking?
802
Chapter 15 Building a Runnable Program
15.8
Summary and Concluding Remarks
In this chapter we focused our attention on the back end of the compiler, and on
code generation, assembly, and linking in particular.
Compiler middle and back ends vary greatly in internal structure. We dis-
cussed one plausible structure, in which semantic analysis is followed by, in order,
intermediate code generation, machine-independent code improvement, target
code generation, and machine-speciﬁc code improvement (including register al-
location and instruction scheduling). The semantic analyzer passes a syntax tree
to the intermediate code generator, which in turn passes a control ﬂow graph to the
machine-independent code improver. Within the nodes of the control ﬂow graph,
we suggested that code be represented by instructions in a pseudo-assembly lan-
guage with an unlimited number of virtual registers. In order to delay discussion
of code improvement to Chapter 17, we also presented a simpler back-end struc-
ture in which code improvement is dropped, naive register allocation happens
early, and intermediate and target code generation are merged into a single phase.
This simpler structure provided the context for our discussion of code generation.
We also discussed intermediate forms (IFs). These can be categorized in terms
of their level, or degree of machine independence. On the companion site we con-
sidered GIMPLE and RTL, the IFs of the Free Software Foundation GNU com-
pilers. A well-deﬁned IF facilitates the construction of compiler families, in which
front ends for one or more languages can be paired with back ends for many ma-
chines. In many systems that compile for a virtual machine (to be discussed at
greater length in Chapter 16), the compiler produces a stack-based medium-level
IF. While not generally suitable for use inside the compiler, such an IF can be
simple and very compact.
Intermediate code generation is typically performed via ad hoc traversal of a
syntax tree. Like semantic analysis, the process can be formalized in terms of
attribute grammars. We presented part of a small example grammar and used
it to generate code for the GCD program introduced in Chapter 1. We noted
in passing that target code generation is often automated, in whole or in part,
using a code generator generator that takes as input a formal description of the
target machine and produces code that performs pattern matching on instruction
sequences or trees.
In our discussion of assembly and linking we described the format of relo-
catable and executable object ﬁles, and discussed the notions of name resolution
and relocation. We noted that while not all compilers include an explicit assem-
bly phase, all compilation systems must make it possible to generate assembly
code for debugging purposes, and must allow the programmer to write special-
purpose routines in assembler. In compilers that use an assembler, the assembly
phase is sometimes responsible for instruction scheduling and other low-level
code improvement. The linker, for its part, supports separate compilation, by
“gluing” together object ﬁles produced by multiple compilations. In many mod-
ern systems, signiﬁcant portions of the linking task are delayed until load time
15.9 Exercises
803
or even run time, to allow programs to share the code segments of large, popu-
lar libraries. For many languages the linker must perform a certain amount of
semantic checking, to guarantee type consistency. In more aggressive optimiz-
ing compilation systems (not discussed in this text), the linker may also perform
interprocedural code improvement.
As noted in Section 1.5, the typical programming environment includes a host
of additional tools, including debuggers, performance proﬁlers, conﬁguration
and version managers, style checkers, preprocessors, pretty-printers, testing sys-
tems, and perusal and cross-referencing utilities. Many of these tools, particularly
in well-integrated environments, are directly supported by the compiler. Many
make use, for example, of symbol-table information embedded in object ﬁles.
Performance proﬁlers and testing systems often rely on special instrumentation
code inserted by the compiler at subroutine calls, loop boundaries, and other key
points in the code. Perusal, style-checking, and pretty-printing programs may
share the compiler’s scanner and parser. Conﬁguration tools often rely on lists of
interﬁle dependences, again generated by the compiler, to tell when a change to
one part of a large system may require that other parts be recompiled.
15.9
Exercises
15.1
If you were writing a two-pass compiler, why might you choose a high-
level IF as the link between the front end and the back end? Why might
you choose a medium-level IF?
15.2
Consider a language like Ada or Modula-2, in which a module M can be
divided into a speciﬁcation (header) ﬁle and an implementation (body)
ﬁle for the purpose of separate compilation (Section 10.2.1). Should M’s
speciﬁcation itself be separately compiled, or should the compiler simply
read it in the process of compiling M’s body and the bodies of other mod-
ules that use abstractions deﬁned in M? If the speciﬁcation is compiled,
what should the output consist of?
15.3
Many research compilers (e.g., for SR [AO93], Cedar [SZBH86], Lynx
[Sco91], and Modula-3 [Har92]) have used C as their IF. C is well doc-
umented and mostly machine independent, and C compilers are much
more widely available than alternative back ends. What are the disadvan-
tages of generating C, and how might they be overcome?
15.4
List as many ways as you can think of in which the back end of a just-
in-time compiler might differ from that of a more conventional compiler.
What design goals dictate the differences?
15.5
Suppose that k (the number of temporary registers) in Figure 15.6 is 4 (this
is an artiﬁcially small number for modern machines). Give an example of
an expression that will lead to register spilling under our naive register
allocation algorithm.
804
Chapter 15 Building a Runnable Program
program
:=
:=
(7)
call
for
(8)
0.0
null
(4)
(10)
1
(7)
:=
call
null
:=
null
call
(6)
(9)
÷
Index
Symbol
Type
Scope
+
(8)
void
int
real
getint
getreal
putreal
n
sum
x
i
0
0
0
0
0
0
1
1
1
2
type
type
type
func: (1) → (2)
func: (1) → (3)
func: (3) → (1)
2
3
3
2
1
2
3
4
5
6
7
8
9
10
null
(5)
(8)
float
(8)
(9)
(7)


![Figure 15.10 Syntax tree...](images/page_837_caption_Figure%2015.10%20Syntax%20tree%20and%20symbol%20table%20for%20a%20program%20that%20computes%20the%20average%20of%20N%20real%20numbers..png)
*Figure 15.10 Syntax tree and symbol table for a program that computes the average of N real numbers. The children of the for node are the index variable, the lower bound, the upper bound, and the body.*

15.6
Modify the attribute grammar of Figure 15.6 in such a way that it will gen-
erate the control ﬂow graph of Figure 15.3 instead of the linear assembly
code of Figure 15.7.
15.7
Add productions and attribute rules to the grammar of Figure 15.6 to han-
dle Ada-style for loops (described in Section 6.5.1). Using your modi-
ﬁed grammar, hand-translate the syntax tree of Figure 15.10 into pseudo-
assembly notation. Keep the index variable and the upper loop bound in
registers.
15.8
One problem (of many) with the code we generated in Section 15.3 is that
it computes at run time the value of expressions that could have been com-
puted at compile time. Modify the grammar of Figure 15.6 to perform a
simple form of constant folding: whenever both operands of an operator
are compile-time constants, we should compute the value at compile time
and then generate code that uses the value directly. Be sure to consider
how to handle overﬂow.
15.9
Modify the grammar of Figure 15.6 to generate jump code for Boolean
expressions, as described in Section 6.4.1. You should assume short-circuit
evaluation (Section 6.1.5).
15.10 Explorations
805
15.10
Our GCD program did not employ subroutines. Extend the grammar of
Figure 15.6 to handle procedures without parameters (feel free to adopt
any reasonable conventions on the structure of the syntax tree). Be sure to
generate appropriate prologue and epilogue code for each subroutine, and
to save and restore any needed temporary registers.
15.11
The grammar of Figure 15.6 assumes that all variables are global. In the
presence of subroutines, we should need to generate different code (with
fp-relative displacement mode addressing) to access local variables and
parameters. In a language with nested scopes we should need to derefer-
ence the static chain (or index into the display) to access objects that are
neither local nor global. Suppose that we are compiling a language with
nested subroutines, and are using a static chain. Modify the grammar of
Figure 15.6 to generate code to access objects correctly, regardless of scope.
You may ﬁnd it useful to deﬁne a to register subroutine that generates the
code to load a given object. Be sure to consider both l-values and r-values,
and parameters passed by both value and result.
15.12–15.15 In More Depth.
15.10
Explorations
15.16
Investigate and describe the IF of the compiler you use most often. Can
you instruct the compiler to dump it to a ﬁle which you can then inspect?
Are there tools other than the compiler phases that operate on the IF (e.g.,
debuggers, code improvers, conﬁguration managers, etc.)? Is the same IF
used by compilers for other languages or machines?
15.17
Implement Figure 15.6 in your favorite programming language. Deﬁne
appropriate data structures to represent a syntax tree; then generate code
for some sample trees via ad hoc tree traversal.
15.18
Augment your solution to the previous exercise to handle various other
language features. Several interesting options have been mentioned in ear-
lier exercises. Others include functions, ﬁrst-class subroutines, case state-
ments, records, arrays (particularly those of dynamic size), and iterators.
15.19
Find out what tools are available on your favorite system to inspect the
content of object ﬁles (on a Unix system, use nm or objdump). Consider
some program consisting of a modest number (three to six, say) of com-
pilation units. Using the appropriate tool, list the imported and exported
symbols in each compilation unit. Then link the ﬁles together. Draw an
address map showing the locations at which the various code and data
segments have been placed. Which instructions within the code segments
have been changed by relocation?
15.20
In your favorite C++ compiler, investigate the encoding of type informa-
tion in the names of external symbols. Are there strange strings of char-
806
Chapter 15 Building a Runnable Program
acters at the end of every name? If so, can you “reverse engineer” the
algorithm used to generate them? For hints, type “C++ name mangling”
into your favorite search engine.
15.21–15.25 In More Depth.
15.11
Bibliographic Notes
Standard compiler textbooks (e.g., those by Aho et al. [ALSU07], Cooper and Tor-
czon [CT04], Grune et al. [GBJ+12], Appel [App97], or Fischer et al. [FCL10])
are an accessible source of information on back-end compiler technology. More
detailed information can be found in the text of Muchnick [Muc97]. Fraser and
Hanson provide a wealth of detail on code generation and (simple) code improve-
ment in their lcc compiler [FH95].
RTL and GIMPLE are documented in the gcc Internals Manual, available from
www.gnu.org/onlinedocs. Java bytecode is documented by Lindholm and Yellin
[LYBB14]. The Common Intermediate Language is described by Miller and Rags-
dale [MR04].
Ganapathi, Fischer, and Hennessy [GFH82] and Henry and Damron [HD89]
provide early surveys of automatic code generator generators. The most widely
used technique from that era was based on LR parsing, and was due to Glanville
and Graham [GG78]. Fraser et al. [FHP92] describe a simpler approach based on
dynamic programming. Documentation for the LLVM Target-Independent Code
Generator can be found at llvm.org/docs/CodeGenerator.html.
Beck [Bec97] provides a good turn-of-the-century introduction to assemblers,
linkers, and software development tools. Gingell et al. describe the implemen-
tation of shared libraries for the SPARC architecture and the SunOS variant of
Unix [GLDW87].
Ho and Olsson describe a particularly ambitious dynamic
linker for Unix [HO91]. Tichy presents a compilation system that avoids un-
necessary recompilations by tracking dependences at a granularity ﬁner than the
source ﬁle [Tic86].
