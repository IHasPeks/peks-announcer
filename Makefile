build:
	pyinstaller cli.py --name "lol-announcer" --add-binary announcer/sounds:announcer/sounds --onefile --noconsole

clean:
	rm -rf lol-announcer.spec build/ dist/

install:
	install -m755 -D dist/lol-announcer /usr/local/bin/
	install -m644 -D appicon.png /usr/local/share/icons/lol-announcer.png
	install -m644 -D lol-announcer.desktop /usr/local/share/applications/

uninstall:
	rm /usr/local/bin/lol-announcer /usr/local/share/icons/lol-announcer.png /usr/local/share/applications/lol-announcer.desktop
