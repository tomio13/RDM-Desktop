#include<stdio.h>
#include<fcntl.h>
#include<string.h>
#include<stdlib.h>

#include "../lists.h"
#include "../path.h"

r_string_t *get_line(FILE* fp, char* text);

/* get_line()
 * read the next line from a file, ignoring anything
 * beyond a # mark
 *
 * parameter FILE *fp   a file pointer to an open file
 * parameter char *text a pointer to allocated memory for the text
 *
 * return:
 * r_string_t * a pointer to the newly allocated string
 *              or NULL on error or reaching the end of file
 */

r_string_t *get_line(FILE* fp) {

    char c=0;
    long pos1=-1, pos2=-1;
    char *b;
    int stop=0;
    int i=0;
    r_string_t *result=NULL;

    if (fp == NULL || feof(fp) != 0) {
        return(NULL);
    }

    /* check ahead where we have something useful */
    while(stop == 0){
        while(((c=getc(fp)) == '\n' || c=='\r') && c != EOF)
        ;

        if (c=='#') {
            /* a  comment comes, go to the end of line */
            while((c=getc(fp)) != '\n' && c!='\r' && c != EOF)
                ;
        } else {
            /* else we are done with passing empty part */
            stop= 1;
        }
    }

    /* now store where we are */
    if((pos1 = ftell(fp)) == -1) {
        fputs("Cannot find file location error\n", stderr);
        return(NULL);
    }

    /* go until we have a string or feof */
    while((c=getc(fp)) != '\n' && c!='\r' && c != EOF)
        ;

    if (c == EOF) {
        return(NULL);
    }

    if((pos2 = ftell(fp)) == -1) {
        fputs("Cannot find file location error\n", stderr);
        return(NULL);
    }

    /* the length is actually pos2 - pos1, but includes a
     * newline or EOF character, which we do not need in
     * the string
     */
    if((result = new_string((size_t)(pos2 - pos1))) == NULL) {
        fputs("Unable to allocate new string!\n", stderr);
        return(NULL);
    }


    if (fseek(fp, pos1 > 0 ? pos1 - 1L:0L, SEEK_SET) < 0) {
        fputs("Unable to relocate file position\n", stderr);
        return(NULL);
    }
    b = result->value;
    for (i=0; i < (int)(result->length); i++) {
        *b = getc(fp);
        b ++;
    }
    /* get the last character (EOF or newline or whatever)
     */
    getc(fp);

    return(result);
}

int main(int argc, const char* argv[]) {

    FILE *fp;
    int i;
    int idir=0;
    char const *def_file="folder.txt";
    char const *filename= NULL;
    r_string_t *line= NULL;
    r_string_t *full_line= NULL;
    r_string_t *main_folder= NULL;

    /*
     * main_folder = getenv("HOME"); // /.config
     * main_folder = getenv("localAppData"); // for Win
     * printf("Got folder name: %s\n", main_folder);
     */

    filename = def_file;
    for (i=1; i < argc; i++) {
        /* do we have a switch?
         * e.g. -c config file name
         * -v version number
         * -u usage info
         */
        if (argv[i][0] == '-') {

            switch(argv[i][1]) {
                case 'v':
                    printf("Project folder generator v 0.1 beta\n");
                    return(0);
                case 'u':
                case 'h':
                    printf("Use it as program project_name -c folder-config.txt\n");
                    return(0);
                case 'c':
                    if (argc > (i+1)) {
                        filename = argv[i+1];
                        i ++;
                    }
            }
        } else if (main_folder == NULL || main_folder->length <1){
            /* parameter is not yet defined, and we have something to fill in */
            main_folder = new_string_from_text((char*)argv[i], strlen(argv[i]));
        } else {
            printf("Main folder is already set to: %s\n", main_folder->value);
            fputs("Unknown option\n", stderr);
        }
    }

    if (main_folder == NULL || main_folder->length < 1) {
        fputs("Called without project name!\n", stderr);
        return(1);
    }

    if ((fp = fopen(filename, "rt")) == NULL) {
        printf("Unable to open configuration file: %s\n", filename);

        if (main_folder != NULL) {
            delete_string(main_folder);
        }

        return(1);
    }

    if ((idir= is_dir(main_folder)) < 0) {
        printf("creating main folder: %s\n", main_folder->value);
        mkdirs(main_folder);

    } else if (idir == 0) {
        fputs("Project folder name is used by a file!\n", stderr);
        delete_string(main_folder);
        return(1);
    } else {

        printf("folder: %s exists\n", main_folder->value);
    }


    while ((line= get_line(fp)) != NULL) {
        /* run the path replacement */
        string_replace_char(line, '/', PATH_SEP);

        if ((full_line= string_concat(main_folder, line, PATH_SEP)) == NULL) {
            fputs("Cannot combine paths!\n", stderr);
        } else {
            printf("next target: %s ... ", full_line->value);
            if ((idir= is_dir(full_line)) < 0) {
                printf("is created\n");
                mkdirs(full_line);
            } else if (idir == 0) {
                printf("is not a dir\n");
            } else {
                printf("exists\n");
            }
        }
        delete_string(line);
        line = NULL;
        delete_string(full_line);
        full_line = NULL;
    }
    fclose(fp);

    delete_string(main_folder);
    return(0);
}
