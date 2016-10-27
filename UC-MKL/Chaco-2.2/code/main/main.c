/* This software was developed by Bruce Hendrickson and Robert Leland   *
 * at Sandia National Laboratories under US Department of Energy        *
 * contract DE-AC04-76DP00789 and is copyrighted by Sandia Corporation. */

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "consts.h"
#include "params.h"

define_print_array_func(print_int_array, int *, "%2d");
define_print_array_func(print_short_array, short *, "%2d");
define_print_array_func(print_char_array, char *, "%2d");

define_save_array_func(save_assignment_array, short *, "assignment_hist.txt");
define_save_array_func(save_switch_capacity_array, int *,
                       "switch_capacity_hist.txt");
define_save_array_func(save_host_usage_array, int *, "host_usage_hist.txt");
define_save_array_func(save_usage_array, int *, "usage_hist.txt");

/**
 * Calculate the sum of CPU share of hosts assigned to each PM.
 * @param nhosts Total number of hosts (nodes).
 * @param host_cpu_percent CPU share required by each host.
 * @param assignment Mapping from host to PM.
 * @param npms Total number of PMs.
 * @param pm_host_usage The array to store the sum of CPU share for each PM.
 */
void update_host_usage(int nhosts, int *host_cpu_percent, short *assignment,
                       int npms, int *pm_host_usage) {
  int i;
  short assigned_pm;
  for (i = 0; i < nhosts; ++i) {
    assigned_pm = assignment[i];
    if (assigned_pm < 0 || assigned_pm >= npms) {
      printf("Error: host %d is assigned to PM #%d which does not exist!\n", i,
             assigned_pm);
      exit(1);
    }
    pm_host_usage[assigned_pm] += host_cpu_percent[i];
  }
}

/**
 * Do a linear search to find the most under-utilized PM. Nodes assigned to
 * disabled PMs may be moved to this PM.
 * @param npms Total number of PMs.
 * @param pm_host_usage Current CPU share used by hosts on each PM.
 * @param is_pm_disabled An array that indicates if each PM is disabled.
 * @return Index of the most under-utilized PM.
 */
int find_most_under_utilized_pm(int npms, int *pm_host_usage,
                                char *is_pm_disabled) {
  int i, min_index = -1, min_usage = INT_MAX;
  for (i = 0; i < npms; ++i) {
    if (is_pm_disabled[i]) continue;
    if (min_usage > pm_host_usage[i]) {
      min_index = i;
      min_usage = pm_host_usage[i];
    }
  }
  return min_index;
}

/**
 * To deal with the case where MKL assigns nodes to disabled PMs, we do a
 * post-assignment check in which we move such nodes to other PMs. Current
 * policy is to move each node to the most under-utilized PM at the time when
 * the PM CPU usages are checked.
 * We observe that such nodes are usually "trivial" leaf nodes so moving them
 * to any PM should work.
 * @param nhosts Total number of hosts (nodes).
 * @param host_cpu_percent CPU share required by each host.
 * @param assignment Mapping from host to PM.
 * @param npms Total number of PMs.
 * @param pm_host_usage The array to store the sum of CPU share for each PM.
 * @param is_pm_disabled An array that indicates if each PM is disabled.
 */
void clear_disabled_pm_mapping(int nhosts, int *host_cpu_percent,
                               short *assignment, int npms, int *pm_host_usage,
                               char *is_pm_disabled) {
  int i;
  short assigned_pm, pm;
  for (i = 0; i < nhosts; ++i) {
    assigned_pm = assignment[i];
    if (is_pm_disabled[assigned_pm]) {
      // This host is assigned to a PM that is disabled.
      pm = find_most_under_utilized_pm(npms, pm_host_usage, is_pm_disabled);
      assignment[i] = pm;
      pm_host_usage[pm] += host_cpu_percent[i];
      pm_host_usage[assigned_pm] -= host_cpu_percent[i];
      printf(
          "Warning: host %d is assigned to disabled PM #%d. Move it to %d.\n",
          i, assigned_pm, pm);
    }
  }
}

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
  char is_pm_disabled[20];

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
    memset(usage, 0, sizeof(usage));
    memset(host_usage, 0, sizeof(host_usage));
    // for (i = 0; i < 20; i++) {
    //   usage[i] = 0;
    //   host_usage[i] = 0;
    //   // printf("-------- %d, %d\n", i,u[i]);
    // }

    print_int_array("usage", usage, 20);
    print_int_array("host_usage", host_usage, 20);

    read_params(params_file);

    input_queries(&fin, &fin_host, &fingeom, &finassign, graphname, hostname,
                  geomname, inassignname, outassignname, outfilename,
                  &architecture, &ndims_tot, set_capa_func, usage,
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
    memset(assignment, 0, nvtxs * sizeof(short));
    host_percent = (int *)smalloc((unsigned)nvtxs * sizeof(int));  // ADD!
    /****** read the host file here! *******/
    // printf("length!!!!!! %d", nvtxs);

    size_t host_percent_sum = 0;
    for (j = 0; j < nvtxs; j++) {
      fscanf(fin_host, "%d", host_percent + j);
      host_percent_sum += host_percent[j];
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

    for (i = 0; i < nprocs; ++i) {
      usage[i] = MIN_CPU_PERCENT;
    }
    print_int_array("usage (averaged)", usage, nprocs);

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

      FILE *f = fopen("vwgts.txt", "w");
      for (i = 0; i < nvtxs; ++i) {
        fprintf(f, "%d\n", vwgts[i]);
      }
      fclose(f);

      // for (cur = 0; cur < nprocs; cur++) {
      //   printf("~~~~~time %d: current switch capacity~~~~~~~  %d\n", n,
      //          set_capa[cur]);
      // }

      // one partitioning
      interface(nvtxs, start, adjacency, vwgts, ewgts, x, y, z, outassignptr,
                outfileptr, assignment, architecture, ndims_tot, mesh_dims,
                goal, global_method, local_method, rqi_flag, vmax,
                ndims, eigtol, seed, host_percent, usage, set_capa_func, is_pm_disabled);
      printf("~~~~~~~~~~~~~~partitioning finished~~~~~~~~~~~~~~~~~~\n");

      print_int_array("host_percent (after partition)", host_percent, nvtxs);

      print_short_array("assignment (after partition)", assignment, nvtxs);
      save_assignment_array(assignment, nvtxs);

      if (architecture != 0) {
        printf(
            "Warning: routine to move nodes out of disabled PMs does not "
            "support architecture %d. Will use all available PMs instead.\n\n",
            architecture);
        for (i = 0; i < nprocs; i++) {
          int *coeff = set_capa_func[i];
          if (coeff[2] + coeff[1] + coeff[0] == 0) {
            is_pm_disabled[i] = 1;
          } else {
            is_pm_disabled[i] = 0;
          }
        }
      }

      print_char_array("is_pm_disabled (after partitioning)",
                       is_pm_disabled, nprocs);

      // recompute u values according to the assignment results
      memset(host_usage, 0, sizeof(host_usage));

      update_host_usage(nvtxs, host_percent, assignment, nprocs, host_usage);

      clear_disabled_pm_mapping(nvtxs, host_percent, assignment, nprocs,
                                host_usage, is_pm_disabled);

      print_int_array("host_usage (updated)", host_usage, 20);
      save_host_usage_array(host_usage, 20);

      int num_under_utilized_host = 0;
      int num_over_utilized_host = 0;

      for (i = 0; i < nprocs; i++) {
        
        // Update CPU usage for a PM iff it's involved in this iteration.
        if (is_pm_disabled[i]) {
          printf("PM %d is disabled in this iteration.\n\n", i);
          continue;
        }

        int total_usage = host_usage[i] + usage[i];
        if (total_usage < UNDER_UTILIZATION_THRESHOLD) {
          num_under_utilized_host++;
          printf("PM %d is under-utilized. Its CPU usage is %d + %d = %d.\n",
                 i, host_usage[i], usage[i], total_usage);
        } else if (total_usage > OVER_UTILIZATION_THRESHOLD) {
          num_over_utilized_host++;
          printf("PM %d is over-utilized. Its CPU usage is %d + %d = %d.\n",
                 i, host_usage[i], usage[i], total_usage);
        } else {
          printf("PM %d seems fine. Its CPU usage is %d + %d = %d.\n", i,
                 host_usage[i], usage[i], total_usage);
        }

        double current_usage = MAX_CPU_PERCENT - host_usage[i];
        if (current_usage < MIN_CPU_PERCENT) {
          current_usage = MIN_CPU_PERCENT;
        }

        double old_usage = usage[i];

        usage[i] = (int)((1 - CURRENT_USAGE_WEIGHT) * (old_usage) +
                           (CURRENT_USAGE_WEIGHT) * (current_usage));

        printf("  |- Accum. usage=%.2lf, New usage=%.2lf, Next usage=%d.\n\n",
               old_usage, current_usage, usage[i]);

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
      for (i = 0; i < n; ++i) {
        if (!memcmp(assignment_history[i], assignment, nvtxs * sizeof(short))) {
          // When finding an assignment that is already attempted, terminate
          // for now. There should be better policy though.
          printf("Iteration %d gives same assignment as %d. Stop.\n", n, i);
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

    for (i = 0; i < n; ++i) free(assignment_history[i]);

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
    } else {
      putchar('\n');
    }
  }
  if (params_file != NULL) fclose(params_file);

  if (DEBUG_TRACE > 1) {
    printf("<Leaving main>\n");
  }

  return (0);
}
