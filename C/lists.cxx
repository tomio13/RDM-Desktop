/* Define here the necessary string struct and functions for:
 * allocation, freeing
 * copying
 * trimming
 * replacing characters
 */

#include<stdio.h>
#include<string.h>
#include<stdlib.h>
/* for adding timestamp entry */
#include<time.h>

#include "lists.h"

/** new_string()
 * allocate a new string and clear up the memory
 * length is without the closing '\0'
 *
 * parameter length integer length of string
 *
 * return
 * a pointer or NULL upon error
 */
r_string_t* new_string(size_t length) {
    size_t i;
    r_string_t *res;

    if (length < 1) {
        printf("Invalid length requested: %u\n", (uint)length);
        return(NULL);
    }

    if ((res = (r_string_t *)malloc(sizeof(r_string_t))) == NULL) {
        fputs("Unable to allocate string array!\n", stderr);
        return(NULL);
    }
    if ((res->value = (char*)malloc((length+1)*sizeof(char))) == NULL) {
        fputs("Unable to allocate value string!\n", stderr);
        free(res);
        return(NULL);
    }
    res->length = length;

    for (i=0; i < (length+1); i++) *(res->value + i) = '\0';

    return(res);
}


/** new_string_from_text()
 * make a new string and fill it up with the provided
 * text.
 * Do everything at low level, not calling new_string
 * Assume that length does NOT include the closing '\0'
 *
 * parameters
 * char* text   the text to copy in
 * int length   the length of text
 *
 * return
 * r_string_t* new pointer
 */
r_string_t* new_string_from_text(char* text, int length) {
    r_string_t *res;

    res = new_string((size_t)length);
    if (text != NULL && length > 0) {
        strncpy(res->value, text, length+1);
    }
    res->length = length > 0 ? length:0;

    return(res);
}


/* new_string_timestamp()
 * create a new string from the current date/time.
 *
 * parameters: None
 * return:
 * r_string_t *timestamp
 */
r_string_t* new_string_timestamp(void) {
    time_t *now= NULL;
    char *timestamp= NULL;

    if (time(now) <0) {
        fputs("Unable to get local time!\n", stderr);
        return(NULL);
    }
    timestamp = ctime((const time_t*)(now));
    /* according to the documentation, the string should be maximum
     * 26 characters long
     */
    return(new_string_from_text(timestamp, strnlen(timestamp, 26)));
}

/* string_concat()
 * concatenate two strings with a separator character into one new string;
 * allocate the new string, so the user has to clean it up.
 * It is assumed that the length parameters point to the
 * end of each string.
 *
 * parameters:
 * r_string_t *s1
 * r_string_t *s2 the two strings to be put together
 * char sep
 *
 * return:
 * r_string_t *res a new string, or s1 or s2 it the other
 * is NULL;
 */
r_string_t *string_concat(r_string_t *s1, r_string_t *s2, char sep=0) {
    r_string_t *res;
    char *s= NULL;
    size_t i=0;
    size_t l=0;

    if (s1 == NULL) {
        return(s2);
    }
    if (s2 == NULL) {
        return(s1);
    }

    l= sep == 0 ? s1->length+s2->length : s1->length + s2->length + 1;
    if( (res = new_string(l)) == NULL) {
        fputs("Unable allocating memory\n", stderr);
        return(NULL);
    }

    s = res->value;
    for(i=0; i < s1->length; i++) {
        *s = *(s1->value+i);
        s++;
    }
    if (sep != 0) {
        *s = sep;
        s++;
    }
    for(;i < l; i++) {
        *s = *(s2->value + i-s1->length);
        s++;
    }
    /* the closing \0 was not included */
    *s = '\0';
    return(res);
}

/* string_replace_char
 * replace one character with another one
 * inside a string
 *
 * parameters:
 * r_string_t *text     the text to replace within
 * char from
 * char to
 *
 * return: None
 * replacement happens in place
 */
void string_replace_char(r_string_t *text, char from, char to) {
    size_t i;

    if (text == NULL || text->value == NULL) {
        return;
    }
    if (from == to) {
        /* nothing to do */
        return;
    }
    for(i=0; i< text->length; i++) {
        if(*(text->value+i) == from) {
            *(text->value+i) = to;
        }
    }
    return;
}


/** delete_string()
 * take a string, clean it up and release the memory
 *
 * parameter pointer to an r_string_t structure
 *
 * return nothing
 */
void delete_string(r_string_t *text){

    size_t i;

    if (text == NULL){
        return;
    }
    if (text -> value != NULL) {
        /* erase the content, so no sensitive information remains
         * in unallocated memory
         */
        for (i=0; i< text->length; i++) *(text->value +i) = '\0';

        free(text->value);
        text->value = NULL;
        text->length = 0;
    }
    free(text);

    return;
}


/** new_record()
 * allocate a simple record for futher use
 *
 * parameters: none
 * return: a pointer to the new record
 */
record_t* new_record(void){
    record_t *res;

    if ((res = (record_t*)malloc(sizeof(record_t))) == NULL) {
        fputs("Unable to allocate new record!\n", stderr);
        return(NULL);
    }
    res->key = NULL;
    res->value= NULL;
    res->type = RECORD_EMPTY;
    /* standing alone: */
    res->previous = NULL;
    res->next = NULL;

    /*
    * printf(".... Allocated new record %p\n", res);
    */
    return(res);
}


/* clear_record()
 * clean out the content of a record deleting the strings,
 * but keeping the record_t* pointer
 *
 * parameter: rec a pointer to a record_t structure
 * return None
 */
void clear_record(record_t *rec) {
    if (rec != NULL){
        delete_string(rec->key);
        /* what we free up, depends on
         * what we have here...
         */
        switch(rec->type) {
            case RECORD_EMPTY:
                return;
            /* these are all stored as string:
             */
            case RECORD_STRING:
            case RECORD_NUMERIC:
            case RECORD_MULTILINE_STRING:
                delete_string((r_string_t*)(rec->value));
                break;
            /* if we have a child here, we may
             * have to clean it up!
             */
            case RECORD_CHILD_LIST:
                delete_list((record_t*)(rec->value));
                break;
            default:
                fputs("Unknown record type in clear_record!\n", stderr);
            }
        rec->type= RECORD_EMPTY;
    }
    /* if we pulled this element from a list,
     * we have to close the hole
     * either we are between next and previous
     * or at one end, where either next or
     * previous are not NULL
     */
    if (rec->next != NULL && rec->previous != NULL) {
        (rec->next)->previous = rec->previous;
        (rec->previous)->next = rec->next;
    } else if (rec->next != NULL) {
        /* we are at the front */
        (rec->next)->previous = NULL;
    } else if (rec->previous != NULL) {
        /* we are at the end */
        (rec->previous)->next= NULL;
    }
    rec->next= NULL;
    rec->previous= NULL;

    return;
}


/** delete_record()
 * delete the record content and release the memory
 *
 * parameter: record_t* rec
 *
 * return: None
 */
void delete_record(record_t *rec) {
    if(rec != NULL){
        clear_record(rec);
        free(rec);
    }
    return;
}

/** end_list()
 * go to the end of a list
 *
 * parameters:
 * record_t *list an element of the list
 *
 * return:
 * record_t *end   the last element of the list
 */

record_t *end_list(record_t *list) {
    record_t *curr;
    if (list == NULL) {
        return(NULL);
    }

    curr= list;
    while(curr->next != NULL) {
        curr = curr->next;
    }

    return(curr);
}

/** start_list()
 * go to the beginning of a list
 *
 * parameters:
 * record_t *list an element of the list
 *
 * return:
 * record_t *end   the last element of the list
 */

record_t *start_list(record_t *list) {
    record_t *curr;
    if (list == NULL) {
        return(NULL);
    }

    curr= list;
    while(curr->previous != NULL) {
        curr = curr->previous;
    }

    return(curr);
}

/** append_record()
 * append a record to an existing list
 * the list is represented by one of its members, we append
 * recort to the end of the list
 *
 * parameters:
 * result_t list a list indicated with one of its members
 * record_t record what to append
 *
 * return the address of the new element
 */

record_t* append_record(record_t *list, record_t *record) {
    record_t *curr_element= NULL;

    if (record == NULL) {
        fputs("Request to add no record!\n", stderr);
        return(list);
    }
    if (list != NULL) {
        /* go to the end of the list */
        /*
         * printf("Start list from: %p\n", list);
         */
        curr_element = end_list(list);
        /*
         * printf("End of list reached: %p\n", curr_element);
         */
        /* and now, append updating the references */
        curr_element->next = record;
        record->previous = curr_element;
        /* record->next = NULL;
         * but leaving this out means we can
         * merge two lists if record is the first
         * in that one...
         */
    }

    /*
     * printf("called append with %p / %p\n", list, record);
     */
    return(record);
}


/** delete_list()
 * delete an entire list, clearing the memory
 *
 * parameters: record_t *list
 *
 * return: None
 */
void delete_list(record_t *list) {
    record_t *current;

    if (list == NULL) {
        return;
    }
    /* a single element only? */
    if (list->next == NULL && list->previous == NULL) {
        delete_record(list);
        return;
    }
    /* go to the beginning of the list */
    current = start_list(list);

    /* we walk upwards, and kill the
     * one before the current one */
    while(current->next != NULL) {
        /*
        printf("deleting: %p\n", current);
        printf("has previous: %p\n", current->previous);
        */
        current = current->next;
        delete_record(current->previous);
    }
    /* now, only one is left and destroyed */
    delete_record(current);
    return;
}

/** list_find()
 * Find the first record in a list
 * where key matches a requested string
 * Go from the provided record, thus if one uses it
 * iteratively, every element with a specific key can be
 * collected
 *
 * parameters:
 * record_t *list  a list element, we walk this list
 * r_string_t *key      a string to search for
 *
 * return:
 * record_t *result     a pointer to the matching record or NULL
 */

record_t* list_find(record_t *list, r_string_t *key) {

    record_t *this_r= NULL;
    int hit =0;

    if (list == NULL) {
        return(NULL);
    }
    /* start where we are: */
    this_r = list;

    /* at least check this element then all next */
    do {
        /* we use this to hold the record address */
        if (this_r->key->length == key->length && \
                strncmp(this_r->key->value, key->value, key->length) == 0) {
            hit= 1;
            break;
        }
    } while(hit <1 && (this_r= this_r->next)!= NULL);

    if (hit < 1) {
        this_r = NULL;
    }
    return(this_r);
}

/* list_find_from_text()
 * do the list find based on a const char text string
 * basically just do some wrapping and call the function above
 *
 * parameters:
 * record_t *list       a pointer inside a list
 * const char* key      what to search for
 *
 * return:
 * record_t*    pointer to the result or NULL
 */
record_t *list_find_from_text(record_t *list, const char* key) {

    r_string_t *keystring = NULL;
    record_t *result= NULL;
    int N= 0;
    N = strlen(key);

    if (N < 1) {
        fputs("Searching for empty list!\n", stderr);
        return(NULL);
    }

    keystring = new_string_from_text((char*)key, N);

    result = list_find(list, keystring);
    delete_string(keystring);

    return(result);
}


/** print_block_indent()
 * print an indented block, like the multiline
 * text in YAML
 *
 * parameters:
 * r_string_t * text
 * int indnet   depth of indentation
 * FILE *fp     file pointer to output
 *
 * return None
 */
void print_block_indent(r_string_t *text, int indent, FILE *fp= stdout) {
    size_t i=0;
    int  j=0;
    char c;

    if (text == NULL || text->length < 1) {
        return;
    }

    if (fp == NULL) {
        fp = stdout;
    }

    for (j=0; j< indent; j++) {
        fputc(' ', fp);
    }
    for (i=0; i<text->length; i++) {
        c = *(text->value +i);
        fputc(c, fp);

        if(c == '\n' || c=='\r') {
            for (j=0; j<indent; j++) {
                fputc(' ', fp);
            }
        }
    }
    /* end of the line, then a new line */
    fputc('\n', fp);
    fputc('\n', fp);

    return;
}


/** print_list_indent()
 * print the content of a list using an indent number of
 * spaces before each line
 * It walks recursively through the list increasing the indent
 * for every subtree
 *
 * parameters:
 * record_t *list   the list to be printed
 * indent int       number of spaces
 * FILE *fp         file pointer for output
 *
 * return None
 */
void print_list_indent(record_t *list, int indent, FILE *fp= stdout) {
    record_t *curr;
    int i;

    if (indent < 0){
        indent = 0;
    }

    curr = list;
    do {
        for(i=0; i<indent; i++) {
            fprintf(fp, " ");
        }
        /*
         * printf("..printing: %p\n", curr);
         */
        switch(curr->type) {
            case RECORD_STRING:
            case RECORD_NUMERIC:
                if (curr->key != NULL) {
                    fprintf(fp, "%s: ", curr->key->value);
                }
                if (curr->value != NULL) {
                    fprintf(fp, "%s", ((r_string_t *)(curr->value))->value);
                }
                fprintf(fp, "\n");
                break;

            /* if we have a child here, we may
             * and it is a list, we have to convert it!
             * so, we go for recursion
             */
            case RECORD_MULTILINE_STRING:
                if (curr->key != NULL) {
                    fprintf(fp, "%s: | \n", curr->key->value);
                }
                if (curr->value != NULL) {
                    print_block_indent((r_string_t *)(curr->value), indent+2, fp);
                }
                break;

            case RECORD_CHILD_LIST:
                /*
                * printf("calling child with %p\n", curr->value);
                */
                if (curr->key != NULL) {
                    fprintf(fp, "%s:", curr->key->value);
                }
                print_list_indent(start_list((record_t *)(curr->value)), indent+2, fp);
                break;
            default:
                break;
        }
    }while((curr= curr->next) != NULL);

    return;
}


/* index_list()
 * find the index of the current position
 *
 * parameters
 * record_t *list   pointer to a list
 *
 * return:
 * int length   the index of the current position
 *              indexing starts at 0
 */
int index_list(record_t *list) {
    int length = 0;
    record_t *curr= NULL;

    if (list == NULL) {
        return(0);
    }
    curr = start_list(list);

    do {
        length ++;
        /* curr->next should never be NULL,
         * but check for any case
         */
    }while((curr= curr->next) != list && curr != NULL);

    return(length);
}


/* len_list()
 * the full length of the list
 *
 * parameter:
 * record_t *list   an element of a list
 *
 * return:
 * int length   the length of the list
 */
int len_list(record_t *list) {
    record_t *curr=NULL;
    int length = 0;

    if (list == NULL) {
        return(0);
    }

    curr = start_list(list);
    do {
        length ++;
    } while( (curr = curr->next) != NULL);

    return(length);
}


/* list_array()
 * convert the list to an array of records
 * It does not change the actual registration of next and previous
 * pointers, just lists up the pointers to each elements
 *
 * parameters:
 * record_t *list   a pointer to an element of the list
 *
 * return:
 * a record_t ** pointer for an array of length+1
 * the last pointer is NULL to indicate the end
 */
record_t **list_array(record_t *list) {
    record_t * curr;
    record_t **res;
    int i=0;
    int length=0;

    if(list == NULL) {
        fputs("Empty list!\n", stderr);
        return(NULL);
    }

    curr= start_list(list);
    length = len_list(curr);
    if ((res=(record_t**)malloc((length+1)*sizeof(record_t*)))==NULL) {
        fputs("Cannot allocate list array!\n", stderr);
        return(NULL);
    }

    do{
        *(res +i) = curr;
        i++;
    }while( (curr=curr->next) != NULL && i <length);
    *(res+i)= NULL;

    return(res);
}

/* delete_list_array()
 * free up the list array
 * but do not free up its content, so the original list
 * can remain intact.
 *
 * parameters:
 * record_t **array the address of the list array
 * int length       length of the array
 *
 * length of the array is len_list() +1
 * return None
 */
void delete_list_array(record_t** array, int length){

    int i;
    if (length <1) {
        return;
    }

    for(i=0; i<length; i++) {
        *(array+i) = NULL;
    }
    free(array);
    return;
}

/* values_array()
 * make an array of strings from the values in
 * the list, replace those which are sub-lists with a NULL.
 *
 * parameters:
 * record_t *list   the list to work on
 *
 * return:
 * r_string_t **array
 *
 * length of the array is len_list() +1
 */

r_string_t **values_array(record_t *list) {
    record_t* curr;
    r_string_t **res=NULL;
    int i =0;
    int length= 0;

    if (list==NULL) {
        return(NULL);
    }

    curr = start_list(list);
    length = len_list(curr);

    if ((res= (r_string_t**)malloc(length*sizeof(r_string_t*))) == NULL) {
        fputs("Unable to allocate string array!\n", stderr);
        return(NULL);
    }

    do {
        switch(curr->type) {
            case RECORD_STRING:
            case RECORD_NUMERIC:
            case RECORD_MULTILINE_STRING:
                *(res+i) = (r_string_t*)curr->value;
                break;
            /* if we have a child here, we may
             * have to clean it up!
             */
            case RECORD_EMPTY:
            case RECORD_CHILD_LIST:
                *(res+i) = NULL;
                break;
            default:
                fputs("Unknown record type in clear_record!\n", stderr);
            }
        i++;
    } while((curr= curr->next) != NULL && i < length);

    return(res);
}


/* keys_array()
 * make an array of strings from the keys in
 * the list, replace those which are sub-lists with a NULL.
 *
 * parameters:
 * record_t *list   the list to work on
 *
 * return:
 * r_string_t **array
 *
 * length of the array is len_list() +1
 */

r_string_t **keys_array(record_t *list) {
    record_t* curr;
    r_string_t **res;
    int i =0;
    int length= 0;

    if (list==NULL) {
        return(NULL);
    }

    curr = start_list(list);
    length = len_list(curr);

    if ((res= (r_string_t**)malloc(length*sizeof(r_string_t*))) == NULL) {
        fputs("Unable to allocate string array!\n", stderr);
        return(NULL);
    }

    do {
        *(res+i) = curr->key;
        i++;
    } while((curr= curr->next) != NULL && i < length);

    return(res);
}

/* delete_string_array()
 * free up the string array, but do not touch the strings
 *
 * parameter:
 * r_string_t **array   a string array made by the above two functions
 * int length           the length of the array
 *
 * return None
 */

void delete_string_array(r_string_t **array, int length) {
    int i;

    if(array== NULL || length < 1) {
        return;
    }
    for (i=0; i<length; i++) {
        *(array+i) = NULL;
    }
    free(array);

    return;
}


/*
int main(void){

    r_string_t *key, *value;
    record_t *rec=NULL;
    record_t *list=NULL;

    key = new_string_from_text("first_key", 10);
    value = new_string_from_text("Hello world", 12);

    printf("created strings key: %s and value %s\n", key->value, value->value);

    rec = new_record();
    rec -> key = key;
    rec -> value = value;
    rec -> type = RECORD_STRING;
    list = append_record(list, rec);
    printf("Current list: %p\n", list);

    rec = new_record();
    key = new_string_from_text("first_key", 10);
    value = new_string_from_text("Hello world", 12);
    rec->value = key;
    rec->key = value;
    rec -> type = RECORD_STRING;
    list = append_record(list, rec);
    printf("Current list: %p\n", list);


    printf("We have a record:\nkey: %s\nvalue: %s\n type %d\n", rec->key->value, ((r_string_t*)(rec->value))->value, (int)rec->type);

    printf("****************\n");

    print_list(start_list(list));
    delete_list(list);

    return(0);
}
*/
