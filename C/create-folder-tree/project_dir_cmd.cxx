#include<stdio.h>
#include<fcntl.h>
#include<string.h>
#include<stdlib.h>

/* widgets */
#include <FL/Fl.H>
#include <FL/fl_ask.H>

#include <sys/stat.h>

#define MAX_LINE 1024

/* directory identifier is platform specific:
 */
#ifdef __linux__
    #define DIRCHECK(x) S_ISDIR((x))
    #define SEP '/'
#endif

#ifdef _WIN32
    #define DIRCHECK(x) (x) == S_IFDIR
    /* separator in windows is '\', which is code: 0x5c*/
    #define SEP 0x5C
#endif

/* get_config_dir()
 * find out some default paths for the program
 *
 * return *const char config_path
 */
char *get_config_dir(void) {
    char *config_dir;
    const char *base;

    if ((config_dir = (char*)malloc(MAX_LINE*sizeof(char))) == NULL) {
        printf("Unable to allocate memory\n");
        return(NULL);
    }

    #ifdef __linux__
        base = getenv("HOME");
        printf("got: %s\n", base);
        /* make space for the full path. config_dir is long enough */
        config_dir = strncpy(config_dir, base, MAX_LINE);
        config_dir = strncat(config_dir, "/.config/dwi_project", MAX_LINE);
    #endif
    #ifdef _WIN32
        base = getenv("localAppData");
        /* make space for the full path. config_dir is long enough */
        config_dir = strncpy(config_dir, base, MAX_LINE);
        config_dir = strncat(config_dir, "\\dwi_project", MAX_LINE);
    #endif

    printf("base dir: %s\n", config_dir);
    return(config_dir);
}

/* get_project_name()
 * use FLTK to pop up an input field for the folder name
 *
 * return const char* project
 */
const char *get_project_name() {
    const char  *project;

    project = fl_input("Project name:");
    Fl::run();
    return(project);
}

/* is_dir(filename)
 * a function to test if a path is a directory, a file
 * or there is nothing with this path
 *
 * parameter *filename  char* a path in the file system
 *
 * return:
 * -1 if path does not exist
 *  0 if it is not a directory
 *  1 if it is a directory
 */
int is_dir(char const *filename) {

    struct stat dtest;

    if (stat("thisdir", &dtest) == -1) {
        /*
         * printf("Folder or file does not exist!\n");
         */
        return(-1);
    }

    /* in Linux: S_ISDIR, in win S_IFDIR*/
    if (DIRCHECK(dtest.st_mode)) {
        return(1);
    } else {
        return(0);
    }
}

/* get_line()
 * read the next line from a file, ignoring anything
 * beyond a # mark
 *
 * parameter FILE *fp   a file pointer to an open file
 * parameter char *text a pointer to allocated memory for the text
 * parameter int Nmax   the maximal allocated memory for the text
 *
 * return: 0 on success, -1 on error
 */

int get_line(FILE* fp, char* text, int Nmax) {

    char c;
    char *b;

    if (Nmax < 1) {
        printf("Invalid allocation length!\n");
        return(-1);
    }
    if (fp == NULL || feof(fp) != 0) {
        return(-1);
    }

    *text = '\0';
    b = text;

    printf("reading in: ");
    /* go until we have a string or feof */
    while(*text == '\0') {
        /* scan the file by character, until you find
         * # or \n (\r)
         * if # then take to the end of the line
         */
        while((c = getc(fp)) != '\n'
                && c != '\r'
                && c != '#'
                && c != EOF
                && (int)(b-text) < Nmax) {
            *b = c;
            b ++;
            printf("%c", c);
        }
        /* finish the line */
/*        if (c != '\n' && c!= '\r' && c != EOF){
            printf("\nComment: ");
            while((c=getc(fp)) != '\n' && c !='\r' && c!= EOF) printf("%c",c);
        }
        */
        while(c != '\n' && c != '\r' && c != EOF) {
            c = getc(fp);
        }
        /* end of file would keep text='\0', so
         * we have to break out
         */
        if (c == EOF && *text == '\0') {
            return(-1);
        }

    }
    *b = '\0';
    printf("\n");
    return(0);
}

/* replace_separator
 * run in a string, and replace separator character with SEP
 * defined on the top of this file
 *
 * parameter filename char* the string holding the path
 *                          its content is overwritten
 * parameter old_sep char   the character to be replaced
 * parameter length int     maximal length of the string
 *
 * return Nothing, replacement runs in place
 */
void replace_separator(char* filename, char old_sep, int length) {

    int i, N;
    char *a;

    if (old_sep == SEP || length < 1) {
        return;
    }

    N = strlen(filename);
    N = N > length ? length : N;
    a = filename;

    for (i=0; i < N; i++) {
        *a = (*a) == old_sep ? SEP : (*a);
        a++;
    }

}

int main(int argc, const char* argv[]) {

    FILE *fp;
    int i;
    char const *def_file="folder.txt";
    char const *filename;
    char line[MAX_LINE];
    char new_folder[MAX_LINE];
    char const *main_folder= NULL;
    char * basefolder;

    /*
     * main_folder = getenv("HOME"); // /.config
     * main_folder = getenv("localAppData"); // for Win
     * printf("Got folder name: %s\n", main_folder);
     */

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
                default:
                    printf("Invalid switch!\n");
            }
        }
    }
    main_folder = get_project_name();

    if (main_folder != NULL && *main_folder != '\0') {
        printf("creating main folder: %s\n", main_folder);
        if (is_dir(main_folder) == 1) {
            printf("folder already exists\n");
        } else {
            mkdir(main_folder, 0755);
        }
    }

    if ((fp = fopen(filename, "rt")) == NULL) {
        printf("Unable to open configuration file: %s\n", filename);
        return(1);
    }

    while (get_line(fp, line, MAX_LINE) != -1) {
        /* run the path replacement */
        replace_separator(line, '/', MAX_LINE);

        if (main_folder != NULL) {
            i= snprintf(new_folder, MAX_LINE, "%s%c%s", main_folder, SEP, line);
            if (i > MAX_LINE) {
                printf("folder name: %s was truncated\n", new_folder);
            }
        } else {
            strncpy(new_folder, line, MAX_LINE);
        }
        printf("Checking: %s\n", line);

        if (is_dir(new_folder) == 1) {
            printf("%s directory exists\n", new_folder);
        } else {
            printf("creating: %s\n", new_folder);
            if(mkdir(new_folder, 0755) == -1) {
                printf("Error creating folder!\n");
            }
        }
    }
    fclose(fp);

    basefolder= get_config_dir();
    if (basefolder != NULL) {
        free(basefolder);
    }

    return(0);
}
