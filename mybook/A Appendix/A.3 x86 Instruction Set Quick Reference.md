# A.3 x86 Instruction Set Quick Reference

tests A list of test numbers that specifies which tests to run (explained next).

The interp-tests function assumes that the subdirectory tests has a collection of Racket programs whose names all start with the family name, followed by an underscore and then the test number, and ending with the file extension .rkt. Also, for each test program that calls read one or more times, there is a file with the same name except that the file extension is .in, which provides the input for the Racket program. If the test program is expected to fail type checking, then there should be an empty file of the same name with extension .tyerr.

compiler-tests This function runs the compiler passes to generate x86 (a .s file) and then runs the GNU C compiler (gcc) to generate machine code. It runs the machine code and checks that the output is 42. The parameters to the compiler-tests function are similar to those of the interp-tests function, and they consist of

![Table A.1...](images/page_226_vector_617.png)
*Table A.1*

