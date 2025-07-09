# Chapter 17: Code Improvement

## 17 Code Improvement

In Chapter 15 we discussed the generation, assembly, and linking of target code in the back end of a compiler. The techniques we presented led to correct but highly suboptimal code: there were many redundant computations, and in- efﬁcient use of the registers, multiple functional units, and cache of a modern microprocessor. This chapter takes a look at code improvement: the phases of compilation devoted to generating good (fast) code. As noted in Section 1.6.4, code improvement is often referred to as optimization, though it seldom makes anything optimal in any absolute sense. Our study will consider simple peephole optimization, which “cleans up” gen- erated target code within a very small instruction window; local optimization, which generates near-optimal code for individual basic blocks; and global opti- mization, which performs more aggressive code improvement at the levelof entire subroutines. We will not cover interprocedural improvement; interested readers are referred to other texts (see the Bibliographic Notes at the end of the chapter). Moreover, even for the subjects we cover, our intent will be more to “demystify” code improvement than to describe the process in detail. Much of the discussion will revolve around the successive reﬁnement of code for a single subroutine. This extended example will allow us to illustrate the effect of several key forms of code improvement without dwelling on the details of how they are achieved.

IN MORE DEPTH

Chapter 17 can be found in its entirety on the companion site.

