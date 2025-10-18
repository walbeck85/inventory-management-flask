import json
from unittest.mock import patch, MagicMock
from cli.cli import main

@patch("cli.cli.requests.get")
def test_cli_list(mock_get, capsys):
    mock_get.return_value.json.return_value = [{"id": 1, "product_name": "Sample Product"}]
    main(["list"])
    out = capsys.readouterr().out
    assert "Sample Product" in out

@patch("cli.cli.requests.post")
def test_cli_import(mock_post, capsys):
    mock_post.return_value.json.return_value = {
        "id": 2, "product_name": "Organic Almond Milk", "barcode": "0123456789012"
    }
    main(["import", "--barcode", "0123456789012"])
    out = capsys.readouterr().out
    assert "Organic Almond Milk" in out