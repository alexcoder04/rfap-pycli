
PREFIX ?= /usr/local
NAME = rfap-pycli

install:
	install -Dm755 rfap-pycli.py "$(DESTDIR)$(PREFIX)/bin/rfap-pycli"
	install -Dm644 README.md "$(DESTDIR)$(PREFIX)/share/doc/$(NAME)/README.md"
	install -Dm644 LICENSE "$(DESTDIR)$(PREFIX)/share/licenses/$(NAME)/LICENSE"

