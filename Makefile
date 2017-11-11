refresh: update build
rebuild: clean update build

update:
	./bin/update_feeds.py

build:
	hugo

clean:
	rm -rf public/* content/feeds/*
