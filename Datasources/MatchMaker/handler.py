import boto3
import requests


def lambda_handler(event, context):
    dynamodb = boto3.client("dynamodb", "eu-west-1")
    response = dynamodb.scan(TableName="FindGameTable")

    items = response.get("Items")
    users = [item["user"]["S"] for item in items]

    games = generate_game_pairs(users)

    found_game_users = []
    for game in games:
        post_game(game)
        found_game_users.append(game["whitePlayer"])
        found_game_users.append(game["blackPlayer"])

    clean_up_find_game_table(dynamodb, found_game_users)


def generate_game_pairs(users):
    pairs = []
    pair = {
        "blackPlayer": None,
        "whitePlayer": None
    }
    for user in users:
        if pair["blackPlayer"] is None:
            pair["blackPlayer"] = user
            continue
        if pair["whitePlayer"] is None:
            pair["whitePlayer"] = user
            pairs.append(pair.copy())
            pair = {
                "blackPlayer": None,
                "whitePlayer": None
            }

    return pairs


def post_game(game):
    cognito = boto3.client("cognito-idp", "eu-west-1")
    resp = cognito.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": "Peter",
            "PASSWORD": "12345678"
        },
        ClientId="2bg2tfob60s2g2lu8b16ipovvh",
    )

    query = """mutation createGame($blackPlayer: ID!, $whitePlayer: ID!) {
          createGame(blackPlayer: $blackPlayer, whitePlayer: $whitePlayer) {
            gameId
            whitePlayer
            blackPlayer
            currentGameState
          }
        }"""
    headers = {
        "Authorization": resp["AuthenticationResult"]["AccessToken"]
    }
    url = "https://api.checkers2022.com/graphql"
    requests.post(url, headers=headers, json={
        "query": query,
        "variables": game
    })


def clean_up_find_game_table(dynamoDb, users):
    user_count = len(users)
    users_deleted_count = 0

    # DynamoDb accepts a maximum of 25 operations in a batch
    while user_count > users_deleted_count:
        batch = users[0+users_deleted_count:24+users_deleted_count]

        delete_requests = []
        for user in batch:
            delete_requests.append(
                {
                    "DeleteRequest": {
                        "Key": {
                            "user": {"S": user}
                        }
                    }
                }
            )

        dynamoDb.batch_write_item(
            RequestItems={
                "FindGameTable": delete_requests
            }
        )

        users_deleted_count += len(batch)
