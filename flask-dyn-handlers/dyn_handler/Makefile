CC = gcc
CFLAGS = -O2 -fPIC -I.
LDFLAGS = -shared -Wl,--no-undefined

TARGET = libhandlers.so
OBJS = dyn_http_sdk.o handlers_example.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c dyn_http_sdk.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
