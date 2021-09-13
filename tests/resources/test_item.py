import json
import pytest


@pytest.mark.asyncio
async def test_item_search_get_filter_extension_cql(
    app_client, load_test_data, load_test_collection
):
    """Test GET search with JSONB query (cql json filter extension)"""
    test_item = load_test_data("test_item.json")
    resp = await app_client.post(
        f"/collections/{test_item['collection']}/items", json=test_item
    )
    assert resp.status_code == 200

    # EPSG is a JSONB key
    params = {
        "collections": [test_item["collection"]],
        "filter": {
            "gt": [
                {"property": "proj:epsg"},
                test_item["properties"]["proj:epsg"] + 1,
            ]
        },
    }
    resp = await app_client.post("/search", json=params)
    resp_json = resp.json()

    assert resp.status_code == 200
    assert len(resp_json.get("features")) == 0

    params = {
        "collections": [test_item["collection"]],
        "filter": {
            "eq": [
                {"property": "proj:epsg"},
                test_item["properties"]["proj:epsg"],
            ]
        },
    }
    resp = await app_client.post("/search", json=params)
    resp_json = resp.json()
    assert len(resp.json()["features"]) == 1
    assert (
        resp_json["features"][0]["properties"]["proj:epsg"]
        == test_item["properties"]["proj:epsg"]
    )
