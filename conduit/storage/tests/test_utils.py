from unittest.mock import patch

import pytest
from storage.models import fetch_all_folder_asset_from_db


@pytest.mark.django_db
class TestUtils:
    @patch(
        "storage.models.Object._get_object_download_url",
        return_value="https://xyz.com",
    )
    def test_fetch_all_folder_asset_from_db(
        self, object_factory, create_tree, tree_paths
    ):
        # set up the factory with data
        data = fetch_all_folder_asset_from_db(create_tree, [], "home")

        assert len(data) == len(tree_paths)
        for asset in data:
            assert asset["path"] in tree_paths
