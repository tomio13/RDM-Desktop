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

    char c;
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
    if((result = new_string((int)(pos2 - pos1))) == NULL) {
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
    char const *def_file="folder.txt";
    char const *filename= NULL;
    r_string_t *line= NULL;
    r_string_t *main_folder= NULL;

    /*
     * main_folder = getenv("HOME"); // /.config
     * main_folder = getenv("localAppData"); // for Win
     * printf("Got folder name: %s\n", main_folder);
     */

    if (argc == 1) {
        printf("Use with a project name and a -c folder-tree file parameter\n");
        return(0);
    }

    filename = def_file;
    for (i=0; i < argc; i++) {
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
                    printf("Use it as program -c folder-config.txt\n");
                    return(0);
                case 'c':
                    if (argc > (i+1)) {
                        filename = argv[i+1];
                        i ++;
                    }
            }
        } else {
            main_folder = new_string_from_text((char*)argv[i], strlen(argv[i]));
        }
    }

    if (main_folder == NULL || main_folder->length < 1) {
        fputs("Called without project name!\n", stderr);
        return(0);
    }

    printf("creating main folder: %s\n", main_folder->value);
    mkdirs(main_folder);

    if ((fp = fopen(filename, "rt")) == NULL) {
        printf("Unable to open configuration file: %s\n", filename);
        return(1);
    }

    while ((line= get_line(fp)) != NULL) {
        /* run the path replacement */
        string_replace_char(line, '/', PATH_SEP);

        if (string_prepend(line, main_folder->value, PATH_SEP) == -1) {
            fputs("Cannot combine paths!\n", stderr);
        } else {
            printf("creating: %s\n", line->value);
            mkdirs(line);
        }
        delete_string(line);
    }
    fclose(fp);

    delete_string(main_folder);
    return(0);
}
