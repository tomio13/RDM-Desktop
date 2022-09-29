/* collection of functions to manipulate paths,
 * create folders etc.
 */

#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#include<sys/stat.h>
#include<limits.h>

#include"lists.h"
#include"path.h"

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
int is_dir(r_string_t *filename) {
    struct stat dtest;

    if (filename == NULL || filename->value == NULL) {
        return(-1);
    }

    if (stat(filename->value, &dtest) == -1) {
        /*
         * printf("Folder or file does not exist!\n");
         */
        return(-1);
    }

    if (S_ISDIR(dtest.st_mode)) {
        return(1);
    } else {
        return(0);
    }
}

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
r_string_t *abspath(r_string_t *path) {
    /* let us assume none has a 2k file path... */
    char pathname[2048];
    char *respath= NULL;
    r_string_t *apath= NULL;
    r_string_t *res= NULL;

    if(path->value == NULL) {
        return(NULL);
    }
    /* realpath has an issue: it expands only to the
     * current dir +1 depth more...
     */
    if (path->length > 0 && \
            (path->value[0] == PATH_SEP || path->value[0] == '/')) {
        return(new_string_from_text(path->value, path->length));
    }
    /* now what else? */
    if(path->length > 1 && \
            path->value[0] == '.' && path->value[1] == '/') {
        respath = realpath(".", pathname);
        if (respath == NULL) {
            fputs("Error resolving local path!\n", stderr);
        }
        apath = new_string_from_text(pathname, strlen(pathname));

        if ((apath->length +1) < 2047) {
            *(apath->value + apath->length) = PATH_SEP;
            apath->length ++;
            *(apath->value + apath->length) = '\0';
        } else {
            /* not enough length, force it to a folder name
             * but then we are anyway in trouble...
             */
            *(apath->value + apath->length-1)= PATH_SEP;
        }

        res = string_concat(apath, path, 0);
    }
    if (apath != NULL) {
        delete_string(apath);
    }

    return(res);
}

/* mkdirs()
 * take a path to a dir, and create it and all the
 * necessary folders between
 *
 * parameters:
 * r_string_t *path     string with the path
 *
 * return None
 */
void mkdirs(r_string_t *path) {
    size_t i;
    char *s= NULL;

    if (path == NULL || path->value == NULL) {
        return;
    }

    /* try your luck with the relative path
     * if that was given...
     */

    s = path->value;
    /* the first character can be '/', it does not matter
     */
    s++;
    for(i=1; i< path->length; i++) {
        if(*s == PATH_SEP) {
            (*s) = '\0';
            if (is_dir(path)!=1) {

                if(mkdir(path->value, 0755) == -1) {
                    fputs("Error making directory", stderr);
                }
            }
            (*s) = PATH_SEP;
        }
        s++;
    }
    /* if the last character was not PATH_SEP,
     * we did not run yet the full path
     * if we did, then the first condition fails
     */
    if (is_dir(path)!=1) {

        if(mkdir(path->value, 0755) == -1) {
            fputs("Error making directory", stderr);
        }
    }

    return;
}


/* get_config_dir()
 * find out some default paths for the program
 *
 * parameter: None
 *
 * return r_string_t* config_path
 */
r_string_t *get_config_dir(void) {
    r_string_t *config_dir= NULL;
    r_string_t *base_dir = NULL;
    r_string_t *default_base= NULL;
    const char *base= NULL;

    #ifdef __linux__
        base = getenv("HOME");
        printf("got: %s\n", base);
        /* make space for the full path. config_dir is long enough */
        default_base = new_string_from_text((char*)"/.config/dwi_project", 21);
    #endif
    #ifdef _WIN32
        base = getenv("localAppData");
        /* make space for the full path. config_dir is long enough */
        default_base = new_string_from_text((char*)"\\dwi_project", 13);
    #endif
    base_dir = new_string_from_text((char*)base, strlen(base));
    config_dir = string_concat(base_dir, default_base, 0);

    /* clean up memory */
    delete_string(base_dir);
    delete_string(default_base);

    printf("base dir: %s\n", config_dir->value);
    return(config_dir);
}


/*
int main(void) {
    r_string_t *path=NULL;

    path = get_config_dir();
    printf("Configuration path: %s\n", path->value);
    if(is_dir(path) == 1) {
        printf("Folder exists\n");
    } else {
        printf("folder does not exist\n");
    }

    delete_string(path);
    return(0);
}
*/
