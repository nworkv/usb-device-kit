CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -Werror -std=gnu11
all: usbemu
usbemu: usbemu.c
	$(CC) $(CFLAGS) -o $@ $<
clean:
	rm -f usbemu
