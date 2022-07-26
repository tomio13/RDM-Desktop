/* header to the yaml reader */

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
record_t *read_yaml(char *filename);
