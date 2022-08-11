/* collection of functions to manipulate paths,
 * create folders etc.
 */

/* directory identifier is platform specific:
 */
#ifdef __linux__
    #define DIRCHECK(x) S_ISDIR((x))
    #define PATH_SEP '/'
#endif

#ifdef _WIN32
    #define DIRCHECK(x) (x) == S_IFDIR
    /* separator in windows is '\', which is code: 0x5c*/
    #define PATH_SEP 0x5C
#endif

/* is_dir(filename)
 * a function to test if a path is a directory, a file
 * or there is nothing with this path
 *
 * parameter
 * r_string* filename a path in the file system
 *
 * return:
 * -1 if path does not exist
 *  0 if it is not a directory
 *  1 if it is a directory
 */
int is_dir(r_string_t *filename);

/* abspath()
 * take a path and turn it into absolute path
 * using the realpath() function
 *
 * parameters:
 * r_string_t *path the path
 *
 * return:
 * r_string_t *abspath  a new string with the absolute path
 */
r_string_t *abspath(r_string_t *path);

/* mkdirs()
 * take a path to a dir, and create it and all the
 * necessary folders between
 *
 * parameters:
 * r_string_t *path     string with the path
 *
 * return None
 */
void mkdirs(r_string_t *path);


/* get_config_dir()
 * find out some default paths for the program
 *
 *parameter: None
 *
 * return:
 * r_string_t * configuration path
 */
r_string_t *get_config_dir(void);
