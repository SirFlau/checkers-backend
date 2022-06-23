import boto3
from util.validate_move import MoveValidator


def lambda_handler(event, context):
    game_id = event["arguments"]["gameId"]
    new_game_state = event["arguments"]["newGameState"]
    user = event["user"]

    dynamodb = boto3.client("dynamodb", "eu-west-1")
    response = fetch_game_from_dynamodb(dynamodb, game_id)

    if response["Item"].get("game_result") is not None:
        return None

    old_game_state = response["Item"]["currentGameState"]["S"]
    white_player = response["Item"]["whitePlayer"]["S"]

    move_requester_color = "white" if white_player == user else "black"

    move_validator = MoveValidator(old_game_state, move_requester_color)
    move_valid = move_validator.validate_new_state(new_game_state)
    if move_valid:
        turn = new_game_state[32:33]
        game_result = None
        result_reason = None
        if turn == "0":
            win_validator = MoveValidator(new_game_state, "black")
            if not win_validator.find_all_valid_new_states():
                game_result = "WHITE_WIN"
                result_reason = "BLACK_CANNOT_MOVE"
        if turn == "1":
            win_validator = MoveValidator(new_game_state, "white")
            if not win_validator.find_all_valid_new_states():
                game_result = "BLACK_WIN"
                result_reason = "WHITE_CANNOT_MOVE"

        return update_game_dynamodb(client=dynamodb,
                                    game_id=game_id,
                                    new_game_state=new_game_state,
                                    game_result=game_result,
                                    game_result_reason=result_reason)

    return None


def fetch_game_from_dynamodb(client, game_id):
    response = client.get_item(TableName="GameTable",
                               Key={
                                     "gameId": {
                                         "S": game_id
                                     }
                               })
    return response


def update_game_dynamodb(client, game_id, new_game_state, game_result=None, game_result_reason=None):

    update_expression = 'ADD gameStateHistory :gameStateAddValue' \
                        '  SET currentGameState=:gameStateValue'
    expression_values = {
        ':gameStateValue': {"S": new_game_state},
        ':gameStateAddValue': {"SS": [new_game_state]}
    }

    if game_result:
        update_expression += ', gameResult=:gameResultValue, gameResultReason=:gameResultReasonValue'
        expression_values.update({
            ':gameResultValue': {"S": game_result},
            ':gameResultReasonValue': {"S": game_result_reason}
        })

    game_result = client.update_item(TableName="GameTable",
                                     Key={
                                         "gameId": {
                                            "S": game_id
                                         },
                                     },
                                     UpdateExpression=update_expression,
                                     ExpressionAttributeValues=expression_values,
                                     ReturnValues="ALL_NEW")

    return_value = {}
    for key, value_dict in game_result["Attributes"].items():
        values = value_dict.values()
        for value in values:
            return_value[key] = value

    return return_value
