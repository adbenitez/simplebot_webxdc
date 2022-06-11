class TestPlugin:
    def test_list(self, mocker):
        msg = mocker.get_one_reply("/list")
        assert "❌" in msg.text

        assert not mocker.get_replies("https://github.com/webxdc/2048.xdc")

        mocker.bot.add_admin("admin@example.org")
        mocker.get_one_reply(
            "https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )

        msg = mocker.get_one_reply("/list")
        assert "❌" not in msg.text

    def test_download(self, mocker):
        msg = mocker.get_one_reply("/download")
        assert "❌" in msg.text

        msg = mocker.get_one_reply("/download https://github.com/webxdc/2048.xdc")
        assert "❌" in msg.text

        mocker.bot.add_admin("admin@example.org")
        mocker.get_one_reply(
            "https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )

        msg = mocker.get_one_reply("/download https://github.com/webxdc/2048.xdc")
        assert "❌" not in msg.text

    def test_delete(self, mocker):
        msg = mocker.get_one_reply("/delete https://github.com/webxdc/2048.xdc")
        assert "✔" not in msg.text

        mocker.bot.add_admin("admin@example.org")

        msg = mocker.get_one_reply(
            "/delete https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )
        assert "✔" not in msg.text

        mocker.get_one_reply(
            "https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )

        msg = mocker.get_one_reply("/list")
        assert "❌" not in msg.text

        msg = mocker.get_one_reply("/delete https://github.com/webxdc/2048.xdc")
        assert "✔" not in msg.text

        msg = mocker.get_one_reply("/delete", addr="admin@example.org")
        assert "✔" not in msg.text

        msg = mocker.get_one_reply(
            "/delete https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )
        assert "✔" in msg.text

        msg = mocker.get_one_reply("/list")
        assert "❌" in msg.text

    def test_refresh(self, mocker):
        msg = mocker.get_one_reply("/refresh https://github.com/webxdc/2048.xdc")
        assert "✔" not in msg.text

        mocker.bot.add_admin("admin@example.org")

        msg = mocker.get_one_reply(
            "/refresh https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )
        assert "✔" not in msg.text

        mocker.get_one_reply(
            "https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )

        msg = mocker.get_one_reply("/refresh https://github.com/webxdc/2048.xdc")
        assert "✔" not in msg.text

        msg = mocker.get_one_reply("/refresh", addr="admin@example.org")
        assert "✔" not in msg.text

        msg = mocker.get_one_reply(
            "/refresh https://github.com/webxdc/2048.xdc", addr="admin@example.org"
        )
        assert "✔" in msg.text
