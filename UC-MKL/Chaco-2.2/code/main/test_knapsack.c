#include <stdio.h>
#include <stdlib.h>
#include "knapsack.h"

void read_ints_to_array(const char *filename_prefix,
                        const char *filename_suffix,
                        int *array, int size) {
  int i;
  char buf[256];
  snprintf(buf, 256, "%s_%s.txt", filename_prefix, filename_suffix);
  FILE *f = fopen(buf, "r");
  if (!f) {
    perror("fopen");
    exit(1);
  }
  for (i = 0; i < size; ++i) {
    if (fscanf(f, "%d", array + i) != 1) {
      perror("fscanf");
      exit(1);
    }
  }
  fclose(f);
}

int main(int argc, char *argv[]) {
  int i, sum_profit = 0, sum_weight = 0;
  int test[2];

  read_ints_to_array(argv[1], "c", test, 2);
  int capacity = test[0];
  int nitems = test[1];
  printf("nitems: %d.\ncapacity: %d.\n", nitems, capacity);

  int profits[nitems];
  int weights[nitems];
  int solution[nitems];

  read_ints_to_array(argv[1], "p", profits, nitems);
  read_ints_to_array(argv[1], "w", weights, nitems);
  read_ints_to_array(argv[1], "s", solution, nitems);

  int profit = solve_knapsack(capacity, nitems, weights, profits);
  for (i = 0; i < nitems; ++i) {
    if (solution[i]) {
      sum_profit += profits[i];
      sum_weight += weights[i];
    }
  }
  
  printf("Desired profit: %d, weight: %d.\n", sum_profit, sum_weight);
  
  if (sum_profit != profit) {
    printf("\033[91m");
  }
  printf("Calculated profit: %d.\n", profit);
  printf("\033[0m");

  return 0;
}
