#include<stdio.h>
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

/* submit_cb()
 * a callback function to collect the submitted data
 *
 * parameters:
 * Fl_Widget *butt --> an Fl_Button* pointer of the button pressed
 * void *param -->  acutally a Fl_Window*, then check the children
 * return: None
 */
void submit_cb(Fl_Widget *butt, void *param) {
    int N=0;
    int i=0;
    Fl_Group *group;
    Fl_Widget *child;
    Fl_Widget *end;

    char *text = NULL;

    group = (Fl_Group *)param;

    printf("callback\n");
    ((Fl_Button*)(butt))->value(1);
    /* get the children of this window */
    N = group->children();
    printf("Window has %d children\n", N);

    for (i=0; i<N; i++) {
        printf("pulling child: %d\n", i);
        child = group->child(i);
        /*
         * printf("Child is: %p\n", child);
         */

        if (child != butt) {
            text = (char *)((Fl_Input *)child)->value();

            printf("%s : %s\n", child->label(), text);
            /* do not free up, it is part of the widget! */

        } else {
            printf("%s : the button itself\n", child->label());
        }
    }

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

int main(void) {
    Fl_Window *window = NULL;
    Fl_Scroll *scroll= NULL;
    Fl_Text_Buffer *txtbuff= NULL;
    Fl_Text_Display *txtdisp= NULL;
    Fl_Group *group = NULL;
    Fl_Input *inputs[4];
    Fl_Button *butt;
    int i=0;
    int y=0;

    /* fill up the structure */
    window = new Fl_Window(50, 50, 400, 600);
    Fl::scheme("gleam");
    scroll = new Fl_Scroll(5, 20, 380, 580);
    window->resizable(window);

    txtbuff= new Fl_Text_Buffer();
    y = 120;
    txtdisp= new Fl_Text_Display(20, 40, 350, y, "Summary");
    y += 70;
    group = new Fl_Group(20, y,398, 500);

    txtdisp->buffer(txtbuff);
    txtbuff->text("Hello world, this is an explanation text\n # improve it!\n now");

    group->box(FL_DOWN_BOX);

    y += 100;
    for (i=0; i<4; i++) {
        switch(i) {
            case 0:

                inputs[i] = new Fl_Input(130, y, 100, 25, "Single line");
                inputs[i] -> copy_tooltip("single line input");
                y += 50;
                break;
            case 1:
                inputs[i] = new Fl_Float_Input(130, y, 100, 25, "Float");
                inputs[i] -> copy_tooltip("please enter a float");
                y += 50;
                break;
            case 2:
                inputs[i] = new Fl_Int_Input(130, y, 100, 25, "Integer");
                inputs[i] -> copy_tooltip("please enter a int");
                y += 50;
                break;
            case 3:
                inputs[i] = new Fl_Multiline_Input(130, y, 200, 100, "Multiline input");
                inputs[i] -> copy_tooltip("please enter a long text");
                y += 150;
                break;
/*we need the new combo element here, but it is not an Fl_Input!
 * case 4:
                inputs[i] = new Fl_Input_Choice(...);
*/
        }
        printf("Tooltip of %d is set to: %s\n", i, inputs[i]->tooltip());
    }

    butt = new Fl_Button(80, y, 75, 25, "submit");
    y += 50;
    /* we can assign a value to the unpressed button */
    butt->value(0);
    butt->callback((Fl_Callback*)submit_cb, group);

    window -> end();
    window ->show();
    /* run the window */
    Fl::run();
    printf("Widget closed, content: \n");
    for (i=0; i<4; i++) {
        printf("%s: %s\n", inputs[i]->label(), inputs[i]->value());
    }
    printf("We are done, bye!\n");

    return(0);
}
