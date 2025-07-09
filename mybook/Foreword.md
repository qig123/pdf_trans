# Foreword

Foreword

Programming languages are universally accepted as one of the core subjects that every computer scientist must master. The reason is clear: these languages are the main notation we use for developing products and for communicating new ideas. They have inﬂuenced the ﬁeld by enabling the development of those multimillion-line programs that shaped the information age. Their success is owed to the long-standing effort of the computer science community in the cre- ation of new languages and in the development of strategies for their implemen- tation. The large number of computer scientists mentioned in the footnotes and bibliographic notes in this book by Michael Scott is a clear manifestation of the magnitude of this effort as is the sheer number and diversity of topics it contains.

Over 75 programming languages are discussed. They represent the best and most inﬂuential contributions in language design across time, paradigms, and ap- plication domains. They are the outcome of decades of work that led initially to Fortran and Lisp in the 1950s, to numerous languages in the years that followed, and, in our times, to the popular dynamic languages used to program the Web. The 75 plus languages span numerous paradigms including imperative, func- tional, logic, static, dynamic, sequential, shared-memory parallel, distributed- memory parallel, dataﬂow, high-level, and intermediate languages. They include languages for scientiﬁc computing, for symbolic manipulations, and for accessing databases. This rich diversity of languages is crucial for programmer productivity and is one of the great assets of the discipline of computing.

Cutting across languages, this book presents a detailed discussion of control ﬂow, types, and abstraction mechanisms. These are the representations needed to develop programs that are well organized, modular, easy to understand, and easy to maintain. Knowledge of these core features and of their incarnation in to- day’s languages is a basic foundation to be an effective programmer and to better understand computer science today.

Strategies to implement programming languages must be studied together with the design paradigms. A reason is that success of a language depends on the quality of its implementation. Also, the capabilities of these strategies some- times constraint the design of languages. The implementation of a language starts with parsing and lexical scanning needed to compute the syntactic structure of programs. Today’s parsing techniques, described in Part I, are among the most beautiful algorithms ever developed and are a great example of the use of mathe- matical objects to create practical instruments. They are worthwhile studying just

xxiii

xxiv Foreword

as an intellectual achievement. They are of course of great practical value, and a good way to appreciate the greatness of these strategies is to go back to the ﬁrst Fortran compiler and study the ad hoc, albeit highly ingenious, strategy used to implement precedence of operators by the pioneers that built that compiler.

The other usual component of implementation are the compiler components that carry out the translation from the high-level language representation to a lower level form suitable for execution by real or virtual machines. The transla- tion can be done ahead of time, during execution (just in time), or both. The book discusses these approaches and implementation strategies including the elegant mechanisms of translation driven by parsing. To produce highly efﬁ- cient code, translation routines apply strategies to avoid redundant computations, make efﬁcient use of the memory hierarchy, and take advantage of intra-processor parallelism. These, sometimes conﬂicting goals, are undertaken by the optimiza- tion components of compilers. Although this topic is typically outside the scope of a ﬁrst course on compilers, the book gives the reader access to a good overview of program optimization in Part IV.

An important recent developmentin computing is the popularization of paral- lelism and the expectation that, in the foreseeable future, performance gains will mainly be the result of effectively exploiting this parallelism. The book responds to this development by presenting the reader with a range of topics in concurrent programming including mechanisms for synchronization, communication, and coordination across threads. This information will become increasingly impor- tant as parallelism consolidates as the norm in computing.

Programming languages are the bridge between programmers and machines. It is in them that algorithms must be represented for execution. The study of pro- gramming languages design and implementation offers great educational value by requiring an understanding of the strategies used to connect the different as- pects of computing. By presenting such an extensive treatment of the subject, Michael Scott’s Programming Language Pragmatics, is a great contribution to the literature and a valuable source of information for computer scientists.

David Padua Siebel Center for Computer Science University of Illinois at Urbana-Champaign

