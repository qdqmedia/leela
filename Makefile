.PHONY: runserver build

build:
	@./environment/dev/scripts/build_images.sh

runserver:
	@./environment/dev/scripts/runserver.sh

scheduler:
	@./environment/dev/scripts/scheduler.sh

shell:
	@./environment/dev/scripts/shell.sh

test:
	@./environment/dev/scripts/test.sh
