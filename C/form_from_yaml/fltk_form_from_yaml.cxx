# include <stdio.h>

/* FLTK includes */
#include<FL/Fl.H>
#include<FL/Fl_Window.H>
#include <FL/Fl_Scroll.H>
#include<FL/Fl_Input.H>
#include<FL/Fl_Float_Input.H>
#include<FL/Fl_Int_Input.H>
#include<FL/Fl_Multiline_Input.H>
#include<FL/Fl_Button.H>
#include<FL/Fl_Text_Display.H>
#include<FL/Fl_Text_Buffer.H>
#include<FL/Fl_Choice.H>

/* record and list handling */
# include "../lists.h"
# include "../path.h"
# include "../read_yaml.h"

/* a set of macros for using as shortcuts to
 * form field types
 */
# include "form_types.h"

/* get_type_from_record
 * check if it finds a record in a record list,
 * with key: "type" and then analyze the value for being:
 * "string", "numeric", "integer", "multiline" or "select"
 * return an integer corresponding based on form_types
 * The string comparison is at byte level, thus case sensitive!
 *
 * parameter:
 * record_t *entry  a list of records characterizing this
 *                  form element
 *
 * return:
 * integer or -1 on error
 */
int get_type_from_record(record_t *entry) {

    r_string_t *type = new_string_from_text((char*)"type", 4);
    r_string_t *val = NULL;
    record_t *hit= NULL;
    const char *compstring[] = {"hidden", "text", "numeric", "integer", "multiline", "select"};
    int res[] = {FORM_TYPE_HIDDEN, FORM_TYPE_STRING, FORM_TYPE_NUMERIC,\
        FORM_TYPE_INTEGER, FORM_TYPE_MULTILINE, FORM_TYPE_SELECT};
    int i=0;

    if (type == NULL) {
        fputs("Error creating search string!\n", stderr);
    }
    /* here we have a list of string, numeric or integer elements, thus
     * we cannot have a sublist */
    if (entry->type == RECORD_CHILD_LIST) {
        printf("This is a sublist\n");
        return(-1);
    }

    hit = list_find(start_list(entry), type);
    if (hit == NULL) {
        printf("Key not found\n");
        return -1;
    }

   /* now, analyze what the value is in hit */
    val = (r_string_t*)(hit->value);
    if (val == NULL) {
        printf("value not found\n");
        print_list(hit);
        return -1;
    }

    for (i=0; i<FORM_TYPE_N; i++) {
        if (strncmp(val->value, compstring[i], val->length) == 0){
            return(res[i]);
        }
    }

    delete_string(type);
    return(-1);
}


/* submit_cb()
 * the submission calback function
 * in our case it just sets the button to value 1
 *
 * parameters:
 * FL_Widget * button calling it
 * User data * data - None
 *
 * return Nothing
 */
void submit_cb(Fl_Widget *butt, void *param) {
    Fl_Widget *end;

    ((Fl_Button*)butt)->value(1);
    /* this will kill the application window*/
    /* go to the top: */
    /*
    end = (Fl_Widget *)param;
    while (end->parent() != NULL) {
        end = end->parent();
    }
    */
    end = ((Fl_Widget *)param)->top_window();

    /* kill at the first suitable time point: */
    Fl::delete_widget(end);

    return;
}


/* make_form_window()
 * receive a list of data, and generate a form window
 * based on the entries.
 * The list has to contain at least some fields that
 * have a 'type' subfield.
 * The content of a 'doc' subfield is set to the tooltip of the element.
 * The key of the subfield is set to label.
 *
 * parameters:
 * record_t *fieldlist      the list with information about the form
 *
 * return:
 * record_t *results        a list with keys and values or NULL on error
 */

record_t *make_form_window(record_t *fieldlist) {

    /* to create the output: */
    record_t *results= NULL;
    record_t *next_record=NULL;
    char *txt = NULL;
    /* we have a document
     * within this we have subfields
     * some are RECORD_CHILD_LIST --> those are menu items
     * In a menu item we have: type, doc, maybe value
     * and options for selectors
     */
    record_t *subfield= NULL;
    record_t *menuitem= NULL;
    record_t *select_list= NULL;
    /* when we are searching for items by names, like
     * doc, type, options, we get the corresponding list
     * element in found, its text content into content
     */
    record_t *found= NULL;
    r_string_t *content= NULL;

    /* main display elements */
    Fl_Window *window = NULL;
    Fl_Scroll *scroll= NULL;
    Fl_Text_Buffer *txtbuff= NULL;
    Fl_Text_Display *txtdisp= NULL;
    Fl_Group *group = NULL;
    Fl_Button *butt = NULL;
    /* counters, etc. */
    int i=0;
    int rec_type= 0;
    int y=0, x=0;
    int h= 50, w= 100;

    /* for the data */
    Fl_Widget **inputs= NULL;
    Fl_Input *inp = NULL;
    Fl_Choice *select= NULL;
    /* to read back the choice menu */
    const Fl_Menu_Item *picked= NULL;
    int *input_types=NULL;
    int rec_len = 0;


    if (fieldlist == NULL) {
        return(NULL);
    }
    /* prepare:
     * check out how many elements we may have
     * we can allocate more, but not less
     * allocate a Fl_Widget * array for the inputs
     * and a type_int array to see what they are
     * to know what subclass to use reading out the widgets
     */
    rec_len = len_list(fieldlist);
    /*
     * printf("Found %d elements\n", rec_len);
     */

    if (rec_len < 1) {
        fputs("Menu called with empty list!\n", stderr);
        return(NULL);
    }

    if ((inputs = (Fl_Widget**)malloc(rec_len*sizeof(Fl_Widget*))) == NULL) {
        fputs("Unable to allocate widget list\n", stderr);
        return(NULL);
    }
    if ((input_types=(int*)malloc(rec_len*sizeof(int))) == NULL) {
        fputs("Unable to allocate type array\n", stderr);
        free(inputs);
        return(NULL);
    }

    /*
     * printf("allocated memory for %d elements\n", rec_len);
     */
    /* start up a window structure first: */
    /* our basic frame is a resizable window
     * with a scroll bar in X and Y
     */
    //window = new Fl_Window(50, 50, 500, 600);
    window = new Fl_Window(500, 600, "Input");
    x= 10;
    y = 10;
    scroll = new Fl_Scroll(x, y, 490, 590);
    Fl::scheme("plastic");
    //window->resizable(window);

    /* the first conten is one of the keys within, we have all
     * fields listed in fieldlist
     */
    fieldlist = start_list(fieldlist);
    if ((subfield = list_find_from_text(fieldlist, "doc")) != NULL) {
        /* a record has a void* value for flexibility
         * now this must be a string
         */
        content = (r_string_t *)(subfield->value);
        txtbuff= new Fl_Text_Buffer(content->length);
        /* where to put this? */
        /* make a special width, for almost the whole window */
        txtdisp= new Fl_Text_Display(x, y, 490, 150, "Summary");
        y += 150;

        txtdisp->buffer(txtbuff);
        txtbuff->text(content->value);
    }

    /* make a group for the form content */
    group = new Fl_Group(x, y, 495, 595);
    group->box(FL_DOWN_BOX);
    y += 50;
    x = 120;

    /* initialize menu counter */
    i = 0;
    subfield = fieldlist;
    do {
        /* It may happen that we have not only the menu elements
         * in the structure. Like the doc one above
         */
        if (subfield->type == RECORD_CHILD_LIST) {
            /* dive into this element, its value is a new list
             * with fields like: doc, type, value, options
             */
            menuitem = (record_t *)subfield->value;
            rec_type = get_type_from_record(menuitem);

            switch(rec_type) {
                case FORM_TYPE_HIDDEN:
                    /* hidden type, needs separate processing */
                    printf("nothing to do with a record type: %d\n", rec_type);
                    break;
                case FORM_TYPE_STRING:
                    /* we have a menu element! */
                    inp = new Fl_Input(x, y, 200, 35, NULL);
                    y += 60;
                    break;
                case FORM_TYPE_NUMERIC:
                    inp = new Fl_Float_Input(x, y, 200, 35, NULL);
                    y += 60;
                    break;
                case FORM_TYPE_INTEGER:
                    inp = new Fl_Int_Input(x, y, 200, 35, NULL);
                    y += 60;
                    break;

                case FORM_TYPE_MULTILINE:
                    inp = new Fl_Multiline_Input(x, y, 300, 200, NULL);
                    y += 260;
                    break;

                case FORM_TYPE_SELECT:
                    found = list_find_from_text(menuitem, "options");
                    if (found == NULL) {
                        fputs("Select field without options!\n", stderr);
                        break;
                    }
                    /* now, create the GUI element: */
                    select = new Fl_Choice(x, y, 200, 35, NULL);
                    y += 60;
                    /* clear the menu list, and add the elements */
                    select->clear();
                    /* fill up the selection list
                     * each element in this list should have a value
                     * of r_string_t*, which has a char* value
                     * the actual text field
                     */
                    select_list = (record_t*)(found->value);
                    do {
                        select->add(((r_string_t*)(select_list->value))->value,\
                                    0,\
                                    NULL);
                        } while((select_list= select_list->next) != NULL);
                    /* we make a default choice to the first element */
                    select->value(0);
                    /* clear found for any case */
                    found = NULL;
                    break;

                default:
                    fputs("Unknown record tipe!\n", stderr);
                    printf("unknown record type or type not found %d\n", rec_type);
                    break;
            } /* end switch */

            /* if we had a meaningful record type, we can
             * decorate the input
             * and we have to increment our counter
             */
            if (rec_type > -1 && rec_type != FORM_TYPE_HIDDEN) {

                /* look for documentation or tooltip */

                found = list_find_from_text(menuitem, "doc");
                if (found != NULL && found->value != NULL) {
                    content = (r_string_t *)(found->value);
                    if (rec_type == FORM_TYPE_SELECT) {
                        select->copy_tooltip(content->value);
                    } else {
                        inp->copy_tooltip(content->value);
                    }
                }

                /* is there a default value?
                 * for a selection field it is 1, the rest can be
                 * specified
                 * Later we may check for finding the selection field default
                 * from the file as well...
                 */
                found = list_find_from_text(menuitem, "value");
                if (rec_type != FORM_TYPE_SELECT && found != NULL && found->value != NULL) {
                    content = (r_string_t*)(found->value);
                    inp->static_value(content->value);
                }

                /* store the fields as generic widget addresses */
                if (rec_type != FORM_TYPE_SELECT && rec_type != FORM_TYPE_HIDDEN) {
                    /* set up the label form the key */
                    inp->label((const char*)subfield->key->value);
                    inp->align(FL_ALIGN_LEFT|FL_ALIGN_WRAP);
                    inputs[i] = (Fl_Widget*)inp;
                } else if (rec_type == FORM_TYPE_SELECT) {
                    /* set up the label form the key */
                    select->label((const char*)subfield->key->value);
                    select->align(FL_ALIGN_LEFT|FL_ALIGN_WRAP);
                    inputs[i] = (Fl_Widget*)select;
                }

                input_types[i] = rec_type;
                i ++;
            } /* end if we had a meaningful menu entry */
        } /* end if a potential form element record */
    } while ((subfield = subfield->next) != NULL && i < rec_len);
    rec_len = i;
    /* update the length of array */

    /* finish the form, add a submission button */
    butt = new Fl_Button(x+40, y, 75, 35, "submit");
    y += 100;
    /* we can assign a value to the unpressed button */
    butt->value(0);
    butt->callback((Fl_Callback*)submit_cb, group);
    //group->resizable(group);

    group->resizable(NULL);
    group->resize(group->x(), group->y(), 500, y > 600? y:600);
    group->resizable(group);

    window->resizable(group);
    group->end();
    window -> end();
    window ->show();
    /* run the window */
    Fl::run();


    if (butt->value() == 1) {
        /* widget has run, returned... what to do with the values? */
        for (i=0; i < rec_len; i++) {
            if (input_types[i] > -1) {
                next_record = new_record();

                if (input_types[i] != FORM_TYPE_SELECT) {
                    inp = (Fl_Input*)inputs[i];
                    txt = (char*)inp->label();
                    next_record->key = new_string_from_text(txt, strlen(txt));

                    txt= (char*)((Fl_Input*)(inp))->value();
                } else {
                    select = (Fl_Choice*)(inputs[i]);
                    txt = (char*)select->label();
                    next_record->key = new_string_from_text(txt, strlen(txt));
                    picked = select->menu();
                    txt = (char*)(picked[select->value()].text);
                }

                if (txt != NULL && strlen(txt) > 0) {
                    next_record->value = (void*)new_string_from_text(txt, strlen(txt));
                } else {
                    next_record->value = (void*)new_string_from_text((char*)"N/A", 3);
                }
                switch(input_types[i]) {
                    case FORM_TYPE_STRING:
                        next_record->type = RECORD_STRING;
                        break;
                    case FORM_TYPE_NUMERIC:
                    case FORM_TYPE_INTEGER:
                    case FORM_TYPE_SELECT:
                        next_record->type = RECORD_NUMERIC;
                        break;
                    case FORM_TYPE_MULTILINE:
                        next_record->type= RECORD_MULTILINE_STRING;
                        break;
                }
                results= append_record(results, next_record);
            }
        }
    }

    /* FLTK theoretically frees up its memory
     * or leaves it to the system
     */

    /* free up what we allocated */
    free(inputs);
    free(input_types);

    return(start_list(results));
}


int main(int argc, const char* argv[]){
    record_t *menu_content= NULL;
    record_t *item=NULL;
    record_t *result= NULL;

    FILE *fout= NULL;
    char const *outfile="output.yaml";
    char const *infile="form-test.yaml";
    int i=0;

    for (i=1; i < argc; i++) {

        if (argv[i][0] == '-' && strlen(argv[i]) > 1) {
            switch(argv[i][1]) {
                case 'i':
                    if (argc > i){
                        infile = argv[i+1];
                    }
                    break;
                case 'o':
                    if (argc > i) {
                        outfile = argv[i+1];
                    }
                    break;
            }
        }
    }

    menu_content = read_yaml((char*)infile);

    if (menu_content == NULL) {
        fputs("Error reading YAML file!\n", stderr);
        return(1);
    }
    /*
     * printf("loaded %d documents\n", len_list(menu_content));
     */
    item = (record_t*)menu_content->value;
    /*
     * printf("containing %d elements\n", len_list(item));
     */
    /* use it to make a form... */
    result = make_form_window(item);
    delete_list(menu_content);

    if (result != NULL) {
        print_list(result);
        if ((fout= fopen(outfile, "wt")) == NULL) {
            fputs("Could not open output\n", stderr);
        } else {
            print_list_indent(result, 0, fout);
            fclose(fout);
        }

        delete_list(result);
    } else {
        printf("result was empty\n");
    }
    return(0);
}
