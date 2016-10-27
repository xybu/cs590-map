/* This software was developed by Bruce Hendrickson and Robert Leland   *
 * at Sandia National Laboratories under US Department of Energy        *
 * contract DE-AC04-76DP00789 and is copyrighted by Sandia Corporation. */

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "consts.h"
#include "defs.h"
#include "knapsack.h"
#include "structs.h"

declare_print_array_func(print_int_array, int *);
declare_save_array_func(save_switch_capacity_array, int *);

void save_goals_array(double *goal, double sum, int size) {
  int i;
  static int nth_save = 0;

  FILE *f;
  if (nth_save == 0) {
    f = fopen("goal_hist.txt", "w");
  } else {
    f = fopen("goal_hist.txt", "a");
  }

  fprintf(f, "%d, %lf", nth_save, sum);
  for (i = 0; i < size; ++i) fprintf(f, ", %lf", goal[i]);
  fputc('\n', f);

  fclose(f);
  nth_save++;
}

typedef struct int_index_pair {
  int value;
  int index;
} IntIndexPair;

int compare_int_index_pair_desc(const void *a, const void *b) {
  // Just in case INT_MIN appears...
  int v1 = ((IntIndexPair *)a)->value;
  int v2 = ((IntIndexPair *)b)->value;
  return -((v1 > v2) - (v1 < v2));
}

int Using_Main = FALSE; /* Is main routine being called? */

int interface(nvtxs, start, adjacency, vwgts, ewgts, x, y, z, outassignname,
              outfilename, assignment, architecture, ndims_tot, mesh_dims, goal,
              global_method, local_method, rqi_flag, vmax, ndims, eigtol, seed,
              host_cpu_percent, switch_cpu_usage, pm_capacity_func,
              is_pm_disabled) int nvtxs; /* number of vertices in full graph */
int *start;          /* start of edge list for each vertex */
int *adjacency;      /* edge list data */
int *vwgts;          /* weights for all vertices */
float *ewgts;        /* weights for all edges */
float *x, *y, *z;    /* coordinates for inertial method */
char *outassignname; /* name of assignment output file */
char *outfilename;   /* output file name */
short *assignment;   /* set number of each vtx (length n) */
int architecture;    /* 0 => hypercube, d => d-dimensional mesh */
int ndims_tot;       /* total number of cube dimensions to divide */
int mesh_dims[3];    /* dimensions of mesh of processors */
double *goal;        /* desired set sizes for each set */
int global_method;   /* global partitioning algorithm */
int local_method;    /* local partitioning algorithm */
int rqi_flag;        /* should I use RQI/Symmlq eigensolver? */
int vmax;            /* how many vertices to coarsen down to? */
int ndims;           /* number of eigenvectors (2^d sets) */
double eigtol;       /* tolerance on eigenvectors */
long seed;           /* for random graph mutations */
int *host_cpu_percent;
int *switch_cpu_usage;
int pm_capacity_func[20][3];
char *is_pm_disabled;
{
  extern char *PARAMS_FILENAME; /* name of file with parameter updates */
  extern int MAKE_VWGTS;        /* make vertex weights equal to degrees? */
  extern int MATCH_TYPE;        /* matching routine to use */
  extern int FREE_GRAPH;        /* free graph data structure after reformat? */
  extern int DEBUG_PARAMS;      /* debug flag for reading parameters */
  extern int DEBUG_TRACE;       /* trace main execution path */
  extern double start_time;     /* time routine is entered */
  extern double reformat_time;  /* time spent reformatting graph */
  FILE *params_file;            /* file for reading new parameters */
  struct vtx_data **graph;      /* graph data structure */
  double vwgt_sum;              /* sum of vertex weights */
  double time;                  /* timing variable */
  float **coords;               /* coordinates for vertices if used */
  int *vptr;                    /* loops through vertex weights */
  int flag;                     /* return code from balance */
  int nedges;                   /* number of edges in graph */
  int using_vwgts;              /* are vertex weights being used? */
  int using_ewgts;              /* are edge weights being used? */
  int nsets_tot;                /* total number of sets being created */
  int igeom;                    /* geometric dimension for inertial method */
  int default_goal;             /* using default goals? */
  int i;                        /* loop counter */
  double seconds();
  double *smalloc_ret();
  int sfree(), submain(), reformat();
  void free_graph(), read_params(), strout();

  if (DEBUG_TRACE > 0) {
    printf("<Entering interface>\n");
  }

  flag = 0;
  graph = NULL;
  coords = NULL;

  if (!Using_Main) { /* If not using main, need to read parameters file. */
    start_time = seconds();
    params_file = fopen(PARAMS_FILENAME, "r");
    if (params_file == NULL && DEBUG_PARAMS > 1) {
      printf("Parameter file `%s' not found; using default parameters.\n",
             PARAMS_FILENAME);
    }
    read_params(params_file);
  }

  if (goal ==
      NULL) { /* If not passed in, default goals have equal set sizes. */
    default_goal = TRUE;
    if (architecture == 0)
      nsets_tot = 1 << ndims_tot;
    else if (architecture == 1)
      nsets_tot = mesh_dims[0];
    else if (architecture == 2)
      nsets_tot = mesh_dims[0] * mesh_dims[1];
    else if (architecture > 2)
      nsets_tot = mesh_dims[0] * mesh_dims[1] * mesh_dims[2];

    if (MAKE_VWGTS && start != NULL) {
      vwgt_sum = start[nvtxs] - start[0] + nvtxs;
    } else if (vwgts == NULL) {
      // if unweighted graph
      vwgt_sum = nvtxs;
    } else {
      vwgt_sum = 0;
      vptr = vwgts;
      for (i = nvtxs; i; i--) vwgt_sum += *(vptr++);
    }
    // REVISED //

    double capa_sum = 0;
    IntIndexPair pm_capacity[nsets_tot];

    for (i = 0; i < nsets_tot; i++) {
      int x = switch_cpu_usage[i];
      double capa_0 = pm_capacity_func[i][2];
      double capa_1 = pm_capacity_func[i][1] * x;
      double capa_2 = pm_capacity_func[i][0] * x * x;
      int fn_capacity = (int)((capa_2 + capa_1 + capa_0) / 10000);

      // TODO: change this to MAX_CPU_PERCENT.
      int max_cpu_share_for_vhosts = UNDER_UTILIZATION_THRESHOLD - switch_cpu_usage[i];
      int knapsack_capacity = solve_knapsack(max_cpu_share_for_vhosts, nvtxs,
                                             host_cpu_percent, vwgts);
      pm_capacity[i].index = i;
      pm_capacity[i].value = min(fn_capacity, knapsack_capacity);
      capa_sum += pm_capacity[i].value;
      printf(
          "PM #%d: cpu_sw=%d, cpu_host=%d, fn_cap=%d, ks_cap=%d. Final=%d.\n",
          i, switch_cpu_usage[i], max_cpu_share_for_vhosts, fn_capacity, knapsack_capacity, pm_capacity[i].value);
    }

    {
      int capacity_values[nsets_tot];
      for (i = 0; i < nsets_tot; ++i) {
        capacity_values[i] = pm_capacity[i].value;
      }
      save_switch_capacity_array(capacity_values, nsets_tot);
    }

    putchar('\n');
    printf("Sum of vertex weight (vwgt_sum): %lf.\n", vwgt_sum);
    printf("Total capacity of PMs (capa_sum): %lf.\n", capa_sum);
    printf("Total number of sets (nsets_tot): %d.\n", nsets_tot);

    goal = (double *)smalloc_ret((unsigned)nsets_tot * sizeof(double));
    if (goal == NULL) {
      strout("\nERROR: No room to make goals.\n");
      flag = 1;
      goto skip;
    }
    memset(goal, 0, (unsigned)nsets_tot * sizeof(double));

    if (capa_sum < vwgt_sum) {
      // When PM packet processing capacity is less than needed, scale
      // up the capacity values proportionally.
      double scaled_capa_sum = 0;
      for (i = 0; i < nsets_tot; i++) {
        goal[i] =
            (double)vwgt_sum * ((double)(pm_capacity[i].value) / capa_sum);
        scaled_capa_sum += goal[i];
      }

      // Fix the rounding error by adding the error to a PM's goal.
      if (vwgt_sum - scaled_capa_sum != 0) {
        for (i = 0; i < nsets_tot; i++) {
          if (goal[i] >= 1) {
            goal[i] += vwgt_sum - scaled_capa_sum;
            break;
          }
        }
      }

      /*double tmp_total = 0;
      for (i = 0; i < nsets_tot; i++) {
        goal[i] = ((double)set_capa[i]) * vwgt_sum / capa_sum;
        tmp_total += goal[i];
      }
      if (vwgt_sum - tmp_total > 0) {
        for (i = 0; i < nsets_tot; i++) {
          if (set_capa[i] >= 1) {
            goal[i] += vwgt_sum - tmp_total;
            break;
          }
        }
      }
      */
    } else {
      puts("Sort PMs by capacity value.");
      qsort(pm_capacity, nsets_tot, sizeof(IntIndexPair),
            compare_int_index_pair_desc);

      for (i = 0; i < nsets_tot; ++i) {
        printf(" %d - PM #%d: capacity=%d.\n", i, pm_capacity[i].index,
               pm_capacity[i].value);
      }

      // TODO: another approach is to distribute weights proportionally.
      // Not sure which one is better.
      for (i = 0; i < nsets_tot; ++i) {
        int index = pm_capacity[i].index;
        int cap = pm_capacity[i].value;
        if (vwgt_sum < 0.1) {
          // If all vertex weight has been covered, PM i is not needed anymore.
          goal[index] = 0;
        } else if (vwgt_sum > cap) {
          // When PM i's capacity is not enough to cover all vertex weight.
          goal[index] = cap;
          vwgt_sum -= cap;
        } else {
          // When partial capacity is needed in the last PM.
          goal[index] = vwgt_sum;
          vwgt_sum = 0;
        }
      }

      /*
      int flag_need_PM = 1;
      for (i = 0; i < nsets_tot; i++) {
        int j = 0;
        int max_index = 0;
        int max_capa = 0;
        for (j = 0; j < nsets_tot;
             j++) {  // find the index of the i'th largest capacity
          if (goal[j] < 0.1 &&
              set_capa[j] >= max_capa) {  // may have problem (<1???)
            max_index = j;
            max_capa = set_capa[j];
          }
        }

        // printf("1111111111111   %d\n", max_index);

        if (flag_need_PM == 0) {
          goal[max_index] = 0;
          continue;
        }
        // TODO: this goal calculation may be refined.
        if (vwgt_sum > set_capa[max_index]) {
          goal[max_index] = set_capa[max_index];
          vwgt_sum -= set_capa[max_index];
        } else {
          goal[max_index] = vwgt_sum;
          flag_need_PM = 0;
        }
      }
      */
    }

    for (i = 0; i < nsets_tot; i++) {
      printf("goal[%d]: %lf\n", i, goal[i]);
      is_pm_disabled[i] = goal[i] < 0.1 ? 1 : 0;
    }
    save_goals_array(goal, capa_sum, nsets_tot);

    // REVISED //

  } else {
    default_goal = FALSE;
  }

  if (MAKE_VWGTS) {
    /* Generate vertex weights equal to degree of node. */
    if (vwgts != NULL) {
      strout("WARNING: Vertex weights being overwritten by vertex degrees.");
    }
    vwgts = (int *)smalloc_ret((unsigned)nvtxs * sizeof(int));
    if (vwgts == NULL) {
      strout("\nERROR: No room to make vertex weights.\n");
      flag = 1;
      goto skip;
    }
    if (start != NULL) {
      for (i = 0; i < nvtxs; i++) vwgts[i] = 1 + start[i + 1] - start[i];
    } else {
      for (i = 0; i < nvtxs; i++) vwgts[i] = 1;
    }
  }

  using_vwgts = (vwgts != NULL);
  using_ewgts = (ewgts != NULL);

  if (start != NULL || vwgts != NULL) { /* Reformat into our data structure. */
    time = seconds();

    flag = reformat(start, adjacency, nvtxs, &nedges, vwgts, ewgts,
                    &graph);  // may have segmentation fault Siyuan!

    if (flag) {
      strout("\nERROR: No room to reformat graph.\n");
      goto skip;
    }

    reformat_time += seconds() - time;
  } else {
    nedges = 0;
  }

  if (FREE_GRAPH) { /* Free old graph data structures. */
    sfree((char *)start);
    sfree((char *)adjacency);
    if (vwgts != NULL) sfree((char *)vwgts);
    if (ewgts != NULL) sfree((char *)ewgts);
    start = NULL;
    adjacency = NULL;
    vwgts = NULL;
    ewgts = NULL;
  }

  if (global_method == 3 ||
      (MATCH_TYPE == 5 &&
       (global_method == 1 || (global_method == 2 && rqi_flag)))) {
    if (x == NULL) {
      igeom = 0;
    } else { /* Set up coordinate data structure. */
      coords = (float **)smalloc_ret((unsigned)3 * sizeof(float *));
      if (coords == NULL) {
        strout("\nERROR: No room to make coordinate array.\n");
        flag = 1;
        goto skip;
      }
      /* Minus 1's are to allow remainder of program to index with 1. */
      coords[0] = x - 1;
      igeom = 1;
      if (y != NULL) {
        coords[1] = y - 1;
        igeom = 2;
        if (z != NULL) {
          coords[2] = z - 1;
          igeom = 3;
        }
      }
    }
  } else {
    igeom = 0;
  }

  /* Subtract from assignment to allow code to index from 1. */
  assignment = assignment - 1;
  flag = submain(graph, nvtxs, nedges, using_vwgts, using_ewgts, igeom, coords,
                 outassignname, outfilename, assignment, goal, architecture,
                 ndims_tot, mesh_dims, global_method, local_method, rqi_flag,
                 vmax, ndims, eigtol, seed);

skip:
  if (coords != NULL) sfree((char *)coords);

  if (default_goal) sfree((char *)goal);

  if (graph != NULL) free_graph(graph);

  if (flag && FREE_GRAPH) {
    sfree((char *)start);
    sfree((char *)adjacency);
    sfree((char *)vwgts);
    sfree((char *)ewgts);
  }

  if (!Using_Main && params_file != NULL) fclose(params_file);

  return (flag);
}
