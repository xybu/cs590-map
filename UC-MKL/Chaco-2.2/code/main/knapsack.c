#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"

// #define _DEBUG

#ifdef _DEBUG
    #define debug(...);  fprintf(stderr, __VA_ARGS__);
#else
    #define debug(...);
#endif

/**
 * A simple solver for 0/1 knapsack problem. Given the capacity of the bag
 * and two lists of nitems items -- the weights (cost) and profits -- return
 * the max possible profit of items that can fit in the bag.
 * @param bag_capacity The limit on sum of weights of chosen items.
 * @param nitems Total number of items.
 * @param weights Weight of each item. Assume an array of length nitems.
 * @param profits Profit of each item. Assume an array of length nitems.
 * @return Best possible profit.
 */
int solve_knapsack(int bag_capacity, int nitems, int *weights, int *profits) {
  int i, j, m[nitems + 1][bag_capacity + 1];
  
  // Actually initialize m[0] is enough.
  memset(m, 0, sizeof(m[0]));
  
  for (i = 0; i < nitems; ++i) {
    debug("Trying item %d (w=%d, v=%d)...\n", i, weights[i], profits[i]);
    for (j = 0; j <= bag_capacity; ++j) {
      debug("Trying to fit weight %d...\n", j);
      if (weights[i] > j) {
        debug("Cannot fit item %d on weight %d because it's too heavy.\n", i, j);
        m[i + 1][j] = m[i][j];
      } else {
        debug("Best so far: %d. With this item: %d.\n", m[i][j], m[i][j-weights[i]] + values[i]);
        m[i + 1][j] = max(m[i][j], m[i][j-weights[i]] + profits[i]);
      }
    }
  }

  return m[nitems][bag_capacity];
}
