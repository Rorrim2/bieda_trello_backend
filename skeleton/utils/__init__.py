from graphql_relay.node.node import from_global_id

def map_id(id: str) -> int:
    return int(from_global_id(id)[1])