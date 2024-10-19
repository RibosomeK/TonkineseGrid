#include <stdio.h>
#include <stdlib.h>
#define DEFAULT_CAPACITY 256

int hello(void) {
    printf("hello world\n");
    return 0;
}

typedef struct {
    char* text;
    size_t count;
    size_t capacity;
} SaveString;

int str_prealloc(SaveString* str, size_t capacity) {
    str->capacity = capacity;
    str->text = realloc(str->text, sizeof(char) * str->capacity);
    if (str->text == NULL) {
        return -1;
    }
    return 0;
}

int str_append(SaveString* str, char* text, size_t count) {
    if (str->count + count > str->capacity) {
        if (str->capacity == 0) {
            str->capacity = DEFAULT_CAPACITY;
        }
        while (str->count + count > str->capacity) {
            str->capacity *= 2;
        }
        str->text = realloc(str->text, sizeof(char) * str->capacity);
        if (str->text == NULL) {
            return -1;
        }
    }
    for (int i = 0; i < count; ++i) {
        str->text[str->count++] = text[i];
    }
    return 0;
}

int str_clear(SaveString* str) {
    str->count = 0;
    return 0;
}

int main(void) {
    SaveString str = { 0 };
    str_prealloc(&str, 1300);
    char* text = "text";
    str_append(&str, text, 4);
    for (int i = 0; i < str.count; i++) {
        printf("%c\n", str.text[i]);
    }
}