/* write some code to test libyaml:
 * loading a YAML file
 * print feedback about what was imported
 */

#include<stdio.h>
#include"../lists.h"

/* to handle yaml: */
#include<yaml.h>

#define MAX_LENGTH 1024
#define INDENT_STRING "  "


/** yaml_parse_inside()
 * take a yaml parser object, and parse the
 * inside of the document recursively
 * every sequence would trigger a call
 * to the same function, groupping the internals
 * This is to manage the global / local mappings
 *
 * parameters:
 * yaml_parser_t *parser the open parser object
 * int map_block    an integer 1/0 to indicate if this is a call on
 *                  a new block map, which means all entries are map
 *                  elements until said otherwise.
 *                  Ending map should return
 * int indent   a counter for depth of indentation used for printing
 *
 * return: None
 */
void yaml_parse_inside(yaml_parser_t *parser, int map_block, int indent){
    yaml_event_t event;
    int i;
    int end= 0;
    int is_map= 0;
    char content[MAX_LENGTH];
    char paired= 0;

    if (parser == NULL) {
        return;
    }
    if (map_block >0) {
        is_map =1;
    }

    for (i=0; i<indent; i++) {
        printf(INDENT_STRING);
    }
    printf("New block started, indent of %d\n", indent);

    do{
        if (!yaml_parser_parse(parser, &event)) {
            printf("Parser error!\n");
            exit(EXIT_FAILURE);
        }
        /* print out the indent before anything else */
        for (i=0; i<indent; i++) {
            printf(INDENT_STRING);
        }

        switch(event.type)
        {
            case YAML_NO_EVENT:
                printf("No event\n");
                break;
            /* these should not happen here: */
            case YAML_STREAM_START_EVENT:
            case YAML_STREAM_END_EVENT:
            case YAML_DOCUMENT_START_EVENT:
                printf("Stream start/end or document start should not happen here!\n");
                break;

            /* when we are done with this branch: */
            case YAML_DOCUMENT_END_EVENT:
            case YAML_SEQUENCE_END_EVENT:
                printf("Block ended, return\n");
                end= 1;
                break;
            /* a new branch has come up */
            case YAML_SEQUENCE_START_EVENT:
                /* Let us assume the last content was a key! */
                printf("New sequence to -- key: %s\n", content);
                /* call but map_block =0 */
                yaml_parse_inside(parser, 0, indent+1);
                /* paired does not matter here */
                /* but coming back from here, we have: */
                paired = 0;
                break;

            case YAML_MAPPING_START_EVENT:
                puts("Mapping started");
                if (is_map > 0) {
                    printf("with key: %s\n", content);
                    yaml_parse_inside(parser, 1, indent+1);
                    /* now, this map is completed */
                } else {
                    /* or, we are in a new mapping */
                    is_map = 1;
                }
                /* this may not be necessary for a well behaving
                 * yaml document */
                paired = 0;
                break;

            case YAML_MAPPING_END_EVENT:
                puts("Mapping ended");
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
                printf("New alias event, anchor: %s\n", event.data.alias.anchor);
                break;

            case YAML_SCALAR_EVENT:
                /* printf("New scalar event ");
                 */
                /* if we are mapping and there is no key, then this is one:
                 *
                    printf("scalar, paired = %d\n", (int)paired);
                 */
                if (is_map >0 && paired) {
                    printf("Next key: %s, ", content);
                }

                strncpy(content, (char*)event.data.scalar.value, MAX_LENGTH);
                if (is_map < 1 || paired) {
                    printf("content: %s\n", content);
                }
                /* just count if we have passed twice already */
                paired = paired > 0 ? 0:1;
                break;
        }

        yaml_event_delete(&event);
    } while(!end);

    /* do not delete the parser, we are inside a document! */
    return;
}


int main(void)
{
  FILE *fh = fopen("test.yaml", "r");
  yaml_parser_t parser;
  yaml_event_t event;
  int end=0;

  /* Initialize parser */
  if(!yaml_parser_initialize(&parser)) {
    fputs("Failed to initialize parser!\n", stderr);
  } else {
      puts("YAML is initialized\n");
  }

  if(fh == NULL)
    fputs("Failed to open file!\n", stderr);

  /* Set input file */
  yaml_parser_set_input_file(&parser, fh);

  /* CODE HERE */
  do {
      if (!yaml_parser_parse(&parser, &event)) {
          printf("Parser error!\n");
          exit(EXIT_FAILURE);
      }
      switch(event.type)
      {
        case YAML_NO_EVENT:
            printf("No event\n");
            break;
        case YAML_STREAM_START_EVENT:
            printf("New stream started\n");
            break;
        case YAML_STREAM_END_EVENT:
            printf("New stream ended\n");
            /* here ends the whole story */
            end= 1;
            break;
        case YAML_DOCUMENT_START_EVENT:
            printf("Document started\n");
            /* start actually processing the content */
            yaml_parse_inside(&parser, 0, 1);
            break;
        case YAML_DOCUMENT_END_EVENT:
            printf("Document ended\n");
            break;
        case YAML_SEQUENCE_START_EVENT:
            puts("This should not happen without a document start\n");
            yaml_parse_inside(&parser, 0, 1);

            break;
        case YAML_SEQUENCE_END_EVENT:
        case YAML_MAPPING_START_EVENT:
        case YAML_MAPPING_END_EVENT:
        case YAML_ALIAS_EVENT:
        case YAML_SCALAR_EVENT:
            puts("there should not happen here!\n");
            break;
      }

      yaml_event_delete(&event);

  } while (!end);

  /* Cleanup */
  yaml_parser_delete(&parser);
  fclose(fh);
  return 0;
}
