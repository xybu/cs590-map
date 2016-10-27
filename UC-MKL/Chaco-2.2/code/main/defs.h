#define max(A, B) ((A) > (B) ? (A) : (B))
#define min(A, B) ((A) < (B) ? (A) : (B))
#define sign(A) ((A) < 0 ? -1 : 1)
#define absval(A) ((A) < 0 ? -(A) : (A))
#define TRUE 1
#define FALSE 0

/* Define constants that are needed in various places */
#define PI 3.141592653589793
#define TWOPI 6.283185307179586
#define HALFPI 1.570796326794896

#define declare_print_array_func(func_name, array_type) \
  extern void func_name(const char*, array_type, int)

#define define_print_array_func(func_name, array_type, print_fmt_str)         \
  void func_name(const char *varname, array_type array, int size) {           \
    int i;                                                                    \
    const int NUMS_PER_LINE = 8;                                              \
    fprintf(stdout, "%s: {\n", varname);                                      \
    for (i = 0; i < size; ++i) {                                              \
      if (i % NUMS_PER_LINE == 0) fputc(' ', stdout);                         \
      fprintf(stdout, "%2d: " print_fmt_str "%s", i, array[i],                \
              (i < size - 1) ? ", " : "");                                    \
      if ((i + 1) % NUMS_PER_LINE == 0 && i != size - 1) fputc('\n', stdout); \
    }                                                                         \
    fprintf(stdout, "\n}\n\n");                                               \
  }

#define declare_save_array_func(func_name, array_type) \
  extern void func_name(array_type, int)

#define define_save_array_func(func_name, array_type, file_name) \
  void func_name(array_type array, int size) {                   \
    int i;                                                       \
    static int nth_save = 0;                                     \
                                                                 \
    FILE *f;                                                     \
    if (nth_save == 0) {                                         \
      f = fopen(file_name, "w");                                 \
    } else {                                                     \
      f = fopen(file_name, "a");                                 \
    }                                                            \
                                                                 \
    fprintf(f, "%d", nth_save);                                  \
    for (i = 0; i < size; ++i) fprintf(f, ", %d", array[i]);     \
    fputc('\n', f);                                              \
                                                                 \
    fclose(f);                                                   \
    nth_save++;                                                  \
  }
