from superllm.inference.router import RoutingStrategy


def test_strategy_values():
    assert RoutingStrategy.auto == "auto"
    assert RoutingStrategy.local_first == "local_first"
    assert RoutingStrategy.cloud_first == "cloud_first"
    assert RoutingStrategy.local_only == "local_only"
    assert RoutingStrategy.cloud_only == "cloud_only"


def test_strategy_uniqueness():
    strategies = [
        RoutingStrategy.auto,
        RoutingStrategy.local_first,
        RoutingStrategy.cloud_first,
        RoutingStrategy.local_only,
        RoutingStrategy.cloud_only,
        RoutingStrategy.cheapest,
        RoutingStrategy.fastest,
    ]
    assert len(set(strategies)) == len(strategies)
