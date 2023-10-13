/* load a yaml file and convert to a record_t list
 * also making the full entry tree utilizing lists as values
 * down the road
 */

#include<stdio.h>
#include"lists.h"

/* to handle yaml: */
#include<yaml.h>

/** yaml_parse_inside()
 * take a yaml parser object, and parse the
 * inside of the document recursively.
 * Every subsequence would trigger a call
 * to the same function, groupping the internals.
 * Allocate and fill in records for every element,
 * that is key/value pairs.
 * Sequences have keys of NULL.
 *
 * Return the subtree collected in this run;
 *
 * parameters:
 * yaml_parser_t *parser the open parser object
 * int map_block    an integer 1/0 to indicate if this is a call on
 *                  a new block map, which means all entries are map
 *                  elements until said otherwise.
 *                  Ending map should return
 *
 * return:
 * record_t *record, NULL upon error
 */
record_t* yaml_parse_inside(yaml_parser_t *parser, int map_block){
    /* key point: a yaml event */
    yaml_event_t event;

    int end= 0;
    int is_map= 0;
    char paired= 0;
    record_t *record= NULL;
    record_t *current= NULL;
    r_string_t *content= NULL;

    if (parser == NULL) {
        fputs("No parser!\n", stderr);
        return(NULL);
    }
    if (map_block >0) {
        is_map =1;
    }
    /*
     * printf("New block is called:\n*****\n");
     */

    do{
        if (!yaml_parser_parse(parser, &event)) {
            fputs("Parser error!\n", stderr);
            delete_list(record);
            return(NULL);
        }

        /* troubleshooting:
        if (content != NULL && content->value != NULL) {
            printf("content: %s\n", content->value);
        }
        */

        switch(event.type)
        {
            case YAML_NO_EVENT:
                printf("No event\n");
                break;
            /* these should not happen here: */
            case YAML_STREAM_START_EVENT:
            case YAML_STREAM_END_EVENT:
            case YAML_DOCUMENT_START_EVENT:
                fputs("WARNING: Stream start/end or document start should not happen here!\n", stderr);
                break;

            /* when we are done with this branch: */
            case YAML_DOCUMENT_END_EVENT:
                /*
                 * puts("Document ended, return");
                 */
                end= 1;
                break;

            case YAML_SEQUENCE_END_EVENT:
                /* puts("Block ended, return");
                 */
                end= 1;
                break;
            /* a new branch has come up */
            case YAML_SEQUENCE_START_EVENT:
                if (current == NULL) {
                    current = new_record();
                }
                if (content != NULL) {
                    /* Let us assume the last content was a key! */
                    current->key = content;
                    /* remove the content, but do not delete it*/
                    content = NULL;
                }
                /*
                 * printf("Assign sequence to: %p\n", current);
                 */
                current->value= yaml_parse_inside(parser, 0);
                current->type = RECORD_CHILD_LIST;
                /* append to the result list and forget the entry */
                record= append_record(record, current);
                current= NULL;
                /* paired does not matter here */
                /* but coming back from here, we have: */
                paired = 0;
                break;

            case YAML_MAPPING_START_EVENT:
                /*
                 * puts("Mapping started");
                 */
                if (is_map > 0) {
                    /* we have a submap, use the key,
                     * and get the value
                     */
                    if (current == NULL) {
                        current= new_record();
                    }
                    if (content == NULL) {
                        fputs("Block mapping without key!", stderr);
                    } else {
                        /*
                         * printf("with key: %s\n", (char*)(content->value));
                         */
                        /* when we collected content, created a new
                         * current record
                         */
                        current->key= content;
                        content = NULL;
                    }

                    current->value= (record_t *)yaml_parse_inside(parser, 1);
                    current->type = RECORD_CHILD_LIST;
                    /* append to the list */
                    record= append_record(record, current);
                    /* now, this map is completed */
                    current= NULL;
                } else {
                    /* or, we are in a new mapping */
                    is_map = 1;
                }
                /* this may not be necessary for a well behaving
                 * yaml document */
                paired = 0;
                break;

            case YAML_MAPPING_END_EVENT:
                /* puts("Mapping ended");
                 */
                /* if we are already down with the map
                 * and it ends again, then it was called as a submap
                 */
                if (map_block >0) {
                    /* we were called in a mapping block,
                     * so return */
                    end = 1;
                } else {
                    is_map =0;
                }
                break;

            /* actual field / value stuff */
            case YAML_ALIAS_EVENT:
                /* do not handle at the moment */
                printf("New alias event, anchor: %s\n", event.data.alias.anchor);
                break;

            case YAML_SCALAR_EVENT:
                /*
                 * printf("scalar, paired: %d, is_map: %d, content_null: %d current_null: %d\n",\
                        paired, is_map, (int)(content == NULL),\
                        (int)(current==NULL));
                 */

                /* what cases do we have?
                 * - we have a new value of something
                 *   if we have a current record, we use it
                 *   if not, we make a new one.
                 * - the new content goes into a value of the record
                 *
                 * - if we are in mapping, paired = 1, we already have a
                 *   record, have to swap key and fill value
                 * - if we are in mapping and paired = 1, we fill value
                 *   and save the record
                 * - if we are not in mapping, we fill in value and record
                 *   the current field (e.g. member of a list), and also
                 *   clear content and current
                 */
                if (current == NULL) {
                    current = new_record();
                }
                if (is_map && paired) {
                    /*
                     * printf("Next key: %s, ", (char*)(content->value));
                     */

                    current->key = content;
                    /* strictly:
                     * current->value = NULL;
                     * but we overwrite it in a second
                     */
                }

                /*
                 * printf("read: %s, %d\n", (char*)(event.data.scalar.value),\
                 *       (int)event.data.scalar.length);
                 */
                /* allocate a new string */
                content = new_string_from_text((char*)event.data.scalar.value,\
                            event.data.scalar.length);
                /*
                 * printf("content: %s, %d\n", content->value, (int)(content->length));
                 */

                if (is_map < 1 || paired) {
                    /* puts("Entered map...");
                     * printf("content: %s\n", (char*)(content->value));
                     */
                    /* we allocate the current field here...
                     * it may have a key later, but for now,
                     * it is just a value element
                    current = new_record();
                     */
                    current->value= content;

                    /* one hint about the type of the string is in the
                     * event.data.style... if folded, it is multiline
                     *
                     * Other possibilities are hidden in the tags, if they are
                     * available in the first place. If the user did not specify
                     * them explicitly, I am not sure if they show up
                     * printf("style: %d for %s\n", event.data.scalar.style, event.data.scalar.value);
                     */
                    if (event.data.scalar.style == YAML_FOLDED_SCALAR_STYLE ||\
                            event.data.scalar.style == YAML_LITERAL_SCALAR_STYLE) {
                        /* printf("Multiline string! %s\n", event.data.scalar.value); */
                        current->type = RECORD_MULTILINE_STRING;
                    } else {
                        /* testing tags for float / int does not work on plain
                         * YAML. So, do not bother at this point
                         * maybe strtod and checking errno is a solution
                         */
                        current->type= RECORD_STRING;
                    }
                    record= append_record(record, current);
                    /* Notice we do not free the memory, because those address
                     * values are now part of the list.
                     * We can clean the pointers for reuse...
                     */
                    current = NULL;
                    content = NULL;
                }
                /* else: we are in map and paired == 0: we keep content
                 * and set the key in the next round depending on if we have
                 * a list, new mapping (block)
                 */
                /* just count if we have passed twice already */
                paired = paired > 0 ? 0:1;
                break;
        }

        yaml_event_delete(&event);
    } while(!end);

    /* do not delete the parser, we are inside a document! */
    /* return the first element of our current segment */
    return(start_list(record));
}


/* read_yaml()
 * Parse and read a YAML file into an internal list structure.
 * use the yaml_parse_inside() function to fill in the content.
 *
 * Parameters:
 * filename char*   the file name to read in
 *
 * Return:
 * record_t *list     a pointer to the beginning of the list of records
 */
record_t *read_yaml(char *filename) {
  FILE *fh= NULL;
  yaml_parser_t parser;
  yaml_event_t event;
  /* our output: */
  record_t *list= NULL;
  record_t *record= NULL;
  int end=0;

  if (filename== NULL || (fh= fopen(filename, "rt")) == NULL) {
      fputs("File not fund error!\n", stderr);
      return(NULL);
  }

  /* Initialize parser */
  if (!yaml_parser_initialize(&parser)) {
    fputs("Failed to initialize parser!\n", stderr);
  }
 /* else {
  * puts("YAML is initialized");
  * }
  */

  /* Set input file */
  yaml_parser_set_input_file(&parser, fh);

  /* parse the file: */
  do {
      if (!yaml_parser_parse(&parser, &event)) {
          fputs("Parser error!\n", stderr);
          delete_list(list);
          return(NULL);
      }
      switch(event.type)
      {
        case YAML_NO_EVENT:
            printf("No event\n");
            break;
        case YAML_STREAM_START_EVENT:
            /*
             * printf("New stream started\n");
             */
            break;
        case YAML_STREAM_END_EVENT:
            /*
             * printf("New stream ended\n");
             */
            /* here ends the whole story */
            end= 1;
            break;
        case YAML_DOCUMENT_START_EVENT:
            /*
             * printf("Document started\n");
             */
            /* start actually processing the content */
            record = new_record();
//            record->key = new_string_from_text("Document", 9);
            record->value= yaml_parse_inside(&parser, 0);
            record->type = RECORD_CHILD_LIST;
            if (record->value != NULL) {
                list = append_record(list, record);
                /*
                 * printf("list expanded, list: 0x%p, record: 0x%p\n",\
                 *              list, record);
                 */
            }
            break;
        case YAML_DOCUMENT_END_EVENT:
            /*
             * printf("Document ended\n");
             */
            break;
        case YAML_SEQUENCE_START_EVENT:
            fputs("This should not happen without a document start\n", stderr);
            record= yaml_parse_inside(&parser, 0);
            record->type = RECORD_CHILD_LIST;

            if (record->value!= NULL) {
                list = append_record(list, record);
                /*
                 * printf("list expanded, list: 0x%p, record: 0x%p\n",\
                        list, record);
                 */
            }

            break;
        case YAML_SEQUENCE_END_EVENT:
        case YAML_MAPPING_START_EVENT:
        case YAML_MAPPING_END_EVENT:
        case YAML_ALIAS_EVENT:
        case YAML_SCALAR_EVENT:
            fputs("this should not happen here!\n", stderr);
            break;
      }

      /*
       * printf("current event type: %d\n", event.type);
       * printf("deleting event %p\n", &event);
       */
      yaml_event_delete(&event);

  } while (!end);

  /* Cleanup */
  yaml_parser_delete(&parser);
  fclose(fh);
  return(start_list(list));
}

/*
int main(void) {
    record_t *list;
    list = read_yaml((char*)"libyaml-test/test.yaml");
    printf("main feedback\n");
    printf("list expanded, list: 0x%p\n",\
                        list);
    list = start_list(list);
    printf("start point: 0x%p\n",\
                        list);
    puts("collected content\n now print:\n *******************************");

    printf("First document has: %d elements\n", len_list((record_t*)(list->value)));
    print_list(list);
    delete_list(list);
    return(0);
}
*/
