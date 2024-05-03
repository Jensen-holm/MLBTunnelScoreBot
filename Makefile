build:
	docker build -t mlb-tunnel-bot .

run:
	docker run \
		--env CLIENT_ID=$(CLIENT_ID) \
		--env CLIENT_SECRET=$(CLIENT_SECRET) \
		--env ACCESS_TOKEN=$(ACCESS_TOKEN) \
		--env ACCESS_TOKEN_SECRET=$(ACCESS_TOKEN_SECRET) \
		--env CONSUMER_KEY=$(CONSUMER_KEY) \
		--env CONSUMER_SECRET=$(CONSUMER_SECRET) \
		--env BEARER_TOKEN=$(BEARER_TOKEN) \
		mlb-tunnel-bot
