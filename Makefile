.PHONY: data backup scrape website all clean server sync most local

PROJECT_NAME = dpc-bling

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

BACKUP_DIR := $(PROJECT_DIR)/database-backup
HUGO_DIR := $(PROJECT_DIR)/hugo-website

PYTHON_INTERPRETER =  python

MAKE = /usr/bin/make

data:
	if [ ! -d $(DATA_DIR) ] ; then wget $(DATA_URL); unzip $(ZIP_FILE); rm $(ZIP_FILE); rm -rf __MACOSX; fi

backup:
	rm $(BACKUP_DIR)/backup.sql
	pg_dump dpcdb > $(BACKUP_DIR)/backup.sql
	#rm $(BACKUP_DIR)/backup.sql.zip
	#zip $(BACKUP_DIR)/backup.sql.zip $(BACKUP_DIR)/backup.sql

scrape:
	$(PYTHON_INTERPRETER) build_data_from_dpc.py

content:
	$(PYTHON_INTERPRETER) build_hugo_data.py

clean:
	rm -rf $(HUGO_DIR)/data
	rm -rf $(HUGO_DIR)/content/awarders
	rm -rf $(HUGO_DIR)/content/challenges
	rm -rf $(HUGO_DIR)/content/recipients

	rm -rf $(HUGO_DIR)/public/awarders
	rm -rf $(HUGO_DIR)/public/categories
	rm -rf $(HUGO_DIR)/public/challenges
	rm -rf $(HUGO_DIR)/public/css
	rm -rf $(HUGO_DIR)/public/js
	rm -rf $(HUGO_DIR)/public/recipients
	rm -rf $(HUGO_DIR)/public/tags
	rm -rf $(HUGO_DIR)/public/*.html
	rm -rf $(HUGO_DIR)/public/*.xml

	rm -rf downloaded

website:
	cd $(HUGO_DIR); hugo --buildDrafts --minify

local:
	cd $(HUGO_DIR); hugo --buildDrafts

server:
	cd $(HUGO_DIR); hugo server -D --disableFastRender --disableLiveReload

sync:
	git add --all
	git commit -m 'Scraper code updating'
	git push -u origin master
	cd $(HUGO_DIR)/public; \
	git add --all; \
	git commit -m 'Website built with latest version'; \
	git push -u origin master

most: scrape content website

all: clean most sync
