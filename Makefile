.PHONY: data backup scrape website all clean server sync

PROJECT_NAME = dpc-bling

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

BACKUP_DIR := $(PROJECT_DIR)/database-backup
HUGO_DIR := $(PROJECT_DIR)/hugo-website

PYTHON_INTERPRETER = pipenv run python

MAKE = /usr/bin/make

data:
	if [ ! -d $(DATA_DIR) ] ; then wget $(DATA_URL); unzip $(ZIP_FILE); rm $(ZIP_FILE); rm -rf __MACOSX; fi

backup:
	rm $(BACKUP_DIR)/backup.sql
	pg_dump dpcdb > $(BACKUP_DIR)/backup.sql
	rm $(BACKUP_DIR)/backup.sql.zip
	zip $(BACKUP_DIR)/backup.sql.zip $(BACKUP_DIR)/backup.sql

scrape:
	$(PYTHON_INTERPRETER) build_data_from_dpc.py

content:
	$(PYTHON_INTERPRETER) build_hugo_data.py

clean:
	rm -rf $(BACKUP_DIR)/backup.sql
	rm -rf $(HUGO_DIR)/data
	rm -rf $(HUGO_DIR)/content/awarders
	rm -rf $(HUGO_DIR)/content/challenges
	rm -rf $(HUGO_DIR)/content/recipients
	rm -rf download

website:
	cd $(HUGO_DIR); hugo --buildDrafts --minify

server:
	cd $(HUGO_DIR); hugo server -D --disableFastRender --disableLiveReload

sync:
	git add --all
	git commit -m 'Scraper code updating'
	git push -u origin master
	cd $(HUGO_DIR)/public
	git add --all
	git commit -m 'Website built with latest version'
	git push -u origin master

all: scrape backup content website sync
