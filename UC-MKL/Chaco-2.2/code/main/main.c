/* This software was developed by Bruce Hendrickson and Robert Leland   *
 * at Sandia National Laboratories under US Department of Energy        *
 * contract DE-AC04-76DP00789 and is copyrighted by Sandia Corporation. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "params.h"

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

define_print_array_func(print_int_array, int *, "%2d");
define_print_array_func(print_short_array, short *, "%2d");

define_save_array_func(save_assignment_array, short *, "assignment_hist.txt");
define_save_array_func(save_switch_capacity_array, int *,
                       "switch_capacity_hist.txt");
define_save_array_func(save_host_usage_array, int *, "host_usage_hist.txt");
define_save_array_func(save_usage_array, int *, "usage_hist.txt");

// A PM is considered under-utilized if its CPU usage is below this limit.
const int UNDER_UTILIZATION_THRESHOLD = 90;

// A PM is considered over-utilized if its CPU usage is above this limit.
const int OVER_UTILIZATION_THRESHOLD = 110;

// Allow the last host to be under-utilized.
const int MAX_UNDER_UTILIZED_HOST_COUNT = 1;

// Range of CPU Usage.
const int MIN_CPU_PERCENT = 0;
const int MAX_CPU_PERCENT = 100;

// Max number of rounds allowed.
const int MAX_ITERATIONS = 1000;

int main() {
  extern int Using_Main;            /* is main routine being called? */
  extern char *Graph_File_Name;     /* name of graph input file */
  extern char *Geometry_File_Name;  /* name of coordinate input file */
  extern char *Assign_In_File_Name; /* name of assignment input input file */
  extern char *PARAMS_FILENAME;     /* name of file with parameter updates */
  extern double EIGEN_TOLERANCE;    /* tolerance for eigen calculations */
  extern int OUTPUT_ASSIGN;         /* whether to write assignment to file */
  extern int DEBUG_MEMORY;          /* debug memory allocation and freeing? */
  extern int DEBUG_TRACE;           /* trace main execution path */
  extern int DEBUG_PARAMS;          /* debug flag for reading parameters */
  extern long RANDOM_SEED;          /* seed for random number generators */
  extern int ECHO;                  /* controls amount of output */
  extern int PROMPT;                /* prompt for input or not? */
  extern int PRINT_HEADERS;         /* print lines for output sections? */
  extern int MATCH_TYPE;            /* matching routine to call */
  extern double input_time;         /* times data file input */
  extern double start_time;         /* time partitioning starts */
  FILE *fin;                        /* input file */
  FILE *fin_host;  /* input host percentage  --------------------------- ADD! */
  FILE *fingeom;   /* geometry input file (for inertial method) */
  FILE *finassign; /* assignment file if reading in */
  FILE *params_file; /* file with parameter value updates */
  double *goal;      /* desired set sizes */
  float *x, *y, *z;  /* coordinates for inertial method */
  int *start;        /* start of edge list for each vertex */
  int *adjacency;    /* edge list data */
  float *ewgts;      /* weights for all edges */
  int *vwgts;        /* weights for all vertices */
  int global_method; /* global partitioning method */
  int local_method;  /* local partitioning method */
  short *assignment; /* set number of each vtx (length nvtxs+1 ----------- NOT
                        REAL! actual length = nvtxs!) */
  int *host_percent; /* host percentage of each vtx (length nvtxs)
                        ------------------------------ADD! */
  double eigtol;     /* tolerance in eigenvector calculation */
  int nvtxs;         /* number of vertices in graph */
  int ndims;         /* dimension of recursive partitioning at each level */
  int architecture;  /* 0 => hypercube, d => d-dimensional mesh */
  int ndims_tot;     /* total number of cube dimensions to divide */
  int *set_capa = NULL;     /* capacity of each PM ----------------ADD! */
  int set_capa_func[20][3]; /* capacity function of each PM (up to 20
                               PMs)-------------ADD! */
  int usage[20]; /* capacity usage for switches (0~100)--------------ADD! */
  int host_usage[20]; /* capacity usage for hosts (0~100)--------------ADD! */
  int mesh_dims[3];   /* dimensions of mesh of processors */
  long seed;          /* for random graph mutations */
  int rqi_flag;       /* use RQI/Symmlq eigensolver? */
  int vmax;           /* if so, how many vertices to coarsen down to? */
  int igeom;          /* geometry dimension if inertial method */
  char graphname[NAME_LENGTH];     /* name of graph input file */
  char hostname[NAME_LENGTH];      /* name of host input file -----------ADD! */
  char geomname[NAME_LENGTH];      /* name of geometry input file */
  char inassignname[NAME_LENGTH];  /* assignment input file name */
  char outassignname[NAME_LENGTH]; /* assignment output file name */
  char outfilename[NAME_LENGTH];   /* name of output file */
  char *outassignptr; /* name or null pointer for output assignment */
  char *outfileptr;   /* name or null pointer for output file */
  int another;        /* run another problem? */
  double time;        /* timing marker */
  int flag;           /* return code from input routines */
  double *smalloc();  /* safe version of malloc */
  double seconds();   /* returns elapsed time in seconds */
  int sfree(), interface(), affirm();
  int input_graph(), input_assign(), input_geom();
  void input_queries(), smalloc_stats(), read_params(), clear_timing();

  int i, j, n;
  short *assignment_history[MAX_ITERATIONS];
  memset(assignment_history, 0, MAX_ITERATIONS * sizeof(short *));

  if (DEBUG_TRACE > 0) {
    printf("<Entering main>\n");
  }

  if (PRINT_HEADERS) {
    printf("\n                    Chaco 2.0\n");
    printf("          Sandia National Laboratories\n\n");
  }

  Using_Main = TRUE;
  another = TRUE;
  params_file = fopen(PARAMS_FILENAME, "r");
  if (params_file == NULL && DEBUG_PARAMS > 1) {
    printf("Parameter file `%s' not found; using default parameters.\n",
           PARAMS_FILENAME);
  }

  while (another) {
    start_time = time = seconds();

    x = y = z = NULL;
    goal = NULL;
    assignment = NULL;
    /*  ADD  */
    for (i = 0; i < 20; i++) {
      usage[i] = 90;
      host_usage[i] = 0;
      // printf("-------- %d, %d\n", i,u[i]);
    }

    print_int_array("usage", usage, 20);
    print_int_array("host_usage", host_usage, 20);

    read_params(params_file);

    input_queries(&fin, &fin_host, &fingeom, &finassign, graphname, hostname,
                  geomname, inassignname, outassignname, outfilename,
                  &architecture, &ndims_tot, &set_capa, set_capa_func, usage,
                  mesh_dims, &global_method, &local_method, &rqi_flag, &vmax,
                  &ndims);  // ADD!

    if (global_method == 7)
      Assign_In_File_Name = inassignname;
    else
      Assign_In_File_Name = NULL;

    if (OUTPUT_ASSIGN > 0)
      outassignptr = outassignname;
    else
      outassignptr = NULL;

    if (ECHO < 0)
      outfileptr = outfilename;
    else
      outfileptr = NULL;

    flag = input_graph(fin, graphname, &start, &adjacency, &nvtxs, &vwgts,
                       &ewgts);  // ADD!
    if (flag) {
      sfree((char *)ewgts);
      sfree((char *)vwgts);
      sfree((char *)adjacency);
      sfree((char *)start);
      goto skip;
    }

    Graph_File_Name = graphname;

    assignment = (short *)malloc((unsigned)nvtxs * sizeof(short));
    host_percent = (int *)smalloc((unsigned)nvtxs * sizeof(int));  // ADD!
    /****** read the host file here! *******/
    // printf("length!!!!!! %d", nvtxs);
    
    for (j = 0; j < nvtxs; j++) {
      fscanf(fin_host, "%d", &host_percent[j]);
      // printf("----%d: %d-----",j, host_percent[j]); //////
    }
    print_int_array("host_percent (fscanf)", host_percent, nvtxs);
    /***************************************/

    if (global_method == 7) {
      flag = input_assign(finassign, inassignname, nvtxs, assignment);
      if (flag) goto skip;
      Assign_In_File_Name = inassignname;
    }

    print_short_array("assignment (input_assign)", assignment, nvtxs);

    if (global_method == 3 ||
        (MATCH_TYPE == 5 &&
         (global_method == 1 || (global_method == 2 && rqi_flag)))) {
      /* Read in geometry data. */
      flag = input_geom(fingeom, geomname, nvtxs, &igeom, &x, &y, &z);
      if (flag) goto skip;
      Geometry_File_Name = geomname;
    } else {
      x = y = z = NULL;
    }

    input_time += seconds() - time;

    eigtol = EIGEN_TOLERANCE;
    seed = RANDOM_SEED;

    /********************************************ADD***************************************************/
    int nprocs = 1 << ndims_tot; /* number of processors being divided into */
    printf("# of PMs: %d\n", nprocs);  ////////////

    int n;
    for (n = 0; n < MAX_ITERATIONS; n++) {

      flag = input_graph(fin, graphname, &start, &adjacency, &nvtxs, &vwgts,
                         &ewgts);  // ADD!
      if (flag) {
        sfree((char *)ewgts);
        sfree((char *)vwgts);
        sfree((char *)adjacency);
        sfree((char *)start);
        goto skip;
      }

      // compute current switch capacity
      int cur = 0;
      for (cur = 0; cur < nprocs; cur++) {
        double capa_0 = set_capa_func[cur][2];
        double capa_1 = set_capa_func[cur][1] * usage[cur];
        double capa_2 = set_capa_func[cur][0] * usage[cur] * usage[cur];
        set_capa[cur] = (int)((capa_2 + capa_1 + capa_0) / 10000);
      }
      print_int_array("set_capa (switch capacity)", set_capa, nprocs);
      save_switch_capacity_array(set_capa, nprocs);

      // for (cur = 0; cur < nprocs; cur++) {
      //   printf("~~~~~time %d: current switch capacity~~~~~~~  %d\n", n,
      //          set_capa[cur]);
      // }

      // one partitioning
      interface(nvtxs, start, adjacency, vwgts, ewgts, x, y, z, outassignptr,
                outfileptr, assignment, architecture, ndims_tot, mesh_dims,
                set_capa, goal, global_method, local_method, rqi_flag, vmax,
                ndims, eigtol, seed);
      printf("~~~~~~~~~~~~~~partitioning finished~~~~~~~~~~~~~~~~~~\n");

      print_int_array("host_percent (after partition)", host_percent, nvtxs);

      print_short_array("assignment (after partition)", assignment, nvtxs);
      save_assignment_array(assignment, nvtxs);

      /*
      for (j = 0; j < nvtxs; j++) {
              //fscanf(fin_host,"%d", &host_percent[j] );
              printf("--%d: %d-----\n",j, assignment[j]);
      }*/

      // recompute u values according to the assignment results
      memset(host_usage, 0, sizeof(host_usage));
      // for (i = 0; i < 20; i++) {
      //   host_usage[i] = 0;
      // }

      for (j = 0; j < nvtxs; j++) {
        int cur_set = assignment[j];
        host_usage[cur_set] += host_percent[j];
      }

      print_int_array("host_usage (updated)", host_usage, 20);
      save_host_usage_array(host_usage, 20);

      int num_under_utilized_host = 0;
      int num_over_utilized_host = 0;

      for (cur = 0; cur < nprocs; cur++) {
        // printf(
        //     "\tcurrent host percentage after partitioning %d: %d\t old switch
        //     "
        //     "usage percentage: %d\n",
        //     cur, host_usage[cur], usage[cur]);

        // compute if all u's have: 95<= u <= 105. if does, stop the loops
        int total_usage = host_usage[cur] + usage[cur];
        if (total_usage < UNDER_UTILIZATION_THRESHOLD) {
          num_under_utilized_host++;
          printf("PM %d is under-utilized. Its CPU usage is %d+%d=%d.\n", cur,
                 host_usage[cur], usage[cur], total_usage);
        } else if (total_usage > OVER_UTILIZATION_THRESHOLD) {
          num_over_utilized_host++;
          printf("PM %d is over-utilized. Its CPU usage is %d+%d=%d.\n", cur,
                 host_usage[cur], usage[cur], total_usage);
        }

        usage[cur] = MAX_CPU_PERCENT - host_usage[cur];
        if (usage[cur] < MIN_CPU_PERCENT) {
          usage[cur] = MIN_CPU_PERCENT;
        }

        // usage[cur] = (usage[cur] + (100 - host_usage[cur])) / 2;
        // if (usage[cur] < 50) {
        //   usage[cur] = 50;
        // } else if (usage[cur] > 90) {
        //   usage[cur] = 90;
        // }
      }

      print_int_array("usage (updated)", usage, nprocs);
      save_usage_array(usage, nprocs);

      if (num_over_utilized_host == 0 &&
          num_under_utilized_host <= MAX_UNDER_UTILIZED_HOST_COUNT) {
        printf("********End earlier because of good total usage!********\n");
        goto skip;
      }

      assignment_history[n] = assignment;

      // Check if the assignment appeared before.
      for (cur = 0; cur < n; ++cur) {
        if (!memcmp(assignment_history[cur], assignment, nvtxs * sizeof(short))) {
          // When finding an assignment that is already attempted, terminate for now.
          // There should be better policy though.
          printf("Iteration %d gives same assignment as %d. Stop.\n", n, cur);
          goto skip;
        }
      }

      assignment = (short *)malloc((unsigned)nvtxs * sizeof(short));
    }
  /***************************/

  skip:
    if (global_method == 3) {
      if (z != NULL) sfree((char *)z);
      if (y != NULL) sfree((char *)y);
      if (x != NULL) sfree((char *)x);
    }
    
    for (i = 0; i < n; ++i)
      free(assignment_history[i]);

    sfree((char *)host_percent);

    if (DEBUG_MEMORY > 0) {
      printf("\n");
      smalloc_stats();
    }

    if (PROMPT) {
      another = affirm("\nRun Another Problem");
    } else {
      another = affirm("");
    }
    if (another) {
      clear_timing();
      printf("\n------------------------------------------------\n\n");
      fflush(stdout);
    }
  }
  if (params_file != NULL) fclose(params_file);

  if (DEBUG_TRACE > 1) {
    printf("<Leaving main>\n");
  }

  return (0);
}
