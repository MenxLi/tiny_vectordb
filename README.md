
A tiny vector database for small projects (vectors are able to be stored in memory)

- It use jit compiling to speed up the vector operation by setting the vector size at compile time 
and speedup the vector operation by using [Eigen](https://eigen.tuxfamily.org/index.php?title=Main_Page).
- Process with only python list, without requiring any other third-party data format.
- The actual storage is base-64 encoded string, in a sqlite database.

**About 10x Faster than numpy-based vector operation.**

**Under development...**
( Only on Linux and Mac OS with `g++`/`clang++` for now, need to write compile script for Windows on your own, refer to `tiny_vectordb.jit` )