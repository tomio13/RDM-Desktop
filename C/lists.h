/* Define here the necessary string struct and functions for:
 * allocation, freeing
 * copying
 * trimming
 * replacing characters
 */

#include<stdio.h>
#include<string.h>
#include<stdlib.h>

typedef struct r_string_s{
    char *value;
    size_t length;
} r_string_t;


typedef enum record_type_e{
    /* record is empty */
    RECORD_EMPTY,
    /* a single line string */
    RECORD_STRING,
    /* float or int, test for float */
    RECORD_NUMERIC,
    /* string contains new lines */
    RECORD_MULTILINE_STRING,
    /* or a list subtree*/
    RECORD_CHILD_LIST
}record_type_t;


/* a record is a key value par
 * we do not care about numbers or strings, store
 * everything as string
 * A key is always a string
 * A value can be:
 *   * a string
 *   * a dict (array of records, see later)
 *   * a list of records
 * thus, we have to use a void* and make sure
 * we know what to do. Use the record_type_t to
 * address this!
 *
 * two pointers to form a list
 */
typedef struct record_s{
    r_string_t *key;
    void *value;
    record_type_t type;
    /* form a list with pointers */
    struct record_s* previous;
    struct record_s* next;
}record_t;

/**************** function ****************/
r_string_t* new_string(size_t length);
r_string_t* new_string_from_text(char* text, int length);
r_string_t* new_string_timestamp(void);
void delete_string(r_string_t *text);
record_t* new_record(void);
void clear_record(record_t *rec);
void delete_record(record_t *rec);

record_t *end_list(record_t *list);
record_t *start_list(record_t *list);
record_t* append_record(record_t *list, record_t *record);
/* delete_record is equivalent to pop the element */
# define pop_record(rec) delete_record(rec)

void delete_list(record_t *list);
record_t *list_find(record_t *list, r_string_t *key);

void print_list_indent(record_t *list, int indent);
#define print_list(x) print_list_indent(x, 0)

int index_list(record_t *list);
int len_list(record_t *list);

/* array from list members or parts for
 * quick access if a sweep is needed multiple times
 */
record_t **list_array(record_t *list);
void delete_list_array(record_t** array, int length);
r_string_t **values_array(record_t *list);
r_string_t **keys_array(record_t *list);
void delete_string_array(r_string_t **array, int length);

