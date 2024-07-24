HOST_USER		=	$(shell whoami)
PROJET_NAME		=	transcendence

IMAGES			=	$(shell docker images -q)
CONTAINERS		=	$(shell docker ps -aq)
VOLUMES			=	$(shell docker volume ls -q)
NETWORKS		=	$(shell docker network ls -q)
DATA_DIR		=	./data/PostgreSQL

all:
	@echo "$(YELLOW)\n. . . Launching . . .\n$(RESET)"
	@mkdir -p $(DATA_DIR)
	@docker compose -p $(PROJET_NAME) -f ./docker-compose.yml up -d
	@echo "\n$(BOLD)$(GREEN)Launched [ ✔ ]\n$(RESET)"

start:
	@echo "$(YELLOW)\n. . . starting containers . . . \n$(RESET)";
	@if [ -n "$$(docker ps -aq)" ]; then \
		docker compose -f ./docker-compose.yml start; \
		echo "\n$(BOLD)$(GREEN)Containers started [ ✔ ]\n$(RESET)"; \
	else \
		echo "\n$(BOLD)$(RED)No Docker containers found.$(RESET)\n"; \
	fi

logs:
	@echo "$(YELLOW)\n. . . Displaying logs . . . \n$(RESET)"
	@docker compose -f ./docker-compose.yml logs -f
	@echo "\n$(BOLD)$(GREEN)Displayed logs [ ✔ ]\n$(RESET)"

stop:
	@echo "$(YELLOW)\n. . . stopping containers . . . \n$(RESET)";
	@if [ -n "$$(docker ps -aq)" ]; then \
		docker compose -f ./docker-compose.yml stop; \
		echo "\n$(BOLD)$(GREEN)Containers stopped [ ✔ ]\n$(RESET)"; \
	else \
		echo "\n$(BOLD)$(RED)No Docker containers found.$(RESET)\n"; \
	fi

down:
	@echo "$(YELLOW)\n. . . stopping and removing docker containers . . . \n$(RESET)";
	@if [ -n "$$(docker ps -aq)" ]; then \
		docker compose -f ./docker-compose.yml down; \
		echo "\n$(BOLD)$(GREEN)Containers stopped and removed[ ✔ ]\n$(RESET)"; \
	else \
		echo "\n$(BOLD)$(RED)No Docker containers found.$(RESET)\n"; \
	fi

clean: down
	@echo "$(YELLOW)\n. . . Cleaning up unused resources (excluding data) . . .\n$(RESET)"
	@docker container prune -f
	@docker image prune -a -f
	@docker volume prune -a -f
	@docker network prune -f
	@echo "\n$(BOLD)$(GREEN)Cleaned up unused resources (excluding data) [ ✔ ]\n$(RESET)"

fclean: clean
	@echo "$(YELLOW)\n. . . Performing full cleanup . . .\n$(RESET)"
	@rm -rf $(DATA_DIR)
	@docker system prune -a -f
	@echo "\n$(BOLD)$(GREEN)Full cleanup completed [ ✔ ]\n$(RESET)"

re: down all
	@echo "$(YELLOW)\n. . . Restarting the project . . .\n$(RESET)"

check_status:
	@echo "\n$(YELLOW)docker ps -a $(RESET)" && docker ps -a
	@echo "\n$(YELLOW)docker volume ls $(RESET)" && docker volume ls
	@echo "\n$(YELLOW)docker images -a $(RESET)" && docker images -a
	@echo "\n$(YELLOW)docker network ls $(RESET)" && docker network ls

.PHONY: all start logs stop down clean fclean re check_status

# COLORS
RESET = \033[0m
WHITE = \033[37m
GREY = \033[90m
RED = \033[91m
DRED = \033[31m
GREEN = \033[92m
DGREEN = \033[32m
YELLOW = \033[93m
DYELLOW = \033[33m
BLUE = \033[94m
DBLUE = \033[34m
MAGENTA = \033[95m
DMAGENTA = \033[35m
CYAN = \033[96m
DCYAN = \033[36m

# FORMAT
BOLD = \033[1m
ITALIC = \033[3m
UNDERLINE = \033[4m
STRIKETHROUGH = \033[9m
