#include "cpython/Python/pyforce.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

// Function to print BranchData array in JSON format
void printBranchDataAsJSON(struct BranchData exec_path[MAX_FORCED_FORKS][128], uint32_t fork_count) {
    printf("  \"exec_path\": [\n");
    for (int i = 0; i < MAX_FORCED_FORKS; i++) {
        printf("    [\n");
        char written = 0;
        for (int j = 0; j < 128; j++) {
            struct BranchData *bd = &exec_path[i][j];
            if (!(bd->data & (1 << B_VALID))) continue;
            printf("%s", written ? "," : "");
            written = 1;
            printf("      {\n");
            printf("        \"data\": %d,\n", bd->data);
            printf("        \"loc\": %d,\n", bd->loc);
            printf("        \"dst\": %d,\n", bd->dst);
            printf("        \"padding\": %d\n", bd->padding);
            printf("      }\n");
        }
        printf("    ]%s\n", i < MAX_FORCED_FORKS - 1 ? "," : "");
    }
    printf("  ],\n");
}

// Function to print RetList array in JSON format
void printRetListAsJSON(struct RetList ret_locations[MAX_FORCED_FORKS]) {
    printf("  \"ret_list\": [\n");
    for (int i = 0; i < MAX_FORCED_FORKS; i++) {
        printf("    [");
        for (uint32_t j = 0; j < ret_locations[i].idx && j < RET_LEN; j++) {
            printf("%d", ret_locations[i].ret_loc[j]);
            if (j < ret_locations[i].idx - 1) {
                printf(", ");
            }
        }
        printf("]%s\n", i < MAX_FORCED_FORKS - 1 ? "," : "");
    }
    printf("  ],\n");
}

void printCovListAsJSON(struct CovList ret_locations[MAX_FORCED_FORKS]) {
    printf("  \"cov_list\": [\n");
    for (int i = 0; i < MAX_FORCED_FORKS; i++) {
        printf("    [");
        for (uint32_t j = 0; j < ret_locations[i].idx && j < RET_LEN; j++) {
            printf("%d", ret_locations[i].loc[j]);
            if (j < ret_locations[i].idx - 1) {
                printf(", ");
            }
        }
        printf("]%s\n", i < MAX_FORCED_FORKS - 1 ? "," : "");
    }
    printf("  ],\n");
}

// Function to print JumpList array in JSON format
void printJumpListAsJSON(struct JumpList jmp_locations[MAX_FORCED_FORKS]) {
    printf("  \"jmp_list\": [\n");
    for (int i = 0; i < MAX_FORCED_FORKS; i++) {
        printf("    [\n");
        for (uint32_t j = 0; j < jmp_locations[i].idx && j < RET_LEN; j++) {
            struct JumpData *jd = &jmp_locations[i].jmp_data[j];
            printf("      [%d, %d]", jd->loc, jd->dst);
            if (j < jmp_locations[i].idx - 1) {
                printf(", ");
            }
            printf("\n");
        }
        printf("    ]%s\n", i < MAX_FORCED_FORKS - 1 ? "," : "");
    }
    printf("  ]\n");
}

// Function to print JSON format of SharedData
void printSharedDataAsJSON(struct SharedData *sharedData) {
    printf("{\n");
    printf("  \"fork_count\": %u,\n", sharedData->fork_count);
    
    printBranchDataAsJSON(sharedData->exec_path, sharedData->fork_count);
    printRetListAsJSON(sharedData->ret_locations);
    printCovListAsJSON(sharedData->cov);
    printJumpListAsJSON(sharedData->jmp_locations);

    printf("}\n");
}

// Main function to read from a file and print JSON
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    const char *filename = argv[1];
    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    struct SharedData sharedData;

    // Read the SharedData structure from the binary file
    size_t bytesRead = fread(&sharedData, sizeof(struct SharedData), 1, file);
    if (bytesRead != 1) {
        fprintf(stderr, "Error reading file\n");
        fclose(file);
        return 1;
    }
    fclose(file);

    // Print SharedData in JSON format
    printSharedDataAsJSON(&sharedData);

    return 0;
}